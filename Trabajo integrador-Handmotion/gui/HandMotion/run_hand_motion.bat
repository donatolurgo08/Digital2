@echo off
setlocal
cd /d "%~dp0"

set "VENV_PY=%~dp0.venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo [Hand Motion] Creando el entorno virtual...
    py -3 -m venv "%~dp0.venv"
    if errorlevel 1 goto :python_error
)

"%VENV_PY%" -c "import PySide6, serial, pyqtgraph, numpy" >nul 2>&1
if errorlevel 1 (
    echo [Hand Motion] Instalando dependencias desde requirements.txt...
    "%VENV_PY%" -m pip install -r "%~dp0requirements.txt"
    if errorlevel 1 goto :dependency_error
)

"%VENV_PY%" -m hand_motion
set "APP_EXIT=%ERRORLEVEL%"
if not "%APP_EXIT%"=="0" echo [Hand Motion] La aplicacion finalizo con un error.
pause
exit /b %APP_EXIT%

:python_error
echo No se pudo crear el entorno virtual. Verifica que Python 3 este instalado y disponible con el comando py.
pause
exit /b 1

:dependency_error
echo No se pudieron instalar las dependencias. Revisa tu conexion a Internet y requirements.txt.
pause
exit /b 1
