@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3.12 -m venv .venv
  if errorlevel 1 goto failed
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto failed
.venv\Scripts\python.exe scripts\setup_local.py
if errorlevel 1 goto failed
set FIRST_RUN=0
if not exist db.sqlite3 set FIRST_RUN=1
.venv\Scripts\python.exe manage.py migrate --noinput
if errorlevel 1 goto failed
if "%FIRST_RUN%"=="1" (
  .venv\Scripts\python.exe manage.py seed_demo --local-demo
  if errorlevel 1 goto failed
)
echo Open http://127.0.0.1:8000/ in your browser.
echo Local usernames: organizer, DEMO-001, DEMO-002, DEMO-003, DEMO-004
echo First-run local password: CampusDemo!2026
.venv\Scripts\python.exe manage.py runserver
goto end
:failed
echo Setup failed. Read the error above. Install Python 3.12 and check README.md.
pause
:end
endlocal
