import requests
import json

def get_elevations(locations):
    """
    Fetch elevation data for a list of (latitude, longitude) tuples
    using the Open-Elevation API.
    """
    if not locations or not all(isinstance(loc, tuple) and len(loc) == 2 for loc in locations):
        raise ValueError("Locations must be a list of (latitude, longitude) tuples.")

    url = "https://api.open-elevation.com/api/v1/lookup"
    payload = {
        "locations": [{"latitude": lat, "longitude": lon} for lat, lon in locations]
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()

        # Extract elevations
        results = [
            (loc["latitude"], loc["longitude"], loc["elevation"])
            for loc in data.get("results", [])
        ]
        return results

    except requests.exceptions.RequestException as e:
        print(f"Error fetching elevation data: {e}")
        return []

# Example usage
if __name__ == "__main__":
    coords = [
        (52.379189, 4.899431),  # Amsterdam
        (48.8566, 2.3522),      # Paris
        (40.7128, -74.0060)     # New York
    ]
    elevations = get_elevations(coords)
    for lat, lon, elev in elevations:
        print(f"Lat: {lat}, Lon: {lon} → Elevation: {elev} m")
        
key = input("Wait")
