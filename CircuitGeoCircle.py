import json
import os
import sys
import csv
import svgwrite
import math
from geopy.distance import great_circle

def readjson(jsonfile):
    totalcoords = []
    def coordinates_to_array(dat1, dat2):
        totalcoords = []
        res1 = dat1["results"]
        for item in res1:
            alt = item["elevation"]
            location = item["location"]
            lon = location["lng"]
            lat = location["lat"]
            coord = [lon, lat, alt]
            totalcoords.append(coord)
        if dat2 is not None:
            res2 = dat2["results"]
            for item in res2:
                alt = item["elevation"]
                location = item["location"]
                lon = location["lng"]
                lat = location["lat"]
                coord = [lon, lat, alt]
                totalcoords.append(coord)
        return totalcoords
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
            totalcoords = coordinates_to_array(data1, data2)
    return totalcoords

def path_length(jsonfile, coords):
    mina = math.inf
    maxa = -math.inf
    for i in range(len(coords)):
        lat, lon, alt = coords[i]
        if alt > maxa:
            maxa = alt
        if alt < mina:
            mina = alt
    print("max altitude", maxa, "min altitude", mina)
    lscale = 100
    ascale = 0.5
    dwg = svgwrite.Drawing('SVG/' + jsonfile + 'A.svg', size=(f'950px', '20px'))
    gcircle = 0.0
    sl = 0.0
    for i in range(len(coords) - 1):
        lat1, lon1, alt1 = coords[i]
        lat2, lon2, alt2 = coords[i + 1]
        coord1 = (lon1, lat1)
        coord2 = (lon2, lat2)
        d = great_circle(coord1, coord2).km
        gcircle += d
        sd = d * lscale
        sl += sd
        a1 = (maxa - alt1) * ascale
        a2 = (maxa - alt2) * ascale
        if i == 0:
            path_data = f"M 0 {a1}"
            path_data += f" L {sl} {a2}"
        else:
            path_data += f" L {sl} {a2}"
    lat1, lon1, alt1 = coords[len(coords) - 1]    
    lat2, lon2, alt2 = coords[0]
    coord1 = (lon1, lat1)
    coord2 = (lon2, lat2)
    d = great_circle(coord1, coord2).km
    gcircle += d
    sd = d * lscale
    sl += sd
    a2 = (maxa - alt2) * ascale
    path_data += f" L {sl} {a2}"
    path = dwg.path(d=path_data, fill="none", stroke='green', stroke_width=10)
    dwg.add(path)
    dwg.save()
    print("gcircle:", gcircle)
    return [gcircle]

if __name__ == "__main__":
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
    print("circuitsdata count", count)    
    for i in range(count):
#        if circuitsdata[i][1] == "us-2023":
        if True:
            jsonfile = circuitsdata[i][1]
            coordinates = readjson(jsonfile)
            try:
                [gcircle] = path_length(jsonfile, coordinates)
                print(f'{circuitsdata[i][0]}, {circuitsdata[i][1]}, len coordinates, {len(coordinates)}, gcircle, {gcircle:.3f}')
            except Exception as e:
                print(f"Error calculating path length: {e}")

key = input("Wait")
