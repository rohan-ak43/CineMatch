#!/usr/bin/env python3
# =============================================================================
# MASTER TRAINER — Run this file to train ALL ML models at once
# =============================================================================
# Usage:  python train_all.py
#
# This runs all 6 ML modules in order:
#   1. Content-Based Recommender
#   2. Collaborative Filtering
#   3. Mood Classifier
#   4. Rating Predictor
#   5. Sentiment Analyzer
#   6. Hybrid Recommender
#
# All models are saved to the models/ folder.
# Run time: ~2-5 minutes depending on your machine.
# =============================================================================

import subprocess
import sys
import os
import time

# Make sure we're running from the project root
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("\n" + "🎬 " * 20)
print("\n  CineMatch — Movie Recommendation System")
print("  Master Training Script")
print("\n" + "🎬 " * 20)

modules = [
    ("C:\\Users\\Rohan\\Documents\\Movie-Recommendation-System\\Cinematch\\ml\\01_content_based_recommender.py", "Content-Based Recommender"),
    ("C:\\Users\\Rohan\\Documents\\Movie-Recommendation-System\\Cinematch\\ml\\02_collaborative_filtering.py",   "Collaborative Filtering (KNN)"),
    ("C:\\Users\\Rohan\\Documents\\Movie-Recommendation-System\\Cinematch\\ml\\03_mood_classifier.py",           "Mood Classifier (NLP)"),
    ("C:\\Users\\Rohan\\Documents\\Movie-Recommendation-System\\Cinematch\\ml\\04_rating_predictor.py",          "Rating Predictor (Random Forest)"),
    ("C:\\Users\\Rohan\\Documents\\Movie-Recommendation-System\\Cinematch\\ml\\05_sentiment_analysis.py",        "Sentiment Analyzer"),
    ("C:\\Users\\Rohan\\Documents\\Movie-Recommendation-System\\Cinematch\\ml\\06_hybrid_recommender.py",        "Hybrid Recommender + Visualizations"),
]

results = []

for i, (script_path, module_name) in enumerate(modules, 1):
    print(f"\n{'='*60}")
    print(f"  [{i}/{len(modules)}] Training: {module_name}")
    print(f"{'='*60}\n")

    start_time = time.time()

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=False,
            text=True,
            timeout=300  # 5 minute timeout per module
        )
        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"\n✅ {module_name} — DONE ({elapsed:.1f}s)")
            results.append((module_name, '✅ SUCCESS', elapsed))
        else:
            print(f"\n❌ {module_name} — FAILED")
            results.append((module_name, '❌ FAILED', elapsed))

    except subprocess.TimeoutExpired:
        print(f"\n⏱️ {module_name} — TIMEOUT (>5min)")
        results.append((module_name, '⏱️ TIMEOUT', 300))
    except Exception as e:
        print(f"\n💥 {module_name} — ERROR: {e}")
        results.append((module_name, f'💥 ERROR', 0))

# Summary
print("\n\n" + "=" * 60)
print("  TRAINING SUMMARY")
print("=" * 60)
for module_name, status, elapsed in results:
    print(f"  {status}  {module_name:<40} {elapsed:.1f}s")

total_time = sum(t for _, _, t in results)
print(f"\n  Total training time: {total_time:.1f}s ({total_time/60:.1f} min)")

all_success = all('SUCCESS' in s for _, s, _ in results)

if all_success:
    print("\n✅ ALL MODELS TRAINED SUCCESSFULLY!")
    print("\nNext steps:")
    print("  1. Set up MySQL: mysql -u root -p < backend/schema.sql")
    print("  2. Start Flask:  cd backend && python app.py")
    print("  3. Open:         http://localhost:5000")
else:
    print("\n⚠️  Some modules failed. Check error messages above.")
    print("    Common fixes:")
    print("    - pip install -r requirements.txt")
    print("    - Check that data/ folder has movies.csv and ratings.csv")