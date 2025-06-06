@echo off
echo Starting Business Consultant Chat...

:: Activate Python 3.11 environment
call C:\Users\matzu\AppData\Local\Programs\Python\Python311\python.exe -m venv venv311
call venv311\Scripts\activate.bat

:: Install required packages
pip install supabase openai python-dotenv

:: Run the chat application
python app/chat.py

:: Deactivate virtual environment
deactivate 