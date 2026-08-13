import os
import sys
import csv
import json
import math
import svgwrite
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.graphics.shapes import *
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer

def Altitude_to_SVG(jsonfile):
    def coordinates_to_path(coordinates):
        l = 0
        path_data = ""
        i = 0
        for item in coordinates:
            lon = item["longitude"]
            lat = item["latitude"]
            elevation = item["elevation"]
            a = elevation
            if i == 0:
                path_data = f"M {l} {a}"
            else:
                d = sqrt(abs(lon - plon)**2 + abs(lat - plat)**2)
                l = l + d * 10000
                path_data += f" L {l} {a}"
            plon = lon
            plat = lat
            i += 1
        print(path_data)
        return path_data
    with open("Data/" + jsonfile + ".json", 'r') as file:
        data = json.load(file)
        path_data = coordinates_to_path(data["results"])
        dwg = svgwrite.Drawing('SVG/' + jsonfile + 'A.svg', size=('1000px', '500px'))
        path = dwg.path(d=path_data, fill='lightblue', stroke='blue', stroke_width=3)
        dwg.add(path)
        dwg.save()
    return
if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)
circuit = "az-2016"
Altitude_to_SVG(circuit)

key = input("Wait")
