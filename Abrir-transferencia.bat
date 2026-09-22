@echo off
REM Abre Transferencia de Fotos (Dia 12). Reutiliza ..\.venv_face o .venv.
cd /d "%~dp0"
set "PY=..\.venv_face\Scripts\pythonw.exe"
if not exist "%PY%" set "PY=.venv\Scripts\pythonw.exe"
if not exist "%PY%" ( echo Ejecuta primero instalar.bat & pause & exit /b 1 )
start "" "%PY%" transferencia_fotos.py
