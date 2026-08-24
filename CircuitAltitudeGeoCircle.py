import os
import sys
import csv
import json
import math
import svgwrite
from geopy.distance import geodesic
from geopy.distance import great_circle
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.graphics.shapes import *
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer

lengthscale = 80.0
altitudescale = 0.5

def Altitude_to_SVG(jsonfile, startindex, ac):
    def coordinates_to_path(dat1, dat2, startindex, ac):
        path_data = ""
        total = 0
        totalcoords = []
        res1 = dat1["results"]
        for item in res1:
            elevation = item["elevation"]
            location = item["location"]
            lon = location["lng"]
            lat = location["lat"]
            coord = [elevation, lon, lat]
            totalcoords.append(coord)
        if dat2 is not None:
            res2 = dat2["results"]
            for item in res2:
                elevation = item["elevation"]
                location = item["location"]
                lon = location["lng"]
                lat = location["lat"]
                coord = [elevation, lon, lat]
                totalcoords.append(coord)
        totalcoords = totalcoords[startindex:] + totalcoords[:startindex - 1]
        lencoords = len(totalcoords)
        mina = math.inf
        maxa = -math.inf
        fa = -1
        la = -1
        maxal = -1
        minal = -1
        for i in range(lencoords):
            elevation = totalcoords[i][0]
            if fa == -1:
                fa = elevation
            if elevation > maxa:
                maxa = elevation
            if elevation < mina:
                mina = elevation
            la = elevation
        l = 0
        sl = 0
        for i in range(lencoords):
            elevation = totalcoords[i][0]
            lon = totalcoords[i][1]
            lat = totalcoords[i][2]
            a = maxa - elevation
            a = altitudescale * a
            if i == 0:
                path_data = f"M {sl} {a}"
            else:
                coord1 = (plon, plat)
                coord2 = (lon, lat)
                d = great_circle(coord1, coord2).km
                l += d
                sl += d * lengthscale
                path_data += f" L {sl} {a}"
            if elevation == maxa:
                maxal = sl
            if elevation == mina:
                minal = sl
            plon = lon
            plat = lat
        fa = maxa - fa
        path_data += f" L {sl} 100"
        path_data += f" L 0.0 100"
        path_data += f" L 0.0 {fa}"
#        print(f'{jsonfile}, len coordinates, {len(totalcoords}, gcircle, {l:.3f}')
        print(f'{jsonfile}, len coordinates, {lencoords}')
        return [path_data, sl, maxa, mina, maxal, minal, l]
#    print("jsonfile", jsonfile, "startindex", startindex, "clockwise", ac)
    file1str = "Data/" + jsonfile + "-1.json"
    file2str = "Data/" + jsonfile + "-2.json"
    if os.path.exists(file1str):
        with open(file1str, 'r') as file1:
            data1 = json.load(file1)
            if os.path.exists(file2str):
                with open(file2str, 'r') as file2:
                    data2 = json.load(file2)
            else:
                data2 = None
            [path_data, sl, maxa, mina, maxal, minal, l] = coordinates_to_path(data1, data2, startindex, ac)
            dwg = svgwrite.Drawing('SVG/' + jsonfile + 'A.svg', size=(f'9500px', '200px'))
            grad = dwg.linearGradient(start=(0, 0), end=(0, 1), id='my-gradient')
            grad.add_stop_color(offset=0.0, color='#ffff7f', opacity=1)
            grad.add_stop_color(offset=0.2, color='#cccc66', opacity=1)
            grad.add_stop_color(offset=1.0, color='#000000', opacity=1)
            dwg.defs.add(grad)
            path = dwg.path(d=path_data, fill="url(#my-gradient)", stroke='black', stroke_width=3)
            dwg.add(path)
            high = dwg.circle(center=(maxal, 0), r=10, fill='red', stroke='black', stroke_width=3)
            dwg.add(high)
            low = dwg.circle(center=(minal, 60), r=10, fill='green', stroke='black', stroke_width=3)
            dwg.add(low)
            dwg.add(dwg.text(str(round(maxa, 1)), insert=(maxal, 60), stroke='none', fill='#ff0000', font_size='50px', font_weight="bold", font_family="Arial"))
            dwg.add(dwg.text(str(round(maxa - mina, 1)), insert=(minal, 120), stroke='none', fill='#00ff00', font_size='50px', font_weight="bold", font_family="Arial"))
            dwg.add(dwg.text(str(round(l * 100, 1)), insert=(minal, 160), stroke='none', fill='#00ff00', font_size='50px', font_weight="bold", font_family="Arial"))
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

for j in range(count):
    if circuitsdata[j][1] == "es-2026" or circuitsdata[j][1] == "mc-1929":
#    if True:
        Altitude_to_SVG(circuitsdata[j][1], int(circuitsdata[j][12]), circuitsdata[j][9])

key = input("Wait")
