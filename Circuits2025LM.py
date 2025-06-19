import os
import sys
import csv
import geojson
from ics import Calendar, Event
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.graphics.shapes import *
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer

circuitscale = 0.20
flagscale = 0.015
flagcorrectionx = -30.0
flagcorrectiony = -30.0
A4_height = A4[1]
A4_width = A4[0]
left_padding = 0
bottom_padding = 0
width = A4_width
height = A4_height
arrowscale = 0.01
arrow_x = 0.0
arrow_y = 0.0

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
def dms_to_decimal(degrees, minutes, seconds, direction):
    decimal = degrees + (minutes / 60) + (seconds / 3600)
    if direction in ['S', 'W']:
        decimal *= -1
    return decimal
def GeoJSON_to_Canvas(circuitindex):
    width = 500
    height = 500
    g_min_x = 0
    g_min_y = 0
    g_max_x = 0
    g_max_y = 0
    with open("Data/" + circuitsdata[circuitindex][1] + ".geojson", 'r') as file:
        geojson_data = geojson.load(file)
    features = geojson_data['features']
    for feature in features:
        geometry = feature["geometry"]
        if geometry['type'] == 'LineString':
            coordinates = geometry["coordinates"]
            min_x = min_y = float('inf')
            max_x = max_y = float('-inf')
            coords = [coordinates]
            for linestring in coords:
               for point in linestring:
                    x, y = point
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
    g_min_x = min_x
    g_min_y = min_y
    g_max_x = max_x
    g_max_y = max_y
    scale_x = width / (g_max_x - g_min_x)
    scale_y = height / (g_max_y - g_min_y)
    scale = (scale_x, scale_y)
    translate = (min_x, min_y)
    startindex = int(circuitsdata[circuitindex][12])
    sect1 = int(circuitsdata[circuitindex][13])
    sect2 = int(circuitsdata[circuitindex][14])
    for linestring in coords:
        for i, point in enumerate(linestring):
            if i == startindex:
                startfinish_x = point[0]
                startfinish_y = point[1]
                startfinish_offset_x = (startfinish_x - g_min_x) * scale_x
                startfinish_offset_y = (startfinish_y - g_min_y) * scale_y
            if i == sect1:
                sect1_x = point[0]
                sect1_y = point[1]
                sect1_offset_x = (sect1_x - g_min_x) * scale_x
                sect1_offset_y = (sect1_y - g_min_y) * scale_y
            if i == sect2:
                sect2_x = point[0]
                sect2_y = point[1]
                sect2_offset_x = (sect2_x - g_min_x) * scale_x
                sect2_offset_y = (sect2_y - g_min_y) * scale_y
    return [startfinish_offset_x, startfinish_offset_y, sect1_offset_x, sect1_offset_y, sect2_offset_x, sect2_offset_y]
def transform_svg(svgfile, tx, ty, sx, sy): 
    svg_root = load_svg_file(svgfile)
    svgRenderer = SvgRenderer(svgfile)
    df1 = svgRenderer.render(svg_root)
    gimg = df1.asGroup()
    gimg.translate(tx, ty)
    gimg.scale(sx, sy)
    return gimg
if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
circuitsdata = []
file_to_open = "Data/Circuits2025.csv"
with open(file_to_open, 'r') as file:
    csvreader = csv.reader(file, delimiter = ';')
    count = 0
    for row in csvreader:
        circuitsdata.append(row)
        count += 1
my_canvas = canvas.Canvas('PDF/Circuits2025LM.pdf')
my_canvas.setFont("Helvetica", 10)
my_canvas.setTitle("Circuits2025")
my_canvas.setFillColorRGB(0,0,0)
my_canvas.rect(left_padding, bottom_padding, width, height, fill=1)
my_canvas.setFillColorRGB(255,170,0)
bottom_margin = 40
left_margin = 20
renderPDF.draw(scaleSVG("SVG/WorldMap.svg", 0.35), my_canvas, 120, 315)
drawing = svg2rlg('SVG/F1.svg')
renderPDF.draw(drawing, my_canvas, 100, 800)
rowcount = 6
colcount = 5
rowheight = 125
worldkaartx = 100.0
worldkaarty = 100.0
colwidth = 115
row = 0
col = 0
for i in range(count):
    if i == 11 or i == 13:
        col = col + 3
    [startfinish_offset_x, startfinish_offset_y, sect1_offset_x, sect1_offset_y, sect2_offset_x, sect2_offset_y] = GeoJSON_to_Canvas(i)
    circuit_x = col * colwidth
    circuit_y = row * rowheight
    renderPDF.draw(scaleSVG("SVG/" + circuitsdata[i][0] + "LM.svg", circuitscale), my_canvas, circuit_x + left_margin, circuit_y + bottom_margin)
    my_canvas.drawString(circuit_x + left_margin, circuit_y + bottom_margin - 12, circuitsdata[i][0])
    flag_x = startfinish_offset_x * circuitscale
    flag_y = startfinish_offset_y * circuitscale
    arrow1_x = sect1_offset_x * circuitscale
    arrow1_y = sect1_offset_y * circuitscale
    arrow2_x = sect2_offset_x * circuitscale
    arrow2_y = sect2_offset_y * circuitscale
    renderPDF.draw(scaleSVG("SVG/racingflag.svg", flagscale), my_canvas, circuit_x + left_margin + flag_x + flagcorrectionx * circuitscale, circuit_y + bottom_margin + flag_y + flagcorrectiony * circuitscale)
    renderPDF.draw(scaleSVG("SVG/" + circuitsdata[i][9] + ".svg", arrowscale), my_canvas, circuit_x + left_margin + arrow1_x, circuit_y + bottom_margin + arrow1_y)
    renderPDF.draw(scaleSVG("SVG/" + circuitsdata[i][9] + ".svg", arrowscale), my_canvas, circuit_x + left_margin + arrow2_x, circuit_y + bottom_margin + arrow2_y)
    worldlocx = worldkaartx + float(circuitsdata[i][3])
    worldlocy = worldkaarty + float(circuitsdata[i][4])
    my_canvas.circle(worldlocx, worldlocy, 2, fill = 1)
    col += 1
    if col == colcount:
        row += 1
        col = 0
my_canvas.save()
key = input("Wait")
