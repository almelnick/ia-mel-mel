import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Ventas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 Dashboard de Ventas Empresariales")
st.markdown("---")

# Datos de ejemplo
@st.cache_data
def load_data():
    # Datos de ventas mensuales
    df_ventas = pd.DataFrame({
        'mes': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio'],
        'ventas': [45000, 52000, 48000, 61000, 55000, 67000]
    })
    
    # Datos de productos
    df_productos = pd.DataFrame({
        'producto': ['Producto A', 'Producto B', 'Producto C', 'Producto D', 'Producto E'],
        'cantidad': [120, 95, 180, 75, 140]
    })
    
    # Datos de regiones
    df_regiones = pd.DataFrame({
        'region': ['Norte', 'Sur', 'Este', 'Oeste'],
        'ventas': [125000, 98000, 87000, 110000]
    })
    
    return df_ventas, df_productos, df_regiones

df_ventas, df_productos, df_regiones = load_data()

# Sidebar
st.sidebar.title("🎛️ Panel de Control")
st.sidebar.markdown("---")

# Filtros
periodo_seleccionado = st.sidebar.selectbox(
    "Seleccionar Período:",
    ["Último mes", "Últimos 3 meses", "Últimos 6 meses", "Año completo"]
)

region_seleccionada = st.sidebar.multiselect(
    "Seleccionar Regiones:",
    df_regiones['region'].tolist(),
    default=df_regiones['region'].tolist()
)

# Métricas principales
st.subheader("📈 Métricas Principales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Ventas Totales",
        value="$328,000",
        delta="12.5%"
    )

with col2:
    st.metric(
        label="Clientes Activos",
        value="1,234",
        delta="8.2%"
    )

with col3:
    st.metric(
        label="Productos Vendidos",
        value="2,580",
        delta="-2.1%"
    )

with col4:
    st.metric(
        label="Tasa de Conversión",
        value="3.45%",
        delta="0.8%"
    )

st.markdown("---")

# Gráficos principales
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Evolución de Ventas")
    
    # Gráfico de líneas para ventas mensuales
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df_ventas['mes'], df_ventas['ventas'], marker='o', linewidth=2, markersize=8)
    ax.set_title('Evolución de Ventas Mensuales', fontsize=16, fontweight='bold')
    ax.set_xlabel('Mes', fontsize=12)
    ax.set_ylabel('Ventas ($)', fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

with col2:
    st.subheader("🛍️ Ventas por Producto")
    
    # Gráfico de barras para productos
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(df_productos['producto'], df_productos['cantidad'], 
                  color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
    ax.set_title('Ventas por Producto', fontsize=16, fontweight='bold')
    ax.set_xlabel('Producto', fontsize=12)
    ax.set_ylabel('Cantidad Vendida', fontsize=12)
    
    # Agregar valores en las barras
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{int(height)}', ha='center', va='bottom')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

st.markdown("---")

# Segunda fila de gráficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌍 Distribución por Regiones")
    
    if region_seleccionada:
        # Filtrar datos según selección
        df_regiones_filtrado = df_regiones[df_regiones['region'].isin(region_seleccionada)]
        
        # Gráfico de pastel para distribución regional
        fig, ax = plt.subplots(figsize=(8, 8))
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        wedges, texts, autotexts = ax.pie(df_regiones_filtrado['ventas'], 
                                          labels=df_regiones_filtrado['region'],
                                          autopct='%1.1f%%',
                                          colors=colors,
                                          startangle=90)
        ax.set_title('Distribución de Ventas por Región', fontsize=16, fontweight='bold')
        
        # Mejorar la apariencia del texto
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        st.pyplot(fig)
    else:
        st.warning("Selecciona al menos una región para ver el gráfico.")

with col2:
    st.subheader("📊 Tabla de Datos")
    
    # Crear datos combinados para la tabla
    tabla_resumen = pd.DataFrame({
        'Categoría': ['Ventas Totales', 'Mejor Mes', 'Producto Top', 'Región Líder'],
        'Valor': [
            f"${df_ventas['ventas'].sum():,}",
            df_ventas.loc[df_ventas['ventas'].idxmax(), 'mes'],
            df_productos.loc[df_productos['cantidad'].idxmax(), 'producto'],
            df_regiones.loc[df_regiones['ventas'].idxmax(), 'region']
        ],
        'Detalle': [
            'Acumulado semestral',
            f"${df_ventas['ventas'].max():,}",
            f"{df_productos['cantidad'].max()} unidades",
            f"${df_regiones['ventas'].max():,}"
        ]
    })
    
    st.dataframe(tabla_resumen, use_container_width=True)
    
    # Tabla detallada de productos
    st.subheader("📦 Detalle de Productos")
    st.dataframe(df_productos, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666666;'>
        Dashboard desarrollado con Streamlit 📊 | Última actualización: Hoy
    </div>
    """, 
    unsafe_allow_html=True
)

# Información adicional en sidebar
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Información del Dashboard:**
    
    - 📊 Datos actualizados en tiempo real
    - 🎯 Métricas clave de rendimiento
    - 📈 Análisis de tendencias
    - 🌍 Segmentación regional
    """
)

st.sidebar.success("Dashboard cargado correctamente ✅")
