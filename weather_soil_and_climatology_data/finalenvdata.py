import requests
import numpy as np
import pandas as pd

# Function to get coordinates of a location using Google Maps Geocoding API
def get_coordinates(address, google_maps_token):
    geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': address,
        'key': google_maps_token
    }
    response = requests.get(geocoding_url, params=params)
    data = response.json()
    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        latitude = location['lat']
        longitude = location['lng']
        return latitude, longitude
    else:
        raise Exception(f"Geocoding error: {data['status']} - {data.get('error_message', '')}")

# Function to get current weather data using OpenWeatherMap API
def get_weather(latitude, longitude, openweather_api_key):
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': latitude,
        'lon': longitude,
        'appid': openweather_api_key,
        'units': 'metric'
    }
    response = requests.get(weather_url, params=params)
    data = response.json()
    if response.status_code == 200:
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        weather_info = (f"Weather at coordinates ({latitude}, {longitude}):\n"
                        f"Description: {weather_description.capitalize()}\n"
                        f"Temperature: {temperature}°C\n"
                        f"Feels like: {feels_like}°C\n"
                        f"Humidity: {humidity}%\n"
                        f"Wind speed: {wind_speed} m/s")
        return weather_info
    else:
        raise Exception(f"Weather API error: {data['message']}")

# Function to get the 5-day rainfall forecast using OpenWeatherMap API
def get_rainfall_forecast(latitude, longitude, openweather_api_key):
    forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        'lat': latitude,
        'lon': longitude,
        'appid': openweather_api_key,
        'units': 'metric'
    }
    response = requests.get(forecast_url, params=params)
    data = response.json()
    if response.status_code == 200:
        forecast_data = data['list']
        rainfall_forecast = []
        for entry in forecast_data:
            rain_data = entry.get('rain', {}).get('3h', 0)
            time_of_forecast = entry['dt_txt']
            if rain_data > 0:
                rainfall_forecast.append(f"At {time_of_forecast}: Rainfall expected - {rain_data} mm")
        if rainfall_forecast:
            return "\n".join(rainfall_forecast)
        else:
            return "No significant rainfall predicted in the next 5 days."
    else:
        raise Exception(f"Forecast API error: {data['message']}")

# Function to get soil moisture data using Open-Meteo API
def get_soil_moisture(latitude, longitude):
    soil_moisture_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'hourly': 'soil_moisture_0_1cm',
        'timezone': 'auto'
    }
    response = requests.get(soil_moisture_url, params=params)
    data = response.json()
    if 'hourly' in data and 'soil_moisture_0_1cm' in data['hourly']:
        soil_moisture = data['hourly']['soil_moisture_0_1cm'][0]
        return f"Soil Moisture at coordinates ({latitude}, {longitude}): {soil_moisture} m³/m³"
    else:
        return "No soil moisture data available for the specified location."

# Function to calculate tilt/slope between two points using elevation difference and distance
def calculate_tilt(elevation_diff, distance):
    return np.degrees(np.arctan(elevation_diff / distance))

# Haversine function to calculate distance between two geographic coordinates
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    a = np.sin(delta_phi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) ** 2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

# Function to get elevation data for a given latitude and longitude
def get_elevation(lat, lon):
    location = [{"latitude": lat, "longitude": lon}]
    response = requests.post('https://api.open-elevation.com/api/v1/lookup', json={"locations": location})
    if response.status_code == 200:
        elevation_data = response.json()
        return elevation_data['results'][0]['elevation']
    else:
        print("Failed to retrieve elevation data:", response.status_code)
        return None

if __name__ == "__main__":
    try:
        # Replace with your actual API keys
        google_maps_token = "AIzaSyBlJfGgpP2kN06cTUkpcY1VZLsflD2_ux0"
        openweather_api_key = "dff8a714e30a29e438b4bd2ebb11190f"
        
        # User input for address
        address = input("Enter the address or location name: ")
        
        # Step 1: Get coordinates for the location
        latitude, longitude = get_coordinates(address, google_maps_token)
        print(f"Coordinates for '{address}': Latitude {latitude}, Longitude {longitude}")
        
        # Step 2: Get the current weather data using the coordinates
        weather_info = get_weather(latitude, longitude, openweather_api_key)
        print(weather_info)
        
        # Step 3: Get the 5-day rainfall forecast using the coordinates
        rainfall_forecast = get_rainfall_forecast(latitude, longitude, openweather_api_key)
        print("Rainfall Forecast:\n", rainfall_forecast)
        
        # Step 4: Get the soil moisture data using the coordinates
        soil_moisture_info = get_soil_moisture(latitude, longitude)
        print(soil_moisture_info)
        
        # Terrain and elevation analysis
        lat, lon = latitude, longitude
        if lat is not None and lon is not None:
            # Get the elevation for the specific latitude and longitude
            elevation = get_elevation(lat, lon)
            if elevation is not None:
                print(f"Elevation at main point (lat: {lat}, lon: {lon}): {elevation} meters")
                # Use a larger distance, 500 meters, for comparison
                nearby_distance = 500  # in meters
                lat_offset = lat + (nearby_distance / 6371000) * (180 / np.pi)
                # Get elevation for the nearby point
                nearby_elevation = get_elevation(lat_offset, lon)
                if nearby_elevation is not None:
                    print(f"Elevation at nearby point (lat: {lat_offset}, lon: {lon}): {nearby_elevation} meters")
                    # Calculate tilt and slope using the two elevations
                    elevation_diff = nearby_elevation - elevation
                    print(f"Elevation difference: {elevation_diff} meters")
                    tilt = calculate_tilt(elevation_diff, nearby_distance)
                    slope = tilt
                    print(f"Tilt: {tilt} degrees")
                    # Relief: Assume reference elevation (sea level) as 0m for simplicity
                    relief = abs(elevation - 0)
                    print(f"Relief: {relief} meters")
                    # Plan and Profile Curvature: Approximated using the difference over 500 meters
                    plan_curvature = elevation_diff / nearby_distance
                    profile_curvature = elevation_diff / nearby_distance
                    print(f"Plan Curvature: {plan_curvature}")
                    print(f"Profile Curvature: {profile_curvature}")
                    # Create a DataFrame with the single point's data and calculated parameters
                    df = pd.DataFrame([[lat, lon, elevation, tilt, slope, relief, plan_curvature, profile_curvature]],
                                      columns=['Latitude', 'Longitude', 'Elevation', 'Tilt', 'Slope', 'Relief', 'Plan Curvature', 'Profile Curvature'])
                    print(df)
                else:
                    print("Failed to retrieve nearby elevation data.")
            else:
                print("Failed to retrieve elevation data.")
        else:
            print("Failed to retrieve coordinates.")
    
    except Exception as e:
        print("Error:", str(e))
