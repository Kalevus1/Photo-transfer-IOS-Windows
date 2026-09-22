@echo off
REM Prepara el entorno. Reutiliza ..\.venv_face si existe; si no, crea .venv aqui.
cd /d "%~dp0"
if exist "..\.venv_face\Scripts\python.exe" ( set "PY=..\.venv_face\Scripts\python.exe" ) else (
  if not exist ".venv\Scripts\python.exe" ( echo Creando entorno... & py -m venv .venv )
  set "PY=.venv\Scripts\python.exe"
)
echo Instalando dependencias...
"%PY%" -m pip install --upgrade pip
"%PY%" -m pip install -r requirements.txt
echo. & echo Listo. Abre con  Abrir-transferencia.bat & pause
