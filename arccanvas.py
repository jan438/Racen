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

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
my_canvas = canvas.Canvas("PDF/ArcCanvas.pdf")
my_canvas.setFillColor(HexColor('#FECDE5'))
p = my_canvas.beginPath()
p.moveTo(22.0, 32.0)
p.arcTo(2.0, 12.0, 22.0, 32.0, startAng = 90, extent = 90)
my_canvas.drawPath(p, fill=1, stroke=1)
my_canvas.save()
key = input("Wait")
