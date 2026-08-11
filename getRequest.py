import requests

# https://api.open-elevation.com/api/v1/lookup?locations=41.161758,-8.583933
# The API endpoint
url = "https://jsonplaceholder.typicode.com/posts/1"

# A GET request to the API
response = requests.get(url)

# Print the response
print(response.json())

key = input("Wait")
