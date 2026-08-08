from __future__ import annotations

import numpy as np
import pandas as pd

MOOD_PROFILES: dict[str, dict[str, float]] = {
    "happy": {
        "Comedy": 1.0, "Family": 0.8, "Animation": 0.7, "Music": 0.5,
        "feel good": 0.6, "friendship": 0.4,
    },
    "sad": {
        "Drama": 1.0, "Romance": 0.4,
        "loss": 0.5, "tearjerker": 0.6, "grief": 0.5,
    },
    "excited": {
        "Action": 1.0, "Adventure": 0.8, "Science Fiction": 0.5,
        "chase": 0.5, "superhero": 0.4,
    },
    "relaxed": {
        "Documentary": 0.7, "Romance": 0.6, "Comedy": 0.4,
        "slow burn": 0.3, "nature": 0.4,
    },
    "scared": {
        "Horror": 1.0, "Thriller": 0.7, "Mystery": 0.5,
        "supernatural": 0.5, "monster": 0.4,
    },
    "romantic": {
        "Romance": 1.0, "Drama": 0.4, "Comedy": 0.3,
        "wedding": 0.4, "love": 0.5,
    },
    "thoughtful": {
        "Drama": 0.7, "Mystery": 0.6, "Science Fiction": 0.6, "History": 0.5,
        "philosophy": 0.5, "identity": 0.4,
    },
    "nostalgic": {
        "Family": 0.6, "Animation": 0.6, "Adventure": 0.5,
        "childhood": 0.6, "1980s": 0.3,
    },
    "tense": {
        "Thriller": 1.0, "Crime": 0.7, "Mystery": 0.6,
        "conspiracy": 0.4, "heist": 0.4,
    },
}


_FREE_TEXT_LEXICON = {
    "happy": ["happy", "cheerful", "upbeat", "fun", "silly", "lighthearted", "giddy"],
    "sad": ["sad", "down", "blue", "heartbroken", "lonely", "grief", "crying"],
    "excited": ["excited", "hyped", "pumped", "energetic", "adrenaline"],
    "relaxed": ["relaxed", "chill", "cozy", "calm", "lazy", "unwind", "mellow"],
    "scared": ["scared", "spooky", "creepy", "halloween", "horror"],
    "romantic": ["romantic", "love", "date night", "valentine", "cuddle"],
    "thoughtful": ["thoughtful", "reflective", "philosophical", "deep", "existential"],
    "nostalgic": ["nostalgic", "childhood", "throwback", "old school"],
    "tense": ["tense", "on edge", "anxious", "suspense", "thriller mood"],
}


def score_free_text_mood(text: str) -> dict[str, float]:
    text = (text or "").lower()
    hits = {}
    for mood, words in _FREE_TEXT_LEXICON.items():
        count = sum(1 for w in words if w in text)
        if count:
            hits[mood] = count
    if not hits:
        return {}
    total = sum(hits.values())
    return {mood: count / total for mood, count in hits.items()}


def mood_scores(catalog: pd.DataFrame, mood: str | None = None,
                 mood_text: str | None = None) -> pd.Series:
    if mood and mood in MOOD_PROFILES:
        blend = {mood: 1.0}
    elif mood_text:
        blend = score_free_text_mood(mood_text)
    else:
        blend = {}

    if not blend:
        # No mood signal — neutral score, doesn't penalize or boost anything.
        return pd.Series(0.0, index=catalog.index)

    combined_weights: dict[str, float] = {}
    for mood_key, mood_weight in blend.items():
        for tag, w in MOOD_PROFILES[mood_key].items():
            combined_weights[tag] = combined_weights.get(tag, 0.0) + w * mood_weight

    def score_row(row):
        tags = set(row["genres"]) | set(row["keywords"])
        return sum(w for tag, w in combined_weights.items() if tag in tags)

    raw = catalog.apply(score_row, axis=1)
    max_val = raw.max()
    return raw / max_val if max_val > 0 else raw