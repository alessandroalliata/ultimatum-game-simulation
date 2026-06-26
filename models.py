from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

import numpy as np

# --- Shared game parameters ---

TOTAL_PIE = 100.0  # Total surplus split between players A and B
DELTA = 0.8        # Per-round discount factor (pie shrinks by 20% each rejection)
MAX_ROUNDS = 3     # Finite horizon: A proposes in odd rounds, B in even rounds

# --- Calibrated CGT parameter sets (from calibrate.py) ---

# Fitted to Classical GT: CGT recovers the rational equilibrium (always Round 1).
# Key driver: very low RT → Boltzmann distribution collapses to "always accept".
# δ is set to 0.4 to match the Cell 5 experimental setup; outcome is insensitive
# to δ at this RT since the game always ends in Round 1 regardless.
CGT_CLASSICAL_PARAMS = {
    "rt": 0.1, "epsilon": 0.5, "gamma_y": 3.0, "gamma_n": 1.0,
    "offer_fraction": 0.40, "delta": 0.4,
}

# Fitted to Ochs & Roth (1989), Cells 5 & 7 combined.
# δ is NOT a free parameter — it is fixed by the experimental design (0.4 or 0.6).
# These params minimise the average MSE across both conditions simultaneously.
# Higher RT introduces enough noise to generate occasional rejections and late rounds.
CGT_EMPIRICAL_PARAMS = {
    "rt": 1.5, "epsilon": 3.0, "gamma_y": 3.0, "gamma_n": 3.0,
    "offer_fraction": 0.43, "delta": 0.4,   # use delta=0.4 (Cell 5); swap to 0.6 for Cell 7
}


@dataclass
class TrialResult:
    """Outcome of a single simulated game."""

    round_ended: int
    accepted: bool
    offer_to_responder: float
    pie_at_round: float


def _pie_at_round(round_num: int, total_pie: float = TOTAL_PIE, delta: float = DELTA) -> float:
    """Remaining pie at the start of a given round (after prior rejections)."""
    return total_pie * (delta ** (round_num - 1))


def simulate_classical(
    max_rounds: int = MAX_ROUNDS,
    total_pie: float = TOTAL_PIE,
    delta: float = DELTA,
) -> TrialResult:
    """
    Classical Rubinstein solution via backward induction.

    Player A opens in Round 1. In equilibrium the first offer is accepted immediately,
    so every trial ends in Round 1 with acceptance.
    """
    # At the final round the proposer keeps the entire (discounted) pie.
    responder_minimum = 0.0

    # Walk backward: each responder must receive at least their discounted
    # continuation value from rejecting and becoming proposer next round.
    for round_num in range(max_rounds - 1, 0, -1):
        pie_next = _pie_at_round(round_num + 1, total_pie, delta)
        proposer_payoff_if_rejected = pie_next - responder_minimum
        responder_minimum = delta * proposer_payoff_if_rejected

    offer_to_responder = responder_minimum
    return TrialResult(
        round_ended=1,
        accepted=True,
        offer_to_responder=offer_to_responder,
        pie_at_round=total_pie,
    )



def simulate_chemical(
    max_rounds: int = MAX_ROUNDS,
    total_pie: float = TOTAL_PIE,
    delta: float = DELTA,
    rt: float = 1.0,
    epsilon: float = 2.0,
    gamma_y: float = 5.0,
    gamma_n: float = 2.0,
    offer_fraction: float = 0.40,
    rng: Optional[random.Random] = None,
) -> TrialResult:
    """
    Chemical Game Theory (CGT): probabilistic acceptance from Boltzmann weights.

    Parameters
    ----------
    rt : float
        Thermal noise / temperature (higher => more random decisions).
    epsilon : float
        Intrinsic cooperative bias (stabilizes "yes" when offers are reasonable).
    gamma_y, gamma_n : float
        Sensitivity of acceptance/rejection free energy to the offer fraction m.
        gamma_y > gamma_n > 0 ensures acceptance is always thermodynamically preferred.
    offer_fraction : float
        Share m of the current pie offered to the responder each round.
    """
    rng = rng or random

    for round_num in range(1, max_rounds + 1):
        pie = _pie_at_round(round_num, total_pie, delta)
        m = offer_fraction  # Responder's share of the current pie

        # Free-energy terms — teammate's formulation (Section: Chemical Game Theory):
        #   ΔG_yes(m) = -γ_y · m - ε   (acceptance; always exergonic, ε adds cooperation bias)
        #   ΔG_no(m)  = -γ_n · m       (rejection; neutral at m=0, more exergonic as m grows)
        # Constraint γ_y > γ_n > 0 ensures |ΔG_yes| > |ΔG_no|, so acceptance is always
        # thermodynamically preferred, but the margin shrinks for small offers.
        dg_yes = -gamma_y * m - epsilon
        dg_no = -gamma_n * m

        # Boltzmann probabilities: P(state) ∝ exp(-ΔG / RT)
        exp_yes = np.exp(-dg_yes / rt)
        exp_no = np.exp(-dg_no / rt)
        p_accept = exp_yes / (exp_yes + exp_no)

        accepted = rng.random() < p_accept
        offer = m * pie

        if accepted:
            return TrialResult(
                round_ended=round_num,
                accepted=True,
                offer_to_responder=offer,
                pie_at_round=pie,
            )

    pie = _pie_at_round(max_rounds, total_pie, delta)
    return TrialResult(
        round_ended=max_rounds,
        accepted=False,
        offer_to_responder=offer_fraction * pie,
        pie_at_round=pie,
    )
