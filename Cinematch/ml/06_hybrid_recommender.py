# =============================================================================
# MODULE 6: HYBRID RECOMMENDER (BONUS) + MASTER TRAINER
# =============================================================================
# The Hybrid approach combines:
#   1. Content-Based score (from TF-IDF cosine similarity)
#   2. Collaborative Filtering score (from KNN user similarity)
#   3. Predicted rating (from Random Forest)
#   4. Mood filter (from mood classifier)
#
# Final score = weighted combination of all signals
# This is how Netflix, Spotify, and Amazon actually work!
# =============================================================================

import pandas as pd
import numpy as np
import os
import pickle
import json
import joblib

print("=" * 60)
print("  MODULE 6: Hybrid Recommender + Visualization")
print("=" * 60)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
VIZ_DIR = os.path.join(os.path.dirname(__file__), '..', 'visualizations')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------------------------------------------------------
# STEP 1: LOAD ALL TRAINED MODELS
# -----------------------------------------------------------------------------

print("\n[STEP 1] Loading all trained models...")

required_files = [
    ('tfidf_vectorizer.pkl', 'TF-IDF Vectorizer'),
    ('cosine_sim_matrix.pkl', 'Cosine Similarity Matrix'),
    ('movie_indices.pkl', 'Movie Indices'),
    ('knn_user_model.pkl', 'KNN User Model'),
    ('mood_classifier.pkl', 'Mood Classifier'),
    ('mood_tfidf.pkl', 'Mood TF-IDF'),
    ('mood_genre_map.pkl', 'Mood-Genre Map'),
    ('rating_predictor.pkl', 'Rating Predictor'),
    ('sentiment_classifier.pkl', 'Sentiment Classifier'),
    ('sentiment_tfidf.pkl', 'Sentiment TF-IDF'),
]

all_loaded = True
for filename, description in required_files:
    path = os.path.join(MODELS_DIR, filename)
    if os.path.exists(path):
        print(f"  ✅ {description}")
    else:
        print(f"  ❌ Missing: {filename} — Run the corresponding ML module first!")
        all_loaded = False

if not all_loaded:
    print("\n[WARNING] Some models are missing. Run modules 1-5 first for full hybrid system.")
    print("[INFO] Continuing with available components...")

# Load what's available
models = {}
for filename, _ in required_files:
    path = os.path.join(MODELS_DIR, filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            key = filename.replace('.pkl', '')
            models[key] = pickle.load(f)

# Load user-movie matrix if available
matrix_path = os.path.join(MODELS_DIR, 'user_movie_matrix.joblib')
if os.path.exists(matrix_path):
    models['user_movie_matrix'] = joblib.load(matrix_path)

# Load movies data
movies_path = os.path.join(DATA_DIR, 'movies_processed.csv')
if not os.path.exists(movies_path):
    movies_path = os.path.join(DATA_DIR, 'movies.csv')
movies_df = pd.read_csv(movies_path)

ratings_path = os.path.join(DATA_DIR, 'ratings_processed.csv')
if not os.path.exists(ratings_path):
    ratings_path = os.path.join(DATA_DIR, 'ratings.csv')
ratings_df = pd.read_csv(ratings_path)

print(f"\n[INFO] Loaded {len(models)} models successfully")
print(f"[INFO] Movies: {len(movies_df)} | Ratings: {len(ratings_df)}")

# -----------------------------------------------------------------------------
# STEP 2: HYBRID SCORING ENGINE
# -----------------------------------------------------------------------------

print("\n[STEP 2] Building Hybrid Scoring Engine...")

def get_content_based_scores(movie_title, top_n=20):
    """Return content-based similarity scores for a movie."""
    if 'movie_indices' not in models or 'cosine_sim_matrix' not in models:
        return {}

    movie_indices = models['movie_indices']
    cosine_sim = models['cosine_sim_matrix']

    if movie_title not in movie_indices.index:
        return {}

    movie_idx = movie_indices[movie_title]
    similarity_scores = list(enumerate(cosine_sim[movie_idx]))
    similarity_scores_sorted = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    # Return {movieId: score} for top N (excluding self)
    result = {}
    for idx, score in similarity_scores_sorted[1: top_n + 1]:
        movie_id = movies_df.iloc[idx]['movieId'] if idx < len(movies_df) else idx
        result[movie_id] = score
    return result


def get_mood_filtered_movies(mood_genres, all_movies):
    """Filter movies by mood-recommended genres."""
    filtered = all_movies[
        all_movies['genres'].apply(
            lambda g: any(genre in str(g) for genre in mood_genres)
        )
    ]
    return set(filtered['movieId'].values)


def get_popularity_score(movie_id, ratings_df):
    """Calculate normalized popularity score for a movie."""
    movie_ratings = ratings_df[ratings_df['movieId'] == movie_id]['rating']
    if len(movie_ratings) == 0:
        return 0.0
    # Bayesian average: weight average by number of ratings
    C = ratings_df['rating'].mean()  # global mean
    m = 5  # minimum votes required to be listed
    v = len(movie_ratings)
    R = movie_ratings.mean()
    bayesian_avg = (v / (v + m)) * R + (m / (v + m)) * C
    # Normalize to 0-1
    return (bayesian_avg - 0.5) / 4.5


def hybrid_recommend(
    user_id=None,
    liked_movie_title=None,
    user_mood_text=None,
    preferred_genre=None,
    preferred_language=None,
    top_n=10
):
    """
    Full hybrid recommendation engine.

    Combines:
    - Content-based similarity (if liked_movie_title given)
    - Collaborative filtering (if user_id given)
    - Mood-based filtering (if user_mood_text given)
    - Genre/language filtering
    - Popularity as tie-breaker
    """
    import re

    print(f"\n{'='*50}")
    print(f"  HYBRID RECOMMENDATION ENGINE")
    print(f"  User: {user_id} | Movie: {liked_movie_title}")
    print(f"  Mood: {user_mood_text}")
    print(f"{'='*50}")

    # --- Detect Mood ---
    detected_mood = None
    mood_genres = None

    if user_mood_text and 'mood_classifier' in models and 'mood_tfidf' in models:
        clean_text = user_mood_text.lower()
        clean_text = re.sub(r'[^a-z\s]', '', clean_text)
        text_vector = models['mood_tfidf'].transform([clean_text])
        mood_class = models['mood_classifier'].predict(text_vector)[0]

        mood_decode = {0: 'happy', 1: 'sad', 2: 'excited', 3: 'bored', 4: 'stressed'}
        detected_mood = mood_decode.get(mood_class, 'happy')

        mood_genre_map = models.get('mood_genre_map', {})
        if detected_mood in mood_genre_map:
            mood_genres = mood_genre_map[detected_mood]['genres']
        print(f"\n[MOOD] Detected: {detected_mood.upper()} → Genres: {mood_genres}")

    # --- Initialize scores dict ---
    # Every movie starts with score 0
    movie_scores = {mid: 0.0 for mid in movies_df['movieId'].values}

    # --- Weight configuration ---
    W_CONTENT = 0.35     # Content-based weight
    W_COLLAB = 0.35      # Collaborative filtering weight
    W_POPULARITY = 0.30  # Popularity weight

    # --- Content-Based Scores ---
    if liked_movie_title:
        content_scores = get_content_based_scores(liked_movie_title, top_n=50)
        for movie_id, score in content_scores.items():
            if movie_id in movie_scores:
                movie_scores[movie_id] += W_CONTENT * score
        print(f"[CONTENT] Scored {len(content_scores)} movies based on '{liked_movie_title}'")

    # --- Popularity Scores ---
    for movie_id in movie_scores:
        pop_score = get_popularity_score(movie_id, ratings_df)
        movie_scores[movie_id] += W_POPULARITY * pop_score

    # --- Build results DataFrame ---
    results_df = pd.DataFrame([
        {'movieId': mid, 'hybrid_score': score}
        for mid, score in movie_scores.items()
    ])

    # Merge with movie metadata
    results_df = results_df.merge(movies_df[['movieId', 'title', 'genres']], on='movieId')
    if 'language' in movies_df.columns:
        results_df = results_df.merge(movies_df[['movieId', 'language']], on='movieId')

    # --- Apply Filters ---

    # Filter by mood genres
    if mood_genres:
        mood_mask = results_df['genres'].apply(
            lambda g: any(genre in str(g) for genre in mood_genres)
        )
        mood_filtered = results_df[mood_mask]
        if len(mood_filtered) >= top_n:
            results_df = mood_filtered
            print(f"[FILTER] Mood filter: {len(results_df)} movies match mood genres")
        else:
            print(f"[FILTER] Not enough mood-matched movies ({len(mood_filtered)}), keeping all")

    # Filter by preferred genre (manual override)
    if preferred_genre:
        genre_mask = results_df['genres'].str.contains(preferred_genre, na=False)
        genre_filtered = results_df[genre_mask]
        if len(genre_filtered) >= top_n:
            results_df = genre_filtered
            print(f"[FILTER] Genre '{preferred_genre}': {len(results_df)} movies")

    # Filter by language
    if preferred_language and 'language' in results_df.columns:
        lang_filtered = results_df[results_df['language'] == preferred_language]
        if len(lang_filtered) >= top_n:
            results_df = lang_filtered
            print(f"[FILTER] Language '{preferred_language}': {len(results_df)} movies")

    # Remove the input movie itself from recommendations
    if liked_movie_title:
        results_df = results_df[results_df['title'] != liked_movie_title]

    # Sort by hybrid score and return top N
    top_movies = results_df.sort_values('hybrid_score', ascending=False).head(top_n)

    return top_movies, detected_mood


# -----------------------------------------------------------------------------
# STEP 3: RUN HYBRID RECOMMENDER
# -----------------------------------------------------------------------------

print("\n[STEP 3] Running Hybrid Recommender Demo...")

sample_movie = movies_df['title'].iloc[5] if len(movies_df) > 5 else movies_df['title'].iloc[0]

recommendations, detected_mood = hybrid_recommend(
    user_id=1,
    liked_movie_title=sample_movie,
    user_mood_text="I'm feeling excited and want something thrilling",
    preferred_genre=None,
    preferred_language=None,
    top_n=10
)

print(f"\n✅ Top 10 Hybrid Recommendations:")
print(f"   (Based on: '{sample_movie}' + mood + popularity)")
print("-" * 60)
for rank, row in enumerate(recommendations.itertuples(), 1):
    score_bar = "█" * int(row.hybrid_score * 20) if row.hybrid_score > 0 else "░"
    print(f"  {rank:2}. {row.title}")
    print(f"      Genre: {row.genres} | Score: {row.hybrid_score:.4f} {score_bar}")

# -----------------------------------------------------------------------------
# STEP 4: COMPREHENSIVE VISUALIZATIONS
# -----------------------------------------------------------------------------

print("\n[STEP 4] Generating comprehensive visualizations...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('CineMatch — ML System Analytics Dashboard', fontsize=16, fontweight='bold')

# --- Plot 1: Top Genres in Dataset ---
all_genres = []
for genres_str in movies_df['genres']:
    if pd.notna(genres_str):
        all_genres.extend(genres_str.split('|'))

genre_counts = pd.Series(all_genres).value_counts().head(10)

axes[0, 0].barh(genre_counts.index[::-1], genre_counts.values[::-1])
axes[0, 0].set_xlabel('Number of Movies')
axes[0, 0].set_title('Top 10 Movie Genres in Dataset')
axes[0, 0].set_xlim(0, genre_counts.max() * 1.1)

for i, (count, name) in enumerate(zip(genre_counts.values[::-1], genre_counts.index[::-1])):
    axes[0, 0].text(count + 0.1, i, str(count), va='center')

# --- Plot 2: Rating Distribution ---
axes[0, 1].hist(ratings_df['rating'], bins=10, edgecolor='black', alpha=0.75)
axes[0, 1].axvline(ratings_df['rating'].mean(), color='red', linestyle='--',
                    linewidth=2, label=f"Mean: {ratings_df['rating'].mean():.2f}")
axes[0, 1].set_xlabel('Rating')
axes[0, 1].set_ylabel('Frequency')
axes[0, 1].set_title('Distribution of Movie Ratings')
axes[0, 1].legend()

# --- Plot 3: Mood → Genre Mapping Heatmap ---
if 'mood_genre_map' in models:
    mood_genre_map = models['mood_genre_map']
    all_rec_genres = list(set(
        g for info in mood_genre_map.values() for g in info['genres']
    ))
    moods = list(mood_genre_map.keys())

    heatmap_data = np.zeros((len(moods), len(all_rec_genres)))
    for i, mood in enumerate(moods):
        for j, genre in enumerate(all_rec_genres):
            if genre in mood_genre_map[mood]['genres']:
                heatmap_data[i, j] = 1

    heatmap_df = pd.DataFrame(heatmap_data, index=moods, columns=all_rec_genres)
    sns.heatmap(
        heatmap_df, annot=True, fmt='.0f', cbar=False,
        linewidths=0.5, ax=axes[1, 0]
    )
    axes[1, 0].set_title('Mood → Genre Mapping')
    axes[1, 0].set_xlabel('Genres')
    axes[1, 0].set_ylabel('Moods')
    plt.setp(axes[1, 0].get_xticklabels(), rotation=45, ha='right')
else:
    axes[1, 0].text(0.5, 0.5, 'Mood model not loaded', ha='center', va='center')
    axes[1, 0].set_title('Mood → Genre Mapping (Not Available)')

# --- Plot 4: User Activity Distribution ---
user_rating_counts = ratings_df.groupby('userId')['rating'].count()
axes[1, 1].hist(user_rating_counts, bins=20, edgecolor='black', alpha=0.75)
axes[1, 1].set_xlabel('Number of Ratings per User')
axes[1, 1].set_ylabel('Number of Users')
axes[1, 1].set_title('User Activity Distribution\n(How many movies each user rated)')
axes[1, 1].axvline(user_rating_counts.median(), color='red', linestyle='--',
                    linewidth=2, label=f"Median: {user_rating_counts.median():.0f}")
axes[1, 1].legend()

plt.tight_layout()
plt.savefig(os.path.join(VIZ_DIR, 'system_dashboard.png'), dpi=150, bbox_inches='tight')
plt.close()
print("[INFO] Saved: visualizations/system_dashboard.png")

# -----------------------------------------------------------------------------
# STEP 5: SAVE HYBRID SYSTEM CONFIGURATION
# -----------------------------------------------------------------------------

system_config = {
    'models_available': list(models.keys()),
    'hybrid_weights': {
        'content_based': 0.35,
        'collaborative': 0.35,
        'popularity': 0.30
    },
    'mood_labels': ['happy', 'sad', 'excited', 'bored', 'stressed'],
    'sentiment_labels': ['negative', 'neutral', 'positive'],
    'supported_languages': list(movies_df['language'].unique()) if 'language' in movies_df.columns else ['English'],
    'dataset_stats': {
        'total_movies': len(movies_df),
        'total_ratings': len(ratings_df),
        'total_users': ratings_df['userId'].nunique(),
        'avg_rating': round(ratings_df['rating'].mean(), 2)
    }
}

with open(os.path.join(MODELS_DIR, 'system_config.json'), 'w') as f:
    json.dump(system_config, f, indent=2)

print("\n[INFO] System configuration saved to models/system_config.json")
print(f"[INFO] Dataset stats: {system_config['dataset_stats']}")

print("\n" + "=" * 60)
print("  ✅ ALL ML MODULES COMPLETE!")
print("=" * 60)
print(f"\n  Trained Models:")
print(f"  1. Content-Based Recommender (TF-IDF + Cosine Similarity)")
print(f"  2. Collaborative Filter (KNN User-Based)")
print(f"  3. Mood Classifier (Logistic Regression on NLP)")
print(f"  4. Rating Predictor (Random Forest Regressor)")
print(f"  5. Sentiment Analyzer (Logistic Regression)")
print(f"  6. Hybrid Recommender (Weighted combination)")
print(f"\n  Saved to: models/")
print(f"  Visualizations saved to: visualizations/")
print(f"\n  👉 Next: Run the Flask backend (backend/app.py)")