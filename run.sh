#!/bin/bash

# Function to stop background processes on script exit
cleanup() {
    echo "Stopping all processes..."
    kill $(jobs -p) 2>/dev/null
    exit
}

# Set up trap to catch script termination
trap cleanup EXIT INT TERM

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python3 to continue."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3 to continue."
    exit 1
fi

# Create virtual environments if they don't exist
if [ ! -d "backend/venv" ]; then
    echo "Creating backend virtual environment..."
    python3 -m venv backend/venv
fi

if [ ! -d "frontend/venv" ]; then
    echo "Creating frontend virtual environment..."
    python3 -m venv frontend/venv
fi

# Install backend dependencies
echo "Installing backend dependencies..."
source backend/venv/bin/activate
pip install -r backend/requirements.txt
deactivate

# Install frontend dependencies
echo "Installing frontend dependencies..."
source frontend/venv/bin/activate
pip install -r frontend/requirements.txt
deactivate

# Start backend
echo "Starting backend server..."
source backend/venv/bin/activate
cd backend && python app.py &
deactivate


echo $(pwd)
# Start frontend
echo "Starting frontend server..."
source frontend/venv/bin/activate
cd frontend && chainlit run main.py &
cd ..


# Wait for both processes
echo "Both servers are running..."
echo "Press Ctrl+C to stop both servers"
wait 