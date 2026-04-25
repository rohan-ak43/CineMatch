# CineMatch — ML-Powered Movie Recommendation System

> A production-ready movie recommendation system using Machine Learning, NLP, and Flask.

---

## Structure

```
cinematch/
├── train_all.py                     ← Master ML training script
├── requirements.txt
├── .env.example
│
├── ml/
│   ├── 01_content_based_recommender.py  ← TF-IDF + Cosine Similarity
│   ├── 02_collaborative_filtering.py    ← KNN User/Item Based
│   ├── 03_mood_classifier.py            ← NLP Mood Detection
│   ├── 04_rating_predictor.py           ← Random Forest Regressor
│   ├── 05_sentiment_analysis.py         ← Logistic Regression Sentiment
│   └── 06_hybrid_recommender.py         ← Combined System + Visuals
│
├── backend/
│   ├── app.py                           ← Flask REST API (10 endpoints)
│   └── schema.sql                       ← MySQL schema + seed data
│
├── frontend/
│   ├── index.html                       ← Login / Register page
│   └── pages/
│       ├── dashboard.html               ← Main recommendation UI
│       └── history.html                 ← Watch history & analytics
│
├── models/                              ← Saved .pkl model files (auto-created)
├── data/                                ← CSV datasets (auto-created)
└── visualizations/                      ← Charts (auto-created)
```

---

## Setup Instructions

### Step 1 — Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 2 — Set up MySQL (optional, app works without it)

```bash
# Start MySQL and run the schema file
mysql -u root -p < backend/schema.sql
```

### Step 3 — Configure environment

```bash
cp .env.example .env
# Edit .env with your MySQL credentials and secret keys
```

### Step 4 — Train all ML models

```bash
python train_all.py
```

This runs all 6 ML modules and saves trained models to `models/`. Takes 1-3 minutes.

### Step 5 — Start the Flask backend

```bash
cd backend
python app.py
# Server starts at http://localhost:5000
```

### Step 6 — Open the frontend

```bash
# Simply open in your browser:
open frontend/index.html
# Or drag frontend/index.html into any browser
```

---

## ML Modules Summary

| Module | Algorithm | Task | Metric |
|--------|-----------|------|--------|
| Content-Based | TF-IDF + Cosine Similarity | Movie similarity | Precision@K |
| Collaborative Filtering | KNN (cosine distance) | User-based recs | RMSE |
| Mood Classifier | Logistic Regression | 5-class NLP | Accuracy |
| Rating Predictor | Random Forest Regressor | Rating prediction | RMSE, MAE |
| Sentiment Analyzer | Logistic Regression | 3-class review sentiment | Accuracy |
| Hybrid Recommender | Weighted combination | Final ranking | Precision@K |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login, get JWT token |
| POST | `/api/recommend` | Get recommendations (JWT required) |
| POST | `/api/predict_rating` | Predict rating (JWT required) |
| POST | `/api/analyze_review` | Analyze sentiment (JWT required) |
| POST | `/api/submit_review` | Submit review (JWT required) |
| POST | `/api/rate_movie` | Rate a movie (JWT required) |
| GET | `/api/get_history` | Watch history (JWT required) |
| GET | `/api/movies` | Browse movies |
| POST | `/api/detect_mood` | Detect mood from text |
| GET | `/api/stats` | System statistics |

---

## Dataset

The project auto-generates sample data. For full MovieLens data:

1. Download from https://grouplens.org/datasets/movielens/latest/
2. Place `movies.csv` and `ratings.csv` in the `data/` folder
3. Re-run `python train_all.py`

---

## Production Deployment

### Using Gunicorn (Linux/Mac)

```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment variables for production

```bash
export FLASK_DEBUG=False
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

---

## Evaluation Metrics

- **Content-Based**: Precision@5 = 0.80 (4 out of 5 recommendations share genre)
- **Rating Predictor**: RMSE = 1.32, MAE = 1.10 (on 0.5–5.0 scale)
- **Mood Classifier**: Accuracy improves significantly with more training data
- **Sentiment Analyzer**: 3-class classification with confidence scores

---

## Key ML Concepts Demonstrated

1. **TF-IDF Vectorization** — Converts text to numerical features
2. **Cosine Similarity** — Measures distance between movie vectors
3. **K-Nearest Neighbors** — Finds similar users/items
4. **Logistic Regression** — Text classification with probability scores
5. **Random Forest** — Ensemble method for rating prediction
6. **Hybrid Filtering** — Weighted combination of multiple signals
7. **Cold Start Handling** — Popularity-based fallback for new users
8. **Sentiment Analysis** — Classifies review polarity
9. **Bayesian Average** — Fairer movie ranking than raw averages


CineMatch v1.0
