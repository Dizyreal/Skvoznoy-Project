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

echo [INFO] Найдена Conda по пути: %CONDA_PATH%

"%CONDA_PATH%" env list | findstr /C:"%ENV_NAME%" >nul
if %errorlevel% equ 0 (
    echo [INFO] Окружение '%ENV_NAME%' уже существует. Пропускаем создание.
) else (
    echo [INFO] Создаем окружение '%ENV_NAME%' с Python %PYTHON_VER%...
    :: Добавлено "|| ver >nul" для игнорирования ложного кода ошибки от conda.exe
    "%CONDA_PATH%" create -n %ENV_NAME% python=%PYTHON_VER% -y || ver >nul
)

echo [INFO] Установка зависимостей из requirements.txt...
if exist "..\requirements.txt" (
    "%CONDA_PATH%" run -n %ENV_NAME% python -m pip install -r ..\requirements.txt || ver >nul
) else if exist "requirements.txt" (
    "%CONDA_PATH%" run -n %ENV_NAME% python -m pip install -r requirements.txt || ver >nul
) else (
    echo [WARNING] Файл requirements.txt не найден, ставим pandas напрямую.
    "%CONDA_PATH%" run -n %ENV_NAME% python -m pip install pandas || ver >nul
)

echo [INFO] Запуск smoke-теста (broken_env.py)...
if exist "..\broken_env.py" (
    "%CONDA_PATH%" run -n %ENV_NAME% python ..\broken_env.py
) else if exist "broken_env.py" (
    "%CONDA_PATH%" run -n %ENV_NAME% python broken_env.py
) else (
    echo [ERROR] Файл broken_env.py не найден для теста!
    goto END_PAUSE
)

if %errorlevel% equ 0 (
    echo [OK] Настройка окружения успешно завершена!
) else (
    echo [ERROR] Smoke-тест упал с ошибкой.
)

:END_PAUSE
echo.
echo Нажмите любую клавишу для выхода из скрипта...
pause > nul
