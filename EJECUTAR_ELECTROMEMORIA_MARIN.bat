@echo off
title ElectroMemoria MARIN - Ingenieria Electrica REBT
echo ========================================================
echo   INICIANDO ELECTROMEMORIA MARIN - INGENIERIA REBT
echo ========================================================
echo.
cd /d "%~dp0"
set PYTHON_EXE=C:\Users\Alvaro\AppData\Local\Programs\Python\Python311\python.exe

if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python
)

echo Abriendo aplicacion en tu navegador...
start "" http://localhost:8501
"%PYTHON_EXE%" -m streamlit run inicio.py --server.port 8501
pause
