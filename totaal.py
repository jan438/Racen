from lxml import etree
SVG_NS = "http://www.w3.org/2000/svg"
NSMAP = {None: SVG_NS}
def add_defs_to_svg(svg_path, output_path):
    try:
        tree = etree.parse(svg_path)
        root = tree.getroot()
        if not root.tag.endswith("svg"):
            raise ValueError("Root element is not <svg>.")
        defs = root.find(f"{{{SVG_NS}}}defs")
        if defs is None:
            defs = etree.SubElement(root, f"{{{SVG_NS}}}defs")
            print("Created new <defs> element.")
        else:
            print("Found existing <defs> element.")
        linear_gradient = etree.SubElement(defs, f"{{{SVG_NS}}}linearGradient", id="grad1")
        etree.SubElement(linear_gradient, f"{{{SVG_NS}}}stop", offset="0%", style="stop-color:blue;stop-opacity:1")
        etree.SubElement(linear_gradient, f"{{{SVG_NS}}}stop", offset="100%", style="stop-color:red;stop-opacity:1")
        ns = {"svg": "http://www.w3.org/2000/svg"}
        paths = tree.xpath('//svg:path',namespaces=ns) 
        if paths:
            paths[0].set('fill', "url(#grad1)")
        tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        print(f"Updated SVG saved to {output_path}")
    except (OSError, etree.XMLSyntaxError, ValueError) as e:
        print(f"Error processing SVG: {e}")
if __name__ == "__main__":
    add_defs_to_svg("input.svg", "output.svg")