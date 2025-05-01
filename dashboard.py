import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard Retail", layout="wide")

# Conexión a la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

@st.cache_data
def cargar_datos():
    df = pd.read_sql("SELECT * FROM ventas", engine)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['mes'] = df['fecha'].dt.to_period("M").astype(str)
    return df

df = cargar_datos()

st.title("📊 Dashboard de Ventas Retail")

# Filtros
col1, col2 = st.columns(2)
with col1:
    tienda = st.selectbox("Filtrar por tienda", ["Todas"] + sorted(df["tienda"].dropna().unique()))
with col2:
    año = st.selectbox("Filtrar por año", ["Todos"] + sorted(df["fecha"].dt.year.unique().astype(str)))

if tienda != "Todas":
    df = df[df["tienda"] == tienda]
if año != "Todos":
    df = df[df["fecha"].dt.year == int(año)]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Ventas", f"${df['ventas'].sum():,.2f}")
col2.metric("📦 Promedio por Venta", f"${df['ventas'].mean():,.2f}")
col3.metric("🧾 Transacciones", len(df))

st.markdown("---")

# Gráfico de ventas por mes
ventas_mes = df.groupby("mes")["ventas"].sum().reset_index()
fig = px.line(ventas_mes, x="mes", y="ventas", title="Evolución Mensual de Ventas", markers=True)
st.plotly_chart(fig, use_container_width=True)

# Tabla de datos
st.subheader("📄 Datos Detallados")
st.dataframe(df, use_container_width=True)
