# ============================================================
# MODÈLE GRN / YUSUF - VERSION CALIBRÉE
# ============================================================

import numpy as np
from scipy.integrate import odeint
from scipy.optimize import minimize
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

@dataclass
class CalibrationData:
    """Données historiques pour le calibrage"""
    years: np.ndarray
    debt: np.ndarray
    gdp: np.ndarray
    confidence: np.ndarray
    resources: np.ndarray

class GRNModel:
    """Modèle GRN (Grand Réseau Numérique) avec calibrage automatique"""
    
    def __init__(self, params=None):
        self.params = params or self.default_params()
        self.calibration_result = None
        self.history = []
        
    def default_params(self):
        """Paramètres par défaut calibrés sur données historiques"""
        return {
            'D0': 100.0,
            'r': 0.05,
            'E0': 1000.0,
            'alpha': 0.01,
            'V0': 50.0,
            'gamma': 1.2,
            'delta': 0.8,
            'P_floor': 80.0,
            'P_ceil': 120.0,
            'C0': 0.8,
            'lam': 0.1,
            'mu': 0.3,
            'theta_seuil': 0.6,
            'V_seuil': 30.0
        }
    
    def equations(self, state, t, params):
        """Équations différentielles du système"""
        D, E, V, C, M, S = state
        
        # Dette exponentielle
        dD_dt = params['r'] * D
        
        # Ressources
        dE_dt = -params['alpha'] * E
        
        # Entropie
        dS_dt = params['alpha'] * abs(dE_dt)
        
        # Stock (Yusuf)
        P_t = self._simulate_price(t)
        if P_t < params['P_floor']:
            dV_dt = 0.5 * (params['P_floor'] - P_t)
        elif P_t > params['P_ceil']:
            dV_dt = -0.3 * (P_t - params['P_ceil'])
        else:
            dV_dt = 0.0
        
        # Masse monétaire
        dM_dt = params['gamma'] * max(0, dV_dt) - params['delta'] * max(0, -dV_dt)
        
        # Confiance
        ratio_DM = D / max(M, 1e-6)
        dC_dt = params['lam'] * (1 - C) - params['mu'] * ratio_DM
        
        return [dD_dt, dE_dt, dV_dt, dC_dt, dM_dt, dS_dt]
    
    def _simulate_price(self, t):
        """Simulation du prix avec bruit et cycles"""
        base = 100 + 20 * np.sin(0.1 * t)
        noise = np.random.normal(0, 5) if t > 0 else 0
        return max(base + noise, 50)
    
    def simulate(self, t_max=200, n_points=2000):
        """Exécute la simulation"""
        t = np.linspace(0, t_max, n_points)
        
        state0 = [
            self.params['D0'],
            self.params['E0'],
            self.params['V0'],
            self.params['C0'],
            0.0,
            0.0
        ]
        
        solution = odeint(self.equations, state0, t, args=(self.params,))
        
        D, E, V, C, M, S = solution.T
        
        # Calcul du paramètre de bifurcation
        Lambda = self._compute_lambda(t, D, E)
        
        results = {
            'time': t,
            'debt': D,
            'resources': E,
            'stock': V,
            'confidence': C,
            'money': M,
            'entropy': S,
            'lambda': Lambda
        }
        
        self.history.append(results)
        return results
    
    def _compute_lambda(self, t, D, E):
        """Calcule le paramètre de bifurcation"""
        Lambda = np.zeros_like(t)
        for i in range(1, len(t)):
            dE_dt = (E[i] - E[i-1]) / (t[i] - t[i-1])
            if abs(dE_dt) > 1e-6:
                Lambda[i] = (D[i] * self.params['r']) / abs(dE_dt)
            else:
                Lambda[i] = np.inf
        return Lambda
    
    def calibrate(self, data: CalibrationData):
        """Calibre les paramètres sur des données historiques"""
        
        def objective(x):
            # Fonction de coût
            self.params['r'] = x[0]
            self.params['alpha'] = x[1]
            self.params['gamma'] = x[2]
            self.params['mu'] = x[3]
            
            results = self.simulate(t_max=data.years[-1], n_points=len(data.years))
            
            # Erreur quadratique moyenne
            debt_error = np.mean((results['debt'] - data.debt) ** 2)
            confidence_error = np.mean((results['confidence'] - data.confidence) ** 2)
            
            return debt_error + confidence_error
        
        # Paramètres initiaux
        x0 = [self.params['r'], self.params['alpha'], 
              self.params['gamma'], self.params['mu']]
        
        # Bornes
        bounds = [(0.01, 0.15), (0.001, 0.05), (0.5, 2.0), (0.1, 0.8)]
        
        # Optimisation
        result = minimize(objective, x0, bounds=bounds, method='L-BFGS-B')
        
        self.params['r'] = result.x[0]
        self.params['alpha'] = result.x[1]
        self.params['gamma'] = result.x[2]
        self.params['mu'] = result.x[3]
        
        self.calibration_result = result
        return result
    
    def detect_collapse(self, results=None):
        """Détecte les signes d'effondrement du système"""
        if results is None:
            results = self.history[-1] if self.history else None
            if results is None:
                return None
        
        # Utiliser les dernières valeurs du tableau
        debt_final = results['debt'][-1] if isinstance(results['debt'], np.ndarray) else results['debt']
        money_final = results['money'][-1] if isinstance(results['money'], np.ndarray) else results['money']
        confidence_final = results['confidence'][-1] if isinstance(results['confidence'], np.ndarray) else results['confidence']
        lambda_final = results['lambda'][-1] if isinstance(results['lambda'], np.ndarray) else results['lambda']
        stock_final = results['stock'][-1] if isinstance(results['stock'], np.ndarray) else results['stock']
        
        collapse_indicators = {
            'confidence_break': confidence_final < 0.5,
            'lambda_critical': lambda_final > 1.0,
            'stock_depletion': stock_final < self.params['V_seuil'],
            'debt_to_money_ratio': debt_final / max(money_final, 1) > 5
        }
        
        # Score de risque
        risk_score = sum([
            collapse_indicators['confidence_break'] * 0.3,
            collapse_indicators['lambda_critical'] * 0.3,
            collapse_indicators['stock_depletion'] * 0.2,
            collapse_indicators['debt_to_money_ratio'] * 0.2
        ])
        
        # Vérifier si les indicateurs sont des booléens Python
        if isinstance(risk_score, (np.bool_, bool)):
            risk_score = float(risk_score)
        
        return {
            'indicators': collapse_indicators,
            'risk_score': risk_score,
            'collapse_imminent': risk_score > 0.6,
            'time_to_collapse': self._estimate_time_to_collapse(results)
        }
    
    def _estimate_time_to_collapse(self, results):
        """Estime le temps restant avant effondrement"""
        if len(results['confidence']) < 2:
            return None
        
        # Taux de déclin de la confiance
        conf_trend = np.polyfit(
            results['time'][-100:], 
            results['confidence'][-100:], 
            1
        )[0]
        
        if conf_trend >= 0:
            return None
        
        # Temps jusqu'à ce que la confiance atteigne 0.3
        time_to_collapse = (0.3 - results['confidence'][-1]) / conf_trend
        return max(time_to_collapse, 0)

# Export explicite des classes
__all__ = ['GRNModel', 'CalibrationData']

# ============================================================
# TEST DU MODÈLE CALIBRÉ
# ============================================================

if __name__ == "__main__":
    # Données synthétiques pour test
    years = np.arange(0, 100)
    debt = 100 * np.exp(0.03 * years) + 50 * np.random.randn(len(years))
    confidence = 0.8 - 0.004 * years + 0.1 * np.sin(0.1 * years)
    resources = 1000 - 10 * years
    
    data = CalibrationData(years, debt, confidence, resources, resources)
    
    model = GRNModel()
    print("Calibration en cours...")
    model.calibrate(data)
    
    results = model.simulate()
    collapse = model.detect_collapse(results)
    
    print("\n=== RÉSULTATS DE SIMULATION ===")
    print(f"Confiance finale: {results['confidence'][-1]:.3f}")
    print(f"Paramètre de bifurcation: {results['lambda'][-1]:.3f}")
    print(f"Risque d'effondrement: {collapse['risk_score']:.2%}")
    print(f"Effondrement imminent: {collapse['collapse_imminent']}")
