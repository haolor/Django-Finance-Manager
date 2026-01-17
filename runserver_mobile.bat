@echo off
echo ========================================
echo   Django Finance Manager - Mobile Mode
echo ========================================
echo.
echo Starting server for mobile access...
echo.
echo Server will be accessible at:
echo   - http://localhost:8000
echo   - http://127.0.0.1:8000
echo   - http://YOUR_IP_ADDRESS:8000
echo.
echo To find your IP address, run: ipconfig
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

py manage.py runserver 0.0.0.0:8000

pause

