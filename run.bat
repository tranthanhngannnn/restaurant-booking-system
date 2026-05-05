@echo off
set PYTHONPATH=%cd%
echo Starting Restaurant Booking System...
if exist backend\.venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call backend\.venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found in backend\.venv
)
echo Running backend and frontend...
set PYTHONPATH=%cd%

:: Start Backend in a new window
start "Backend Server" cmd /c "if exist backend\.venv\Scripts\activate.bat (call backend\.venv\Scripts\activate.bat) & python -m backend.run"

:: Start Frontend in a new window
start "Frontend Server" cmd /c "echo Running frontend server at http://127.0.0.1:5500... & python -m http.server 5500 --directory frontend"

echo.
echo Servers are starting!
echo Backend: http://127.0.0.1:5000
echo Frontend: http://127.0.0.1:5500/templates/customer/home.html
echo.
pause
