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
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer
from PIL import Image as PILImage
from io import StringIO

class MyLogo(_Symbol):
    def __init__(self):
        self.x = 215
        self.y = 780
        self.size = 100
        self.fillColor = colors.blue

    def draw(self):
        g = shapes.Group()
        g.add(Circle(self.x + 9, self.y + 20, 26, fillColor = "#FEDDB9"))
        lab = Label()
        lab.setOrigin(self.x - 7, self.y + 40)
        lab.boxAnchor = 'ne'
        lab.angle = 45
        lab.boxStrokeColor = colors.black
        lab.setText("abc")
        g.add(lab)
        return g
        
class MyArc(_Symbol):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.fillColor = colors.blue
        self.strokeColor = colors.purple
        
    def mycircle(self, x, y, radius, direction, startdegree, smooth):
    # 0 raden
    # cos(0) = 1 sin(0) = 0
    # sin(30) = 0.5
        print("cos0", cos(0), "sin0", sin(0))
        print("sin30", sin(radians(30)))
        bzpoints = [x+cos(radians(0))*radius, y+sin(radians(0))*radius, 
        x+cos(radians(30))*radius, y+sin(radians(30))*radius, 
        x+cos(radians(60))*radius, y+sin(radians(60))*radius, 
        x+cos(radians(90))*radius, y+sin(radians(90))*radius]
        bzcurve = shapes.PolyLine(
        points = bzpoints,
                 strokeColor = self.strokeColor)
        return bzcurve

    def draw(self):
        g = shapes.Group()
        logo1 = shapes.Polygon(
        points=[self.x + 1.0, self.y + 2.0, self.x + 40.0, self.y + 30.0, self.x + 60.0, self.y + 70.0],
               fillColor = self.fillColor,
               strokeColor = self.strokeColor,
               strokeWidth = 5)
        g.add(logo1)
        logo2 = shapes.PolyLine(
        points=[self.x + 81.0, self.y + 102.0, self.x + 90.0, self.y + 43.0, self.x + 160.0, self.y + 170.0],
               strokeColor = self.strokeColor,
               strokeWidth = 5)
        g.add(logo2)
        bzcurve1 = self.mycircle(300, 400, 100.0, -1, 0, 3)
        g.add(bzcurve1)
        return g

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
d = Drawing(595, 842)
l = MyLogo()
d.add(l)
a = MyArc(115, 200)
d.add(a)
renderPDF.drawToFile(d, 'PDF/Arc.pdf') 
key = input("Wait")
