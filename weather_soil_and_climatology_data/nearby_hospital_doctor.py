import requests
from dotenv import load_dotenv
import os

def fetch_nearby_hospitals(latitude, longitude, access_token):
    query = "hospital"  # Search for hospitals
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"
    
    params = {
        "proximity": f"{longitude},{latitude}",
        "access_token": access_token,
        "types": "poi",
        "limit": 5  # Adjust this number to get more or fewer results
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad responses
        data = response.json()
        
        if 'features' in data and len(data['features']) > 0:
            print("Nearby Hospitals:")
            for hospital in data['features']:
                name = hospital['text']
                coordinates = hospital['center']
                
                # Construct detailed address
                address_parts = [name]
                if 'address' in hospital:
                    address_parts.append(hospital['address'])
                
                context = hospital.get('context', [])
                for item in context:
                    if item['id'].startswith('neighborhood'):
                        address_parts.append(item['text'])
                    elif item['id'].startswith('postcode'):
                        address_parts.append(item['text'])
                    elif item['id'].startswith('place'):
                        address_parts.append(item['text'])
                    elif item['id'].startswith('region'):
                        address_parts.append(item['text'])
                    elif item['id'].startswith('country'):
                        address_parts.append(item['text'])
                
                detailed_address = ", ".join(address_parts)
                
                print(f"Name: {name}")
                print(f"Detailed Address: {detailed_address}")
                print(f"Coordinates: {coordinates[1]}, {coordinates[0]}")
                print("--------------------")
        else:
            print("No hospitals found.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

# Example usage
if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file
    
    latitude = 12.75254324291148  # Replace with desired latitude
    longitude = 80.19182909380226  # Replace with desired longitude
    access_token = os.getenv("MAPBOX_TOKEN")  # Make sure this is set in your .env file
   


    if not access_token:
        print("Mapbox access token not found. Please set it in your .env file.")
    else:
        fetch_nearby_hospitals(latitude, longitude, access_token)