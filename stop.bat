@echo off
title SKVOZNOY PROJECT - Stop

echo.
echo [INFO] Stopping all project containers...
docker compose down
if %errorlevel% equ 0 (
    echo [OK] All containers stopped.
) else (
    echo [WARN] Docker may not be running or containers already stopped.
)
echo.
pause
