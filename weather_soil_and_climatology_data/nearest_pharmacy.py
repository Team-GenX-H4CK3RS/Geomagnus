# import requests

# # Step 1: Get the user's location based on their IP using Mapbox
# def get_user_location(mapbox_token):
#     mapbox_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/"
#     ip_info_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{mapbox_token}.json?types=country,region,postcode,district,place,locality,neighborhood,address&limit=1"
#     response = requests.get(ip_info_url)
#     data = response.json()
    
#     if response.status_code == 200:
#         loc = data['center']  # Extract latitude and longitude
#         latitude = loc[1]  # Lat is the second item
#         longitude = loc[0]  # Lon is the first item
#         return float(latitude), float(longitude)
#     else:
#         raise Exception(f"Unable to retrieve location: {data}")

# # Step 2: Find nearby pharmacies using Mapbox's Places API
# def find_nearest_pharmacy(mapbox_token, latitude, longitude):
#     search_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/pharmacy.json"
#     params = {
#         'proximity': f'{longitude},{latitude}',  # Coordinates for proximity search
#         'access_token': mapbox_token,
#         'limit': 5  # Limit to 5 nearest pharmacies
#     }
    
#     response = requests.get(search_url, params=params)
#     data = response.json()
    
#     if 'features' in data and data['features']:
#         pharmacies = data['features']
#         for i, pharmacy in enumerate(pharmacies, start=1):
#             name = pharmacy['text']
#             address = pharmacy['place_name']
#             print(f"{i}. {name} - Address: {address}")
#     else:
#         print("No nearby pharmacies found.")

# # Main function
# if __name__ == "__main__":
#     try:
#         # Replace 'your_mapbox_token' with your actual Mapbox token
#         mapbox_token = "pk.eyJ1IjoiYW5raXRoLTU1IiwiYSI6ImNtMjNqYXg2eDA3dGwyanF3bWEycHRxbXgifQ.LLo6Dvxm16a_pwIHKPFETQ"
#         latitude, longitude = get_user_location(mapbox_token)
#         print(f"User's location: Latitude {latitude}, Longitude {longitude}")
        
#         find_nearest_pharmacy(mapbox_token, latitude, longitude)
        
#     except Exception as e:
#         print("Error:", str(e))
import requests

# Step 1: Get the user's location based on their IP using ipinfo.io
def get_user_location():
    ip_info_url = "http://ipinfo.io"
    response = requests.get(ip_info_url)
    data = response.json()
    
    if 'loc' in data:
        loc = data['loc'].split(',')  # loc contains latitude and longitude in 'lat,long' format
        latitude = loc[0]
        longitude = loc[1]
        return float(latitude), float(longitude)
    else:
        raise Exception(f"Unable to retrieve location from IP address: {data}")

# Step 2: Find nearby pharmacies using Mapbox's Places API
def find_nearest_pharmacy(mapbox_token, latitude, longitude):
    search_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/pharmacy.json"
    params = {
        'proximity': f'{longitude},{latitude}',  # Coordinates for proximity search
        'access_token': mapbox_token,
        'limit': 5  # Limit to 5 nearest pharmacies
    }
    
    response = requests.get(search_url, params=params)
    data = response.json()
    
    if 'features' in data and data['features']:
        pharmacies = data['features']
        for i, pharmacy in enumerate(pharmacies, start=1):
            name = pharmacy['text']
            address = pharmacy['place_name']
            print(f"{i}. {name} - Address: {address}")
    else:
        print("No nearby pharmacies found.")

# Main function
if __name__ == "__main__":
    try:
        # Replace 'your_mapbox_token' with your actual Mapbox token
        mapbox_token = "pk.eyJ1IjoiYW5raXRoLTU1IiwiYSI6ImNtMjNqYXg2eDA3dGwyanF3bWEycHRxbXgifQ.LLo6Dvxm16a_pwIHKPFETQ"
        
        # Step 1: Get user's latitude and longitude based on IP
        latitude, longitude = get_user_location()
        print(f"User's location: Latitude {latitude}, Longitude {longitude}")
        
        # Step 2: Find nearest pharmacies using Mapbox API
        find_nearest_pharmacy(mapbox_token, latitude, longitude)
        
    except Exception as e:
        print("Error:", str(e))
