"""
De-vig a sportsbook line and compute true expected value + fractional Kelly.

Quick use:
    from ev_tools import evaluate_bet
    evaluate_bet(my_odds=-110, my_prob=0.556, opp_odds=-110, bankroll=500)

Note on de-vigging: the vig can only be removed when you know BOTH sides of the
market. One price alone has no separable commission. If you don't have the other
side, pass vig_assumption (e.g. 0.045 for a standard -110/-110 two-way market) and
the function will infer the opposite price for you, and say that it did.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
import math


# --------------------------------------------------------------------------- #
# Odds conversions
# --------------------------------------------------------------------------- #

def american_to_decimal(odds: float) -> float:
    if odds == 0:
        raise ValueError("American odds cannot be 0.")
    return 1 + (100 / abs(odds) if odds < 0 else odds / 100)


def american_to_implied(odds: float) -> float:
    """Raw implied probability, vig included."""
    return abs(odds) / (abs(odds) + 100) if odds < 0 else 100 / (odds + 100)


def decimal_to_american(dec: float) -> float:
    if dec <= 1:
        raise ValueError("Decimal odds must exceed 1.")
    return -100 / (dec - 1) if dec < 2 else (dec - 1) * 100


def implied_to_american(p: float) -> float:
    if not 0 < p < 1:
        raise ValueError("Probability must be between 0 and 1.")
    return decimal_to_american(1 / p)


# --------------------------------------------------------------------------- #
# De-vigging
# --------------------------------------------------------------------------- #

def devig_multiplicative(probs: list[float]) -> list[float]:
    """
    Multiplicative (proportional) method: divide each raw implied probability by
    the book's total. Standard, fast, and what most bettors mean by 'no-vig'.
    """
    total = sum(probs)
    return [p / total for p in probs]


def devig_power(probs: list[float], tol: float = 1e-10) -> list[float]:
    """
    Power (log-odds) method: find k such that sum(p_i ** k) == 1.
    Takes more vig out of longshots than the multiplicative method, so it is the
    better choice on lopsided markets (heavy favorites, big spreads, player props).
    """
    lo, hi = 0.5, 3.0
    for _ in range(200):
        k = (lo + hi) / 2
        s = sum(p ** k for p in probs)
        if abs(s - 1) < tol:
            break
        if s > 1:
            lo = k
        else:
            hi = k
    return [p ** k for p in probs]


# --------------------------------------------------------------------------- #
# EV + Kelly
# --------------------------------------------------------------------------- #

@dataclass
class BetEvaluation:
    odds: float
    decimal_odds: float
    raw_implied: float
    market_fair_prob: float
    model_prob: float
    edge: float
    ev_per_dollar: float
    ev_percent: float
    break_even_prob: float
    hold_percent: float
    kelly_full: float
    kelly_fraction: float
    stake: float
    method: str
    verdict: str
    notes: str

    def report(self) -> str:
        lines = [
            f"Line                 {self.odds:+g}  (decimal {self.decimal_odds:.3f})",
            f"Raw implied prob     {self.raw_implied:.2%}   <- includes the vig",
            f"Market fair prob     {self.market_fair_prob:.2%}   <- vig removed, {self.method} method",
            f"Book hold            {self.hold_percent:.2%}",
            f"Your model prob      {self.model_prob:.2%}",
            f"Edge vs market       {self.edge:+.2%}",
            f"Break-even prob      {self.break_even_prob:.2%}",
            f"Expected value       {self.ev_percent:+.2f}% per dollar risked",
            f"Kelly (full)         {self.kelly_full:.2%} of bankroll",
            f"Kelly (0.25x)        {self.kelly_fraction:.2%}  ->  ${self.stake:,.2f}",
            f"VERDICT              {self.verdict}",
        ]
        if self.notes:
            lines.append(f"Note                 {self.notes}")
        return "\n".join(lines)


def evaluate_bet(my_odds: float,
                 my_prob: float,
                 opp_odds: float | None = None,
                 bankroll: float = 1000.0,
                 kelly_multiplier: float = 0.25,
                 method: str = "multiplicative",
                 vig_assumption: float = 0.045,
                 min_ev: float = 0.0) -> BetEvaluation:
    """
    my_odds  : American odds on the side you want to bet (-110, +150, ...)
    my_prob  : your model's true win probability, as a decimal (0.556)
    opp_odds : American odds on the other side. Strongly recommended.
    method   : "multiplicative" or "power"
    """
    if not 0 < my_prob < 1:
        raise ValueError("my_prob must be a decimal between 0 and 1.")

    dec = american_to_decimal(my_odds)
    raw = american_to_implied(my_odds)
    notes = ""

    if opp_odds is None:
        # Infer the other side so the book's total lands at 1 + vig_assumption.
        opp_raw = max(1e-6, (1 + vig_assumption) - raw)
        notes = (f"Other side not supplied; assumed a {vig_assumption:.1%} hold "
                 f"(implied {implied_to_american(opp_raw):+.0f}). Pass opp_odds for exact numbers.")
    else:
        opp_raw = american_to_implied(opp_odds)

    probs = [raw, opp_raw]
    fair = (devig_power(probs) if method == "power" else devig_multiplicative(probs))[0]
    hold = sum(probs) - 1

    # Expected value on one dollar risked
    b = dec - 1
    ev = my_prob * b - (1 - my_prob)
    break_even = 1 / dec

    kelly_full = max(0.0, (my_prob * dec - 1) / b)
    kelly_frac = kelly_full * kelly_multiplier
    stake = kelly_frac * bankroll

    if ev > min_ev and my_prob > break_even:
        verdict = f"+EV. Bet it. Your number is {my_prob - fair:+.2%} off the market's fair price."
    elif ev > 0:
        verdict = "Marginally +EV. Below your minimum threshold: pass or bet small."
    else:
        verdict = "-EV. No bet. The price does not cover your win probability."

    if my_prob > fair + 0.12:
        verdict += "  WARNING: you disagree with the market by more than 12 points. Check for news or a stale line before trusting it."

    return BetEvaluation(
        odds=my_odds, decimal_odds=dec, raw_implied=raw, market_fair_prob=fair,
        model_prob=my_prob, edge=my_prob - fair, ev_per_dollar=ev, ev_percent=ev * 100,
        break_even_prob=break_even, hold_percent=hold, kelly_full=kelly_full,
        kelly_fraction=kelly_frac, stake=stake, method=method, verdict=verdict, notes=notes,
    )


def evaluate_pickem(my_prob: float, picks: int, payout: float,
                    bankroll: float = 1000.0, kelly_multiplier: float = 0.25) -> dict:
    """
    Sleeper / Underdog style pick'em: `picks` legs must all hit to pay `payout` times the entry.
    Assumes independent legs, which is why correlated legs from one game break the math.
    """
    p_all = my_prob ** picks
    ev = p_all * (payout - 1) - (1 - p_all)
    b = payout - 1
    kelly_full = max(0.0, (p_all * payout - 1) / b)
    return {
        "per_leg_prob": my_prob,
        "break_even_per_leg": (1 / payout) ** (1 / picks),
        "prob_all_hit": p_all,
        "ev_percent": ev * 100,
        "kelly_fraction": kelly_full * kelly_multiplier,
        "stake": kelly_full * kelly_multiplier * bankroll,
        "verdict": "+EV" if ev > 0 else "-EV: your per-leg probability is below the break-even rate.",
    }


if __name__ == "__main__":
    print("--- Totals bet, both sides known ---")
    print(evaluate_bet(my_odds=-110, my_prob=0.556, opp_odds=-110, bankroll=500).report())

    print("\n--- Underdog, one side only, power method ---")
    print(evaluate_bet(my_odds=+145, my_prob=0.44, opp_odds=-165, bankroll=500, method="power").report())

    print("\n--- Sleeper 3-pick at 6x ---")
    for k, v in evaluate_pickem(my_prob=0.56, picks=3, payout=6, bankroll=500).items():
        print(f"{k:22} {v if isinstance(v, str) else round(v, 4)}")
