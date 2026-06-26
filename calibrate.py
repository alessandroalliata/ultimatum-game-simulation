"""
Calibrate CGT (simulate_chemical) parameters to reproduce
Ochs & Roth (1989) experimental round distributions.

Empirical targets come from 3-period symmetric discount-factor cells
(Cells 5 and 7 combined, n = 190 bargaining games):

  Cell 5: delta1 = delta2 = 0.4, T = 3 (n = 100 games)
  Cell 7: delta1 = delta2 = 0.6, T = 3 (n =  90 games)

  Round 1 acceptance : 165/190 = 86.8%
  Round 2 acceptance :  16/190 =  8.4%
  Round 3 (agree)    :   4/190 =  2.1%
  Disagreement       :   5/190 =  2.6%  (game ends with no deal)
  Overall acceptance : 185/190 = 97.4%

Observed proposer behaviour: first-period offers cluster at 45-50% of the pie;
we use offer_fraction = 0.43 (mean observed first offer ~ 43% to the responder).

NOTE on discount factor: the paper's experiment used delta = 0.4 or 0.6, not
the delta = 0.8 default in models.py. The grid search includes both values so
we can see which produces the best fit.
"""

from __future__ import annotations

import itertools
from collections import Counter

from models import simulate_chemical

# ------------------------------------------------------------------
# Empirical targets  (Ochs & Roth 1989, Cells 5 + 7 combined)
# ------------------------------------------------------------------
TARGETS = {
    "round_dist": {1: 0.868, 2: 0.084, 3: 0.047},   # fraction ending per round
    "acceptance_rate": 0.974,
}

N_TRIALS = 3_000   # Monte Carlo trials per parameter combination
MAX_ROUNDS = 3


def _run(rt, epsilon, gamma_y, gamma_n, offer_fraction, delta):
    """Run one trial with specific CGT parameters."""
    return simulate_chemical(
        max_rounds=MAX_ROUNDS,
        delta=delta,
        rt=rt,
        epsilon=epsilon,
        gamma_y=gamma_y,
        gamma_n=gamma_n,
        offer_fraction=offer_fraction,
    )


def score(rt, epsilon, gamma_y, gamma_n, offer_fraction, delta, n=N_TRIALS):
    """
    Simulate n trials and return MSE vs. empirical targets.
    Lower MSE = better fit.
    """
    results = [_run(rt, epsilon, gamma_y, gamma_n, offer_fraction, delta) for _ in range(n)]

    counts = Counter(r.round_ended for r in results)
    sim_dist = {r: counts[r] / n for r in range(1, MAX_ROUNDS + 1)}
    sim_acc = sum(1 for r in results if r.accepted) / n

    # Penalise deviations in round fractions and acceptance rate equally
    mse = sum(
        (sim_dist.get(r, 0.0) - TARGETS["round_dist"].get(r, 0.0)) ** 2
        for r in range(1, MAX_ROUNDS + 1)
    )
    mse += (sim_acc - TARGETS["acceptance_rate"]) ** 2

    return mse, sim_dist, sim_acc


def grid_search():
    """Search over a discrete parameter grid; return results sorted by MSE."""

    # Parameter grid (each axis represents one CGT knob)
    grid = {
        "rt":             [0.3, 0.5, 0.8, 1.0, 1.5],      # thermal noise
        "epsilon":        [0.5, 1.0, 2.0, 3.0],            # cooperative bias
        "gamma_y":        [3.0, 5.0, 7.0, 9.0],            # acceptance gain weight
        "gamma_n":        [1.0, 2.0, 3.0, 4.0],            # rejection gain weight
        "offer_fraction": [0.40, 0.43, 0.45],               # share offered to responder
        "delta":          [0.4, 0.6],                       # discount factor (from paper)
    }

    combos = list(itertools.product(*grid.values()))
    print(f"Grid search: {len(combos)} combinations × {N_TRIALS} trials each")
    print(f"Targets  →  R1={TARGETS['round_dist'][1]:.1%}  "
          f"R2={TARGETS['round_dist'][2]:.1%}  "
          f"R3={TARGETS['round_dist'][3]:.1%}  "
          f"acc={TARGETS['acceptance_rate']:.1%}")
    print()

    records = []
    for i, (rt, eps, gy, gn, m, d) in enumerate(combos):
        mse, sim_dist, sim_acc = score(rt, eps, gy, gn, m, d)
        records.append((mse, rt, eps, gy, gn, m, d, sim_dist, sim_acc))
        if (i + 1) % 200 == 0:
            print(f"  {i + 1}/{len(combos)} evaluated …")

    records.sort(key=lambda x: x[0])
    return records


def report(records, top_n=5):
    print(f"\n{'=' * 65}")
    print(f"Top {top_n} parameter fits  (Ochs & Roth 1989)")
    print(f"{'=' * 65}")
    for rank, (mse, rt, eps, gy, gn, m, d, sim_dist, sim_acc) in enumerate(records[:top_n], 1):
        print(f"\n#{rank}  MSE = {mse:.6f}")
        print(f"     rt={rt}  epsilon={eps}  gamma_y={gy}  gamma_n={gn}")
        print(f"     offer_fraction={m}  delta={d}")
        print(f"     Simulated → R1={sim_dist.get(1, 0):.1%}  "
              f"R2={sim_dist.get(2, 0):.1%}  "
              f"R3={sim_dist.get(3, 0):.1%}  "
              f"acc={sim_acc:.1%}")

    _, rt, eps, gy, gn, m, d, _, _ = records[0]
    print(f"\n{'=' * 65}")
    print("Best-fit parameters — copy into simulate_chemical() defaults:")
    print(f"{'=' * 65}")
    print(f"  rt={rt}, epsilon={eps}, gamma_y={gy}, gamma_n={gn},")
    print(f"  offer_fraction={m}, delta={d}")


if __name__ == "__main__":
    records = grid_search()
    report(records)
