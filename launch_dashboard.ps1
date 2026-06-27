# launch_dashboard.ps1
Write-Host "🚀 Lancement du dashboard GRN/Yusuf..." -ForegroundColor Green
Write-Host "📊 Ouverture du navigateur..." -ForegroundColor Yellow
Start-Process "http://localhost:8501"
streamlit run ui/dashboard.py
