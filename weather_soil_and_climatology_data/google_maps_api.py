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

# Step 2: Find nearby pharmacies using Google Maps Places API
def find_nearest_pharmacy(google_maps_token, latitude, longitude):
    search_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': f'{latitude},{longitude}',  # Coordinates for proximity search
        'radius': 5000,  # Search within a 5 km radius
        'keyword': 'pharmacy',  # Searching for pharmacies
        'key': google_maps_token  # Your Google Maps API key
    }
    
    response = requests.get(search_url, params=params)
    data = response.json()
    
    if 'results' in data and data['results']:
        pharmacies = data['results']
        for i, pharmacy in enumerate(pharmacies, start=1):
            name = pharmacy['name']
            address = pharmacy.get('vicinity', 'No address provided')
            print(f"{i}. {name} - Address: {address}")
    else:
        print("No nearby pharmacies found.")

# Main function
if __name__ == "__main__":
    try:
        # Replace 'your_google_maps_token' with your actual Google Maps API key
        google_maps_token = "AIzaSyBlJfGgpP2kN06cTUkpcY1VZLsflD2_ux0"
        
        # Step 1: Get user's latitude and longitude based on IP
        latitude, longitude = get_user_location()
        print(f"User's location: Latitude {latitude}, Longitude {longitude}")
        
        # Step 2: Find nearest pharmacies using Google Maps API
        find_nearest_pharmacy(google_maps_token, latitude, longitude)
        
    except Exception as e:
        print("Error:", str(e))
