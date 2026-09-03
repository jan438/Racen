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
        totalcoords = []
        for item in dat:
            lat = item["lat"]
            print(lat)
        return totalcoords
    if os.path.exists(jsonfile):
        with open(jsonfile, 'r') as file:
            data = json.load(file)
            totalcoords = coordinates_to_array(data)
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
