@echo off
echo ====================================
echo Smart Condominio - Setup Script
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo Por favor instala Python 3.10+ desde https://www.python.org/
    pause
    exit /b 1
)

echo [1/6] Python detectado
python --version

REM Check if venv exists
if not exist "venv" (
    echo.
    echo [2/6] Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado
) else (
    echo.
    echo [2/6] Entorno virtual ya existe
)

REM Activate virtual environment
echo.
echo [3/6] Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] No se pudo activar el entorno virtual
    pause
    exit /b 1
)

REM Upgrade pip
echo.
echo [4/6] Actualizando pip, setuptools y wheel...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo [WARNING] Hubo un problema al actualizar pip
)

REM Install dependencies
echo.
echo [5/6] Instalando dependencias...
echo Esto puede tomar varios minutos...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Hubo problemas al instalar las dependencias
    echo.
    echo Soluciones:
    echo 1. Si el error es con Pillow, instala Microsoft C++ Build Tools:
    echo    https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo.
    echo 2. Intenta instalar Pillow por separado:
    echo    pip install Pillow
    echo.
    echo 3. Consulta GUIA_INSTALACION.md para mas ayuda
    echo.
    pause
    exit /b 1
)

REM Check if .env exists
echo.
echo [6/6] Verificando configuracion...
if not exist ".env" (
    echo.
    echo [WARNING] No se encontro el archivo .env
    echo Por favor crea un archivo .env con la configuracion de la base de datos
    echo Consulta GUIA_INSTALACION.md para mas detalles
    echo.
)

echo.
echo ====================================
echo [OK] Instalacion completada!
echo ====================================
echo.
echo Proximos pasos:
echo 1. Configura tu archivo .env con las credenciales de PostgreSQL
echo 2. Crea la base de datos en PostgreSQL
echo 3. Ejecuta: python manage.py migrate
echo 4. Crea un superusuario: python manage.py createsuperuser
echo 5. Inicia el servidor: python manage.py runserver
echo.
echo Consulta GUIA_INSTALACION.md para instrucciones detalladas
echo.
pause
