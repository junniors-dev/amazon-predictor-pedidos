@echo off
REM ============================================================
REM  Iniciar la app web (demo de la exposicion) - Grupo 05
REM  Doble clic en este archivo para abrir el Predictor.
REM ============================================================
cd /d "%~dp0"
echo Iniciando la aplicacion... se abrira en tu navegador.
echo Para detenerla, cierra esta ventana o presiona Ctrl + C.
python -m streamlit run app.py
pause
