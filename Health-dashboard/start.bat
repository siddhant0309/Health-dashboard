@echo off
echo Starting Cloud Health Dashboard...
echo.

echo Starting Backend Server...
cd backend
start "Backend Server" cmd /k "python app.py"
cd ..

echo.
echo Starting Frontend Server...
cd frontend
start "Frontend Server" cmd /k "npm start"
cd ..

echo.
echo Cloud Health Dashboard is starting up!
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul
