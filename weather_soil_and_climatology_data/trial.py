import requests
from dotenv import load_dotenv
import os

# Function to get current location using ipinfo.io or similar service
def get_current_location():
    try:
        response = requests.get("https://ipinfo.io/")
        response.raise_for_status()
        data = response.json()
        loc = data['loc'].split(',')  # 'loc' provides "latitude,longitude"
        print(f"Detected Location from IP: {loc[0]}, {loc[1]}")
        return float(loc[0]), float(loc[1])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching location: {e}")
        return None, None

# Function to manually input location if IP geolocation fails or is inaccurate
def get_manual_location():
    try:
        latitude = float(input("Enter your latitude: "))
        longitude = float(input("Enter your longitude: "))
        return latitude, longitude
    except ValueError:
        print("Invalid input. Please enter numeric latitude and longitude.")
        return None, None

# Main execution
if __name__ == "__main__":
    try:
        print("Starting the script...")
        
        # Load environment variables from .env file
        load_dotenv()
        
        # Fetch the user's current location
        latitude, longitude = get_current_location()
        
        if latitude is None or longitude is inaccurate:
            print("IP-based location inaccurate. Please enter your location manually.")
            latitude, longitude = get_manual_location()
        
        if latitude is not None and longitude is not None:
            access_token = os.getenv("MAPBOX_TOKEN")  # Ensure this is set in your .env file
            
            if not access_token:
                print("Mapbox access token not found. Please set it in your .env file.")
            else:
                print(f"Using Mapbox token: {access_token}")
                fetch_nearby_hospitals(latitude, longitude, access_token)
    
    except Exception as e:
        print(f"An error occurred: {e}")
