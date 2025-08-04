#!/bin/bash

# Setup script for LLM Monitor

echo "Setting up LLM Monitor..."

# Create virtual environment for backend
echo "Creating virtual environment..."
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd ../frontend
npm install

echo "Setup complete!"
echo ""
echo "To start the application:"
echo "  docker-compose up"
echo ""
echo "Or run manually:"
echo "  Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "  Frontend: cd frontend && npm run dev"

