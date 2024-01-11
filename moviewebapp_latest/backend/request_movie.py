"""Creating API method to connect Web"""
import json
import requests

YOUR_API_KEY = "ae98550b"
BASE_URL = "http://www.omdbapi.com"


class RequestErrors(Exception):
    """RequestErrors is a class for raising errors."""

    def __init__(self, message: object) -> None:
        super().__init__(message)


def get_name_method_requests(method_name: str, movie_name: str) -> str:
    """Sets the  movie name search end point method.
    Args:
        method_name (str): "name" string.
        movie_name (str): given string by user.
    Returns:
        str: returns whole url modified by user input.
    """
    method_api = {"name": f"{BASE_URL}/?t={movie_name}&apikey={YOUR_API_KEY}"}
    if method_name in method_api:
        return method_api[method_name]
    return None


def get_by_name(movie_name: str) -> dict:
    """get_by_name is a method that returns a dict.
    Args:
        movie_name (str): given string by user.
    Returns:
        parsed_data: returns dictionary of movie.
    """
    request_api = get_name_method_requests("name", movie_name)
    if request_api is not None:
        try:
            response = requests.get(request_api, timeout=5)
            parsed_data = json.loads(response.text)
            # Check for HTTP error status codes
            response.raise_for_status()
            response_status = parsed_data.get("Response", "Unknown")
            title_status = parsed_data.get("Title", "Unknown")
            # Unvalid user text returns Response: False
            if not response_status == "True" or title_status == "Unknown":
                raise RequestErrors(f"Entered movie name: {movie_name} has no response")
            return parsed_data
        except requests.exceptions.RequestException as rer:
            raise RequestErrors(
                f"Error requesting page {request_api}:\n\t--> {rer}"
            ) from rer
    return None


def extract_movie_data(movie_name):
    """Extract Title, Director, Year, imdbRating"""
    movie = get_by_name(movie_name)
    extracted_movie_data = {
        "Title": movie.get("Title"),
        "Year": movie.get("Year", "Not provided"),
        "imdbRating": movie.get("imdbRating", 0.0),
        "Poster": movie.get("Poster", "Not provided"),
    }
    return extracted_movie_data
