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
my_canvas.arc(2.0, 12.0, 22.0, 32.0, startAng = 90, extent = 90)
my_canvas.setFillColorRGB(1, 0.6, 0.8)
p = my_canvas.beginPath()
p.moveTo(0.2*inch, 0.2*inch)
p.arcTo(inch, inch, 2.5*inch,2*inch, startAng=-30, extent=135)
p.arc(3*inch, inch, 4*inch, 2.5*inch, startAng=-45, extent=270)
my_canvas.drawPath(p, fill=1, stroke=1)
my_canvas.save()
key = input("Wait")
