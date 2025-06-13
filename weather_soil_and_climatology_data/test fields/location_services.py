# # # # # # # import geocoder
# # # # # # # import requests
# # # # # # # from typing import Tuple, Dict

# # # # # # # def get_location_services():
# # # # # # #     """Independent location services with Google Geocoding"""
    
# # # # # # #     def get_current_location() -> Tuple[float, float]:
# # # # # # #         """Get current location using IP geolocation"""
# # # # # # #         try:
# # # # # # #             g = geocoder.ip('me')
# # # # # # #             if g.ok:
# # # # # # #                 return 12.9915, 80.2337
# # # # # # #             else:
# # # # # # #                 print("Could not determine location automatically")
# # # # # # #                 # Default to New Delhi coordinates
# # # # # # #                 return 28.6139, 77.2090
# # # # # # #         except Exception as e:
# # # # # # #             print(f"Error getting current location: {e}")
# # # # # # #             return 28.6139, 77.2090

# # # # # # #     def get_location_info(lat: float, lon: float) -> Dict:
# # # # # # #         """Get detailed location information using Google Geocoding API"""
# # # # # # #         try:
# # # # # # #             api_key = 'AIzaSyBfd1bm_3mxeU8VhNwt2GE9-h0BtMT2Sv4'
# # # # # # #             url = "https://maps.googleapis.com/maps/api/geocode/json"
# # # # # # #             params = {
# # # # # # #                 'latlng': f"{lat},{lon}",
# # # # # # #                 'key': api_key
# # # # # # #             }
            
# # # # # # #             response = requests.get(url, params=params)
# # # # # # #             if response.status_code == 200:
# # # # # # #                 data = response.json()
# # # # # # #                 if data['results']:
# # # # # # #                     return {
# # # # # # #                         'formatted_address': data['results'][0]['formatted_address'],
# # # # # # #                         'components': data['results'][0]['address_components']
# # # # # # #                     }
# # # # # # #             return {'formatted_address': f"Lat: {lat}, Lon: {lon}", 'components': []}
# # # # # # #         except Exception as e:
# # # # # # #             print(f"Error getting location info: {e}")
# # # # # # #             return {'formatted_address': f"Lat: {lat}, Lon: {lon}", 'components': []}

# # # # # # #     # Main execution
# # # # # # #     lat, lon = get_current_location()
# # # # # # #     location_info = get_location_info(lat, lon)
    
# # # # # # #     print(f"📍 Current Location: {lat:.4f}, {lon:.4f}")
# # # # # # #     print(f"📍 Address: {location_info['formatted_address']}")
    
# # # # # # #     return {
# # # # # # #         'latitude': lat,
# # # # # # #         'longitude': lon,
# # # # # # #         'address': location_info['formatted_address'],
# # # # # # #         'components': location_info['components']
# # # # # # #     }

# # # # # # # # Run the function
# # # # # # # if __name__ == "__main__":
# # # # # # #     result = get_location_services()
# # # # # # #     print(f"Location Data: {result}")


# # # # # # import gpsd

# # # # # # # Connect to the local gpsd
# # # # # # gpsd.connect()

# # # # # # # Get current GPS data
# # # # # # packet = gpsd.get_current()
# # # # # # latitude, longitude = packet.position()

# # # # # # print(f"Live GPS Coordinates: {latitude}, {longitude}")

# # # # # import geocoder

# # # # # # Get current location based on IP address
# # # # # location = geocoder.ip('me')
# # # # # latitude, longitude = location.latlng

# # # # # print(f"Latitude: {latitude}, Longitude: {longitude}")
# # # # import winrt.windows.devices.geolocation as wdg, asyncio

# # # # async def getCoords():
# # # #     locator = wdg.Geolocator()
# # # #     pos = await locator.get_geoposition_async()
# # # #     return [pos.coordinate.latitude, pos.coordinate.longitude]

# # # # def getLoc():
# # # #     return asyncio.run(getCoords())

# # # # print(getLoc())


# # # from geopy.geocoders import Nominatim

# # # geolocator = Nominatim(user_agent="geoapi")
# # # location = geolocator.reverse((latitude, longitude))
# # # print("Address:", location.address)

# # import geocoder
# # from geopy.geocoders import Nominatim

# # # Step 1: Get coordinates using geocoder
# # g = geocoder.ip('me')
# # latitude, longitude = g.latlng  # Now these variables are defined

# # print(f"Latitude: {latitude}, Longitude: {longitude}")

# # # Step 2: Reverse geocoding to get address
# # geolocator = Nominatim(user_agent="geoapi")
# # location = geolocator.reverse((latitude, longitude))
# # print("Address:", location.address)
# import requests

# def get_coords_from_ip():
#     response = requests.get('https://ipinfo.io/json')
#     data = response.json()
#     loc = data['loc']  # e.g., "28.6139,77.2090"
#     latitude, longitude = map(float, loc.split(','))
#     return latitude, longitude

# latitude, longitude = get_coords_from_ip()
# print(f"Latitude: {latitude}, Longitude: {longitude}")

import requests

def get_coords_from_ip():
    response = requests.get('https://ipinfo.io/json')
    data = response.json()
    loc = data['loc']
    latitude, longitude = map(float, loc.split(','))
    return latitude, longitude

def reverse_geocode(api_key, latitude, longitude):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'latlng': f'{latitude},{longitude}',
        'key': api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK' and data['results']:
            return data['results'][0]['formatted_address']
        else:
            return None
    else:
        return None

api_key = "AIzaSyBfd1bm_3mxeU8VhNwt2GE9-h0BtMT2Sv4"
latitude, longitude = get_coords_from_ip()
print(f"Latitude: {latitude}, Longitude: {longitude}")

address = reverse_geocode(api_key, latitude, longitude)
print(f"Approximate Address: {address}")
