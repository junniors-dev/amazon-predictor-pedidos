# ============================================================
# app.py — Aplicación web predictiva de pedidos Amazon
# PA02 — Analítica de Datos | Grupo 05 | USS 2026-I
# ============================================================

import os
import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

# ── Configuración de la página ──────────────────────────────
st.set_page_config(
    page_title="Predictor de Pedidos Amazon",
    page_icon="🛒",
    layout="wide"
)

# ── Categorías del dataset (fuente única, evita repetir listas) ──
CATEGORIAS = ["Electronics", "Books", "Clothing",
              "Home & Kitchen", "Sports & Outdoors", "Toys & Games"]
METODOS_PAGO = ["Credit Card", "Debit Card", "UPI",
                "Amazon Pay", "Net Banking", "Cash on Delivery"]
PAISES = ["United States", "India", "Canada",
          "United Kingdom", "Australia"]
MARCAS = ["Apex", "BrightLux", "CoreTech", "FitLife", "HomeEase",
          "KiddoFun", "NexPro", "ReadMore", "UrbanStyle", "Zenith"]


def one_hot(valor, opciones, prefijo):
    """Construye las columnas one-hot para una variable categórica,
    igual que pd.get_dummies pero con el mismo formato de nombre de
    columna usado al entrenar el modelo (Prefijo_Opcion)."""
    return {f"{prefijo}_{op}": [1 if valor == op else 0] for op in opciones}


# ── Cargar modelo, scaler y mediana de entrenamiento ─────────
@st.cache_resource
def cargar_modelo():
    modelo = joblib.load('modelos/modelo_ganador.pkl')
    scaler = joblib.load('modelos/scaler.pkl')
    # Mediana real usada para etiquetar "alto valor" durante el entrenamiento
    # (ver MODELOS.ipynb, Celda 3). Se guarda en un .pkl en vez de
    # escribirla a mano para que el texto de la app nunca quede
    # desincronizado del modelo si este se reentrena.
    mediana = joblib.load('modelos/mediana.pkl')
    return modelo, scaler, mediana


# ── Cargar el dataset completo, solo para mostrar estadísticas ──
# (el modelo NO depende de esto — únicamente alimenta los paneles
# de contexto y la pestaña de estadísticas)
@st.cache_data
def cargar_dataset():
    return pd.read_csv('data/Amazon.csv')


@st.cache_data
def calcular_tasas_historicas(_df, mediana):
    """Para cada valor de Category/PaymentMethod/Brand/Country, calcula
    qué % de los pedidos históricos con ese valor fueron 'alto valor'.
    Sirve de contexto junto a la predicción del modelo (no es una
    explicación exacta del SVM, que al usar kernel RBF no expone
    coeficientes/feature_importances_ directamente)."""
    df = _df.copy()
    df['AltoValor'] = (df['TotalAmount'] > mediana).astype(int)
    return {
        col: (df.groupby(col)['AltoValor'].mean() * 100).round(1)
        for col in ['Category', 'PaymentMethod', 'Brand', 'Country']
    }


modelo, scaler, mediana = cargar_modelo()
df = cargar_dataset()
tasas = calcular_tasas_historicas(df, mediana)

if 'historial' not in st.session_state:
    st.session_state.historial = []

# ── Título ──────────────────────────────────────────────────
st.title("🛒 Predictor de Valor de Pedidos")
st.subheader("Amazon — Sistema Predictivo | Grupo 05 USS")
st.markdown("---")

tab_pred, tab_stats, tab_hist = st.tabs(
    ["🔮 Predicción", "📊 Estadísticas del dataset", "🕘 Historial de la sesión"]
)

# ============================================================
# TAB 1 — Predicción
# ============================================================
with tab_pred:
    st.markdown(
        "Ingresa los datos de un pedido y el sistema predecirá "
        "si será un pedido de **alto valor** o **bajo valor** económico."
    )
    st.markdown("### 📋 Datos del pedido")

    col1, col2 = st.columns(2)

    with col1:
        categoria = st.selectbox("Categoría", CATEGORIAS)
        metodo_pago = st.selectbox("Método de pago", METODOS_PAGO)
        cantidad = st.slider("Cantidad", min_value=1, max_value=5, value=2)

    with col2:
        costo_envio = st.number_input(
            "Costo de envío (USD)",
            min_value=0.0, max_value=15.0,
            value=7.5, step=0.5
        )
        pais = st.selectbox("País", PAISES)
        marca = st.selectbox("Marca", MARCAS)

    st.markdown("---")

    if st.button("🔮 PREDECIR PEDIDO", width="stretch"):

        # Construir el vector de entrada: variables numéricas +
        # One-Hot Encoding manual (Category, PaymentMethod, Country, Brand)
        entrada = pd.DataFrame({'Quantity': [cantidad], 'ShippingCost': [costo_envio]})
        entrada = entrada.assign(
            **one_hot(categoria, CATEGORIAS, "Category"),
            **one_hot(metodo_pago, METODOS_PAGO, "PaymentMethod"),
            **one_hot(pais, PAISES, "Country"),
            **one_hot(marca, MARCAS, "Brand"),
        )

        # Escalar Quantity y ShippingCost con el mismo StandardScaler del
        # entrenamiento. Se rellenan las demás columnas con 0 porque
        # StandardScaler escala cada columna de forma independiente
        # ((x - mean_i) / scale_i)); el relleno no afecta el resultado de
        # Quantity/ShippingCost, y seleccionar por NOMBRE (no por posición
        # [0, 4]) evita que un futuro cambio de orden de columnas rompa la app.
        columnas_escalador = ['Quantity', 'UnitPrice', 'Discount',
                              'Tax', 'ShippingCost', 'TotalAmount']
        frame_a_escalar = pd.DataFrame({
            'Quantity': [cantidad], 'UnitPrice': [0], 'Discount': [0],
            'Tax': [0], 'ShippingCost': [costo_envio], 'TotalAmount': [0]
        })[columnas_escalador]
        escalado = pd.DataFrame(
            scaler.transform(frame_a_escalar), columns=columnas_escalador
        )
        entrada['Quantity'] = escalado['Quantity']
        entrada['ShippingCost'] = escalado['ShippingCost']

        # Alinear columnas con el modelo (orden y nombres exactos de entrenamiento)
        columnas_modelo = modelo.feature_names_in_ if hasattr(modelo, 'feature_names_in_') else entrada.columns
        entrada = entrada.reindex(columns=columnas_modelo, fill_value=0)

        # Predecir
        prediccion = modelo.predict(entrada)[0]
        probabilidad = modelo.predict_proba(entrada)[0][1] * 100

        # ── Resultado ─────────────────────────────────────────
        st.markdown("### 📊 Resultado de la predicción")

        if prediccion == 1:
            st.success("✅ PEDIDO DE ALTO VALOR")
            st.markdown(f"> El modelo predice que este pedido superará la mediana de **${mediana:,.2f} USD**.")
        else:
            st.warning("⚠️ PEDIDO DE BAJO VALOR")
            st.markdown(f"> El modelo predice que este pedido estará por debajo de la mediana de **${mediana:,.2f} USD**.")

        st.metric("Probabilidad de Alto Valor", f"{probabilidad:.1f}%")
        st.progress(int(round(probabilidad)))

        # ── Contexto adicional (más datos sobre esta predicción) ──
        st.markdown("#### 🔎 Contexto de esta predicción")

        c1, c2 = st.columns(2)
        with c1:
            st.metric(
                "Cantidad vs. promedio histórico",
                f"{cantidad} unidades",
                delta=f"{cantidad - df['Quantity'].mean():+.2f} vs. {df['Quantity'].mean():.2f}"
            )
        with c2:
            st.metric(
                "Costo de envío vs. promedio histórico",
                f"${costo_envio:.2f}",
                delta=f"{costo_envio - df['ShippingCost'].mean():+.2f} vs. ${df['ShippingCost'].mean():.2f}"
            )

        st.markdown(
            "**Tasa histórica de 'alto valor' según cada característica elegida** "
            "(% de pedidos pasados con ese mismo atributo que superaron la mediana; "
            "el SVM con kernel RBF no expone importancia de variables directamente, "
            "esto es un proxy descriptivo, no la explicación exacta del modelo):"
        )
        detalle = pd.DataFrame({
            "Característica": ["Categoría", "Método de pago", "Marca", "País"],
            "Valor elegido": [categoria, metodo_pago, marca, pais],
            "Tasa histórica de alto valor": [
                f"{tasas['Category'][categoria]}%",
                f"{tasas['PaymentMethod'][metodo_pago]}%",
                f"{tasas['Brand'][marca]}%",
                f"{tasas['Country'][pais]}%",
            ],
        })
        st.dataframe(detalle, hide_index=True, width="stretch")

        st.caption("Modelo: SVM | F1-Score: 0.759 | AUC-ROC: 0.787 | Grupo 05 USS 2026-I")

        # ── Guardar en el historial de la sesión ──────────────
        st.session_state.historial.append({
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Categoría": categoria,
            "Método de pago": metodo_pago,
            "País": pais,
            "Marca": marca,
            "Cantidad": cantidad,
            "Envío (USD)": costo_envio,
            "Predicción": "Alto valor" if prediccion == 1 else "Bajo valor",
            "Probabilidad (%)": round(probabilidad, 1),
        })

# ============================================================
# TAB 2 — Estadísticas del dataset
# ============================================================
with tab_stats:
    st.markdown("### 📊 Estadísticas generales del dataset")
    st.caption(f"Basado en los {len(df):,} pedidos usados para entrenar el modelo")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total de pedidos", f"{len(df):,}")
    m2.metric("Valor mediano (umbral)", f"${mediana:,.2f}")
    m3.metric("Costo de envío promedio", f"${df['ShippingCost'].mean():.2f}")
    m4.metric("Cantidad promedio", f"{df['Quantity'].mean():.2f}")

    st.markdown("---")
    st.markdown("#### Tasa de 'alto valor' por característica")
    b1, b2 = st.columns(2)
    with b1:
        st.markdown("**Por categoría**")
        st.bar_chart(tasas['Category'])
        st.markdown("**Por marca**")
        st.bar_chart(tasas['Brand'])
    with b2:
        st.markdown("**Por país**")
        st.bar_chart(tasas['Country'])
        st.markdown("**Por método de pago**")
        st.bar_chart(tasas['PaymentMethod'])

    st.markdown("---")
    st.markdown("#### Gráficas del análisis exploratorio (EDA.ipynb / MODELOS.ipynb)")
    g1, g2 = st.columns(2)
    graficas_izq = [
        ("graficas/grafica1_distribucion_estados.png", "Distribución de estados de pedido"),
        ("graficas/grafica3_correlaciones.png", "Correlaciones entre variables numéricas"),
        ("graficas/grafica5_curvas_ROC.png", "Curvas ROC — comparación de modelos"),
    ]
    graficas_der = [
        ("graficas/grafica2_cancelaciones_pago.png", "Tasa de cancelación por método de pago"),
        ("graficas/grafica4_distribuciones.png", "Distribución de TotalAmount y ShippingCost"),
        ("graficas/grafica6_confusion_ganador.png", "Matriz de confusión del modelo ganador"),
    ]
    with g1:
        for ruta, leyenda in graficas_izq:
            if os.path.exists(ruta):
                st.image(ruta, caption=leyenda, width="stretch")
    with g2:
        for ruta, leyenda in graficas_der:
            if os.path.exists(ruta):
                st.image(ruta, caption=leyenda, width="stretch")

# ============================================================
# TAB 3 — Historial de la sesión
# ============================================================
with tab_hist:
    st.markdown("### 🕘 Historial de predicciones de esta sesión")
    st.caption("Se guarda solo mientras la app está abierta (no persiste al cerrar el navegador).")

    if st.session_state.historial:
        hist_df = pd.DataFrame(st.session_state.historial)
        st.dataframe(hist_df, hide_index=True, width="stretch")

        col_a, col_b = st.columns([1, 1])
        with col_a:
            st.download_button(
                "⬇️ Descargar historial (CSV)",
                hist_df.to_csv(index=False).encode("utf-8"),
                file_name="historial_predicciones.csv",
                mime="text/csv",
                width="stretch",
            )
        with col_b:
            if st.button("🗑️ Limpiar historial", width="stretch"):
                st.session_state.historial = []
                st.rerun()
    else:
        st.info("Aún no has hecho ninguna predicción en esta sesión. Ve a la pestaña 🔮 Predicción para empezar.")
