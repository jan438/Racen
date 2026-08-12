import os
import sys
import csv
import json
import math
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.graphics.shapes import *
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer

def Altitude_to_SVG(jsonfile, svgfile):
    def coordinates_to_path(coordinates):
        path_data = ""
        for item in coordinates:
            print(item["longitude"])
        return path_data
    with open("Data/" + jsonfile + ".json", 'r') as file:
        data = json.load(file)
        coords = data["results"]
        coordinates_to_path(coords)
#    with open("SVG/" + svgfile + "A.svg", 'w') as f:
#        f.write(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n')
#        for feature in geojson_data['features']:
#            geometry = feature['geometry']
#            coords = geometry['coordinates']
#            if geometry['type'] == 'LineString':
#                print("To write elevation")
#        f.write('<path d="M 100 50 L 300 50 L 200 100 Z" fill="red" stroke="blue" stroke-width="3" />')
#        f.write('</svg>')    
    return
if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
circuit = "be-1925"
Altitude_to_SVG(circuit, circuit)

key = input("Wait")
