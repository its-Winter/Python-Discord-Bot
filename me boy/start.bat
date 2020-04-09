@echo off
call "%USERPROFILE%\Documents\Github\Python-Discord-Bot\Scripts\activate.bat"
:start
python main.py

if %ERRORLEVEL% EQU 26 (
      goto :start
)