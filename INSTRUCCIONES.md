# PA02 — Cómo ejecutar el proyecto

Grupo 05 · Analítica de Datos · USS 2026-I

## Requisitos
- **Python 3.11 o superior** (probado en 3.14)
- Conexión a internet la primera vez (para instalar las librerías)

## 1. Copiar el proyecto
Copia la **carpeta completa** `PA02_Amazon` (≈46 MB). Debe incluir:

```
app.py                    requirements.txt
data/Amazon.csv           modelos/*.pkl
graficas/*.png            EDA.ipynb  MODELOS.ipynb  Analisis_Avanzado.ipynb
```

> Sin `data/`, `modelos/` y `graficas/` la app **no arranca**: usa rutas relativas.

## 2. Instalar las librerías
Abre una terminal **dentro de la carpeta** `PA02_Amazon` y ejecuta:

```
pip install -r requirements.txt
```

## 3. Ejecutar la aplicación web
```
python -m streamlit run app.py
```
Se abre sola en <http://localhost:8501>. Para detenerla: `Ctrl + C`.

> Atajo: doble clic en **`iniciar_app.bat`** (hace los pasos 3 automáticamente).

## 4. Ejecutar los notebooks
Ábrelos en VS Code o Jupyter y ejecútalos **en este orden**:

1. `EDA.ipynb` → genera `modelos/X_train.pkl`, `X_test.pkl`, `scaler.pkl`
2. `MODELOS.ipynb` → entrena los 4 algoritmos y guarda `modelo_ganador.pkl` y `mediana.pkl`
3. `Analisis_Avanzado.ipynb` → outliers, PCA/t-SNE y modelos de predicción

---

## Errores comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `missing ScriptRunContext!` y no abre nada | Pulsaste el botón ▶ *Run* de VS Code | Usa `python -m streamlit run app.py` en la terminal |
| `FileNotFoundError: modelos/modelo_ganador.pkl` | La terminal no está en la carpeta del proyecto | `cd` hasta `PA02_Amazon` (el prompt debe terminar en `...\PA02_Amazon>`) |
| `InconsistentVersionWarning` de scikit-learn | Versión distinta a la que entrenó los `.pkl` | Instala con `requirements.txt` (fija `scikit-learn==1.7.2`) |
| `could not convert string to float: 'Charlotte'` | `X_train.pkl` viejo con columnas de texto | Vuelve a ejecutar `EDA.ipynb` completo antes de `MODELOS.ipynb` |
| `ModuleNotFoundError: streamlit` | Faltan las librerías | `pip install -r requirements.txt` |

## Recomendación para la exposición
Lleva **tu propia laptop** con todo ya instalado y la app **ya abierta** en el navegador.
Si debes usar la PC del profesor, necesitarás internet para el `pip install`.
Ten siempre las **capturas de pantalla** como respaldo.
