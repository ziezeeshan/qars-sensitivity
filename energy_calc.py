"""
STM32F407 Energy Consumption Analysis
======================================
Paper: Post-Quantum Cryptography Migration Frameworks for Critical
       Infrastructure: A Systematic Literature Review and Strategic Roadmap
Author: Muhammad Zeeshan, Air University, Multan, Pakistan

Source: STM32F407 Datasheet, Doc ID 022152 Rev 8, Table 24
        pqm4 benchmark: ML-DSA-65 signing = 134 ms @ 24 MHz

Formula:
    E = V × I × t
    Signs per battery = (capacity_Ah × V_battery × 3600 J/Wh) / E_joules

Note: 3.3V is the TYPICAL operating voltage per datasheet.
      1.8V is the MINIMUM voltage (not typical).
      Original paper incorrectly used 1.8V as the baseline.
"""

# ── Constants from datasheet and pqm4 ──────────────────────────────────────
I_ACTIVE_A    = 0.050     # 50 mA active run current (Table 24, 24 MHz)
T_SIGN_S      = 0.134     # 134 ms ML-DSA-65 signing time (pqm4 v2024.01)
BATTERY_MAH   = 1000      # 1000 mAh reference battery
BATTERY_V     = 3.7       # Nominal Li-ion battery voltage

print("=" * 60)
print("STM32F407 ENERGY SENSITIVITY ANALYSIS")
print("=" * 60)
print(f"\nActive current (datasheet Table 24, 24 MHz): {I_ACTIVE_A*1000:.0f} mA")
print(f"Signing time (pqm4 ML-DSA-65):               {T_SIGN_S*1000:.0f} ms")
print(f"Reference battery:                           {BATTERY_MAH} mAh @ {BATTERY_V} V")

# ── Compute energy and battery life across voltage range ───────────────────
print(f"\n{'Voltage':>10} | {'Energy (mJ)':>12} | {'Signs/1000mAh':>15}")
print("-" * 45)

results = []
for V_supply in [1.8, 3.0, 3.3]:
    # Energy per signing operation (Joules)
    E_joules = V_supply * I_ACTIVE_A * T_SIGN_S

    # Battery capacity in Joules
    # 1000 mAh = 1 Ah; Energy = 1 Ah × 3.7 V × 3600 s/h = 13,320 J
    battery_joules = (BATTERY_MAH / 1000) * BATTERY_V * 3600

    # Number of signatures per full battery charge
    n_signs = battery_joules / E_joules

    E_mJ = E_joules * 1000
    results.append((V_supply, E_mJ, n_signs))
    print(f"{V_supply:>8.1f} V | {E_mJ:>12.1f} | {n_signs:>15.3e}")

print(f"\nNOTE: 3.3 V (typical) is the correct reference value.")
print(f"      At 3.3 V: {results[2][1]:.1f} mJ per signing operation.")
print(f"      Battery depletion for daily signing:")

for (V, E_mJ, n_signs) in results:
    for signs_per_day in [100, 1000, 10000]:
        days = n_signs / signs_per_day
        print(f"  {V}V, {signs_per_day:>6} signs/day → {days:>10.1f} days "
              f"({days/365:.1f} years)")

# ── Save results ───────────────────────────────────────────────────────────
with open("energy_results.txt", "w") as f:
    f.write("STM32F407 ENERGY SENSITIVITY RESULTS\n")
    f.write(f"Current: {I_ACTIVE_A*1000:.0f} mA (datasheet Table 24)\n")
    f.write(f"Time:    {T_SIGN_S*1000:.0f} ms (pqm4 ML-DSA-65)\n\n")
    f.write(f"{'Voltage':>8} | {'Energy_mJ':>10} | {'Signs/1000mAh':>14}\n")
    f.write("-" * 40 + "\n")
    for (V, E_mJ, n_signs) in results:
        f.write(f"{V:>6.1f} V | {E_mJ:>10.1f} | {n_signs:>14.3e}\n")

print("\nResults saved to energy_results.txt")
print("DONE.")
