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
    print("jsonfile", jsonfile)
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
        gcircle += great_circle(coord1, coord2).km
    return [haver, mathl, gdesic, gcircle]

if __name__ == "__main__":
    circuitsdata = []
    file_to_open = "Data/Circuits2027.csv"
    with open(file_to_open, 'r') as file:
        csvreader = csv.reader(file, delimiter = ';')
        count = 0
        for row in csvreader:
            circuitsdata.append(row)
            count += 1
    print("circuitsdata count", count)    
    lvcoordinates = readjson("us-2023")
    print(len(lvcoordinates))
    mccoordinates = readjson("mc-1929")
    print(len(mccoordinates))
    try:
        [haverlv, lvl, lvgdesic, lvgcircle] = path_length(lvcoordinates)
        print("Las Vegas", "haver", haverlv, "math", lvl, "lvgdesic", lvgdesic, "lvgcircle", lvgcircle)
        [havermc, mcl, mcgdesic, mcgcircle] = path_length(mccoordinates)
        print("Monaco", "haver", havermc, "math", mcl, "mcgdesic", mcgdesic, "mcgcircle", mcgcircle)
    except Exception as e:
        print(f"Error calculating path length: {e}")
        
key = input("Wait")
