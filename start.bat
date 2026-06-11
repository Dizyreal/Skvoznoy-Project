@echo off
title SKVOZNOY PROJECT - Launcher

echo.
echo ============================================
echo  SKVOZNOY PROJECT - Earthquake ETL Pipeline
echo ============================================
echo.

:: ---- Check / start Docker Desktop ----------------------------------------
docker info > nul 2>&1
if %errorlevel% equ 0 goto DOCKER_READY

echo [INFO] Docker Desktop is not running. Starting it now...

if exist "%PROGRAMFILES%\Docker\Docker\Docker Desktop.exe" (
    start "" "%PROGRAMFILES%\Docker\Docker\Docker Desktop.exe"
) else if exist "%LOCALAPPDATA%\Docker\Docker Desktop.exe" (
    start "" "%LOCALAPPDATA%\Docker\Docker Desktop.exe"
) else (
    echo [ERROR] Docker Desktop not found. Please install it.
    goto END_PAUSE
)

echo [INFO] Waiting for Docker Engine (up to 120 sec)...
set wait=0
:WAIT_DOCKER
timeout /t 5 /nobreak > nul
set /a wait=wait+5 >nul 2>&1
docker info > nul 2>&1
if %errorlevel% equ 0 goto DOCKER_READY
if %wait% gtr 120 (
    echo [ERROR] Docker did not start in 120 sec. Start it manually and retry.
    goto END_PAUSE
)
echo [INFO] Still waiting... (%wait% sec)
goto WAIT_DOCKER

:DOCKER_READY
echo [OK] Docker is running.

:: ---- Clean previous state (keep metabase settings, reset postgres) --------
echo.
echo [INFO] Stopping previous containers...
docker compose down > nul 2>&1

echo [INFO] Resetting postgres volume for a clean start...
docker volume rm skvoznoy_project_pgdata > nul 2>&1

:: ---- Start stack ----------------------------------------------------------
echo.
echo [1/3] Starting PostgreSQL...
docker compose up -d postgres
if %errorlevel% neq 0 goto DOCKER_ERROR

echo [2/3] Initializing Airflow (first run ~2 min)...
docker compose up airflow-init
if %errorlevel% neq 0 goto DOCKER_ERROR

echo [3/3] Starting Airflow webserver, scheduler and Metabase...
docker compose up -d airflow-webserver airflow-scheduler metabase
if %errorlevel% neq 0 goto DOCKER_ERROR

:: ---- Wait for Airflow webserver -------------------------------------------
echo.
echo [INFO] Waiting for Airflow Webserver (up to 90 sec)...
set attempts=0
:WAIT_AIRFLOW
set /a attempts=attempts+1 >nul 2>&1
if %attempts% gtr 18 goto SHOW_URLS
docker compose exec -T airflow-webserver curl -sf http://localhost:8080/health > nul 2>&1
if %errorlevel% equ 0 goto SHOW_URLS
echo [INFO] Not ready yet, retrying in 5 sec... (%attempts%/18)
timeout /t 5 /nobreak > nul
goto WAIT_AIRFLOW

:SHOW_URLS
echo.
echo ============================================
echo  All services are UP!
echo ============================================
echo.
echo  Airflow UI  :  http://localhost:8080
echo                 Login:     admin
echo                 Password:  admin
echo.
echo  Metabase BI :  http://localhost:3000
echo                 First-run DB setup (Add your data step):
echo                 Host=postgres   Port=5432
echo                 DB=analytics    User=student  PW=student_pw
echo                 NOTE: use "postgres" not "localhost" as host!
echo.
echo  PostgreSQL  :  localhost:5432
echo                 analytics db  -  student / student_pw
echo                 airflow db    -  student / student_pw
echo.
echo  To stop: run stop.bat
echo.
goto END_PAUSE

:DOCKER_ERROR
echo.
echo [ERROR] Failed to start. Run: docker compose logs
echo.

:END_PAUSE
pause
