# 🛒 Predictor de Valor de Pedidos Amazon

Sistema predictivo que clasifica un pedido de Amazon como **alto valor** o
**bajo valor** económico (respecto a la mediana de `TotalAmount`), con una app
web interactiva en Streamlit.

**PA02 — Analítica de Datos | Grupo 05 | USS 2026-I**

## 🚀 App en vivo

> _(Se agrega la URL de Streamlit Community Cloud tras el despliegue)_

## 📦 Contenido

| Archivo | Descripción |
|---|---|
| `app.py` | App web de predicción (Streamlit): predicción, estadísticas del dataset e historial de sesión. |
| `EDA.ipynb` | Análisis exploratorio de datos. |
| `MODELOS.ipynb` | Entrenamiento y comparación de modelos; el ganador es un **SVM** (F1 ≈ 0.759, AUC-ROC ≈ 0.787). |
| `Analisis_Avanzado.ipynb` | Análisis adicional (PCA, t-SNE, outliers, regresión). |
| `modelos/` | Modelo entrenado, scaler, mediana umbral y splits de datos (`.pkl`). |
| `data/Amazon.csv` | Dataset (100 000 pedidos). |
| `graficas/` | Figuras generadas por el EDA y el modelado. |
| `CAMBIOS.md` | Bitácora de cambios y correcciones. |

## ▶️ Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

En Windows también puedes usar `iniciar_app.bat`.

## ☁️ Desplegar en Streamlit Community Cloud

1. Entra a https://share.streamlit.io e inicia sesión con GitHub.
2. **New app** → elige este repositorio, rama `main`, archivo `app.py`.
3. **Deploy**. Streamlit instala `requirements.txt` y publica una URL pública.

> Los modelos `.pkl` se entrenaron con **scikit-learn 1.9.0** (fijado en
> `requirements.txt`) para que carguen sin errores de versión en la nube.
