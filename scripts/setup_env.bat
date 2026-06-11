@echo off
chcp 65001 > nul
set "ENV_NAME=my_project_env"
set "PYTHON_VER=3.10"

echo [INFO] Ищем установку Conda...

if exist "%USERPROFILE%\miniconda3\Scripts\conda.exe" (
    set "CONDA_PATH=%USERPROFILE%\miniconda3\Scripts\conda.exe"
) else if exist "%USERPROFILE%\anaconda3\Scripts\conda.exe" (
    set "CONDA_PATH=%USERPROFILE%\anaconda3\Scripts\conda.exe"
) else if exist "C:\ProgramData\miniconda3\Scripts\conda.exe" (
    set "CONDA_PATH=C:\ProgramData\miniconda3\Scripts\conda.exe"
) else if exist "C:\ProgramData\anaconda3\Scripts\conda.exe" (
    set "CONDA_PATH=C:\ProgramData\anaconda3\Scripts\conda.exe"
) else (
    where conda >nul 2>nul
    if %errorlevel% equ 0 (
        set "CONDA_PATH=conda"
    ) else (
        echo [ERROR] Conda не найдена! Установите Miniconda/Anaconda.
        goto END_PAUSE
    )
)

echo [INFO] Найдена Conda: %CONDA_PATH%

"%CONDA_PATH%" env list | findstr /C:"%ENV_NAME%" >nul
if %errorlevel% equ 0 (
    echo [INFO] Окружение '%ENV_NAME%' уже существует. Пропускаем создание.
) else (
    echo [INFO] Создаем окружение '%ENV_NAME%' (Python %PYTHON_VER%)...
    "%CONDA_PATH%" create -n %ENV_NAME% python=%PYTHON_VER% -y || ver >nul
)

echo [INFO] Устанавливаем зависимости из requirements.txt...
if exist "..\requirements.txt" (
    "%CONDA_PATH%" run -n %ENV_NAME% python -m pip install -r ..\requirements.txt || ver >nul
) else if exist "requirements.txt" (
    "%CONDA_PATH%" run -n %ENV_NAME% python -m pip install -r requirements.txt || ver >nul
) else (
    echo [WARNING] Файл requirements.txt не найден.
    goto END_PAUSE
)

echo [INFO] Запуск smoke-теста...
if exist "..\scripts\smoke_test.py" (
    "%CONDA_PATH%" run -n %ENV_NAME% python ..\scripts\smoke_test.py
) else if exist "smoke_test.py" (
    "%CONDA_PATH%" run -n %ENV_NAME% python smoke_test.py
) else (
    echo [ERROR] Файл smoke_test.py не найден!
    goto END_PAUSE
)

if %errorlevel% equ 0 (
    echo.
    echo [OK] Окружение готово к работе!
) else (
    echo [ERROR] Smoke-тест завершился с ошибкой.
)

:END_PAUSE
echo.
echo Нажмите любую клавишу для выхода...
pause > nul
