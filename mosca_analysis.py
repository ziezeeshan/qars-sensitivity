"""
Mosca's Theorem Analysis
=========================
Paper: Post-Quantum Cryptography Migration Frameworks for Critical
       Infrastructure: A Systematic Literature Review and Strategic Roadmap
Author: Muhammad Zeeshan, Air University, Multan, Pakistan

Computes:
  1. How many assets violate Mosca inequality at different ZT values
  2. Security gap (years overdue) for each asset
  3. Impossible scenario analysis (ZT < MT)

Mosca's Inequality: DL + MT > ZT → RISK PRESENT
"""

# ── Asset dataset (same 50 assets as qars_sensitivity.py) ─────────────────
ASSETS = [
    # (name, DL, MT, ZT, sector)
    ("Nuclear-1",     40, 10, 15, "energy"),
    ("Nuclear-2",     40, 10, 15, "energy"),
    ("Nuclear-3",     40, 10, 15, "energy"),
    ("Nuclear-4",     40, 10, 15, "energy"),
    ("Nuclear-5",     40, 10, 15, "energy"),
    ("SCADA-RTU-1",   25, 10, 15, "energy"),
    ("SCADA-RTU-2",   25, 10, 15, "energy"),
    ("SCADA-RTU-3",   20,  8, 15, "energy"),
    ("SCADA-RTU-4",   30, 12, 15, "energy"),
    ("SCADA-RTU-5",   20,  8, 15, "energy"),
    ("SCADA-RTU-6",   25, 10, 15, "energy"),
    ("SCADA-RTU-7",   30, 12, 15, "energy"),
    ("SCADA-RTU-8",   20,  8, 15, "energy"),
    ("SCADA-RTU-9",   25, 10, 15, "energy"),
    ("SCADA-RTU-10",  30, 12, 15, "energy"),
    ("SCADA-RTU-11",  25, 10, 15, "energy"),
    ("SCADA-RTU-12",  20,  8, 15, "energy"),
    ("SCADA-RTU-13",  25, 10, 15, "energy"),
    ("SCADA-RTU-14",  30, 12, 15, "energy"),
    ("SCADA-RTU-15",  25, 10, 15, "energy"),
    ("Substation-1",  20,  5, 15, "energy"),
    ("Substation-2",  25, 10, 15, "energy"),
    ("Substation-3",  15,  5, 15, "energy"),
    ("Substation-4",  20,  8, 15, "energy"),
    ("Substation-5",  25, 10, 15, "energy"),
    ("Substation-6",  15,  5, 15, "energy"),
    ("Substation-7",  20,  8, 15, "energy"),
    ("Substation-8",  25, 10, 15, "energy"),
    ("Substation-9",  15,  5, 15, "energy"),
    ("Substation-10", 20,  8, 15, "energy"),
    ("BankSvr-1",     10,  2, 15, "finance"),
    ("BankSvr-2",      7,  2, 15, "finance"),
    ("BankSvr-3",     10,  3, 15, "finance"),
    ("BankSvr-4",      8,  2, 15, "finance"),
    ("BankSvr-5",     10,  4, 15, "finance"),
    ("BankSvr-6",      7,  2, 15, "finance"),
    ("BankSvr-7",     10,  3, 15, "finance"),
    ("BankSvr-8",      8,  4, 15, "finance"),
    ("BankSvr-9",     10,  2, 15, "finance"),
    ("BankSvr-10",     7,  3, 15, "finance"),
    ("PKI-Root-1",    20,  3, 15, "energy"),
    ("PKI-Root-2",    20,  3, 15, "energy"),
    ("PKI-Root-3",    20,  3, 15, "energy"),
    ("PKI-Root-4",    20,  3, 15, "energy"),
    ("PKI-Root-5",    20,  3, 15, "energy"),
    ("IoT-Sensor-1",   5,  3, 15, "energy"),
    ("IoT-Sensor-2",  10,  5, 15, "energy"),
    ("IoT-Sensor-3",   7,  4, 15, "energy"),
    ("IoT-Sensor-4",   5,  3, 15, "energy"),
    ("IoT-Sensor-5",  10,  5, 15, "energy"),
]

print("=" * 65)
print("MOSCA'S THEOREM ANALYSIS")
print("=" * 65)

# ── 1. Per-asset Mosca check ───────────────────────────────────────────────
print("\n=== PER-ASSET MOSCA CHECK (ZT=15 years) ===")
print(f"{'Asset':<14} {'DL':>4} {'MT':>4} {'DL+MT':>6} {'ZT':>4} "
      f"{'Gap':>6} {'Status'}")
print("-" * 65)

violated = 0
for (name, DL, MT, ZT, sec) in ASSETS:
    gap = (DL + MT) - ZT
    status = "RISK" if gap > 0 else "SAFE"
    if gap > 0:
        violated += 1
    print(f"{name:<14} {DL:>4} {MT:>4} {DL+MT:>6} {ZT:>4} "
          f"{gap:>6} {status}")

print(f"\nViolations: {violated}/50 ({100*violated/50:.0f}%)")

# ── 2. ZT sensitivity ─────────────────────────────────────────────────────
print(f"\n=== ZT SENSITIVITY (how ZT estimate affects % at risk) ===")
for zt in [10, 15, 20, 30]:
    v = sum(1 for (n, DL, MT, ZT, s) in ASSETS if DL + MT > zt)
    print(f"  ZT={zt:>2} years: {v:>2}/50 assets at risk ({100*v/50:.0f}%)")

# ── 3. Impossible scenario (ZT < MT) ──────────────────────────────────────
print(f"\n=== IMPOSSIBLE SCENARIO: ZT < MT ===")
print("When CRQC arrives before migration completes, full migration is")
print("impossible before Q-Day. Recommended action: immediate BITW.")
print()
impossible_cases = [
    ("Nuclear plant (ZT=5)",  20, 10,  5, "energy"),
    ("Large utility (ZT=8)",  30, 10,  8, "energy"),
    ("Legacy SCADA (ZT=10)",  25, 12, 10, "energy"),
]
for (desc, DL, MT, ZT, sec) in impossible_cases:
    gap = DL + MT - ZT
    impossible = ZT < MT
    print(f"  {desc}:")
    print(f"    DL+MT={DL+MT}, ZT={ZT} → Gap={gap} years")
    print(f"    Migration impossible before Q-Day: {impossible}")
    print(f"    Recommendation: BITW immediately + hardware refresh plan")
    print()

# ── 4. Save results ───────────────────────────────────────────────────────
with open("mosca_results.txt", "w") as f:
    f.write("MOSCA'S THEOREM ANALYSIS RESULTS\n\n")
    f.write("ZT SENSITIVITY\n")
    for zt in [10, 15, 20, 30]:
        v = sum(1 for (n,DL,MT,ZT,s) in ASSETS if DL+MT>zt)
        f.write(f"  ZT={zt}: {v}/50 ({100*v/50:.0f}%)\n")

print("Results saved to mosca_results.txt")
print("DONE.")
