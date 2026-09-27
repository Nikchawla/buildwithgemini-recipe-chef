"""Google Maps Geocoding and Places (New) API tools for recipe-chef agent."""

import json
import os
import urllib.parse
import urllib.request


def _get_maps_api_key() -> str:
    """Reads GOOGLE_MAPS_API_KEY from environment or local .env file."""
    key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not key or key == "PASTE_KEY_HERE":
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GOOGLE_MAPS_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val and val != "PASTE_KEY_HERE":
                            key = val
                        break
    return key or ""


def geocode_address(address: str) -> str:
    """Turn a street address or location name into geographic coordinates (latitude/longitude) using Google Geocoding API.

    Args:
        address: The address or location to geocode (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA' or 'San Francisco, CA').

    Returns:
        Formatted string containing the formatted address and latitude/longitude coordinates.
    """
    api_key = _get_maps_api_key()
    if not api_key or api_key == "PASTE_KEY_HERE":
        return "Error: GOOGLE_MAPS_API_KEY is not set in .env or environment."

    encoded_address = urllib.parse.quote(address.strip())
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RecipeChef/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        status = data.get("status")
        if status != "OK" or not data.get("results"):
            return f"Geocoding failed for address '{address}': {status}"

        result = data["results"][0]
        formatted_address = result.get("formatted_address", address)
        location = result.get("geometry", {}).get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")

        return f"Address: {formatted_address}\nLocation: Latitude {lat}, Longitude {lng}"

    except Exception as e:
        return f"Error geocoding address '{address}': {str(e)}"


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "supermarket",
    radius_meters: float = 1000.0,
) -> str:
    """Find nearby places of a given type around a geographic location using Google Places API (New).

    Args:
        latitude: Geographic latitude coordinate (e.g. 37.7749).
        longitude: Geographic longitude coordinate (e.g. -122.4194).
        place_type: Type of place to search for (e.g. 'supermarket', 'grocery_store', 'restaurant', 'bakery').
        radius_meters: Search radius in meters (default 1000.0 meters).

    Returns:
        Formatted list of nearby places including name, address, and coordinates.
    """
    api_key = _get_maps_api_key()
    if not api_key or api_key == "PASTE_KEY_HERE":
        return "Error: GOOGLE_MAPS_API_KEY is not set in .env or environment."

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
    }

    body = {
        "includedTypes": [place_type.strip().lower()],
        "maxResultCount": 10,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                },
                "radius": float(radius_meters),
            }
        },
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        places = data.get("places", [])
        if not places:
            return f"No nearby places of type '{place_type}' found within {radius_meters}m."

        results = []
        for p in places:
            name = p.get("displayName", {}).get("text", "Unknown Place")
            address = p.get("formattedAddress", "No address provided")
            loc = p.get("location", {})
            lat = loc.get("latitude")
            lng = loc.get("longitude")

            results.append(
                f"- **{name}**\n"
                f"  Address: {address}\n"
                f"  Location: ({lat}, {lng})"
            )

        return f"Found {len(results)} nearby place(s) of type '{place_type}':\n\n" + "\n\n".join(results)

    except Exception as e:
        return f"Error finding nearby places: {str(e)}"
