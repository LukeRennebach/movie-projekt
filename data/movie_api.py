"""
Client module for retrieving movie information from the OMDb API.

Uses an API key loaded from a .env file and returns structured movie data
(title, year, rating, poster URL) for a given title.
"""

import os
import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("KEY")  # Ensure your .env file contains: KEY=your_api_key
API_URL = "http://www.omdbapi.com/"


def fetch_movie_data(title):
    """
    Retrieve movie information from the OMDb API by title.

    Args:
        title (str): The movie title to search for.

    Returns:
        tuple: (year, rating, poster_url, fetched_title) if found,
               otherwise None.
    """
    params = {"t": title, "apikey": API_KEY}
    response = requests.get(API_URL, params=params)
    data = response.json()

    if data.get("Response") == "False":
        print(f"Movie '{title}' not found: {data.get('Error')}")
        return None

    fetched_title = data.get("Title", title)
    year = data.get("Year", "N/A")
    rating = data.get("imdbRating", "N/A")
    poster_url = data.get("Poster", "N/A")

    print(year, rating, poster_url, fetched_title)
    return year, rating, poster_url, fetched_title
