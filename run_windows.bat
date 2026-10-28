@echo off
setlocal enabledelayedexpansion

title AI Document Comparison Assistant - Launcher
echo ==============================================================================
echo           AI DOCUMENT COMPARISON ASSISTANT - WINDOWS 11 LAUNCHER
echo                 Xpert Champs AI Engineering Internship
echo ==============================================================================
echo.

:: 1. Check Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not found in system PATH.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/5] Python installation detected:
python --version
echo.

:: 2. Create or verify Virtual Environment
if not exist "venv" (
    echo [2/5] Creating isolated virtual environment in .\venv ...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo [2/5] Existing virtual environment found in .\venv.
)
echo.

:: 3. Activate Virtual Environment
echo [3/5] Activating virtual environment ...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)
echo Environment activated.
echo.

:: 4. Install Dependencies
echo [4/5] Checking and installing required dependencies from requirements.txt ...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Package installation failed. Please check your internet connection.
    pause
    exit /b 1
)
echo All dependencies are up to date.
echo.

:: 5. Check .env Configuration
if not exist ".env" (
    echo [NOTICE] '.env' file not found. Copying '.env.example' to '.env' ...
    copy .env.example .env >nul
    echo.
    echo [IMPORTANT] A template '.env' file has been created.
    echo Please open '.env' in Notepad and set your GEMINI_API_KEY.
    echo (You can also enter your API key directly inside the Streamlit web interface sidebar).
    echo.
)

:: 6. Launch Application
echo [5/5] Starting Streamlit Web Application ...
echo URL: http://localhost:8501
echo Press Ctrl+C in this console window to stop the application.
echo.
python -m streamlit run app.py

if %errorlevel% neq 0 (
    echo [ERROR] Streamlit encountered an unexpected runtime issue.
    pause
    exit /b 1
)

pause
