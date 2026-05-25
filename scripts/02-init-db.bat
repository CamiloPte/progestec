@echo off
REM =============================================
REM  Inicializa la base de datos:
REM   - Corre migraciones de Alembic
REM   - Ejecuta el seed (roles, estados, modulos, admin)
REM =============================================

cd /d "%~dp0.."

echo.
echo ===========================================
echo   Inicializando base de datos
echo ===========================================
echo.

echo [1/2] Aplicando migraciones de Alembic...
docker exec fastapi_app alembic upgrade head

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Fallo aplicando migraciones.
    pause
    exit /b 1
)

echo.
echo [2/2] Ejecutando seed inicial (roles, estados, modulos, admin)...
docker exec fastapi_app python scripts/seed_initial.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Fallo el seed inicial.
    pause
    exit /b 1
)

echo.
echo [OK] Base de datos lista.
echo.
echo   Usuario ADMIN:
echo     Email:    admin@progestec.com
echo     Password: Admin123!
echo.
pause
