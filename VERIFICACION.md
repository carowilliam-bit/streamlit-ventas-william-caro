# Verificación del proyecto

Entorno: Python 3.12.14; versiones de Streamlit, pandas y Plotly registradas en `requirements.txt`.

Se ejecutó la aplicación con `streamlit.testing.v1.AppTest` y se comprobaron:

- Carga de los 24 registros sin excepciones de la aplicación.
- Ventas acumuladas: 3,347.0 millones; publicidad acumulada: 571.9 millones, contrastadas con el CSV.
- Título inicial: +82.1% en ventas y +15.7% en publicidad.
- Filtro por 2025: 12 observaciones.
- Cambio a la escala indexada sin excepciones.
- Selección de un solo mes: indicador de un mes y título descriptivo sin afirmar una evolución.

No se completó la inspección visual en navegador por una restricción del entorno al iniciar Chromium. Antes de entregar el enlace final, conviene abrir la aplicación publicada en escritorio y teléfono. No se realizó un despliegue en una cuenta de GitHub/Streamlit.

El archivo RAR se verificó abriendo todos sus miembros y comparando sus bytes con los originales. El CSV empaquetado coincide con el suministrado.
