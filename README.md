# Rubinstein Ultimatum Game Simulation

A Python project comparing two approaches to the **Rubinstein alternating-offers bargaining game**:

1. **Classical** — rational subgame-perfect equilibrium via backward induction
2. **Chemical Game Theory (CGT)** — probabilistic acceptance derived from Gibbs free energy (ΔG) and Boltzmann statistics, calibrated against real experimental data

## Background

In the Rubinstein (1982) model, two players alternate making offers to split a pie. Each rejection costs time: the pie shrinks by a discount factor δ per round. Under perfect rationality, the unique equilibrium is reached immediately in Round 1.

Ochs & Roth (1989) ran lab experiments on this game and found that real people deviate substantially: ~16% of games go past Round 1. CGT models decisions as probabilistic chemical reactions driven by free energy terms (ΔG) and Boltzmann statistics.

The project answers two questions through calibration:
1. **Can CGT recover the classical equilibrium?** — yes, by tuning parameters so acceptance probability → 1.
2. **Can CGT match real human behaviour?** — yes, by tuning parameters to fit the Ochs & Roth data.

## Project structure

| File | Purpose |
|------|---------|
| `models.py` | Two simulation engines (`simulate_classical`, `simulate_chemical`) and calibrated parameter sets |
| `simulation.py` | Monte Carlo runner: 1,000 trials per scenario, prints summary statistics |
| `app.py` | Bar chart comparing ending-round distributions across all three scenarios |
| `calibrate.py` | Grid search that finds CGT parameters fitting the two calibration targets |
| `requirements.txt` | Python dependencies (`numpy`, `matplotlib`) |

## Setup

Requires Python 3.10+.

```bash
pip install -r requirements.txt
```

## How to run

**Print simulation statistics** (average rounds, acceptance rate, round distribution):

```bash
python simulation.py
```

**Show the comparison chart**:

```bash
python app.py
```

**Re-run the parameter calibration** (takes ~15 seconds):

```bash
python calibrate.py
```

## The three scenarios

### 1. Classical (`simulate_classical`)

Backward induction on a finite 3-round game. Under perfect rationality the equilibrium offer is always accepted in Round 1 — every trial ends immediately.

Key parameters: `TOTAL_PIE`, `DELTA`, `MAX_ROUNDS` (top of `models.py`).

### 2 & 3. Chemical / CGT (`simulate_chemical`) — two calibrations

Based on the CGT framework in the project report. Each round, acceptance and rejection are treated as competing reaction pathways. Acceptance probability follows Boltzmann weighting of their Gibbs free energy terms:

$$\Delta G_{\text{yes}}(m) = -\gamma_y \cdot m - \varepsilon$$
$$\Delta G_{\text{no}}(m) = -\gamma_n \cdot m$$
$$P(\text{yes}) = \frac{e^{-\Delta G_{\text{yes}}/RT}}{e^{-\Delta G_{\text{yes}}/RT} + e^{-\Delta G_{\text{no}}/RT}}$$

where $m$ is the offer fraction to the responder. The constraint $\gamma_y > \gamma_n > 0$ ensures acceptance is always thermodynamically preferred, but the margin shrinks for small offers.

Key parameters:

| Parameter | Meaning |
|-----------|---------|
| `RT` | Thermal noise / temperature — higher = more random decisions |
| `epsilon` | Intrinsic cooperation bias (acceptance even at m=0) |
| `gamma_y` | Sensitivity of acceptance free energy to offer size |
| `gamma_n` | Sensitivity of rejection free energy to offer size |
| `offer_fraction` | Share of the current pie offered to the responder |

The same function is used for both CGT scenarios — only the parameter values differ. The two calibrated sets live in `models.py` as `CGT_CLASSICAL_PARAMS` and `CGT_EMPIRICAL_PARAMS`.

## Calibration (`calibrate.py`)

`calibrate.py` runs a grid search over the free CGT parameters — `RT`, `ε`, `γ_y`, `γ_n`, `offer_fraction` — against two targets. **δ is never a free parameter**: it is fixed by the experimental design of Ochs & Roth and held constant throughout.

---

**Target 1 — Classical equilibrium** (game always ends in Round 1)

| | Round 1 | Round 2 | Round 3 |
|---|---|---|---|
| Target | 100% | 0% | 0% |
| Best-fit CGT | 100% | 0% | 0% |

Best-fit params: `rt=0.1, epsilon=0.5, gamma_y=3.0, gamma_n=1.0, offer_fraction=0.40`

Key insight: very low `RT` (= 0.1) collapses the Boltzmann distribution toward certainty — CGT recovers deterministic rational behaviour regardless of δ.

---

**Target 2 — Ochs & Roth (1989) lab data**

δ is fixed at the two experimental values and the search minimises the **average MSE across both conditions** simultaneously:

| Condition | δ | R1 target | R2 target | R3 target | acc target |
|---|---|---|---|---|---|
| Cell 5 | 0.4 | 88% | 10% | 2% | 99% |
| Cell 7 | 0.6 | 86% | 7% | 8% | 96% |

Best-fit params: `rt=1.5, epsilon=3.0, gamma_y=3.0, gamma_n=3.0, offer_fraction=0.43`

Simulation results with best-fit params:

| Condition | δ | R1 sim | R2 sim | R3 sim |
|---|---|---|---|---|
| Cell 5 | 0.4 | 87.7% | 10.7% | 1.6% |
| Cell 7 | 0.6 | 88.7% | 9.5% | 1.8% |

Key insight: higher `RT` (= 1.5) introduces enough thermal noise to generate occasional rejections and late agreements. The remaining gap at Round 3 reflects ultimatum rejections driven by fairness concerns that the Boltzmann model does not fully capture.

---

## Key references

- Rubinstein, A. (1982). *Perfect Equilibrium in a Bargaining Model*. Econometrica, 50(1), 97–109.
- Ochs, J. & Roth, A. E. (1989). *An Experimental Study of Sequential Bargaining*. American Economic Review, 79(3), 355–384.
