from __future__ import annotations

import ast
import re
import pandas as pd

DATA_DIR = "/mnt/user-data/uploads"


def _safe_literal_list(raw, key="name"):
    """Parse TMDB's stringified list-of-dicts columns (genres, keywords)."""
    if not isinstance(raw, str) or not raw.strip():
        return []
    try:
        items = ast.literal_eval(raw)
        return [d[key] for d in items if isinstance(d, dict) and key in d]
    except (ValueError, SyntaxError):
        return []


def _clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def load_movies_metadata() -> pd.DataFrame:
    md = pd.read_csv(f"{DATA_DIR}/movies_metadata.csv", low_memory=False)

    # id should be numeric TMDB id; a handful of rows are corrupted (contain
    # dates from a shifted-column bug in the source CSV) — drop those.
    md = md[md["id"].astype(str).str.isnumeric()].copy()
    md["id"] = md["id"].astype(int)
    md = md.drop_duplicates(subset="id")

    md["vote_average"] = pd.to_numeric(md["vote_average"], errors="coerce").fillna(0)
    md["vote_count"] = pd.to_numeric(md["vote_count"], errors="coerce").fillna(0)
    md["popularity"] = pd.to_numeric(md["popularity"], errors="coerce").fillna(0)
    md["overview"] = md["overview"].fillna("")
    md["genres"] = md["genres"].apply(_safe_literal_list)

    return md[[
        "id", "title", "genres", "overview",
        "vote_average", "vote_count", "popularity", "release_date",
    ]].rename(columns={"id": "tmdbId"})


def load_keywords() -> pd.DataFrame:
    kw = pd.read_csv(f"{DATA_DIR}/keywords.csv")
    kw = kw.drop_duplicates(subset="id")
    kw["keywords"] = kw["keywords"].apply(_safe_literal_list)
    return kw.rename(columns={"id": "tmdbId"})[["tmdbId", "keywords"]]


def load_links_small() -> pd.DataFrame:
    links = pd.read_csv(f"{DATA_DIR}/links_small.csv")
    links = links.dropna(subset=["tmdbId"])
    links["tmdbId"] = links["tmdbId"].astype(int)
    return links[["movieId", "tmdbId"]]


def load_ratings_small(valid_movie_ids: set[int]) -> pd.DataFrame:
    ratings = pd.read_csv(f"{DATA_DIR}/ratings_small.csv")
    ratings = ratings[ratings["movieId"].isin(valid_movie_ids)]
    return ratings[["userId", "movieId", "rating"]]


def build_catalog():
    md = load_movies_metadata()
    kw = load_keywords()
    links = load_links_small()

    # Restrict the content catalog to the movies we actually have
    # MovieLens ratings coverage for (links_small) — this keeps content
    # features and collaborative signal aligned on the same movie set.
    catalog = links.merge(md, on="tmdbId", how="inner")
    catalog = catalog.merge(kw, on="tmdbId", how="left")
    catalog["keywords"] = catalog["keywords"].apply(lambda x: x if isinstance(x, list) else [])
    catalog = catalog.drop_duplicates(subset="tmdbId").reset_index(drop=True)

    # Build the "soup" text used for TF-IDF: genres + keywords weighted
    # higher (repeated) than the free-text overview, since they're cleaner
    # signal for mood/theme matching.
    def make_soup(row):
        genre_txt = " ".join(row["genres"]) * 3
        kw_txt = " ".join(row["keywords"]) * 2
        overview_txt = _clean_text(row["overview"])
        return _clean_text(f"{genre_txt} {kw_txt} {overview_txt}")

    catalog["soup"] = catalog.apply(make_soup, axis=1)
    catalog = catalog.set_index("tmdbId", drop=False)

    ml_to_tmdb = dict(zip(catalog["movieId"], catalog["tmdbId"]))
    tmdb_to_ml = dict(zip(catalog["tmdbId"], catalog["movieId"]))

    ratings = load_ratings_small(valid_movie_ids=set(ml_to_tmdb.keys()))

    return catalog, ml_to_tmdb, tmdb_to_ml, ratings


if __name__ == "__main__":
    catalog, ml_to_tmdb, tmdb_to_ml, ratings = build_catalog()
    print(f"Catalog: {len(catalog)} movies")
    print(f"Ratings: {len(ratings)} rows, {ratings['userId'].nunique()} users")
    print(catalog[["title", "genres", "vote_average"]].head())