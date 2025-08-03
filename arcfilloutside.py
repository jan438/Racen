import os
import sys
import csv
import math
import unicodedata
from pathlib import Path
from datetime import datetime, date, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch, mm

outsidearea = "#9e9e9e"
circuitarea = "#ffa981"

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
my_canvas = canvas.Canvas("PDF/arcfilloutside.pdf")
my_canvas.setFillColor(HexColor(outsidearea))
p = my_canvas.beginPath()
p.arc(20.0, 20.0, 40.0, 40.0, startAng = 90, extent = 90)
p.lineTo(20, 40)
my_canvas.drawPath(p, fill=1, stroke=0)
my_canvas.setFillColor(HexColor(circuitarea))
p = my_canvas.beginPath()
p.arc(60.0, 60.0, 80.0, 80.0, startAng = 90, extent = 90)
p.lineTo(60, 80)
my_canvas.drawPath(p, fill=1, stroke=0)
my_canvas.save()
key = input("Wait")
