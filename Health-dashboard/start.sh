#!/bin/bash

echo "Starting Cloud Health Dashboard..."
echo

echo "Starting Backend Server..."
cd backend
gnome-terminal --title="Backend Server" -- bash -c "python app.py; exec bash" &
cd ..

echo
echo "Starting Frontend Server..."
cd frontend
gnome-terminal --title="Frontend Server" -- bash -c "npm start; exec bash" &
cd ..

echo
echo "Cloud Health Dashboard is starting up!"
echo
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo
echo "Press Ctrl+C to stop all servers"
echo

# Wait for user to stop
trap 'echo "Stopping servers..."; pkill -f "python app.py"; pkill -f "npm start"; exit' INT
wait
