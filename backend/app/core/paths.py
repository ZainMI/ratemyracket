from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
ML_DIR = BASE_DIR / "ml"
DATA_DIR = ML_DIR / "data"
MODEL_DIR = ML_DIR / "models" / "catboost" / "artifacts" / "predictor_package"
