@echo off
setlocal enabledelayedexpansion

title AI Document Comparison Assistant - Launcher
echo ==============================================================================
echo           AI DOCUMENT COMPARISON ASSISTANT - WINDOWS 11 LAUNCHER
echo                 Xpert Champs AI Engineering Internship
echo ==============================================================================
echo.

:: Set paths relative to script directory
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "REQ_FILE=%SCRIPT_DIR%requirements.txt"
set "APP_FILE=%SCRIPT_DIR%app.py"
set "ENV_FILE=%SCRIPT_DIR%.env"
set "ENV_EXAMPLE=%SCRIPT_DIR%.env.example"

:: 1. Check Python installation or existing virtual environment
if exist "%VENV_PY%" (
    echo [1/5] Verified existing virtual environment Python interpreter:
    "%VENV_PY%" --version
    goto :venv_ready
)

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not found in system PATH.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/5] System Python detected:
python --version
echo.

:: 2. Create Virtual Environment if not present
if not exist "%VENV_PY%" (
    echo [2/5] Creating isolated virtual environment in .\venv ...
    python -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment in "%VENV_DIR%".
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
)

:venv_ready
echo.

:: 3. Verify Virtual Environment Python
if not exist "%VENV_PY%" (
    echo [ERROR] Virtual environment Python not found at "%VENV_PY%".
    pause
    exit /b 1
)
echo [2/5] Virtual environment verified: %VENV_DIR%
echo.

:: 4. Verify Dependencies (Skip redundant reinstall if already satisfied)
echo [3/5] Verifying application dependencies ...
"%VENV_PY%" -c "import streamlit, google.genai, pypdf, docx, dotenv, pydantic, reportlab, pytest" >nul 2>nul
if %errorlevel% equ 0 (
    echo All required dependencies are verified and installed.
) else (
    echo Missing dependencies detected. Installing from requirements.txt ...
    if not exist "%REQ_FILE%" (
        echo [ERROR] requirements.txt not found at "%REQ_FILE%".
        pause
        exit /b 1
    )
    "%VENV_PY%" -m pip install -r "%REQ_FILE%"
    if %errorlevel% neq 0 (
        echo [ERROR] Package installation failed. Please check internet access.
        pause
        exit /b 1
    )
    echo Dependencies installed successfully.
)
echo.

:: 5. Check .env Configuration (Careful syntax: no unescaped parentheses)
echo [4/5] Checking environment configuration ...
if not exist "%ENV_FILE%" (
    if exist "%ENV_EXAMPLE%" (
        copy "%ENV_EXAMPLE%" "%ENV_FILE%" >nul
        echo [NOTICE] Created .env file from template .env.example.
        echo [IMPORTANT] Please add your GEMINI_API_KEY in .env or enter it in the Streamlit sidebar.
    ) else (
        echo [WARNING] .env.example template not found.
    )
) else (
    echo .env configuration file found.
)
echo.

:: 6. Verify main application file exists
if not exist "%APP_FILE%" (
    echo [ERROR] Main application file app.py not found at "%APP_FILE%".
    pause
    exit /b 1
)

:: 7. Launch Application with the virtual environment Python interpreter
echo [5/5] Launching AI Document Comparison Assistant ...
echo Local URL: http://localhost:8501
echo Press Ctrl+C in this console window to stop the application.
echo.

"%VENV_PY%" -m streamlit run "%APP_FILE%" --browser.gatherUsageStats false

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Streamlit exited with error code %errorlevel%.
    pause
    exit /b %errorlevel%
)

pause
