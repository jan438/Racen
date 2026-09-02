import os
import sys
import csv
import geojson
import random
import math
from math import radians, cos, sin
from ics import Calendar, Event
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics  
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics  
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor
from reportlab.graphics.shapes import *
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer
import xml.etree.ElementTree as ET

circuitscale = 0.23
altitudescale = 0.15
flagscale = 0.015
locationscale = 0.012
flagcorrectionx = -30.0
flagcorrectiony = -30.0
A4_height = A4[1]
A4_width = A4[0]
left_padding = 0
bottom_padding = 0
width = A4_width
height = A4_height
arrowscale = 0.0075
arrow_x = 0.0
arrow_y = 0.0
circlescale = 0.35
rulerscale = 0.034
clockwisescale = 0.010
turnscale = 0.02
worldmapscale = 0.6
worldmap_x = 118
worldmap_y = 285
cirfont = "LiberationSerif"
  
circuitcolors = ["#88255F", "#DB4035", "#FF9933", "#FAD000", "#AFB83B", "#7ECC49", "#E7E84F", "#299438", "#A8A202", "#158FAD", "#14AAF5", "#CD0027", "#4073FF", "#D38895", "#884DFF", "#AF38EB", "#EB96EB", "#E05194", "#FF8D85", "#808080", "#FFE001", "#CCAC93", "#9A6324", "#80FF80"]

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
def scalecolorSVG(svgfile, scaling_factor, color):
    svg_root = load_svg_file(svgfile)
    svg_root.set("fill", color)
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
    def get_angle(point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        angle_radians = math.atan2(y2 - y1, x2 - x1)
        angle_degrees = math.degrees(angle_radians)
        normalized_angle = round((angle_degrees % 360) / 10) * 10
        if normalized_angle == 360:
            arrow_id = "000"
        elif normalized_angle < 10:
            arrow_id = "00" + str(normalized_angle)
        elif normalized_angle < 100:
            arrow_id = "0" + str(normalized_angle)
        else:
            arrow_id = str(normalized_angle)
        return arrow_id
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
        properties = feature['properties']
        if geometry['type'] == 'LineString':
            length = properties['length']
            altitude = properties['altitude']
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
    sect2 = int(circuitsdata[circuitindex][13])
    sect3 = int(circuitsdata[circuitindex][14])
    for linestring in coords:
        for i, point in enumerate(linestring):
            if i == startindex:
                startfinish_x = point[0]
                startfinish_y = point[1]
                startfinish_offset_x = (startfinish_x - g_min_x) * scale_x
                startfinish_offset_y = (startfinish_y - g_min_y) * scale_y
            if i == sect2:
                sect2_x = point[0]
                sect2_y = point[1]
                sect2_offset_x = (sect2_x - g_min_x) * scale_x
                sect2_offset_y = (sect2_y - g_min_y) * scale_y
                point2 = linestring[i + 1]
                sect2_angle = get_angle(point, point2)
            if i == sect3:
                sect3_x = point[0]
                sect3_y = point[1]
                sect3_offset_x = (sect3_x - g_min_x) * scale_x
                sect3_offset_y = (sect3_y - g_min_y) * scale_y
                point2 = linestring[i + 1]
                sect3_angle = get_angle(point, point2)
    startfinish_offset_x = int(circuitsdata[circuitindex][15])
    startfinish_offset_y = int(circuitsdata[circuitindex][16])
    sect2_offset_x = int(circuitsdata[circuitindex][18])
    sect2_offset_y = int(circuitsdata[circuitindex][19])
    sect2_angle = circuitsdata[circuitindex][20][1:]
    sect3_offset_x = int(circuitsdata[circuitindex][21])
    sect3_offset_y = int(circuitsdata[circuitindex][22])
    sect3_angle = circuitsdata[circuitindex][23][1:]
    return [startfinish_offset_x, startfinish_offset_y, sect2_offset_x, sect2_offset_y, sect2_angle, sect3_offset_x, sect3_offset_y, sect3_angle, length, altitude]
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
file_to_open = "Data/Circuits2027.csv"
with open(file_to_open, 'r') as file:
    csvreader = csv.reader(file, delimiter = ';')
    count = 0
    for row in csvreader:
        circuitsdata.append(row)
        count += 1
pdfmetrics.registerFont(TTFont('LiberationSerif', 'LiberationSerif-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerifBold', 'LiberationSerif-Bold.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerifItalic', 'LiberationSerif-Italic.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerifBoldItalic', 'LiberationSerif-BoldItalic.ttf'))
my_canvas = canvas.Canvas('PDF/Circuits2027LM.pdf')
my_canvas.setFont(cirfont, 10)
my_canvas.setTitle("Circuits2027")
my_canvas.setFillColorRGB(0,0,0)
my_canvas.rect(left_padding, bottom_padding, width, height, fill=1)
my_canvas.setFillColorRGB(255,170,0)
bottom_margin = 20
left_margin = 10
renderPDF.draw(scaleSVG("SVG/world-map.svg", worldmapscale), my_canvas, worldmap_x, worldmap_y)
drawing = svg2rlg('SVG/F1.svg')
renderPDF.draw(drawing, my_canvas, 100, 800)
my_canvas.setFillColorRGB(255, 255, 255)
my_canvas.setFont(cirfont, 25)
my_canvas.drawString(100, 775, "2027 Circuits")
rowcount = 6
colcount = 5
rowheight = 125
colwidth = 115
row = 5
col = 0
legendcol = 0
legendrow = 0
for i in range(count):
    if i == 11 or i == 13:
        col = col + 3
    [startfinish_offset_x, startfinish_offset_y, sect2_offset_x, sect2_offset_y, sect2_angle, sect3_offset_x, sect3_offset_y, sect3_angle, length, altitude] = GeoJSON_to_Canvas(i)
    circuit_x = left_margin + col * colwidth
    circuit_y = bottom_margin + row * rowheight
    altitudedrawing = scaleSVG("SVG/" + circuitsdata[i][1] + "A.svg", altitudescale)
    renderPDF.draw(altitudedrawing, my_canvas, circuit_x + 0, circuit_y + 20)
    circuitdrawing = scaleSVG("SVG/" + circuitsdata[i][0] + "LM.svg", circuitscale)
    renderPDF.draw(circuitdrawing, my_canvas, circuit_x + (colwidth - circuitdrawing.width) / 2, circuit_y + (rowheight - circuitdrawing.height) / 2 + 8)
    my_canvas.setFont(cirfont, 9)
    my_canvas.setFillColorRGB(255,170,0)
    displayname = circuitsdata[i][24]
    namewidth = pdfmetrics.stringWidth(displayname, cirfont, 9)
    my_canvas.drawString(circuit_x + (colwidth - namewidth) / 2, circuit_y, displayname)
    flag_x = startfinish_offset_x * circuitscale
    flag_y = startfinish_offset_y * circuitscale
    arrow1_x = sect2_offset_x * circuitscale
    arrow1_y = sect2_offset_y * circuitscale
    arrow2_x = sect3_offset_x * circuitscale
    arrow2_y = sect3_offset_y * circuitscale
    info_x = float(circuitsdata[i][10])
    info_y = float(circuitsdata[i][11])
    if info_x > 0:
        circledrawing = scaleSVG("SVG/circle.svg", circlescale)
        renderPDF.draw(circledrawing, my_canvas, circuit_x + info_x - circledrawing.width / 2, circuit_y + info_y - circledrawing.height / 2)
        my_canvas.setFont(cirfont, 7)
        my_canvas.setFillColorRGB(170,255,127)
        lapsstr = circuitsdata[i][2]
        my_canvas.drawString(circuit_x + info_x - 4, circuit_y + info_y - 2, lapsstr)
    worldlocx = worldmap_x + float(circuitsdata[i][3])
    worldlocy = worldmap_y + float(circuitsdata[i][4])
    my_canvas.setFillColor(HexColor(circuitcolors[i]))
    my_canvas.setStrokeColor(HexColor("#000000"))
    if worldlocx > worldmap_x:
        renderPDF.draw(scalecolorSVG("SVG/location.svg", locationscale, circuitcolors[i]), my_canvas, worldlocx, worldlocy)
    if circuitsdata[i][9] == "a":
        renderPDF.draw(scalecolorSVG("SVG/turnleft.svg", turnscale, circuitcolors[i]), my_canvas, circuit_x +  (colwidth - namewidth) / 2 - 15, circuit_y)
    else:
        renderPDF.draw(scalecolorSVG("SVG/turnright.svg", turnscale, circuitcolors[i]), my_canvas, circuit_x + (colwidth - namewidth) / 2 - 15, circuit_y)
    legend_x = worldmap_x + 30 + legendcol * 52
    legend_y = worldmap_y - 40 + legendrow * 10
    my_canvas.setFillColor(HexColor("#FFFFFF"))
    my_canvas.setLineWidth(1)
    my_canvas.setStrokeColor(HexColor("#ffffff"))
#    my_canvas.rect(circuit_x, circuit_y, colwidth, rowheight, stroke=1, fill=0)
    legendcol += 1
    if legendcol == 6:
        legendrow = legendrow + 1
        legendcol = 0
    col += 1
    if col == colcount:
        row = row - 1
        col = 0
my_canvas.save()
key = input("Wait")
