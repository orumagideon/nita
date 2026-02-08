#!/bin/bash

# NITA Dashboard Development Startup Script
# This script starts both backend and frontend servers

echo "🚀 Starting NITA Dashboard (Development Mode)"
echo "============================================="
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Backend
echo "🔧 Starting Backend Server..."
cd backend

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

source venv/bin/activate || . venv/Scripts/activate

# Check if service_account.json exists
if [ ! -f "service_account.json" ]; then
    echo "⚠️  WARNING: service_account.json not found!"
    echo "The API will not be able to connect to Google Sheets."
    echo "Please copy your credentials to backend/service_account.json"
fi

uvicorn main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   Backend logs: backend.log"
echo ""

cd ..

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 3

# Start Frontend
echo "🎨 Starting Frontend Server..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

npm start &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo ""

# Display URLs
echo "📱 Dashboard URLs:"
echo "===================="
echo "Frontend:  http://localhost:3000"
echo "Backend:   http://localhost:8000"
echo "API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Keep the script running
wait
