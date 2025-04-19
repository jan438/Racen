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

styles = getSampleStyleSheet()

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
file_to_open = "Data/Formule12025.csv"
with open(file_to_open, 'r') as file:
    csvreader = csv.reader(file, delimiter = ';')
    count = 0
    for row in csvreader:
        formule1data.append(row)
        count += 1
print("Count:", count)
d = Drawing(595, 842)
pdfmetrics.registerFont(TTFont('LiberationSerif', 'LiberationSerif-Regular.ttf'))
text = "Hello, ReportLab!"
formule1font = "LiberationSerif"
font_size = 18
text_width = pdfmetrics.stringWidth(text, formule1font, font_size)
print(f"The width of the text '{text}' is {text_width} points.")
d.add(transform_svg("SVG/F1.svg", 297.5 - 60, 800, 1.1, 1.1))
rowheight = 160
colwidth = 297.5
halfcolwidth = 148.75
logox = 250
logoy = 130
row = 0
col = 0
flagx = 110 
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
    #team 0
    d.add(String(10 + col * colwidth, row * rowheight + 135, formule1data[i][0], fontSize = 22, fillColor = colors.black))
    #name2 7
    d.add(String(10 + col * colwidth, row * rowheight + 95, formule1data[i][7], fontSize = 18, fillColor = colors.black))
    #score2 8
    d.add(String(col * colwidth + halfcolwidth - 60, row * rowheight + 95, formule1data[i][8], font = "LiberationSerif", fontSize = 18, fillColor = colors.black))
    #surnane2 6
    d.add(String(10 + col * colwidth, row * rowheight + 110, formule1data[i][6], fontSize = 16, fillColor = colors.black))
    #name1 3
    d.add(String(col * colwidth + 0.5 * colwidth, row * rowheight + 95, formule1data[i][3], fontSize = 18, fillColor = colors.black))
    #score1 4
    d.add(String((col + 1) * colwidth - 60, row * rowheight + 95, formule1data[i][4], font = "LiberationSerif", fontSize = 18, fillColor = colors.black))
    #surname1 2
    d.add(String(col * colwidth + 0.5 * colwidth, row * rowheight + 110, formule1data[i][2], fontSize = 16, fillColor = colors.black))
    img = "Teams/" + formule1data[i][1] + ".png"
    d.add(Image(path = img, width = 270, height = 89, x = 10 + col * colwidth, y = row * rowheight))
    d.add(transform_svg("Logos/" + formule1data[i][1] + ".svg", logox - float(formule1data[i][10]) + col * colwidth, logoy - float(formule1data[i][11]) + row * rowheight,float(formule1data[i][12]), float(formule1data[i][13])))
    #land1 5
    landcode = formule1data[i][5]
    d.add(transform_svg(lookupflag(landcode), col * colwidth + halfcolwidth + flagx, row * rowheight + 90, 0.3 ,0.3))
    #land2 9
    landcode = formule1data[i][9]
    d.add(transform_svg(lookupflag(landcode), col * colwidth + flagx, row * rowheight + 90, 0.3 ,0.3))
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
