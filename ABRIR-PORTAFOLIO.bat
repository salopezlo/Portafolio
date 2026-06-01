@echo off
echo Iniciando servidor local...
cd /d "C:\Users\SANTI Y LUI\Cowork"
start "" "http://localhost:8080/portafolio-v5.html"
python -m http.server 8080
pause
