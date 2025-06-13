# import requests

# def get_coordinates(address, google_maps_token):
#     # Google Maps Geocoding API endpoint
#     geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
#     # Set up the parameters for the request
#     params = {
#         'address': address,
#         'key': google_maps_token  # Your Google Maps API key
#     }
    
#     # Send the request to the Geocoding API
#     response = requests.get(geocoding_url, params=params)
#     data = response.json()
    
#     if data['status'] == 'OK':
#         # Extract the latitude and longitude from the response
#         location = data['results'][0]['geometry']['location']
#         latitude = location['lat']
#         longitude = location['lng']
#         return latitude, longitude
#     else:
#         raise Exception(f"Geocoding error: {data['status']} - {data.get('error_message', '')}")

# # Example usage
# if __name__ == "__main__":
#     try:
#         google_maps_token = "AIzaSyBlJfGgpP2kN06cTUkpcY1VZLsflD2_ux0"  # Replace with your actual API key
#         address = "Shiv Nadar University, Chennai"  # Replace with the address you want to geocode
#         latitude, longitude = get_coordinates(address, google_maps_token)
#         print(f"Coordinates for '{address}': Latitude {latitude}, Longitude {longitude}")
#     except Exception as e:
#         print("Error:", str(e))


import requests

def get_coordinates(address, google_maps_token):
    # Google Maps Geocoding API endpoint
    geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    # Set up the parameters for the request
    params = {
        'address': address,
        'key': google_maps_token  # Your Google Maps API key
    }
    
    # Send the request to the Geocoding API
    response = requests.get(geocoding_url, params=params)
    data = response.json()
    
    if data['status'] == 'OK':
        # Extract the latitude and longitude from the response
        location = data['results'][0]['geometry']['location']
        latitude = location['lat']
        longitude = location['lng']
        return latitude, longitude
    else:
        raise Exception(f"Geocoding error: {data['status']} - {data.get('error_message', '')}")

# Main function
if __name__ == "__main__":
    try:
        google_maps_token = "AIzaSyBlJfGgpP2kN06cTUkpcY1VZLsflD2_ux0"  # Replace with your actual API key
        
        # User input for address
        address = input("Enter the address or location name: ")
        
        # Get coordinates
        latitude, longitude = get_coordinates(address, google_maps_token)
        print(f"Coordinates for '{address}': Latitude {latitude}, Longitude {longitude}")
        
    except Exception as e:
        print("Error:", str(e))
