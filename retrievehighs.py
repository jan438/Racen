import requests
import json
import sys
import os
import geojson

selectioncoords = []
resp = requests.Response

def readgeojsonfile(geojsonfile, min, max):
    index = 0
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
                    if index >= min and index < max:
                        selectioncoords.append([x, y])
                    index += 1
    return selectioncoords
    
def lookuphighs():
    response = requests.post(
            url="https://api.open-elevation.com/api/v1/lookup",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
            },
            data=json.dumps({
                "locations": [
                    {
                        "longitude": 5.96502000000,
                        "latitude": 50.44425100000
                    },
                    {
                        "longitude": 5.96341900000,
                        "latitude": 50.44603300000
                    }
                ]
            })
        )
    return response

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)

selectedcoords = readgeojsonfile("be-1925", 0, 10)
print(len(selectedcoords))

resp = lookuphighs()
print('Response HTTP Status Code: {status_code}'.format(status_code=resp.status_code))
print('Response HTTP Response Body: {content}'.format(content=resp.content))

print(resp)

key = input("Wait")
