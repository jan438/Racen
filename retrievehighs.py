import requests
import json
import sys
import os
import geojson

selectioncoords = []

def readgeojsonfile(geojsonfile):
    with open("Data/" + geojsonfile + ".geojson", 'r') as file:
        geojson_data = geojson.load(file)
    features = geojson_data['features']
    print("Count features", len(features))
    for feature in features:
        geometry = feature["geometry"]
        properties = feature['properties']
        if geometry['type'] == 'LineString':
            coordinates = geometry["coordinates"]
            coords = [coordinates]
            for linestring in coords:
               print(geojsonfile, "len", len(linestring))
               for point in linestring:
                    x, y = point
                    selectioncoords.append([x, y])
    return selectioncoords

#response = requests.post(
#            url="https://api.open-elevation.com/api/v1/lookup",
#            headers={
#                "Accept": "application/json",
#                "Content-Type": "application/json; charset=utf-8",
#            },
#            data=json.dumps({
#                "locations": [
#                    {
#                        "longitude": 5.96502000000,
#                        "latitude": 50.44425100000
#                    },
#                    {
#                        "longitude": 5.96341900000,
#                        "latitude": 50.44603300000
#                    }
#                ]
#            })
#        )

#print('Response HTTP Status Code: {status_code}'.format(status_code=response.status_code))
#print('Response HTTP Response Body: {content}'.format(content=response.content))

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)

selectedcoords = readgeojsonfile("be-1925")
print(len(selectedcoords))

key = input("Wait")
