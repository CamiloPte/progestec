@echo off
REM =============================================
REM  MENU PRINCIPAL: arranque completo del proyecto
REM  Lanza Docker, catalog-service y frontend en ventanas separadas
REM =============================================

cd /d "%~dp0.."

echo.
echo ===========================================
echo   ProGesTec - Arranque completo
echo ===========================================
echo.

echo [1/4] Verificando Docker...
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker no esta corriendo. Abre Docker Desktop primero.
    pause
    exit /b 1
)

echo [2/4] Levantando contenedores...
docker compose up -d
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo al levantar Docker.
    pause
    exit /b 1
)

echo        Esperando 10 segundos para que arranquen...
timeout /t 10 /nobreak >nul

echo [3/4] Abriendo Catalog Service en nueva ventana...
start "Catalog Service" cmd /k "%~dp004-start-catalog.bat"

timeout /t 3 /nobreak >nul

echo [4/4] Abriendo Frontend Angular en nueva ventana...
start "Frontend Angular" cmd /k "%~dp005-start-frontend.bat"

echo.
echo ===========================================
echo   Todo iniciado
echo ===========================================
echo.
echo   Backend API:     http://localhost:8000
echo   Swagger:         http://localhost:8000/docs
echo   Catalog Service: http://localhost:5000
echo   Frontend:        http://localhost:4200
echo.
echo   Para detener todo usa: scripts\stop-all.bat
echo.
pause
