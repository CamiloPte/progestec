@echo off
REM =============================================
REM  Restaura el backup de Supabase en el Postgres local
REM  Solo correr UNA VEZ o cuando se quiera refrescar el catalogo
REM =============================================

cd /d "%~dp0.."

echo.
echo ===========================================
echo   Restaurando catalogo de dispositivos
echo ===========================================
echo.

REM Busca el primer archivo .backup en la carpeta backup/
set BACKUP_FILE=
for %%f in (backup\*.backup) do (
    set BACKUP_FILE=%%~nxf
    goto :found
)

:found
if "%BACKUP_FILE%"=="" (
    echo [ERROR] No se encontro ningun archivo .backup en la carpeta backup/
    echo         Coloca el archivo de Supabase en: backup\
    pause
    exit /b 1
)

echo Archivo encontrado: %BACKUP_FILE%
echo.

docker exec -it catalog_postgres psql -U catalog -d postgres -v ON_ERROR_STOP=0 -f /backup/%BACKUP_FILE%

echo.
echo Verificando tablas restauradas:
docker exec catalog_postgres psql -U catalog -d postgres -c "SELECT table_name FROM information_schema.tables WHERE table_name IN ('manufacturers','device_models','device_variants');"

echo.
echo [OK] Restauracion completada.
echo.
pause
