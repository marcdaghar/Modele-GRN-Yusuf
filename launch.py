# launch.py - Script de lancement pour les simulations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_collapse_simulation():
    from src.simulation.collapse_simulation import CollapseSimulator
    simulator = CollapseSimulator()
    simulator.simulate_interest_rate_crisis()
    simulator.plot_scenarios('interest_crisis', 'debt')
    simulator.analyze_collapse()

def run_historical_comparison():
    from src.simulation.historical_comparison import HistoricalComparison
    comparison = HistoricalComparison()
    for name in comparison.historical_data.keys():
        comparison.simulate_crisis(name)
    comparison.plot_comparison()
    comparison.generate_report()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "collapse":
            run_collapse_simulation()
        elif sys.argv[1] == "historical":
            run_historical_comparison()
        elif sys.argv[1] == "all":
            run_collapse_simulation()
            run_historical_comparison()
        else:
            print("Usage: python launch.py [collapse|historical|all]")
    else:
        print("Usage: python launch.py [collapse|historical|all]")
