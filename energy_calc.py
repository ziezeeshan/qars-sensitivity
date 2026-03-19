# STM32F407 Energy Sensitivity Analysis
# Source: STM32F407 Datasheet Table 24, active run mode 24MHz

I = 0.050   # 50mA active current from datasheet
t = 0.134   # 134ms = ML-DSA-65 signing time from pqm4

print("=== STM32F407 ENERGY ANALYSIS ===")
print(f"Active current (datasheet): {I*1000:.0f} mA")
print(f"Signing time (pqm4):        {t*1000:.0f} ms\n")

results = []
for V in [1.8, 3.0, 3.3]:
    E_mJ = V * I * t * 1000
    capacity_J = 1000 * 3.7 * 3.6
    signs = capacity_J / (E_mJ / 1000)
    results.append((V, E_mJ, signs))
    print(f"{V}V: Energy = {E_mJ:.1f} mJ | Signs per 1000mAh = {signs:.2e}")

with open("energy_results.txt", "w") as f:
    f.write("=== ENERGY SENSITIVITY RESULTS ===\n")
    f.write(f"Current: {I*1000:.0f}mA (STM32F407 datasheet)\n")
    f.write(f"Time: {t*1000:.0f}ms (pqm4 benchmark)\n\n")
    for V, E, S in results:
        f.write(f"{V}V: {E:.1f} mJ, ~{S:.2e} signatures/1000mAh\n")

print("\nSaved to energy_results.txt")

