import os
import pickle

from recommender import CineMatchRecommender

ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
ARTIFACT_PATH = os.path.join(ARTIFACT_DIR, "cinematch_model.pkl")


def main():
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    print("Fitting CineMatchRecommender...")
    model = CineMatchRecommender().fit()

    with open(ARTIFACT_PATH, "wb") as f:
        pickle.dump(model, f)

    print(f"Saved {ARTIFACT_PATH}")
    print(f"  catalog size:  {len(model.catalog)}")
    print(f"  rated movies:  {len(model.ml_ids)}")
    print(f"  ratings rows:  {len(model.ratings)}")


if __name__ == "__main__":
    main()