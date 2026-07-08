@echo off
REM ============================================================
REM  PA02 - Grupo 05 | Instala las librerias y abre la app
REM  Doble clic aqui en la PC del profesor.
REM ============================================================
cd /d "%~dp0"
title PA02 Amazon - Grupo 05

echo.
echo [1/3] Verificando que Python este instalado...
python --version
if errorlevel 1 (
    echo.
    echo  ERROR: Python no esta instalado en esta PC.
    echo  Usa tu propia laptop o instala Python 3.11 o superior.
    echo.
    pause
    exit /b 1
)

echo.
echo [2/3] Instalando librerias... (puede tardar unos minutos, necesita internet)
python -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo.
    echo  ERROR: No se pudieron instalar las librerias.
    echo  Revisa que haya internet, o usa tu propia laptop.
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] Iniciando la aplicacion... se abrira en el navegador.
echo       Para detenerla: cierra esta ventana o pulsa Ctrl + C
echo.
python -m streamlit run app.py

pause
