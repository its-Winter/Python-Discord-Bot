@echo off
call "%USERPROFILE%\Documents\Phoenix\Scripts\activate.bat"
:start
python main.py

if %ERRORLEVEL% NEQ 0 (
      goto :start
)