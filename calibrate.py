"""
Calibrate CGT (simulate_chemical) parameters against two targets:

  1. CLASSICAL fit — CGT reproduces the rational equilibrium:
       game always ends in Round 1, acceptance rate ~100%.

  2. EMPIRICAL fit — CGT reproduces Ochs & Roth (1989) lab data.
       Delta (δ) is NOT a free parameter: it is fixed by the experimental
       design (chip values shrink by δ per period, told to subjects).
       We run two sub-calibrations — one per experimental condition —
       and average their MSEs so the winning parameters fit BOTH:

         Cell 5: δ = 0.4, T = 3, n ≈ 100 games
           R1=88%  R2=10%  R3=2%   acc=99%

         Cell 7: δ = 0.6, T = 3, n ≈ 90 games
           R1=86%  R2=7%   R3=8%   acc=96%

       Free parameters to fit: RT, ε, γ_y, γ_n, offer_fraction
"""

from __future__ import annotations

import itertools
from collections import Counter

from models import simulate_chemical

# ── Targets ────────────────────────────────────────────────────────────────

TARGETS = {
    "classical": {
        "label": "Classical GT (Round 1 always)",
        # δ does not matter here: with very low RT the game always ends R1
        # regardless of how fast the pie shrinks.
        "conditions": [
            {"delta": 0.4,
             "round_dist": {1: 1.0, 2: 0.0, 3: 0.0},
             "acceptance_rate": 1.0},
        ],
    },
    "empirical": {
        "label": "Ochs & Roth (1989) — Cells 5 & 7 (δ fixed by experiment)",
        # Two conditions with their own δ and own empirical distribution.
        # Targets derived from paper: figures 1B, Tables 7 & 8.
        "conditions": [
            {"delta": 0.4,                                       # Cell 5
             "round_dist": {1: 0.88, 2: 0.10, 3: 0.02},
             "acceptance_rate": 0.99},
            {"delta": 0.6,                                       # Cell 7
             "round_dist": {1: 0.856, 2: 0.067, 3: 0.078},
             "acceptance_rate": 0.956},
        ],
    },
}

N_TRIALS = 3_000
MAX_ROUNDS = 3

# ── Parameter grid (δ excluded — fixed by experiment) ─────────────────────

GRID = {
    "rt":             [0.1, 0.3, 0.5, 0.8, 1.0, 1.5],
    "epsilon":        [0.5, 1.0, 2.0, 3.0, 5.0],
    "gamma_y":        [3.0, 5.0, 7.0, 9.0],
    "gamma_n":        [1.0, 2.0, 3.0, 4.0],
    "offer_fraction": [0.40, 0.43, 0.45],
}


# ── Core helpers ───────────────────────────────────────────────────────────

def _mse_for_condition(rt, epsilon, gamma_y, gamma_n, offer_fraction, condition):
    """Simulate N trials for one (δ, target) condition and return MSE."""
    delta = condition["delta"]
    results = [
        simulate_chemical(
            max_rounds=MAX_ROUNDS,
            delta=delta,
            rt=rt,
            epsilon=epsilon,
            gamma_y=gamma_y,
            gamma_n=gamma_n,
            offer_fraction=offer_fraction,
        )
        for _ in range(N_TRIALS)
    ]
    counts = Counter(r.round_ended for r in results)
    sim_dist = {r: counts[r] / N_TRIALS for r in range(1, MAX_ROUNDS + 1)}
    sim_acc = sum(1 for r in results if r.accepted) / N_TRIALS

    mse = sum(
        (sim_dist.get(r, 0.0) - condition["round_dist"].get(r, 0.0)) ** 2
        for r in range(1, MAX_ROUNDS + 1)
    )
    mse += (sim_acc - condition["acceptance_rate"]) ** 2
    return mse, sim_dist, sim_acc


def _search(target_key: str) -> list:
    target = TARGETS[target_key]
    conditions = target["conditions"]
    combos = list(itertools.product(*GRID.values()))
    keys = list(GRID.keys())

    print(f"\n{'─'*65}")
    print(f"Target : {target['label']}")
    for c in conditions:
        print(f"  δ={c['delta']}  →  "
              f"R1={c['round_dist'][1]:.0%}  "
              f"R2={c['round_dist'][2]:.0%}  "
              f"R3={c['round_dist'][3]:.0%}  "
              f"acc={c['acceptance_rate']:.0%}")
    n_cond = len(conditions)
    print(f"Grid   : {len(combos)} combos × {N_TRIALS} trials × {n_cond} condition(s)")

    records = []
    for i, vals in enumerate(combos):
        params = dict(zip(keys, vals))

        # Average MSE across all conditions for this target
        total_mse = 0.0
        per_condition = []
        for cond in conditions:
            mse, sim_dist, sim_acc = _mse_for_condition(**params, condition=cond)
            total_mse += mse
            per_condition.append((cond["delta"], sim_dist, sim_acc))
        avg_mse = total_mse / n_cond

        records.append((avg_mse, params, per_condition))
        if (i + 1) % 400 == 0:
            print(f"  {i + 1}/{len(combos)} evaluated …")

    records.sort(key=lambda x: x[0])
    return records


def _report(records: list, top_n: int = 3) -> dict:
    print(f"\nTop {top_n} fits:")
    for rank, (avg_mse, params, per_cond) in enumerate(records[:top_n], 1):
        print(f"\n  #{rank}  avg MSE={avg_mse:.5f}")
        print(f"       params: {params}")
        for delta, sim_dist, sim_acc in per_cond:
            print(f"       δ={delta}  →  "
                  f"R1={sim_dist.get(1,0):.1%}  "
                  f"R2={sim_dist.get(2,0):.1%}  "
                  f"R3={sim_dist.get(3,0):.1%}  "
                  f"acc={sim_acc:.1%}")
    return records[0][1]


# ── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    best_classical = _report(_search("classical"), top_n=3)
    best_empirical = _report(_search("empirical"), top_n=3)

    print(f"\n{'='*65}")
    print("Copy these into models.py:")
    print(f"{'='*65}")
    print(f"\nCGT_CLASSICAL_PARAMS = {best_classical}")
    print(f"\nCGT_EMPIRICAL_PARAMS = {best_empirical}")
    print("\nNote: delta is NOT part of the free parameters.")
    print("Use delta=0.4 for Cell 5 conditions, delta=0.6 for Cell 7.")
