# Rubinstein Ultimatum Game Simulation

A Python project comparing two approaches to the **Rubinstein alternating-offers bargaining game**:

1. **Classical** — rational subgame-perfect equilibrium via backward induction
2. **Chemical Game Theory (CGT)** — probabilistic acceptance derived from Gibbs free energy (ΔG) and Boltzmann statistics, calibrated against real experimental data

## Background

In the Rubinstein (1982) model, two players alternate making offers to split a pie. Each rejection costs time: the pie shrinks by a discount factor δ per round. Under perfect rationality, the unique equilibrium is reached immediately in Round 1.

Ochs & Roth (1989) ran lab experiments on this game and found that real people deviate substantially from the equilibrium prediction — around 16% of games go past Round 1. CGT models this deviation by treating each player's decision as a probabilistic chemical reaction driven by free energy terms.

## Project structure

| File | Purpose |
|------|---------|
| `models.py` | Two simulation engines (`simulate_classical`, `simulate_chemical`) and shared parameters |
| `simulation.py` | Monte Carlo runner: 1,000 trials per model, prints summary statistics |
| `app.py` | Bar chart comparing ending-round distributions for both models |
| `calibrate.py` | Grid search over CGT parameters to fit Ochs & Roth (1989) empirical data |
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

**Calibrate CGT parameters against Ochs & Roth (1989)**:

```bash
python calibrate.py
```

## The two models

### Classical (`simulate_classical`)

Backward induction on a finite 3-round game. Under perfect rationality the equilibrium offer is always accepted in Round 1 — every trial ends immediately. The equilibrium offer to the responder is ~28.8% of the pie with the default discount factor δ = 0.8.

Key parameters: `TOTAL_PIE`, `DELTA`, `MAX_ROUNDS` (top of `models.py`).

### Chemical / CGT (`simulate_chemical`)

Based on the framework in the CGT section of the project report. Each round, acceptance and rejection are treated as competing reaction pathways. Acceptance probability is computed via Boltzmann weighting of their Gibbs free energy terms:

$$\Delta G_{\text{yes}}(m) = -\gamma_y \cdot m - \varepsilon$$
$$\Delta G_{\text{no}}(m) = -\gamma_n \cdot m$$
$$P(\text{yes}) = \frac{e^{-\Delta G_{\text{yes}}/RT}}{e^{-\Delta G_{\text{yes}}/RT} + e^{-\Delta G_{\text{no}}/RT}}$$

where $m$ is the offer fraction to the responder. The constraint $\gamma_y > \gamma_n > 0$ ensures acceptance is always thermodynamically preferred, but small offers reduce the margin.

Key parameters:

| Parameter | Meaning |
|-----------|---------|
| `RT` | Thermal noise / temperature — higher = more random decisions |
| `epsilon` | Intrinsic cooperation bias (acceptance even at m=0) |
| `gamma_y` | Sensitivity of acceptance free energy to offer size |
| `gamma_n` | Sensitivity of rejection free energy to offer size |
| `offer_fraction` | Share of the current pie offered to the responder |

## Calibration against Ochs & Roth (1989)

`calibrate.py` fits CGT parameters to the empirical round distribution from the 3-period symmetric discount-factor cells (Cells 5 and 7 combined, n = 190 games):

| | Round 1 | Round 2 | Round 3 | Acceptance rate |
|---|---|---|---|---|
| **Empirical** | 86.8% | 8.4% | 4.7% | 97.4% |
| **Best-fit CGT** | 87.4% | 10.6% | 2.0% | 99.8% |

Best-fit parameters: `rt=1.5, epsilon=1.0, gamma_y=5.0, gamma_n=1.0, offer_fraction=0.45, delta=0.6`

The remaining gap at Round 3 reflects a feature the model does not yet capture: in the experiment, subjects sometimes reject offers even in the final round (ultimatum rejections driven by fairness concerns), while the Boltzmann model always assigns a positive acceptance probability.

## Key references

- Rubinstein, A. (1982). *Perfect Equilibrium in a Bargaining Model*. Econometrica, 50(1), 97–109.
- Ochs, J. & Roth, A. E. (1989). *An Experimental Study of Sequential Bargaining*. American Economic Review, 79(3), 355–384.
