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
    st.info("🔌 Conecta tus plataformas de marketing y ventas")
    
    api_categories = {
        "Publicidad": ["Meta Ads (Facebook/Instagram)", "Google Ads", "TikTok Ads", "LinkedIn Ads"],
        "E-commerce": ["Shopify", "WooCommerce", "Magento", "BigCommerce"],
        "Analytics": ["Google Analytics", "Mixpanel", "Hotjar", "Adobe Analytics"],
        "CRM": ["Salesforce", "HubSpot", "Pipedrive", "Zoho CRM"],
        "Email Marketing": ["Mailchimp", "SendGrid", "ConvertKit", "Klaviyo"]
    }
    
    selected_apis = []
    
    for category, apis in api_categories.items():
        with st.expander(f"📊 {category}"):
            for api in apis:
                if st.checkbox(api, key=f"api_{api}"):
                    selected_apis.append(api)
                    show_api_credentials(api)
    
    if selected_apis:
        st.session_state.user_config['selected_apis'] = selected_apis
        st.success(f"Seleccionadas {len(selected_apis)} integraciones")

def show_api_credentials(api_name):
    """Mostrar campos específicos para cada API"""
    st.write(f"**Configuración de {api_name}:**")
    
    if api_name == "Meta Ads (Facebook/Instagram)":
        col1, col2 = st.columns(2)
        with col1:
            app_id = st.text_input("App ID:", key=f"{api_name}_app_id", 
                                 help="ID de tu aplicación de Facebook")
            access_token = st.text_input("Access Token:", type="password", 
                                       key=f"{api_name}_token",
                                       help="Token de acceso de larga duración")
        with col2:
            app_secret = st.text_input("App Secret:", type="password", 
                                     key=f"{api_name}_secret")
            ad_account_id = st.text_input("Ad Account ID:", 
                                        key=f"{api_name}_account",
                                        help="ID de tu cuenta publicitaria (act_XXXXXXX)")
        
        st.info("📖 [Guía: Cómo obtener credenciales de Meta Ads](https://developers.facebook.com/docs/marketing-api/get-started)")
    
    elif api_name == "Google Ads":
        col1, col2 = st.columns(2)
        with col1:
            client_id = st.text_input("Client ID:", key=f"{api_name}_client_id")
            client_secret = st.text_input("Client Secret:", type="password", 
                                        key=f"{api_name}_client_secret")
        with col2:
            refresh_token = st.text_input("Refresh Token:", type="password", 
                                        key=f"{api_name}_refresh_token")
            customer_id = st.text_input("Customer ID:", key=f"{api_name}_customer_id",
                                      help="ID de cliente sin guiones (ej: 1234567890)")
        
        st.info("📖 [Guía: Configurar API de Google Ads](https://developers.google.com/google-ads/api/docs/first-call/overview)")
    
    elif api_name == "Shopify":
        col1, col2 = st.columns(2)
        with col1:
            shop_domain = st.text_input("Dominio de la tienda:", 
                                      placeholder="mi-tienda.myshopify.com",
                                      key=f"{api_name}_domain")
        with col2:
            api_key = st.text_input("Admin API Access Token:", type="password",
                                  key=f"{api_name}_token",
                                  help="Token de la API Admin")
        
        st.info("📖 [Guía: Generar token de Shopify](https://shopify.dev/apps/auth/admin-app-access-tokens)")
    
    elif api_name == "Google Analytics":
        col1, col2 = st.columns(2)
        with col1:
            property_id = st.text_input("Property ID:", key=f"{api_name}_property",
                                      help="ID de propiedad de GA4")
            credentials_file = st.file_uploader("Service Account JSON:", 
                                              type=['json'],
                                              key=f"{api_name}_credentials",
                                              help="Archivo de credenciales de la cuenta de servicio")
        with col2:
            view_id = st.text_input("View ID (opcional):", key=f"{api_name}_view",
                                  help="Para GA Universal Analytics")
        
        st.info("📖 [Guía: Configurar Google Analytics API](https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py)")
    
    elif api_name == "HubSpot":
        access_token = st.text_input("Private App Access Token:", type="password",
                                   key=f"{api_name}_token",
                                   help="Token de aplicación privada de HubSpot")
        
        st.info("📖 [Guía: Crear aplicación privada en HubSpot](https://developers.hubspot.com/docs/api/private-apps)")
    
    elif api_name == "Salesforce":
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username:", key=f"{api_name}_username")
            password = st.text_input("Password:", type="password", key=f"{api_name}_password")
        with col2:
            security_token = st.text_input("Security Token:", type="password", 
                                         key=f"{api_name}_token")
            domain = st.text_input("Domain:", placeholder="your-domain.salesforce.com",
                                 key=f"{api_name}_domain")
    
    else:
        # Configuración genérica para otras APIs
        col1, col2 = st.columns(2)
        with col1:
            api_url = st.text_input("API URL:", key=f"{api_name}_url",
                                  placeholder="https://api.example.com")
        with col2:
            api_token = st.text_input("API Token/Key:", type="password",
                                    key=f"{api_name}_token")
    
    # Botón de prueba de conexión
    if st.button(f"🔍 Probar conexión con {api_name}", key=f"test_{api_name}"):
        test_api_connection(api_name)

def test_api_connection(api_name):
    """Simular prueba de conexión con las APIs"""
    with st.spinner(f"Probando conexión con {api_name}..."):
        import time
        time.sleep(2)  # Simular tiempo de conexión
        
        # En una implementación real, aquí harías las llamadas a las APIs
        success_rate = np.random.choice([True, False], p=[0.8, 0.2])  # 80% éxito
        
        if success_rate:
            st.success(f"✅ Conexión exitosa con {api_name}")
            if api_name == "Meta Ads (Facebook/Instagram)":
                st.info("Se encontraron 3 cuentas publicitarias activas")
            elif api_name == "Google Ads":
                st.info("Se encontraron 2 cuentas de Google Ads")
            elif api_name == "Shopify":
                st.info("Tienda conectada: 1,234 productos encontrados")
        else:
            st.error(f"❌ Error al conectar con {api_name}. Verifica tus credenciales.")

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
