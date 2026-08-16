import requests
import json
import sys
import os
import geojson
import time

resp = requests.Response

def merge_json_files(file_paths, output_file):
    merged_data = []
    for path in file_paths:
        with open(path, 'r') as file:
             print("merge:", path)
#            data = json.load(file)
#            merged_data.append(data)
#    with open(output_file, 'w') as outfile:
#        json.dump(merged_data, outfile)

def readgeojsonfile(geojsonfile, min, max):
    index = 0
    selectioncoords = []
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
    url = "https://api.opentopodata.org/v1/srtm90m"
    locsstr = ""
    for q in selectedcoords:
        longtitude = str(float(q[0]))
        latitude = str(float(q[1]))
        locsstr += latitude + "," + longtitude + "|"
    data = {
     "locations": locsstr,
     "interpolation": "cubic",
    }
    response = requests.post(url, json=data)
    print(data)
    return response

if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)

circuitname = "ae-2009"
selectedcoords = readgeojsonfile(circuitname, 0, 100)
print("len selected coords", len(selectedcoords))
resp = lookuphighs(selectedcoords)
print('Response HTTP Status Code: {status_code}'.format(status_code=resp.status_code))
if resp.status_code == 200:
    highslows = resp.content
    data = json.loads(highslows.decode('utf-8'))
    with open('Data/' + circuitname + '-2-1.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        time.sleep(20.0)
        selectedcoords = readgeojsonfile(circuitname, 100, 200)
        print("len selected coords", len(selectedcoords))
        resp = lookuphighs(selectedcoords)
        print('Response HTTP Status Code: {status_code}'.format(status_code=resp.status_code))
        if resp.status_code == 200:
            highslows = resp.content
            data = json.loads(highslows.decode('utf-8'))
            with open('Data/' + circuitname + '-2-2.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                file1 = "Data/" + circuitname + "-2-1.json"
                file2 = "Data/" + circuitname + "-2-2.json"
                print(file1, file2)
                file_paths = [file1, file2]
                output_file = "Data/" + circuitname + '-2.json'
                merge_json_files(file_paths, output_file)
                print(f"Merged data written to '{output_file}'")
        else:
            print("Invalid request")
else:
    print("Invalid request")
key = input("Wait")
