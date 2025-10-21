"""
Main entry point and CLI for the Movie database app.

Provides a text-based menu to list, add, delete, update, and search movies,
show basic statistics from the stored data, and generate a static website.
"""

import random
from data.movie_api import fetch_movie_data
from static.website_gen import generate_website
from storage import movie_storage_sql as storage


RUN_PROGRAM = True

MENU_OPTIONS = [
    "Exit",
    "List movies",
    "Add movie",
    "Delete movie",
    "Update movie",
    "Stats",
    "Random movie",
    "Search movie",
    "Movies sorted by rating",
    "Generate website",
]


def print_menu(menu_options):
    """Render and return the menu as a formatted string."""
    print("\n********** WELCOME TO MY MOVIE DATABASE **********\n")
    body = ["MENU:"]
    for idx, label in enumerate(menu_options):
        body.append(f"{idx}. {label}")
    return "\n".join(body) + "\n"


def get_movie_data():
    """
    Return all movies as a dictionary.

    Example:
        {
            "Inception": {"year": 2010, "rating": 9.0, "poster": "..."},
            ...
        }
    """
    return storage.get_movies()


def command_list_movies():
    """Print all movies with their ratings and release years."""
    movies = get_movie_data()
    if not movies:
        print("No movies in database.")
        return
    print(f"\n{len(movies)} movies in total:")
    for title, data in movies.items():
        print(f"{title}: Rating {data.get('rating')}, Year {data.get('year')}")


def command_add_movie():
    """
    Prompt user for a movie title, fetch its data from OMDb,
    and store it in the database.
    """
    movies = get_movie_data()
    title_input = input("Enter movie title: ").strip()
    if not title_input:
        print("Title cannot be empty.")
        return

    # Duplicate check (case-insensitive)
    lower_titles = {t.lower() for t in movies.keys()}
    if title_input.lower() in lower_titles:
        print(f"Movie already exists as '{title_input}'.")
        return

    # Fetch data via API client
    result = fetch_movie_data(title_input)
    if result is None:
        # fetch_movie_data already prints a helpful message
        return

    year, rating, poster_url, fetched_title = result

    # Fallbacks
    if year is None:
        year = 0
    if rating is None:
        rating = 0.0
    poster_url = poster_url or ""

    success = storage.add_movie(fetched_title, year, rating, poster_url)
    if success:
        print(f"Added '{fetched_title}' with rating {rating}, year {year}")
    else:
        print("Failed to add movie. Please try again.")


def command_delete_movie():
    """Prompt user to delete a movie (exact title match)."""
    title = input("Enter movie name to delete: ").strip()
    if not title:
        print("Title cannot be empty.")
        return
    success = storage.delete_movie(title)
    if success:
        print(f"Movie '{title}' deleted.")
    else:
        print("Movie not found or could not be deleted.")


def command_update_movie():
    """Prompt user to update a movie's rating (exact title match)."""
    title = input("Enter movie name to update: ").strip()
    if not title:
        print("Title cannot be empty.")
        return

    # Rating input only
    while True:
        try:
            new_rating = float(input("Enter new rating (0-10): "))
            break
        except ValueError:
            print("Invalid input. Please enter a number for rating.")

    success = storage.update_movie(title, rating=new_rating)
    if success:
        print(f"Updated '{title}' with rating {new_rating}")
    else:
        print("Movie not found or update failed.")


def command_stats_of_movies():
    """Display basic statistics of stored movie ratings."""
    storage.stats_of_movies()


def command_random_movie():
    """Select and display a random movie from the database."""
    movies = get_movie_data()
    if not movies:
        print("No movies in database.")
        return
    title, data = random.choice(list(movies.items()))
    print(f"Tonight's movie: {title} (Rating: {data.get('rating')}, Year {data.get('year')})")


def command_search_movie():
    """Search for movies by partial title (case-insensitive)."""
    movies = get_movie_data()
    if not movies:
        print("No movies in database.")
        return

    query = input("Enter part of movie name to search: ").strip().lower()
    if not query:
        print("Search text cannot be empty.")
        return

    matches = {t: d for t, d in movies.items() if query in t.lower()}
    if matches:
        for title, data in matches.items():
            print(f"{title}: Rating {data.get('rating')}, Year {data.get('year')}")
    else:
        print(f"No matching movies found for '{query}'.")


def command_ranking_of_movies():
    """Display all movies sorted by rating in descending order."""
    movies = get_movie_data()
    if not movies:
        print("No movies in database.")
        return

    print("\nMovies sorted by rating:")
    for title, data in sorted(movies.items(),
                              key=lambda item: item[1].get("rating", 0),
                              reverse=True):
        print(f"{title}: Rating {data.get('rating')}, Year {data.get('year')}")


def command_generate_website():
    """Generate a static website (index.html) with all movies."""
    generate_website(title="MY MOVIE APP")


def command_exit_program():
    """Exit the program loop."""
    global RUN_PROGRAM
    RUN_PROGRAM = False
    print("Bye!\n********** END OF PROGRAM **********")


def main():
    """Run the main program loop and dispatch menu commands."""
    dispatcher = {
        0: command_exit_program,
        1: command_list_movies,
        2: command_add_movie,
        3: command_delete_movie,
        4: command_update_movie,
        5: command_stats_of_movies,
        6: command_random_movie,
        7: command_search_movie,
        8: command_ranking_of_movies,
        9: command_generate_website,
    }

    loop_count = 0
    while RUN_PROGRAM:
        if loop_count >= 1:
            input("\nPress [ENTER] to continue.\n")

        try:
            print(print_menu(MENU_OPTIONS))
            min_choice, max_choice = min(dispatcher), max(dispatcher)
            raw = input(f"ENTER CHOICE ({min_choice} - {max_choice}): ").strip()
            user_choice = int(raw)
            if user_choice not in dispatcher:
                print(f"\nInvalid choice. Please enter a number between "
                      f"{min_choice} and {max_choice}.\n")
                continue

            action = dispatcher[user_choice]
            action()
        except ValueError:
            print("\nInvalid input. Please type a number.\n")

        loop_count += 1


if __name__ == "__main__":
    main()
