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
rowheight = 160
colwidth = 297.5
row = 0
col = 0
class MyLogo(_Symbol):
    def __init__(self):
        self.x = 215
        self.y = 712
        self.size = 100
        self.fillColor = colors.red

    def draw(self):
        g = shapes.Group()
        g.add(Circle(self.x + 9, self.y + 20, 26, fillColor = "#FEDDB9"))
        arrow = shapes.Polygon(points = [
        self.x + 26.1, self.y + 4.0,
        self.x + 11.2, self.y + 18.9,
        self.x + 14.5, self.y + 23.0,
        self.x + 7.2, self.y + 24.2,
        self.x, self.y + 26.1, # arrow point
        self.x + 1.9, self.y + 18.9,
        self.x + 3.8, self.y + 11.6,
        self.x + 7.2, self.y + 14.9,
        self.x + 22.1, self.y 
        ],
               fillColor = self.fillColor,
               strokeColor = None,
               strokeWidth=0)
        g.add(arrow)
        lab = Label()
        lab.setOrigin(self.x - 7, self.y + 40)
        lab.boxAnchor = 'ne'
        lab.angle = 45
        lab.boxStrokeColor = colors.black
        lab.setText("N")
        g.add(lab)
        return g
l = MyLogo()
d.add(l)
for i in range(count):
    print(i, formule1data[i][0], formule1data[i][1], "col", col, "row", row)
    d.add(String(col * colwidth, row * rowheight + 100, formule1data[i][0], fontSize = 25, fillColor = colors.black))
    d.add(String(col * colwidth + 0.5 * colwidth, row * rowheight + 72, formule1data[i][2], fontSize = 18, fillColor = colors.black))
    d.add(String(col * colwidth, row * rowheight + 72, formule1data[i][3], fontSize = 18, fillColor = colors.black))
    img = "Teams/" + formule1data[i][1] + ".png"
    d.add(Image(path = img, width = 232, height = 69, x = col * colwidth, y = row * rowheight))
    img = "Logos/" + formule1data[i][1] + ".png"
    d.add(Image(path = img, width = 65, height = 65, x = 232.5 + col * colwidth, y = row * rowheight))
    col = col + 1
    if col == 2:
        col = 0
        row = row + 1
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
