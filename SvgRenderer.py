class SvgRenderer:
    """Renderer that renders an SVG file on a ReportLab Drawing instance.

    This is the base class for walking over an SVG DOM document and
    transforming it into a ReportLab Drawing instance.
    """

    def __init__(self, path, color_converter=None, parent_svgs=None, font_map=None):
        self.source_path = path
        self._parent_chain = parent_svgs or []  # To detect circular refs.
        self.attrConverter = Svg2RlgAttributeConverter(
            color_converter=color_converter, font_map=font_map
        )
        self.shape_converter = Svg2RlgShapeConverter(path, self.attrConverter)
        self.handled_shapes = self.shape_converter.get_handled_shapes()
        self.definitions = {}
        self.waiting_use_nodes = defaultdict(list)
        self._external_svgs = {}
        self.attrConverter.css_rules = CSSMatcher()

    def render(self, svg_node):
        node = NodeTracker.from_xml_root(svg_node)
        view_box = self.get_box(node, default_box=True)
        # Knowing the main box is useful for percentage units
        self.attrConverter.set_box(view_box)

        main_group = self.renderSvg(node, outermost=True)
        for xlink in self.waiting_use_nodes.keys():
            logger.debug("Ignoring unavailable object width ID %r.", xlink)

        main_group.translate(0 - view_box.x, -view_box.height - view_box.y)

        width, height = self.shape_converter.convert_length_attrs(
            svg_node, "width", "height", defaults=(view_box.width, view_box.height)
        )
        drawing = Drawing(width, height)
        drawing.add(main_group)
        return drawing

    def renderNode(self, node, parent=None):
        nid = node.getAttribute("id")
        ignored = False
        item = None
        name = node_name(node)

        clipping = self.get_clippath(node)
        if name == "svg":
            item = self.renderSvg(node)
            parent.add(item)
        elif name == "defs":
            ignored = True  # defs are handled in the initial rendering phase.
        elif name == 'a':
            item = self.renderA(node)
            parent.add(item)
        elif name == 'g':
            display = node.getAttribute("display")
            item = self.renderG(node, clipping=clipping)
            if display != "none":
                parent.add(item)
        elif name == "style":
            self.renderStyle(node)
        elif name == "symbol":
            item = self.renderSymbol(node)
            # First time the symbol node is rendered, it should not be part of a group.
            # It is only rendered to be part of definitions.
            if node.attrib.get('_rendered'):
                parent.add(item)
            else:
                node.set('_rendered', '1')
        elif name == "use":
            item = self.renderUse(node, clipping=clipping)
            parent.add(item)
        elif name == "clipPath":
            item = self.renderG(node)
        elif name in self.handled_shapes:
            if name == 'image':
                # We resolve the image target at renderer level because it can point
                # to another SVG file or node which has to be rendered too.
                target = self.xlink_href_target(node)
                if target is None:
                    return
                elif isinstance(target, tuple):
                    # This is SVG content needed to be rendered
                    gr = Group()
                    renderer, img_node = target
                    renderer.renderNode(img_node, parent=gr)
                    self.apply_node_attr_to_group(node, gr)
                    parent.add(gr)
                    return
                else:
                    # Attaching target to node, so we can get it back in convertImage
                    node._resolved_target = target

            item = self.shape_converter.convertShape(name, node, clipping)
            display = node.getAttribute("display")
            if item and display != "none":
                parent.add(item)
        else:
            ignored = True
            logger.debug("Ignoring node: %s", name)

        if not ignored:
            if nid and item:
                self.definitions[nid] = node
                # preserve id to keep track of svg objects
                # and simplify further analyses of generated document
                item.setProperties({'svgid': nid})
                # labels are used in inkscape to name specific groups as layers
                # preserving them simplify extraction of feature from the generated document
                label_attrs = [v for k, v in node.attrib.items() if 'label' in k]
                if len(label_attrs) == 1:
                    label, = label_attrs
                    item.setProperties({'label': label})
            if nid in self.waiting_use_nodes.keys():
                to_render = self.waiting_use_nodes.pop(nid)
                for use_node, group in to_render:
                    self.renderUse(use_node, group=group)
            self.print_unused_attributes(node)

    def get_clippath(self, node):
        """
        Return the clipping Path object referenced by the node 'clip-path'
        attribute, if any.
        """
        def get_shape_from_group(group):
            for elem in group.contents:
                if isinstance(elem, Group):
                    return get_shape_from_group(elem)
                elif isinstance(elem, SolidShape):
                    return elem

        def get_shape_from_node(node):
            for child in node.iter_children():
                if node_name(child) == 'path':
                    group = self.shape_converter.convertShape('path', child)
                    return group.contents[-1]
                elif node_name(child) == 'use':
                    grp = self.renderUse(child)
                    return get_shape_from_group(grp)
                elif node_name(child) == 'rect':
                    return self.shape_converter.convertRect(child)
                else:
                    return get_shape_from_node(child)

        clip_path = node.getAttribute('clip-path')
        if not clip_path:
            return
        m = re.match(r'url\(#([^\)]*)\)', clip_path)
        if not m:
            return
        ref = m.groups()[0]
        if ref not in self.definitions:
            logger.warning("Unable to find a clipping path with id %s", ref)
            return

        shape = get_shape_from_node(self.definitions[ref])
        if isinstance(shape, Rect):
            # It is possible to use a rect as a clipping path in an svg, so we
            # need to convert it to a path for rlg.
            x1, y1, x2, y2 = shape.getBounds()
            cp = ClippingPath()
            cp.moveTo(x1, y1)
            cp.lineTo(x2, y1)
            cp.lineTo(x2, y2)
            cp.lineTo(x1, y2)
            cp.closePath()
            # Copy the styles from the rect to the clipping path.
            copy_shape_properties(shape, cp)
            return cp
        elif isinstance(shape, Path):
            return ClippingPath(copy_from=shape)
        elif shape:
            logger.error(
                "Unsupported shape type %s for clipping",
                shape.__class__.__name__
            )

    def print_unused_attributes(self, node):
        if logger.level > logging.DEBUG:
            return
        all_attrs = self.attrConverter.getAllAttributes(node.etree_element).keys()
        unused_attrs = [attr for attr in all_attrs if attr not in node.usedAttrs]
        if unused_attrs:
            logger.debug("Unused attrs: %s %s", node_name(node), unused_attrs)

    def apply_node_attr_to_group(self, node, group):
        getAttr = node.getAttribute
        transform, x, y = map(getAttr, ("transform", "x", "y"))
        if x or y:
            transform += f" translate({x or 0}, {y or 0})"
        if transform:
            self.shape_converter.applyTransformOnGroup(transform, group)

    def xlink_href_target(self, node, group=None):
        """
        Return either:
            - a tuple (renderer, node) when the the xlink:href attribute targets
              a vector file or node
            - a PIL Image object representing the image file
            - None if any problem occurs
        """
        # Bare 'href' was introduced in SVG 2.
        xlink_href = node.attrib.get('{http://www.w3.org/1999/xlink}href') or node.attrib.get('href')
        if not xlink_href:
            return None

        # First handle any raster embedded image data
        match = re.match(r"^data:image/(jpe?g|png);base64", xlink_href)
        if match:
            image_data = base64.decodebytes(xlink_href[(match.span(0)[1] + 1):].encode('ascii'))
            bytes_stream = BytesIO(image_data)

            return PILImage.open(bytes_stream)

        # From here, we can assume this is a path.
        if '#' in xlink_href:
            iri, fragment = xlink_href.split('#', 1)
        else:
            iri, fragment = xlink_href, None

        if iri:
            # Only local relative paths are supported yet
            if not isinstance(self.source_path, str):
                logger.error(
                    "Unable to resolve image path %r as the SVG source is not "
                    "a file system path.",
                    iri
                )
                return None
            path = os.path.normpath(os.path.join(os.path.dirname(self.source_path), iri))
            if not os.access(path, os.R_OK):
                return None
            if path == self.source_path:
                # Self-referencing, ignore the IRI part
                iri = None

        if iri:
            if path.endswith('.svg'):
                if path in self._parent_chain:
                    logger.error("Circular reference detected in file.")
                    raise CircularRefError()
                if path not in self._external_svgs:
                    self._external_svgs[path] = ExternalSVG(path, self)
                ext_svg = self._external_svgs[path]
                if ext_svg.root_node is not None:
                    if fragment:
                        ext_frag = ext_svg.get_fragment(fragment)
                        if ext_frag is not None:
                            return ext_svg.renderer, ext_frag
                    else:
                        return ext_svg.renderer, NodeTracker.from_xml_root(ext_svg.root_node)
            else:
                # A raster image path
                try:
                    # This will catch invalid images
                    PDFImage(path, 0, 0)
                except OSError:
                    logger.error("Unable to read the image %s. Skipping...", path)
                    return None
                return path

        elif fragment:
            # A pointer to an internal definition
            if fragment in self.definitions:
                return self, self.definitions[fragment]
            else:
                # The missing definition should appear later in the file
                self.waiting_use_nodes[fragment].append((node, group))
                return DELAYED

    def renderTitle_(self, node):
        # Main SVG title attr. could be used in the PDF document info field.
        pass

    def renderDesc_(self, node):
        # Main SVG desc. attr. could be used in the PDF document info field.
        pass

    def get_box(self, svg_node, default_box=False):
        view_box = svg_node.getAttribute("viewBox")
        if view_box:
            view_box = self.attrConverter.convertLengthList(view_box)
            return Box(*view_box)
        if default_box:
            width, height = map(svg_node.getAttribute, ("width", "height"))
            width, height = map(self.attrConverter.convertLength, (width, height))
            return Box(0, 0, width, height)

    def renderSvg(self, node, outermost=False):
        _saved_preserve_space = self.shape_converter.preserve_space
        self.shape_converter.preserve_space = node.getAttribute(f"{{{XML_NS}}}space") == 'preserve'
        view_box = self.get_box(node, default_box=True)
        _saved_box = self.attrConverter.main_box
        if view_box:
            self.attrConverter.set_box(view_box)

        # Rendering all definition nodes first.
        svg_ns = node.nsmap.get(None)
        for def_node in node.iter_subtree():
            if def_node.tag == (f'{{{svg_ns}}}defs' if svg_ns else 'defs'):
                self.renderG(def_node)

        group = Group()
        for child in node.iter_children():
            self.renderNode(child, group)
        self.shape_converter.preserve_space = _saved_preserve_space
        self.attrConverter.set_box(_saved_box)

        # Translating
        if not outermost:
            x, y = self.shape_converter.convert_length_attrs(node, "x", "y")
            if x or y:
                group.translate(x or 0, y or 0)

        # Scaling
        if not view_box and outermost:
            # Apply only the 'reverse' y-scaling (PDF 0,0 is bottom left)
            group.scale(1, -1)
        elif view_box:
            x_scale, y_scale = 1, 1
            width, height = self.shape_converter.convert_length_attrs(
                node, "width", "height", defaults=(None,) * 2
            )
            if height is not None and view_box.height != height:
                y_scale = height / view_box.height
            if width is not None and view_box.width != width:
                x_scale = width / view_box.width
            group.scale(x_scale, y_scale * (-1 if outermost else 1))

        return group

    def renderG(self, node, clipping=None):
        getAttr = node.getAttribute
        id, transform = map(getAttr, ("id", "transform"))
        gr = Group()
        if clipping:
            gr.add(clipping)
        for child in node.iter_children():
            self.renderNode(child, parent=gr)

        if transform:
            self.shape_converter.applyTransformOnGroup(transform, gr)

        return gr

    def renderStyle(self, node):
        self.attrConverter.css_rules.add_styles(node.text or "")

    def renderSymbol(self, node):
        return self.renderG(node)

    def renderA(self, node):
        # currently nothing but a group...
        # there is no linking info stored in shapes, maybe a group should?
        return self.renderG(node)

    def renderUse(self, node, group=None, clipping=None):
        if group is None:
            group = Group()

        try:
            item = self.xlink_href_target(node, group=group)
        except CircularRefError:
            node.parent.etree_element.remove(node.etree_element)
            return group
        if item is None:
            return
        elif isinstance(item, str):
            logger.error("<use> nodes cannot reference bitmap image files")
            return
        elif item is DELAYED:
            return group
        else:
            item = item[1]  # [0] is the renderer, not used here.

        if clipping:
            group.add(clipping)
        if len(node.getchildren()) == 0:
            # Append a copy of the referenced node as the <use> child (if not already done)
            node.append(copy.deepcopy(item))
        self.renderNode(list(node.iter_children())[-1], parent=group)
        self.apply_node_attr_to_group(node, group)
        return group


class SvgShapeConverter:
    """An abstract SVG shape converter.

    Implement subclasses with methods named 'convertX(node)', where
    'X' should be the capitalised name of an SVG node element for
    shapes, like 'Rect', 'Circle', 'Line', etc.

    Each of these methods should return a shape object appropriate
    for the target format.
    """
    def __init__(self, path, attrConverter=None):
        self.attrConverter = attrConverter or Svg2RlgAttributeConverter()
        self.svg_source_file = path
        self.preserve_space = False

    @classmethod
    def get_handled_shapes(cls):
        """Dynamically determine a list of handled shape elements based on
           convert<shape> method existence.
        """
        return [key[7:].lower() for key in dir(cls) if key.startswith('convert')]


class Svg2RlgShapeConverter(SvgShapeConverter):
    """Converter from SVG shapes to RLG (ReportLab Graphics) shapes."""

    def convertShape(self, name, node, clipping=None):
        method_name = f"convert{name.capitalize()}"
        shape = getattr(self, method_name)(node)
        if not shape:
            return
        if name not in ('path', 'polyline', 'text'):
            # Only apply style where the convert method did not apply it.
            self.applyStyleOnShape(shape, node)
        transform = node.getAttribute("transform")
        if not (transform or clipping):
            return shape
        else:
            group = Group()
            if transform:
                self.applyTransformOnGroup(transform, group)
            if clipping:
                group.add(clipping)
            group.add(shape)
            return group

    def convert_length_attrs(self, node, *attrs, em_base=DEFAULT_FONT_SIZE, **kwargs):
        # Support node both as NodeTracker or lxml node
        getAttr = (
            node.getAttribute if hasattr(node, 'getAttribute')
            else lambda attr: node.attrib.get(attr, '')
        )
        convLength = self.attrConverter.convertLength
        defaults = kwargs.get('defaults', (0.0,) * len(attrs))
        return [
            convLength(getAttr(attr), attr_name=attr, em_base=em_base, default=default)
            for attr, default in zip(attrs, defaults)
        ]

    def convertLine(self, node):
        points = self.convert_length_attrs(node, 'x1', 'y1', 'x2', 'y2')
        nudge_points(points)
        return Line(*points)

    def convertRect(self, node):
        x, y, width, height, rx, ry = self.convert_length_attrs(
            node, 'x', 'y', 'width', 'height', 'rx', 'ry'
        )
        if rx > (width / 2):
            rx = width / 2
        if ry > (height / 2):
            ry = height / 2
        if rx and not ry:
            ry = rx
        elif ry and not rx:
            rx = ry
        return Rect(x, y, width, height, rx=rx, ry=ry)

    def convertCircle(self, node):
        # not rendered if r == 0, error if r < 0.
        cx, cy, r = self.convert_length_attrs(node, 'cx', 'cy', 'r')
        return Circle(cx, cy, r)

    def convertEllipse(self, node):
        cx, cy, rx, ry = self.convert_length_attrs(node, 'cx', 'cy', 'rx', 'ry')
        width, height = rx, ry
        return Ellipse(cx, cy, width, height)

    def convertPolyline(self, node):
        points = node.getAttribute("points")
        points = points.replace(',', ' ')
        points = points.split()
        points = list(map(self.attrConverter.convertLength, points))
        if len(points) % 2 != 0 or len(points) == 0:
            # Odd number of coordinates or no coordinates, invalid polyline
            return None

        nudge_points(points)
        polyline = PolyLine(points)
        self.applyStyleOnShape(polyline, node)
        has_fill = self.attrConverter.findAttr(node, 'fill') not in ('', 'none')

        if has_fill:
            # ReportLab doesn't fill polylines, so we are creating a polygon
            # polygon copy of the polyline, but without stroke.
            group = Group()
            polygon = Polygon(points)
            self.applyStyleOnShape(polygon, node)
            polygon.strokeColor = None
            group.add(polygon)
            group.add(polyline)
            return group

        return polyline

    def convertPolygon(self, node):
        points = node.getAttribute("points")
        points = points.replace(',', ' ')
        points = points.split()
        points = list(map(self.attrConverter.convertLength, points))
        if len(points) % 2 != 0 or len(points) == 0:
            # Odd number of coordinates or no coordinates, invalid polygon
            return None
        nudge_points(points)
        shape = Polygon(points)

        return shape

    def convertText(self, node):
        attrConv = self.attrConverter
        xml_space = node.getAttribute(f"{{{XML_NS}}}space")
        if xml_space:
            preserve_space = xml_space == 'preserve'
        else:
            preserve_space = self.preserve_space

        gr = Group()

        frag_lengths = []

        dx0, dy0 = 0, 0
        x1, y1 = 0, 0
        ff = attrConv.findAttr(node, "font-family") or DEFAULT_FONT_NAME
        fw = attrConv.findAttr(node, "font-weight") or DEFAULT_FONT_WEIGHT
        fstyle = attrConv.findAttr(node, "font-style") or DEFAULT_FONT_STYLE
        ff = attrConv.convertFontFamily(ff, fw, fstyle)
        fs = attrConv.findAttr(node, "font-size") or str(DEFAULT_FONT_SIZE)
        fs = attrConv.convertLength(fs)
        x, y = self.convert_length_attrs(node, 'x', 'y', em_base=fs)
        for subnode, text, is_tail in iter_text_node(node, preserve_space):
            if not text:
                continue
            has_x, has_y = False, False
            dx, dy = 0, 0
            baseLineShift = 0
            if not is_tail:
                x1, y1, dx, dy = self.convert_length_attrs(subnode, 'x', 'y', 'dx', 'dy', em_base=fs)
                has_x, has_y = (subnode.attrib.get('x', '') != '', subnode.attrib.get('y', '') != '')
                dx0 = dx0 + (dx[0] if isinstance(dx, list) else dx)
                dy0 = dy0 + (dy[0] if isinstance(dy, list) else dy)
            baseLineShift = subnode.attrib.get("baseline-shift", '0')
            if baseLineShift in ("sub", "super", "baseline"):
                baseLineShift = {"sub": -fs/2, "super": fs/2, "baseline": 0}[baseLineShift]
            else:
                baseLineShift = attrConv.convertLength(baseLineShift, em_base=fs)

            frag_lengths.append(stringWidth(text, ff, fs))

            # When x, y, dx, or dy is a list, we calculate position for each char of text.
            if any(isinstance(val, list) for val in (x1, y1, dx, dy)):
                if has_x:
                    xlist = x1 if isinstance(x1, list) else [x1]
                else:
                    xlist = [x + dx0 + sum(frag_lengths[:-1])]
                if has_y:
                    ylist = y1 if isinstance(y1, list) else [y1]
                else:
                    ylist = [y + dy0]
                dxlist = dx if isinstance(dx, list) else [dx]
                dylist = dy if isinstance(dy, list) else [dy]
                last_x, last_y, last_char = xlist[0], ylist[0], ''
                for char_x, char_y, char_dx, char_dy, char in itertools.zip_longest(
                        xlist, ylist, dxlist, dylist, text):
                    if char is None:
                        break
                    if char_dx is None:
                        char_dx = 0
                    if char_dy is None:
                        char_dy = 0
                    new_x = char_dx + (
                        last_x + stringWidth(last_char, ff, fs) if char_x is None else char_x
                    )
                    new_y = char_dy + (last_y if char_y is None else char_y)
                    shape = String(new_x, -(new_y - baseLineShift), char)
                    self.applyStyleOnShape(shape, node)
                    if node_name(subnode) == 'tspan':
                        self.applyStyleOnShape(shape, subnode)
                    gr.add(shape)
                    last_x = new_x
                    last_y = new_y
                    last_char = char
            else:
                new_x = (x1 + dx) if has_x else (x + dx0 + sum(frag_lengths[:-1]))
                new_y = (y1 + dy) if has_y else (y + dy0)
                shape = String(new_x, -(new_y - baseLineShift), text)
                self.applyStyleOnShape(shape, node)
                if node_name(subnode) == 'tspan':
                    self.applyStyleOnShape(shape, subnode)
                gr.add(shape)

        gr.scale(1, -1)

        return gr

    def convertPath(self, node):
        d = node.get('d')
        if not d:
            return None
        normPath = normalise_svg_path(d)
        path = Path()
        points = path.points
        # Track subpaths needing to be closed later
        unclosed_subpath_pointers = []
        subpath_start = []
        lastop = ''
        last_quadratic_cp = None

        for i in range(0, len(normPath), 2):
            op, nums = normPath[i:i+2]

            if op in ('m', 'M') and i > 0 and path.operators[-1] != _CLOSEPATH:
                unclosed_subpath_pointers.append(len(path.operators))

            # moveto absolute
            if op == 'M':
                path.moveTo(*nums)
                subpath_start = points[-2:]
            # lineto absolute
            elif op == 'L':
                path.lineTo(*nums)

            # moveto relative
            elif op == 'm':
                if len(points) >= 2:
                    if lastop in ('Z', 'z'):
                        starting_point = subpath_start
                    else:
                        starting_point = points[-2:]
                    xn, yn = starting_point[0] + nums[0], starting_point[1] + nums[1]
                    path.moveTo(xn, yn)
                else:
                    path.moveTo(*nums)
                subpath_start = points[-2:]
            # lineto relative
            elif op == 'l':
                xn, yn = points[-2] + nums[0], points[-1] + nums[1]
                path.lineTo(xn, yn)

            # horizontal/vertical line absolute
            elif op == 'H':
                path.lineTo(nums[0], points[-1])
            elif op == 'V':
                path.lineTo(points[-2], nums[0])

            # horizontal/vertical line relative
            elif op == 'h':
                path.lineTo(points[-2] + nums[0], points[-1])
            elif op == 'v':
                path.lineTo(points[-2], points[-1] + nums[0])

            # cubic bezier, absolute
            elif op == 'C':
                path.curveTo(*nums)
            elif op == 'S':
                x2, y2, xn, yn = nums
                if len(points) < 4 or lastop not in {'c', 'C', 's', 'S'}:
                    xp, yp, x0, y0 = points[-2:] * 2
                else:
                    xp, yp, x0, y0 = points[-4:]
                xi, yi = x0 + (x0 - xp), y0 + (y0 - yp)
                path.curveTo(xi, yi, x2, y2, xn, yn)

            # cubic bezier, relative
            elif op == 'c':
                xp, yp = points[-2:]
                x1, y1, x2, y2, xn, yn = nums
                path.curveTo(xp + x1, yp + y1, xp + x2, yp + y2, xp + xn, yp + yn)
            elif op == 's':
                x2, y2, xn, yn = nums
                if len(points) < 4 or lastop not in {'c', 'C', 's', 'S'}:
                    xp, yp, x0, y0 = points[-2:] * 2
                else:
                    xp, yp, x0, y0 = points[-4:]
                xi, yi = x0 + (x0 - xp), y0 + (y0 - yp)
                path.curveTo(xi, yi, x0 + x2, y0 + y2, x0 + xn, y0 + yn)

            # quadratic bezier, absolute
            elif op == 'Q':
                x0, y0 = points[-2:]
                x1, y1, xn, yn = nums
                last_quadratic_cp = (x1, y1)
                (x0, y0), (x1, y1), (x2, y2), (xn, yn) = \
                    convert_quadratic_to_cubic_path((x0, y0), (x1, y1), (xn, yn))
                path.curveTo(x1, y1, x2, y2, xn, yn)
            elif op == 'T':
                if last_quadratic_cp is not None:
                    xp, yp = last_quadratic_cp
                else:
                    xp, yp = points[-2:]
                x0, y0 = points[-2:]
                xi, yi = x0 + (x0 - xp), y0 + (y0 - yp)
                last_quadratic_cp = (xi, yi)
                xn, yn = nums
                (x0, y0), (x1, y1), (x2, y2), (xn, yn) = \
                    convert_quadratic_to_cubic_path((x0, y0), (xi, yi), (xn, yn))
                path.curveTo(x1, y1, x2, y2, xn, yn)

            # quadratic bezier, relative
            elif op == 'q':
                x0, y0 = points[-2:]
                x1, y1, xn, yn = nums
                x1, y1, xn, yn = x0 + x1, y0 + y1, x0 + xn, y0 + yn
                last_quadratic_cp = (x1, y1)
                (x0, y0), (x1, y1), (x2, y2), (xn, yn) = \
                    convert_quadratic_to_cubic_path((x0, y0), (x1, y1), (xn, yn))
                path.curveTo(x1, y1, x2, y2, xn, yn)
            elif op == 't':
                if last_quadratic_cp is not None:
                    xp, yp = last_quadratic_cp
                else:
                    xp, yp = points[-2:]
                x0, y0 = points[-2:]
                xn, yn = nums
                xn, yn = x0 + xn, y0 + yn
                xi, yi = x0 + (x0 - xp), y0 + (y0 - yp)
                last_quadratic_cp = (xi, yi)
                (x0, y0), (x1, y1), (x2, y2), (xn, yn) = \
                    convert_quadratic_to_cubic_path((x0, y0), (xi, yi), (xn, yn))
                path.curveTo(x1, y1, x2, y2, xn, yn)

            # elliptical arc
            elif op in ('A', 'a'):
                rx, ry, phi, fA, fS, x2, y2 = nums
                x1, y1 = points[-2:]
                if op == 'a':
                    x2 += x1
                    y2 += y1
                if abs(rx) <= 1e-10 or abs(ry) <= 1e-10:
                    path.lineTo(x2, y2)
                else:
                    bp = bezier_arc_from_end_points(x1, y1, rx, ry, phi, fA, fS, x2, y2)
                    for _, _, x1, y1, x2, y2, xn, yn in bp:
                        path.curveTo(x1, y1, x2, y2, xn, yn)

            # close path
            elif op in ('Z', 'z'):
                path.closePath()

            else:
                logger.debug("Suspicious path operator: %s", op)

            if op not in ('Q', 'q', 'T', 't'):
                last_quadratic_cp = None
            lastop = op

        gr = Group()
        self.applyStyleOnShape(path, node)

        if path.operators[-1] != _CLOSEPATH:
            unclosed_subpath_pointers.append(len(path.operators))

        if unclosed_subpath_pointers and path.fillColor is not None:
            # ReportLab doesn't fill unclosed paths, so we are creating a copy
            # of the path with all subpaths closed, but without stroke.
            # https://bitbucket.org/rptlab/reportlab/issues/99/
            closed_path = NoStrokePath(copy_from=path)
            for pointer in reversed(unclosed_subpath_pointers):
                closed_path.operators.insert(pointer, _CLOSEPATH)
            gr.add(closed_path)
            path.fillColor = None

        gr.add(path)
        return gr

    def convertImage(self, node):
        x, y, width, height = self.convert_length_attrs(node, 'x', 'y', 'width', 'height')
        image = node._resolved_target
        image = Image(int(x), int(y + height), int(width), int(height), image)

        group = Group(image)
        group.translate(0, (y + height) * 2)
        group.scale(1, -1)
        return group

    def applyTransformOnGroup(self, transform, group):
        """Apply an SVG transformation to a RL Group shape.

        The transformation is the value of an SVG transform attribute
        like transform="scale(1, -1) translate(10, 30)".

        rotate(<angle> [<cx> <cy>]) is equivalent to:
          translate(<cx> <cy>) rotate(<angle>) translate(-<cx> -<cy>)
        """

        tr = self.attrConverter.convertTransform(transform)
        for op, values in tr:
            if op == "scale":
                if not isinstance(values, tuple):
                    values = (values, values)
                group.scale(*values)
            elif op == "translate":
                if isinstance(values, (int, float)):
                    # From the SVG spec: If <ty> is not provided, it is assumed to be zero.
                    values = values, 0
                group.translate(*values)
            elif op == "rotate":
                if not isinstance(values, tuple) or len(values) == 1:
                    group.rotate(values)
                elif len(values) == 3:
                    angle, cx, cy = values
                    group.translate(cx, cy)
                    group.rotate(angle)
                    group.translate(-cx, -cy)
            elif op == "skewX":
                group.skew(values, 0)
            elif op == "skewY":
                group.skew(0, values)
            elif op == "matrix" and len(values) == 6:
                group.transform = mmult(group.transform, values)
            else:
                logger.debug("Ignoring transform: %s %s", op, values)

    def applyStyleOnShape(self, shape, node, only_explicit=False):
        """
        Apply styles from an SVG element to an RLG shape.
        If only_explicit is True, only attributes really present are applied.
        """

        # RLG-specific: all RLG shapes
        "Apply style attributes of a sequence of nodes to an RL shape."

        # tuple format: (svgAttributes, rlgAttr, converter, default)
        mappingN = (
            (["fill"], "fillColor", "convertColor", ["black"]),
            (["fill-opacity"], "fillOpacity", "convertOpacity", [1]),
            (["fill-rule"], "_fillRule", "convertFillRule", ["nonzero"]),
            (["stroke"], "strokeColor", "convertColor", ["none"]),
            (["stroke-width"], "strokeWidth", "convertLength", ["1"]),
            (["stroke-opacity"], "strokeOpacity", "convertOpacity", [1]),
            (["stroke-linejoin"], "strokeLineJoin", "convertLineJoin", ["0"]),
            (["stroke-linecap"], "strokeLineCap", "convertLineCap", ["0"]),
            (["stroke-dasharray"], "strokeDashArray", "convertDashArray", ["none"]),
        )
        mappingF = (
            (
                ["font-family", "font-weight", "font-style"],
                "fontName", "convertFontFamily",
                [DEFAULT_FONT_NAME, DEFAULT_FONT_WEIGHT, DEFAULT_FONT_STYLE]
            ),
            (["font-size"], "fontSize", "convertLength", [str(DEFAULT_FONT_SIZE)]),
            (["text-anchor"], "textAnchor", "id", ["start"]),
        )

        if shape.__class__ == Group:
            # Recursively apply style on Group subelements
            for subshape in shape.contents:
                self.applyStyleOnShape(subshape, node, only_explicit=only_explicit)
            return

        ac = self.attrConverter
        for mapping in (mappingN, mappingF):
            if shape.__class__ != String and mapping == mappingF:
                continue
            for (svgAttrNames, rlgAttr, func, defaults) in mapping:
                svgAttrValues = []
                for index, svgAttrName in enumerate(svgAttrNames):
                    svgAttrValue = ac.findAttr(node, svgAttrName)
                    if svgAttrValue == '':
                        if only_explicit:
                            continue
                        if (
                            svgAttrName == 'fill-opacity'
                            and getattr(shape, 'fillColor', None) is not None
                            and getattr(shape.fillColor, 'alpha', 1) != 1
                        ):
                            svgAttrValue = shape.fillColor.alpha
                        elif (
                            svgAttrName == 'stroke-opacity'
                            and getattr(shape, 'strokeColor', None) is not None
                            and getattr(shape.strokeColor, 'alpha', 1) != 1
                        ):
                            svgAttrValue = shape.strokeColor.alpha
                        else:
                            svgAttrValue = defaults[index]
                    if svgAttrValue == "currentColor":
                        svgAttrValue = ac.findAttr(node.parent, "color") or defaults[index]
                    if isinstance(svgAttrValue, str):
                        svgAttrValue = svgAttrValue.replace('!important', '').strip()
                    svgAttrValues.append(svgAttrValue)
                try:
                    meth = getattr(ac, func)
                    setattr(shape, rlgAttr, meth(*svgAttrValues))
                except (AttributeError, KeyError, ValueError):
                    logger.debug("Exception during applyStyleOnShape")
        if getattr(shape, 'fillOpacity', None) is not None and shape.fillColor:
            shape.fillColor.alpha = shape.fillOpacity
        if getattr(shape, 'strokeWidth', None) == 0:
            # Quoting from the PDF 1.7 spec:
            # A line width of 0 denotes the thinnest line that can be rendered at device
            # resolution: 1 device pixel wide. However, some devices cannot reproduce 1-pixel
            # lines, and on high-resolution devices, they are nearly invisible. Since the
            # results of rendering such zero-width lines are device-dependent, their use
            # is not recommended.
            shape.strokeColor = None


def svg2rlg(path, resolve_entities=False, **kwargs):
    """
    Convert an SVG file to an RLG Drawing object.
    `path` can be a file, a file-like, or a file path as str or pathlib.Path.
    """

    if isinstance(path, pathlib.Path):
        path = str(path)

    # unzip .svgz file into .svg
    unzipped = False
    if isinstance(path, str) and os.path.splitext(path)[1].lower() == ".svgz":
        with gzip.open(path, 'rb') as f_in, open(path[:-1], 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        path = path[:-1]
        unzipped = True

    svg_root = load_svg_file(path, resolve_entities=resolve_entities)
    if svg_root is None:
        return

    # convert to a RLG drawing
    svgRenderer = SvgRenderer(path, **kwargs)
    drawing = svgRenderer.render(svg_root)

    # remove unzipped .svgz file (.svg)
    if unzipped:
        os.remove(path)

    return drawing


def nudge_points(points):
    """ Nudge first coordinate if all coordinate pairs are identical.

    This works around reportlab's decision to hide shapes of size zero, even
    when the stroke should be visible.
    """
    if not points:
        return
    if len(points) < 4:
        return
    x = points[0]
    y = points[1]
    for i in range(2, len(points)-1, 2):
        if x != points[i] or y != points[i+1]:
            break
    else:
        # All points were identical, so we nudge.
        points[0] *= 1.0000001


def load_svg_file(path, resolve_entities=False):
    parser = etree.XMLParser(
        remove_comments=True, recover=True, resolve_entities=resolve_entities
    )
    try:
        doc = etree.parse(path, parser=parser)
        svg_root = doc.getroot()
    except Exception as exc:
        logger.error("Failed to load input file! (%s)", exc)
    else:
        return svg_root


def node_name(node):
    """Return lxml node name without the namespace prefix."""

    try:
        return node.tag.split('}')[-1]
    except AttributeError:
        pass


def iter_text_node(node, preserve_space, level=0):
    """
    Recursively iterate through text node and its children, including node tails.
    """
    level0 = level == 0
    text = clean_text(
        node.text, preserve_space, strip_start=level0, strip_end=(level0 and len(node.getchildren()) == 0)
    ) if node.text else None

    yield node, text, False

    for child in node.iter_children():
        yield from iter_text_node(child, preserve_space, level=level + 1)

    if level > 0:  # We are not interested by tail of main node.
        strip_end = level <= 1 and node.getnext() is None
        tail = clean_text(node.tail, preserve_space, strip_end=strip_end) if node.tail else None
        if tail not in (None, ''):
            yield node.parent, tail, True


def clean_text(text, preserve_space, strip_start=False, strip_end=False):
    """Text cleaning as per https://www.w3.org/TR/SVG/text.html#WhiteSpace"""
    if text is None:
        return None
    text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\t', ' ')
    if not preserve_space:
        if strip_start:
            text = text.lstrip()
        if strip_end:
            text = text.rstrip()
        while '  ' in text:
            text = text.replace('  ', ' ')
    return text


def copy_shape_properties(source_shape, dest_shape):
    for prop, val in source_shape.getProperties().items():
        try:
            setattr(dest_shape, prop, val)
        except AttributeError:
            pass


def monkeypatch_reportlab():
    """
    https://bitbucket.org/rptlab/reportlab/issues/95/
    ReportLab always use 'Even-Odd' filling mode for paths, this patch forces
    RL to honor the path fill rule mode (possibly 'Non-Zero Winding') instead.
    """
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.graphics import shapes

    original_renderPath = shapes._renderPath

    def patchedRenderPath(path, drawFuncs, **kwargs):
        # Patched method to transfer fillRule from Path to PDFPathObject
        # Get back from bound method to instance
        try:
            drawFuncs[0].__self__.fillMode = path._fillRule
        except AttributeError:
            pass
        return original_renderPath(path, drawFuncs, **kwargs)
    shapes._renderPath = patchedRenderPath

    original_drawPath = Canvas.drawPath

    def patchedDrawPath(self, path, **kwargs):
        current = self._fillMode
        if hasattr(path, 'fillMode'):
            self._fillMode = path.fillMode
        else:
            self._fillMode = FILL_NON_ZERO
        original_drawPath(self, path, **kwargs)
        self._fillMode = current
    Canvas.drawPath = patchedDrawPath


monkeypatch_reportlab()
