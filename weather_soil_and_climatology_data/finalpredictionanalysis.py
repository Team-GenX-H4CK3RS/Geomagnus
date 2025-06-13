import numpy as np
import pandas as pd
import requests

# Function to calculate tilt/slope between two points using elevation difference and distance
def calculate_tilt(elevation_diff, distance):
    return np.degrees(np.arctan(elevation_diff / distance))  # Tilt in degrees

# Haversine function to calculate distance between two geographic coordinates
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Radius of the Earth in meters
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    a = np.sin(delta_phi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) ** 2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))  # Distance in meters

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

# Function to get coordinates of a location using Google Maps Geocoding API
def get_coordinates(location_name, google_maps_token):
    geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    params = {
        'address': location_name,
        'key': google_maps_token  # Your Google Maps API key
    }
    
    response = requests.get(geocoding_url, params=params)
    data = response.json()
    
    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        latitude = location['lat']
        longitude = location['lng']
        return latitude, longitude
    else:
        print(f"Geocoding error: {data['status']} - {data.get('error_message', '')}")
        return None, None

# Main function
if __name__ == "__main__":
    try:
        # Replace with your actual Google Maps API key
        google_maps_token = "AIzaSyBlJfGgpP2kN06cTUkpcY1VZLsflD2_ux0"  # Your Google Maps API key
        
        # Get location name from user input
        location_name = input("Enter the location name: ")
        
        # Get coordinates for the location name
        lat, lon = get_coordinates(location_name, google_maps_token)

        if lat is not None and lon is not None:
            print(f"Coordinates for '{location_name}': Latitude {lat}, Longitude {lon}")

            # Get the elevation for the specific latitude and longitude
            elevation = get_elevation(lat, lon)

            if elevation is not None:
                print(f"Elevation at main point (lat: {lat}, lon: {lon}): {elevation} meters")

                # Use a larger distance, 500 meters, for comparison
                nearby_distance = 500  # in meters
                lat_offset = lat + (nearby_distance / 6371000) * (180 / np.pi)  # Move latitude slightly for comparison

                # Get elevation for the nearby point
                nearby_elevation = get_elevation(lat_offset, lon)

                if nearby_elevation is not None:
                    print(f"Elevation at nearby point (lat: {lat_offset}, lon: {lon}): {nearby_elevation} meters")

                    # Calculate tilt and slope using the two elevations
                    elevation_diff = nearby_elevation - elevation
                    print(f"Elevation difference: {elevation_diff} meters")

                    tilt = calculate_tilt(elevation_diff, nearby_distance)
                    slope = tilt  # Since slope and tilt are similar concepts
                    print(f"Tilt: {tilt} degrees")

                    # Relief: Assume reference elevation (sea level) as 0m for simplicity
                    relief = abs(elevation - 0)
                    print(f"Relief: {relief} meters")

                    # Plan and Profile Curvature: Approximated using the difference over 500 meters
                    plan_curvature = elevation_diff / nearby_distance  # Approximation
                    profile_curvature = elevation_diff / nearby_distance  # Approximation
                    print(f"Plan Curvature: {plan_curvature}")
                    print(f"Profile Curvature: {profile_curvature}")

                    # Create a DataFrame with the single point's data and calculated parameters
                    df = pd.DataFrame([[lat, lon, elevation, tilt, slope, relief, plan_curvature, profile_curvature]],
                                      columns=['Latitude', 'Longitude', 'Elevation', 'Tilt', 'Slope', 'Relief', 'Plan Curvature', 'Profile Curvature'])

                    # Display the DataFrame
                    print(df)

                else:
                    print("Failed to retrieve nearby elevation data.")
            else:
                print("Failed to retrieve elevation data.")
        else:
            print("Failed to retrieve coordinates.")
    
    except Exception as e:
        print("An error occurred:", e)
