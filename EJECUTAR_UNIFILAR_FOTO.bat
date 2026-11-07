@echo off
title ElectroMemoria MARIN - Extractor Unifilar Foto
echo ========================================================
echo   INICIANDO EXTRACTOR UNIFILAR POR FOTO (IA)
echo ========================================================
echo.
cd /d "%~dp0"
set PYTHON_EXE=C:\Users\Alvaro\AppData\Local\Programs\Python\Python311\python.exe

if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python
)

echo Abriendo modulo unifilar en tu navegador...
start "" http://localhost:8502
"%PYTHON_EXE%" -m streamlit run modulos/unifilar_foto.py --server.port 8502
pause
