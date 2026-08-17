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

lengthscale = 10000.0
altitudescale = 0.5

def Altitude_to_SVG(jsonfile):
    def coordinates_to_path(results):
        for item in results:
            print(item)
        path_data = ""
        return path_data
    with open("Data/" + jsonfile + "-2.json", 'r') as file:
        data = json.load(file)
        data1 = data[0]
        data2 = data[1]
        print("len data" , len(data))
        print("data1" , len(data1), data1)
        print("data2" , len(data2), data2)
        return
        path_data = coordinates_to_path(res)
        dwg = svgwrite.Drawing('SVG/' + jsonfile + 'A2.svg', size=('1000px', '300px'))
        grad = dwg.linearGradient(start=(0, 0), end=(0, 1), id='my-gradient')
        grad.add_stop_color(offset=0.0, color='#6d6d6d', opacity=1)
        grad.add_stop_color(offset=1.0, color='#000000', opacity=1)
        dwg.defs.add(grad)
        path = dwg.path(d=path_data, fill="url(#my-gradient)", stroke='black', stroke_width=3)
        dwg.add(path)
        dwg.save()
    return
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
print("circuitsdata", count)        

#for j in range(count):
#    Altitude_to_SVG(circuitsdata[j][1])
#    print(circuitsdata[j][0])
Altitude_to_SVG("be-1925")

key = input("Wait")
