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
    def coordinates_to_path(dat1, dat2):
        total = 0
        totalcoords = []
        res1 = dat1["results"]
        res2 = dat2["results"]
        for item in res1:
            elevation = item["elevation"]
            location = item["location"]
            lon = location["lng"]
            lat = location["lat"]
            coord = [elevation, lon, lat]
            totalcoords.append(coord)
        for item in res2:
            elevation = item["elevation"]
            location = item["location"]
            lon = location["lng"]
            lat = location["lat"]
            coord = [elevation, lon, lat]
            totalcoords.append(coord)
        print("total", len(totalcoords))
        mina = math.inf
        maxa = -math.inf
        fa = -1
        la = -1
        for i in range(len(totalcoords)):
            elevation = totalcoords[i][0]
            if fa == -1:
                fa = elevation
            if elevation > maxa:
                maxa = elevation
            if elevation < mina:
                mina = elevation
            la = elevation
        diff = maxa - mina
        l = 0
        path_data = ""
        for i in range(len(totalcoords)):
            elevation = totalcoords[i][0]
            lon = totalcoords[i][1]
            lat = totalcoords[i][2]
            a = maxa - elevation
            a = altitudescale * a
            if i == 0:
                path_data = f"M {l} {a}"
            else:
                d = sqrt(abs(lon - plon)**2 + abs(lat - plat)**2)
                l = l + d * lengthscale
                path_data += f" L {l} {a}"
            plon = lon
            plat = lat
        mina = 100
        fa = maxa - fa
        path_data += f" L {l} {mina}"
        path_data += f" L 0.0 {mina}"
        path_data += f" L 0.0 {fa}"
        return path_data
    with open("Data/" + jsonfile + "-2.json", 'r') as file:
        data = json.load(file)
        data1 = data[0]
        data2 = data[1]
        path_data = coordinates_to_path(data1, data2)
        dwg = svgwrite.Drawing('SVG/' + jsonfile + 'A.svg', size=('1000px', '300px'))
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
Altitude_to_SVG("au-1953")

key = input("Wait")
