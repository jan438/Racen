import os
import sys
import csv
import math
import unicodedata
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
# Open the image with a palette
image = PILImage.open('Teams/642.png')
# Convert the image to RGBA
rgba_image = image.convert('RGBA')
# Create a mask image with the same size as the original
mask = PILImage.new('L', rgba_image.size, 0)
# Define the color to be made transparent (e.g., white)
transparent_color = (255, 255, 255)
# Get the data of the image
data = rgba_image.getdata()
# Create a new mask data list
mask_data = []
for item in data:
    if item[:3] == transparent_color:
        mask_data.append(0)  # Fully transparent
    else:
        mask_data.append(255)  # Fully opaque
# Update the mask data
mask.putdata(mask_data)
# Apply the mask to the image
rgba_image.putalpha(mask)
# Save the image in RGBA format
rgba_image.save('PDF/whitetotransparant.png')

image = PILImage.open("Teams/642.png").convert("RGBA")
new_image = PILImage.new("RGBA", image.size, "WHITE")
new_image.paste(image, mask=image)

new_image.convert("RGB").save("test.jpg")
key = input("Wait")
