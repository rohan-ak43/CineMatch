# =============================================================================
# MODULE 1: CONTENT-BASED RECOMMENDATION SYSTEM
# =============================================================================
# How it works:
#   - Each movie has a "description" (genre + overview + tags combined)
#   - We convert all descriptions into numbers using TF-IDF
#   - TF-IDF gives higher weight to RARE but important words
#   - Then we measure how "similar" two movies are using cosine similarity
#   - If you liked Movie A, we find movies whose descriptions are closest to A
# =============================================================================

import pandas as pd
import numpy as np
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

print("=" * 60)
print("  MODULE 1: Content-Based Recommendation System")
print("=" * 60)

# -----------------------------------------------------------------------------
# STEP 1: LOAD THE DATASET
# -----------------------------------------------------------------------------
# We use the MovieLens small dataset. If you don't have it, we generate
# a sample dataset for demonstration purposes.
# -----------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

movies_path = os.path.join(DATA_DIR, 'movies.csv')

if os.path.exists(movies_path):
    print("\n[INFO] Loading movies.csv from data folder...")
    movies_df = pd.read_csv(movies_path)
else:
    print("\n[INFO] movies.csv not found. Creating sample dataset...")
    # Sample data mimicking MovieLens format
    sample_data = {
        'movieId': range(1, 31),
        'title': [
            'Toy Story (1995)', 'Jumanji (1995)', 'Grumpier Old Men (1995)',
            'Waiting to Exhale (1995)', 'Father of the Bride Part II (1995)',
            'Heat (1995)', 'Sabrina (1995)', 'Tom and Huck (1995)',
            'Sudden Death (1995)', 'GoldenEye (1995)',
            'American President, The (1995)', 'Dracula: Dead and Loving It (1995)',
            'Balto (1995)', 'Nixon (1995)', 'Cutthroat Island (1995)',
            'Casino (1995)', 'Sense and Sensibility (1995)', 'Four Rooms (1995)',
            'Ace Ventura: When Nature Calls (1995)', 'Money Train (1995)',
            'Get Shorty (1995)', 'Copycat (1995)', 'Assassins (1995)',
            'Powder (1995)', 'Leaving Las Vegas (1995)', 'Othello (1995)',
            'Now and Then (1995)', 'Persuasion (1995)', 'City of Lost Children (1995)',
            'Shanghai Triad (1995)'
        ],
        'genres': [
            'Adventure|Animation|Children|Comedy|Fantasy',
            'Adventure|Children|Fantasy',
            'Comedy|Romance',
            'Comedy|Drama|Romance',
            'Comedy',
            'Action|Crime|Thriller',
            'Comedy|Romance',
            'Adventure|Children',
            'Action',
            'Action|Adventure|Thriller',
            'Comedy|Drama|Romance',
            'Comedy|Horror',
            'Adventure|Animation|Children',
            'Drama',
            'Action|Adventure|Romance',
            'Crime|Drama',
            'Drama|Romance',
            'Comedy|Mystery',
            'Comedy',
            'Action|Comedy|Crime|Drama|Thriller',
            'Comedy|Crime|Thriller',
            'Crime|Drama|Thriller',
            'Action|Thriller',
            'Drama|Sci-Fi',
            'Drama|Romance',
            'Drama|Romance',
            'Children|Comedy|Drama',
            'Drama|Romance',
            'Adventure|Drama|Fantasy|Mystery|Sci-Fi',
            'Crime|Drama'
        ]
    }
    movies_df = pd.DataFrame(sample_data)
    os.makedirs(DATA_DIR, exist_ok=True)
    movies_df.to_csv(movies_path, index=False)
    print(f"[INFO] Sample dataset saved to {movies_path}")

print(f"\n[INFO] Dataset loaded: {len(movies_df)} movies")
print(movies_df.head())

# -----------------------------------------------------------------------------
# STEP 2: PREPROCESS — Create a "soup" of text features for each movie
# -----------------------------------------------------------------------------
# We combine genres and title into one text blob per movie.
# This becomes the "fingerprint" of each movie.
# -----------------------------------------------------------------------------

print("\n[STEP 2] Creating text features (genre soup)...")

# Replace pipe '|' with space so each genre becomes a separate word
movies_df['genre_clean'] = movies_df['genres'].str.replace('|', ' ', regex=False)

# Extract the movie title without year for cleaner text
movies_df['title_clean'] = movies_df['title'].str.replace(r'\s*\(\d{4}\)', '', regex=True)

# Add overview column if it doesn't exist (MovieLens basic doesn't have it)
if 'overview' not in movies_df.columns:
    movies_df['overview'] = ''

# Combine all text: genre + title + overview
# This is the "content" we use to find similar movies
movies_df['content_soup'] = (
    movies_df['genre_clean'] + ' ' +
    movies_df['title_clean'] + ' ' +
    movies_df['overview'].fillna('')
)

print("[INFO] Sample content soup for movie 1:")
print(movies_df['content_soup'].iloc[0])

# -----------------------------------------------------------------------------
# STEP 3: TF-IDF VECTORIZATION
# -----------------------------------------------------------------------------
# TF-IDF = Term Frequency × Inverse Document Frequency
#
# - Term Frequency: How often a word appears in THIS movie's description
# - Inverse Document Frequency: How rare/unique that word is across ALL movies
#
# Result: Words like "Action" that appear in many movies get lower scores.
#         Rare words that describe a specific movie get higher scores.
# -----------------------------------------------------------------------------

print("\n[STEP 3] Applying TF-IDF Vectorization...")

# Create the TF-IDF vectorizer
# stop_words='english' removes common words like 'the', 'is', 'and'
# max_features limits vocabulary size to avoid memory issues
tfidf = TfidfVectorizer(
    stop_words='english',   # Remove common English words
    max_features=5000,      # Keep top 5000 most important words
    ngram_range=(1, 2)      # Use single words AND 2-word phrases
)

# Fit and transform: learn vocabulary from all movies, then convert to numbers
# Result is a matrix: rows = movies, columns = words, values = TF-IDF score
tfidf_matrix = tfidf.fit_transform(movies_df['content_soup'])

print(f"[INFO] TF-IDF Matrix shape: {tfidf_matrix.shape}")
print(f"       → {tfidf_matrix.shape[0]} movies × {tfidf_matrix.shape[1]} words")

# -----------------------------------------------------------------------------
# STEP 4: COMPUTE COSINE SIMILARITY
# -----------------------------------------------------------------------------
# Cosine similarity measures the ANGLE between two movie vectors.
# - Score = 1.0 → Movies are IDENTICAL
# - Score = 0.0 → Movies have NOTHING in common
#
# We compute similarity between ALL pairs of movies at once.
# Result: a matrix[i][j] = similarity between movie i and movie j
# -----------------------------------------------------------------------------

print("\n[STEP 4] Computing Cosine Similarity Matrix...")

cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

print(f"[INFO] Similarity Matrix shape: {cosine_sim.shape}")
print(f"       → This is a {cosine_sim.shape[0]}×{cosine_sim.shape[1]} matrix")
print(f"       → Each cell = similarity score between two movies (0 to 1)")

# Show sample: similarity of movie 0 with all others
print(f"\n[INFO] Sample: Similarity of '{movies_df['title'].iloc[0]}' with first 5 movies:")
for i in range(5):
    print(f"  vs '{movies_df['title'].iloc[i]}': {cosine_sim[0][i]:.4f}")

# -----------------------------------------------------------------------------
# STEP 5: BUILD MOVIE INDEX (Title → Row Number)
# -----------------------------------------------------------------------------
# We need a fast lookup: given a movie title, find its row number in the matrix
# -----------------------------------------------------------------------------

print("\n[STEP 5] Building movie title index...")

# Create a mapping: movie title → index in the dataframe
movie_indices = pd.Series(movies_df.index, index=movies_df['title']).drop_duplicates()

print(f"[INFO] Index built for {len(movie_indices)} movies")

# -----------------------------------------------------------------------------
# STEP 6: RECOMMENDATION FUNCTION (written as inline steps, no functions)
# -----------------------------------------------------------------------------
# Given a movie title, we:
#   1. Find its index
#   2. Get its row from the similarity matrix
#   3. Sort by similarity score (descending)
#   4. Return top N most similar movies
# -----------------------------------------------------------------------------

print("\n[STEP 6] Running Content-Based Recommendation...")

# --- Choose the movie to recommend for ---
INPUT_MOVIE = movies_df['title'].iloc[0]  # First movie in dataset
TOP_N = 5  # How many recommendations to return

print(f"\n[INFO] Getting recommendations for: '{INPUT_MOVIE}'")

# Get the index of the input movie in our dataframe
movie_idx = movie_indices.get(INPUT_MOVIE, None)

if movie_idx is None:
    print(f"[ERROR] Movie '{INPUT_MOVIE}' not found in database!")
else:
    # Get the similarity scores of this movie with ALL other movies
    # This is one row from the cosine_sim matrix
    similarity_scores = list(enumerate(cosine_sim[movie_idx]))

    # Sort movies by similarity score in DESCENDING order
    # 'key=lambda x: x[1]' means "sort by the score (second element)"
    similarity_scores_sorted = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    # Skip the first result (index 0) because that's the INPUT MOVIE ITSELF
    # (A movie is 100% similar to itself — not useful)
    top_similar = similarity_scores_sorted[1: TOP_N + 1]

    # Extract movie indices from the result
    top_movie_indices = [idx for idx, score in top_similar]

    # Get the movie titles using those indices
    recommended_movies = movies_df['title'].iloc[top_movie_indices].tolist()
    recommended_scores = [round(score, 4) for idx, score in top_similar]

    print(f"\n✅ Top {TOP_N} Content-Based Recommendations:")
    print("-" * 40)
    for rank, (title, score) in enumerate(zip(recommended_movies, recommended_scores), 1):
        genre = movies_df[movies_df['title'] == title]['genres'].values[0]
        print(f"  {rank}. {title}")
        print(f"     Genre: {genre}")
        print(f"     Similarity Score: {score}")

# -----------------------------------------------------------------------------
# STEP 7: SAVE MODELS FOR FLASK BACKEND USE
# -----------------------------------------------------------------------------

print("\n[STEP 7] Saving models to disk...")

# Save the TF-IDF vectorizer
with open(os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl'), 'wb') as f:
    pickle.dump(tfidf, f)

# Save the cosine similarity matrix
with open(os.path.join(MODELS_DIR, 'cosine_sim_matrix.pkl'), 'wb') as f:
    pickle.dump(cosine_sim, f)

# Save the movies dataframe (cleaned)
movies_df.to_csv(os.path.join(DATA_DIR, 'movies_processed.csv'), index=False)

# Save movie index mapping
with open(os.path.join(MODELS_DIR, 'movie_indices.pkl'), 'wb') as f:
    pickle.dump(movie_indices, f)

print("[INFO] Saved:")
print(f"  → models/tfidf_vectorizer.pkl")
print(f"  → models/cosine_sim_matrix.pkl")
print(f"  → models/movie_indices.pkl")
print(f"  → data/movies_processed.csv")

print("\n✅ Module 1 Complete: Content-Based Recommender trained and saved!")

# -----------------------------------------------------------------------------
# EVALUATION: Precision@K (manual check)
# -----------------------------------------------------------------------------
print("\n[EVALUATION] Precision@K Check:")
print("  Precision@K measures: Out of K recommendations, how many are relevant?")
print("  For content-based: relevance = same primary genre as input movie")

input_genre = movies_df[movies_df['title'] == INPUT_MOVIE]['genres'].values[0].split('|')[0]
relevant_count = 0

for title in recommended_movies:
    rec_genres = movies_df[movies_df['title'] == title]['genres'].values[0]
    if input_genre in rec_genres:
        relevant_count += 1

precision_at_k = relevant_count / TOP_N
print(f"  Input movie primary genre: {input_genre}")
print(f"  Relevant recommendations: {relevant_count}/{TOP_N}")
print(f"  Precision@{TOP_N} = {precision_at_k:.2f}")