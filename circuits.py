import os
import sys
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
my_canvas = canvas.Canvas('PDF/svg_on_canvas.pdf')
drawing = svg2rlg('SVG/F1.svg')
renderPDF.draw(drawing, my_canvas, 0, 40)
my_canvas.drawString(50, 30, 'My SVG Image')
my_canvas.save()
key = input("Wait")
