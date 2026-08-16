import requests
import json
import sys
import os


if sys.platform[0] == 'l':
    path = '/home/jan/git/Racen'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
os.chdir(path)

try:
    with open("PDF/data.json", "r") as json_file:
        existing_data = json.load(json_file)
except (FileNotFoundError, json.decoder.JSONDecodeError):
    existing_data = []

latitude = "41.161758"
longitude = "-8.583933"
url = "https://api.open-elevation.com/api/v1/lookup?locations=" + latitude + "," + longitude
response = requests.get(url)

if response.status_code == 200:
    new_data = response.json()
    existing_data.update(new_data)
    with open("PDF/data.json", "w") as json_file:
        json.dump(existing_data, json_file, indent=4)
        print("Data appended to data.json file.")
else:
    print("Failed to retrieve data from the API. Status code:", response.status_code)
    
key = input("Wait")
