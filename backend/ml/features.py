# features.py

import math
import pickle
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, List

import numpy as np
import pandas as pd

SPORTS = ["TT", "BD", "SQ", "TN"]

USE_IDS = False

BASE = 0.0
MAX_DIFF = 21.0

ALPHAS = {
    "TT": 0.060,
    "BD": 0.080,
    "SQ": 0.060,
    "TN": 0.040,
}

ETA_MIN = 0.04
ETA_MAX = 0.30
ETA_TAU = 20.0
L2 = 1e-5

MARGIN_MULT_BY_SPORT = {
    "TT": 0.6,
    "BD": 0.8,
    "SQ": 0.6,
    "TN": 0.4,
}

TIME_C = {
    "TT": 0.6,
    "BD": 0.7,
    "SQ": 0.6,
    "TN": 0.5,
}

TIME_TAU_DAYS = {
    "TT": 90.0,
    "BD": 120.0,
    "SQ": 90.0,
    "TN": 120.0,
}

BLOWOUT_WIN_THRESHOLD = 10.0
BLOWOUT_LOSS_THRESHOLD = -10.0
CLOSE_MATCH_ABS_THRESHOLD = 3.0
FAVORITE_EXPECTED_DIFF_THRESHOLD = 5.0
EWM_ALPHA = 0.25
LONG_TERM_SHRINK = 10.0


def safe_datetime(df: pd.DataFrame) -> pd.Series:
    if "datetime" in df.columns:
        dt = pd.to_datetime(df["datetime"], errors="coerce")
        if dt.notna().any():
            return dt

    d = pd.to_datetime(df["match_date"], format="%Y%m%d", errors="coerce")
    if "match_time" in df.columns:
        dt = pd.to_datetime(
            d.astype(str) + " " + df["match_time"].astype(str),
            errors="coerce",
        )
        return dt.fillna(d)
    return d


def normalize_player_name(x) -> str:
    return str(x).strip().lower()


def player_country(row: pd.Series, side: int) -> str:
    country = str(row.get(f"team{side}_nationalities", "")).strip().lower()

    if country == "nan":
        return ""

    if country == "eng":
        return "gbr"

    return country


def player_key(row: pd.Series, side: int) -> str:
    name = normalize_player_name(row.get(f"team{side}_players", "unknown"))
    country = player_country(row, side)

    if not country:
        return f"name::{name}"

    return f"{name}__{country}"


def player_name(row: pd.Series, side: int) -> str:
    return normalize_player_name(row.get(f"team{side}_players", ""))


def pair_key(a: str, b: str) -> Tuple[str, str]:
    return (a, b) if a <= b else (b, a)


def get_sport_diff(row: pd.Series, sport: str) -> Optional[float]:
    a = row.get(f"{sport}_p1")
    b = row.get(f"{sport}_p2")
    if pd.isna(a) or pd.isna(b):
        return None
    return float(a) - float(b)


def get_sport_total(row: pd.Series, sport: str) -> Optional[float]:
    a = row.get(f"{sport}_p1")
    b = row.get(f"{sport}_p2")
    if pd.isna(a) or pd.isna(b):
        return None
    return float(a) + float(b)


def get_month_key(dt: pd.Timestamp) -> Optional[str]:
    if pd.isna(dt):
        return None
    return f"{dt.year:04d}-{dt.month:02d}"


def clip_diff(d: float) -> float:
    return float(np.clip(d, -MAX_DIFF, MAX_DIFF))


def rating_to_score_diff(x: float, alpha: float) -> float:
    return MAX_DIFF * math.tanh((alpha * x) / 2.0)


def d_pred_dx(x: float, alpha: float) -> float:
    t = math.tanh((alpha * x) / 2.0)
    return MAX_DIFF * (alpha / 2.0) * (1.0 - t * t)


def eta_eff(games_played: int) -> float:
    gp = max(0, int(games_played))
    return ETA_MIN + (ETA_MAX - ETA_MIN) * math.exp(-gp / ETA_TAU)


def days_since(last_dt: Optional[pd.Timestamp], dt: pd.Timestamp) -> float:
    if last_dt is None or pd.isna(last_dt) or pd.isna(dt):
        return 0.0
    return float(max(0, (dt - last_dt).days))


def time_multiplier(sport: str, gap_days: float) -> float:
    return 1.0 + TIME_C[sport] * (
        1.0 - math.exp(-gap_days / TIME_TAU_DAYS[sport])
    )


def add_prefixed(d: Dict[str, float], prefix: str) -> Dict[str, float]:
    return {f"{prefix}{k}": v for k, v in d.items()}


def add_pairwise_deltas(
    out: Dict[str, float],
    sport: str,
    p1_feats: Dict[str, float],
    p2_feats: Dict[str, float],
) -> None:
    for k in p1_feats.keys():
        out[f"{sport}_{k}_diff_p1_p2"] = float(p1_feats[k]) - float(p2_feats[k])


@dataclass
class RollingWindow:
    maxlen: int
    values: deque = field(default_factory=deque)
    sum_: float = 0.0
    sumsq_: float = 0.0

    def push(self, x: float) -> None:
        x = float(x)
        if len(self.values) == self.maxlen:
            old = self.values.popleft()
            self.sum_ -= old
            self.sumsq_ -= old * old
        self.values.append(x)
        self.sum_ += x
        self.sumsq_ += x * x

    def count(self) -> int:
        return len(self.values)

    def mean(self, default: float = 0.0) -> float:
        n = len(self.values)
        return float(self.sum_ / n) if n > 0 else float(default)

    def std(self, default: float = 0.0) -> float:
        n = len(self.values)
        if n <= 1:
            return float(default)
        mean = self.sum_ / n
        var = max(0.0, self.sumsq_ / n - mean * mean)
        return float(math.sqrt(var))


@dataclass
class PlayerSportRecentState:
    n_matches: int = 0
    last_dt: Optional[pd.Timestamp] = None

    diff5: RollingWindow = field(default_factory=lambda: RollingWindow(5))
    diff10: RollingWindow = field(default_factory=lambda: RollingWindow(10))
    diff20: RollingWindow = field(default_factory=lambda: RollingWindow(20))

    total5: RollingWindow = field(default_factory=lambda: RollingWindow(5))
    total10: RollingWindow = field(default_factory=lambda: RollingWindow(10))

    win5: RollingWindow = field(default_factory=lambda: RollingWindow(5))
    win10: RollingWindow = field(default_factory=lambda: RollingWindow(10))
    win20: RollingWindow = field(default_factory=lambda: RollingWindow(20))

    blowout_win10: RollingWindow = field(
        default_factory=lambda: RollingWindow(10)
    )
    blowout_loss10: RollingWindow = field(
        default_factory=lambda: RollingWindow(10)
    )
    close10: RollingWindow = field(default_factory=lambda: RollingWindow(10))

    resid10: RollingWindow = field(default_factory=lambda: RollingWindow(10))
    resid20: RollingWindow = field(default_factory=lambda: RollingWindow(20))
    resid_pos10: RollingWindow = field(
        default_factory=lambda: RollingWindow(10)
    )

    fav_win10: RollingWindow = field(default_factory=lambda: RollingWindow(10))
    fav_diff10: RollingWindow = field(default_factory=lambda: RollingWindow(10))
    dog_win10: RollingWindow = field(default_factory=lambda: RollingWindow(10))
    dog_diff10: RollingWindow = field(default_factory=lambda: RollingWindow(10))

    ewm_diff: float = 0.0
    ewm_initialized: bool = False


def recent_state_features(
    st: PlayerSportRecentState,
    dt: Optional[pd.Timestamp],
) -> Dict[str, float]:
    if st.last_dt is None or dt is None or pd.isna(dt):
        days_since_last_match = -1.0
    else:
        days_since_last_match = float((dt - st.last_dt).days)

    return {
        "matches_played": float(st.n_matches),
        "days_since_last_match": days_since_last_match,
        "recent_n_5": float(st.diff5.count()),
        "recent_n_10": float(st.diff10.count()),
        "recent_n_20": float(st.diff20.count()),
        "diff_mean_5": st.diff5.mean(),
        "diff_mean_10": st.diff10.mean(),
        "diff_mean_20": st.diff20.mean(),
        "diff_std_10": st.diff10.std(),
        "diff_std_20": st.diff20.std(),
        "total_mean_5": st.total5.mean(),
        "total_mean_10": st.total10.mean(),
        "total_std_10": st.total10.std(),
        "winrate_5": st.win5.mean(),
        "winrate_10": st.win10.mean(),
        "winrate_20": st.win20.mean(),
        "blowout_win_rate_10": st.blowout_win10.mean(),
        "blowout_loss_rate_10": st.blowout_loss10.mean(),
        "close_match_rate_10": st.close10.mean(),
        "resid_mean_10": st.resid10.mean(),
        "resid_mean_20": st.resid20.mean(),
        "resid_std_10": st.resid10.std(),
        "resid_pos_rate_10": st.resid_pos10.mean(),
        "ewm_diff": float(st.ewm_diff if st.ewm_initialized else 0.0),
        "momentum_diff_5_20": st.diff5.mean() - st.diff20.mean(),
        "momentum_win_5_20": st.win5.mean() - st.win20.mean(),
        "fav_count_10": float(st.fav_diff10.count()),
        "fav_winrate_10": st.fav_win10.mean(),
        "fav_diff_mean_10": st.fav_diff10.mean(),
        "dog_count_10": float(st.dog_diff10.count()),
        "dog_winrate_10": st.dog_win10.mean(),
        "dog_diff_mean_10": st.dog_diff10.mean(),
    }


def update_recent_state(
    st: PlayerSportRecentState,
    actual_diff_player_pov: float,
    actual_total: float,
    expected_diff_player_pov: float,
    dt: pd.Timestamp,
    ewm_alpha: float = EWM_ALPHA,
) -> None:
    actual_diff_player_pov = float(actual_diff_player_pov)
    actual_total = float(actual_total)
    expected_diff_player_pov = float(expected_diff_player_pov)

    residual = actual_diff_player_pov - expected_diff_player_pov
    win = 1.0 if actual_diff_player_pov > 0 else 0.0
    blowout_win = (
        1.0 if actual_diff_player_pov >= BLOWOUT_WIN_THRESHOLD else 0.0
    )
    blowout_loss = (
        1.0 if actual_diff_player_pov <= BLOWOUT_LOSS_THRESHOLD else 0.0
    )
    close_match = (
        1.0 if abs(actual_diff_player_pov) <= CLOSE_MATCH_ABS_THRESHOLD else 0.0
    )
    resid_pos = 1.0 if residual > 0 else 0.0

    st.diff5.push(actual_diff_player_pov)
    st.diff10.push(actual_diff_player_pov)
    st.diff20.push(actual_diff_player_pov)

    st.total5.push(actual_total)
    st.total10.push(actual_total)

    st.win5.push(win)
    st.win10.push(win)
    st.win20.push(win)

    st.blowout_win10.push(blowout_win)
    st.blowout_loss10.push(blowout_loss)
    st.close10.push(close_match)

    st.resid10.push(residual)
    st.resid20.push(residual)
    st.resid_pos10.push(resid_pos)

    if expected_diff_player_pov >= FAVORITE_EXPECTED_DIFF_THRESHOLD:
        st.fav_win10.push(win)
        st.fav_diff10.push(actual_diff_player_pov)
    elif expected_diff_player_pov <= -FAVORITE_EXPECTED_DIFF_THRESHOLD:
        st.dog_win10.push(win)
        st.dog_diff10.push(actual_diff_player_pov)

    if not st.ewm_initialized:
        st.ewm_diff = actual_diff_player_pov
        st.ewm_initialized = True
    else:
        st.ewm_diff = (
            ewm_alpha * actual_diff_player_pov + (1.0 - ewm_alpha) * st.ewm_diff
        )

    st.n_matches += 1
    st.last_dt = dt
