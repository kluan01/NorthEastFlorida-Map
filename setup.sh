#!/bin/bash

echo "Setting up the project..."

# Check for Python executable
PYTHON_CMD=""

if command -v python3 &>/dev/null; then
  PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
  PYTHON_CMD="python"
else
  echo "Error: Python is not installed or not available in PATH!"
  exit 1
fi

# Install Python dependencies
if [ -f "requirements.txt" ]; then
  echo "Installing Python dependencies using $PYTHON_CMD..."
  $PYTHON_CMD -m pip install -r requirements.txt
else
  echo "Error: requirements.txt not found in the root directory!"
  exit 1
fi

# Install Node.js dependencies in the React app directory
if [ -d "mapInterface" ]; then
  echo "Installing Node.js dependencies for React app..."
  cd mapInterface && npm install
  cd .. # Return to the root directory after installing React dependencies
else
  echo "Error: React app directory 'mapInterface' not found!"
  exit 1
fi

# Start Flask backend
echo "Starting Flask backend using $PYTHON_CMD..."
$PYTHON_CMD main.py & # Run Flask backend in the background

# Start React frontend
if [ -d "mapInterface" ]; then
  echo "Starting React frontend..."
  cd mapInterface
  npm run start
else
  echo "Error: React app directory 'mapInterface' not found!"
  exit 1
fi

# Keep script running if necessary (for Flask to remain active)
wait
