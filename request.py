import requests
import json

response = requests.get("https://www.geeksforgeeks.org/")
print(response.status_code)

# Source - https://stackoverflow.com/a/72914207
# Posted by Bruno Robert
# Retrieved 2026-08-09, License - CC BY-SA 4.0

response = requests.post(
            url="https://api.open-elevation.com/api/v1/lookup",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
            },
            data=json.dumps({
                "locations": [
                    {
                        "longitude": 10,
                        "latitude": 10
                    },
                    {
                        "longitude": 20,
                        "latitude": 20
                    }
                ]
            })
        )

print('Response HTTP Status Code: {status_code}'.format(status_code=response.status_code))
print('Response HTTP Response Body: {content}'.format(content=response.content))


key = input("Wait")
