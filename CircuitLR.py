import os
import sys
import csv
import geojson
import math
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.graphics.shapes import *
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer
from lxml import etree

circuitscale = 1.0
dustyred = "#c1432e"
rustedgold = "#ce9e62"

def scaleSVG(svgfile, scaling_factor):
    svg_root = load_svg_file(svgfile)
    svgRenderer = SvgRenderer(svgfile)
    drawing = svgRenderer.render(svg_root)
    scaling_x = scaling_factor
    scaling_y = scaling_factor
    drawing.width = drawing.minWidth() * scaling_x
    drawing.height = drawing.height * scaling_y
    drawing.scale(scaling_x, scaling_y)
    return drawing
def SVG_to_RSVG(state, cx, cy):
    SVG_NS = "http://www.w3.org/2000/svg"
    NSMAP = {None: SVG_NS}
    tree = etree.parse("Location/" + state + ".svg")
    root = tree.getroot()
    defs = root.find(f"{{{SVG_NS}}}defs")
    if defs is None:
        defs = etree.SubElement(root, f"{{{SVG_NS}}}defs")
        print("Created new <defs> element.")
    else:
        print("Found existing <defs> element.")
    radial_gradient = etree.SubElement(defs, f"{{{SVG_NS}}}radialGradient", id="grad1", cx=f"{cx}%", cy=f"{cy}%")
    etree.SubElement(radial_gradient, f"{{{SVG_NS}}}stop", offset="0%", style=f"stop-color:{rustedgold};stop-opacity:1")
    etree.SubElement(radial_gradient, f"{{{SVG_NS}}}stop", offset="100%", style=f"stop-color:{dustyred};stop-opacity:1")
    ns = {"svg": "http://www.w3.org/2000/svg"}
    paths = tree.xpath('//svg:path',namespaces=ns) 
    if paths:
        paths[0].set('fill', "url(#grad1)")
    tree.write("Location/" + state + "R.svg", pretty_print=True, xml_declaration=True, encoding="UTF-8")
    return
if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
circuitsdata = []
file_to_open = "Data/Circuits2027.csv"
with open(file_to_open, 'r') as file:
    csvreader = csv.reader(file, delimiter = ';')
    count = 0
    for row in csvreader:
        circuitsdata.append(row)
        count += 1
for i in range(len(circuitsdata)):
    state = circuitsdata[i][25]
    cx = circuitsdata[i][30]
    cy = circuitsdata[i][31]
    print(state)
    my_canvas = canvas.Canvas("PDF/" + state + "R.pdf")
    my_canvas.setFont("Helvetica", 25)
    my_canvas.setTitle(state + "R")
    bottom_margin = 5
    left_margin = 5
    SVG_to_RSVG(state, cx, cy)
    circuit_x = 0
    circuit_y = 0
    name_x = 10
    name_y = 10
    renderPDF.draw(scaleSVG("Location/" + state + "R.svg", circuitscale), my_canvas, circuit_x + left_margin, circuit_y + bottom_margin)
    my_canvas.drawString(circuit_x + left_margin + name_x, circuit_y + bottom_margin + name_y, state)
my_canvas.save()
key = input("Wait")
