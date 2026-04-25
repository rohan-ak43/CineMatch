# =============================================================================
# MODULE 2: COLLABORATIVE FILTERING (KNN-Based)
# =============================================================================
# How it works:
#   - We build a User × Movie matrix where each cell = rating given
#   - To recommend for User A, we find K users most similar to User A
#     (they liked/disliked the same movies in the past)
#   - We then recommend movies those similar users loved, but User A hasn't seen
#
# This is "User-Based Collaborative Filtering"
# The power: It finds unexpected gems you wouldn't know to search for!
# =============================================================================

import pandas as pd
import numpy as np
import os
import pickle
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

print("=" * 60)
print("  MODULE 2: Collaborative Filtering (KNN)")
print("=" * 60)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# STEP 1: LOAD RATINGS DATA
# -----------------------------------------------------------------------------

ratings_path = os.path.join(DATA_DIR, 'ratings.csv')

if os.path.exists(ratings_path):
    print("\n[INFO] Loading ratings.csv...")
    ratings_df = pd.read_csv(ratings_path)
else:
    print("\n[INFO] ratings.csv not found. Creating sample ratings data...")
    # Simulate 50 users rating 30 movies (sparse — not all users rate all movies)
    np.random.seed(42)
    num_users = 50
    num_movies = 30
    num_ratings = 400  # Only 400 out of 1500 possible ratings exist

    user_ids = np.random.randint(1, num_users + 1, num_ratings)
    movie_ids = np.random.randint(1, num_movies + 1, num_ratings)
    ratings_vals = np.random.choice([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0], num_ratings)

    ratings_df = pd.DataFrame({
        'userId': user_ids,
        'movieId': movie_ids,
        'rating': ratings_vals,
        'timestamp': np.random.randint(1000000000, 1600000000, num_ratings)
    })
    # Remove duplicate user-movie pairs (keep last rating)
    ratings_df = ratings_df.drop_duplicates(subset=['userId', 'movieId'], keep='last')
    ratings_df.to_csv(ratings_path, index=False)
    print(f"[INFO] Sample ratings saved to {ratings_path}")

print(f"\n[INFO] Ratings loaded: {len(ratings_df)} ratings")
print(f"       Unique users: {ratings_df['userId'].nunique()}")
print(f"       Unique movies: {ratings_df['movieId'].nunique()}")
print(ratings_df.head())

# -----------------------------------------------------------------------------
# STEP 2: NORMALIZE RATINGS (Center each user's ratings)
# -----------------------------------------------------------------------------
# Different users have different scales. User A might rate 5 for "good" movies,
# User B might only ever rate up to 3. Normalizing removes this bias.
# We subtract each user's MEAN rating from their ratings.
# -----------------------------------------------------------------------------

print("\n[STEP 2] Normalizing ratings (subtracting user mean)...")

# Calculate each user's average rating
user_means = ratings_df.groupby('userId')['rating'].mean()

# Merge average back into ratings
ratings_df = ratings_df.merge(
    user_means.rename('user_mean'), on='userId'
)

# Normalized rating = actual rating - user's average rating
ratings_df['rating_normalized'] = ratings_df['rating'] - ratings_df['user_mean']

print("[INFO] Sample normalized ratings:")
print(ratings_df[['userId', 'movieId', 'rating', 'user_mean', 'rating_normalized']].head(8))

# -----------------------------------------------------------------------------
# STEP 3: CREATE USER-MOVIE MATRIX (Pivot Table)
# -----------------------------------------------------------------------------
# Rows = Users, Columns = Movies, Values = Normalized Ratings
# Missing = 0 (user hasn't rated that movie)
#
# Example:
#          Movie1  Movie2  Movie3
# User 1:   0.5     -1.0    NaN → 0
# User 2:   NaN     0.5     1.0
# User 3:   -0.5    NaN     0.5
# -----------------------------------------------------------------------------

print("\n[STEP 3] Building User-Movie Matrix...")

user_movie_matrix = ratings_df.pivot_table(
    index='userId',       # Rows = users
    columns='movieId',    # Columns = movies
    values='rating_normalized',  # Cell values = normalized ratings
    fill_value=0          # Missing ratings filled with 0
)

print(f"[INFO] User-Movie Matrix shape: {user_movie_matrix.shape}")
print(f"       → {user_movie_matrix.shape[0]} users × {user_movie_matrix.shape[1]} movies")

sparsity = (user_movie_matrix == 0).sum().sum() / user_movie_matrix.size * 100
print(f"[INFO] Matrix sparsity: {sparsity:.1f}% (most cells are 0 — normal!)")

# -----------------------------------------------------------------------------
# STEP 4: CONVERT TO SPARSE MATRIX (Memory Optimization)
# -----------------------------------------------------------------------------
# Real datasets have millions of users and movies.
# Storing all those zeros wastes memory.
# CSR (Compressed Sparse Row) matrix only stores NON-ZERO values.
# This makes it 10-100x more memory efficient!
# -----------------------------------------------------------------------------

print("\n[STEP 4] Converting to Sparse Matrix for efficiency...")

user_movie_sparse = csr_matrix(user_movie_matrix.values)

print(f"[INFO] Sparse matrix created: {user_movie_sparse.shape}")
print(f"       Non-zero elements: {user_movie_sparse.nnz}")

# -----------------------------------------------------------------------------
# STEP 5: TRAIN KNN MODEL (User Similarity)
# -----------------------------------------------------------------------------
# KNN = K-Nearest Neighbors
# We use "cosine" metric — same as content-based but now on USER RATINGS
# instead of movie descriptions.
#
# metric='cosine': Two users are similar if they rate movies PROPORTIONALLY alike
# algorithm='brute': Check all users (fine for small datasets)
# -----------------------------------------------------------------------------

print("\n[STEP 5] Training KNN Model for User Similarity...")

K_NEIGHBORS = min(10, user_movie_matrix.shape[0] - 1)  # Can't have more neighbors than users

knn_model = NearestNeighbors(
    n_neighbors=K_NEIGHBORS + 1,  # +1 because the user itself is returned as neighbor 0
    metric='cosine',
    algorithm='brute',            # Works well for sparse matrices
    n_jobs=-1                     # Use all CPU cores
)

# Fit the model to the USER-MOVIE matrix
# KNN doesn't "learn" parameters — it just memorizes the data
knn_model.fit(user_movie_sparse)

print(f"[INFO] KNN model fitted with K={K_NEIGHBORS} neighbors")

# -----------------------------------------------------------------------------
# STEP 6: FIND SIMILAR USERS AND RECOMMEND MOVIES
# -----------------------------------------------------------------------------

print("\n[STEP 6] Running Collaborative Filtering Recommendations...")

# Choose a target user to recommend for
TARGET_USER_ID = user_movie_matrix.index[0]  # First user in dataset
TOP_N = 5

print(f"\n[INFO] Generating recommendations for User ID: {TARGET_USER_ID}")

# Get the target user's row from the matrix as a 2D array (required by sklearn)
target_user_row = user_movie_matrix.loc[TARGET_USER_ID].values.reshape(1, -1)

# Find K most similar users
# distances: how far they are (0=identical, 2=completely opposite for cosine)
# indices: their row positions in our matrix
distances, indices = knn_model.kneighbors(target_user_row, n_neighbors=K_NEIGHBORS + 1)

# Remove the first result (distance=0, it's the user themselves)
similar_user_distances = distances[0][1:]
similar_user_indices = indices[0][1:]

# Get the actual user IDs of similar users
similar_user_ids = user_movie_matrix.index[similar_user_indices]

print(f"\n[INFO] Top {K_NEIGHBORS} similar users to User {TARGET_USER_ID}:")
for i, (uid, dist) in enumerate(zip(similar_user_ids, similar_user_distances), 1):
    similarity = 1 - dist  # Convert distance to similarity score
    print(f"  {i}. User {uid} — Similarity: {similarity:.4f}")

# Find movies the TARGET USER has NOT rated
target_user_rated_movies = set(
    ratings_df[ratings_df['userId'] == TARGET_USER_ID]['movieId'].values
)

# Collect ratings from all similar users
similar_users_ratings = ratings_df[ratings_df['userId'].isin(similar_user_ids)]

# Filter to movies the target user hasn't seen
unseen_movies = similar_users_ratings[
    ~similar_users_ratings['movieId'].isin(target_user_rated_movies)
]

# Calculate weighted average rating for each unseen movie
# Weight = similarity of the user who rated it
# Build a similarity lookup dictionary
similarity_lookup = {uid: 1 - dist for uid, dist in zip(similar_user_ids, similar_user_distances)}
unseen_movies = unseen_movies.copy()
unseen_movies['weight'] = unseen_movies['userId'].map(similarity_lookup)

# Weighted score = sum(rating × similarity) / sum(similarities)
movie_scores = (
    unseen_movies
    .groupby('movieId')
    .apply(lambda x: (x['rating'] * x['weight']).sum() / x['weight'].sum())
    .reset_index()
)
movie_scores.columns = ['movieId', 'predicted_rating']
movie_scores = movie_scores.sort_values('predicted_rating', ascending=False)

# Get top N recommendations
top_recommendations = movie_scores.head(TOP_N)

print(f"\n✅ Top {TOP_N} Collaborative Filtering Recommendations for User {TARGET_USER_ID}:")
print("-" * 50)

# Load movies to show titles
movies_processed_path = os.path.join(DATA_DIR, 'movies_processed.csv')
if os.path.exists(movies_processed_path):
    movies_df = pd.read_csv(movies_processed_path)
    for rank, row in enumerate(top_recommendations.itertuples(), 1):
        movie_title_row = movies_df[movies_df['movieId'] == row.movieId]
        title = movie_title_row['title'].values[0] if len(movie_title_row) > 0 else f"Movie {row.movieId}"
        print(f"  {rank}. {title}")
        print(f"     Predicted Rating: {row.predicted_rating:.2f} / 5.0")
else:
    for rank, row in enumerate(top_recommendations.itertuples(), 1):
        print(f"  {rank}. Movie ID {row.movieId} — Predicted Rating: {row.predicted_rating:.2f}")

# -----------------------------------------------------------------------------
# STEP 7: ITEM-BASED COLLABORATIVE FILTERING (Bonus)
# -----------------------------------------------------------------------------
# Instead of finding similar USERS, find similar MOVIES based on who rated them
# We simply transpose the matrix: now rows=Movies, columns=Users
# -----------------------------------------------------------------------------

print("\n[STEP 7] Item-Based Collaborative Filtering (Bonus)...")

# Transpose matrix: Movies become rows
movie_user_matrix = user_movie_matrix.T
movie_user_sparse = csr_matrix(movie_user_matrix.values)

knn_item = NearestNeighbors(
    n_neighbors=min(6, movie_user_matrix.shape[0]),
    metric='cosine',
    algorithm='brute'
)
knn_item.fit(movie_user_sparse)

# Recommend movies similar to a specific movie
SAMPLE_MOVIE_IDX = 0
sample_movie_row = movie_user_matrix.iloc[SAMPLE_MOVIE_IDX].values.reshape(1, -1)
distances_item, indices_item = knn_item.kneighbors(sample_movie_row)

sample_movie_id = movie_user_matrix.index[SAMPLE_MOVIE_IDX]
print(f"\n[INFO] Movies similar to Movie ID {sample_movie_id} (item-based):")
for i, (idx, dist) in enumerate(zip(indices_item[0][1:], distances_item[0][1:]), 1):
    sim_movie_id = movie_user_matrix.index[idx]
    print(f"  {i}. Movie ID {sim_movie_id} — Similarity: {1-dist:.4f}")

# -----------------------------------------------------------------------------
# STEP 8: SAVE MODELS
# -----------------------------------------------------------------------------

print("\n[STEP 8] Saving models to disk...")

with open(os.path.join(MODELS_DIR, 'knn_user_model.pkl'), 'wb') as f:
    pickle.dump(knn_model, f)

with open(os.path.join(MODELS_DIR, 'knn_item_model.pkl'), 'wb') as f:
    pickle.dump(knn_item, f)

# Save the user-movie matrix (needed for inference)
import joblib
joblib.dump(user_movie_matrix, os.path.join(MODELS_DIR, 'user_movie_matrix.joblib'))

ratings_df.to_csv(os.path.join(DATA_DIR, 'ratings_processed.csv'), index=False)

print("[INFO] Saved: models/knn_user_model.pkl")
print("[INFO] Saved: models/knn_item_model.pkl")
print("[INFO] Saved: models/user_movie_matrix.joblib")
print("[INFO] Saved: data/ratings_processed.csv")

print("\n✅ Module 2 Complete: Collaborative Filtering trained and saved!")