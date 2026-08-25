import math
import json
import os
import sys
import csv
from geopy.distance import geodesic
from geopy.distance import great_circle

def readjson(jsonfile):
    totalcoords = []
    def coordinates_to_array(dat1, dat2):
        totalcoords = []
        res1 = dat1["results"]
        for item in res1:
            location = item["location"]
            lon = location["lng"]
            lat = location["lat"]
            coord = [lon, lat]
            totalcoords.append(coord)
        if dat2 is not None:
            res2 = dat2["results"]
            for item in res2:
                location = item["location"]
                lon = location["lng"]
                lat = location["lat"]
                coord = [lon, lat]
                totalcoords.append(coord)
        return totalcoords
#    print("jsonfile", jsonfile)
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

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on Earth.
    Inputs are in decimal degrees.
    Returns distance in kilometers.
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371.0088  # Earth's radius in kilometers
    return r * c

def path_length(coords):
    """
    Calculate total path length from a list of (lat, lon) tuples.
    """
    haver = 0.0
    mathl = 0.0
    gdesic = 0.0
    gcircle = 0.0
    for i in range(len(coords) - 1):
        lat1, lon1 = coords[i]
        lat2, lon2 = coords[i + 1]
        haver += haversine(lat1, lon1, lat2, lon2)
        mathl += math.sqrt(abs(lon2 - lon1)**2 + abs(lat2 - lat1)**2)
        coord1 = (lon1, lat1)
        coord2 = (lon2, lat2)
        gdesic += geodesic(coord1, coord2).km
        d = great_circle(coord1, coord2).km
        gcircle += d
        print(i, lat1, lon1, lat2, lon2, d, gcircle)
    lat1, lon1 = coords[len(coords) - 1]    
    lat2, lon2 = coords[0]
    d = great_circle(coord1, coord2).km
    gcircle += d
    print(len(coords) - 1, lat1, lon1, lat2, lon2, d, gcircle)
    return [haver, mathl, gdesic, gcircle]

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
#        if True:
        if circuitsdata[i][1] == "mc-1929":
            coordinates = readjson(circuitsdata[i][1])
#            coordinates = coordinates[:10]
            try:
                [haver, l, gdesic, gcircle] = path_length(coordinates)
#               print(f'{circuitsdata[i][0]}, haver, {haver:.3f}, math, {l:.3f}, gdesic, {gdesic:.3f}, gcircle, {gcircle:.3f}')
                print(f'{circuitsdata[i][0]}, {circuitsdata[i][1]}, len coordinates, {len(coordinates)}, gcircle, {gcircle:.3f}')
            except Exception as e:
                print(f"Error calculating path length: {e}")

key = input("Wait")
