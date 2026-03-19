import numpy as np

# ============================================
# QARS Sensitivity Analysis
# Paper: PQC Migration for Critical Infrastructure
# Python 3.11.5, NumPy 1.24.3, seed=42
# ============================================

np.random.seed(42)
n_runs = 10000

# 50 synthetic CI assets (DL, MT, ZT, S, E, sector)
assets = [
    # Nuclear control x5
    (40, 10, 15, 1.0, 0.5, "energy"),
    (40, 10, 15, 1.0, 0.5, "energy"),
    (40, 10, 15, 1.0, 0.5, "energy"),
    (40, 10, 15, 1.0, 0.5, "energy"),
    (40, 10, 15, 1.0, 0.5, "energy"),
    # SCADA RTUs x15
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
    # Substation relays x10
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
    # Banking servers x10
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
    # PKI roots x5
    (20,  3, 15, 1.0, 0.5, "energy"),
    (20,  3, 15, 1.0, 0.5, "energy"),
    (20,  3, 15, 1.0, 0.5, "energy"),
    (20,  3, 15, 1.0, 0.5, "energy"),
    (20,  3, 15, 1.0, 0.5, "energy"),
    # IoT sensors x5
    ( 5,  3, 15, 0.2, 1.0, "energy"),
    (10,  5, 15, 0.2, 1.0, "energy"),
    ( 7,  4, 15, 0.2, 0.5, "energy"),
    ( 5,  3, 15, 0.2, 1.0, "energy"),
    (10,  5, 15, 0.2, 0.5, "energy"),
]

# Sector weights (wT, wS, wE)
base_weights = {
    "energy":  (0.3, 0.5, 0.2),
    "finance": (0.3, 0.2, 0.5),
}

def sigmoid(r, alpha=7):
    return 1.0 / (1.0 + np.exp(-alpha * (r - 1.0)))

def compute_qars(DL, MT, ZT, S, E, wT, wS, wE):
    r = (DL + MT) / ZT
    T = sigmoid(r)
    return wT*T + wS*S + wE*E

def classify(q):
    if q > 0.8:   return "RED"
    elif q > 0.4: return "YELLOW"
    else:         return "GREEN"

# ---- Baseline ----
baseline_scores  = []
baseline_classes = []
for (DL, MT, ZT, S, E, sector) in assets:
    wT, wS, wE = base_weights[sector]
    q = compute_qars(DL, MT, ZT, S, E, wT, wS, wE)
    baseline_scores.append(q)
    baseline_classes.append(classify(q))

print("=== BASELINE ===")
print(f"RED:    {baseline_classes.count('RED')}")
print(f"YELLOW: {baseline_classes.count('YELLOW')}")
print(f"GREEN:  {baseline_classes.count('GREEN')}")
print(f"QARS range: {min(baseline_scores):.3f} to {max(baseline_scores):.3f}")

# ---- Monte Carlo ----
same_count = 0
one_shift  = 0
two_shift  = 0
qars_deltas = []
order = ["GREEN", "YELLOW", "RED"]

for run in range(n_runs):
    if run % 1000 == 0:
        print(f"Running... {run}/{n_runs}")
    for (DL, MT, ZT, S, E, sector) in assets:
        wT0, wS0, wE0 = base_weights[sector]
        # Perturb weights by +/-20%
        wT = np.random.uniform(0.8*wT0, 1.2*wT0)
        wS = np.random.uniform(0.8*wS0, 1.2*wS0)
        wE = np.random.uniform(0.8*wE0, 1.2*wE0)
        total = wT + wS + wE
        wT /= total
        wS /= total
        wE /= total

        q_base = compute_qars(DL, MT, ZT, S, E, wT0, wS0, wE0)
        q_new  = compute_qars(DL, MT, ZT, S, E, wT,  wS,  wE)
        qars_deltas.append(abs(q_new - q_base))

        shift = abs(order.index(classify(q_new)) -
                    order.index(classify(q_base)))
        if   shift == 0: same_count += 1
        elif shift == 1: one_shift  += 1
        else:            two_shift  += 1

total = n_runs * len(assets)
pct_same = 100 * same_count / total
pct_one  = 100 * one_shift  / total
pct_two  = 100 * two_shift  / total
mean_d   = np.mean(qars_deltas)
ci_low   = np.percentile(qars_deltas,  2.5)
ci_high  = np.percentile(qars_deltas, 97.5)

print("\n=== MONTE CARLO RESULTS ===")
print(f"Same priority class:  {pct_same:.1f}%")
print(f"Shift by one class:   {pct_one:.1f}%")
print(f"Shift by two classes: {pct_two:.1f}%")
print(f"Mean delta QARS:      {mean_d:.4f}")
print(f"95% CI:               [{ci_low:.4f}, {ci_high:.4f}]")

# Save results to file
with open("qars_results.txt", "w") as f:
    f.write("=== QARS SENSITIVITY ANALYSIS RESULTS ===\n")
    f.write(f"n_runs = {n_runs}\n")
    f.write(f"n_assets = {len(assets)}\n")
    f.write(f"seed = 42\n\n")
    f.write(f"Same priority class:  {pct_same:.1f}%\n")
    f.write(f"Shift by one class:   {pct_one:.1f}%\n")
    f.write(f"Shift by two classes: {pct_two:.1f}%\n")
    f.write(f"Mean delta QARS:      {mean_d:.4f}\n")
    f.write(f"95% CI:               [{ci_low:.4f}, {ci_high:.4f}]\n")

print("\nResults saved to qars_results.txt")
