import requests
import json

response = requests.post(
            url="https://api.open-elevation.com/api/v1/lookup",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
            },
            data=json.dumps({
                "locations": [
                    {
                        "longitude": 5.96502000000,
                        "latitude": 50.44425100000
                    },
                    {
                        "longitude": 5.96341900000,
                        "latitude": 50.44603300000
                    }
                ]
            })
        )

print('Response HTTP Status Code: {status_code}'.format(status_code=response.status_code))
print('Response HTTP Response Body: {content}'.format(content=response.content))


key = input("Wait")
