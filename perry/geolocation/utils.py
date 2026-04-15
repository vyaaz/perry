from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable


def geocode_address(address):
    """
    Geocode an address to latitude and longitude using Nominatim.
    Returns (latitude, longitude) or (None, None) if failed.
    """
    geolocator = Nominatim(user_agent="perry-crm")
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return location.latitude, location.longitude
    except (GeocoderTimedOut, GeocoderUnavailable):
        pass
    return None, None