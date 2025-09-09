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

# Inicializar estado de sesión
if 'onboarding_complete' not in st.session_state:
    st.session_state.onboarding_complete = False
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'user_config' not in st.session_state:
    st.session_state.user_config = {}

def show_onboarding():
    """Proceso de onboarding paso a paso"""
    
    st.title("🚀 Bienvenido a tu Dashboard de Ventas")
    st.markdown("Te ayudaremos a configurar tu dashboard en unos simples pasos.")
    
    # Barra de progreso
    progress = (st.session_state.current_step - 1) / 4
    st.progress(progress)
    st.write(f"Paso {st.session_state.current_step} de 5")
    
    if st.session_state.current_step == 1:
        show_step_welcome()
    elif st.session_state.current_step == 2:
        show_step_data_source()
    elif st.session_state.current_step == 3:
        show_step_metrics()
    elif st.session_state.current_step == 4:
        show_step_visualization()
    elif st.session_state.current_step == 5:
        show_step_final()

def show_step_welcome():
    """Paso 1: Bienvenida y configuración básica"""
    st.subheader("Paso 1: Información Básica")
    
    col1, col2 = st.columns(2)
    
    with col1:
        company_name = st.text_input(
            "Nombre de tu empresa:",
            placeholder="Ej: Mi Empresa S.A."
        )
        
        industry = st.selectbox(
            "Industria:",
            ["Retail", "E-commerce", "Servicios", "Manufactura", "Tecnología", "Otro"]
        )
    
    with col2:
        currency = st.selectbox(
            "Moneda:",
            ["USD", "EUR", "CLP", "MXN", "ARS", "COL"]
        )
        
        timezone = st.selectbox(
            "Zona horaria:",
            ["America/Santiago", "America/Mexico_City", "America/New_York", "Europe/Madrid"]
        )
    
    st.markdown("---")
    
    if st.button("Continuar", type="primary", disabled=not company_name):
        st.session_state.user_config.update({
            'company_name': company_name,
            'industry': industry,
            'currency': currency,
            'timezone': timezone
        })
        st.session_state.current_step = 2
        st.rerun()

def show_step_data_source():
    """Paso 2: Selección de fuente de datos"""
    st.subheader("Paso 2: ¿Cómo quieres conectar tus datos?")
    
    data_options = {
        "demo": {
            "title": "Usar datos de demostración",
            "description": "Perfecto para probar el dashboard",
            "icon": "🎮"
        },
        "csv": {
            "title": "Subir archivo CSV/Excel",
            "description": "Sube tus archivos de ventas",
            "icon": "📁"
        },
        "database": {
            "title": "Conectar base de datos",
            "description": "MySQL, PostgreSQL, SQL Server",
            "icon": "🗄️"
        },
        "api": {
            "title": "Conectar API",
            "description": "Shopify, WooCommerce, REST API",
            "icon": "🔌"
        }
    }
    
    selected_source = None
    
    for key, option in data_options.items():
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button(option["icon"], key=f"btn_{key}"):
                selected_source = key
        
        with col2:
            st.write(f"**{option['title']}**")
            st.write(option["description"])
        
        st.markdown("---")
    
    # Configuración específica según la selección
    if selected_source == "csv":
        show_csv_config()
    elif selected_source == "database":
        show_database_config()
    elif selected_source == "api":
        show_api_config()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Atrás"):
            st.session_state.current_step = 1
            st.rerun()
    
    with col2:
        if st.button("Continuar", type="primary"):
            st.session_state.user_config['data_source'] = selected_source or 'demo'
            st.session_state.current_step = 3
            st.rerun()

def show_csv_config():
    """Configuración para archivos CSV"""
    st.info("📄 Sube tu archivo de ventas (CSV o Excel)")
    
    uploaded_file = st.file_uploader(
        "Selecciona tu archivo:",
        type=['csv', 'xlsx'],
        help="El archivo debe contener al menos columnas de fecha y monto de ventas"
    )
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success("Archivo cargado correctamente!")
            st.write("Vista previa:")
            st.dataframe(df.head())
            
            # Mapeo de columnas
            st.write("Mapea las columnas de tu archivo:")
            col1, col2 = st.columns(2)
            
            with col1:
                date_column = st.selectbox("Columna de fecha:", df.columns)
            with col2:
                sales_column = st.selectbox("Columna de ventas:", df.columns)
            
            st.session_state.user_config.update({
                'uploaded_data': df,
                'date_column': date_column,
                'sales_column': sales_column
            })
            
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")

def show_database_config():
    """Configuración para base de datos"""
    st.info("🗄️ Conecta tu base de datos")
    
    db_type = st.selectbox("Tipo de base de datos:", ["MySQL", "PostgreSQL", "SQL Server"])
    
    col1, col2 = st.columns(2)
    with col1:
        host = st.text_input("Host:", placeholder="localhost")
        database = st.text_input("Base de datos:", placeholder="ventas_db")
    
    with col2:
        port = st.text_input("Puerto:", placeholder="3306")
        username = st.text_input("Usuario:", placeholder="admin")
    
    password = st.text_input("Contraseña:", type="password")
    
    if st.button("Probar conexión"):
        st.info("Funcionalidad disponible en la versión completa")

def show_api_config():
    """Configuración para APIs"""
    st.info("🔌 Conecta tu API")
    
    api_type = st.selectbox("Tipo de API:", ["Shopify", "WooCommerce", "REST API personalizada"])
    
    if api_type == "Shopify":
        shop_domain = st.text_input("Dominio de la tienda:", placeholder="mi-tienda.myshopify.com")
        api_key = st.text_input("API Key:", type="password")
    elif api_type == "REST API personalizada":
        api_url = st.text_input("URL de la API:", placeholder="https://api.empresa.com")
        api_token = st.text_input("Token de autenticación:", type="password")

def show_step_metrics():
    """Paso 3: Selección de métricas"""
    st.subheader("Paso 3: ¿Qué métricas quieres ver?")
    
    st.write("Selecciona las métricas más importantes para tu negocio:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Métricas de Ventas:**")
        metrics_sales = st.multiselect(
            "",
            ["Ventas Totales", "Ventas por Período", "Crecimiento de Ventas", "Promedio de Venta"],
            default=["Ventas Totales", "Crecimiento de Ventas"],
            key="sales_metrics"
        )
        
        st.write("**Métricas de Productos:**")
        metrics_products = st.multiselect(
            "",
            ["Productos Más Vendidos", "Inventario", "Margen por Producto", "Rotación"],
            default=["Productos Más Vendidos"],
            key="product_metrics"
        )
    
    with col2:
        st.write("**Métricas de Clientes:**")
        metrics_customers = st.multiselect(
            "",
            ["Clientes Activos", "Nuevos Clientes", "Valor de Vida del Cliente", "Retención"],
            default=["Clientes Activos", "Nuevos Clientes"],
            key="customer_metrics"
        )
        
        st.write("**Métricas Geográficas:**")
        metrics_geo = st.multiselect(
            "",
            ["Ventas por Región", "Ventas por Ciudad", "Mapa de Calor", "Distribución"],
            default=["Ventas por Región"],
            key="geo_metrics"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Atrás"):
            st.session_state.current_step = 2
            st.rerun()
    
    with col2:
        if st.button("Continuar", type="primary"):
            st.session_state.user_config.update({
                'metrics_sales': metrics_sales,
                'metrics_products': metrics_products,
                'metrics_customers': metrics_customers,
                'metrics_geo': metrics_geo
            })
            st.session_state.current_step = 4
            st.rerun()

def show_step_visualization():
    """Paso 4: Preferencias de visualización"""
    st.subheader("Paso 4: Personaliza tu dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Tema del dashboard:**")
        theme = st.radio(
            "",
            ["Claro", "Oscuro", "Automático"],
            horizontal=True
        )
        
        st.write("**Período por defecto:**")
        default_period = st.selectbox(
            "",
            ["Últimos 7 días", "Últimos 30 días", "Últimos 3 meses", "Último año"]
        )
    
    with col2:
        st.write("**Actualización de datos:**")
        refresh_frequency = st.selectbox(
            "",
            ["Manual", "Cada hora", "Cada día", "Cada semana"]
        )
        
        st.write("**Formato de números:**")
        number_format = st.selectbox(
            "",
            ["1,234.56", "1.234,56", "1 234.56"]
        )
    
    st.write("**Colores del dashboard:**")
    color_scheme = st.selectbox(
        "Esquema de colores:",
        ["Azul profesional", "Verde natura", "Naranja vibrante", "Morado creativo"]
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Atrás"):
            st.session_state.current_step = 3
            st.rerun()
    
    with col2:
        if st.button("Continuar", type="primary"):
            st.session_state.user_config.update({
                'theme': theme,
                'default_period': default_period,
                'refresh_frequency': refresh_frequency,
                'number_format': number_format,
                'color_scheme': color_scheme
            })
            st.session_state.current_step = 5
            st.rerun()

def show_step_final():
    """Paso 5: Resumen y finalización"""
    st.subheader("🎉 ¡Todo listo!")
    
    st.write("Tu dashboard ha sido configurado con las siguientes opciones:")
    
    config = st.session_state.user_config
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Configuración General:**")
        st.write(f"• Empresa: {config.get('company_name', 'No especificada')}")
        st.write(f"• Industria: {config.get('industry', 'No especificada')}")
        st.write(f"• Moneda: {config.get('currency', 'USD')}")
        
        st.write("**Fuente de Datos:**")
        data_source_names = {
            'demo': 'Datos de demostración',
            'csv': 'Archivo CSV/Excel',
            'database': 'Base de datos',
            'api': 'API externa'
        }
        st.write(f"• {data_source_names.get(config.get('data_source', 'demo'), 'Demo')}")
    
    with col2:
        st.write("**Preferencias:**")
        st.write(f"• Tema: {config.get('theme', 'Claro')}")
        st.write(f"• Período: {config.get('default_period', 'Últimos 30 días')}")
        st.write(f"• Actualización: {config.get('refresh_frequency', 'Manual')}")
        
        st.write("**Métricas Seleccionadas:**")
        total_metrics = len(config.get('metrics_sales', [])) + len(config.get('metrics_products', [])) + len(config.get('metrics_customers', [])) + len(config.get('metrics_geo', []))
        st.write(f"• {total_metrics} métricas activas")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Atrás"):
            st.session_state.current_step = 4
            st.rerun()
    
    with col2:
        if st.button("Reiniciar configuración"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    with col3:
        if st.button("Completar configuración", type="primary"):
            st.session_state.onboarding_complete = True
            st.balloons()
            st.rerun()

def show_dashboard():
    """Dashboard principal después del onboarding"""
    config = st.session_state.user_config
    
    # Título personalizado
    company_name = config.get('company_name', 'Mi Empresa')
    st.title(f"📊 Dashboard de {company_name}")
    
    # Botón para reconfigurar en la sidebar
    with st.sidebar:
        st.write("**Configuración Actual:**")
        st.write(f"Empresa: {company_name}")
        st.write(f"Fuente: {config.get('data_source', 'demo')}")
        
        if st.button("🔧 Reconfigurar Dashboard"):
            st.session_state.onboarding_complete = False
            st.session_state.current_step = 1
            st.rerun()
    
    # Cargar datos según configuración
    df_ventas, df_productos, df_regiones = load_data_based_on_config()
    
    # Mostrar métricas seleccionadas
    show_selected_metrics(config)
    
    # Mostrar visualizaciones
    show_visualizations(df_ventas, df_productos, df_regiones, config)

@st.cache_data
def load_data_based_on_config():
    """Cargar datos según la configuración del usuario"""
    config = st.session_state.user_config
    
    if config.get('data_source') == 'csv' and 'uploaded_data' in config:
        # Procesar datos cargados por el usuario
        df = config['uploaded_data']
        # Aquí procesarías los datos reales del usuario
        # Por ahora retornamos datos de ejemplo
        pass
    
    # Datos de ejemplo (fallback)
    df_ventas = pd.DataFrame({
        'mes': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio'],
        'ventas': [45000, 52000, 48000, 61000, 55000, 67000]
    })
    
    df_productos = pd.DataFrame({
        'producto': ['Producto A', 'Producto B', 'Producto C', 'Producto D', 'Producto E'],
        'cantidad': [120, 95, 180, 75, 140]
    })
    
    df_regiones = pd.DataFrame({
        'region': ['Norte', 'Sur', 'Este', 'Oeste'],
        'ventas': [125000, 98000, 87000, 110000]
    })
    
    return df_ventas, df_productos, df_regiones

def show_selected_metrics(config):
    """Mostrar solo las métricas seleccionadas por el usuario"""
    metrics_sales = config.get('metrics_sales', [])
    
    if metrics_sales:
        st.subheader("📈 Métricas de Ventas")
        
        cols = st.columns(len(metrics_sales))
        
        for i, metric in enumerate(metrics_sales):
            with cols[i]:
                if metric == "Ventas Totales":
                    st.metric(label="Ventas Totales", value="$328,000", delta="12.5%")
                elif metric == "Crecimiento de Ventas":
                    st.metric(label="Crecimiento", value="15.3%", delta="2.1%")
                # Agregar más métricas según selección

def show_visualizations(df_ventas, df_productos, df_regiones, config):
    """Mostrar visualizaciones según configuración"""
    
    # Aplicar esquema de colores seleccionado
    color_schemes = {
        "Azul profesional": ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78'],
        "Verde natura": ['#2ca02c', '#98df8a', '#d62728', '#ff9896'],
        "Naranja vibrante": ['#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a'],
        "Morado creativo": ['#9467bd', '#c5b0d5', '#8c564b', '#c49c94']
    }
    
    colors = color_schemes.get(config.get('color_scheme', 'Azul profesional'))
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if "Ventas por Período" in config.get('metrics_sales', []):
            st.subheader("📈 Evolución de Ventas")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(df_ventas['mes'], df_ventas['ventas'], 
                   marker='o', linewidth=2, markersize=8, color=colors[0])
            ax.set_title('Evolución de Ventas Mensuales', fontweight='bold')
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
    
    with col2:
        if "Productos Más Vendidos" in config.get('metrics_products', []):
            st.subheader("🛍️ Productos Más Vendidos")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(df_productos['producto'], df_productos['cantidad'], 
                         color=colors)
            ax.set_title('Ventas por Producto', fontweight='bold')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

# Lógica principal
if not st.session_state.onboarding_complete:
    show_onboarding()
else:
    show_dashboard()
