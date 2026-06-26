from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Callable, Dict

from models import (
    MAX_ROUNDS,
    TrialResult,
    simulate_chemical,
    simulate_classical,
)

N_TRIALS = 1_000  


@dataclass
class ModelSummary:
    """Aggregated Monte Carlo statistics for one model."""

    name: str
    n_trials: int
    mean_rounds: float
    acceptance_rate: float
    round_distribution: Dict[int, float]  # fraction of trials ending in each round


def _run_trials(sim_fn: Callable[[], TrialResult], n_trials: int) -> list[TrialResult]:
    return [sim_fn() for _ in range(n_trials)]


def summarize(name: str, results: list[TrialResult]) -> ModelSummary:
    counts = Counter(r.round_ended for r in results)
    n = len(results)
    return ModelSummary(
        name=name,
        n_trials=n,
        mean_rounds=sum(r.round_ended for r in results) / n,
        acceptance_rate=sum(1 for r in results if r.accepted) / n,
        round_distribution={round_num: counts[round_num] / n for round_num in range(1, MAX_ROUNDS + 1)},
    )


def run_all(n_trials: int = N_TRIALS) -> Dict[str, ModelSummary]:
    """Run Monte Carlo simulations for Classical and CGT models."""
    models = {
        "Classical": simulate_classical,
        "Chemical (CGT)": simulate_chemical,
    }
    return {name: summarize(name, _run_trials(sim_fn, n_trials)) for name, sim_fn in models.items()}


def print_summary(summaries: Dict[str, ModelSummary]) -> None:
    for summary in summaries.values():
        print(f"\n{summary.name} ({summary.n_trials} trials)")
        print(f"  Average rounds to agreement: {summary.mean_rounds:.2f}")
        print(f"  Acceptance rate: {summary.acceptance_rate:.1%}")
        print("  Round distribution:")
        for round_num in range(1, MAX_ROUNDS + 1):
            pct = summary.round_distribution.get(round_num, 0.0)
            print(f"    Round {round_num}: {pct:.1%}")


if __name__ == "__main__":
    results = run_all()
    print_summary(results)
