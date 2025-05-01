import os
import sys
import csv
import geojson
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg

def coordinates_to_path(coordinates, scale, translate):
    path_data = ""
    for polygon in coordinates:
        for i, point in enumerate(polygon):
            x = (point[0] - translate[0]) * scale[0]
            y = (point[1] - translate[1]) * scale[1]
            command = "M" if i == 0 else "L"
            path_data += f"{command}{x},{height - y} "
        path_data += "Z "
    return path_data.strip()

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
print("Count:", count)
with open('Data/Zandvoort.geojson', 'r') as file:
    geojson_data = geojson.load(file)
features = geojson_data['features']
geometry = features[0]["geometry"]
coordinates = geometry["coordinates"]
min_x = min_y = float('inf')
max_x = max_y = float('-inf')
if geometry['type'] == 'LineString':
    coords = [coordinates]
    for linestring in coords:
        for point in linestring:
            x, y = point
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
width = 500
height = 500
scale_x = width / (max_x - min_x)
scale_y = height / (max_y - min_y)
scale = (scale_x, scale_y)
translate = (min_x, min_y)
svg_paths = []
for feature in geojson_data['features']:
    geometry = feature['geometry']
    coords = geometry['coordinates']
    if geometry['type'] == 'LineString':
        svg_paths.append(coordinates_to_path([coords], scale, translate))    
    with open("PDF/Zandvoort.svg", 'w') as f:
        f.write(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n')
        for path in svg_paths:
            f.write(f'  <path d="{path}" fill="none" stroke="black"/>\n')
        f.write('</svg>')
my_canvas = canvas.Canvas('PDF/Circuits.pdf')
drawing = svg2rlg('SVG/F1.svg')
renderPDF.draw(drawing, my_canvas, 0, 40)
drawing = svg2rlg('SVG/Zandvoort.svg')
my_canvas.drawString(50, 30, 'My SVG Image')
my_canvas.save()
key = input("Wait")
