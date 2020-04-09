@echo off
call "%USERPROFILE%\Documents\Github\Python-Discord-Bot\Scripts\activate.bat"
:start
python main.py

if %ERRORLEVEL% NEQ 0 (
      goto :start
)