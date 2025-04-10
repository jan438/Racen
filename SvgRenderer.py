class SvgRenderer:

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
            if fragment in self.definitions:
                return self, self.definitions[fragment]
            else:
                self.waiting_use_nodes[fragment].append((node, group))
                return DELAYED

    def renderTitle_(self, node):
        pass

    def renderDesc_(self, node):
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
