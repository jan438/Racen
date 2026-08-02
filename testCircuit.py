import os
import sys
import csv
import geojson
import math
import random
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.graphics.shapes import *
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer

circuitscale = 1.0
testscale = 0.2
flagcorrection = -5.0
sec1color = "#db4a25"   #red
sec2color = "#58fdff"   #blue
sec3color = "#fae44a"   #yellow

class rand():
    def __str__(self):
        return str(random.randint(0, 100))

class rgbset():
    def __str__(self):
        return str(random.randint(0, 255))

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
def tail(my_list, n):
    my_list = my_list[-n:] + my_list[:-n]
    return my_list
def dms_to_decimal(degrees, minutes, seconds, direction):
    decimal = degrees + (minutes / 60) + (seconds / 3600)
    if direction in ['S', 'W']:
        decimal *= -1
    return decimal
def get_angle(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    angle_radians = math.atan2(y2 - y1, x2 - x1)
    angle_degrees = math.degrees(angle_radians)
    normalized_angle = angle_degrees % 360
    return normalized_angle
def GeoJSON_to_SVG(cx, geojsonfile, svgfile):
    def coordinates_to_path(coordinates, scale, translate):
        path_data = ""
        for LineString in coordinates:
            for i, point in enumerate(LineString):
                x = (point[0] - translate[0]) * scale[0]
                y = (point[1] - translate[1]) * scale[1]
                command = "M" if i == 0 else "L"
                path_data += f"{command}{x},{height - y} "
        return path_data.strip()
    def nearestpoint(coordinates, coords):
        np = -1
        dist = float('inf')
        for linestring in coords:
            counter = 0
            for point in linestring:
                d = calculate_distance(point[0], point[1], coordinates[0], coordinates[1])
                if d < dist:
                    dist = d
                    np = counter
                counter += 1
        return np
    def calculate_distance(x1, y1, x2, y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    width = 500
    height = 500
    with open("Data/" + geojsonfile + ".geojson", 'r') as file:
        geojson_data = geojson.load(file)
    features = geojson_data['features']
    print(cx, "Count features", len(features))
    startindices = []
    start_x = []
    start_y = []
    start_a = []
    startfinishindex = 0
    for feature in features:
        geometry = feature["geometry"]
        properties = feature['properties']
        if geometry['type'] == 'LineString':
            coordinates = geometry["coordinates"]
            min_x = min_y = float('inf')
            max_x = max_y = float('-inf')
            coords = [coordinates]
            for linestring in coords:
               print(geojsonfile, "len", len(linestring))
               for point in linestring:
                    x, y = point
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
    scale_x = width / (max_x - min_x)
    scale_y = height / (max_y - min_y)
    scale = (scale_x, scale_y)
    translate = (min_x, min_y)
    for feature in features:
        geometry = feature["geometry"]
        properties = feature['properties']
        if geometry['type'] == 'Point' and properties['place'] == "startfinish":
            coordinates = geometry["coordinates"]
            startfinish_x = coordinates[0]
            startfinish_y = coordinates[1]
            npointstartfinish = nearestpoint(coordinates, coords)
            startindices.append(npointstartfinish)
            print("Nearest Point startfinish", npointstartfinish)
        elif geometry['type'] == 'Point' and properties['place'] == "startsector":
            coordinates = geometry["coordinates"]
            npoint = nearestpoint(coordinates, coords)
            startindices.append(npoint)
            start_x.append(coordinates[0])
            start_y.append(coordinates[1])
            start_a.append(0)
    if len(startindices) < 3:
        print("Insufficient startindices", startindices)
        return
    else:
        offset_x0 = (start_x[0] - min_x) * scale_x
        offset_y0 = (start_y[0] - min_y) * scale_y
        offset_y0 = height - offset_y0
        print(0, "x", round(offset_x0), "y", round(offset_y0))
        offset_x1 = (start_x[1] - min_x) * scale_x
        offset_y1 = (start_y[1] - min_y) * scale_y
        offset_y1 = height - offset_y1
        print(1, "x", round(offset_x1), "y", round(offset_y1))
    offset_x = (startfinish_x - min_x) * scale_x
    offset_y = (startfinish_y - min_y) * scale_y
    print("Startindexes", startindices[0], startindices[1], startindices[2])
    with open(svgfile, 'w') as f:
        f.write(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n')
        f.write(f'<defs><linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="red" /><stop offset="100%" stop-color="blue" /></linearGradient><linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="yellow" /><stop offset="100%" stop-color="green" /></linearGradient></defs>">\n')
        for feature in geojson_data['features']:
            geometry = feature['geometry']
            coords = geometry['coordinates']
            if geometry['type'] == 'LineString':
                print("Circuitsdata", svgfile, circuitsdata[cx][12], circuitsdata[cx][13], circuitsdata[cx][14])
                idx1 = 0
                idx2 = 88
                # idx1 68 idx2 35 idx3 86
                path = coordinates_to_path([coords[:idx2]], scale, translate)
                f.write(f'<path d="{path}" fill="url(#gradient1)"/>\n')
        f.write('</svg>')    
    return [offset_x, offset_y]
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
ran = rand()
rgb = rgbset()
svg1 = '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 1400 400">\n<rect width="1400" height="400"/>\n<defs>\n'
svg2 = '<linearGradient id="a" x1="'+str(ran)+'%" y1="'+str(ran)+'%" x2="'+str(ran)+'%" y2="'+str(ran)+'%">\n'
svg3 = '<stop offset="0%" style="stop-color:rgb('+str(rgb)+','+str(rgb)+','+str(rgb)+');stop-opacity:1" />\n'
svg4 = '<stop offset="100%" style="stop-color:rgb('+str(rgb)+','+str(rgb)+','+str(rgb)+');stop-opacity:1" />\n'
svg5 = '</linearGradient>\n</defs>\n<rect fill="url(#a)" width="1400" height="400"/>\n</svg>'
file = open("SVG/grad.svg", "w")
file.writelines("%s%s%s%s%s" % (svg1,svg2,svg3,svg4,svg5))
file.close()
circuitsdata = []
svgfile = "SVG/testCircuit.svg"
file_to_open = "Data/testCircuit.csv"
with open(file_to_open, 'r') as file:
    csvreader = csv.reader(file, delimiter = ';')
    count = 0
    for row in csvreader:
        circuitsdata.append(row)
        count += 1
for i in range(len(circuitsdata)):
    if circuitsdata[i][0] == "testCircuit":
        cx = i
        print(cx, "testCircuit")
        my_canvas = canvas.Canvas("PDF/testCircuit.pdf")
        my_canvas.setFont("Helvetica", 25)
        my_canvas.setTitle("testCircuit")
        bottom_margin = 5
        left_margin = 5
        drawing = svg2rlg('SVG/F1.svg')
        renderPDF.draw(drawing, my_canvas, 300, 750)
        name_x = 300
        name_y = 25
        print("GeoJSON_to_SVG", circuitsdata[cx][1], svgfile)
        [offset_x, offset_y] = GeoJSON_to_SVG(cx, circuitsdata[cx][1], svgfile)
        circuit_x = 0
        circuit_y = 0
        renderPDF.draw(scaleSVG("SVG/testCircuit.svg", circuitscale), my_canvas, circuit_x + left_margin, circuit_y + bottom_margin)
        my_canvas.drawString(circuit_x + left_margin + name_x, circuit_y + bottom_margin + name_y, svgfile)
        flag_x = offset_x * circuitscale
        flag_y = offset_y * circuitscale
        renderPDF.draw(scaleSVG("SVG/finishflag.svg", circuitscale), my_canvas, circuit_x + left_margin + flag_x + flagcorrection * circuitscale, circuit_y + bottom_margin + flag_y)
        renderPDF.draw(scaleSVG("SVG/grad.svg", testscale), my_canvas, left_margin, 500)
        renderPDF.draw(scaleSVG("SVG/gradpath1.svg", 5 * testscale), my_canvas, left_margin + 300, 500)
        renderPDF.draw(scaleSVG("SVG/gradpath2.svg", 5 * testscale), my_canvas, left_margin + 450, 500)
        renderPDF.draw(scaleSVG("SVG/gradpath3.svg", 5 * testscale), my_canvas, left_margin + 450, 400)
        my_canvas.save()
key = input("Wait")
