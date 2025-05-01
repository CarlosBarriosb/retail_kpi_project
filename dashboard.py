import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os

# Conexión a la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Consulta simple de ejemplo
@st.cache_data
def cargar_datos():
    return pd.read_sql("SELECT * FROM ventas", engine)

st.title("Dashboard de Ventas Retail")
df = cargar_datos()
st.dataframe(df)