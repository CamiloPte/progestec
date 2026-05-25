@echo off
REM =============================================
REM  Levanta el microservicio de Catalogo (Node/Express)
REM  Se queda en primer plano mostrando los logs
REM =============================================

cd /d "%~dp0..\catalog-service"

echo.
echo ===========================================
echo   Iniciando Catalog Service (puerto 5000)
echo ===========================================
echo.

REM Instalar dependencias si faltan
if not exist node_modules (
    echo Instalando dependencias...
    call npm install
)

call npm start
