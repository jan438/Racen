import os
import sys
import csv
import math
import unicodedata
import calendar
import svgwrite
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

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)


def draw_svg_calendar(year, month, filename="SVG/calendar.svg"):
    # Create a new SVG drawing
    dwg = svgwrite.Drawing(filename, profile='tiny', size=("800px", "600px"))
    
    # Title
    title = f"{calendar.month_name[month]} {year}"
    dwg.add(dwg.text(title, insert=(300, 50), font_size="24px", font_family="Arial", fill="black"))
    
    # Days of the week
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, day in enumerate(days):
        dwg.add(dwg.text(day, insert=(100 + i * 100, 100), font_size="18px", font_family="Arial", fill="black"))
    
    # Calendar grid
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)
    
    for row, week in enumerate(month_days):
        for col, day in enumerate(week):
            if day != 0:  # Skip empty days
                x = 100 + col * 100
                y = 150 + row * 50
                dwg.add(dwg.text(str(day), insert=(x, y), font_size="16px", font_family="Arial", fill="black"))
    
    # Save the SVG file
    dwg.save()
    print(f"SVG calendar saved as {filename}")

# Example usage
draw_svg_calendar(2025, 5)
key = input("Wait")
