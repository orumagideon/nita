#!/bin/bash

# NITA Dashboard Setup Script
# This script automates the initial setup process

set -e

echo "🚀 NITA Dashboard Setup Script"
echo "=============================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 14 or higher."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

echo "✅ All prerequisites are met!"
echo ""

# Backend setup
echo "🔧 Setting up Backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

cd ..
echo "✅ Backend setup complete!"
echo ""

# Frontend setup
echo "🎨 Setting up Frontend..."
cd frontend

echo "Installing dependencies..."
npm install

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

cd ..
echo "✅ Frontend setup complete!"
echo ""

# Summary
echo "📝 Setup Summary"
echo "================="
echo ""
echo "✅ Backend environment: backend/venv"
echo "✅ Frontend dependencies: frontend/node_modules"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. Add your Google Service Account JSON:"
echo "   cp ~/Downloads/your-key-file.json ./backend/service_account.json"
echo ""
echo "2. Share your Google Sheet with the service account email:"
echo "   - Open the JSON file and find 'client_email'"
echo "   - Share your sheet with that email address"
echo ""
echo "3. Run the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "4. In a new terminal, run the frontend:"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "5. Open http://localhost:3000 in your browser"
echo ""
echo "📚 For more information, see README.md"
echo ""
