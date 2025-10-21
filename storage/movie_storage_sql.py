from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


# --- Database initialization -------------------------------------------------

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "movies.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DB_URL = f"sqlite:///{DB_PATH.as_posix()}"

engine = create_engine(DB_URL, echo=False)

with engine.begin() as conn:
    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL,
                year INTEGER NOT NULL,
                rating REAL NOT NULL,
                poster TEXT NOT NULL
            )
            """
        )
    )


# --- Operations --------------------------------------------------------------


def get_movies():
    """Return all movies as {title: {year, rating, poster}}."""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT title, year, rating, poster FROM movies")
        )
        rows = result.fetchall()
    return {r[0]: {"year": r[1], "rating": r[2], "poster": r[3]} for r in rows}


def add_movie(title, year, rating, poster):
    """Insert a movie. Return True on success."""
    with engine.begin() as conn:
        try:
            conn.execute(
                text(
                    """
                    INSERT INTO movies (title, year, rating, poster)
                    VALUES (:title, :year, :rating, :poster)
                    """
                ),
                {
                    "title": title,
                    "year": year,
                    "rating": rating,
                    "poster": poster,
                },
            )
            return True
        except IntegrityError:
            print(f"Movie '{title}' already exists.")
            return False
        except Exception as exc:
            print(f"Unexpected error while adding '{title}': {exc}")
            return False


def delete_movie(title):
    """Delete by title (case-insensitive). Return True if something was deleted."""
    with engine.begin() as conn:
        try:
            result = conn.execute(
                text(
                    "DELETE FROM movies WHERE LOWER(title) = :title"
                ),
                {"title": title.lower()},
            )
            return bool(result.rowcount and result.rowcount > 0)
        except Exception as exc:
            print(f"Unexpected error while deleting '{title}': {exc}")
            return False


def update_movie(title, rating=None):
    """Update rating only. Return True if something was updated."""
    if rating is None:
        return False

    params = {"title": title.lower(), "rating": rating}
    query = "UPDATE movies SET rating = :rating WHERE LOWER(title) = :title"

    with engine.begin() as conn:
        try:
            result = conn.execute(text(query), params)
            return bool(result.rowcount and result.rowcount > 0)
        except SQLAlchemyError as exc:
            print(f"Database error while updating '{title}': {exc}")
            return False


def stats_of_movies():
    """Print count, min, max, and average rating."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT rating FROM movies"))
        ratings = [row[0] for row in result.fetchall()]

    if not ratings:
        print("No movies in database.")
        return

    count = len(ratings)
    min_r = min(ratings)
    max_r = max(ratings)
    avg_r = sum(ratings) / count

    print(
        f"Movies: {count} | "
        f"Min rating: {min_r:.2f} | "
        f"Max rating: {max_r:.2f} | "
        f"Avg rating: {avg_r:.2f}"
    )
