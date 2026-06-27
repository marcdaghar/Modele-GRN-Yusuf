# run.ps1 - Script de lancement pour le projet GRN/Yusuf

param(
    [string] = "dashboard"
)

switch () {
    "dashboard" {
        Write-Host "🚀 Lancement du dashboard Streamlit..." -ForegroundColor Green
        streamlit run ui/dashboard.py
    }
    "simulate" {
        Write-Host "🔄 Lancement de la simulation d'effondrement..." -ForegroundColor Yellow
        python src/simulation/collapse_simulation.py
    }
    "historical" {
        Write-Host "📊 Comparaison avec les crises historiques..." -ForegroundColor Cyan
        python src/simulation/historical_comparison.py
    }
    "deploy" {
        Write-Host "🔨 Déploiement du smart contract sur Sepolia..." -ForegroundColor Magenta
        python scripts/deploy_testnet.py
    }
    "test" {
        Write-Host "🧪 Exécution des tests..." -ForegroundColor White
        pytest tests/
    }
    default {
        Write-Host "Usage: .\run.ps1 [dashboard|simulate|historical|deploy|test]" -ForegroundColor Red
    }
}
