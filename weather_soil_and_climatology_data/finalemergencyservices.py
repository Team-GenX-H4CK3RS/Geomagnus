import requests
import math

GEOCODING_API_KEY = 'AIzaSyBlJfGgpP2kN06cTUkpcY1VZLsflD2_ux0'
PLACES_API_KEY = 'AIzaSyBfd1bm_3mxeU8VhNwt2GE9-h0BtMT2Sv4'

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance (in km) between two points on the Earth.
    """
    R = 6371  # Earth radius in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_coordinates(address, api_key):
    geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {'address': address, 'key': api_key}
    response = requests.get(geocoding_url, params=params)
    data = response.json()
    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        raise Exception(f"Geocoding error: {data['status']} - {data.get('error_message', '')}")

def get_place_details(place_id, api_key):
    details_url = (
        f"https://maps.googleapis.com/maps/api/place/details/json?"
        f"place_id={place_id}&fields=name,formatted_phone_number,website,url,rating,review,formatted_address&key={api_key}"
    )
    response = requests.get(details_url)
    data = response.json()
    if data.get('status') == 'OK':
        result = data['result']
        return {
            'phone_number': result.get('formatted_phone_number', 'N/A'),
            'website': result.get('website', 'N/A'),
            'google_url': result.get('url', 'N/A'),
            'rating': result.get('rating', 'N/A'),
            'reviews': result.get('reviews', []),
            'full_address': result.get('formatted_address', 'N/A')
        }
    return {
        'phone_number': 'N/A',
        'website': 'N/A',
        'google_url': 'N/A',
        'rating': 'N/A',
        'reviews': [],
        'full_address': 'N/A'
    }

def print_attractive_results(results):
    for place_type, places in results.items():
        print(f"\nNearby {place_type.replace('_', ' ').title()}s:")
        if not places:
            print("  No results found.")
        else:
            for i, place in enumerate(places, 1):
                print(f"\n  {i}. {place['name']}")
                print(f"     Address: {place['address']}")
                print(f"     Full Address: {place['full_address']}")
                print(f"     Coordinates: ({place['location']['lat']}, {place['location']['lng']})")
                print(f"     Distance: {place['distance_km']} km")
                print(f"     Rating: {place['rating']}")
                print(f"     Phone: {place['phone_number']}")
                print(f"     Website: {place['website']}")
                print(f"     Google Places URL: {place['google_url']}")
                if place['reviews']:
                    print("     Reviews:")
                    for review in place['reviews'][:2]:  # Show up to 2 reviews
                        author = review.get('author_name', 'Anonymous')
                        rating = review.get('rating', 'N/A')
                        text = review.get('text', '')
                        time_desc = review.get('relative_time_description', '')
                        print(f"       - {author} ({time_desc}) - Rating: {rating}")
                        print(f"         \"{text}\"")
                else:
                    print("     Reviews: None")

def main():
    address = input("Enter the address or location name: ")

    # Get latitude and longitude for the address
    latitude, longitude = get_coordinates(address, GEOCODING_API_KEY)
    print(f"\nCoordinates for '{address}': Latitude {latitude}, Longitude {longitude}")

    radius = 5000  # Search radius in meters

    place_types = {
        'hospital': {'type': 'hospital'},
        'police_station': {'type': 'police'},
        'blood_bank': {'keyword': 'blood bank'},
        'restaurant': {'type': 'restaurant'},
        'fire_station': {'type': 'fire_station'}
    }

    results = {}

    for place_type, params in place_types.items():
        url = (
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
            f"location={latitude},{longitude}&radius={radius}&key={PLACES_API_KEY}"
        )
        if 'type' in params:
            url += f"&type={params['type']}"
        if 'keyword' in params:
            url += f"&keyword={params['keyword']}"

        response = requests.get(url)
        data = response.json()

        places_list = []
        for place in data.get('results', [])[:5]:  # Limit to 5 results
            name = place.get('name', 'N/A')
            address = place.get('vicinity', 'N/A')
            location = place['geometry']['location']
            place_id = place.get('place_id')
            details = get_place_details(place_id, PLACES_API_KEY) if place_id else {}

            # Calculate distance
            dist_km = haversine(latitude, longitude, location['lat'], location['lng'])
            dist_km = round(dist_km, 2)

            places_list.append({
                'name': name,
                'address': address,
                'location': location,
                'phone_number': details.get('phone_number', 'N/A'),
                'website': details.get('website', 'N/A'),
                'google_url': details.get('google_url', 'N/A'),
                'rating': details.get('rating', 'N/A'),
                'reviews': details.get('reviews', []),
                'full_address': details.get('full_address', 'N/A'),
                'distance_km': dist_km
            })

        results[place_type] = places_list

    print_attractive_results(results)

if __name__ == "__main__":
    main()