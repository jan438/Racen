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
    
def lookuphighs(selectedcoords):
    urlstr = "https://api.open-elevation.com/api/v1/lookup"
    headersarr = {
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8"}     
    line_items = []
    for q in selectedcoords:
        longtitude = q[0]
        latitude = q[1]
        myjson = {
                'longtitude': longtitude,
                'latitude': latitude
            }
        line_items.append(myjson)
    locsstr = json.dumps(line_items)
    print("locstr", locsstr)
    response = requests.post(
            url = urlstr,
            headers = headersarr,
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

selectedcoords = readgeojsonfile("be-1925", 0, 2)
print(len(selectedcoords))

resp = lookuphighs(selectedcoords)
print('Response HTTP Status Code: {status_code}'.format(status_code=resp.status_code))
print('Response HTTP Response Body: {content}'.format(content=resp.content))

key = input("Wait")
