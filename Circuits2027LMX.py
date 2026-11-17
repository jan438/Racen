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
circuitsdata = sorted(circuitsdata, key=operator.itemgetter(24))    
pdfmetrics.registerFont(TTFont('LiberationSerif', 'LiberationSerif-Regular.ttf'))
my_canvas = canvas.Canvas('PDF/Circuits2027LMX.pdf')
renderPDF.draw(scaleSVG("SVG/world-map.svg", worldmapscale), my_canvas, worldmap_x, worldmap_y)
drawing = svg2rlg('SVG/F1.svg')
renderPDF.draw(drawing, my_canvas, 100, 800)
#circuitdrawing = scaleSVG("SVG/" + circuitsdata[0][1] + "x.svg", circuitscale)
print(circuitsdata[0][1] + "x.svg")
my_canvas.save()
key = input("Wait")
