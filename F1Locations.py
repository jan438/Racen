import json
import os
import sys
import csv
import svgwrite
import math
from geopy.distance import great_circle

circuitsdata = []
maxdifa = -1

def readjson(jsonfile):
    totalcoords = []
    def coordinates_to_array(dat):
        minlon = math.inf
        maxlon = -math.inf
        minlat = math.inf
        maxlat = -math.inf
        totalcoords = []
        for item in dat:
            lon = item["lon"]
            lat = item["lat"]
            if lon > maxlon:
                maxlon = lon
            if lon < minlon:
                minlon = lon
            if lat > maxlat:
                maxlat = lat
            if lat < minlat:
                minlat = lat         
            loc = item["location"]
            coord = [lon, lat]
            totalcoords.append(coord)
            print(loc, lon, lat)
        return [totalcoords, minlon, maxlon, minlat, maxlat]
    if os.path.exists(jsonfile):
        with open(jsonfile, 'r') as file:
            data = json.load(file)
            [totalcoords, minlon, maxlon, minlat, maxlat] = coordinates_to_array(data)
            print("minlon", minlon, "maxlon", maxlon, "minlat", minlat, "maxlat", maxlat)
    return totalcoords

if __name__ == "__main__":
    if sys.platform[0] == 'l':
        path = '/home/jan/git/Racen'
    if sys.platform[0] == 'w':
        path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
    os.chdir(path)
    jsonfile = "Data/f1-locations.json"
    coordinates = readjson(jsonfile)

key = input("Wait")
