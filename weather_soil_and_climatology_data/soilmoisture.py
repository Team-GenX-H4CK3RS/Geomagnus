import requests

def get_soil_moisture(lat, lon, api_key):
    url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={api_key}'
    response = requests.get(url)
    data = response.json()
    
    # Check if soil moisture data is available
    if 'soil_moisture' in data['current']:
        moisture = data['current']['soil_moisture']
        return f"Soil moisture: {moisture} m³/m³"
    else:
        return "No soil moisture data available."

# Example usage
latitude = 37.7749
longitude = -122.4194
api_key = "dff8a714e30a29e438b4bd2ebb11190f"  # Replace with your actual API key
print(get_soil_moisture(latitude, longitude, api_key))