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
arrowscale = 0.0075
arrow_x = 0.0
arrow_y = 0.0
rulerscale = 0.034
clockwisescale = 0.01

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
def rotatescaleSVG(svgfile, angle, scaling_factor):
    svg_root = load_svg_file(svgfile)
    svgRenderer = SvgRenderer(svgfile)
    namespace = {'svg': 'http://www.w3.org/2000/svg'}
    paths = svg_root.findall('.//svg:path', namespaces=namespace)
    path_data = [path.attrib.get('d') for path in paths if 'd' in path.attrib]
    print("Before", path_data[0])
    path_data[0] = rotate_path(path_data[0], angle)
    print("After", path_data[0])
    drawing = svgRenderer.render(svg_root)
    scaling_x = scaling_factor
    scaling_y = scaling_factor
    drawing.width = drawing.minWidth() * scaling_x
    drawing.height = drawing.height * scaling_y
    drawing.scale(scaling_x, scaling_y)
    return drawing
def rotate_path(path, angle_degrees):
    return path
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
    if circuitindex == 13:
        print("Todo", circuitsdata[circuitindex][0], "sf", round(startfinish_offset_x), round(startfinish_offset_y), "s2", round(sect2_offset_x), round(sect2_offset_y), "s3", round(sect3_offset_x), round(sect3_offset_y))
    startfinish_offset_x = int(circuitsdata[circuitindex][15])
    startfinish_offset_y = int(circuitsdata[circuitindex][16])
    sect2_offset_x = int(circuitsdata[circuitindex][18])
    sect2_offset_y = int(circuitsdata[circuitindex][19])
    sect2_angle = circuitsdata[circuitindex][20][1:]
    sect3_offset_x = int(circuitsdata[circuitindex][21])
    sect3_offset_y = int(circuitsdata[circuitindex][22])
    sect3_angle = circuitsdata[circuitindex][23][1:]
    return [startfinish_offset_x, startfinish_offset_y, sect2_offset_x, sect2_offset_y, sect2_angle, sect3_offset_x, sect3_offset_y, sect3_angle, length]
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
    [startfinish_offset_x, startfinish_offset_y, sect2_offset_x, sect2_offset_y, sect2_angle, sect3_offset_x, sect3_offset_y, sect3_angle, length] = GeoJSON_to_Canvas(i)
    circuit_x = col * colwidth
    circuit_y = row * rowheight
    renderPDF.draw(scaleSVG("SVG/" + circuitsdata[i][0] + "LM.svg", circuitscale), my_canvas, circuit_x + left_margin, circuit_y + bottom_margin)
    my_canvas.setFont("Helvetica", 9)
    my_canvas.setFillColorRGB(255,170,0)
    displayname = circuitsdata[i][24]
    namewidth = pdfmetrics.stringWidth(displayname, "Helvetica", 9)
    my_canvas.drawString(circuit_x + (left_margin + colwidth - namewidth) / 2, circuit_y + bottom_margin - 12, displayname)
    flag_x = startfinish_offset_x * circuitscale
    flag_y = startfinish_offset_y * circuitscale
    arrow1_x = sect2_offset_x * circuitscale
    arrow1_y = sect2_offset_y * circuitscale
    arrow2_x = sect3_offset_x * circuitscale
    arrow2_y = sect3_offset_y * circuitscale
    renderPDF.draw(scaleSVG("SVG/racingflag.svg", flagscale), my_canvas, circuit_x + left_margin + flag_x + flagcorrectionx * circuitscale, circuit_y + bottom_margin + flag_y + flagcorrectiony * circuitscale)
    renderPDF.draw(scaleSVG("SVG/a" + sect2_angle + ".svg", arrowscale), my_canvas, circuit_x + left_margin + arrow1_x, circuit_y + bottom_margin + arrow1_y)
    renderPDF.draw(scaleSVG("SVG/a" + sect3_angle + ".svg", arrowscale), my_canvas, circuit_x + left_margin + arrow2_x, circuit_y + bottom_margin + arrow2_y)
    renderPDF.draw(scaleSVG("SVG/ruler.svg", rulerscale), my_canvas, circuit_x + left_margin + int(circuitsdata[i][10]), circuit_y + bottom_margin + int(circuitsdata[i][11]))
    my_canvas.setFont("Helvetica", 8)
    my_canvas.setFillColorRGB(170,255,127)
    my_canvas.drawString(circuit_x + left_margin + 5 + int(circuitsdata[i][10]), circuit_y + bottom_margin + 7 + int(circuitsdata[i][11]) + 10, f"{length}")
    if circuitsdata[i][9] == "a":
        renderPDF.draw(scaleSVG("SVG/anticlockwise.svg", clockwisescale), my_canvas, circuit_x + left_margin + 8 + int(circuitsdata[i][10]), circuit_y + bottom_margin + int(circuitsdata[i][11]) - 2)
    else:
        renderPDF.draw(scaleSVG("SVG/clockwise.svg", clockwisescale), my_canvas, circuit_x + left_margin + 8 + int(circuitsdata[i][10]), circuit_y + bottom_margin + int(circuitsdata[i][11]) - 2)
    worldlocx = worldkaartx + float(circuitsdata[i][3])
    worldlocy = worldkaarty + float(circuitsdata[i][4])
    my_canvas.circle(worldlocx, worldlocy, 2, fill = 1)
    col += 1
    if col == colcount:
        row += 1
        col = 0
my_canvas.save()
key = input("Wait")
