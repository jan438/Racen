import os
import sys
import csv
import math
import unicodedata
from pathlib import Path
from datetime import datetime, date, timedelta
from ics import Calendar, Event
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER, A4, landscape, portrait
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import blue, green, black, red, pink, gray, brown, purple, orange, yellow, white, lightgrey
from reportlab.pdfbase import pdfmetrics  
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Image, Spacer, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.graphics.shapes import *
from reportlab.graphics import renderPDF
from reportlab.graphics import shapes
from reportlab.graphics import widgetbase
from reportlab.graphics.widgetbase import Widget
from reportlab.graphics.widgets import signsandsymbols
from reportlab.graphics.widgets.signsandsymbols import _Symbol
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer
from PIL import Image as PILImage

styles = getSampleStyleSheet()
teamcolors = ["#005081", "#00482C", "#FFFFFF", "#FFFFFF", 
              "#710006", "#4D5052", "#863400", "#007560", 
              "#2345AB", "#003282", "#000681"]

def mycorner(x, y, radius, startdegree, smooth, width, color):
    step = 90 / smooth
    mcpoints = []
    for i in range(smooth + 1):
        mcpoints.append(x + cos(radians(startdegree + i * step)) * radius)
        mcpoints.append(y + sin(radians(startdegree + i * step)) * radius)
    mccurve = shapes.PolyLine(points = mcpoints, strokeWidth = width, strokeColor = color)
    return mccurve
def upperrightcorner(x, y, radius, width, color):
    corner = mycorner(x, y, radius, 0, 36, width, color)
    return corner
def bottomrightcorner(x, y, radius, width, color):
    corner = mycorner(x, y, radius, 270, 36, width, color)
    return corner
def transform_svg(svgfile, tx, ty, sx, sy): 
    svg_root = load_svg_file(svgfile)
    svgRenderer = SvgRenderer(svgfile)
    df1 = svgRenderer.render(svg_root)
    gimg = df1.asGroup()
    gimg.translate(tx, ty)
    gimg.scale(sx, sy)
    return gimg
def lookupflag(flagcode):
    flagimage = "Flags/" + flagcode + "tw.svg"
    return flagimage
if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
formule1data = []
file_to_open = "Data/Teams2026.csv"
with open(file_to_open, 'r') as file:
    csvreader = csv.reader(file, delimiter = ';')
    count = 0
    for row in csvreader:
        formule1data.append(row)
        count += 1
print("Count:", count)
# 595 pixels = 210 mm A4 width
d = Drawing(210*mm, 297*mm)
pdfmetrics.registerFont(TTFont('LiberationSerif', 'LiberationSerif-Regular.ttf'))
formule1font = "LiberationSerif"
rowheight = 180
colwidth = 195
row = 4
col = 0
birthdayy = 115
leftmargin = 5.0
bottommargin = -120.0
d.add(Rect(leftmargin + col * colwidth, bottommargin + row * rowheight - 10, colwidth, 85, strokeColor = teamcolors[0], fillColor = teamcolors[0]))
renderPDF.drawToFile(d, 'PDF/gradientdrawing.pdf') 
key = input("Wait")
