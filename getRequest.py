import requests

url = "https://api.open-elevation.com/api/v1/lookup?locations=41.161758,-8.583933"

try:
    response = requests.get(url)
    print(response.json())

except:
	print("Exception")

key = input("Wait")