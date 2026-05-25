@echo off
REM =============================================
REM  PELIGRO: Borra toda la base de datos de ProGesTec
REM  y vuelve a crear las tablas + seed desde cero
REM =============================================

cd /d "%~dp0.."

echo.
echo ===========================================
echo   RESET de la base de datos ProGesTec
echo ===========================================
echo.
echo   ATENCION: Esto borrara TODOS los datos de MySQL.
echo             (Facturas, tickets, usuarios, etc.)
echo             No afecta al catalogo Postgres.
echo.

set /p CONFIRM=Escribe SI para continuar: 
if /i not "%CONFIRM%"=="SI" (
    echo Cancelado.
    pause
    exit /b 0
)

echo.
echo [1/4] Deteniendo contenedores...
docker compose down

echo [2/4] Eliminando volumen de MySQL...
docker volume rm proyecto_db_data 2>nul
docker volume rm progestec_db_data 2>nul

echo [3/4] Levantando contenedores de nuevo...
docker compose up -d
timeout /t 15 /nobreak >nul

echo [4/4] Aplicando migraciones y seed...
docker exec fastapi_app alembic upgrade head
docker exec fastapi_app python scripts/seed_initial.py

echo.
echo [OK] Base de datos reiniciada.
echo.
pause
