import json
import os
import sys
import csv
import svgwrite
import math
from geopy.distance import great_circle

circuitsdata = []
# be-1925 pdf 171.0  137.0   geo 5.971 50.436
# sg-2008 pdf 278.0  76.5    geo 103.859 1.291     
# gb-1948 pdf 164.0  138.0   geo -1.017 52.072 
# us-2023 pdf 48.0   120.0   geo -115.168 36.116
# au-1953 pdf 315.0  17.5    geo 144.97 -37.846
#
# dx ratio las vegas melbourne pdf  48.0 315.0 geo -115.168 144.97
# dy ratio london    melbourne pdf 138.0  17.5 geo   52.072 -37.846

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
            id = item["id"]
            coord = [lon, lat]
            totalcoords.append(coord)
            print(loc, lon, lat, id)
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
