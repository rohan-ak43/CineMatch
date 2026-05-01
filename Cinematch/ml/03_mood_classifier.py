# =============================================================================
# MODULE 3: MOOD-BASED RECOMMENDATION (NLP)
# =============================================================================
# How it works:
#   - User types how they feel: "I'm feeling anxious and restless"
#   - We train a Logistic Regression classifier on labeled mood data
#   - The model classifies text into: happy, sad, excited, bored, stressed
#   - We then map that mood to appropriate movie genres
#   - Those genres filter our movie database for recommendations
#
# This is essentially a TEXT CLASSIFICATION task using NLP.
# =============================================================================

import pandas as pd
import numpy as np
import os
import pickle
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend (for server environments)
import matplotlib.pyplot as plt
import seaborn as sns

print("=" * 60)
print("  MODULE 3: Mood-Based Recommendation (NLP)")
print("=" * 60)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# STEP 1: CREATE MOOD TRAINING DATASET
# -----------------------------------------------------------------------------
# We need labeled examples: (text, mood_label)
# In a real project, this would come from user surveys or existing datasets
# like GoEmotions or ISEAR.
# Here we create a comprehensive synthetic dataset.
# -----------------------------------------------------------------------------

print("\n[STEP 1] Creating Mood Training Dataset...")

mood_data = {
    'text': [
        # HAPPY
        "I feel great and joyful today", "Everything is wonderful and beautiful",
        "I'm so happy and excited about life", "Feeling cheerful and positive",
        "Life is amazing and I love everything", "I feel blessed and grateful",
        "Today is a fantastic day full of joy", "I'm in a great mood and loving it",
        "Feeling ecstatic and full of energy", "I feel delighted and content",
        "Everything is going perfectly for me", "I'm feeling wonderful and upbeat",
        "So much happiness and love today", "Feeling on top of the world",
        "I'm beaming with joy and optimism", "Life feels beautiful and bright",
        "feeling good", "I'm in a great mood", "today was awesome", "couldn't be happier",
        "I am so happy", "feeling fantastic", "pretty good", "doing well", "had a great day",
        "I'm feeling very positive", "cheerful", "upbeat", "in high spirits", "feeling lucky",
        "everything is going my way", "feeling joyful", "content with life", "smiles all around",
        "feeling sunny", "great day", "feeling jolly", "jolly good time", "merry and bright", "gleeful",

        # SAD
        "I feel sad and lonely today", "Everything feels hopeless and gloomy",
        "I'm depressed and crying", "Feeling heartbroken and miserable",
        "Nothing seems to matter anymore", "I feel empty and lost inside",
        "Today is really painful and hard", "I'm feeling down and blue",
        "Tears won't stop and I'm grieving", "I feel melancholic and sorrowful",
        "The world feels dark and sad", "I miss someone and feel lonely",
        "Feeling devastated and broken hearted", "So much pain and sadness",
        "I can't stop feeling sorry and sad", "Overwhelmed with grief and sorrow",
        "feeling down", "I'm sad", "feeling miserable", "kind of depressed",
        "I'm feeling gloomy", "crying right now", "feeling heartbroken", "upset",
        "not having a good day", "feeling low", "sad and lonely", "feeling terrible",
        "everything sucks", "I feel empty", "feeling blue", "in a bad mood",
        "feeling sorrowful", "very unhappy", "so sad", "feeling awful",
        "feeling downcast", "despondent", "weeping", "tearful",

        # EXCITED
        "I'm so pumped and thrilled today", "Can't wait for this adventure to start",
        "Feeling hyped and energetic right now", "So stoked and enthusiastic about everything",
        "I'm buzzing with excitement and energy", "This is so thrilling and amazing",
        "Feeling adrenaline rushing through me", "I'm on fire and ready to go",
        "So passionate and fired up about this", "Electric excitement running through me",
        "I'm psyched and raring to go", "This feels exhilarating and intense",
        "Feeling totally wired and excited", "Can barely contain my excitement",
        "I feel alive and turbocharged", "Maximum energy and enthusiasm today",
        "I'm pumped", "so excited", "thrilled", "can't wait", "hyped up",
        "feeling energetic", "ready for action", "super excited", "stoked",
        "feeling adventurous", "amped up", "really looking forward to it",
        "feeling wild", "full of energy", "raring to go", "adrenaline is pumping",
        "I'm eager", "exhilarated", "feeling electric", "buzzing",
        "mind-blowing", "heart is racing", "super hyped", "exhilarating",

        # BORED
        "I'm bored and have nothing to do", "Everything feels dull and monotonous",
        "Feeling uninterested and zoned out", "Nothing excites me right now",
        "I'm restless and tired of routine", "Everything seems pointless and boring",
        "I just want something different to do", "Feeling sluggish and unstimulated",
        "So bored of the same old things", "Life feels flat and uninteresting",
        "I'm vegetating and wasting time", "Nothing captures my attention today",
        "Feeling lethargic and unengaged", "Same old boring day again",
        "I need something to entertain me", "Completely indifferent to everything",
        "bored out of my mind", "nothing to do", "feeling meh", "boredom",
        "yawn", "so bored", "uninterested", "nothing is happening",
        "need entertainment", "wish I had something to do", "feeling dull",
        "tired of waiting", "staring at the wall", "bored silly", "I'm just bored",
        "not much going on", "bland day", "feeling uninspired", "need a distraction", "killing time",
        "monotonous", "tedious", "nothing to do here", "yawning",

        # STRESSED
        "I feel so stressed and overwhelmed", "Everything is too much to handle",
        "I'm anxious and worried about everything", "Pressure is crushing me right now",
        "I feel burned out and exhausted", "Too much work and not enough time",
        "I'm panicking and can't calm down", "My mind won't stop racing with worries",
        "Feeling tense and under pressure", "I'm freaking out about everything",
        "So much anxiety and stress today", "I feel frantic and overwhelmed",
        "Can't relax because I'm too stressed", "Nervous and on edge about everything",
        "I'm tightly wound and stressed out", "Feeling frazzled and burnt out",
        "feeling stressed out", "too much pressure", "anxious", "worried",
        "feeling overwhelmed", "I'm tense", "freaking out", "so much to do",
        "stressed", "feeling panicked", "can't relax", "mind is racing",
        "feeling nervous", "under a lot of stress", "having a panic attack",
        "losing my mind", "feeling strained", "exhausted from stress", "feeling jittery", "stressed and tired",
        "panic", "sweating", "overworked", "can't breathe",
    ],
    'mood': (
        ['happy'] * 40 +
        ['sad'] * 40 +
        ['excited'] * 40 +
        ['bored'] * 40 +
        ['stressed'] * 40
    )
}

mood_df = pd.DataFrame(mood_data)
print(f"[INFO] Mood dataset created: {len(mood_df)} samples")
print(mood_df['mood'].value_counts())

# -----------------------------------------------------------------------------
# STEP 2: TEXT PREPROCESSING
# -----------------------------------------------------------------------------
# Clean the text before vectorizing:
#   - Convert to lowercase
#   - Remove punctuation and numbers
#   - Extra whitespace removal
# Note: We DON'T remove stop words here because "not happy" ≠ "happy"
# -----------------------------------------------------------------------------

print("\n[STEP 2] Preprocessing text...")

# Convert to lowercase
mood_df['text_clean'] = mood_df['text'].str.lower()

# Remove punctuation and special characters (keep only letters and spaces)
mood_df['text_clean'] = mood_df['text_clean'].apply(
    lambda x: re.sub(r'[^a-z\s]', '', x)
)

# Remove extra whitespace
mood_df['text_clean'] = mood_df['text_clean'].apply(
    lambda x: re.sub(r'\s+', ' ', x).strip()
)

print("[INFO] Sample cleaned text:")
print(mood_df[['text', 'text_clean']].head(3).to_string())

# -----------------------------------------------------------------------------
# STEP 3: ENCODE MOOD LABELS
# -----------------------------------------------------------------------------
# Machine learning models need numbers, not text labels.
# We create a mapping: happy=0, sad=1, excited=2, bored=3, stressed=4
# -----------------------------------------------------------------------------

print("\n[STEP 3] Encoding mood labels...")

# Define label mapping
mood_label_map = {
    'happy': 0,
    'sad': 1,
    'excited': 2,
    'bored': 3,
    'stressed': 4
}

# Reverse mapping for decoding predictions later
mood_label_decode = {v: k for k, v in mood_label_map.items()}

# Apply encoding
mood_df['mood_encoded'] = mood_df['mood'].map(mood_label_map)

print(f"[INFO] Label mapping: {mood_label_map}")

# -----------------------------------------------------------------------------
# STEP 4: SPLIT INTO TRAIN AND TEST SETS
# -----------------------------------------------------------------------------
# We train on 80% of the data and test on 20%
# stratify=True ensures equal distribution of mood labels in both sets
# -----------------------------------------------------------------------------

print("\n[STEP 4] Splitting data (80% train, 20% test)...")

X = mood_df['text_clean']           # Features (text)
y = mood_df['mood_encoded']          # Labels (mood numbers)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,      # 20% for testing
    random_state=42,    # For reproducibility
    stratify=y          # Keep equal mood distribution
)

print(f"[INFO] Training samples: {len(X_train)}")
print(f"[INFO] Test samples:     {len(X_test)}")

# -----------------------------------------------------------------------------
# STEP 5: TF-IDF VECTORIZATION (for mood text)
# -----------------------------------------------------------------------------
# Different from Module 1: here we DON'T remove stop words
# because "not excited" means something different from "excited"
# -----------------------------------------------------------------------------

print("\n[STEP 5] Vectorizing text with TF-IDF...")

mood_tfidf = TfidfVectorizer(
    max_features=2000,      # Vocabulary size limit
    ngram_range=(1, 3),     # Use 1, 2, and 3-word phrases
    sublinear_tf=True       # Apply log normalization to TF (reduces impact of very common words)
)

# Fit on training data only (prevent data leakage)
X_train_tfidf = mood_tfidf.fit_transform(X_train)

# Transform test data using the SAME vocabulary learned from training
X_test_tfidf = mood_tfidf.transform(X_test)

print(f"[INFO] Train TF-IDF shape: {X_train_tfidf.shape}")
print(f"[INFO] Test TF-IDF shape:  {X_test_tfidf.shape}")

# -----------------------------------------------------------------------------
# STEP 6: TRAIN LOGISTIC REGRESSION MODEL
# -----------------------------------------------------------------------------
# Logistic Regression works well for text classification because:
# - It gives probability scores for each class (useful!)
# - It's fast and interpretable
# - It handles high-dimensional TF-IDF vectors well
#
# : handles 5 classes (not just binary)
# C=1.0: regularization strength (prevents overfitting)
# -----------------------------------------------------------------------------

print("\n[STEP 6] Training Logistic Regression Mood Classifier...")

lr_model = LogisticRegression(
      # 5-class problem
    solver='lbfgs',             # Optimization algorithm
    C=1.0,                      # Regularization (lower = more regularization)
    max_iter=1000,              # Max iterations for convergence
    random_state=42
)

lr_model.fit(X_train_tfidf, y_train)

# Predict on test set
y_pred_lr = lr_model.predict(X_test_tfidf)
accuracy_lr = accuracy_score(y_test, y_pred_lr)

print(f"\n[INFO] Logistic Regression Accuracy: {accuracy_lr:.4f} ({accuracy_lr*100:.1f}%)")
print("\n[INFO] Detailed Classification Report:")
print(classification_report(
    y_test, y_pred_lr,
    target_names=list(mood_label_map.keys())
))

# -----------------------------------------------------------------------------
# STEP 7: COMPARE WITH NAIVE BAYES
# -----------------------------------------------------------------------------
# Naive Bayes is another classic text classifier.
# We compare to pick the best model.
# -----------------------------------------------------------------------------

print("\n[STEP 7] Comparing with Naive Bayes...")

# Note: MultinomialNB requires NON-NEGATIVE values
# TF-IDF produces non-negative values, so it's fine
nb_model = MultinomialNB(alpha=0.1)  # alpha is smoothing parameter

# MultinomialNB needs non-negative dense features
from sklearn.preprocessing import MinMaxScaler
# Use Complement Naive Bayes instead — works better with TF-IDF
from sklearn.naive_bayes import ComplementNB

cnb_model = ComplementNB(alpha=0.1)
cnb_model.fit(X_train_tfidf, y_train)
y_pred_cnb = cnb_model.predict(X_test_tfidf)
accuracy_cnb = accuracy_score(y_test, y_pred_cnb)

print(f"[INFO] Complement Naive Bayes Accuracy: {accuracy_cnb:.4f} ({accuracy_cnb*100:.1f}%)")
print(f"[INFO] Logistic Regression Accuracy:    {accuracy_lr:.4f} ({accuracy_lr*100:.1f}%)")

# Pick the better model
if accuracy_lr >= accuracy_cnb:
    best_model = lr_model
    best_model_name = "Logistic Regression"
    best_accuracy = accuracy_lr
else:
    best_model = cnb_model
    best_model_name = "Complement Naive Bayes"
    best_accuracy = accuracy_cnb

print(f"\n✅ Best Model: {best_model_name} (Accuracy: {best_accuracy*100:.1f}%)")

# -----------------------------------------------------------------------------
# STEP 8: CONFUSION MATRIX VISUALIZATION
# -----------------------------------------------------------------------------

print("\n[STEP 8] Generating Confusion Matrix...")

y_pred_best = best_model.predict(X_test_tfidf)
cm = confusion_matrix(y_test, y_pred_best)

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    xticklabels=list(mood_label_map.keys()),
    yticklabels=list(mood_label_map.keys()),
    ax=ax
)
ax.set_xlabel('Predicted Mood')
ax.set_ylabel('Actual Mood')
ax.set_title(f'Mood Classifier Confusion Matrix\n({best_model_name}, Accuracy={best_accuracy*100:.1f}%)')
plt.tight_layout()

viz_dir = os.path.join(os.path.dirname(__file__), '..', 'visualizations')
os.makedirs(viz_dir, exist_ok=True)
plt.savefig(os.path.join(viz_dir, 'mood_confusion_matrix.png'), dpi=150)
plt.close()
print(f"[INFO] Saved confusion matrix to visualizations/mood_confusion_matrix.png")

# -----------------------------------------------------------------------------
# STEP 9: MOOD → GENRE MAPPING + RECOMMENDATION FILTER
# -----------------------------------------------------------------------------
# Map detected mood to movie genres.
# This is our "business logic" — you can customize this mapping!
# -----------------------------------------------------------------------------

print("\n[STEP 9] Defining Mood → Genre Mapping...")

MOOD_GENRE_MAP = {
    'happy': {
        'genres': ['Comedy', 'Family', 'Animation', 'Music', 'Romance'],
        'description': 'Light-hearted and fun movies to keep the good vibes going!'
    },
    'sad': {
        'genres': ['Drama', 'Romance', 'Family', 'Animation', 'Musical'],
        'description': 'Heartwarming movies to comfort and uplift your spirits.'
    },
    'excited': {
        'genres': ['Action', 'Thriller', 'Adventure', 'Sci-Fi', 'Fantasy'],
        'description': 'High-energy movies to match your excitement!'
    },
    'bored': {
        'genres': ['Comedy', 'Adventure', 'Fantasy', 'Mystery', 'Animation'],
        'description': 'Engaging movies to cure your boredom!'
    },
    'stressed': {
        'genres': ['Comedy', 'Animation', 'Family', 'Musical', 'Documentary'],
        'description': 'Relaxing and soothing movies to help you unwind.'
    }
}

print("[INFO] Mood-to-Genre Mapping:")
for mood, info in MOOD_GENRE_MAP.items():
    print(f"  {mood.upper()}: {' | '.join(info['genres'])}")

# -----------------------------------------------------------------------------
# STEP 10: TEST WITH SAMPLE USER INPUTS
# -----------------------------------------------------------------------------

print("\n[STEP 10] Testing with sample user inputs...")

test_inputs = [
    "I had a terrible day and I feel really sad",
    "So pumped up and ready for action!",
    "Nothing to do, completely bored",
    "I'm stressed with deadlines and anxious",
    "Feeling happy and full of joy today"
]

print("\n[RESULTS] Mood Detection Results:")
print("-" * 60)

for user_text in test_inputs:
    # Clean the text
    clean_text = user_text.lower()
    clean_text = re.sub(r'[^a-z\s]', '', clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    # Vectorize
    text_vector = mood_tfidf.transform([clean_text])

    # Predict mood
    predicted_class = best_model.predict(text_vector)[0]
    predicted_mood = mood_label_decode[predicted_class]

    # Get confidence probabilities (only available for LR)
    if hasattr(best_model, 'predict_proba'):
        probabilities = best_model.predict_proba(text_vector)[0]
        confidence = max(probabilities) * 100
    else:
        confidence = 100.0  # CNB doesn't provide calibrated probabilities

    # Get recommended genres
    recommended_genres = MOOD_GENRE_MAP[predicted_mood]['genres']
    description = MOOD_GENRE_MAP[predicted_mood]['description']

    print(f"\n  Input:      '{user_text}'")
    print(f"  Mood:       {predicted_mood.upper()} ({confidence:.1f}% confidence)")
    print(f"  Genres:     {', '.join(recommended_genres)}")
    print(f"  Message:    {description}")

# -----------------------------------------------------------------------------
# STEP 11: SAVE MODELS
# -----------------------------------------------------------------------------

print("\n[STEP 11] Saving mood classifier models...")

with open(os.path.join(MODELS_DIR, 'mood_classifier.pkl'), 'wb') as f:
    pickle.dump(best_model, f)

with open(os.path.join(MODELS_DIR, 'mood_tfidf.pkl'), 'wb') as f:
    pickle.dump(mood_tfidf, f)

with open(os.path.join(MODELS_DIR, 'mood_label_map.pkl'), 'wb') as f:
    pickle.dump(mood_label_map, f)

with open(os.path.join(MODELS_DIR, 'mood_label_decode.pkl'), 'wb') as f:
    pickle.dump(mood_label_decode, f)

with open(os.path.join(MODELS_DIR, 'mood_genre_map.pkl'), 'wb') as f:
    pickle.dump(MOOD_GENRE_MAP, f)

print("[INFO] Saved: models/mood_classifier.pkl")
print("[INFO] Saved: models/mood_tfidf.pkl")
print("[INFO] Saved: models/mood_label_map.pkl")
print("[INFO] Saved: models/mood_genre_map.pkl")

print(f"\n✅ Module 3 Complete: Mood Classifier trained with {best_accuracy*100:.1f}% accuracy!")