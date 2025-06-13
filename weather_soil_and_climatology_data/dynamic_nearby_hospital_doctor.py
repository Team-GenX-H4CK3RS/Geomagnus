# import requests
# from dotenv import load_dotenv
# import os

# # Function to get current location using ipinfo.io or similar service
# def get_current_location():
#     try:
#         response = requests.get("https://ipinfo.io/")
#         response.raise_for_status()
#         data = response.json()
#         loc = data['loc'].split(',')  # 'loc' provides "latitude,longitude"
#         return float(loc[0]), float(loc[1])
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching location: {e}")
#         return None, None

# def fetch_nearby_hospitals(latitude, longitude, access_token):
#     query = "hospital"  # Search for hospitals
#     url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"
    
#     params = {
#         "proximity": f"{longitude},{latitude}",
#         "access_token": access_token,
#         "types": "poi",
#         "limit": 5  # Adjust this number to get more or fewer results
#     }
    
#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()  # Raise an exception for bad responses
#         data = response.json()
        
#         if 'features' in data and len(data['features']) > 0:
#             print("Nearby Hospitals:")
#             for hospital in data['features']:
#                 name = hospital['text']
#                 coordinates = hospital['center']
                
#                 # Construct detailed address
#                 address_parts = [name]
#                 if 'address' in hospital:
#                     address_parts.append(hospital['address'])
                
#                 context = hospital.get('context', [])
#                 for item in context:
#                     if item['id'].startswith('neighborhood'):
#                         address_parts.append(item['text'])
#                     elif item['id'].startswith('postcode'):
#                         address_parts.append(item['text'])
#                     elif item['id'].startswith('place'):
#                         address_parts.append(item['text'])
#                     elif item['id'].startswith('region'):
#                         address_parts.append(item['text'])
#                     elif item['id'].startswith('country'):
#                         address_parts.append(item['text'])
                
#                 detailed_address = ", ".join(address_parts)
                
#                 print(f"Name: {name}")
#                 print(f"Detailed Address: {detailed_address}")
#                 print(f"Coordinates: {coordinates[1]}, {coordinates[0]}")
#                 print("--------------------")
#         else:
#             print("No hospitals found.")
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching data: {e}")

# # Example usage
# if __name__ == "__main__":
#     load_dotenv()  # Load environment variables from .env file
    
#     # Fetch the user's current location
#     latitude, longitude = get_current_location()
    
#     if latitude is None or longitude is None:
#         print("Unable to fetch current location. Please enter manually.")
#     else:
#         access_token = os.getenv("MAPBOX_TOKEN")  # Make sure this is set in your .env file
        
#         if not access_token:
#             print("Mapbox access token not found. Please set it in your .env file.")
#         else:
#             fetch_nearby_hospitals(latitude, longitude, access_token)


import requests
from dotenv import load_dotenv
import os

# Function to get current location using ipinfo.io or similar service
def get_current_location():
    try:
        response = requests.get("https://ipinfo.io/")
        response.raise_for_status()
        data = response.json()
        print(data)
        loc = data['loc'].split(',')  # 'loc' provides "latitude,longitude"
        print(f"Current Location: {loc[0]}, {loc[1]}")
        return float(loc[0]), float(loc[1])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching location: {e}")
        return None, None

# Function to fetch nearby hospitals
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

# Main execution
if __name__ == "__main__":
    try:
        print("Starting the script...")
        
        # Load environment variables from .env file
        load_dotenv()
        
        # Fetch the user's current location
        latitude, longitude = get_current_location()
        
        if latitude is None or longitude is None:
            print("Unable to fetch current location. Please enter manually.")
        else:
            access_token = os.getenv("MAPBOX_TOKEN")  # Ensure this is set in your .env file
            
            if not access_token:
                print("Mapbox access token not found. Please set it in your .env file.")
            else:
                print(f"Using Mapbox token: {access_token}")
                fetch_nearby_hospitals(latitude, longitude, access_token)
    
    except Exception as e:
        print(f"An error occurred: {e}")
