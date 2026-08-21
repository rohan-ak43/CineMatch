import os
import pickle

from flask import Blueprint, jsonify, request

ARTIFACT_PATH = os.path.join(os.path.dirname(__file__), "artifacts", "creqx_model.pkl")

recommender_bp = Blueprint("recommender", __name__)

_model = None


def get_model():
    global _model
    if _model is None:
        with open(ARTIFACT_PATH, "rb") as f:
            _model = pickle.load(f)
    return _model


def _movie_payload(row) -> dict:
    return {
        "tmdbId": int(row["tmdbId"]),
        "movieId": int(row["movieId"]),
        "title": row["title"],
        "genres": row["genres"],
        "voteAverage": round(float(row["vote_average"]), 1),
        "matchScore": round(float(row["score"]) * 100, 1),  # 0-100 for UI display
        "breakdown": {
            "mood": round(float(row["mood_score"]), 3),
            "history": round(float(row["history_score"]), 3),
            "watchlist": round(float(row["watchlist_score"]), 3),
            "quality": round(float(row["quality_score"]), 3),
        },
    }


@recommender_bp.route("/mood", methods=["POST"])
def mood_endpoint():
    """
    Body: { "mood": "excited" }               # fixed picker chip, OR
          { "moodText": "kind of a cozy night" }  # free-text mood note
    Returns a quick set of mood-only picks (used right after the mood
    picker on the /mood page, before factoring in history/watchlist).
    """
    body = request.get_json(force=True) or {}
    model = get_model()

    result = model.recommend(
        mood=body.get("mood"),
        mood_text=body.get("moodText"),
        top_n=int(body.get("topN", 12)),
    )
    return jsonify({"results": [_movie_payload(r) for _, r in result.iterrows()]})


@recommender_bp.route("/recommendations", methods=["POST"])
def recommendations_endpoint():
    """
    Body: {
        "mood": "thoughtful",                 # optional
        "moodText": "...",                     # optional, alternative to mood
        "watchHistory": [31, 1029, 1061],       # MovieLens movieIds, optional
        "watchlist": [862, 8844],                # TMDB ids, optional
        "topN": 20                                # optional, default 10
    }
    Full hybrid recommendation combining every signal that's present.
    """
    body = request.get_json(force=True) or {}
    model = get_model()

    result = model.recommend(
        mood=body.get("mood"),
        mood_text=body.get("moodText"),
        watch_history=body.get("watchHistory", []),
        watchlist=body.get("watchlist", []),
        top_n=int(body.get("topN", 10)),
    )
    return jsonify({"results": [_movie_payload(r) for _, r in result.iterrows()]})


@recommender_bp.route("/health", methods=["GET"])
def health():
    model = get_model()
    return jsonify({"status": "ok", "catalogSize": len(model.catalog)})