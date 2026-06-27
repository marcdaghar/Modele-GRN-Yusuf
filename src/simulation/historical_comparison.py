# ============================================================
# COMPARAISON AVEC DES CRISES FINANCIÈRES HISTORIQUES
# ============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.grn_model import GRNModel

class HistoricalComparison:
    """Compare le modèle avec des crises financières historiques"""
    
    def __init__(self):
        self.historical_data = self._load_historical_data()
        self.comparisons = {}
    
    def _load_historical_data(self):
        """Charge les données de crises historiques"""
        return {
            'Great_Depression_1929': {
                'years': np.arange(1929, 1939),
                'debt_change': np.array([0, -5, -10, -15, -20, -15, -10, -5, 0, 5]),
                'confidence': np.array([0.8, 0.6, 0.4, 0.3, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7]),
                'description': 'Grande Dépression (1929-1939)'
            },
            'Oil_Shock_1973': {
                'years': np.arange(1973, 1983),
                'debt_change': np.array([0, 5, 10, 15, 20, 25, 20, 15, 10, 5]),
                'confidence': np.array([0.8, 0.7, 0.6, 0.5, 0.4, 0.35, 0.4, 0.5, 0.6, 0.7]),
                'description': 'Choc pétrolier (1973-1983)'
            },
            'Dotcom_2000': {
                'years': np.arange(2000, 2010),
                'debt_change': np.array([0, 5, 10, 5, 0, -5, -10, -5, 0, 5]),
                'confidence': np.array([0.8, 0.7, 0.5, 0.4, 0.35, 0.4, 0.5, 0.6, 0.7, 0.75]),
                'description': 'Bulles Dotcom (2000-2010)'
            },
            'Subprime_2008': {
                'years': np.arange(2008, 2018),
                'debt_change': np.array([0, 10, 20, 30, 40, 35, 30, 25, 20, 15]),
                'confidence': np.array([0.8, 0.6, 0.3, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7]),
                'description': 'Crise Subprime (2008-2018)'
            },
            'Covid_2020': {
                'years': np.arange(2020, 2025),
                'debt_change': np.array([0, 15, 30, 25, 20]),
                'confidence': np.array([0.8, 0.5, 0.4, 0.5, 0.6]),
                'description': 'Pandémie COVID-19 (2020-2025)'
            }
        }
    
    def simulate_crisis(self, crisis_name, t_max=100):
        """Simule une crise à partir de données historiques"""
        if crisis_name not in self.historical_data:
            print(f"Crise {crisis_name} non trouvée")
            return None
        
        data = self.historical_data[crisis_name]
        
        # Création du modèle adapté
        model = GRNModel()
        
        # Ajustement des paramètres pour correspondre à la crise
        if 'debt_change' in data:
            # Calcul du taux d'intérêt effectif à partir des données
            debt_growth = np.gradient(data['debt_change'])
            positive_growth = debt_growth[debt_growth > 0]
            if len(positive_growth) > 0:
                model.params['r'] = max(0.05 + 0.01 * np.mean(positive_growth), 0.01)
        
        # Adaptation de la confiance
        if 'confidence' in data:
            conf_data = data['confidence']
            model.params['C0'] = conf_data[0]
            if len(conf_data) > 1:
                diff_conf = np.diff(conf_data)
                if np.all(conf_data[:-1] != 0):
                    model.params['lam'] = 0.15 * (1 - np.mean(diff_conf / conf_data[:-1]))
                    model.params['lam'] = max(model.params['lam'], 0.01)
        
        # Simulation
        results = model.simulate(t_max=t_max)
        results['crisis_name'] = crisis_name
        results['description'] = data.get('description', crisis_name)
        results['model'] = model
        
        self.comparisons[crisis_name] = results
        return results
    
    def plot_comparison(self):
        """Visualise la comparaison avec les crises historiques"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        colors = {
            'Great_Depression_1929': 'red',
            'Oil_Shock_1973': 'orange',
            'Dotcom_2000': 'green',
            'Subprime_2008': 'blue',
            'Covid_2020': 'purple'
        }
        
        # Simulation de toutes les crises
        for name in self.historical_data.keys():
            if name not in self.comparisons:
                self.simulate_crisis(name)
        
        # Graphique 1: Évolution de la confiance
        ax = axes[0, 0]
        for name, data in self.comparisons.items():
            hist_data = self.historical_data[name]
            max_len = len(hist_data.get('years', data['time']))
            time = data['time'][:max_len]
            confidence = data['confidence'][:len(time)]
            ax.plot(time, confidence, color=colors.get(name, 'gray'), 
                   linewidth=2, label=data.get('description', name))
        ax.set_title('Évolution de la confiance dans les crises')
        ax.set_xlabel('Temps')
        ax.set_ylabel('Confiance')
        ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.5)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Graphique 2: Dette
        ax = axes[0, 1]
        for name, data in self.comparisons.items():
            hist_data = self.historical_data[name]
            max_len = len(hist_data.get('years', data['time']))
            time = data['time'][:max_len]
            debt = data['debt'][:len(time)]
            ax.plot(time, debt, color=colors.get(name, 'gray'), 
                   linewidth=2, label=data.get('description', name))
        ax.set_title('Évolution de la dette')
        ax.set_xlabel('Temps')
        ax.set_ylabel('Dette')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Graphique 3: Paramètre de bifurcation
        ax = axes[1, 0]
        for name, data in self.comparisons.items():
            hist_data = self.historical_data[name]
            max_len = len(hist_data.get('years', data['time']))
            time = data['time'][:max_len]
            lambda_val = data['lambda'][:len(time)]
            # Filtrage des infinis
            lambda_val = np.clip(lambda_val, 0, 10)
            ax.plot(time, lambda_val, color=colors.get(name, 'gray'), 
                   linewidth=2, label=data.get('description', name))
        ax.set_title('Paramètre de bifurcation')
        ax.set_xlabel('Temps')
        ax.set_ylabel('Lambda')
        ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.5)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Graphique 4: Stock
        ax = axes[1, 1]
        for name, data in self.comparisons.items():
            hist_data = self.historical_data[name]
            max_len = len(hist_data.get('years', data['time']))
            time = data['time'][:max_len]
            stock = data['stock'][:len(time)]
            ax.plot(time, stock, color=colors.get(name, 'gray'), 
                   linewidth=2, label=data.get('description', name))
        ax.set_title('Stock (Principe de Yusuf)')
        ax.set_xlabel('Temps')
        ax.set_ylabel('Stock')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.suptitle('Comparaison Modèle GRN vs Crises Financières Historiques', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig('historical_comparison.png', dpi=150)
        plt.show()
    
    def generate_report(self):
        """Génère un rapport de comparaison"""
        report = []
        
        for name, data in self.comparisons.items():
            hist = self.historical_data[name]
            model = data['model']
            collapse = model.detect_collapse(data)
            
            max_len = len(hist.get('years', data['time']))
            conf_min = data['confidence'][:max_len].min()
            debt_max = data['debt'][:max_len].max()
            lambda_max = np.clip(data['lambda'][:max_len], 0, 10).max()
            
            report.append({
                'Crise': hist.get('description', name),
                'Confiance min': f"{conf_min:.3f}",
                'Dette max': f"{debt_max:.3f}",
                'Lambda max': f"{lambda_max:.3f}",
                'Risque': f"{collapse['risk_score']:.1%}",
                'Récupération possible': "Oui" if collapse['risk_score'] < 0.7 else "Non"
            })
        
        df = pd.DataFrame(report)
        print("\n=== COMPARAISON AVEC LES CRISES HISTORIQUES ===")
        print(df.to_string(index=False))
        return df

# Export explicite de la classe
__all__ = ['HistoricalComparison']

# ============================================================
# EXÉCUTION DE LA COMPARAISON
# ============================================================

if __name__ == "__main__":
    comparison = HistoricalComparison()
    
    print("🔄 Simulation des crises historiques...")
    for name in comparison.historical_data.keys():
        comparison.simulate_crisis(name)
    
    print("📊 Génération des graphiques...")
    comparison.plot_comparison()
    
    print("📝 Génération du rapport...")
    comparison.generate_report()
