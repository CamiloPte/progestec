@echo off
REM =============================================
REM  Levanta el frontend Angular
REM  Accesible desde cualquier equipo en la red via http://IP:4200
REM =============================================

cd /d "%~dp0..\progestec-front"

echo.
echo ===========================================
echo   Iniciando Frontend Angular (puerto 4200)
echo ===========================================
echo.

REM Instalar dependencias si faltan
if not exist node_modules (
    echo Instalando dependencias de Angular. Esto puede tardar varios minutos...
    call npm install
)

echo.
echo Tu IP local:
ipconfig | findstr /C:"IPv4"
echo.
echo Los otros equipos pueden acceder en: http://TU_IP:4200
echo.

call npm start
