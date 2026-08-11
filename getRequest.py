import requests

# The API endpoint
url = "https://jsonplaceholder.typicode.com/posts/1"

# A GET request to the API
response = requests.get(url)

# Print the response
print(response.json())

key = input("Wait")
