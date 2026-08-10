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
    lon0 = float(selectedcoords[0][0])
    lat0 = float(selectedcoords[0][1])
    lon1 = float(selectedcoords[1][0])
    lat1 = float(selectedcoords[1][1])
    lon2 = float(selectedcoords[2][0])
    lat2 = float(selectedcoords[2][1])
    lon3 = float(selectedcoords[3][0])
    lat3 = float(selectedcoords[3][1])
    lon4 = float(selectedcoords[4][0])
    lat4 = float(selectedcoords[4][1])
    lon5 = float(selectedcoords[5][0])
    lat5 = float(selectedcoords[5][1])
    lon6 = float(selectedcoords[6][0])
    lat6 = float(selectedcoords[6][1])
    lon7 = float(selectedcoords[7][0])
    lat7 = float(selectedcoords[7][1])
    lon8 = float(selectedcoords[8][0])
    lat8 = float(selectedcoords[8][1])
    lon9 = float(selectedcoords[9][0])
    lat9 = float(selectedcoords[9][1])
    response = requests.post(
            url = urlstr,
            headers = headersarr,
            data=json.dumps({
                "locations": [
                    {
                        "longitude": lon0,
                        "latitude": lat0
                    },
                    {
                        "longitude": lon1,
                        "latitude": lat1
                    },
                    {
                        "longitude": lon2,
                        "latitude": lat2
                    },
                    {
                        "longitude": lon3,
                        "latitude": lat3
                    },
                    {
                        "longitude": lon4,
                        "latitude": lat4
                    },
                    {
                        "longitude": lon5,
                        "latitude": lat5
                    },
                    {
                        "longitude": lon6,
                        "latitude": lat6
                    },
                    {
                        "longitude": lon7,
                        "latitude": lat7
                    },
                    {
                        "longitude": lon8,
                        "latitude": lat8
                    },
                    {
                        "longitude": lon9,
                        "latitude": lat9
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

resp = lookuphighs(selectedcoords)
print('Response HTTP Status Code: {status_code}'.format(status_code=resp.status_code))
highs = resp.content
with open("Data/be-1925-000-009", 'w') as f:
    f.write(str(resp.content))

key = input("Wait")
