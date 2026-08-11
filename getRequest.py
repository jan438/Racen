import requests
import json

url = "https://api.open-elevation.com/api/v1/lookup?locations=41.161758,-8.583933"
response = requests.get(url)

if response.status_code == 200:
    new_data = response.json()
    with open("PDF/data.json", "w") as json_file:
        json.dump(new_data, json_file, indent=4)
        print("Data appended to data.json file.")
else:
    print("Failed to retrieve data from the API. Status code:", response.status_code)
    
key = input("Wait")
