# QARS Sensitivity Analysis

**Repository for:** "Post-Quantum Cryptography Migration Frameworks for Critical Infrastructure: A Systematic Literature Review and Strategic Roadmap"

**Author:** Muhammad Zeeshan, Air University, Multan, Pakistan

---

## Overview

This repository contains the Python implementation of the Quantum-Adjusted Risk Score (QARS) sensitivity analysis described in the paper. The QARS model extends Mosca's Theorem to continuous asset-level risk scoring for post-quantum cryptography (PQC) migration prioritization in critical infrastructure (CI).

The QARS formula is:

```
QARS(a) = wT · T(a) + wS · S(a) + wE · E(a)
```

Where:
- `T(a)` = Timeline Risk (logistic sigmoid of Mosca ratio)
- `S(a)` = Sensitivity Risk (asset criticality)
- `E(a)` = Exposure Risk (HNDL attack susceptibility)
- `wT, wS, wE` = sector-specific weights summing to 1.0

---

## Files

| File | Description |
|---|---|
| `qars_sensitivity.py` | Main Monte Carlo sensitivity analysis (n=10,000 runs, 50 assets) |
| `energy_calc.py` | STM32F407 energy consumption sensitivity across voltage range |
| `qars_results.txt` | Output from qars_sensitivity.py |
| `energy_results.txt` | Output from energy_calc.py |

---

## Requirements

```
Python 3.11.5
numpy==1.24.3
```

Install with:
```bash
pip install numpy==1.24.3
```

---

## Reproducing Results

### QARS Sensitivity Analysis
```bash
python qars_sensitivity.py
```

Expected output:
```
Same priority class:  96.9%
Shift by one class:   3.1%
Shift by two classes: 0.0%
Mean |ΔQARS|:         0.0134
95% CI:               [0.0005, 0.0428]
```

### Energy Analysis
```bash
python energy_calc.py
```

Expected output:
```
1.8V: 12.1 mJ | 1.104e+06 signs/1000mAh
3.0V: 20.1 mJ | 6.627e+05 signs/1000mAh
3.3V: 22.1 mJ | 6.024e+05 signs/1000mAh
```

---

## Asset Dataset

The sensitivity analysis uses 50 synthetic CI assets across 6 classes:

| Asset Class | n | DL (years) | MT (years) | ZT (years) |
|---|---|---|---|---|
| Nuclear control systems | 5 | 40 | 10 | 15 |
| SCADA RTUs | 15 | 20–30 | 8–12 | 15 |
| Substation relays | 10 | 15–25 | 5–10 | 15 |
| Banking servers | 10 | 7–10 | 2–4 | 15 |
| PKI roots | 5 | 20 | 3 | 15 |
| IoT sensors | 5 | 5–10 | 3–5 | 15 |

---

## Sector Weights

| Sector | wT | wS | wE |
|---|---|---|---|
| Energy | 0.3 | 0.5 | 0.2 |
| Finance | 0.3 | 0.2 | 0.5 |

---

## Simulation Parameters

- Random seed: 42
- Perturbation: Uniform U[0.8w, 1.2w] per weight (±20%)
- Normalization: Weights re-normalized to sum to 1.0 after sampling
- Runs: 10,000 × 50 assets = 500,000 total trials

---

## Priority Classification

| QARS Score | Priority | Action |
|---|---|---|
| > 0.8 | RED | Immediate BITW gateway deployment |
| 0.4 – 0.8 | YELLOW | Next refresh cycle |
| ≤ 0.4 | GREEN | Deferred to standard lifecycle |

---


