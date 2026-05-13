#!/bin/bash

# Navigate to the project root directory
cd "$(dirname "$0")"

echo "Starting Restaurant Booking System..."

# Set PYTHONPATH to the current directory so that 'backend' can be imported as a module
export PYTHONPATH=$PWD

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/Scripts/activate
else
    echo "Warning: Virtual environment not found in backend/.venv"
fi

# Run the backend in the background
echo "Running backend server at http://127.0.0.1:5000..."
python -m backend.run &

# Run the frontend server
echo "Running frontend server at http://127.0.0.1:5500..."
echo "Access the app at: http://127.0.0.1:5500/templates/customer/home.html"
python -m http.server 5500 --directory frontend