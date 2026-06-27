# ============================================================
# SIMULATION D'EFFONDREMENT DU SYSTÈME USURAIRE
# ============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.grn_model import GRNModel

class CollapseSimulator:
    """Simule différents scénarios d'effondrement systémique"""
    
    def __init__(self):
        self.scenarios = {}
        self.results = {}
    
    def create_scenario(self, name, params_modifier):
        """Crée un scénario en modifiant les paramètres"""
        model = GRNModel()
        for key, value in params_modifier.items():
            model.params[key] = value
        return model
    
    def simulate_interest_rate_crisis(self):
        """Simule une crise de taux d'intérêt"""
        scenarios = {
            'Normal': {},
            'Taux élevé': {'r': 0.15},
            'Taux très élevé': {'r': 0.25},
            'Taux extrême': {'r': 0.35}
        }
        
        results = {}
        for name, mod in scenarios.items():
            model = self.create_scenario(name, mod)
            results[name] = model.simulate()
            results[name]['model'] = model
        
        self.results['interest_crisis'] = results
        return results
    
    def simulate_ressource_depletion(self):
        """Simule l'épuisement des ressources"""
        scenarios = {
            'Normal': {'alpha': 0.01},
            'Dégradation rapide': {'alpha': 0.03},
            'Dégradation critique': {'alpha': 0.05},
            'Dégradation extrême': {'alpha': 0.08}
        }
        
        results = {}
        for name, mod in scenarios.items():
            model = self.create_scenario(name, mod)
            results[name] = model.simulate()
            results[name]['model'] = model
        
        self.results['ressource_depletion'] = results
        return results
    
    def simulate_confidence_collapse(self):
        """Simule un effondrement de confiance"""
        scenarios = {
            'Normal': {'C0': 0.8, 'lam': 0.1},
            'Choc de confiance': {'C0': 0.5, 'lam': 0.05},
            'Panique': {'C0': 0.3, 'lam': 0.02},
            'Effondrement total': {'C0': 0.1, 'lam': 0.01}
        }
        
        results = {}
        for name, mod in scenarios.items():
            model = self.create_scenario(name, mod)
            results[name] = model.simulate()
            results[name]['model'] = model
        
        self.results['confidence_collapse'] = results
        return results
    
    def plot_scenarios(self, scenario_type, variable='confidence'):
        """Visualise les différents scénarios"""
        if scenario_type not in self.results:
            print(f"Scénario {scenario_type} non trouvé")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        results = self.results[scenario_type]
        
        for idx, (name, data) in enumerate(results.items()):
            if idx >= 4:
                break
            ax = axes[idx]
            
            time = data['time']
            if variable == 'confidence':
                values = data['confidence']
                color = 'blue'
                title = 'Confiance'
            elif variable == 'debt':
                values = data['debt']
                color = 'red'
                title = 'Dette'
            elif variable == 'lambda':
                values = data['lambda']
                color = 'orange'
                title = 'Paramètre Lambda'
            else:
                values = data['stock']
                color = 'green'
                title = 'Stock'
            
            ax.plot(time, values, color=color, linewidth=2, label=name)
            ax.set_title(f"{title} - {name}")
            ax.set_xlabel('Temps')
            ax.set_ylabel(title)
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Ajout des seuils critiques
            if variable == 'confidence':
                ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.5)
            elif variable == 'lambda':
                ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.5)
            
            # Détection d'effondrement
            model = data['model']
            collapse = model.detect_collapse(data)
            if collapse and collapse['collapse_imminent']:
                ax.text(0.05, 0.95, '⚠️ EFFONDREMENT', 
                       transform=ax.transAxes, color='red',
                       fontsize=12, fontweight='bold',
                       bbox=dict(boxstyle="round", facecolor='white', alpha=0.8))
        
        plt.suptitle(f'Scénarios d\'effondrement - {scenario_type.replace("_", " ").title()}', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'collapse_scenario_{scenario_type}.png', dpi=150)
        plt.show()
    
    def analyze_collapse(self):
        """Analyse comparative des scénarios"""
        summary = []
        
        for scenario_type, results in self.results.items():
            for name, data in results.items():
                model = data['model']
                collapse = model.detect_collapse(data)
                
                summary.append({
                    'scenario': scenario_type,
                    'name': name,
                    'final_confidence': data['confidence'][-1],
                    'final_debt': data['debt'][-1],
                    'final_lambda': data['lambda'][-1],
                    'risk_score': collapse['risk_score'],
                    'collapse_imminent': collapse['collapse_imminent'],
                    'time_to_collapse': collapse['time_to_collapse']
                })
        
        df = pd.DataFrame(summary)
        print("\n=== ANALYSE COMPARATIVE DES SCÉNARIOS ===")
        print(df.to_string(index=False))
        return df

# Export explicite de la classe
__all__ = ['CollapseSimulator']

# ============================================================
# TEST DE LA SIMULATION
# ============================================================

if __name__ == "__main__":
    simulator = CollapseSimulator()
    
    print("🔄 Simulation de crises de taux d'intérêt...")
    simulator.simulate_interest_rate_crisis()
    
    print("🔄 Simulation d'épuisement des ressources...")
    simulator.simulate_ressource_depletion()
    
    print("🔄 Simulation d'effondrement de confiance...")
    simulator.simulate_confidence_collapse()
    
    # Visualisation
    print("\n📊 Visualisation des scénarios...")
    simulator.plot_scenarios('interest_crisis', 'debt')
    simulator.plot_scenarios('ressource_depletion', 'confidence')
    simulator.plot_scenarios('confidence_collapse', 'lambda')
    
    # Analyse
    summary = simulator.analyze_collapse()
