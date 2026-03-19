"""
QARS Sensitivity Analysis
=========================
Paper: Post-Quantum Cryptography Migration Frameworks for Critical
       Infrastructure: A Systematic Literature Review and Strategic Roadmap
Author: Muhammad Zeeshan, Air University, Multan, Pakistan
GitHub: https://github.com/kitten0x0/qars-sensitivity

Dependencies: numpy==1.24.3, matplotlib (for plots)
Usage: python qars_sensitivity.py
"""

import numpy as np

np.random.seed(42)
N_RUNS = 10000

# ── Asset dataset (50 synthetic CI assets) ────────────────────────────────
# Fields: (DL, MT, ZT, S, E, sector)
#   DL  = Data Lifespan (years)
#   MT  = Migration Time (years)
#   ZT  = Zero-Day / CRQC estimate (years) = 15 for all (NSA/ETSI consensus)
#   S   = Sensitivity: 1.0=safety-critical, 0.6=operational, 0.2=low
#   E   = Exposure:    1.0=internet, 0.5=WAN, 0.1=air-gapped
#   sector = "energy" or "finance" (determines weight set)
ASSETS = [
    # ── Nuclear control systems (n=5) ─────────────────────────────────────
    (40, 10, 15, 1.0, 0.5, "energy"),
    (40, 10, 15, 1.0, 0.5, "energy"),
    (40, 10, 15, 1.0, 0.5, "energy"),
    (40, 10, 15, 1.0, 0.5, "energy"),
    (40, 10, 15, 1.0, 0.5, "energy"),
    # ── SCADA RTUs (n=15) ─────────────────────────────────────────────────
    (25, 10, 15, 1.0, 0.5, "energy"),
    (25, 10, 15, 1.0, 0.1, "energy"),
    (20,  8, 15, 0.6, 0.5, "energy"),
    (30, 12, 15, 1.0, 0.5, "energy"),
    (20,  8, 15, 1.0, 0.1, "energy"),
    (25, 10, 15, 0.6, 0.5, "energy"),
    (30, 12, 15, 1.0, 0.5, "energy"),
    (20,  8, 15, 0.6, 0.1, "energy"),
    (25, 10, 15, 1.0, 0.5, "energy"),
    (30, 12, 15, 1.0, 0.1, "energy"),
    (25, 10, 15, 0.6, 0.5, "energy"),
    (20,  8, 15, 1.0, 0.5, "energy"),
    (25, 10, 15, 1.0, 0.1, "energy"),
    (30, 12, 15, 0.6, 0.5, "energy"),
    (25, 10, 15, 1.0, 0.5, "energy"),
    # ── Substation protection relays (n=10) ───────────────────────────────
    (20,  5, 15, 1.0, 0.5, "energy"),
    (25, 10, 15, 1.0, 0.1, "energy"),
    (15,  5, 15, 1.0, 0.5, "energy"),
    (20,  8, 15, 1.0, 0.1, "energy"),
    (25, 10, 15, 1.0, 0.5, "energy"),
    (15,  5, 15, 1.0, 0.5, "energy"),
    (20,  8, 15, 1.0, 0.1, "energy"),
    (25, 10, 15, 1.0, 0.5, "energy"),
    (15,  5, 15, 1.0, 0.5, "energy"),
    (20,  8, 15, 1.0, 0.1, "energy"),
    # ── Banking servers (n=10) ────────────────────────────────────────────
    (10,  2, 15, 0.6, 1.0, "finance"),
    ( 7,  2, 15, 0.6, 1.0, "finance"),
    (10,  3, 15, 0.6, 1.0, "finance"),
    ( 8,  2, 15, 0.6, 1.0, "finance"),
    (10,  4, 15, 0.6, 1.0, "finance"),
    ( 7,  2, 15, 0.6, 1.0, "finance"),
    (10,  3, 15, 0.6, 1.0, "finance"),
    ( 8,  4, 15, 0.6, 1.0, "finance"),
    (10,  2, 15, 0.6, 1.0, "finance"),
    ( 7,  3, 15, 0.6, 1.0, "finance"),
    # ── PKI roots (n=5) ───────────────────────────────────────────────────
    (20,  3, 15, 1.0, 0.5, "energy"),
    (20,  3, 15, 1.0, 0.5, "energy"),
    (20,  3, 15, 1.0, 0.5, "energy"),
    (20,  3, 15, 1.0, 0.5, "energy"),
    (20,  3, 15, 1.0, 0.5, "energy"),
    # ── IoT sensors (n=5) ─────────────────────────────────────────────────
    ( 5,  3, 15, 0.2, 1.0, "energy"),
    (10,  5, 15, 0.2, 1.0, "energy"),
    ( 7,  4, 15, 0.2, 0.5, "energy"),
    ( 5,  3, 15, 0.2, 1.0, "energy"),
    (10,  5, 15, 0.2, 0.5, "energy"),
]

# ── Sector-specific weights (wT, wS, wE) ──────────────────────────────────
BASE_WEIGHTS = {
    "energy":  (0.3, 0.5, 0.2),   # Safety paramount
    "finance": (0.3, 0.2, 0.5),   # Exposure paramount
}

# ── QARS functions ─────────────────────────────────────────────────────────
def sigmoid(r, alpha=7):
    """Logistic sigmoid for timeline risk scaling."""
    return 1.0 / (1.0 + np.exp(-alpha * (r - 1.0)))

def compute_qars(DL, MT, ZT, S, E, wT, wS, wE):
    """Compute QARS score for one asset."""
    r = (DL + MT) / ZT
    T = sigmoid(r)
    return wT * T + wS * S + wE * E

def classify(q):
    """Classify QARS score into priority tier."""
    if   q > 0.8: return "RED"
    elif q > 0.4: return "YELLOW"
    else:         return "GREEN"


def run_baseline():
    """Compute baseline QARS scores and classes for all 50 assets."""
    scores, classes = [], []
    for (DL, MT, ZT, S, E, sector) in ASSETS:
        wT, wS, wE = BASE_WEIGHTS[sector]
        q = compute_qars(DL, MT, ZT, S, E, wT, wS, wE)
        scores.append(q)
        classes.append(classify(q))
    return scores, classes


def run_monte_carlo(n_runs=N_RUNS):
    """
    Monte Carlo weight perturbation sensitivity analysis.
    Each weight perturbed by U[-20%, +20%], re-normalized to sum=1.
    Returns classification stability statistics.
    """
    same = one = two = 0
    deltas = []
    order = ["GREEN", "YELLOW", "RED"]

    for run_idx in range(n_runs):
        if run_idx % 2000 == 0:
            print(f"  Monte Carlo progress: {run_idx}/{n_runs}")

        for (DL, MT, ZT, S, E, sector) in ASSETS:
            wT0, wS0, wE0 = BASE_WEIGHTS[sector]

            # Perturb ±20%
            wT = np.random.uniform(0.8 * wT0, 1.2 * wT0)
            wS = np.random.uniform(0.8 * wS0, 1.2 * wS0)
            wE = np.random.uniform(0.8 * wE0, 1.2 * wE0)
            total = wT + wS + wE
            wT /= total; wS /= total; wE /= total

            q_base = compute_qars(DL, MT, ZT, S, E, wT0, wS0, wE0)
            q_new  = compute_qars(DL, MT, ZT, S, E, wT,  wS,  wE)
            deltas.append(abs(q_new - q_base))

            shift = abs(order.index(classify(q_new)) -
                        order.index(classify(q_base)))
            if   shift == 0: same += 1
            elif shift == 1: one  += 1
            else:            two  += 1

    total_trials = n_runs * len(ASSETS)
    return {
        "same_pct":  100 * same / total_trials,
        "one_pct":   100 * one  / total_trials,
        "two_pct":   100 * two  / total_trials,
        "mean_delta": np.mean(deltas),
        "ci_low":    np.percentile(deltas,  2.5),
        "ci_high":   np.percentile(deltas, 97.5),
        "deltas":    deltas,
    }


def mosca_zt_sensitivity():
    """Test how many assets violate Mosca inequality at different ZT values."""
    print("\n=== MOSCA ZT SENSITIVITY ===")
    for zt in [10, 15, 20, 30]:
        violated = sum(1 for (DL, MT, ZT, S, E, sec) in ASSETS
                       if DL + MT > zt)
        print(f"  ZT={zt} years: {violated}/50 assets violate "
              f"Mosca ({100*violated/50:.0f}%)")


def worked_examples():
    """Print complete step-by-step QARS calculations for 3 example assets."""
    print("\n=== WORKED QARS EXAMPLES ===")
    cases = [
        ("SCADA RTU (Energy)",    25, 10, 15, 1.0, 0.5, "energy"),
        ("Banking Server (Finance)", 10, 3, 15, 0.6, 1.0, "finance"),
        ("IoT Sensor (Energy)",    5,  3, 15, 0.2, 1.0, "energy"),
    ]
    for (name, DL, MT, ZT, S, E, sector) in cases:
        wT, wS, wE = BASE_WEIGHTS[sector]
        r = (DL + MT) / ZT
        T = sigmoid(r)
        q = compute_qars(DL, MT, ZT, S, E, wT, wS, wE)
        print(f"\n  {name}:")
        print(f"    DL={DL}, MT={MT}, ZT={ZT}, S={S}, E={E}")
        print(f"    r = ({DL}+{MT})/{ZT} = {r:.4f}")
        print(f"    T = 1/(1+exp(-7×({r:.4f}-1))) = {T:.4f}")
        print(f"    QARS = {wT}×{T:.4f} + {wS}×{S} + {wE}×{E}")
        print(f"         = {wT*T:.4f} + {wS*S:.4f} + {wE*E:.4f}")
        print(f"         = {q:.4f}  →  {classify(q)}")


def main():
    print("=" * 60)
    print("QARS SENSITIVITY ANALYSIS")
    print(f"n_runs={N_RUNS}, n_assets={len(ASSETS)}, seed=42")
    print("=" * 60)

    # Baseline
    scores, classes = run_baseline()
    print("\n=== BASELINE DISTRIBUTION ===")
    print(f"  RED:    {classes.count('RED')} "
          f"({100*classes.count('RED')/50:.0f}%)")
    print(f"  YELLOW: {classes.count('YELLOW')} "
          f"({100*classes.count('YELLOW')/50:.0f}%)")
    print(f"  GREEN:  {classes.count('GREEN')} "
          f"({100*classes.count('GREEN')/50:.0f}%)")
    print(f"  QARS range: {min(scores):.4f} – {max(scores):.4f}")

    # Monte Carlo
    print(f"\n=== RUNNING MONTE CARLO (n={N_RUNS} runs) ===")
    mc = run_monte_carlo(N_RUNS)
    print(f"\n=== MONTE CARLO RESULTS ===")
    print(f"  Same priority class:  {mc['same_pct']:.1f}%")
    print(f"  Shift by one class:   {mc['one_pct']:.1f}%")
    print(f"  Shift by two classes: {mc['two_pct']:.1f}%")
    print(f"  Mean |ΔQARS|:         {mc['mean_delta']:.4f}")
    print(f"  95% CI:               [{mc['ci_low']:.4f}, "
          f"{mc['ci_high']:.4f}]")

    # Mosca sensitivity
    mosca_zt_sensitivity()

    # Worked examples
    worked_examples()

    # Save results
    with open("qars_results.txt", "w") as f:
        f.write("QARS SENSITIVITY ANALYSIS RESULTS\n")
        f.write(f"n_runs={N_RUNS}, n_assets={len(ASSETS)}, seed=42\n\n")
        f.write("BASELINE\n")
        f.write(f"  RED:    {classes.count('RED')}/50\n")
        f.write(f"  YELLOW: {classes.count('YELLOW')}/50\n")
        f.write(f"  GREEN:  {classes.count('GREEN')}/50\n\n")
        f.write("MONTE CARLO\n")
        f.write(f"  Same class:    {mc['same_pct']:.1f}%\n")
        f.write(f"  One shift:     {mc['one_pct']:.1f}%\n")
        f.write(f"  Two shift:     {mc['two_pct']:.1f}%\n")
        f.write(f"  Mean |ΔQARS|:  {mc['mean_delta']:.4f}\n")
        f.write(f"  95% CI:        [{mc['ci_low']:.4f}, "
                f"{mc['ci_high']:.4f}]\n\n")
        f.write("MOSCA ZT SENSITIVITY\n")
        for zt in [10, 15, 20, 30]:
            v = sum(1 for (DL,MT,ZT,S,E,s) in ASSETS if DL+MT>zt)
            f.write(f"  ZT={zt}: {v}/50 ({100*v/50:.0f}%)\n")

    print("\nResults saved to qars_results.txt")
    print("DONE.")


if __name__ == "__main__":
    main()
