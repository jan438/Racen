import os
import sys
import geojson
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
with open('Data/sample.geojson', 'r') as file:
    geojson_data = geojson.load(file)
features = geojson_data['features']
print("properties", features[0]["properties"])
print("bbox", features[0]["bbox"])
geometry = features[0]["geometry"]
print("geometry", geometry)
coordinates = geometry["coordinates"]
print("coordinates", coordinates)
if geometry['type'] == 'LineString':
    coords = [coordinates]
    for polygon in coords:
        for ring in polygon:
            for point in ring:
                print(point)
                #min_x = min(min_x, x)
                #max_x = max(max_x, x)
                #min_y = min(min_y, y)
                #max_y = max(max_y, y)
    #print("min_x", str(min_x))
my_canvas = canvas.Canvas('PDF/Circuits.pdf')
drawing = svg2rlg('SVG/F1.svg')
renderPDF.draw(drawing, my_canvas, 0, 40)
my_canvas.drawString(50, 30, 'My SVG Image')
my_canvas.save()
key = input("Wait")
