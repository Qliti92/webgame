@echo off
echo ========================================
echo    RESTART GAME TOPUP SERVER
echo ========================================
echo.

REM Check if running with Docker or local
if exist "docker-compose.yml" (
    echo [1] Docker mode
    echo [2] Local development mode
    echo.
    set /p mode="Select mode (1 or 2): "
) else (
    set mode=2
)

if "%mode%"=="1" (
    echo.
    echo [*] Stopping Docker containers...
    docker-compose down

    echo.
    echo [*] Building and starting containers...
    docker-compose up --build -d

    echo.
    echo [*] Waiting for database to be ready...
    timeout /t 5 /nobreak >nul

    echo.
    echo [*] Running migrations...
    docker-compose exec web python manage.py migrate

    echo.
    echo [*] Collecting static files...
    docker-compose exec web python manage.py collectstatic --noinput

    echo.
    echo ========================================
    echo    SERVER STARTED (Docker)
    echo    Access: http://localhost
    echo ========================================
) else (
    echo.
    echo [*] Stopping any running Django server...
    taskkill /F /IM python.exe 2>nul

    echo.
    echo [*] Changing to backend directory...
    cd /d "%~dp0backend"

    echo.
    echo [*] Installing/updating dependencies...
    pip install -r requirements.txt -q

    echo.
    echo [*] Running migrations...
    python manage.py migrate

    echo.
    echo [*] Starting development server...
    echo.
    echo ========================================
    echo    SERVER STARTING (Local)
    echo    Access: http://localhost:8000
    echo    Press Ctrl+C to stop
    echo ========================================
    echo.
    python manage.py runserver 0.0.0.0:8000
)

pause
