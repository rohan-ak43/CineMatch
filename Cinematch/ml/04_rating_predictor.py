# =============================================================================
# MODULE 4: RATING PREDICTION MODEL
# =============================================================================
# How it works:
#   - Given a user and a movie, predict what rating the user WOULD give
#   - This helps us rank recommendations (show movies user will rate highest)
#
# Input features:
#   - User's average rating (their personal scale)
#   - User's number of ratings (experience level)
#   - Movie's average rating (popularity/quality signal)
#   - Movie's genre (encoded as numbers)
#   - Movie's language (encoded)
#
# Models compared:
#   - Linear Regression (baseline)
#   - Random Forest Regressor (more powerful, handles non-linear patterns)
#
# Metrics:
#   - RMSE: Root Mean Square Error (penalizes large mistakes heavily)
#   - MAE:  Mean Absolute Error (average prediction error in rating points)
# =============================================================================

import pandas as pd
import numpy as np
import os
import pickle
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print("=" * 60)
print("  MODULE 4: Rating Prediction Model")
print("=" * 60)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
VIZ_DIR = os.path.join(os.path.dirname(__file__), '..', 'visualizations')
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(VIZ_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# STEP 1: LOAD DATA
# -----------------------------------------------------------------------------

print("\n[STEP 1] Loading data...")

movies_path = os.path.join(DATA_DIR, 'movies_processed.csv')
ratings_path = os.path.join(DATA_DIR, 'ratings_processed.csv')

movies_df = pd.read_csv(movies_path) if os.path.exists(movies_path) else pd.read_csv(
    os.path.join(DATA_DIR, 'movies.csv'))
ratings_df = pd.read_csv(ratings_path) if os.path.exists(ratings_path) else pd.read_csv(
    os.path.join(DATA_DIR, 'ratings.csv'))

print(f"[INFO] Movies: {len(movies_df)}, Ratings: {len(ratings_df)}")

# Ensure column names are consistent
if 'rating_normalized' not in ratings_df.columns:
    user_means = ratings_df.groupby('userId')['rating'].mean()
    ratings_df = ratings_df.merge(user_means.rename('user_mean'), on='userId')
    ratings_df['rating_normalized'] = ratings_df['rating'] - ratings_df['user_mean']

# Add language column to movies if missing (simulate it)
if 'language' not in movies_df.columns:
    languages = ['English', 'English', 'English', 'English', 'French', 'Spanish', 'Hindi', 'Japanese']
    np.random.seed(42)
    movies_df['language'] = np.random.choice(languages, len(movies_df),
                                               p=[0.5, 0.15, 0.1, 0.1, 0.05, 0.04, 0.04, 0.02])

print(f"[INFO] Languages in dataset: {movies_df['language'].unique()}")

# -----------------------------------------------------------------------------
# STEP 2: FEATURE ENGINEERING
# -----------------------------------------------------------------------------
# We create NEW features from existing data. This is the most creative
# part of machine learning — designing informative features.
# -----------------------------------------------------------------------------

print("\n[STEP 2] Engineering features...")

# --- USER-LEVEL FEATURES ---

# Feature 1: User's average rating (their personal generosity/strictness)
user_avg_rating = ratings_df.groupby('userId')['rating'].mean().rename('user_avg_rating')

# Feature 2: User's rating count (how experienced they are)
user_rating_count = ratings_df.groupby('userId')['rating'].count().rename('user_rating_count')

# Feature 3: User's rating standard deviation (how opinionated they are)
user_rating_std = ratings_df.groupby('userId')['rating'].std().fillna(0).rename('user_rating_std')

# --- MOVIE-LEVEL FEATURES ---

# Feature 4: Movie's average rating (quality signal)
movie_avg_rating = ratings_df.groupby('movieId')['rating'].mean().rename('movie_avg_rating')

# Feature 5: Movie's popularity (number of ratings it received)
movie_rating_count = ratings_df.groupby('movieId')['rating'].count().rename('movie_popularity')

# Feature 6: Movie's rating standard deviation (how divisive is it?)
movie_rating_std = ratings_df.groupby('movieId')['rating'].std().fillna(0).rename('movie_rating_std')

# Merge all features into the ratings dataframe
rating_features = ratings_df[['userId', 'movieId', 'rating']].copy()
rating_features = rating_features.merge(user_avg_rating, on='userId')
rating_features = rating_features.merge(user_rating_count, on='userId')
rating_features = rating_features.merge(user_rating_std, on='userId')
rating_features = rating_features.merge(movie_avg_rating, on='movieId')
rating_features = rating_features.merge(movie_rating_count, on='movieId')
rating_features = rating_features.merge(movie_rating_std, on='movieId')

# Merge movie metadata (genre, language)
rating_features = rating_features.merge(
    movies_df[['movieId', 'genres', 'language']],
    on='movieId',
    how='left'
)

# Fill any missing values from the merge
rating_features['genres'] = rating_features['genres'].fillna('Unknown')
rating_features['language'] = rating_features['language'].fillna('English')

print(f"[INFO] Features created: {rating_features.shape[1]} columns")
print(f"[INFO] Sample feature row:\n{rating_features.iloc[0]}")

# -----------------------------------------------------------------------------
# STEP 3: ENCODE CATEGORICAL VARIABLES
# -----------------------------------------------------------------------------
# ML models only understand numbers. We need to convert:
# - Genre (string like "Action|Adventure") → Number
# - Language (string like "English") → Number
# -----------------------------------------------------------------------------

print("\n[STEP 3] Encoding categorical features...")

# --- ENCODE PRIMARY GENRE ---
# Extract just the FIRST genre from the pipe-separated list
rating_features['primary_genre'] = rating_features['genres'].apply(
    lambda x: x.split('|')[0] if pd.notna(x) else 'Unknown'
)

# LabelEncoder: assigns each unique genre a number
# Action=0, Adventure=1, Animation=2, Comedy=3, etc.
genre_encoder = LabelEncoder()
rating_features['genre_encoded'] = genre_encoder.fit_transform(
    rating_features['primary_genre']
)

print(f"[INFO] Genres encoded: {list(zip(genre_encoder.classes_, range(len(genre_encoder.classes_))))}")

# --- ENCODE LANGUAGE ---
language_encoder = LabelEncoder()
rating_features['language_encoded'] = language_encoder.fit_transform(
    rating_features['language']
)

print(f"[INFO] Languages encoded: {list(zip(language_encoder.classes_, range(len(language_encoder.classes_))))}")

# --- FEATURE: Rating difference from user average ---
# If a movie's avg rating is much higher than what the user usually gives,
# this user might rate it higher too
rating_features['user_movie_avg_diff'] = (
    rating_features['movie_avg_rating'] - rating_features['user_avg_rating']
)

# -----------------------------------------------------------------------------
# STEP 4: DEFINE FEATURES (X) AND TARGET (y)
# -----------------------------------------------------------------------------

print("\n[STEP 4] Defining feature matrix X and target y...")

FEATURE_COLUMNS = [
    'user_avg_rating',       # User's general rating tendency
    'user_rating_count',     # User's experience
    'user_rating_std',       # User's rating variability
    'movie_avg_rating',      # Movie's general quality
    'movie_popularity',      # How many people rated this movie
    'movie_rating_std',      # How divisive the movie is
    'genre_encoded',         # Primary genre as number
    'language_encoded',      # Language as number
    'user_movie_avg_diff',   # Difference between movie avg and user avg
]

X = rating_features[FEATURE_COLUMNS]
y = rating_features['rating']

print(f"[INFO] Feature matrix shape: {X.shape}")
print(f"[INFO] Target shape: {y.shape}")
print(f"[INFO] Rating distribution:\n{y.describe()}")

# Handle any remaining NaN values
X = X.fillna(0)

# -----------------------------------------------------------------------------
# STEP 5: TRAIN-TEST SPLIT
# -----------------------------------------------------------------------------

print("\n[STEP 5] Splitting data (80/20)...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"[INFO] Training set: {X_train.shape[0]} samples")
print(f"[INFO] Test set:     {X_test.shape[0]} samples")

# -----------------------------------------------------------------------------
# STEP 6: SCALE FEATURES (Standardization)
# -----------------------------------------------------------------------------
# Linear Regression is sensitive to feature scales.
# Standardization: transforms each feature to mean=0, std=1
# This ensures no single feature dominates just because of its scale.
# (Random Forest doesn't need scaling, but it doesn't hurt)
# -----------------------------------------------------------------------------

print("\n[STEP 6] Scaling features...")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("[INFO] Features scaled (mean=0, std=1)")

# -----------------------------------------------------------------------------
# STEP 7: TRAIN LINEAR REGRESSION (Baseline)
# -----------------------------------------------------------------------------

print("\n[STEP 7] Training Linear Regression (baseline model)...")

lr_model = LinearRegression()
lr_model.fit(X_train_scaled, y_train)

y_pred_lr = lr_model.predict(X_test_scaled)

# Clip predictions to valid range [0.5, 5.0]
y_pred_lr = np.clip(y_pred_lr, 0.5, 5.0)

rmse_lr = np.sqrt(mean_squared_error(y_test, y_pred_lr))
mae_lr = mean_absolute_error(y_test, y_pred_lr)

print(f"[INFO] Linear Regression Results:")
print(f"       RMSE: {rmse_lr:.4f} (lower is better)")
print(f"       MAE:  {mae_lr:.4f} (on a 0.5-5.0 scale)")

# Show feature importance (coefficients)
feature_importance_lr = pd.DataFrame({
    'feature': FEATURE_COLUMNS,
    'coefficient': lr_model.coef_
}).sort_values('coefficient', key=abs, ascending=False)
print(f"\n[INFO] Feature Coefficients (|impact| ranking):")
print(feature_importance_lr.to_string(index=False))

# -----------------------------------------------------------------------------
# STEP 8: TRAIN RANDOM FOREST REGRESSOR
# -----------------------------------------------------------------------------
# Random Forest:
# - Builds many decision trees on random subsets of data
# - Each tree makes a prediction
# - Final prediction = AVERAGE of all tree predictions
# - More powerful than Linear Regression — captures non-linear patterns
# - n_estimators: number of trees (more = better but slower)
# - max_depth: how deep each tree can grow (limits overfitting)
# -----------------------------------------------------------------------------

print("\n[STEP 8] Training Random Forest Regressor...")

rf_model = RandomForestRegressor(
    n_estimators=100,       # 100 decision trees
    max_depth=10,           # Each tree max 10 levels deep
    min_samples_split=5,    # Need at least 5 samples to split a node
    min_samples_leaf=2,     # Each leaf must have at least 2 samples
    random_state=42,
    n_jobs=-1               # Use all CPU cores
)

rf_model.fit(X_train, y_train)  # Random Forest doesn't need scaled data

y_pred_rf = rf_model.predict(X_test)
y_pred_rf = np.clip(y_pred_rf, 0.5, 5.0)

rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
mae_rf = mean_absolute_error(y_test, y_pred_rf)

print(f"[INFO] Random Forest Results:")
print(f"       RMSE: {rmse_rf:.4f}")
print(f"       MAE:  {mae_rf:.4f}")

# Feature importance from Random Forest (more reliable than LR coefficients)
feature_importance_rf = pd.DataFrame({
    'feature': FEATURE_COLUMNS,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print(f"\n[INFO] Feature Importances (Random Forest):")
print(feature_importance_rf.to_string(index=False))

# -----------------------------------------------------------------------------
# STEP 9: MODEL COMPARISON AND SELECTION
# -----------------------------------------------------------------------------

print("\n[STEP 9] Model Comparison:")
print("-" * 40)
print(f"{'Model':<25} {'RMSE':>8} {'MAE':>8}")
print("-" * 40)
print(f"{'Linear Regression':<25} {rmse_lr:>8.4f} {mae_lr:>8.4f}")
print(f"{'Random Forest':<25} {rmse_rf:>8.4f} {mae_rf:>8.4f}")
print("-" * 40)

# Pick model with lower RMSE
if rmse_rf < rmse_lr:
    best_model = rf_model
    best_model_name = "Random Forest"
    best_rmse = rmse_rf
    best_mae = mae_rf
    y_pred_best = y_pred_rf
    needs_scaling = False
else:
    best_model = lr_model
    best_model_name = "Linear Regression"
    best_rmse = rmse_lr
    best_mae = mae_lr
    y_pred_best = y_pred_lr
    needs_scaling = True

print(f"\n✅ Best Model: {best_model_name}")
print(f"   RMSE: {best_rmse:.4f} | MAE: {best_mae:.4f}")

# -----------------------------------------------------------------------------
# STEP 10: VISUALIZATIONS
# -----------------------------------------------------------------------------

print("\n[STEP 10] Generating visualizations...")

# Plot 1: Actual vs Predicted ratings
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].scatter(y_test, y_pred_best, alpha=0.3, s=10)
axes[0].plot([0.5, 5.0], [0.5, 5.0], 'r--', linewidth=2)
axes[0].set_xlabel('Actual Rating')
axes[0].set_ylabel('Predicted Rating')
axes[0].set_title(f'Actual vs Predicted Ratings\n({best_model_name})')
axes[0].set_xlim([0, 5.5])
axes[0].set_ylim([0, 5.5])

# Plot 2: Feature importance (Random Forest)
axes[1].barh(
    feature_importance_rf['feature'],
    feature_importance_rf['importance']
)
axes[1].set_xlabel('Importance Score')
axes[1].set_title('Feature Importances (Random Forest)')
axes[1].invert_yaxis()

plt.tight_layout()
plt.savefig(os.path.join(VIZ_DIR, 'rating_prediction_evaluation.png'), dpi=150)
plt.close()
print("[INFO] Saved: visualizations/rating_prediction_evaluation.png")

# Plot 2: Rating distribution
fig, ax = plt.subplots(figsize=(8, 5))
bins = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5]
ax.hist(ratings_df['rating'], bins=bins, edgecolor='black', alpha=0.8)
ax.set_xlabel('Rating')
ax.set_ylabel('Count')
ax.set_title('Rating Distribution in Dataset')
ax.set_xticks([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])
plt.tight_layout()
plt.savefig(os.path.join(VIZ_DIR, 'rating_distribution.png'), dpi=150)
plt.close()
print("[INFO] Saved: visualizations/rating_distribution.png")

# -----------------------------------------------------------------------------
# STEP 11: DEMO — Predict rating for a specific user-movie pair
# -----------------------------------------------------------------------------

print("\n[STEP 11] Demo: Predicting rating for a specific user-movie pair...")

# Simulate a new user-movie pair
sample_features = {
    'user_avg_rating': [3.8],        # This user tends to rate ~3.8 on average
    'user_rating_count': [45],        # They've rated 45 movies
    'user_rating_std': [0.9],         # Their ratings vary by ~0.9
    'movie_avg_rating': [4.2],        # This movie is highly rated by others
    'movie_popularity': [150],         # 150 people have rated this movie
    'movie_rating_std': [0.7],        # Not very divisive
    'genre_encoded': [0],             # Action genre (index 0)
    'language_encoded': [0],          # English
    'user_movie_avg_diff': [0.4],     # Movie avg is 0.4 above user avg
}

sample_df = pd.DataFrame(sample_features)

if needs_scaling:
    sample_scaled = scaler.transform(sample_df)
    predicted_rating = best_model.predict(sample_scaled)[0]
else:
    predicted_rating = best_model.predict(sample_df)[0]

predicted_rating = np.clip(predicted_rating, 0.5, 5.0)
print(f"\n[RESULT] Predicted Rating: {predicted_rating:.2f} / 5.0")
print(f"         ({'⭐' * int(round(predicted_rating))} out of ⭐⭐⭐⭐⭐)")

# -----------------------------------------------------------------------------
# STEP 12: SAVE MODELS AND ENCODERS
# -----------------------------------------------------------------------------

print("\n[STEP 12] Saving models...")

with open(os.path.join(MODELS_DIR, 'rating_predictor.pkl'), 'wb') as f:
    pickle.dump(best_model, f)

with open(os.path.join(MODELS_DIR, 'rating_scaler.pkl'), 'wb') as f:
    pickle.dump(scaler, f)

with open(os.path.join(MODELS_DIR, 'genre_encoder.pkl'), 'wb') as f:
    pickle.dump(genre_encoder, f)

with open(os.path.join(MODELS_DIR, 'language_encoder.pkl'), 'wb') as f:
    pickle.dump(language_encoder, f)

# Save metadata about the best model
import json
model_metadata = {
    'best_model': best_model_name,
    'rmse': round(best_rmse, 4),
    'mae': round(best_mae, 4),
    'features': FEATURE_COLUMNS,
    'needs_scaling': needs_scaling
}
with open(os.path.join(MODELS_DIR, 'rating_model_metadata.json'), 'w') as f:
    json.dump(model_metadata, f, indent=2)

print("[INFO] Saved: models/rating_predictor.pkl")
print("[INFO] Saved: models/rating_scaler.pkl")
print("[INFO] Saved: models/genre_encoder.pkl")
print("[INFO] Saved: models/language_encoder.pkl")
print("[INFO] Saved: models/rating_model_metadata.json")

print(f"\n✅ Module 4 Complete: Rating Predictor trained!")
print(f"   Best Model: {best_model_name} | RMSE: {best_rmse:.4f} | MAE: {best_mae:.4f}")