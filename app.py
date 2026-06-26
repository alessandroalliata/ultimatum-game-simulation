import matplotlib.pyplot as plt
import numpy as np

from models import MAX_ROUNDS
from simulation import run_all

ROUND_LABELS = [f"Round {r}" for r in range(1, MAX_ROUNDS + 1)]
COLORS = ["#4C72B0", "#55A868"]  # Classical, CGT


def plot_round_distributions(summaries=None, save_path: str | None = None) -> None:
    if summaries is None:
        summaries = run_all()

    x = np.arange(len(ROUND_LABELS))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 5))

    for idx, summary in enumerate(summaries.values()):
        heights = [summary.round_distribution.get(r, 0.0) for r in range(1, MAX_ROUNDS + 1)]
        offset = (idx - 1) * width
        bars = ax.bar(x + offset, heights, width, label=summary.name, color=COLORS[idx])
        ax.bar_label(
            bars,
            labels=[f"{h:.0%}" if h > 0 else "" for h in heights],
            padding=2,
            fontsize=8,
        )

    ax.set_xlabel("Round where the game ended")
    ax.set_ylabel("Share of trials")
    ax.set_title("Rubinstein Ultimatum Game: Ending Round by Model")
    ax.set_xticks(x)
    ax.set_xticklabels(ROUND_LABELS)
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150)

    plt.show()


if __name__ == "__main__":
    plot_round_distributions()
