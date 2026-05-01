# =============================================================================
# MODULE 5: SENTIMENT ANALYSIS (HUGGING FACE TRANSFORMERS)
# =============================================================================
# This module uses a pre-trained Transformer (Deep Learning) model to 
# analyze sentiment. Unlike TF-IDF, it understands context, sarcasm, and
# meaning without relying on a preset vocabulary of words.
# =============================================================================

import os
import json
from transformers import pipeline

print("=" * 60)
print("  MODULE 5: Sentiment Analysis (Hugging Face)")
print("=" * 60)

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

print("\n[INFO] Loading pre-trained Hugging Face Transformer...")
# We use a robust, pre-trained sentiment model for 3 classes
model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"

try:
    sentiment_pipeline = pipeline("sentiment-analysis", model=model_name, tokenizer=model_name)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    exit(1)

print("\n[INFO] Testing with sample reviews...")
test_reviews = [
    "This movie was absolutely incredible! Best film of the decade.",
    "Terrible script, boring pace, and wooden acting. Waste of time.",
    "It was okay. Some good scenes but not particularly memorable.",
    "Don't watch this, it's a complete disaster from start to finish.",
    "A brilliant and thought-provoking masterpiece of cinema.",
    "The movie had potential but did not fully deliver.",
    "I cannot believe how bad this was. An insult to the viewer.",
    "Not the worst movie ever made, but definitely not good.",
    "I wanted to love this but it just did not work for me.",
]

def map_sentiment(label):
    label = label.lower()
    if label == "positive" or label == "label_2":
        return "positive"
    elif label == "neutral" or label == "label_1":
        return "neutral"
    else:
        return "negative"

results = sentiment_pipeline(test_reviews)

for review, result in zip(test_reviews, results):
    mapped_label = map_sentiment(result['label'])
    confidence = result['score'] * 100
    emoji = {'positive': '😊', 'neutral': '😐', 'negative': '😞'}[mapped_label]
    
    print(f"\n  Review: '{review}'")
    print(f"  → {emoji} {mapped_label.upper()} ({confidence:.1f}% confidence)")

# Save a config file so the backend knows what model to load
config_path = os.path.join(MODELS_DIR, 'sentiment_hf_config.json')
with open(config_path, 'w') as f:
    json.dump({
        "model_name": model_name,
        "is_huggingface": True
    }, f)

print(f"\n[INFO] Saved config to {config_path}")
print("✅ Module 5 Complete: Sentiment Classifier now uses Hugging Face Transformers!")