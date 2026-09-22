"""
Strict out-of-sample backtest for a sports betting model.

WHAT IT ENFORCES
  1. Chronological (season) splits only. Expanding walk-forward by default, or a single
     fixed split (train 2022-2024, test 2025). No shuffling, no future data in training.
  2. Reports ATS win rate, ROI, max drawdown, and a per-season breakdown.
  3. Compares train vs test performance to expose overfitting, and flags the features
     driving the gap via coefficient drift across folds and permutation importance.

HOW TO MAP YOUR DATA
  Build one DataFrame, one row per game, with these columns:

    game_id        any unique id
    season         int, e.g. 2024
    week           int (used only for ordering inside a season)
    kickoff        datetime (used for ordering; optional if week is present)
    market_spread  closing/at-bet spread from the HOME team's side (-7.5 = home favored by 7.5)
    market_total   closing/at-bet over-under
    actual_margin  home_points - away_points
    actual_total   home_points + away_points
    price          American odds you bet at (default -110)
    <features...>  any pre-game features. MUST be built from information available
                   BEFORE kickoff (ratings through week-1, not season totals).

  Then:
    res = run_backtest(df, margin_features=[...], total_features=[...])

DEPENDENCIES: pandas, numpy, scikit-learn
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import TimeSeriesSplit
from sklearn.inspection import permutation_importance

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #

DEFAULT_PRICE = -110          # American odds
EDGE_THRESHOLD = 4.0          # points of edge required to place a bet
MARKET_TRUST = 0.75           # final = trust * market + (1 - trust) * model
FLAT_STAKE = 1.0              # units per bet
REQUIRED = [
    "game_id", "season", "market_spread", "market_total",
    "actual_margin", "actual_total",
]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def american_profit(price: float, stake: float = 1.0) -> float:
    """Profit on a winning bet of `stake` units at American odds `price`."""
    return stake * (100.0 / abs(price)) if price < 0 else stake * (price / 100.0)


def validate(df: pd.DataFrame, features: list[str]) -> None:
    missing = [c for c in REQUIRED + features if c not in df.columns]
    if missing:
        raise ValueError(f"DataFrame is missing columns: {missing}")
    if df["game_id"].duplicated().any():
        raise ValueError("Duplicate game_id values: each game must appear once.")
    if df[features].isna().any().any():
        bad = df[features].columns[df[features].isna().any()].tolist()
        raise ValueError(f"NaNs in feature columns {bad}. Fill or drop before backtesting.")


def grade(pick_is_over_or_home: np.ndarray, line_result: np.ndarray) -> np.ndarray:
    """
    Returns 1 for a win, 0 for a loss, np.nan for a push.
    `line_result` = actual - line, signed so positive favors the over/home side.
    """
    out = np.where(line_result > 0, 1.0, 0.0)
    out[line_result == 0] = np.nan
    return np.where(pick_is_over_or_home, out, 1.0 - out)


def max_drawdown(pnl: np.ndarray) -> tuple[float, int]:
    """Largest peak-to-trough drop of the cumulative P&L curve, in units."""
    if len(pnl) == 0:
        return 0.0, 0
    curve = np.cumsum(pnl)
    peak = np.maximum.accumulate(curve)
    dd = curve - peak
    i = int(np.argmin(dd))
    return float(dd[i]), i


def summarize(bets: pd.DataFrame, label: str) -> dict:
    """ATS win rate, ROI, drawdown, and the break-even rate implied by the price."""
    graded = bets.dropna(subset=["won"])
    n = len(graded)
    if n == 0:
        return {"segment": label, "bets": 0}
    wins = int(graded["won"].sum())
    pnl = graded["pnl"].to_numpy()
    dd, dd_i = max_drawdown(pnl)
    staked = graded["stake"].sum()
    be = abs(DEFAULT_PRICE) / (abs(DEFAULT_PRICE) + 100) if DEFAULT_PRICE < 0 else 100 / (DEFAULT_PRICE + 100)
    return {
        "segment": label,
        "bets": n,
        "pushes": int(bets["won"].isna().sum()),
        "wins": wins,
        "losses": n - wins,
        "win_rate": round(wins / n, 4),
        "break_even": round(be, 4),
        "edge_vs_be": round(wins / n - be, 4),
        "units": round(pnl.sum(), 2),
        "roi": round(pnl.sum() / staked, 4) if staked else 0.0,
        "max_drawdown_units": round(dd, 2),
        "worst_bet_index": dd_i,
    }


# --------------------------------------------------------------------------- #
# Core walk-forward engine
# --------------------------------------------------------------------------- #

def _fit_predict(train: pd.DataFrame, test: pd.DataFrame, features: list[str],
                 target: str, alpha: float) -> tuple[np.ndarray, np.ndarray, Ridge]:
    model = Ridge(alpha=alpha)
    model.fit(train[features], train[target])
    return model.predict(train[features]), model.predict(test[features]), model


def _bet_frame(part: pd.DataFrame, pred: np.ndarray, market_col: str,
               actual_col: str, market_sign: int, threshold: float,
               trust: float, price_col: str | None) -> pd.DataFrame:
    """
    market_sign = +1 for totals (market number compares directly to the prediction)
                  -1 for spreads (a home spread of -7.5 means an expected margin of +7.5)
    """
    market_number = market_sign * part[market_col].to_numpy()
    model_number = pred
    blended = trust * market_number + (1 - trust) * model_number
    edge = model_number - market_number
    take = np.abs(edge) >= threshold

    price = part[price_col].to_numpy() if price_col and price_col in part else np.full(len(part), DEFAULT_PRICE)
    actual = part[actual_col].to_numpy()
    line_result = actual - market_number          # positive = over / home covered
    pick_high = edge > 0                          # bet the over / bet the home side

    won = grade(pick_high, line_result)
    pnl = np.where(
        np.isnan(won), 0.0,
        np.where(won == 1, [american_profit(p, FLAT_STAKE) for p in price], -FLAT_STAKE),
    )
    return pd.DataFrame({
        "game_id": part["game_id"].to_numpy(),
        "season": part["season"].to_numpy(),
        "week": part["week"].to_numpy() if "week" in part else 0,
        "market": market_number,
        "model": model_number,
        "blended": blended,
        "edge": edge,
        "actual": actual,
        "pick_high": pick_high,
        "won": won,
        "stake": FLAT_STAKE,
        "pnl": pnl,
    })[take]


def run_backtest(df: pd.DataFrame,
                 features: list[str],
                 kind: str = "total",
                 alpha: float = 1.0,
                 threshold: float = EDGE_THRESHOLD,
                 trust: float = MARKET_TRUST,
                 mode: str = "walk_forward",
                 test_seasons: list[int] | None = None,
                 price_col: str | None = "price",
                 verbose: bool = True) -> dict:
    """
    kind  : "total" (bet over/under) or "spread" (bet the side)
    mode  : "walk_forward" trains on every earlier season, tests the next one.
            "fixed" trains on everything before min(test_seasons).
    """
    validate(df, features)
    target = "actual_total" if kind == "total" else "actual_margin"
    market_col = "market_total" if kind == "total" else "market_spread"
    market_sign = 1 if kind == "total" else -1

    order = ["season"] + (["week"] if "week" in df else []) + (["kickoff"] if "kickoff" in df else [])
    df = df.sort_values(order).reset_index(drop=True)
    seasons = sorted(df["season"].unique())

    if test_seasons is None:
        test_seasons = seasons[1:] if mode == "walk_forward" else seasons[-1:]

    fold_rows, all_bets, coefs, train_bets = [], [], [], []
    for s in test_seasons:
        train = df[df["season"] < s] if mode == "walk_forward" else df[df["season"] < min(test_seasons)]
        test = df[df["season"] == s]
        if len(train) < 100 or test.empty:
            continue

        pred_tr, pred_te, model = _fit_predict(train, test, features, target, alpha)

        bt_tr = _bet_frame(train, pred_tr, market_col, target, market_sign, threshold, trust, price_col)
        bt_te = _bet_frame(test, pred_te, market_col, target, market_sign, threshold, trust, price_col)
        train_bets.append(bt_tr)
        all_bets.append(bt_te)

        tr_sum, te_sum = summarize(bt_tr, f"train<{s}"), summarize(bt_te, f"test {s}")
        fold_rows.append({
            "test_season": s,
            "train_games": len(train),
            "test_games": len(test),
            "train_mae": round(float(np.mean(np.abs(pred_tr - train[target]))), 3),
            "test_mae": round(float(np.mean(np.abs(pred_te - test[target]))), 3),
            "train_win_rate": tr_sum.get("win_rate"),
            "test_win_rate": te_sum.get("win_rate"),
            "test_bets": te_sum.get("bets"),
            "test_roi": te_sum.get("roi"),
            "test_units": te_sum.get("units"),
            "test_max_dd": te_sum.get("max_drawdown_units"),
        })
        coefs.append(pd.Series(model.coef_, index=features, name=s))

    if not fold_rows:
        raise ValueError("No usable folds. Check that you have multiple seasons of data.")

    folds = pd.DataFrame(fold_rows)
    bets = pd.concat(all_bets, ignore_index=True)
    tr_all = pd.concat(train_bets, ignore_index=True)
    coef_df = pd.DataFrame(coefs)

    overall = summarize(bets, "ALL TEST SEASONS")
    per_season = [summarize(bets[bets["season"] == s], f"test {s}") for s in sorted(bets["season"].unique())]

    # ---- overfitting diagnostics -------------------------------------------
    gap_wr = float(folds["train_win_rate"].mean() - folds["test_win_rate"].mean())
    gap_mae = float(folds["test_mae"].mean() - folds["train_mae"].mean())
    coef_drift = (coef_df.std() / coef_df.abs().mean().replace(0, np.nan)).sort_values(ascending=False)

    last_train = df[df["season"] < test_seasons[-1]]
    last_test = df[df["season"] == test_seasons[-1]]
    perm = None
    if len(last_test) > 30:
        m = Ridge(alpha=alpha).fit(last_train[features], last_train[target])
        pi = permutation_importance(m, last_test[features], last_test[target],
                                    n_repeats=20, random_state=0,
                                    scoring="neg_mean_absolute_error")
        perm = pd.Series(pi.importances_mean, index=features).sort_values(ascending=False)

    flags = []
    if gap_wr > 0.03:
        flags.append(f"Train win rate exceeds test by {gap_wr:.1%}: the fit is not generalizing.")
    if gap_mae > 1.0:
        flags.append(f"Test MAE is {gap_mae:.2f} pts worse than train: too many features or alpha too low.")
    unstable = coef_drift[coef_drift > 0.5].index.tolist()
    if unstable:
        flags.append("Unstable coefficients across folds (prime overfit suspects): " + ", ".join(unstable))
    if perm is not None:
        useless = perm[perm <= 0].index.tolist()
        if useless:
            flags.append("Features that did not help out of sample: " + ", ".join(useless))
    if overall.get("bets", 0) < 200:
        flags.append(f"Only {overall.get('bets', 0)} test bets. Too few to trust: aim for 300+.")
    if not flags:
        flags.append("No overfitting red flags. Edge still needs live confirmation via CLV.")

    if verbose:
        pd.set_option("display.width", 160)
        print(f"\n=== {kind.upper()} BACKTEST | edge >= {threshold} pts | price {DEFAULT_PRICE} ===")
        print("\n-- folds (chronological, no leakage) --")
        print(folds.to_string(index=False))
        print("\n-- results --")
        print(pd.DataFrame(per_season + [overall]).to_string(index=False))
        print("\n-- overfitting check --")
        print(f"train vs test win rate gap: {gap_wr:+.3f}   |   test-minus-train MAE: {gap_mae:+.2f} pts")
        print("\ncoefficient drift (std / mean across folds, high = unstable):")
        print(coef_drift.round(2).to_string())
        if perm is not None:
            print("\npermutation importance on the final test season (higher = more useful):")
            print(perm.round(3).to_string())
        print("\n-- flags --")
        for f in flags:
            print(" * " + f)

    return {"folds": folds, "bets": bets, "train_bets": tr_all, "overall": overall,
            "per_season": pd.DataFrame(per_season), "coef_drift": coef_drift,
            "perm_importance": perm, "flags": flags}


# --------------------------------------------------------------------------- #
# Placeholder data so the script runs as-is
# --------------------------------------------------------------------------- #

def placeholder_df(n_per_season: int = 700, seasons=(2022, 2023, 2024, 2025), seed: int = 7) -> pd.DataFrame:
    """Synthetic games with a small, realistic model edge. Replace with your own data."""
    rng = np.random.default_rng(seed)
    rows = []
    for s in seasons:
        for i in range(n_per_season):
            eff_h, eff_a = rng.normal(0, 0.12, 2)
            pace = rng.normal(135, 10)
            true_margin = 60 * (eff_h - eff_a) + 2.8
            true_total = 52 + 40 * (eff_h + eff_a) + 0.08 * (pace - 135)
            margin = true_margin + rng.normal(0, 15)
            total = true_total + rng.normal(0, 14)
            rows.append({
                "game_id": f"{s}-{i}", "season": s, "week": i % 14 + 1,
                "eff_diff": eff_h - eff_a, "eff_sum": eff_h + eff_a, "pace": pace,
                "home_field": 1.0, "noise_feature": rng.normal(),
                "market_spread": -round((true_margin + rng.normal(0, 2)) * 2) / 2,
                "market_total": round((true_total + rng.normal(0, 2.5)) * 2) / 2,
                "actual_margin": margin, "actual_total": total, "price": -110,
            })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = placeholder_df()
    run_backtest(df, features=["eff_sum", "pace", "home_field", "noise_feature"], kind="total")
    run_backtest(df, features=["eff_diff", "home_field", "noise_feature"], kind="spread")
