import numpy as np
import pandas as pd
import requests
from datetime import datetime

def calculate_tilt(elevation_diff, distance):
    return np.degrees(np.arctan(elevation_diff / distance)) 

def get_elevation(lat, lon):
    location = [{"latitude": lat, "longitude": lon}]
    response = requests.post('https://api.open-elevation.com/api/v1/lookup', json={"locations": location})
    
    if response.status_code == 200:
        elevation_data = response.json()
        return elevation_data['results'][0]['elevation']
    else:
        print(f"Failed to retrieve elevation data for ({lat}, {lon}): {response.status_code}")
        return None

def get_coordinates(location_name, google_maps_token):
    geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    params = {
        'address': location_name,
        'key': google_maps_token
    }
    
    response = requests.get(geocoding_url, params=params)
    data = response.json()
    
    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        print(f"Geocoding error for {location_name}: {data['status']} - {data.get('error_message', '')}")
        return None, None

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
        return {
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'pressure': data['main']['pressure']
        }
    else:
        print(f"Weather API error: {data['message']}")
        return None

def get_soil_moisture(latitude, longitude):
    soil_moisture_url = "https://api.open-meteo.com/v1/forecast"
    
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'hourly': 'soil_moisture_0_1cm',
        'start': datetime.now().strftime('%Y-%m-%dT00:00'),
        'end': datetime.now().strftime('%Y-%m-%dT23:00'),
        'timezone': 'auto'
    }
    
    response = requests.get(soil_moisture_url, params=params)
    data = response.json()

    if 'hourly' in data and 'soil_moisture_0_1cm' in data['hourly']:
        return data['hourly']['soil_moisture_0_1cm'][0]
    else:
        print(f"No soil moisture data available for ({latitude}, {longitude})")
        return None

def process_location(location_name, google_maps_token, openweather_api_key):
    lat, lon = get_coordinates(location_name, google_maps_token)
    if lat is None or lon is None:
        return None

    elevation = get_elevation(lat, lon)
    if elevation is None:
        return None

    nearby_distance = 500  # in meters
    lat_offset = lat + (nearby_distance / 6371000) * (180 / np.pi)
    nearby_elevation = get_elevation(lat_offset, lon)
    if nearby_elevation is None:
        return None

    elevation_diff = nearby_elevation - elevation
    tilt = calculate_tilt(elevation_diff, nearby_distance)
    relief = abs(elevation - 0)
    plan_curvature = elevation_diff / nearby_distance
    profile_curvature = elevation_diff / nearby_distance

    weather_data = get_weather(lat, lon, openweather_api_key)
    if weather_data is None:
        return None

    soil_moisture = get_soil_moisture(lat, lon)

    return {
        'Latitude': lat,
        'Longitude': lon,
        'Elevation': elevation,
        'Tilt': tilt,
        'Relief': relief,
        'PlanCurvature': plan_curvature,
        'ProfileCurvature': profile_curvature,
        'Temperature': weather_data['temperature'],
        'Humidity': weather_data['humidity'],
        'WindSpeed': weather_data['wind_speed'],
        'AtmosphericPressure': weather_data['pressure'],
        'SoilMoisture': soil_moisture if soil_moisture is not None else np.nan
    }

def process_locations(locations, google_maps_token, openweather_api_key, output_file):
    results = []
    for location in locations:
        print(f"Processing {location}...")
        result = process_location(location, google_maps_token, openweather_api_key)
        if result:
            results.append(result)
        else:
            print(f"Failed to process {location}")

    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    google_maps_token = "AIzaSyBlJfGgpP2kN06cTUkpcY1VZLsflD2_ux0"  # Replace with your actual Google Maps API key
    openweather_api_key = "dff8a714e30a29e438b4bd2ebb11190f"  # Replace with your actual OpenWeatherMap API key
    
    locations = [
    # Bhutan
    "Thimphu, Bhutan",
    "Paro, Bhutan",
    "Punakha, Bhutan",
    "Wangdue Phodrang, Bhutan",
    "Haa Valley, Bhutan",
    "Bumthang, Bhutan",
    
    # China
    "Tibet, China",
    "Lhasa, Tibet, China",
    "Shigatse, Tibet, China",
    "Ganzi Tibetan Autonomous Prefecture, China",
    "Nyingchi, Tibet, China",
    "Dali, Yunnan, China",
    "Zhongdian, Yunnan, China",
    
    # Sri Lanka
    "Nuwara Eliya, Sri Lanka",
    "Ella, Sri Lanka",
    "Haputale, Sri Lanka",
    "Badulla, Sri Lanka",
    "Kandy, Sri Lanka",
    
    # Myanmar
    "Shan State, Myanmar",
    "Kachin State, Myanmar",
    "Chin State, Myanmar",
    "Magway Region, Myanmar",
    "Kayah State, Myanmar",
    
    # Pakistan
    "Murree, Pakistan",
    "Nathiagali, Pakistan",
    "Abbottabad, Pakistan",
    "Kaghan Valley, Pakistan",
    "Hunza Valley, Pakistan",
    "Skardu, Pakistan",
    "Fairy Meadows, Pakistan",
    "Swat Valley, Pakistan",
    
    # Afghanistan
    "Kabul, Afghanistan",
    "Bamiyan, Afghanistan",
    "Badakhshan, Afghanistan",
    "Panjshir Valley, Afghanistan",
    "Nuristan, Afghanistan",
    
    # Other neighboring countries
    "Nepalgunj, Nepal",
    "Pokhara, Nepal",
    "Kathmandu, Nepal",
    "Gorkha, Nepal",
    "Jomsom, Nepal",
    "Darjeeling, West Bengal, India",
    "Kalimpong, West Bengal, India",
    "Gangtok, Sikkim, India"
]
    
    output_file = "b.csv"
    
    process_locations(locations, google_maps_token, openweather_api_key, output_file)
    