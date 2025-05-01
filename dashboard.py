import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard Retail Avanzado", layout="wide", 
                  initial_sidebar_state="expanded")

# Estilo personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subheader {
        font-size: 1.5rem;
        color: #2563EB;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .card {
        border-radius: 10px;
        padding: 1.5rem;
        background-color: #F3F4F6;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-label {
        font-size: 1rem;
        color: #4B5563;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E40AF;
    }
    .small-text {
        font-size: 0.8rem;
        color: #6B7280;
    }
</style>
""", unsafe_allow_html=True)

# Conexión a la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

@st.cache_data(ttl=3600)
def cargar_datos():
    df = pd.read_sql("SELECT * FROM ventas", engine)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['mes'] = df['fecha'].dt.to_period("M").astype(str)
    df['dia_semana'] = df['fecha'].dt.day_name()
    df['semana'] = df['fecha'].dt.isocalendar().week
    return df

@st.cache_data(ttl=3600)
def cargar_inventario():
    return pd.read_sql("SELECT * FROM inventario", engine)

@st.cache_data(ttl=3600)
def cargar_clientes():
    df = pd.read_sql("SELECT * FROM clientes", engine)
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

# Cargar todos los datos
try:
    df_ventas = cargar_datos()
    df_inventario = cargar_inventario()
    df_clientes = cargar_clientes()
    
    # Fusionar datos para análisis
    df_completo = pd.merge(df_ventas, df_clientes, on=['fecha', 'tienda'], how='left')
except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    st.stop()

# Sidebar para filtros
st.sidebar.markdown("<h2>Filtros</h2>", unsafe_allow_html=True)

# Filtro de rango de fechas
min_date = df_ventas['fecha'].min().date()
max_date = df_ventas['fecha'].max().date()
fecha_inicio, fecha_fin = st.sidebar.date_input(
    "Rango de fechas",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Convertir a datetime para filtrado
fecha_inicio = pd.Timestamp(fecha_inicio)
fecha_fin = pd.Timestamp(fecha_fin) + timedelta(days=1) - timedelta(seconds=1)

# Filtros adicionales
tienda = st.sidebar.multiselect(
    "Tienda",
    options=["Todas"] + sorted(df_ventas["tienda"].unique().tolist()),
    default="Todas"
)

producto = st.sidebar.multiselect(
    "Producto",
    options=["Todos"] + sorted(df_ventas["producto"].unique().tolist()),
    default="Todos"
)

# Aplicar filtros
df_filtrado = df_ventas.copy()
df_completo_filtrado = df_completo.copy()

# Filtro de fechas
df_filtrado = df_filtrado[(df_filtrado['fecha'] >= fecha_inicio) & (df_filtrado['fecha'] <= fecha_fin)]
df_completo_filtrado = df_completo_filtrado[(df_completo_filtrado['fecha'] >= fecha_inicio) & (df_completo_filtrado['fecha'] <= fecha_fin)]

# Filtro de tienda
if "Todas" not in tienda:
    df_filtrado = df_filtrado[df_filtrado["tienda"].isin(tienda)]
    df_completo_filtrado = df_completo_filtrado[df_completo_filtrado["tienda"].isin(tienda)]

# Filtro de producto
if "Todos" not in producto:
    df_filtrado = df_filtrado[df_filtrado["producto"].isin(producto)]
    df_completo_filtrado = df_completo_filtrado[df_completo_filtrado["producto"].isin(producto)]

# Panel principal
st.markdown("<h1 class='main-header'>📊 Dashboard de Ventas Retail</h1>", unsafe_allow_html=True)

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<p class='metric-label'>💰 Total Ventas</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='metric-value'>${df_filtrado['total'].sum():,.2f}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<p class='metric-label'>📦 Ticket Promedio</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='metric-value'>${df_filtrado['total'].mean():,.2f}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<p class='metric-label'>🛒 Unidades Vendidas</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='metric-value'>{df_filtrado['cantidad'].sum():,}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<p class='metric-label'>🧾 Transacciones</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='metric-value'>{len(df_filtrado):,}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<h2 class='subheader'>Análisis Temporal</h2>", unsafe_allow_html=True)

# Gráficos en pestañas
tab1, tab2, tab3 = st.tabs(["Ventas Diarias", "Ventas por Producto", "Comparativa por Tienda"])

with tab1:
    # Gráfico de ventas diarias
    ventas_diarias = df_filtrado.groupby('fecha')['total'].sum().reset_index()
    fig_diarias = px.line(ventas_diarias, x='fecha', y='total', 
                        title="Evolución Diaria de Ventas", 
                        markers=True,
                        template="plotly_white")
    fig_diarias.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Ventas ($)",
        height=400
    )
    st.plotly_chart(fig_diarias, use_container_width=True)

with tab2:
    # Ventas por producto
    ventas_producto = df_filtrado.groupby('producto')['total'].sum().reset_index().sort_values('total', ascending=False)
    fig_producto = px.bar(ventas_producto, x='producto', y='total', 
                        title="Ventas por Producto",
                        color='producto',
                        template="plotly_white")
    fig_producto.update_layout(
        xaxis_title="Producto",
        yaxis_title="Ventas ($)",
        height=400
    )
    st.plotly_chart(fig_producto, use_container_width=True)

with tab3:
    # Comparativa por tienda
    ventas_tienda = df_filtrado.groupby(['tienda', 'fecha'])['total'].sum().reset_index()
    fig_tienda = px.line(ventas_tienda, x='fecha', y='total', color='tienda', 
                       title="Comparativa de Ventas por Tienda",
                       markers=True,
                       template="plotly_white")
    fig_tienda.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Ventas ($)",
        height=400
    )
    st.plotly_chart(fig_tienda, use_container_width=True)

# Segunda fila de visualizaciones
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h2 class='subheader'>Distribución de Ventas</h2>", unsafe_allow_html=True)
    # Gráfico pastel de distribución por tienda
    ventas_tienda_total = df_filtrado.groupby('tienda')['total'].sum().reset_index()
    fig_pie = px.pie(ventas_tienda_total, values='total', names='tienda', 
                    title="Distribución de Ventas por Tienda",
                    hole=0.4,
                    template="plotly_white")
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.markdown("<h2 class='subheader'>Top Productos</h2>", unsafe_allow_html=True)
    # Top productos por cantidad vendida
    top_productos = df_filtrado.groupby('producto')['cantidad'].sum().reset_index().sort_values('cantidad', ascending=False)
    fig_top = px.bar(top_productos, x='producto', y='cantidad', 
                    title="Productos por Unidades Vendidas",
                    color='producto',
                    template="plotly_white")
    fig_top.update_layout(
        xaxis_title="Producto",
        yaxis_title="Unidades vendidas",
        showlegend=False
    )
    st.plotly_chart(fig_top, use_container_width=True)

# Análisis de inventario y stock
st.markdown("<h2 class='subheader'>Análisis de Inventario</h2>", unsafe_allow_html=True)

# Cálculo de stock vs ventas
inventario_analisis = df_inventario.copy()
ventas_por_producto = df_filtrado.groupby('producto')['cantidad'].sum().reset_index()
inventario_analisis = pd.merge(inventario_analisis, ventas_por_producto, on='producto', how='left')
inventario_analisis['cantidad'] = inventario_analisis['cantidad'].fillna(0)
inventario_analisis['porcentaje_vendido'] = (inventario_analisis['cantidad'] / inventario_analisis['stock_actual']) * 100
inventario_analisis['porcentaje_vendido'] = inventario_analisis['porcentaje_vendido'].clip(upper=100)  # Limitar a 100%

# Crear el gráfico
fig_inventario = go.Figure()

# Añadir barras para stock actual
fig_inventario.add_trace(go.Bar(
    x=inventario_analisis['producto'],
    y=inventario_analisis['stock_actual'],
    name='Stock Actual',
    marker_color='lightblue'
))

# Añadir barras para ventas
fig_inventario.add_trace(go.Bar(
    x=inventario_analisis['producto'],
    y=inventario_analisis['cantidad'],
    name='Unidades Vendidas',
    marker_color='coral'
))

# Actualizar layout
fig_inventario.update_layout(
    title='Stock Actual vs. Unidades Vendidas',
    barmode='group',
    xaxis_title='Producto',
    yaxis_title='Cantidad',
    template='plotly_white',
    height=400
)

st.plotly_chart(fig_inventario, use_container_width=True)

# Tabla detallada
st.markdown("<h2 class='subheader'>Datos Detallados</h2>", unsafe_allow_html=True)

# Opciones para explorar datos
option = st.selectbox(
    "Seleccionar vista:",
    ["Transacciones", "Inventario", "Clientes"]
)

if option == "Transacciones":
    st.dataframe(df_filtrado, use_container_width=True)
elif option == "Inventario":
    st.dataframe(df_inventario, use_container_width=True)
else:
    st.dataframe(df_clientes, use_container_width=True)

# Información adicional
st.markdown("<p class='small-text'>Última actualización: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "</p>", unsafe_allow_html=True)