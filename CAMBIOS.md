# Cambios aplicados al proyecto PA02_Amazon

Análisis realizado el 2026-07-05. Resumen de lo revisado y lo modificado.

## Bug encontrado: la mediana mostrada no era la mediana real del modelo

El modelo (`modelos/modelo_ganador.pkl`, un SVM) se entrenó etiquetando
"alto valor" con la mediana calculada sobre el split de entrenamiento
(`MODELOS.ipynb`, Celda 3). Esa mediana real es **715.37**, pero se había
escrito a mano en dos lugares distintos, y con otro valor:

- `app.py` mostraba al usuario "$714.31 USD"
- La celda de Chi-cuadrado en `MODELOS.ipynb` usaba `mediana = 714.31`
- `Informe_Tecnico_PA02.docx` menciona "USD 714.32"

Ningún de los tres coincidía con el valor real (715.37) usado por el
modelo ya entrenado. La diferencia es pequeña y no cambia las
conclusiones (verifiqué que el resultado del Chi-cuadrado es el mismo:
p ≈ 0.276, no hay relación significativa), pero es información incorrecta
mostrada al usuario final de la app.

**Arreglado:** ahora `modelos/mediana.pkl` guarda ese valor una sola vez
(calculado directamente de `X_train.pkl` + `scaler.pkl`), y tanto `app.py`
como la celda de Chi-cuadrado lo cargan desde ahí en vez de tener el
número escrito a mano.

**Pendiente de tu decisión:** no toqué `Informe_Tecnico_PA02.docx` porque
es un documento ya entregable/revisable por el docente — si quieres,
puedo actualizar el "USD 714.32" a "715.37" ahí también.

## Limpieza de código en `app.py`

- Las 4 variables categóricas (Categoría, Método de pago, País, Marca)
  tenían ~30 líneas de diccionarios repetidos a mano para el one-hot
  encoding. Se reemplazaron por una función `one_hot()` reutilizable.
- El escalado de `Quantity`/`ShippingCost` seleccionaba columnas por
  posición (`[:, [0, 4]]`), lo cual se rompe silenciosamente si alguna vez
  cambia el orden de columnas del scaler. Ahora se selecciona por nombre.
- El realineado de columnas con el modelo usaba un loop manual; se
  reemplazó por `entrada.reindex(columns=..., fill_value=0)`, más idiomático.
- Verifiqué que estos cambios no alteran el comportamiento: corrí el
  pipeline viejo y el nuevo con el mismo pedido de prueba y la predicción
  y probabilidad son idénticas (0, 25.07%).

## Otros archivos

- `requirements.txt`: nuevo, lista las librerías usadas por el proyecto.
- `app.py.bak` y `MODELOS.ipynb.bak`: copias de las versiones originales,
  por si quieres comparar o revertir algo.

## Ampliación: la app ahora muestra más datos (2026-07-05, segunda pasada)

A pedido tuyo, `app.py` pasó de una sola pantalla de predicción a 3 pestañas:

- **🔮 Predicción** (la que ya existía) — ahora además muestra, tras predecir:
  la probabilidad como barra de progreso, cómo se compara la cantidad y el
  costo de envío ingresados contra el promedio histórico del dataset, y una
  tabla con la tasa histórica de "alto valor" para la categoría/método de
  pago/marca/país elegidos (nota: es un dato descriptivo del dataset, no una
  explicación exacta del SVM — un SVM con kernel RBF no expone coeficientes
  ni feature importances como sí lo haría un modelo lineal o un árbol).
- **📊 Estadísticas del dataset** — métricas generales (100,000 pedidos,
  mediana, promedios), tasa de "alto valor" por categoría/marca/país/método
  de pago, y las gráficas ya generadas en `graficas/` (se reutilizan las
  imágenes existentes del EDA en vez de recalcularlas).
- **🕘 Historial de la sesión** — cada predicción que hagas queda en una
  tabla (con botón para descargar CSV y para limpiar). Se guarda solo
  mientras la app sigue abierta; no queda en ningún archivo ni base de datos.

**No agregué campos de entrada nuevos** (ej. fecha, ciudad, estado): el
modelo SVM ya entrenado solo sabe usar las variables con las que se
entrenó (Quantity, ShippingCost, Category, PaymentMethod, Brand, Country).
Añadir un campo realmente nuevo requeriría reentrenar el modelo desde
`EDA.ipynb`/`MODELOS.ipynb` — decía si quieres que lo haga.

**Verificado:** corrí la app completa con `streamlit.testing.AppTest`
(sin abrir navegador) — carga sin excepciones, probé 2 combinaciones de
pedido distintas y el flujo completo de predecir → ver detalle → aparecer
en historial → descargar/limpiar historial, todo funciona.

También corregí una advertencia de Streamlit: `use_container_width` está
deprecado (se elimina después de 2025-12-31, ya pasado) y lo reemplacé por
`width="stretch"` en los 7 lugares donde se usaba, para que la app no se
rompa si actualizas Streamlit más adelante.

## Observación (no modificada)

`EDA.ipynb` construye una variable objetivo de **cancelación de pedido**
(`Target`, Celda 10) que nunca se usa: `MODELOS.ipynb` la descarta y
reconstruye un objetivo distinto ("alto valor", según el objetivo real
del informe). No es un error — el proyecto evolucionó — pero si alguien
lee `EDA.ipynb` de forma aislada puede pensar que ese es el objetivo
final. No lo cambié porque no rompe nada y no quise tocar una fase que ya
diste por cerrada; avísame si quieres que lo aclare con un comentario o
lo actualice.
