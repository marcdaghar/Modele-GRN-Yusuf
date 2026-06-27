import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Test d'import des modules...")

try:
    from src.models.grn_model import GRNModel
    print("✅ GRNModel importé")
except Exception as e:
    print(f"❌ Erreur GRNModel: {e}")

try:
    from src.simulation.collapse_simulation import CollapseSimulator
    print("✅ CollapseSimulator importé")
except Exception as e:
    print(f"❌ Erreur CollapseSimulator: {e}")

try:
    from src.simulation.historical_comparison import HistoricalComparison
    print("✅ HistoricalComparison importé")
except Exception as e:
    print(f"❌ Erreur HistoricalComparison: {e}")

print("Test terminé.")
