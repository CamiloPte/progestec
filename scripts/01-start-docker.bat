@echo off
REM =============================================
REM  Levanta los contenedores Docker (backend + MySQL + Postgres)
REM =============================================

cd /d "%~dp0.."

echo.
echo ===========================================
echo   Levantando contenedores Docker
echo ===========================================
echo.

docker compose up -d

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] No se pudo levantar Docker. Verifica que Docker Desktop este corriendo.
    pause
    exit /b 1
)

echo.
echo Esperando 10 segundos para que los servicios arranquen...
timeout /t 10 /nobreak >nul

echo.
echo Contenedores activos:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo [OK] Docker listo.
echo.
pause
