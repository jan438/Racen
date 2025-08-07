import os
import sys
import csv
import geojson
import math
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.graphics.shapes import *
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer

circuitscale = 1.0
flagcorrection = -5.0
cx = 3
sec1color = "#db4a25"   #red
sec2color = "#58fdff"   #blue
sec3color = "#fae44a"   #yellow

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
def GeoJSON_to_SVG(geojsonfile, svgfile):
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
    print("Count features", len(features))
    startindices = []
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
    if len(startindices) < 3:
        print("Insufficient startindices", startindices)
        return
    offset_x = (startfinish_x - min_x) * scale_x
    offset_y = (startfinish_y - min_y) * scale_y
    print("Startindexes", startindices[0], startindices[1], startindices[2])
    with open("SVG/" + svgfile + "LM.svg", 'w') as f:
        f.write(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n')
        for feature in geojson_data['features']:
            geometry = feature['geometry']
            coords = geometry['coordinates']
            if geometry['type'] == 'LineString':
                print("Circuitsdata", circuitsdata[cx][0], circuitsdata[cx][12], circuitsdata[cx][13], circuitsdata[cx][14])
                idx1 = int(circuitsdata[cx][12])
                idx2 = int(circuitsdata[cx][13])
                idx3 = int(circuitsdata[cx][14])
                if cx == 0:
                    path = coordinates_to_path([coords[idx1:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx2:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx3:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                elif cx == 1:
                    path = coordinates_to_path([coords[idx3:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[:idx1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx1 - 1:idx2]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx2 - 1:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                elif cx == 2:
                    path = coordinates_to_path([coords[idx3:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx1:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx2:idx1 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                elif cx == 3:
                    path = coordinates_to_path([coords[idx1:idx2]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                    #path = coordinates_to_path([coords[idx2:idx3 + 1]], scale, translate)
                    #f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx3:idx1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                elif cx == 4:
                    path = coordinates_to_path([coords[idx1:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx2 - 1:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                    path = coordinates_to_path([coords[idx3 - 1:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[:idx1 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                elif cx == 14:
                    path = coordinates_to_path([coords[:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx3 - 1:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx2 - 1:idx1 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                    path = coordinates_to_path([coords[idx1 - 1:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                elif cx == 5:
                    path = coordinates_to_path([coords[idx1:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx2 - 1:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx3 - 1:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                elif cx == 6:
                    path = coordinates_to_path([coords[idx1:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx2:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx3:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                elif cx == 7:
                    path = coordinates_to_path([coords[idx2:idx3]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx3 - 1:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                elif cx == 8:
                    path = coordinates_to_path([coords[:idx2]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx2 - 1:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx3 - 1:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                elif cx == 9:
                    path = coordinates_to_path([coords[:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx2 - 1:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx3 - 1:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                elif cx == 10:
                    path = coordinates_to_path([coords[:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx2:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx3:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                elif cx == 11:
                    path = coordinates_to_path([coords[:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx2 - 1:idx3]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx3 - 1:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                elif cx == 12:
                    path = coordinates_to_path([coords[idx2:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx3 - 1:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                elif cx == 13:
                    path = coordinates_to_path([coords[idx2 - 1:idx1 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                    path = coordinates_to_path([coords[idx3:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx1:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                elif cx == 15:
                    path = coordinates_to_path([coords[idx2 - 1:idx1 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                    path = coordinates_to_path([coords[idx3 - 1:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx1 - 1:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                elif cx == 16:
                    path = coordinates_to_path([coords[:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx2 - 1:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx3 - 1:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                elif cx == 17:
                    path = coordinates_to_path([coords[:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx2 - 1:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx3:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                elif cx == 18:
                    path = coordinates_to_path([coords[idx3 - 1:idx1 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                    path = coordinates_to_path([coords[:idx3]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx2:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx1:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                elif cx == 19:
                    path = coordinates_to_path([coords[:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx2:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx3:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                elif cx == 20:
                    path = coordinates_to_path([coords[:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx2:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx3:idx1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                    path = coordinates_to_path([coords[idx1:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx1 - 1:idx1 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                elif cx == 21:
                    path = coordinates_to_path([coords[idx2 - 1:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                    path = coordinates_to_path([coords[idx3 - 1:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[:idx3]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                elif cx == 22:
                    path = coordinates_to_path([coords[:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx2 - 1:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx3 - 1:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                elif cx == 23:
                    path = coordinates_to_path([coords[idx1:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx2 - 1:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx3 - 1:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
                else:
                    path = coordinates_to_path([coords[idx1:idx2 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec1color}"/>\n')
                    path = coordinates_to_path([coords[idx2 - 1:idx3 + 1]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec2color}"/>\n')
                    path = coordinates_to_path([coords[idx3 - 1:]], scale, translate)
                    f.write(f'<path d="{path}" fill="none" stroke-width="7" stroke="{sec3color}"/>\n')
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
circuitsdata = []
file_to_open = "Data/Circuits2026.csv"
with open(file_to_open, 'r') as file:
    csvreader = csv.reader(file, delimiter = ';')
    count = 0
    for row in csvreader:
        circuitsdata.append(row)
        count += 1
my_canvas = canvas.Canvas("PDF/" + circuitsdata[cx][0] + "2025LM.pdf")
my_canvas.setFont("Helvetica", 25)
my_canvas.setTitle(circuitsdata[cx][0])
bottom_margin = 5
left_margin = 5
drawing = svg2rlg('SVG/F1.svg')
renderPDF.draw(drawing, my_canvas, 300, 750)
name_x = 300
name_y = 25
[offset_x, offset_y] = GeoJSON_to_SVG(circuitsdata[cx][1], circuitsdata[cx][0])
circuit_x = 0
circuit_y = 0
renderPDF.draw(scaleSVG("SVG/" + circuitsdata[cx][0] + "LM.svg", circuitscale), my_canvas, circuit_x + left_margin, circuit_y + bottom_margin)
my_canvas.drawString(circuit_x + left_margin + name_x, circuit_y + bottom_margin + name_y, circuitsdata[cx][0])
flag_x = offset_x * circuitscale
flag_y = offset_y * circuitscale
renderPDF.draw(scaleSVG("SVG/finishflag.svg", circuitscale), my_canvas, circuit_x + left_margin + flag_x + flagcorrection * circuitscale, circuit_y + bottom_margin + flag_y)
my_canvas.save()
key = input("Wait")
