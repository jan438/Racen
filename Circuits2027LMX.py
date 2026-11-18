import os
import sys
import csv
import geojson
import random
import math
import operator
from math import radians, cos, sin
from ics import Calendar, Event
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics  
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics  
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor
import xml.etree.ElementTree as ET
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer

circuitscale = 0.08
worldmapscale = 0.6
worldmap_x = 118
worldmap_y = 285
cirfont = "LiberationSerif"

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
rowcount = 6
colcount = 5
rowheight = 125
colwidth = 115
row = 5
col = 0
bottom_margin = 20
left_margin = 10
circuitsdata = sorted(circuitsdata, key=operator.itemgetter(24))    
pdfmetrics.registerFont(TTFont('LiberationSerif', 'LiberationSerif-Regular.ttf'))
my_canvas = canvas.Canvas('PDF/Circuits2027LMX.pdf')
renderPDF.draw(scaleSVG("SVG/world-map.svg", worldmapscale), my_canvas, worldmap_x, worldmap_y)
drawing = svg2rlg('SVG/F1.svg')
renderPDF.draw(drawing, my_canvas, 100, 800)
for i in range(count):
    if i == 11 or i == 13:
        col = col + 3
    circuit_x = left_margin + col * colwidth
    circuit_y = bottom_margin + row * rowheight
    circuitdrawing = scaleSVG("SVG/" + circuitsdata[i][1] + "x.svg", circuitscale)
    renderPDF.draw(circuitdrawing, my_canvas, circuit_x + (colwidth - circuitdrawing.width) / 2, circuit_y + (rowheight - circuitdrawing.height) / 2 + 8)
    if i == 0:
        break
    col += 1
    if col == colcount:
        row = row - 1
        col = 0
my_canvas.save()
key = input("Wait")
