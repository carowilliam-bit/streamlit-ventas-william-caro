"""Exploración descriptiva de ventas y publicidad. Ejecutar con streamlit run app.py."""
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Ventas y publicidad | William Caro", page_icon="📈", layout="wide")
st.markdown("""<style>
.block-container {max-width:1160px;padding-top:2.4rem;}
[data-testid="stMetric"] {background:#eef3fa;border:1px solid #d9e3f2;border-radius:12px;padding:16px;}
h1,h2,h3 {letter-spacing:-.025em;}
</style>""", unsafe_allow_html=True)

@st.cache_data
def cargar_datos():
    # La ruta absoluta se deriva del script, sin depender de la carpeta de ejecución.
    tabla = pd.read_csv(Path(__file__).parent / "data" / "01_ventas_mensuales.csv", encoding="utf-8-sig")
    requeridas = {"fecha", "mes", "ventas_millones", "publicidad_millones"}
    if not requeridas.issubset(tabla.columns):
        raise ValueError("El CSV no contiene todas las columnas requeridas.")
    tabla["fecha"] = pd.to_datetime(tabla["fecha"], errors="raise")
    for col in ["ventas_millones", "publicidad_millones"]:
        tabla[col] = pd.to_numeric(tabla[col], errors="raise")
        if tabla[col].isna().any() or (tabla[col] <= 0).any():
            raise ValueError("Se requieren importes positivos y completos.")
    if tabla.empty or tabla["fecha"].duplicated().any() or tabla["fecha"].isna().any():
        raise ValueError("Se requieren meses únicos y fechas válidas.")
    return tabla.sort_values("fecha").reset_index(drop=True)

try:
    datos = cargar_datos()
except (OSError, ValueError) as error:
    st.error(f"No fue posible cargar los datos: {error}")
    st.stop()

st.caption("VISUALIZACIÓN DE DATOS · WILLIAM CARO")
st.title("Ventas y publicidad")
st.write("¿Cómo evolucionan las ventas y la inversión publicitaria mes a mes?")
st.caption("Pregunta propuesta a partir de la guía adjunta · Datos ficticios, enero de 2024 a diciembre de 2025.")

with st.sidebar:
    st.header("Explorar el periodo")
    anios = sorted(datos.fecha.dt.year.unique().tolist())
    periodo = st.selectbox("Año", ["Todos", *map(str, anios)])
    vista = st.radio("Escala de la gráfica", ["Valores en millones", "Índice: primer mes = 100"])
    st.caption("El índice compara cambios relativos. Los millones comparan importes en una escala común.")
    st.divider()
    st.caption("Fuente única: 01_ventas_mensuales.csv\n\n24 observaciones mensuales · 4 columnas\n\nLa moneda no está especificada en el archivo.")

base = datos if periodo == "Todos" else datos[datos.fecha.dt.year == int(periodo)]
meses = base.mes.tolist()
inicio, fin = st.select_slider("Intervalo de meses", options=meses, value=(meses[0], meses[-1]))
filtrado = base.iloc[meses.index(inicio):meses.index(fin)+1].copy()
primero, ultimo = filtrado.iloc[0], filtrado.iloc[-1]
gv = (ultimo.ventas_millones / primero.ventas_millones - 1) * 100
gp = (ultimo.publicidad_millones / primero.publicidad_millones - 1) * 100
n = len(filtrado)
cols = st.columns(3)
cols[0].metric("Ventas acumuladas · millones", f"{filtrado.ventas_millones.sum():,.1f}")
cols[1].metric("Publicidad acumulada · millones", f"{filtrado.publicidad_millones.sum():,.1f}")
cols[2].metric("Meses seleccionados", str(n))

if n > 1:
    st.subheader(f"Las ventas {'suben' if gv >= 0 else 'bajan'} {abs(gv):.1f}% y la publicidad {'sube' if gp >= 0 else 'baja'} {abs(gp):.1f}%")
    st.caption(f"Comparación entre {primero['mes']} y {ultimo['mes']}; variación entre extremos, no crecimiento acumulado mensual.")
else:
    st.subheader(f"Las ventas registran {primero.ventas_millones:,.1f} millones en {primero['mes']}")
    st.caption("Un solo mes no permite describir una evolución temporal.")

fig = go.Figure()
for columna, nombre, color, guion in [
    ("ventas_millones", "Ventas", "#1858a8", "solid"),
    ("publicidad_millones", "Publicidad", "#c25716", "dash"),
]:
    valores = filtrado[columna]
    if vista.startswith("Índice"):
        valores = valores / valores.iloc[0] * 100
    fig.add_trace(go.Scatter(
        x=filtrado.fecha, y=valores, mode="lines+markers", name=nombre,
        line=dict(color=color, width=3, dash=guion), marker=dict(size=7),
        customdata=filtrado[["mes", columna]].to_numpy(),
        hovertemplate="%{customdata[0]}<br>" + nombre + ": %{customdata[1]:,.1f} millones<br>Valor del eje: %{y:,.1f}<extra></extra>",
    ))
fig.update_layout(
    template="plotly_white", height=440, margin=dict(l=15,r=15,t=30,b=20),
    legend=dict(orientation="h", y=1.12, x=0), hovermode="x unified",
    yaxis_title="Índice (primer mes seleccionado = 100)" if vista.startswith("Índice") else "Millones · moneda no especificada",
    xaxis_title="Mes", font=dict(family="Arial", size=13, color="#20314d"),
)
fig.update_yaxes(rangemode="tozero", gridcolor="#e9edf3")
fig.update_xaxes(tickvals=filtrado.fecha, ticktext=filtrado.mes, nticks=12, tickangle=-45)
st.plotly_chart(fig, width="stretch", config={"displaylogo": False})
st.info("Límite de interpretación: estas series descriptivas y ficticias no permiten concluir que la publicidad cause el aumento de las ventas, ni calcular su retorno causal.")

with st.expander("Interpretación y elección de la gráfica", expanded=True):
    if n > 1:
        st.write(f"Entre {primero['mes']} y {ultimo['mes']}, las ventas pasan de {primero.ventas_millones:,.1f} a {ultimo.ventas_millones:,.1f} millones; la publicidad pasa de {primero.publicidad_millones:,.1f} a {ultimo.publicidad_millones:,.1f} millones.")
    st.write("Las líneas conservan el orden temporal y permiten comparar las dos series. Se utiliza un solo eje vertical para evitar que dos escalas distintas sugieran una relación artificial. La vista de índice facilita comparar los cambios relativos sin confundirlos con importes monetarios.")
    st.caption("No se controlan otros factores, estacionalidad ni efectos rezagados. Los resultados describen exclusivamente el intervalo seleccionado.")
with st.expander("Datos y descarga"):
    st.dataframe(filtrado, hide_index=True, width="stretch", column_config={"fecha": st.column_config.DateColumn("Fecha", format="YYYY-MM-DD")})
    st.download_button("Descargar selección en CSV", filtrado.to_csv(index=False).encode("utf-8-sig"), "ventas_seleccionadas.csv", "text/csv")
st.caption("Desarrollado por William Caro · Ejercicio académico · Streamlit + Python")
