@echo off
setlocal
cd /d "%~dp0"

set "PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PYTHON=%CD%\.venv\Scripts\python.exe"

start "LaptopDSS Backend" cmd /k ""%PYTHON%" -X utf8 -m uvicorn src.api:app --host 127.0.0.1 --port 8000"
start "LaptopDSS Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

endlocal
