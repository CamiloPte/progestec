@echo off
REM =============================================
REM  Detiene todos los contenedores Docker del proyecto
REM =============================================

cd /d "%~dp0.."

echo.
echo ===========================================
echo   Deteniendo contenedores Docker
echo ===========================================
echo.

docker compose down

echo.
echo [OK] Contenedores detenidos.
echo.
echo Nota: Los procesos de Node (catalog-service y frontend)
echo       debes cerrarlos manualmente con Ctrl+C en sus ventanas.
echo.
pause
