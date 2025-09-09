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
    flagimage = "Flags/" + flagcode + ".svg"
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
d.add(transform_svg("SVG/F1.svg", 100, 800, 1, 1))
rowheight = 150
colwidth = 198
logox = 170
logoy = 140
namey = 90
surname = 103
logowidth = 25
logoheight = 25
row = 4
col = 0
flagx = 25.0
flagy = 115
birthdayx = 0
birthdayy = 115
leftmargin = 4.0
bottommargin = 0.0
d.add(String(100, 775,"2026 Teams", fontSize = 30, fillColor = colors.black))
for i in range(count):
    #team name
    d.add(String(leftmargin + col * colwidth, bottommargin + row * rowheight + 135, formule1data[i][0], font = formule1font, fontSize = 20, fillColor = colors.black))
    #name2 7
    d.add(String(leftmargin + col * colwidth, bottommargin + row * rowheight + namey, formule1data[i][7], font = formule1font, fontSize = 15, fillColor = colors.black))
    #surname2 6
    d.add(String(leftmargin + col * colwidth, bottommargin + row * rowheight + surname, formule1data[i][6], font = formule1font, fontSize = 14, fillColor = colors.black))
    #name1 3
    d.add(String(leftmargin + col * colwidth + 0.5 * colwidth, bottommargin + row * rowheight + namey, formule1data[i][3], font = formule1font, fontSize = 15, fillColor = colors.black))
    #surname1 2
    d.add(String(leftmargin + col * colwidth + 0.5 * colwidth, bottommargin + row * rowheight + surname, formule1data[i][2], font = formule1font, fontSize = 14, fillColor = colors.black))
    # logo
    svg_root = load_svg_file("Logos/" + formule1data[i][1] + ".svg")
    svgwidth = svg_root.attrib.get('width')
    svgheight = svg_root.attrib.get('height')
    print(formule1data[i][1] + ".svg", "SVGWidth", svgwidth, "SVGHeight", svgheight, "Logowidth", float(formule1data[i][10]), "Logoheight", float(formule1data[i][11]), "Scalingx", float(formule1data[i][12]), "Scalingy", float(formule1data[i][13]))
    d.add(transform_svg("Logos/" + formule1data[i][1] + ".svg", logox - 0.5 * float(formule1data[i][10]) + col * colwidth, logoy -  0.5 * float(formule1data[i][11]) + bottommargin + row * rowheight, float(formule1data[i][12]), float(formule1data[i][13])))
    #
    # birthday1
    birthday = formule1data[i][8]
    d.add(transform_svg("SVG/calendar-blank.svg", leftmargin + col * colwidth + birthdayx, bottommargin + row * rowheight + birthdayy, 0.5 , 0.5))
    d.add(String(leftmargin + col * colwidth + birthdayx, bottommargin + row * rowheight + birthdayy + 6, birthday[:5], fontSize = 8, fillColor = colors.black))
    d.add(String(leftmargin + col * colwidth + birthdayx, bottommargin + row * rowheight + birthdayy, birthday[6:10], fontSize = 8, fillColor = colors.black))
    #land1 5
    landcode = formule1data[i][5]
    d.add(transform_svg(lookupflag(landcode), col * colwidth + 0.5 * colwidth + flagx, bottommargin + row * rowheight + flagy, 0.3 , 0.3))
    #birthday2
    birthday = formule1data[i][4]
    d.add(transform_svg("SVG/calendar-blank.svg", leftmargin + col * colwidth + 0.5 * colwidth + birthdayx, bottommargin + row * rowheight + birthdayy, 0.5 , 0.5))
    d.add(String(leftmargin + col * colwidth + 0.5 * colwidth + birthdayx, bottommargin + row * rowheight + birthdayy + 6, birthday[:5], fontSize = 8, fillColor = colors.black))
    d.add(String(leftmargin + col * colwidth + 0.5 * colwidth + birthdayx, bottommargin + row * rowheight + birthdayy, birthday[6:10], fontSize = 8, fillColor = colors.black))
    #land2 9
    landcode = formule1data[i][9]
    d.add(transform_svg(lookupflag(landcode), col * colwidth + flagx, bottommargin + row * rowheight + flagy, 0.3 , 0.3))
    d.add(Line(leftmargin + col * colwidth, bottommargin + row * rowheight + 155, col * colwidth + colwidth - 10, bottommargin + row * rowheight + 155, strokeColor=colors.black, strokeWidth = 1))
    d.add(upperrightcorner(leftmargin + col * colwidth + colwidth - 14, bottommargin + row * rowheight + 145, 10.0, 1, colors.black))
    d.add(Line(leftmargin + col * colwidth + colwidth - 4, bottommargin + row * rowheight + 145, leftmargin + col * colwidth + colwidth - 4, bottommargin + row * rowheight + 105, strokeColor=colors.black, strokeWidth = 1))
    d.add(Line(leftmargin + col * colwidth, bottommargin + row * rowheight + 82, leftmargin + col * colwidth + 0.5 * colwidth - 8.0 - 4, bottommargin + row * rowheight + 82, strokeColor=colors.black, strokeWidth = 1))
    d.add(bottomrightcorner(leftmargin + col * colwidth + 0.5 * colwidth - 8.0 - 4, bottommargin + row * rowheight + 90, 8.0, 1, colors.black))
    d.add(Line(leftmargin + col * colwidth + 0.5 * colwidth - 4, bottommargin + row * rowheight + 90, leftmargin + col * colwidth + 0.5 * colwidth - 4, bottommargin + row * rowheight + 120, strokeColor=colors.black, strokeWidth = 1))
    d.add(Line(leftmargin + col * colwidth + 0.5 * colwidth, bottommargin + row * rowheight + 82, leftmargin + col * colwidth + colwidth - 8.0 - 4, bottommargin + row * rowheight + 82, strokeColor=colors.black, strokeWidth = 1))
    d.add(bottomrightcorner(leftmargin + col * colwidth + colwidth - 8.0 -4, bottommargin + row * rowheight + 90, 8.0, 1, colors.black))
    d.add(Line(leftmargin + col * colwidth + colwidth - 4, bottommargin + row * rowheight + 90, leftmargin + col * colwidth + colwidth - 4, bottommargin + row * rowheight + 120, strokeColor=colors.black, strokeWidth = 1))
    # logomiddle
    d.add(Line(leftmargin + col * colwidth + logox - 0.5 * logowidth, bottommargin + row * rowheight + logoy, col * colwidth + logox + 0.5 * logowidth, bottommargin + row * rowheight + logoy, strokeColor=colors.blue, strokeWidth=1))
    d.add(Line(col * colwidth + logox, bottommargin + row * rowheight + logoy - 0.5 * logoheight, col * colwidth + logox, bottommargin + row * rowheight + logoy + 0.5 * logoheight, strokeColor=colors.blue, strokeWidth=1))
    col = col + 1
    if col == 3:
        col = 0
        row = row - 1
#d.add(Line(595,0,595,842, strokeColor=colors.blue, strokeWidth=1))
#for i in range(5):
    #d.add(Line(0,i*rowheight+logoy,595,i*rowheight+logoy, strokeColor=colors.blue, strokeWidth=1))
renderPDF.drawToFile(d, 'PDF/Teams2026.pdf') 
key = input("Wait")
