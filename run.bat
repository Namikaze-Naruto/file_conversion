@echo off
echo Starting File Conversion Platform...
cd backend
call venv\Scripts\activate.bat
echo.
echo Server starting on http://localhost:8000
echo.
echo Web Interface: http://localhost:8000/static/index.html
echo API Documentation: http://localhost:8000/docs
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
