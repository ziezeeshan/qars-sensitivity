"""
generate_dataset.py
===================
Reproducible synthetic CI asset dataset generator for QARS sensitivity analysis.

Paper: Post-Quantum Cryptography Migration Frameworks for Critical Infrastructure
Author: Muhammad Zeeshan, Air University, Multan, Pakistan
GitHub: https://github.com/ziezeeshan/qars-sensitivity

DISTRIBUTION SPECIFICATION
===========================
All asset parameters are drawn from discrete uniform distributions
Uniform(a, b) means integer values drawn uniformly from [a, b] inclusive.
Fixed(v) means the parameter is deterministic (no sampling).

Justification for uniform distribution:
  - CI asset lifetimes are bounded by procurement cycles and regulatory
    review periods. Within each asset class, no systematic reason exists to
    prefer any particular value within the stated range (e.g., a SCADA RTU
    installed 20 years ago is equally likely as one installed 28 years ago).
  - Uniform distribution is the maximum-entropy choice given only the
    min/max bounds from published CI lifecycle data.
  - Source for ranges: DOE Grid Modernization report (2022), NERC CIP
    inventory data, ICS-CERT advisories.

PARAMETER SOURCES
=================
  ZT = 15 years (all assets): NSA Cybersecurity Advisory (2021) + ETSI
       White Paper No. 8 (2015). Conservative mid-range estimate.
  S  (Sensitivity): Based on CISA NCF criticality classification.
       L1=1.0: safety-critical (railway, nuclear), L2=0.6: operational,
       L3=0.2: non-essential.
  E  (Exposure): Network architecture assessment.
       Internet=1.0, Enterprise WAN=0.5, Air-gapped=0.1.
  Weights: Energy sector wS=0.5 (safety paramount);
           Finance sector wE=0.5 (internet exposure paramount).

USAGE
=====
  python generate_dataset.py         # generates CSV + runs QARS
  python generate_dataset.py --help  # show this message

OUTPUT
======
  qars_dataset.csv      -- full 50-asset dataset with distribution metadata
  qars_results.txt      -- Monte Carlo sensitivity analysis results
"""

import numpy as np
import csv
import sys

if "--help" in sys.argv:
    print(__doc__)
    sys.exit(0)

# ── Reproducibility ───────────────────────────────────────────────────────
SEED    = 42
N_RUNS  = 10_000
np.random.seed(SEED)

# ── Asset class definitions ───────────────────────────────────────────────
# Format: (class_name, n, DL_dist, DL_min, DL_max,
#                          MT_dist, MT_min, MT_max,
#                          ZT, S, E, sector)
ASSET_CLASSES = [
    # Nuclear control: deterministic (all known to be 40-yr plants, 10-yr
    # re-certification cycle per NRC regulations).
    ("Nuclear_Control",   5,  "Fixed",   40, 40,   "Fixed",   10, 10,  15, 1.0, 0.5, "energy"),

    # SCADA RTUs: installed over 1995-2005 → ages 20-30 yr.
    # Migration time: 8-12 yr (IEC 62443 re-cert + hardware cycle).
    ("SCADA_RTU",        15,  "Uniform", 20, 30,   "Uniform",  8, 12,  15, 1.0, 0.5, "energy"),

    # Substation protection relays: 15-25 yr installed base.
    # Migration: 5-10 yr (simpler firmware, shorter cert cycle).
    ("Substation_Relay", 10,  "Uniform", 15, 25,   "Uniform",  5, 10,  15, 1.0, 0.1, "energy"),

    # Banking servers: 7-10 yr data retention (PCI-DSS / SOX requirement).
    # Migration: 2-4 yr (IT, no ICS certification).
    ("Banking_Server",   10,  "Uniform",  7, 10,   "Uniform",  2,  4,  15, 0.6, 1.0, "finance"),

    # PKI roots: 20 yr key ceremonies (industry practice, RFC 5280).
    # Migration: 3 yr (software-only, HSM replacement).
    ("PKI_Root",          5,  "Fixed",   20, 20,   "Fixed",    3,  3,  15, 1.0, 0.5, "energy"),

    # IoT sensors: 5-10 yr battery/hardware lifecycle.
    # Migration: 3-5 yr (firmware OTA or physical replacement).
    ("IoT_Sensor",        5,  "Uniform",  5, 10,   "Uniform",  3,  5,  15, 0.2, 1.0, "energy"),
]

# ── Sector weights ────────────────────────────────────────────────────────
WEIGHTS = {
    "energy":  {"wT": 0.3, "wS": 0.5, "wE": 0.2},
    "finance": {"wT": 0.3, "wS": 0.2, "wE": 0.5},
}

# ── QARS functions ────────────────────────────────────────────────────────
def sigmoid(r, alpha=7):
    """Logistic sigmoid for timeline risk. alpha=7 chosen so T>0.9 when r>1.5."""
    return 1.0 / (1.0 + np.exp(-alpha * (r - 1.0)))

def compute_qars(DL, MT, ZT, S, E, wT, wS, wE):
    r = (DL + MT) / ZT
    return wT * sigmoid(r) + wS * S + wE * E

def classify(q):
    if   q > 0.8: return "RED"
    elif q > 0.4: return "YELLOW"
    else:         return "GREEN"

# ── Generate dataset ──────────────────────────────────────────────────────
def generate_assets():
    rows = []
    asset_id = 1
    for (cls, n, dl_dist, dl_min, dl_max,
             mt_dist, mt_min, mt_max,
             ZT, S, E, sector) in ASSET_CLASSES:
        w = WEIGHTS[sector]
        for _ in range(n):
            # Sample DL
            if dl_dist == "Fixed":
                DL = dl_min
            else:
                DL = int(np.random.randint(dl_min, dl_max + 1))
            # Sample MT
            if mt_dist == "Fixed":
                MT = mt_min
            else:
                MT = int(np.random.randint(mt_min, mt_max + 1))

            q = compute_qars(DL, MT, ZT, S, E, w["wT"], w["wS"], w["wE"])
            rows.append({
                "asset_id":       f"A{asset_id:03d}",
                "asset_class":    cls,
                "sector":         sector,
                "DL_years":       DL,
                "DL_distribution":dl_dist,
                "DL_min":         dl_min,
                "DL_max":         dl_max,
                "MT_years":       MT,
                "MT_distribution":mt_dist,
                "MT_min":         mt_min,
                "MT_max":         mt_max,
                "ZT_years":       ZT,
                "ZT_source":      "NSA_ETSI_consensus",
                "S_sensitivity":  S,
                "S_level":        ("L1_Safety" if S == 1.0 else
                                   ("L2_Operational" if S == 0.6
                                    else "L3_Low")),
                "E_exposure":     E,
                "E_type":         ("Internet" if E == 1.0 else
                                   ("WAN" if E == 0.5 else "Air_Gapped")),
                "wT":             w["wT"],
                "wS":             w["wS"],
                "wE":             w["wE"],
                "QARS_score":     round(q, 4),
                "QARS_class":     classify(q),
                "mosca_gap":      (DL + MT) - ZT,
                "mosca_violated": "YES" if (DL + MT) > ZT else "NO",
            })
            asset_id += 1
    return rows

# ── Monte Carlo sensitivity ───────────────────────────────────────────────
def run_monte_carlo(assets):
    same = one = two = 0
    deltas = []
    order = ["GREEN", "YELLOW", "RED"]

    for run in range(N_RUNS):
        if run % 2000 == 0:
            print(f"  Monte Carlo: {run}/{N_RUNS}")
        for row in assets:
            wT0, wS0, wE0 = row["wT"], row["wS"], row["wE"]
            # Perturb ±20%
            wT = np.random.uniform(0.8*wT0, 1.2*wT0)
            wS = np.random.uniform(0.8*wS0, 1.2*wS0)
            wE = np.random.uniform(0.8*wE0, 1.2*wE0)
            t  = wT + wS + wE
            wT /= t; wS /= t; wE /= t

            q0 = compute_qars(
                row["DL_years"], row["MT_years"], row["ZT_years"],
                row["S_sensitivity"], row["E_exposure"],
                wT0, wS0, wE0)
            qn = compute_qars(
                row["DL_years"], row["MT_years"], row["ZT_years"],
                row["S_sensitivity"], row["E_exposure"],
                wT, wS, wE)
            deltas.append(abs(qn - q0))
            sh = abs(order.index(classify(qn)) - order.index(classify(q0)))
            if   sh == 0: same += 1
            elif sh == 1: one  += 1
            else:         two  += 1

    total = N_RUNS * len(assets)
    return {
        "same_pct":   100 * same / total,
        "one_pct":    100 * one  / total,
        "two_pct":    100 * two  / total,
        "mean_delta": float(np.mean(deltas)),
        "ci_low":     float(np.percentile(deltas,  2.5)),
        "ci_high":    float(np.percentile(deltas, 97.5)),
    }

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("QARS DATASET GENERATION & SENSITIVITY ANALYSIS")
    print(f"seed={SEED}, n_runs={N_RUNS}")
    print("=" * 60)

    # 1. Generate dataset
    print("\nGenerating 50 synthetic CI assets...")
    assets = generate_assets()

    # 2. Print distribution summary
    print("\n=== DISTRIBUTION SPECIFICATION ===")
    for (cls, n, dl_dist, dl_min, dl_max,
             mt_dist, mt_min, mt_max, *_) in ASSET_CLASSES:
        print(f"  {cls} (n={n}):")
        print(f"    DL ~ {dl_dist}({dl_min}, {dl_max}) years")
        print(f"    MT ~ {mt_dist}({mt_min}, {mt_max}) years")

    # 3. Print baseline distribution
    classes = [r["QARS_class"] for r in assets]
    print("\n=== BASELINE QARS DISTRIBUTION ===")
    print(f"  RED:    {classes.count('RED')}/50 ({100*classes.count('RED')/50:.0f}%)")
    print(f"  YELLOW: {classes.count('YELLOW')}/50 ({100*classes.count('YELLOW')/50:.0f}%)")
    print(f"  GREEN:  {classes.count('GREEN')}/50 ({100*classes.count('GREEN')/50:.0f}%)")
    violated = sum(1 for r in assets if r["mosca_violated"] == "YES")
    print(f"  Mosca violated (ZT=15): {violated}/50 ({100*violated/50:.0f}%)")

    # 4. Save CSV
    csv_file = "qars_dataset.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(assets[0].keys()))
        writer.writeheader()
        writer.writerows(assets)
    print(f"\nDataset saved to {csv_file} ({len(assets)} rows)")

    # 5. Monte Carlo
    print(f"\n=== RUNNING MONTE CARLO (n={N_RUNS}) ===")
    mc = run_monte_carlo(assets)
    print(f"\n=== MONTE CARLO RESULTS ===")
    print(f"  Same priority class:  {mc['same_pct']:.1f}%")
    print(f"  Shift by one class:   {mc['one_pct']:.1f}%")
    print(f"  Shift by two classes: {mc['two_pct']:.1f}%")
    print(f"  Mean |ΔQARS|:         {mc['mean_delta']:.4f}")
    print(f"  95% CI:               [{mc['ci_low']:.4f}, {mc['ci_high']:.4f}]")

    # 6. Save results
    with open("qars_results.txt", "w") as f:
        f.write("QARS SENSITIVITY ANALYSIS RESULTS\n")
        f.write(f"seed={SEED}, n_runs={N_RUNS}, n_assets={len(assets)}\n\n")
        f.write("DISTRIBUTION SPECIFICATION\n")
        for (cls, n, dl_dist, dl_min, dl_max,
                 mt_dist, mt_min, mt_max, *_) in ASSET_CLASSES:
            f.write(f"  {cls}(n={n}): "
                    f"DL~{dl_dist}({dl_min},{dl_max}), "
                    f"MT~{mt_dist}({mt_min},{mt_max})\n")
        f.write("\nBASELINE\n")
        f.write(f"  RED:    {classes.count('RED')}/50\n")
        f.write(f"  YELLOW: {classes.count('YELLOW')}/50\n")
        f.write(f"  GREEN:  {classes.count('GREEN')}/50\n")
        f.write(f"  Mosca violated: {violated}/50\n")
        f.write("\nMONTE CARLO\n")
        f.write(f"  Same class:    {mc['same_pct']:.1f}%\n")
        f.write(f"  One shift:     {mc['one_pct']:.1f}%\n")
        f.write(f"  Two shift:     {mc['two_pct']:.1f}%\n")
        f.write(f"  Mean |ΔQARS|:  {mc['mean_delta']:.4f}\n")
        f.write(f"  95% CI:        [{mc['ci_low']:.4f}, {mc['ci_high']:.4f}]\n")

    print("\nResults saved to qars_results.txt")
    print("DONE.")

if __name__ == "__main__":
    main()
