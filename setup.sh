#!/bin/bash

echo "Setting up the project..."

# check for Python executable
PYTHON_CMD=""

if command -v python3 &>/dev/null; then
  PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
  PYTHON_CMD="python"
else
  echo "Error: Python is not installed or not available in PATH!"
  exit 1
fi

# install Python dependencies
if [ -f "requirements.txt" ]; then
  echo "Installing Python dependencies using $PYTHON_CMD..."
  $PYTHON_CMD -m pip install -r requirements.txt
else
  echo "Error: requirements.txt not found in the root directory!"
  exit 1
fi

# install Node.js dependencies in the React app directory
if [ -d "mapInterface" ]; then
  echo "Installing Node.js dependencies for React app..."
  cd mapInterface && npm install
  cd .. 
else
  echo "Error: React app directory 'mapInterface' not found!"
  exit 1
fi

# check if port 5000 is in use
if lsof -i:5000 > /dev/null; then
  echo "Port 5000 is already in use. Stopping the current process..."
  # kill the process using the port
  lsof -i:5000 | awk 'NR>1 {print $2}' | xargs kill -9
  echo "Port 5000 has been cleared."
fi

# start Flask backend
echo "Starting Flask backend using $PYTHON_CMD..."
$PYTHON_CMD main.py & # Run Flask backend in the background

# wait for Flask backend to initialize
sleep 20

# start React frontend
if [ -d "mapInterface" ]; then
  echo "Starting React frontend..."
  cd mapInterface
  npm run start
else
  echo "Error: React app directory 'mapInterface' not found!"
  exit 1
fi

# keep script running to allow Flask to remain active
wait
