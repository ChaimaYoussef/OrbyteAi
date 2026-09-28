@echo off
setlocal enabledelayedexpansion

echo ======================================================================
echo           ORBYTE - SCRIPT DE DEMARRAGE DEPLOIEMENT LAN (WIFI)
echo ======================================================================
echo.

:: 1. Detection automatique de l'IP LAN active via PowerShell
for /f "tokens=*" %%a in ('powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' -and $_.InterfaceAlias -notlike '*vEthernet*' -and $_.InterfaceAlias -notlike '*Docker*' } | Select-Object -ExpandProperty IPAddress | Select-Object -First 1)"') do (
    set LAN_IP=%%a
)

if "%LAN_IP%"=="" (
    echo [ATTENTION] Impossible de detecter l'IP LAN automatiquement.
    echo Utilisation de la valeur par defaut: localhost
    set LAN_IP=127.0.0.1
    set NIP_URL=http://localhost:3000
) else (
    echo [SUCCES] IP LAN detectee : %LAN_IP%
    set NIP_URL=http://orbyte.%LAN_IP%.nip.io:3000
)

echo.
echo ======================================================================
echo  URL PROFESSIONNELLE A PARTAGER AUX UTILISATEURS (DEMO / MOBILE / PC) :
echo  ---> !NIP_URL!
echo.
echo  (URL de secours en IP brute si absence de DNS/Internet) :
echo  ---> http://!LAN_IP!:3000
echo ======================================================================
echo.

:: 2. Injection des variables d'environnement LAN pour Nginx / FastAPI
set WEB_DOMAIN=!NIP_URL!
set CORS_ALLOWED_ORIGIN=!NIP_URL!,http://!LAN_IP!:3000,http://localhost:3000,http://127.0.0.1:3000

echo [INFO] Variables injectees pour Docker Compose :
echo        WEB_DOMAIN=!WEB_DOMAIN!
echo        CORS_ALLOWED_ORIGIN=!CORS_ALLOWED_ORIGIN!
echo.

:: 3. Lancement de Docker Compose
cd /d "%~dp0deployment\docker_compose"
echo [INFO] Lancement de Docker Compose...
docker compose up -d

echo.
echo [OK] Services demarres avec succes !
echo.
echo Pour arreter la plateforme :
echo   cd deployment\docker_compose ^& docker compose down
echo.
