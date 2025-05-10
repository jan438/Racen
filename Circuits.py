import os
import sys
import csv
import geojson
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.graphics.shapes import *
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer

circuitscale = 0.2
flagcorrection = -5.0

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
def GeoJSON_to_SVG(circuitname):
    def coordinates_to_path(coordinates, scale, translate):
        path_data = ""
        for LineString in coordinates:
            for i, point in enumerate(LineString):
                x = (point[0] - translate[0]) * scale[0]
                y = (point[1] - translate[1]) * scale[1]
                command = "M" if i == 0 else "L"
                path_data += f"{command}{x},{height - y} "
            path_data += "Z "
        return path_data.strip()
    width = 500
    height = 500
    with open("Data/" + circuitname + ".geojson", 'r') as file:
        geojson_data = geojson.load(file)
    features = geojson_data['features']
    for feature in features:
        geometry = feature["geometry"]
        if geometry['type'] == 'Point':
            coordinates = geometry["coordinates"]
            startfinish_x = coordinates[0]
            startfinish_y = coordinates[1]
        elif geometry['type'] == 'LineString':
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
    scale_x = width / (max_x - min_x)
    scale_y = height / (max_y - min_y)
    scale = (scale_x, scale_y)
    translate = (min_x, min_y)
    offset_x = (startfinish_x - min_x) * scale_x
    offset_y = (startfinish_y - min_y) * scale_y
    svg_paths = []
    for feature in geojson_data['features']:
        geometry = feature['geometry']
        coords = geometry['coordinates']
        if geometry['type'] == 'LineString':
            svg_paths.append(coordinates_to_path([coords], scale, translate))
            with open("SVG/" + circuitname + ".svg", 'w') as f:
                f.write(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n')
                for path in svg_paths:
                    f.write(f'<path d="{path}" fill="none" stroke-width="3" stroke="black"/>\n')
                f.write('</svg>')
    print("Scale", scale_x, scale_y, "Startfinish", startfinish_x, startfinish_y, "Offsetflag", offset_x, offset_y)
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
file_to_open = "Data/Circuits2025.csv"
with open(file_to_open, 'r') as file:
    csvreader = csv.reader(file, delimiter = ';')
    count = 0
    for row in csvreader:
        circuitsdata.append(row)
        count += 1
my_canvas = canvas.Canvas('PDF/Circuits2025.pdf')
my_canvas.setFont("Helvetica", 10)
drawing = svg2rlg('SVG/F1.svg')
renderPDF.draw(drawing, my_canvas, 300, 750)
rowcount = 6
colcount = 4
rowheight = 120
colwidth = 130
row = 0
col = 0
for i in range(count):
    [offset_x, offset_y] = GeoJSON_to_SVG(circuitsdata[i][0])
    circuit_x = col * colwidth
    circuit_y = row * rowheight
    renderPDF.draw(scaleSVG("SVG/" + circuitsdata[i][0] + ".svg", circuitscale), my_canvas, circuit_x, circuit_y)
    my_canvas.drawString(circuit_x, circuit_y, circuitsdata[i][0])
    flag_x = offset_x * circuitscale
    flag_y = offset_y * circuitscale
    print(i, circuitsdata[i][0], circuitsdata[i][1], flag_x, flag_y)
    renderPDF.draw(scaleSVG("SVG/finishflag.svg", circuitscale), my_canvas, circuit_x + flag_x + flagcorrection * circuitscale, circuit_y + flag_y)
    col += 1
    if col == colcount:
       row += 1
       col = 0
my_canvas.save()
key = input("Wait")
