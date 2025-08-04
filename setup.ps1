# Setup script for LLM Monitor (Windows PowerShell)

Write-Host "Setting up LLM Monitor..." -ForegroundColor Green

# Create virtual environment for backend
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
Set-Location backend
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location ..\frontend
npm install

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Cyan
Write-Host "  docker-compose up" -ForegroundColor White
Write-Host ""
Write-Host "Or run manually:" -ForegroundColor Cyan
Write-Host "  Backend: cd backend && .\venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "  Frontend: cd frontend && npm run dev" -ForegroundColor White

