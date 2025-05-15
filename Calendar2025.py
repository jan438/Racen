import os
import calendar
import datetime
import os
import sys
import csv
import math
import unicodedata
import svgwrite
from svgwrite import Drawing
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.graphics.shapes import *
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer

monthnames = ["Januari","Februari","Maart","April","Mei","Juni","Juli","Augustus", "September","Oktober","November","December"]

def scaleSVG(svgfile, scaling_factor):
    svg_root = load_svg_file(svgfile)
    svgRenderer = SvgRenderer(svgfile)
    drawing = svgRenderer.render(svg_root)
    scaling_x = scaling_factor
    scaling_y = scaling_factor
    drawing.width = drawing.minWidth() * scaling_x
    drawing.height = drawing.height * scaling_y
    drawing.scale(scaling_x, scaling_y)
    return drawing

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
my_canvas = canvas.Canvas("PDF/Calendar2025.pdf")
my_canvas.setFont("Helvetica", 25)
my_canvas.setTitle("Calendar 2025")
my_canvas.bookmarkPage("Meaning_of_life")
my_canvas.linkAbsolute("Find the Meaning of Life", "Meaning_of_life", (0, 0, 6, 2), Border='[0 0 0]')
drawing = svg2rlg('SVG/F1.svg')
renderPDF.draw(drawing, my_canvas, 100, 800)
row = 0
col = 1
leftmargin = 75
bottommargin = 50
colwidth = 200
rowheight = 125
for i in range(12):
    renderPDF.draw(scaleSVG("SVG/" + monthnames[11 - i] + ".svg", 0.25), my_canvas, leftmargin + col * colwidth, bottommargin + row * rowheight)
    if i == 7:
        renderPDF.draw(scaleSVG("Flags/NL.svg", 0.25), my_canvas, leftmargin + col * colwidth, bottommargin + row * rowheight)
        renderPDF.draw(scaleSVG("SVG/clock-two-thirty.svg", 0.025), my_canvas, leftmargin + 20 + col * colwidth, bottommargin + row * rowheight)
    col -= 1
    if col == -1:
        row += 1
        col = 1
my_canvas.save()
key = input("Wait")
