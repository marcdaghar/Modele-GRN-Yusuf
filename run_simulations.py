# run_simulations.py - Script simplifié

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("🚀 LANCEMENT DES SIMULATIONS GRN/YUSUF")
print("=" * 60)

print("\n📊 Simulation d'effondrement...")
from src.simulation.collapse_simulation import CollapseSimulator
simulator = CollapseSimulator()
simulator.simulate_interest_rate_crisis()
simulator.plot_scenarios('interest_crisis', 'debt')
simulator.analyze_collapse()

print("\n📊 Comparaison historique...")
from src.simulation.historical_comparison import HistoricalComparison
comparison = HistoricalComparison()
for name in comparison.historical_data.keys():
    comparison.simulate_crisis(name)
comparison.plot_comparison()
comparison.generate_report()

print("\n✅ Toutes les simulations sont terminées !")
