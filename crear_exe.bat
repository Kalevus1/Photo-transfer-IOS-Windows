@echo off
REM Genera el ejecutable en DOS formatos:
REM   1) CARPETA  -> dist\Transferencia\
REM   2) EMPAQUETADO -> dist\Transferencia.exe  (un solo archivo)
cd /d "%~dp0"
set "PYDIR=..\.venv_face\Scripts"
if not exist "%PYDIR%\python.exe" set "PYDIR=.venv\Scripts"
if not exist "%PYDIR%\pyinstaller.exe" ( echo Instalando PyInstaller... & "%PYDIR%\python.exe" -m pip install pyinstaller )

set OPTS=--collect-all flask --collect-all werkzeug --collect-all jinja2 --collect-all qrcode
set EXCL=--exclude-module PySide6.QtWebEngineCore --exclude-module PySide6.QtWebEngineWidgets --exclude-module PySide6.QtQuick --exclude-module PySide6.QtQml --exclude-module PySide6.Qt3DCore --exclude-module PySide6.QtMultimedia --exclude-module PySide6.QtPdf --exclude-module PySide6.QtWebChannel --exclude-module PySide6.QtDesigner --exclude-module scipy --exclude-module jax --exclude-module jaxlib --exclude-module matplotlib --exclude-module cv2 --exclude-module mediapipe --exclude-module tensorflow --exclude-module torch --exclude-module numpy

echo === 1/2  Version CARPETA (onedir) ===
"%PYDIR%\pyinstaller.exe" --noconfirm --clean --windowed --onedir ^
  --name "Transferencia" --icon "recursos\icono.ico" %OPTS% %EXCL% transferencia_fotos.py

echo === 2/2  Version EMPAQUETADA (onefile) ===
"%PYDIR%\pyinstaller.exe" --noconfirm --windowed --onefile ^
  --name "Transferencia" --icon "recursos\icono.ico" %OPTS% %EXCL% transferencia_fotos.py
echo.
echo Listo:  dist\Transferencia\Transferencia.exe   y   dist\Transferencia.exe
pause
