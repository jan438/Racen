class SvgShapeConverter:

    def __init__(self, path, attrConverter=None):
        self.attrConverter = attrConverter or Svg2RlgAttributeConverter()
        self.svg_source_file = path
        self.preserve_space = False

    @classmethod
    def get_handled_shapes(cls):
        return [key[7:].lower() for key in dir(cls) if key.startswith('convert')]


class Svg2RlgShapeConverter(SvgShapeConverter):

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
            return None

        nudge_points(points)
        polyline = PolyLine(points)
        self.applyStyleOnShape(polyline, node)
        has_fill = self.attrConverter.findAttr(node, 'fill') not in ('', 'none')

        if has_fill:
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

        tr = self.attrConverter.convertTransform(transform)
        for op, values in tr:
            if op == "scale":
                if not isinstance(values, tuple):
                    values = (values, values)
                group.scale(*values)
            elif op == "translate":
                if isinstance(values, (int, float)):
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
