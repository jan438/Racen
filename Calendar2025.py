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
drawing = svg2rlg('SVG/F1.svg')
renderPDF.draw(drawing, my_canvas, 100, 800)
row = 0
col = 2
leftmargin = 25
bottommargin = 100
colwidth = 180
rowheight = 140
flagoffset = 155
linkx1 = 0
linky1 = 0
linkx2 = 10
linky2 = 10
linkarea = (linkx1, linky1, linkx2, linky2)
for i in range(12):
    renderPDF.draw(scaleSVG("SVG/" + monthnames[11 - i] + ".svg", 0.30), my_canvas, leftmargin + col * colwidth, bottommargin + row * rowheight)
    if i == 4:
        renderPDF.draw(scaleSVG("Flags/NL.svg", 0.25), my_canvas, leftmargin + flagoffset + col * colwidth, bottommargin + row * rowheight + 4)
        renderPDF.draw(scaleSVG("SVG/racingcar.svg", 0.025), my_canvas, leftmargin + flagoffset - 20 + col * colwidth, bottommargin + row * rowheight + 9)
        linkx1 = leftmargin + flagoffset + col * colwidth
        linky1 = bottommargin + row * rowheight + 9
        linkx2 = linkx1 + 20
        linky2 = linky1 + 10
        linkarea = (linkx1, linky1, linkx2, linky2)
        #my_canvas.linkAbsolute("Find the Meaning of Life", "Meaning_of_life", linkarea, addtopage = 1, thickness = 1, color = colors.green)
        my_canvas.linkAbsolute("Find the Meaning of Life", "Meaning_of_life", linkarea, addtopage = 1, thickness = 0, color = None)
    col -= 1
    if col == -1:
        row += 1
        col = 2
my_canvas.showPage()
drawing = svg2rlg('SVG/F1.svg')
renderPDF.draw(drawing, my_canvas, 100, 800)
renderPDF.draw(scaleSVG("SVG/time.svg", 0.025), my_canvas, 50, 30)
my_canvas.bookmarkPage("Meaning_of_life", fit = "XYZ", left = 50,top = 30, zoom = 4)
my_canvas.save()
key = input("Wait")
