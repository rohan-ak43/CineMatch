from __future__ import annotations

import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors

from data_pipeline import build_catalog
from mood_engine import mood_scores

DEFAULT_WEIGHTS = {"mood": 0.35, "history": 0.35, "watchlist": 0.20, "quality": 0.10}


class CReqxRecommender:
    def __init__(self):
        self.catalog: pd.DataFrame | None = None
        self.ml_to_tmdb: dict[int, int] = {}
        self.tmdb_to_ml: dict[int, int] = {}
        self.ratings: pd.DataFrame | None = None

        self.tfidf: TfidfVectorizer | None = None
        self.tfidf_matrix = None  # sparse, rows aligned to catalog order
        self.tmdb_ids: list[int] = []  # catalog row order -> tmdbId

        self.item_knn: NearestNeighbors | None = None
        self.movie_vectors = None  # sparse user-rating vectors per movieId
        self.ml_ids: list[int] = []  # movie_vectors row order -> movieId (MovieLens)

        self.quality_prior: pd.Series | None = None

    # Training / fitting
    def fit(self):
        catalog, ml_to_tmdb, tmdb_to_ml, ratings = build_catalog()
        self.catalog = catalog
        self.ml_to_tmdb = ml_to_tmdb
        self.tmdb_to_ml = tmdb_to_ml
        self.ratings = ratings

        self._fit_content_model()
        self._fit_collaborative_model()
        self._fit_quality_prior()
        return self

    def _fit_content_model(self):
        self.tfidf = TfidfVectorizer(max_features=20000, stop_words="english")
        self.tfidf_matrix = self.tfidf.fit_transform(self.catalog["soup"])
        self.tmdb_ids = list(self.catalog["tmdbId"])

    def _fit_collaborative_model(self):
        # item-based CF: rows = movies, cols = users, cells = rating
        pivot = self.ratings.pivot_table(index="movieId", columns="userId", values="rating")
        pivot = pivot.fillna(0)
        self.ml_ids = list(pivot.index)
        self.movie_vectors = sp.csr_matrix(pivot.values)

        n_neighbors = min(21, len(self.ml_ids))  # self + up to 20 neighbors
        self.item_knn = NearestNeighbors(metric="cosine", algorithm="brute")
        self.item_knn.fit(self.movie_vectors)
        self._cf_n_neighbors = n_neighbors

    def _fit_quality_prior(self):
        c = self.catalog
        m = c["vote_count"].quantile(0.60)  # minimum votes threshold
        v_mean = c["vote_average"].mean()

        def bayesian_avg(row):
            v, r = row["vote_count"], row["vote_average"]
            return (v / (v + m)) * r + (m / (v + m)) * v_mean

        raw = c.apply(bayesian_avg, axis=1)
        self.quality_prior = (raw - raw.min()) / (raw.max() - raw.min())

    # Signal scoring
    def _mood_score(self, mood, mood_text) -> pd.Series:
        if not mood and not mood_text:
            return None
        return mood_scores(self.catalog, mood=mood, mood_text=mood_text)

    def _history_score(self, watch_history_ml_ids: list[int]) -> pd.Series | None:
        """Item-based CF: for each watched movie, pull its nearest neighbors
        (other movies liked by similar users) and accumulate similarity,
        weighted by inverse distance."""
        watched = [m for m in watch_history_ml_ids if m in self.ml_ids]
        if not watched:
            return None

        scores = pd.Series(0.0, index=self.catalog.index)
        id_pos = {mid: i for i, mid in enumerate(self.ml_ids)}

        for ml_id in watched:
            idx = id_pos[ml_id]
            distances, neighbor_idx = self.item_knn.kneighbors(
                self.movie_vectors[idx], n_neighbors=self._cf_n_neighbors
            )
            for dist, n_idx in zip(distances[0], neighbor_idx[0]):
                neighbor_ml_id = self.ml_ids[n_idx]
                if neighbor_ml_id == ml_id:
                    continue
                tmdb_id = self.ml_to_tmdb.get(neighbor_ml_id)
                if tmdb_id is None or tmdb_id not in scores.index:
                    continue
                similarity = 1 - dist
                scores.loc[tmdb_id] += max(similarity, 0)

        max_val = scores.max()
        return scores / max_val if max_val > 0 else scores

    def _watchlist_score(self, watchlist_tmdb_ids: list[int]) -> pd.Series | None:
        present = [t for t in watchlist_tmdb_ids if t in self.tmdb_ids]
        if not present:
            return None

        row_positions = [self.tmdb_ids.index(t) for t in present]
        profile_vector = self.tfidf_matrix[row_positions].mean(axis=0)
        profile_vector = np.asarray(profile_vector)
        sims = cosine_similarity(profile_vector, self.tfidf_matrix)[0]
        return pd.Series(sims, index=self.catalog.index)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def recommend(
        self,
        mood: str | None = None,
        mood_text: str | None = None,
        watch_history: list[int] | None = None,   # MovieLens movieIds
        watchlist: list[int] | None = None,        # TMDB ids
        top_n: int = 10,
        weights: dict[str, float] | None = None,
    ) -> pd.DataFrame:
        watch_history = watch_history or []
        watchlist = watchlist or []
        weights = weights or DEFAULT_WEIGHTS

        signals = {
            "mood": self._mood_score(mood, mood_text),
            "history": self._history_score(watch_history),
            "watchlist": self._watchlist_score(watchlist),
            "quality": self.quality_prior,
        }

        active = {k: v for k, v in signals.items() if v is not None}
        active_weight_sum = sum(weights[k] for k in active)
        final = pd.Series(0.0, index=self.catalog.index)
        for k, series in active.items():
            renormalized_weight = weights[k] / active_weight_sum
            final = final.add(series * renormalized_weight, fill_value=0)

        exclude_tmdb = set(watchlist) | {
            self.ml_to_tmdb[m] for m in watch_history if m in self.ml_to_tmdb
        }
        result = self.catalog.copy()
        result["score"] = final
        for k in ("mood", "history", "watchlist", "quality"):
            result[f"{k}_score"] = signals[k] if signals[k] is not None else 0.0

        result = result[~result["tmdbId"].isin(exclude_tmdb)]
        result = result.sort_values("score", ascending=False).head(top_n)

        return result[[
            "tmdbId", "movieId", "title", "genres", "vote_average",
            "score", "mood_score", "history_score", "watchlist_score", "quality_score",
        ]].reset_index(drop=True)


if __name__ == "__main__":
    model = CReqxRecommender().fit()

    print("\n=== Cold start (no mood/history/watchlist) ===")
    print(model.recommend(top_n=5)[["title", "genres", "score"]])

    print("\n=== Mood: excited ===")
    print(model.recommend(mood="excited", top_n=5)[["title", "genres", "score"]])

    sample_history = list(model.ratings[model.ratings["userId"] == 1]["movieId"])[:5]
    print(f"\n=== Watch history signal (user 1's first 5 watched movieIds: {sample_history}) ===")
    print(model.recommend(watch_history=sample_history, top_n=5)[["title", "genres", "score"]])

    sample_watchlist_tmdb = [862, 8844]  # Toy Story, Jumanji
    print(f"\n=== Watchlist signal (tmdbIds {sample_watchlist_tmdb}) ===")
    print(model.recommend(watchlist=sample_watchlist_tmdb, top_n=5)[["title", "genres", "score"]])

    print("\n=== Full hybrid (mood + history + watchlist) ===")
    print(model.recommend(
        mood="thoughtful",
        watch_history=sample_history,
        watchlist=sample_watchlist_tmdb,
        top_n=10,
    )[["title", "genres", "score", "mood_score", "history_score", "watchlist_score"]])