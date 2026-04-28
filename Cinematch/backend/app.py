# =============================================================================
# CineMatch — Flask Backend API
# =============================================================================
# This is the main backend server. It:
#   1. Loads all trained ML models on startup
#   2. Exposes REST API endpoints for the frontend
#   3. Handles user authentication with JWT tokens
#   4. Connects to MySQL for persistent storage
#   5. Uses Firebase Authentication + Firestore for user management
#
# API Endpoints:
#   POST  /api/auth/register     — Register new user (Email/Password)
#   POST  /api/auth/login        — Login, returns JWT token
#   POST  /api/auth/firebase     — Verify Firebase ID token (Google / Email), returns JWT
#   POST  /api/recommend         — Get movie recommendations
#   POST  /api/predict_rating    — Predict rating for a movie
#   POST  /api/analyze_review    — Analyze review sentiment
#   GET   /api/get_history       — Get user's watch history
#   POST  /api/rate_movie        — Submit a rating
#   POST  /api/submit_review     — Submit a review
#   GET   /api/movies            — Get all movies (with filters)
#   GET   /api/stats             — Get system stats
#   GET   /api/health            — Health check
# =============================================================================

import os
import re
import json
import pickle
import numpy as np
import pandas as pd
import joblib
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth, firestore

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
import bcrypt

# Initialize Firebase Admin SDK with service account
_SERVICE_ACCOUNT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'firebase', 'functions', 'serviceAccountKey.json'
)
cred = credentials.Certificate(_SERVICE_ACCOUNT_PATH)
firebase_admin.initialize_app(cred)

# Firestore client (used throughout the app)
db = firestore.client()

# =============================================================================
# APP INITIALIZATION
# =============================================================================

# Resolve the frontend directory relative to this file
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,   # serve /frontend as static files
    static_url_path='',           # root URL maps to frontend folder
)
CORS(app, origins=["http://localhost:5000", "http://127.0.0.1:5000",
                    "http://localhost:3000", "*"])

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cinematch-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'cinematch-jwt-secret-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Database config (SQLAlchemy-free version using direct queries for simplicity)
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'cinematch'),
    'port': int(os.environ.get('DB_PORT', 3306)),
}

jwt = JWTManager(app)

# =============================================================================
# PATH SETUP
# =============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# =============================================================================
# DATABASE CONNECTION (with graceful fallback for development without MySQL)
# =============================================================================

USE_MEMORY_DB = False  # Will be set to True if MySQL is not available
memory_db = {
    'users': {},      # {user_id: {name, email, password, ...}}
    'ratings': [],    # [{user_id, movie_id, rating, created_at}]
    'reviews': [],    # [{user_id, movie_id, review_text, sentiment, ...}]
    'watch_history': [],
    'next_user_id': 1
}

def get_db_connection():
    """Get a MySQL database connection, or return None if unavailable."""
    try:
        import pymysql
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5
        )
        return conn
    except Exception as e:
        app.logger.warning(f"MySQL unavailable ({e}). Using in-memory database.")
        return None


def db_execute(query, params=None, fetch='none'):
    """
    Execute a SQL query. Falls back to in-memory operations if MySQL unavailable.
    fetch: 'none' | 'one' | 'all'
    """
    conn = get_db_connection()
    if conn is None:
        return None  # Handle in calling function

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            if fetch == 'all':
                return cursor.fetchall()
            elif fetch == 'one':
                return cursor.fetchone()
            else:
                conn.commit()
                return cursor.lastrowid
    except Exception as e:
        app.logger.error(f"DB Error: {e}")
        return None
    finally:
        conn.close()

# =============================================================================
# LOAD ALL ML MODELS
# =============================================================================

print("\n[STARTUP] Loading ML models...")

ml_models = {}  # Global dict to hold all models

def load_models():
    """Load all trained ML models into memory at startup."""
    global ml_models

    model_files = {
        'tfidf': 'tfidf_vectorizer.pkl',
        'cosine_sim': 'cosine_sim_matrix.pkl',
        'movie_indices': 'movie_indices.pkl',
        'knn_user': 'knn_user_model.pkl',
        'mood_classifier': 'mood_classifier.pkl',
        'mood_tfidf': 'mood_tfidf.pkl',
        'mood_label_decode': 'mood_label_decode.pkl',
        'mood_genre_map': 'mood_genre_map.pkl',
        'rating_predictor': 'rating_predictor.pkl',
        'rating_scaler': 'rating_scaler.pkl',
        'genre_encoder': 'genre_encoder.pkl',
        'language_encoder': 'language_encoder.pkl',
        'sentiment_classifier': 'sentiment_classifier.pkl',
        'sentiment_tfidf': 'sentiment_tfidf.pkl',
        'sentiment_map': 'sentiment_map.pkl',
    }

    for key, filename in model_files.items():
        path = os.path.join(MODELS_DIR, filename)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                ml_models[key] = pickle.load(f)
            print(f"  ✅ Loaded: {filename}")
        else:
            print(f"  ⚠️  Missing: {filename} — Run train_all.py first")

    # Load joblib files
    matrix_path = os.path.join(MODELS_DIR, 'user_movie_matrix.joblib')
    if os.path.exists(matrix_path):
        ml_models['user_movie_matrix'] = joblib.load(matrix_path)
        print(f"  ✅ Loaded: user_movie_matrix.joblib")

    # Load JSON config
    config_path = os.path.join(MODELS_DIR, 'system_config.json')
    if os.path.exists(config_path):
        with open(config_path) as f:
            ml_models['system_config'] = json.load(f)

    # Load contractions
    contractions_path = os.path.join(MODELS_DIR, 'contractions.json')
    if os.path.exists(contractions_path):
        with open(contractions_path) as f:
            ml_models['contractions'] = json.load(f)

    # Load movies and ratings dataframes
    movies_path = os.path.join(DATA_DIR, 'movies_processed.csv')
    if not os.path.exists(movies_path):
        movies_path = os.path.join(DATA_DIR, 'movies.csv')
    if os.path.exists(movies_path):
        ml_models['movies_df'] = pd.read_csv(movies_path)

    ratings_path = os.path.join(DATA_DIR, 'ratings_processed.csv')
    if not os.path.exists(ratings_path):
        ratings_path = os.path.join(DATA_DIR, 'ratings.csv')
    if os.path.exists(ratings_path):
        ml_models['ratings_df'] = pd.read_csv(ratings_path)

    print(f"\n[STARTUP] Loaded {len(ml_models)} model components")


load_models()

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def clean_text_for_ml(text, expand_contractions=True):
    """Clean and normalize text for ML model input."""
    text = str(text).lower()
    if expand_contractions and 'contractions' in ml_models:
        for c, e in ml_models['contractions'].items():
            text = text.replace(c, e)
    text = re.sub(r'<[^>]+>', '', text)        # Remove HTML
    text = re.sub(r'http\S+', '', text)         # Remove URLs
    text = re.sub(r'[^\w\s]', ' ', text)        # Remove punctuation
    text = re.sub(r'\d+', '', text)             # Remove digits
    text = re.sub(r'\s+', ' ', text).strip()    # Clean whitespace
    return text


def movie_to_dict(row):
    """Convert a movie dataframe row to a JSON-friendly dict."""
    return {
        'id': int(row.get('movieId', 0)),
        'title': str(row.get('title', '')),
        'genres': str(row.get('genres', '')),
        'language': str(row.get('language', 'English')),
        'avg_rating': float(row.get('avg_rating', 0)) if pd.notna(row.get('avg_rating')) else 0,
        'poster_url': row.get('poster_url', None),
    }


def get_movies_df():
    """Get movies dataframe, either from ML models or from DB."""
    if 'movies_df' in ml_models:
        return ml_models['movies_df']
    return pd.DataFrame()


def get_ratings_df():
    """Get ratings dataframe."""
    if 'ratings_df' in ml_models:
        return ml_models['ratings_df']
    return pd.DataFrame()

# =============================================================================
# ROUTE: SERVE FRONTEND (makes Firebase Auth work — requires http://)
# =============================================================================

from flask import send_from_directory

@app.route('/')
def serve_index():
    """Serve the main login page."""
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/pages/<path:filename>')
def serve_pages(filename):
    """Serve files from the /frontend/pages/ directory."""
    pages_dir = os.path.join(FRONTEND_DIR, 'pages')
    return send_from_directory(pages_dir, filename)

# =============================================================================
# ROUTE: HEALTH CHECK
# =============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'models_loaded': list(ml_models.keys()),
        'version': '1.0.0'
    })


# =============================================================================
# ROUTE: USER REGISTRATION
# =============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Register a new user via Email/Password.
    Request body: { name, email, password }
    User profile is saved to Firestore 'users' collection.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    # Validation
    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({'error': 'Invalid email format'}), 400

    # Hash password with bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user_id = None

    # Try MySQL first
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                # Check if email exists
                cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    return jsonify({'error': 'Email already registered'}), 409

                # Insert new user
                cursor.execute(
                    "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                    (name, email, hashed_password)
                )
                conn.commit()
                user_id = cursor.lastrowid
        finally:
            conn.close()
    else:
        # In-memory fallback
        if any(u['email'] == email for u in memory_db['users'].values()):
            return jsonify({'error': 'Email already registered'}), 409
        user_id = memory_db['next_user_id']
        memory_db['users'][user_id] = {
            'user_id': user_id, 'name': name, 'email': email,
            'password': hashed_password, 'created_at': datetime.now().isoformat()
        }
        memory_db['next_user_id'] += 1

    # Sync user profile to Firestore
    try:
        user_doc_ref = db.collection('users').document(str(user_id))
        user_doc_ref.set({
            'user_id': user_id,
            'name': name,
            'email': email,
            'provider': 'email_password',
            'created_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat(),
        }, merge=True)
    except Exception as fs_err:
        app.logger.warning(f"Firestore sync failed for user {user_id}: {fs_err}")

    # Generate JWT token
    token = create_access_token(identity=str(user_id))

    return jsonify({
        'message': 'Registration successful!',
        'user': {'id': user_id, 'name': name, 'email': email},
        'token': token
    }), 201

# =============================================================================
# ROUTE: USER LOGIN
# =============================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT token.
    Request body: { email, password }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    # Look up user
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT user_id, name, email, password FROM users WHERE email = %s AND is_active = 1",
                    (email,)
                )
                user = cursor.fetchone()
        finally:
            conn.close()
    else:
        # In-memory fallback
        user = next((u for u in memory_db['users'].values() if u['email'] == email), None)

    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    # Verify password
    stored_password = user['password'] if isinstance(user, dict) else user['password']
    if not bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
        return jsonify({'error': 'Invalid email or password'}), 401

    user_id = user['user_id']
    token = create_access_token(identity=str(user_id))

    # Update last_login in Firestore
    try:
        db.collection('users').document(str(user_id)).set(
            {'last_login': datetime.now().isoformat()}, merge=True
        )
    except Exception as fs_err:
        app.logger.warning(f"Firestore last_login update failed: {fs_err}")

    return jsonify({
        'message': 'Login successful!',
        'user': {
            'id': user_id,
            'name': user['name'],
            'email': user['email']
        },
        'token': token
    })


# =============================================================================
# ROUTE: FIREBASE AUTH (Email/Password + Google Sign-In via client SDK)
# =============================================================================

@app.route('/api/auth/firebase', methods=['POST'])
def firebase_login():
    """
    Verify a Firebase ID token issued by the client (Email/Password or Google).
    The client calls Firebase SDK first, then sends the resulting ID token here.
    This endpoint:
      1. Verifies the token with Firebase Admin SDK
      2. Upserts the user record in Firestore 'users' collection
      3. Returns a JWT for all subsequent @jwt_required() API calls

    Request body: { id_token: "<firebase_id_token>" }
    """
    data = request.get_json()
    if not data or not data.get('id_token'):
        return jsonify({'error': 'Firebase ID token is required'}), 400

    id_token = data['id_token']

    # 1. Verify the Firebase ID token
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
    except firebase_auth.ExpiredIdTokenError:
        return jsonify({'error': 'Firebase token has expired. Please sign in again.'}), 401
    except firebase_auth.InvalidIdTokenError:
        return jsonify({'error': 'Invalid Firebase token.'}), 401
    except Exception as e:
        app.logger.error(f"Firebase token verification error: {e}")
        return jsonify({'error': 'Token verification failed.'}), 401

    firebase_uid = decoded_token['uid']
    email = decoded_token.get('email', '')
    name = decoded_token.get('name', email.split('@')[0] if email else 'User')
    picture = decoded_token.get('picture', None)
    provider = decoded_token.get('firebase', {}).get('sign_in_provider', 'unknown')

    # 2. Upsert user in Firestore 'users' collection (keyed by Firebase UID)
    now = datetime.now().isoformat()
    user_doc_ref = db.collection('users').document(firebase_uid)
    user_doc = user_doc_ref.get()

    if user_doc.exists:
        # Existing user — update last login
        user_doc_ref.update({
            'last_login': now,
            'name': name,
            'picture': picture,
        })
        user_data = user_doc.to_dict()
        is_new_user = False
    else:
        # New user — create full profile
        user_data = {
            'firebase_uid': firebase_uid,
            'name': name,
            'email': email,
            'picture': picture,
            'provider': provider,
            'created_at': now,
            'last_login': now,
            'ratings_count': 0,
            'reviews_count': 0,
        }
        user_doc_ref.set(user_data)
        is_new_user = True

    # Generate and store initial recommendations
    try:
        recs, _, _ = generate_recommendations(top_n=10)
        if isinstance(recs, list):
            user_doc_ref.set({'recommendations': recs}, merge=True)
    except Exception as e:
        app.logger.error(f"Failed to generate/store initial recommendations: {e}")

    # 3. Issue a JWT using the Firebase UID as identity
    jwt_token = create_access_token(identity=firebase_uid)

    return jsonify({
        'message': 'Welcome back!' if not is_new_user else 'Account created!',
        'user': {
            'id': firebase_uid,
            'name': name,
            'email': email,
            'picture': picture,
        },
        'token': jwt_token,
        'is_new_user': is_new_user,
    })

# =============================================================================
# ROUTE: RECOMMENDATIONS
# =============================================================================

def get_int_user_id(identity):
    """Safely convert a JWT identity (which might be a Firebase string UID) to an int."""
    try:
        return int(identity)
    except (ValueError, TypeError):
        return 0

def generate_recommendations(mood_text='', liked_movie='', preferred_genre='', preferred_language='', top_n=10):
    """Core recommendation logic extracted from /api/recommend."""
    movies_df = get_movies_df()
    ratings_df = get_ratings_df()

    if movies_df.empty:
        return {'error': 'Movie database not loaded.'}, None, None

    # --- Step 1: Detect mood ---
    detected_mood = None
    mood_genres = None

    if mood_text and 'mood_classifier' in ml_models and 'mood_tfidf' in ml_models:
        clean_mood = clean_text_for_ml(mood_text, expand_contractions=False)
        mood_vector = ml_models['mood_tfidf'].transform([clean_mood])
        mood_class = ml_models['mood_classifier'].predict(mood_vector)[0]
        mood_decode = ml_models.get('mood_label_decode', {0: 'happy', 1: 'sad', 2: 'excited', 3: 'bored', 4: 'stressed'})
        detected_mood = mood_decode.get(mood_class, 'happy')

        mood_genre_map = ml_models.get('mood_genre_map', {})
        if detected_mood in mood_genre_map:
            mood_genres = mood_genre_map[detected_mood]['genres']

    # --- Step 2: Content-Based Scores ---
    movie_scores = {mid: 0.0 for mid in movies_df['movieId'].values}

    if liked_movie and liked_movie in ml_models.get('movie_indices', pd.Series()).index:
        cosine_sim = ml_models['cosine_sim']
        movie_idx = ml_models['movie_indices'][liked_movie]
        sim_scores = list(enumerate(cosine_sim[movie_idx]))
        sim_scores_sorted = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:50]

        for idx, score in sim_scores_sorted:
            if idx < len(movies_df):
                mid = int(movies_df.iloc[idx]['movieId'])
                movie_scores[mid] = movie_scores.get(mid, 0) + 0.4 * score

    # --- Step 3: Popularity boost ---
    if not ratings_df.empty:
        movie_avg = ratings_df.groupby('movieId')['rating'].mean()
        movie_count = ratings_df.groupby('movieId')['rating'].count()
        global_mean = ratings_df['rating'].mean()

        for mid in movie_scores:
            if mid in movie_avg.index:
                v = movie_count[mid]
                R = movie_avg[mid]
                m = 5
                bayesian = (v / (v + m)) * R + (m / (v + m)) * global_mean
                movie_scores[mid] += 0.3 * (bayesian / 5.0)
            else:
                movie_scores[mid] += 0.3 * (global_mean / 5.0)

    # --- Step 4: Build results ---
    results = []
    for mid, score in movie_scores.items():
        row = movies_df[movies_df['movieId'] == mid]
        if row.empty:
            continue
        row = row.iloc[0]
        results.append({
            'id': int(mid),
            'title': str(row.get('title', '')),
            'genres': str(row.get('genres', '')),
            'language': str(row.get('language', 'English')),
            'score': float(score),
            'poster_url': row.get('poster_url', None)
        })

    results_df = pd.DataFrame(results)

    # --- Step 5: Apply filters ---
    if mood_genres and len(results_df) > 0:
        mood_mask = results_df['genres'].apply(
            lambda g: any(genre in str(g) for genre in mood_genres)
        )
        mood_filtered = results_df[mood_mask]
        if len(mood_filtered) >= top_n:
            results_df = mood_filtered

    if preferred_genre and len(results_df) > 0:
        genre_mask = results_df['genres'].str.contains(preferred_genre, na=False, case=False)
        genre_filtered = results_df[genre_mask]
        if len(genre_filtered) >= top_n:
            results_df = genre_filtered

    if preferred_language and len(results_df) > 0:
        lang_filtered = results_df[results_df['language'] == preferred_language]
        if len(lang_filtered) >= top_n:
            results_df = lang_filtered

    # Remove liked movie from results
    if liked_movie:
        results_df = results_df[results_df['title'] != liked_movie]

    # Sort and return top N
    top_results = results_df.sort_values('score', ascending=False).head(top_n)
    
    if 'poster_url' in top_results.columns:
        top_results['poster_url'] = top_results['poster_url'].fillna('')
        
    return top_results.to_dict(orient='records'), detected_mood, mood_genres

@app.route('/api/recommend', methods=['POST'])
@jwt_required()
def recommend():
    """
    Get personalized movie recommendations.
    Request body: {
        mood_text: "I feel excited and want action",
        liked_movie: "Heat (1995)",           (optional)
        genre: "Action",                       (optional)
        language: "English",                   (optional)
        top_n: 10
    }
    """
    identity = get_jwt_identity()
    user_id = get_int_user_id(identity)
    data = request.get_json() or {}

    mood_text = data.get('mood_text', '')
    liked_movie = data.get('liked_movie', '')
    preferred_genre = data.get('genre', '')
    preferred_language = data.get('language', '')
    top_n = min(int(data.get('top_n', 10)), 20)

    recs, detected_mood, mood_genres = generate_recommendations(
        mood_text, liked_movie, preferred_genre, preferred_language, top_n
    )

    if isinstance(recs, dict) and 'error' in recs:
        return jsonify(recs), 500

    # Log recommendation session
    rec_data = {
        'user_id': user_id,
        'mood_input': mood_text,
        'detected_mood': detected_mood,
        'genre_filter': preferred_genre,
        'language_filter': preferred_language,
        'movies_returned': json.dumps([r['id'] for r in recs]),
        'algorithm_used': 'hybrid'
    }
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO recommendations_log
                       (user_id, mood_input, detected_mood, genre_filter, language_filter, movies_returned, algorithm_used)
                       VALUES (%(user_id)s, %(mood_input)s, %(detected_mood)s, %(genre_filter)s, %(language_filter)s,
                               %(movies_returned)s, %(algorithm_used)s)""",
                    rec_data
                )
                conn.commit()
        finally:
            conn.close()

    return jsonify({
        'recommendations': recs,
        'detected_mood': detected_mood,
        'mood_genres': mood_genres,
        'total': len(recs),
        'algorithm': 'hybrid'
    })

# =============================================================================
# ROUTE: PREDICT RATING
# =============================================================================

@app.route('/api/predict_rating', methods=['POST'])
@jwt_required()
def predict_rating():
    """
    Predict what rating a user would give a specific movie.
    Request body: { movie_id: 6 }
    """
    identity = get_jwt_identity()
    user_id = get_int_user_id(identity)
    data = request.get_json() or {}
    movie_id = data.get('movie_id')

    if not movie_id:
        return jsonify({'error': 'movie_id is required'}), 400

    if 'rating_predictor' not in ml_models:
        return jsonify({'error': 'Rating predictor not loaded'}), 500

    movies_df = get_movies_df()
    ratings_df = get_ratings_df()

    movie_row = movies_df[movies_df['movieId'] == int(movie_id)]
    if movie_row.empty:
        return jsonify({'error': f'Movie {movie_id} not found'}), 404

    movie_row = movie_row.iloc[0]

    # Build feature vector
    user_ratings = ratings_df[ratings_df['userId'] == user_id]['rating'] if not ratings_df.empty else pd.Series([3.0])
    movie_ratings = ratings_df[ratings_df['movieId'] == int(movie_id)]['rating'] if not ratings_df.empty else pd.Series([3.0])

    user_avg = user_ratings.mean() if len(user_ratings) > 0 else 3.0
    user_count = len(user_ratings)
    user_std = user_ratings.std() if len(user_ratings) > 1 else 0.5
    movie_avg = movie_ratings.mean() if len(movie_ratings) > 0 else 3.0
    movie_pop = len(movie_ratings)
    movie_std = movie_ratings.std() if len(movie_ratings) > 1 else 0.5

    # Encode genre
    primary_genre = str(movie_row.get('genres', 'Drama')).split('|')[0]
    genre_encoder = ml_models.get('genre_encoder')
    genre_encoded = 0
    if genre_encoder:
        try:
            genre_encoded = int(genre_encoder.transform([primary_genre])[0])
        except Exception:
            genre_encoded = 0

    # Encode language
    language = str(movie_row.get('language', 'English'))
    lang_encoder = ml_models.get('language_encoder')
    lang_encoded = 0
    if lang_encoder:
        try:
            lang_encoded = int(lang_encoder.transform([language])[0])
        except Exception:
            lang_encoded = 0

    features = pd.DataFrame([{
        'user_avg_rating': user_avg,
        'user_rating_count': user_count,
        'user_rating_std': user_std,
        'movie_avg_rating': movie_avg,
        'movie_popularity': movie_pop,
        'movie_rating_std': movie_std,
        'genre_encoded': genre_encoded,
        'language_encoded': lang_encoded,
        'user_movie_avg_diff': movie_avg - user_avg,
    }])

    # Apply scaling if needed
    metadata_path = os.path.join(MODELS_DIR, 'rating_model_metadata.json')
    needs_scaling = False
    if os.path.exists(metadata_path):
        with open(metadata_path) as f:
            meta = json.load(f)
            needs_scaling = meta.get('needs_scaling', False)

    if needs_scaling and 'rating_scaler' in ml_models:
        features_scaled = ml_models['rating_scaler'].transform(features)
        predicted = float(ml_models['rating_predictor'].predict(features_scaled)[0])
    else:
        predicted = float(ml_models['rating_predictor'].predict(features)[0])

    predicted = round(max(0.5, min(5.0, predicted)), 1)

    return jsonify({
        'movie_id': int(movie_id),
        'movie_title': str(movie_row.get('title', '')),
        'predicted_rating': predicted,
        'stars': '⭐' * int(round(predicted)),
        'confidence': 'medium'
    })

# =============================================================================
# ROUTE: SENTIMENT ANALYSIS
# =============================================================================

@app.route('/api/analyze_review', methods=['POST'])
@jwt_required()
def analyze_review():
    """
    Analyze sentiment of a movie review.
    Request body: { review_text: "This movie was amazing!" }
    """
    data = request.get_json() or {}
    review_text = data.get('review_text', '').strip()

    if not review_text:
        return jsonify({'error': 'review_text is required'}), 400
    if len(review_text) < 5:
        return jsonify({'error': 'Review is too short'}), 400

    if 'sentiment_classifier' not in ml_models:
        return jsonify({'error': 'Sentiment model not loaded'}), 500

    # Clean the text
    clean_review = clean_text_for_ml(review_text)

    # Vectorize
    review_vector = ml_models['sentiment_tfidf'].transform([clean_review])

    # Predict
    predicted_class = int(ml_models['sentiment_classifier'].predict(review_vector)[0])
    sentiment_data = ml_models.get('sentiment_map', {'decode': {0: 'negative', 1: 'neutral', 2: 'positive'}})
    sentiment_decode = sentiment_data.get('decode', {0: 'negative', 1: 'neutral', 2: 'positive'})
    predicted_sentiment = sentiment_decode.get(predicted_class, 'neutral')

    # Get probabilities
    probabilities = ml_models['sentiment_classifier'].predict_proba(review_vector)[0]
    confidence = float(max(probabilities) * 100)
    prob_dict = {
        'negative': float(probabilities[0] * 100),
        'neutral': float(probabilities[1] * 100),
        'positive': float(probabilities[2] * 100)
    }

    emoji_map = {'positive': '😊', 'neutral': '😐', 'negative': '😞'}

    return jsonify({
        'sentiment': predicted_sentiment,
        'confidence': round(confidence, 1),
        'probabilities': {k: round(v, 1) for k, v in prob_dict.items()},
        'emoji': emoji_map.get(predicted_sentiment, '😐')
    })

# =============================================================================
# ROUTE: SUBMIT REVIEW (with auto-sentiment analysis)
# =============================================================================

@app.route('/api/submit_review', methods=['POST'])
@jwt_required()
def submit_review():
    """
    Submit a movie review. Automatically runs sentiment analysis.
    Request body: { movie_id, review_text }
    """
    identity = get_jwt_identity()
    user_id = get_int_user_id(identity)
    data = request.get_json() or {}

    movie_id = data.get('movie_id')
    review_text = data.get('review_text', '').strip()

    if not movie_id or not review_text:
        return jsonify({'error': 'movie_id and review_text are required'}), 400

    # Auto-detect sentiment
    sentiment = 'neutral'
    confidence = 0.0

    if 'sentiment_classifier' in ml_models:
        clean_review = clean_text_for_ml(review_text)
        review_vector = ml_models['sentiment_tfidf'].transform([clean_review])
        predicted_class = int(ml_models['sentiment_classifier'].predict(review_vector)[0])
        sentiment_data = ml_models.get('sentiment_map', {'decode': {0: 'negative', 1: 'neutral', 2: 'positive'}})
        sentiment_decode = sentiment_data.get('decode', {0: 'negative', 1: 'neutral', 2: 'positive'})
        sentiment = sentiment_decode.get(predicted_class, 'neutral')
        probabilities = ml_models['sentiment_classifier'].predict_proba(review_vector)[0]
        confidence = float(max(probabilities) * 100)

    # Save to DB
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO reviews (user_id, movie_id, review_text, sentiment, confidence)
                       VALUES (%s, %s, %s, %s, %s)
                       ON DUPLICATE KEY UPDATE
                       review_text = VALUES(review_text),
                       sentiment = VALUES(sentiment),
                       confidence = VALUES(confidence)""",
                    (user_id, movie_id, review_text, sentiment, confidence)
                )
                conn.commit()
                review_id = cursor.lastrowid
        finally:
            conn.close()
    else:
        review_id = len(memory_db['reviews']) + 1
        memory_db['reviews'].append({
            'review_id': review_id, 'user_id': user_id, 'movie_id': movie_id,
            'review_text': review_text, 'sentiment': sentiment,
            'confidence': confidence, 'created_at': datetime.now().isoformat()
        })

    return jsonify({
        'message': 'Review submitted successfully!',
        'review_id': review_id,
        'sentiment': sentiment,
        'confidence': round(confidence, 1)
    }), 201

# =============================================================================
# ROUTE: RATE A MOVIE
# =============================================================================

@app.route('/api/rate_movie', methods=['POST'])
@jwt_required()
def rate_movie():
    """
    Submit or update a movie rating.
    Request body: { movie_id, rating }
    """
    identity = get_jwt_identity()
    user_id = get_int_user_id(identity)
    data = request.get_json() or {}

    movie_id = data.get('movie_id')
    rating = data.get('rating')

    if not movie_id or rating is None:
        return jsonify({'error': 'movie_id and rating are required'}), 400
    if not (0.5 <= float(rating) <= 5.0):
        return jsonify({'error': 'Rating must be between 0.5 and 5.0'}), 400

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO ratings (user_id, movie_id, rating)
                       VALUES (%s, %s, %s)
                       ON DUPLICATE KEY UPDATE rating = VALUES(rating)""",
                    (user_id, movie_id, float(rating))
                )
                conn.commit()
        finally:
            conn.close()
    else:
        # Update in-memory
        existing = next(
            (r for r in memory_db['ratings']
             if r['user_id'] == user_id and r['movie_id'] == movie_id),
            None
        )
        if existing:
            existing['rating'] = float(rating)
        else:
            memory_db['ratings'].append({
                'user_id': user_id, 'movie_id': movie_id,
                'rating': float(rating), 'created_at': datetime.now().isoformat()
            })

        # Add to watch history
        memory_db['watch_history'].append({
            'user_id': user_id, 'movie_id': movie_id,
            'watched_at': datetime.now().isoformat()
        })

    return jsonify({'message': 'Rating saved!', 'rating': float(rating)})

# =============================================================================
# ROUTE: WATCH HISTORY
# =============================================================================

@app.route('/api/get_history', methods=['GET'])
@jwt_required()
def get_history():
    """Get the authenticated user's watch history."""
    identity = get_jwt_identity()
    user_id = get_int_user_id(identity)
    limit = int(request.args.get('limit', 20))

    movies_df = get_movies_df()

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT wh.movie_id, wh.watched_at, m.title, m.genre
                       FROM watch_history wh
                       LEFT JOIN movies m ON wh.movie_id = m.movie_id
                       WHERE wh.user_id = %s
                       ORDER BY wh.watched_at DESC LIMIT %s""",
                    (user_id, limit)
                )
                history = cursor.fetchall()
        finally:
            conn.close()
    else:
        # In-memory fallback
        user_history = [h for h in memory_db['watch_history'] if h['user_id'] == user_id]
        user_history = sorted(user_history, key=lambda x: x['watched_at'], reverse=True)[:limit]

        history = []
        for h in user_history:
            movie_row = movies_df[movies_df['movieId'] == h['movie_id']]
            if not movie_row.empty:
                row = movie_row.iloc[0]
                history.append({
                    'movie_id': int(h['movie_id']),
                    'watched_at': h['watched_at'],
                    'title': str(row.get('title', '')),
                    'genre': str(row.get('genres', ''))
                })

    return jsonify({'history': history, 'total': len(history)})

# =============================================================================
# ROUTE: GET MOVIES (with filtering)
# =============================================================================

@app.route('/api/movies', methods=['GET'])
def get_movies():
    """
    Get all movies with optional filtering.
    Query params: ?genre=Action&language=English&search=toy&limit=20
    """
    genre = request.args.get('genre', '')
    language = request.args.get('language', '')
    search = request.args.get('search', '')
    limit = min(int(request.args.get('limit', 20)), 100)

    movies_df = get_movies_df()

    if movies_df.empty:
        return jsonify({'movies': [], 'total': 0})

    filtered = movies_df.copy()

    if genre:
        filtered = filtered[filtered['genres'].str.contains(genre, na=False, case=False)]
    if language and 'language' in filtered.columns:
        filtered = filtered[filtered['language'].str.lower() == language.lower()]
    if search:
        filtered = filtered[filtered['title'].str.contains(search, na=False, case=False)]

    filtered = filtered.head(limit)

    movies_list = []
    for _, row in filtered.iterrows():
        movies_list.append({
            'id': int(row.get('movieId', 0)),
            'title': str(row.get('title', '')),
            'genres': str(row.get('genres', '')),
            'language': str(row.get('language', 'English')),
        })

    return jsonify({'movies': movies_list, 'total': len(movies_list)})

# =============================================================================
# ROUTE: SYSTEM STATS
# =============================================================================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics for the dashboard."""
    movies_df = get_movies_df()
    ratings_df = get_ratings_df()

    all_genres = []
    if not movies_df.empty and 'genres' in movies_df.columns:
        for genres_str in movies_df['genres'].dropna():
            all_genres.extend(genres_str.split('|'))

    genre_counts = pd.Series(all_genres).value_counts().head(10).to_dict()

    stats = {
        'total_movies': len(movies_df) if not movies_df.empty else 0,
        'total_ratings': len(ratings_df) if not ratings_df.empty else 0,
        'total_users': int(ratings_df['userId'].nunique()) if not ratings_df.empty else 0,
        'avg_rating': float(round(ratings_df['rating'].mean(), 2)) if not ratings_df.empty else 0,
        'top_genres': genre_counts,
        'models_loaded': len(ml_models),
        'system_config': ml_models.get('system_config', {})
    }

    return jsonify(stats)

# =============================================================================
# ROUTE: DETECT MOOD (standalone endpoint)
# =============================================================================

@app.route('/api/detect_mood', methods=['POST'])
def detect_mood():
    """Detect mood from text without requiring authentication."""
    data = request.get_json() or {}
    text = data.get('text', '').strip()

    if not text:
        return jsonify({'error': 'text is required'}), 400

    if 'mood_classifier' not in ml_models:
        return jsonify({'error': 'Mood model not loaded'}), 500

    clean = clean_text_for_ml(text, expand_contractions=False)
    vector = ml_models['mood_tfidf'].transform([clean])
    mood_class = int(ml_models['mood_classifier'].predict(vector)[0])
    mood_decode = ml_models.get('mood_label_decode', {0: 'happy', 1: 'sad', 2: 'excited', 3: 'bored', 4: 'stressed'})
    detected_mood = mood_decode.get(mood_class, 'happy')

    mood_genre_map = ml_models.get('mood_genre_map', {})
    genres = mood_genre_map.get(detected_mood, {}).get('genres', [])
    description = mood_genre_map.get(detected_mood, {}).get('description', '')

    probabilities = []
    if hasattr(ml_models['mood_classifier'], 'predict_proba'):
        proba = ml_models['mood_classifier'].predict_proba(vector)[0]
        confidence = float(max(proba) * 100)
    else:
        confidence = 100.0

    return jsonify({
        'mood': detected_mood,
        'confidence': round(confidence, 1),
        'recommended_genres': genres,
        'message': description
    })

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(422)
def unprocessable(e):
    return jsonify({'error': 'Invalid request data'}), 422

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    print(f"\n{'='*50}")
    print(f"  🎬 CineMatch API Server")
    print(f"  Running on http://localhost:{port}")
    print(f"  Debug mode: {debug}")
    print(f"{'='*50}\n")

    app.run(host='0.0.0.0', port=port, debug=debug)