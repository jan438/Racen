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
col = 0
row = 6
arcdim = 20
colwidth = 148
rowheight = 120

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
my_canvas = canvas.Canvas("PDF/arcfilloutside.pdf")
my_canvas.setFillColor(HexColor(outsidearea))
my_canvas.setStrokeColor(HexColor(outsidearea))
for i in range(24):
    p = my_canvas.beginPath()
    p.arc(col * colwidth + 2.0, row * rowheight + 12.0, col * colwidth + 2.0 + arcdim, row * rowheight + 12.0 + arcdim, startAng = 90, extent = 90)
    p.lineTo(col * colwidth + 2.0, row * rowheight + 12.0 + arcdim)
    my_canvas.drawPath(p, fill=1, stroke=0)
    p = my_canvas.beginPath()
    p.arc(col * colwidth + 120.0, row * rowheight - 80.0, col * colwidth + 140.0, row * rowheight - 60.0, startAng = 270, extent = 90)
    p.lineTo(col * colwidth + 140.0, row * rowheight - 80.0)
    my_canvas.drawPath(p, fill = 1, stroke = 0)
    col += 1
    if col == 4:
        col = 0
        row -= 1
my_canvas.save()
key = input("Wait")
