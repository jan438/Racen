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
from reportlab.lib.units import inch
from reportlab.lib.colors import blue, green, black, red, pink, gray, brown, purple, orange, yellow, white, lightgrey
from reportlab.pdfbase import pdfmetrics  
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Image, Spacer, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.graphics.shapes import *
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import *
from reportlab.graphics import shapes
from reportlab.graphics import widgetbase
from reportlab.graphics.widgetbase import Widget
from reportlab.graphics.widgets import signsandsymbols
from reportlab.graphics.widgets.signsandsymbols import _Symbol
from reportlab.graphics.charts.textlabels import Label
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer

formule1font = "LiberationSerif"

styles = getSampleStyleSheet()

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
formule1data = []
file_to_open = "Data/Formule12025.csv"
with open(file_to_open, 'r') as file:
    csvreader = csv.reader(file, delimiter = ';')
    count = 0
    for row in csvreader:
        formule1data.append(row)
        count += 1
print("Count:", count)
d = Drawing(595, 842)
svgfile =  "SVG/F1.svg"
svg_root = load_svg_file(svgfile)
svgRenderer = SvgRenderer(svgfile)
df1 = svgRenderer.render(svg_root)
gf1 = df1.asGroup()
gf1.translate(297.5 - 60, 800)
gf1.scale(1.1, 1.1)
d.add(gf1)
rowheight = 160
colwidth = 297.5
logox = 250
logoy = 130
row = 0
col = 0
class MyLogo(_Symbol):
    def __init__(self):
        self.x = 215
        self.y = 780
        self.size = 100
        self.fillColor = colors.blue

    def draw(self):
        g = shapes.Group()
        g.add(Circle(self.x + 9, self.y + 20, 26, fillColor = "#FEDDB9"))
        logo = shapes.Polygon(
        points=[59.68, 762.591, 58.224, 7154.294, 110.626, 788.064, 61.135, 764.774],
               fillColor = self.fillColor,
               strokeColor = None,
               strokeWidth=0)
        g.add(logo)
        lab = Label()
        lab.setOrigin(self.x - 7, self.y + 40)
        lab.boxAnchor = 'ne'
        lab.angle = 45
        lab.boxStrokeColor = colors.black
        lab.setText("")
        g.add(lab)
        return g
#l = MyLogo()
#d.add(l)
for i in range(count):
    d.add(String(10 + col * colwidth, row * rowheight + 135, formule1data[i][0], fontSize = 22, fillColor = colors.black))
    d.add(String(10 + col * colwidth, row * rowheight + 95, formule1data[i][5], fontSize = 18, fillColor = colors.black))
    d.add(String(10 + col * colwidth, row * rowheight + 105, formule1data[i][4], fontSize = 18, fillColor = colors.black))
    d.add(String(col * colwidth + 0.5 * colwidth, row * rowheight + 95, formule1data[i][3], fontSize = 18, fillColor = colors.black))
    d.add(String(col * colwidth + 0.5 * colwidth, row * rowheight + 105, formule1data[i][2], fontSize = 18, fillColor = colors.black))
    img = "Teams/" + formule1data[i][1] + ".png"
    d.add(Image(path = img, width = 270, height = 89, x = 10 + col * colwidth, y = row * rowheight))
    svgfile = "Logos/" + formule1data[i][1] + ".svg"
    svg_root = load_svg_file(svgfile)
    svgRenderer = SvgRenderer(svgfile)
    df1 = svgRenderer.render(svg_root)
    gf1 = df1.asGroup()
    gf1.translate(logox - float(formule1data[i][6]) + col * colwidth, logoy - float(formule1data[i][7]) + row * rowheight)
    gf1.scale(float(formule1data[i][8]), float(formule1data[i][9]))
    d.add(gf1)
    col = col + 1
    if col == 2:
        col = 0
        row = row + 1
#d.add(Line(logox,0,logox,842, strokeColor=colors.blue, strokeWidth=1))
#d.add(Line(logox + colwidth,0,logox + colwidth,842, strokeColor=colors.blue, strokeWidth=1))
#d.add(Line(595,0,595,842, strokeColor=colors.blue, strokeWidth=1))
#for i in range(5):
    #d.add(Line(0,i*rowheight+logoy,595,i*rowheight+logoy, strokeColor=colors.blue, strokeWidth=1))
renderPDF.drawToFile(d, 'PDF/Formule12025.pdf') 
pdfmetrics.registerFont(TTFont('Ubuntu', 'Ubuntu-Regular.ttf'))
pdfmetrics.registerFont(TTFont('UbuntuBold', 'Ubuntu-Bold.ttf'))
pdfmetrics.registerFont(TTFont('UbuntuItalic', 'Ubuntu-Italic.ttf'))
pdfmetrics.registerFont(TTFont('UbuntuBoldItalic', 'Ubuntu-BoldItalic.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerif', 'LiberationSerif-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerifBold', 'LiberationSerif-Bold.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerifItalic', 'LiberationSerif-Italic.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerifBoldItalic', 'LiberationSerif-BoldItalic.ttf'))
key = input("Wait")
