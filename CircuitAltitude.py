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
        x = 0
        y = 0
        path_data = ""
        i = 0
        for item in coordinates:
            longitude = item["longitude"]
            latitude = item["latitude"]
            elevation = item["elevation"]
            a = elevation
            if i == 0:
                path_data = f"M {l} {a}"
            else:
                d = sqrt(abs(longitude - x)**2 + abs(latitude - y)**2)
                l = l + d
                path_data += f" L {l} {a}"
                x = longitude
                y = latitude
            print(i, "length", l, "altitude", a)
            i += 1
            if i == 3:
                 break
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
circuit = "be-1925"
Altitude_to_SVG(circuit)

key = input("Wait")
