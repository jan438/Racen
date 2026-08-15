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
    url = 'https://api.opentopodata.org/v1/eudem25m?'
    #https://api.opentopodata.org/v1/srtm90m?locations=-43.5,172.5%7C27.6,1.98&interpolation=cubic
    #url = "https://api.open-elevation.com/api/v1/lookup"
    fileToSend = {"locations": []}
    for q in selectedcoords:
        longtitude = float(q[0])
        latitude = float(q[1])
        fileToSend["locations"].append({"latitude": latitude, "longitude": longtitude})
    response = requests.post(url, json=fileToSend)
    return response

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)

circuitname = "ae-2009"
selectedcoords = readgeojsonfile(circuitname, 0, 514)
print(len(selectedcoords))

resp = lookuphighs(selectedcoords)
print('Response HTTP Status Code: {status_code}'.format(status_code=resp.status_code))
highslows = resp.content
data = json.loads(highslows.decode('utf-8'))
with open('Data/' + circuitname + '.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

key = input("Wait")
