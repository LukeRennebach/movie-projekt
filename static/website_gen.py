"""
Generate a static HTML website from the stored movie data.

Builds a simple list of movies with title, year, and poster using
a template string or an external HTML file.
"""

from html import escape
from pathlib import Path
from storage import movie_storage_sql as storage


TEMPLATE_DEFAULT = """<!doctype html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>My Movie App</title>
    <link rel="stylesheet" href="style.css"/>
</head>
<body>
<div class="list-movies-title">
    <h1>__TEMPLATE_TITLE__</h1>
</div>
<div>
    <ol class="movie-grid">
        __TEMPLATE_MOVIE_GRID__
    </ol>
</div>
</body>
</html>
"""


def _movie_li(title: str, year, poster_url: str) -> str:
    """
    Build a single <li> movie element.

    Even if the poster is missing or 'N/A', include the <img> tag
    with an alt attribute for accessibility.
    """
    safe_title = escape(str(title))
    safe_year = escape(str(year)) if year is not None else ""
    safe_poster = escape(poster_url or "N/A")

    return (
        "<li>"
        "<div class='movie'>"
        f"<img class='movie-poster' src='{safe_poster}' "
        f"alt='Poster image not available.'/>"
        f"<div class='movie-title'>{safe_title}</div>"
        f"<div class='movie-year'>{safe_year}</div>"
        "</div>"
        "</li>"
    )


def _build_movie_grid(movies_dict: dict) -> str:
    """
    Build the <ol> movie grid HTML content from the movie dictionary.

    Expects:
        {
            "Title": {"year": 2010, "rating": 8.7, "poster": "https://..."},
            ...
        }
    """
    items = []
    for title, data in movies_dict.items():
        year = data.get("year")
        poster = data.get("poster") or "N/A"
        items.append(_movie_li(title, year, poster))
    return "".join(items)


def _load_template_str(template_path: str | None) -> str:
    """
    Load an external HTML template from disk if provided.

    Falls back to the built-in default template otherwise.
    """
    if not template_path:
        return TEMPLATE_DEFAULT

    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def render_website_html(title: str, template_str: str, movies_dict: dict) -> str:
    """
    Replace placeholders in the HTML template with the given title and movie grid.
    """
    grid_html = _build_movie_grid(movies_dict)
    html = (
        template_str
        .replace("__TEMPLATE_TITLE__", escape(title))
        .replace("__TEMPLATE_MOVIE_GRID__", grid_html)
    )
    return html


def generate_website(
    title: str = "MY MOVIE APP",
    template_path: str | None = None,
    output_path: str | None = None,
) -> None:
    """
    Generate a complete static HTML file from the movie data and template.

    If no output path is given, write the result as 'index.html'
    in the same directory as this script.
    """
    template_str = _load_template_str(template_path)
    movies = storage.get_movies()
    html = render_website_html(title, template_str, movies)

    base_dir = Path(__file__).resolve().parent
    out_path = Path(output_path) if output_path else (base_dir / "index.html")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    print("Website was generated successfully.")


if __name__ == "__main__":
    generate_website()
