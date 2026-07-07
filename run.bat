@echo off
title PL-300 Exam Center
start /b "" "%~dp0PL300.exe" >nul 2>&1
echo Starting PL-300 Exam Center...
echo Opening http://localhost:9090
timeout /t 3 /nobreak >nul
start http://localhost:9090
echo.
echo Press any key to stop the server...
pause >nul
taskkill /f /im PL300.exe >nul 2>&1
echo Server stopped.
