import requests
import json

response = requests.get("https://www.geeksforgeeks.org/")
print(response.status_code)

key = input("Wait")
