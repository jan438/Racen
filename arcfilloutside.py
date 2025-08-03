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
col = 13
row = 17
arcdim = 20

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
my_canvas = canvas.Canvas("PDF/arcfilloutside.pdf")
my_canvas.setFillColor(HexColor(outsidearea))
p = my_canvas.beginPath()
p.arc(col, row, col + arcdim, row + arcdim, startAng = 90, extent = 90)
p.lineTo(col, row + arcdim)
my_canvas.drawPath(p, fill=1, stroke=0)
my_canvas.save()
key = input("Wait")
