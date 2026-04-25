# =============================================================================
# MODULE 5: SENTIMENT ANALYSIS ON MOVIE REVIEWS
# =============================================================================
# How it works:
#   - User writes a review: "Absolutely loved it, incredible story!"
#   - We classify the review as POSITIVE, NEGATIVE, or NEUTRAL
#   - Steps:
#     1. Clean the text (remove punctuation, stopwords)
#     2. Convert to TF-IDF numbers
#     3. Logistic Regression predicts the sentiment
#
# This is similar to Module 3 but for review text instead of mood text.
# Reviews have more complex language (sarcasm, negations, etc.)
# =============================================================================

import pandas as pd
import numpy as np
import os
import pickle
import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (accuracy_score, classification_report,
                              confusion_matrix, roc_auc_score)
from sklearn.preprocessing import label_binarize
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

print("=" * 60)
print("  MODULE 5: Sentiment Analysis on Movie Reviews")
print("=" * 60)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
VIZ_DIR = os.path.join(os.path.dirname(__file__), '..', 'visualizations')
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(VIZ_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# STEP 1: CREATE REVIEW TRAINING DATASET
# -----------------------------------------------------------------------------
# In production, you'd use:
# - IMDB 50K Movie Reviews dataset (https://www.kaggle.com/datasets/lakshmi25npsuresh/imdb-dataset-of-50k-movie-reviews)
# - Rotten Tomatoes dataset
#
# Here we create a comprehensive synthetic dataset covering:
# - Clear positive reviews
# - Clear negative reviews
# - Neutral/mixed reviews (harder to classify)
# - Tricky cases (negations, sarcasm markers)
# -----------------------------------------------------------------------------

print("\n[STEP 1] Creating Review Training Dataset...")

reviews_data = {
    'review': [
        # ===== POSITIVE REVIEWS =====
        "This movie was absolutely fantastic! The story was compelling and the acting was superb.",
        "One of the best films I have ever seen. Masterpiece of modern cinema.",
        "Incredible performances from the entire cast. Highly recommended!",
        "A beautiful and touching story that moved me to tears. Loved every minute.",
        "Brilliant direction and stunning visuals. A must-watch for everyone.",
        "The plot twists kept me on the edge of my seat throughout.",
        "Exceptional filmmaking at its finest. Perfect pacing and great characters.",
        "I was completely captivated from start to finish. Outstanding!",
        "A wonderful blend of drama and humor that works perfectly together.",
        "The cinematography is breathtaking and the score is mesmerizing.",
        "Absolutely loved this film. Exceeded all my expectations.",
        "Heartwarming and inspiring story that will stay with you for days.",
        "A true cinematic gem. The writing is sharp and the acting is flawless.",
        "Deeply moving and emotionally resonant. Best movie of the year.",
        "Funny, touching, and thought-provoking. A perfect film.",
        "The chemistry between the leads is electric. Phenomenal movie.",
        "Gripping from beginning to end. The best thriller I have seen in years.",
        "Beautifully crafted with incredible attention to detail.",
        "A spectacular achievement in storytelling. Simply outstanding.",
        "This deserves every award it gets. An absolute triumph.",

        # ===== NEGATIVE REVIEWS =====
        "Terrible movie. Boring plot and terrible acting. Wasted two hours of my life.",
        "Complete disaster. The story made no sense and the characters were annoying.",
        "One of the worst movies I have ever seen. Avoid at all costs.",
        "Awful cinematography and a nonsensical plot. Very disappointing.",
        "The acting was wooden and the dialogue was cringe-worthy throughout.",
        "A complete waste of money and time. Nothing redeemable about this film.",
        "Painfully slow and utterly boring. Could not wait for it to end.",
        "The script is a mess and the plot holes are enormous.",
        "Horrible characters I could not care less about. Terrible film.",
        "Appalling special effects and a generic unoriginal story.",
        "This film insults the intelligence of its audience. Dreadful.",
        "Poorly directed and poorly acted. A complete failure.",
        "The worst screenplay I have seen in years. Absolutely awful.",
        "Laughably bad visual effects and a storyline that goes nowhere.",
        "A tedious and uninspired film that bores you into submission.",
        "Dull, predictable, and forgettable. Save your money.",
        "The director clearly had no idea what they were doing.",
        "A sloppy and amateurish production that fails on every level.",
        "Excruciating to sit through. One of the year's biggest disappointments.",
        "Poorly written with zero character development. Skip this one.",

        # ===== NEUTRAL REVIEWS =====
        "The movie was okay. Some good moments but overall nothing special.",
        "Decent film with a few standout scenes but mostly forgettable.",
        "Average production value. Some scenes work, others do not.",
        "It was fine. Nothing groundbreaking but watchable enough.",
        "Had potential but the execution was mixed. Worth a single watch maybe.",
        "Some impressive moments but the overall film felt uneven.",
        "Not bad, not great. A middle-of-the-road experience.",
        "Interesting concept but the story did not fully deliver on it.",
        "Solid performances carrying a mediocre script.",
        "Enjoyable enough for a lazy afternoon but nothing memorable.",
        "A fair effort that partially succeeds but also partially disappoints.",
        "The first half is strong but the second half falls apart.",
        "Good ideas that are only partially executed well.",
        "Better than I expected but still not a great movie overall.",
        "Hits some emotional notes but the story meanders too much.",
        "Technically competent but emotionally cold.",
        "A passable film that does what you expect and nothing more.",
        "Some great individual scenes in an otherwise average movie.",
        "Not as good as the hype suggested but not terrible either.",
        "Worth watching once if you have nothing better to do.",

        # ===== TRICKY CASES (negations, mixed signals) =====
        "I did not hate this movie as much as I expected to.",
        "Not the worst movie ever made, but definitely not good.",
        "I wanted to love this but it just did not work for me.",
        "Despite the terrible trailer, the movie was surprisingly decent.",
        "The acting is great but everything else falls flat.",
        "Beautiful visuals cannot save a terrible story.",
        "Started strong but completely fell apart in the third act.",
        "I cannot believe they ruined such a promising concept.",
        "A few laughs here and there but mostly disappointing.",
        "The ending almost made up for the boring first two hours.",
    ],
    'sentiment': (
        ['positive'] * 20 +
        ['negative'] * 20 +
        ['neutral'] * 20 +
        # Tricky cases — label based on overall tone
        ['neutral', 'negative', 'negative', 'neutral', 'negative',
         'negative', 'negative', 'negative', 'negative', 'neutral']
    )
}

reviews_df = pd.DataFrame(reviews_data)
print(f"[INFO] Reviews dataset: {len(reviews_df)} samples")
print(reviews_df['sentiment'].value_counts())

# Save dataset
reviews_df.to_csv(os.path.join(DATA_DIR, 'sample_reviews.csv'), index=False)

# -----------------------------------------------------------------------------
# STEP 2: TEXT CLEANING / PREPROCESSING
# -----------------------------------------------------------------------------
# This is more thorough than Module 3 because reviews are messier text.
# We:
#   1. Lowercase everything
#   2. Expand contractions (don't → do not) — important for negations!
#   3. Remove HTML tags (in case scraped from web)
#   4. Remove punctuation
#   5. Remove extra whitespace
#
# NOTE: We do NOT remove stopwords in sentiment analysis!
# "not good" is very different from "good" — keeping "not" matters!
# -----------------------------------------------------------------------------

print("\n[STEP 2] Cleaning review text...")

# Contraction expansion dictionary (partial — in production use 'contractions' library)
CONTRACTIONS = {
    "don't": "do not", "doesn't": "does not", "didn't": "did not",
    "isn't": "is not", "wasn't": "was not", "weren't": "were not",
    "can't": "cannot", "couldn't": "could not", "shouldn't": "should not",
    "wouldn't": "would not", "won't": "will not", "haven't": "have not",
    "hasn't": "has not", "hadn't": "had not", "it's": "it is",
    "i'm": "i am", "i've": "i have", "i'd": "i would", "i'll": "i will",
    "they're": "they are", "we're": "we are", "you're": "you are",
    "he's": "he is", "she's": "she is", "that's": "that is",
    "there's": "there is", "what's": "what is", "who's": "who is",
}

def expand_contractions(text):
    """Replace contractions with full forms."""
    for contraction, expansion in CONTRACTIONS.items():
        text = text.replace(contraction, expansion)
    return text

# Apply all cleaning steps
cleaned_reviews = []
for review in reviews_df['review']:
    # Step 1: Lowercase
    text = review.lower()
    # Step 2: Expand contractions
    text = expand_contractions(text)
    # Step 3: Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Step 4: Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    # Step 5: Remove punctuation (except apostrophes already handled)
    text = re.sub(r'[^\w\s]', ' ', text)
    # Step 6: Remove digits
    text = re.sub(r'\d+', '', text)
    # Step 7: Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    cleaned_reviews.append(text)

reviews_df['review_clean'] = cleaned_reviews

print("[INFO] Sample cleaning result:")
print(f"  Original: {reviews_df['review'].iloc[0][:80]}...")
print(f"  Cleaned:  {reviews_df['review_clean'].iloc[0][:80]}...")

# -----------------------------------------------------------------------------
# STEP 3: ENCODE SENTIMENT LABELS
# -----------------------------------------------------------------------------

print("\n[STEP 3] Encoding sentiment labels...")

sentiment_map = {'positive': 2, 'neutral': 1, 'negative': 0}
sentiment_decode = {v: k for k, v in sentiment_map.items()}

reviews_df['sentiment_encoded'] = reviews_df['sentiment'].map(sentiment_map)

print(f"[INFO] Sentiment encoding: {sentiment_map}")

# -----------------------------------------------------------------------------
# STEP 4: TRAIN-TEST SPLIT
# -----------------------------------------------------------------------------

print("\n[STEP 4] Splitting data...")

X = reviews_df['review_clean']
y = reviews_df['sentiment_encoded']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"[INFO] Training: {len(X_train)} | Test: {len(X_test)}")

# -----------------------------------------------------------------------------
# STEP 5: TF-IDF VECTORIZATION
# -----------------------------------------------------------------------------
# Key settings for sentiment analysis:
# - ngram_range=(1, 3): captures "not good", "absolutely loved", etc.
# - sublinear_tf=True: reduces impact of very frequent words
# - min_df=1: include words that appear at least once (small dataset)
# -----------------------------------------------------------------------------

print("\n[STEP 5] TF-IDF Vectorization...")

sentiment_tfidf = TfidfVectorizer(
    max_features=10000,     # Large vocabulary
    ngram_range=(1, 3),     # Unigrams, bigrams, trigrams
    sublinear_tf=True,      # Apply log normalization
    min_df=1,               # Include rare words (small dataset)
    strip_accents='unicode', # Handle accented characters
    analyzer='word'         # Analyze at word level
)

X_train_tfidf = sentiment_tfidf.fit_transform(X_train)
X_test_tfidf = sentiment_tfidf.transform(X_test)

print(f"[INFO] TF-IDF Matrix: {X_train_tfidf.shape}")

# -----------------------------------------------------------------------------
# STEP 6: TRAIN LOGISTIC REGRESSION FOR SENTIMENT
# -----------------------------------------------------------------------------

print("\n[STEP 6] Training Sentiment Classifier...")

# Logistic Regression with L2 regularization
sentiment_model = LogisticRegression(
    C=1.0,              # Regularization strength
    solver='lbfgs',
      # 3-class: positive, neutral, negative
    max_iter=1000,
    random_state=42,
    class_weight='balanced'  # Handle class imbalance
)

sentiment_model.fit(X_train_tfidf, y_train)

# Evaluate on test set
y_pred = sentiment_model.predict(X_test_tfidf)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n[INFO] Sentiment Model Accuracy: {accuracy:.4f} ({accuracy*100:.1f}%)")
print("\n[INFO] Classification Report:")
print(classification_report(
    y_test, y_pred,
    target_names=['negative', 'neutral', 'positive']
))

# Cross-validation for more reliable accuracy estimate
cv_scores = cross_val_score(sentiment_model, X_train_tfidf, y_train, cv=3)
print(f"[INFO] 3-Fold Cross-Validation Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# -----------------------------------------------------------------------------
# STEP 7: ANALYZE MOST IMPORTANT WORDS PER SENTIMENT
# -----------------------------------------------------------------------------
# This is model interpretability — understanding WHAT the model learned.
# For each sentiment class, we show which words are most indicative.
# -----------------------------------------------------------------------------

print("\n[STEP 7] Most influential words per sentiment class...")

feature_names = sentiment_tfidf.get_feature_names_out()
classes = ['negative', 'neutral', 'positive']

for class_idx, class_name in enumerate(classes):
    # Get the coefficients for this class
    class_coefs = sentiment_model.coef_[class_idx]
    # Top 10 words with highest positive coefficient = most indicative
    top_positive_indices = class_coefs.argsort()[-10:][::-1]
    top_words = [feature_names[i] for i in top_positive_indices]
    print(f"\n  Top words for '{class_name.upper()}':")
    print(f"  {' | '.join(top_words)}")

# -----------------------------------------------------------------------------
# STEP 8: CONFUSION MATRIX
# -----------------------------------------------------------------------------

print("\n[STEP 8] Generating Confusion Matrix...")

cm = confusion_matrix(y_test, y_pred)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Confusion matrix heatmap
sns.heatmap(
    cm, annot=True, fmt='d',
    xticklabels=['negative', 'neutral', 'positive'],
    yticklabels=['negative', 'neutral', 'positive'],
    ax=axes[0]
)
axes[0].set_xlabel('Predicted Sentiment')
axes[0].set_ylabel('Actual Sentiment')
axes[0].set_title(f'Sentiment Confusion Matrix\n(Accuracy: {accuracy*100:.1f}%)')

# Sentiment distribution in training data
sentiment_counts = reviews_df['sentiment'].value_counts()
axes[1].bar(sentiment_counts.index, sentiment_counts.values)
axes[1].set_xlabel('Sentiment')
axes[1].set_ylabel('Count')
axes[1].set_title('Sentiment Distribution in Dataset')

plt.tight_layout()
plt.savefig(os.path.join(VIZ_DIR, 'sentiment_analysis_results.png'), dpi=150)
plt.close()
print("[INFO] Saved: visualizations/sentiment_analysis_results.png")

# -----------------------------------------------------------------------------
# STEP 9: TEST WITH SAMPLE REVIEWS
# -----------------------------------------------------------------------------

print("\n[STEP 9] Testing with sample reviews...")

test_reviews = [
    "This movie was absolutely incredible! Best film of the decade.",
    "Terrible script, boring pace, and wooden acting. Waste of time.",
    "It was okay. Some good scenes but not particularly memorable.",
    "Don't watch this, it's a complete disaster from start to finish.",
    "A brilliant and thought-provoking masterpiece of cinema.",
    "The movie had potential but did not fully deliver.",
    "I cannot believe how bad this was. An insult to the viewer.",
]

print("\n[RESULTS] Sentiment Analysis Results:")
print("-" * 65)

for review in test_reviews:
    # Clean the review
    clean = review.lower()
    clean = expand_contractions(clean)
    clean = re.sub(r'[^\w\s]', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()

    # Vectorize
    vector = sentiment_tfidf.transform([clean])

    # Predict
    predicted_class = sentiment_model.predict(vector)[0]
    predicted_sentiment = sentiment_decode[predicted_class]

    # Get probabilities
    probabilities = sentiment_model.predict_proba(vector)[0]
    confidence = max(probabilities) * 100

    # Probability for each class
    neg_prob = probabilities[0] * 100
    neu_prob = probabilities[1] * 100
    pos_prob = probabilities[2] * 100

    # Emoji indicator
    emoji = {'positive': '😊', 'neutral': '😐', 'negative': '😞'}[predicted_sentiment]

    print(f"\n  Review: '{review[:60]}...'")
    print(f"  → {emoji} {predicted_sentiment.upper()} ({confidence:.0f}% confidence)")
    print(f"     Neg: {neg_prob:.0f}% | Neu: {neu_prob:.0f}% | Pos: {pos_prob:.0f}%")

# -----------------------------------------------------------------------------
# STEP 10: SAVE MODELS
# -----------------------------------------------------------------------------

print("\n[STEP 10] Saving sentiment analysis models...")

with open(os.path.join(MODELS_DIR, 'sentiment_classifier.pkl'), 'wb') as f:
    pickle.dump(sentiment_model, f)

with open(os.path.join(MODELS_DIR, 'sentiment_tfidf.pkl'), 'wb') as f:
    pickle.dump(sentiment_tfidf, f)

with open(os.path.join(MODELS_DIR, 'sentiment_map.pkl'), 'wb') as f:
    pickle.dump({'map': sentiment_map, 'decode': sentiment_decode}, f)

# Save the contraction dict for the Flask API
import json
with open(os.path.join(MODELS_DIR, 'contractions.json'), 'w') as f:
    json.dump(CONTRACTIONS, f)

print("[INFO] Saved: models/sentiment_classifier.pkl")
print("[INFO] Saved: models/sentiment_tfidf.pkl")
print("[INFO] Saved: models/sentiment_map.pkl")
print("[INFO] Saved: models/contractions.json")

print(f"\n✅ Module 5 Complete: Sentiment Classifier trained with {accuracy*100:.1f}% accuracy!")