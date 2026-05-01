from ml.funcs import (
    predict as predict_fn,
    matchup_bundle as matchup_bundle_fn,
    load_model,
)


def predict_matchup(player1_key: str, player2_key: str):
    return predict_fn(player1_key, player2_key)


def get_matchup_bundle(player1_key: str, player2_key: str):
    return matchup_bundle_fn(player1_key, player2_key)


def ensure_model_loaded():
    return load_model()
