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
cx = 0

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
def SVG_to_RSVG(svgfile):
    tree = etree.parse('Location/Belgium.svg')
    root = tree.getroot()
    children = root.getchildren()
    for child in children:
        print(len(children), child.tag, child.values)
    for element in root.getiterator("child"):
        print(element.tag, '-', element.text)    
    et = etree.ElementTree(root)
    et.write('Location/BelgiumR.svg', pretty_print=True)
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
my_canvas = canvas.Canvas("PDF/BelgiumR.pdf")
my_canvas.setFont("Helvetica", 25)
my_canvas.setTitle("BelgiumR")
bottom_margin = 5
left_margin = 5
SVG_to_RSVG("Belgium.svg")
circuit_x = 0
circuit_y = 0
name_x = 10
name_y = 10
#renderPDF.draw(scaleSVG("Location/BelgiumLR.svg", circuitscale), my_canvas, circuit_x + left_margin, circuit_y + bottom_margin)
my_canvas.drawString(circuit_x + left_margin + name_x, circuit_y + bottom_margin + name_y, "Belgium")
my_canvas.save()
key = input("Wait")
