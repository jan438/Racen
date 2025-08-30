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
import cairosvg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.graphics.shapes import *
from pypdf import PdfReader, PdfWriter
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer

def processreport():
    merger = PdfWriter()

    if os.path.isfile("PDF/Calendar2026LC.pdf"):
        inputpdf = open("PDF/Calendar2026LC.pdf", "rb")
        merger.append(inputpdf)
        inputpdf.close()
    if os.path.isfile("PDF/Circuits2026LM.pdf"):
        inputpdf = open("PDF/Circuits2026LM.pdf", "rb")
        merger.append(inputpdf)
        inputpdf.close()
    if os.path.isfile("PDF/Teams2026.pdf"):
        inputpdf = open("PDF/Teams2026.pdf", "rb")
        merger.append(inputpdf)
        inputpdf.close()
    output = open("PDF/F1Totaal2026.pdf", "wb")
    merger.write(output)
    merger.close()
    output.close()
   
if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
processreport()
key = input("Wait")
