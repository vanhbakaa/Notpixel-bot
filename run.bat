:loop
python main.py
echo Restarting the program in 2 seconds...
timeout /t 2 /nobreak >nul
goto :loop
