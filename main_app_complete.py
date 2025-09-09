import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

# Configuración de página
st.set_page_config(
    page_title="🚀 Marketing Dashboard AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para diseño moderno
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    .stMetric {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 1rem;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
    }
    .insight-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.05));
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .recommendation-high {
        background: linear-gradient(135deg, rgba(220, 53, 69, 0.1), rgba(220, 53, 69, 0.05));
        border-left: 4px solid #dc3545;
    }
    .recommendation-medium {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.1), rgba(255, 193, 7, 0.05));
        border-left: 4px solid #ffc107;
    }
    .recommendation-low {
        background: linear-gradient(135deg, rgba(40, 167, 69, 0.1), rgba(40, 167, 69, 0.05));
        border-left: 4px solid #28a745;
    }
    .header-container {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Importar módulos locales (con manejo de errores)
try:
    from integrations.manager import IntegrationManager
    from utils.ai_analyzer import AIAnalyzer
    from utils.data_processor import DataProcessor
    from utils.intelligent_onboarding import IntelligentOnboarding
    from dashboards.ecommerce_dashboard import EcommerceDashboard
except ImportError as e:
    st.error(f"Error importando módulos: {e}")
    st.info("Asegúrate de que todos los archivos estén en las carpetas correctas")

# Inicializar managers
@st.cache_resource
def init_managers():
    return {
        'integration_manager': IntegrationManager(),
        'ai_analyzer': AIAnalyzer(),
        'data_processor': DataProcessor(),
        'onboarding_system': IntelligentOnboarding()
    }

managers = init_managers()

# Funciones principales
def main():
    # Verificar si el onboarding fue completado
    onboarding = managers['onboarding_system']
    
    if not onboarding.is_onboarding_completed() and not st.session_state.get('onboarding_completed'):
        # Mostrar onboarding
        onboarding.run_onboarding()
        return
    
    # Sidebar para navegación
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h1 style='color: white; font-size: 24px; margin-bottom: 10px;'>
                🚀 Marketing Dashboard
            </h1>
            <p style='color: rgba(255,255,255,0.8); font-size: 14px;'>
                Inteligencia de Marketing Digital
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        page = st.selectbox(
            "📍 Navegación",
            ["Dashboard Principal", "Configurar Integraciones", "Análisis IA", "Reportes", "Configuración"],
            key="navigation"
        )
        
        # Mostrar estado de integraciones
        st.markdown("---")
        active_integrations = managers['integration_manager'].get_active_integrations()
        
        if active_integrations:
            st.success(f"✅ {len(active_integrations)} integraciones activas")
            for integration in active_integrations:
                st.text(f"• {integration.title()}")
        else:
            st.warning("⚠️ Sin integraciones configuradas")
            st.info("👈 Ve a 'Configurar Integraciones' para empezar")
        
        # Quick stats en sidebar
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        if active_integrations:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("ROI", "245%", "12%")
            with col2:
                st.metric("ROAS", "3.2x", "0.3x")
    
    # Routing de páginas
    if page == "Dashboard Principal":
        show_dashboard()
    elif page == "Configurar Integraciones":
        show_integrations_config()
    elif page == "Análisis IA":
        show_ai_analysis()
    elif page == "Reportes":
        show_reports()
    elif page == "Configuración":
        show_settings()

def show_dashboard():
    """Dashboard principal con métricas y gráficos"""
    # Header
    st.markdown("""
    <div class="header-container">
        <h1 style="font-size: 3rem; font-weight: bold; margin-bottom: 1rem; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🚀 Dashboard Principal
        </h1>
        <p style="font-size: 1.2rem; color: #666; margin-bottom: 0;">
            Análisis en tiempo real de tu performance de marketing digital
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar integraciones
    active_integrations = managers['integration_manager'].get_active_integrations()
    if not active_integrations:
        st.warning("⚠️ No hay integraciones configuradas. Ve a la sección 'Configurar Integraciones' para empezar.")
        return
    
    # Selector de rango de fechas
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        start_date = st.date_input("📅 Fecha Inicio", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("📅 Fecha Fin", datetime.now())
    with col3:
        if st.button("🔄 Actualizar", type="primary"):
            st.cache_data.clear()
            st.rerun()
    
    # Obtener y mostrar datos
    dashboard_data = fetch_all_data(start_date, end_date)
    
    if dashboard_data:
        render_dashboard(dashboard_data)
    else:
        st.info("📊 Haz clic en 'Actualizar' para cargar el dashboard")

def fetch_all_data(start_date, end_date):
    """Obtener datos de todas las integraciones"""
    manager = managers['integration_manager']
    all_data = {}
    
    active_integrations = manager.get_active_integrations()
    
    if not active_integrations:
        return None
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, integration_name in enumerate(active_integrations):
        try:
            status_text.text(f"Obteniendo datos de {integration_name}...")
            data = manager.get_data(integration_name, start_date, end_date)
            all_data[integration_name] = data
            progress_bar.progress((i + 1) / len(active_integrations))
        except Exception as e:
            st.error(f"Error obteniendo datos de {integration_name}: {str(e)}")
    
    progress_bar.empty()
    status_text.empty()
    return all_data

def render_dashboard(data):
    """Renderizar dashboard con datos"""
    
    # Calcular KPIs
    kpis = managers['data_processor'].calculate_kpis(data)
    
    # KPIs principales
    st.subheader("📈 KPIs Principales")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        revenue = kpis.get('revenue', 0)
        revenue_change = kpis.get('revenue_change', 0)
        st.metric(
            "💰 Revenue Total",
            f"${revenue:,.0f}",
            f"{revenue_change:+.1f}%" if revenue_change else None
        )
    
    with col2:
        aov = kpis.get('aov', 0)
        aov_change = kpis.get('aov_change', 0)
        st.metric(
            "🛒 AOV",
            f"${aov:.2f}",
            f"{aov_change:+.1f}%" if aov_change else None
        )
    
    with col3:
        conv_rate = kpis.get('conversion_rate', 0)
        conv_change = kpis.get('conversion_rate_change', 0)
        st.metric(
            "📈 Conversión",
            f"{conv_rate:.2f}%",
            f"{conv_change:+.1f}%" if conv_change else None
        )
    
    with col4:
        roas = kpis.get('roas', 0)
        roas_change = kpis.get('roas_change', 0)
        st.metric(
            "🎯 ROAS",
            f"{roas:.1f}x",
            f"{roas_change:+.1f}%" if roas_change else None
        )
    
    with col5:
        orders = kpis.get('orders', 0)
        orders_change = kpis.get('orders_change', 0)
        st.metric(
            "📋 Órdenes",
            f"{orders:,}",
            f"{orders_change:+.1f}%" if orders_change else None
        )
    
    # Gráficos principales
    st.subheader("📊 Análisis de Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de gasto por canal
        channel_spend = managers['data_processor'].get_channel_spend(data)
        if not channel_spend.empty:
            fig = px.pie(
                channel_spend, 
                values='spend', 
                names='channel',
                title="💸 Distribución de Gasto por Canal",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(
                font=dict(size=12),
                showlegend=True,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de conversiones por canal
        channel_conversions = managers['data_processor'].get_channel_conversions(data)
        if not channel_conversions.empty:
            fig = px.bar(
                channel_conversions,
                x='channel',
                y='conversions',
                title="🎯 Conversiones por Canal",
                color='conversions',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                font=dict(size=12),
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Tabla de performance
    st.subheader("📋 Performance Detallado por Canal")
    
    channel_comparison = managers['data_processor'].get_channel_comparison(data)
    if not channel_comparison.empty:
        # Formatear datos para mostrar
        formatted_data = channel_comparison.copy()
        formatted_data['spend'] = formatted_data['spend'].apply(lambda x: f"${x:,.2f}")
        formatted_data['conversions'] = formatted_data['conversions'].apply(lambda x: f"{x:.0f}")
        formatted_data['roi'] = formatted_data['roi'].apply(lambda x: f"{x:.1f}%")
        formatted_data['cpc'] = formatted_data['cpc'].apply(lambda x: f"${x:.2f}")
        formatted_data['ctr'] = formatted_data['ctr'].apply(lambda x: f"{x:.2f}%" if x > 0 else "N/A")
        
        # Renombrar columnas
        formatted_data.columns = ['Canal', 'Gasto', 'Conversiones', 'ROI', 'CPC', 'CTR']
        
        st.dataframe(formatted_data, use_container_width=True, hide_index=True)
    
    # Insights automáticos
    st.subheader("🧠 Insights Automáticos")
    
    insights = managers['data_processor'].generate_performance_insights(data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**💡 Insights Principales:**")
        for insight in insights[:3]:
            if insight['type'] == 'positive':
                st.markdown(f"""
                <div class="insight-card">
                    <strong>✅ {insight['metric']}:</strong> {insight['message']} ({insight['value']})
                </div>
                """, unsafe_allow_html=True)
            elif insight['type'] == 'negative':
                st.markdown(f"""
                <div class="insight-card recommendation-high">
                    <strong>⚠️ {insight['metric']}:</strong> {insight['message']} ({insight['value']})
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("**🚀 Recomendaciones:**")
        ai_insights = managers['ai_analyzer'].analyze_data(data)
        
        for rec in ai_insights.get('recommendations', [])[:3]:
            priority_class = f"recommendation-{rec.get('priority', 'low')}"
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec.get('priority', 'low'), '⚪')
            
            st.markdown(f"""
            <div class="insight-card {priority_class}">
                <strong>{priority_icon} {rec.get('title', 'Recomendación')}:</strong><br>
                <small>{rec.get('description', 'Descripción no disponible')}</small>
            </div>
            """, unsafe_allow_html=True)

def show_integrations_config():
    """Página de configuración de integraciones"""
    st.markdown("""
    <div class="header-container">
        <h1 style="font-size: 3rem; font-weight: bold; margin-bottom: 1rem; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🔗 Configurar Integraciones
        </h1>
        <p style="font-size: 1.2rem; color: #666; margin-bottom: 0;">
            Conecta tus herramientas de marketing para obtener insights automáticos
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs para diferentes integraciones
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏪 E-commerce", "📱 Social Media", "📧 Email Marketing", "📊 Analytics", "📄 CSV Upload"
    ])
    
    with tab1:
        st.subheader("E-commerce Platforms")
        col1, col2 = st.columns(2)
        with col1:
            configure_shopify()
        with col2:
            configure_woocommerce()
    
    with tab2:
        st.subheader("Social Media Advertising")
        configure_meta()
    
    with tab3:
        st.subheader("Email Marketing Platforms")
        col1, col2, col3 = st.columns(3)
        with col1:
            configure_klaviyo()
        with col2:
            configure_mailchimp()
        with col3:
            configure_mailerlite()
    
    with tab4:
        st.subheader("Analytics Platforms")
        configure_ga4()
    
    with tab5:
        st.subheader("CSV Data Upload")
        configure_csv()

def configure_ga4():
    """Configuración de GA4"""
    manager = managers['integration_manager']
    
    st.markdown("### 📊 Google Analytics 4")
    
    if manager.is_configured('ga4'):
        st.success("✅ Google Analytics 4 está configurado")
        config = manager.get_config('ga4')
        st.info(f"Property ID: {config.get('property_id', 'No configurado')}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reconfigurar GA4", key="reconfig_ga4"):
                manager.remove_integration('ga4')
                st.rerun()
        
        with col2:
            if st.button("🧪 Probar Conexión GA4", key="test_ga4"):
                with st.spinner("Probando conexión..."):
                    test_result = manager.test_connection('ga4')
                    if test_result['success']:
                        st.success("✅ Conexión exitosa")
                        st.json(test_result['sample_data'])
                    else:
                        st.error(f"❌ Error: {test_result['error']}")
    else:
        st.info("ℹ️ Configura tu integración con Google Analytics 4")
        
        with st.form("ga4_config"):
            property_id = st.text_input(
                "Property ID",
                placeholder="123456789",
                help="Encuentra tu Property ID en GA4 > Admin > Property Settings"
            )
            
            credentials_json = st.text_area(
                "Service Account JSON",
                placeholder="Pega aquí el contenido de tu archivo de credenciales JSON",
                help="Crea una Service Account en Google Cloud Console"
            )
            
            submitted = st.form_submit_button("💾 Guardar Configuración")
            
            if submitted:
                if property_id and credentials_json:
                    try:
                        config = {
                            'property_id': property_id,
                            'credentials': json.loads(credentials_json)
                        }
                        
                        success = manager.add_integration('ga4', config)
                        
                        if success:
                            st.success("✅ GA4 configurado correctamente")
                            st.rerun()
                        else:
                            st.error("❌ Error al configurar GA4")
                    
                    except json.JSONDecodeError:
                        st.error("❌ JSON de credenciales inválido")
                else:
                    st.error("❌ Completa todos los campos")

def configure_meta():
    """Configuración de Meta Ads"""
    manager = managers['integration_manager']
    
    st.markdown("### 📘 Meta Ads (Facebook/Instagram)")
    
    if manager.is_configured('meta'):
        st.success("✅ Meta Ads está configurado")
        config = manager.get_config('meta')
        st.info(f"Ad Account ID: {config.get('ad_account_id', 'No configurado')}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reconfigurar Meta", key="reconfig_meta"):
                manager.remove_integration('meta')
                st.rerun()
        
        with col2:
            if st.button("🧪 Probar Conexión Meta", key="test_meta"):
                with st.spinner("Probando conexión..."):
                    test_result = manager.test_connection('meta')
                    if test_result['success']:
                        st.success("✅ Conexión exitosa")
                        st.json(test_result['sample_data'])
                    else:
                        st.error(f"❌ Error: {test_result['error']}")
    else:
        st.info("ℹ️ Configura tu integración con Meta Ads")
        
        with st.form("meta_config"):
            access_token = st.text_input(
                "Access Token",
                type="password",
                help="Genera un token de acceso en Meta for Developers"
            )
            
            ad_account_id = st.text_input(
                "Ad Account ID",
                placeholder="act_123456789",
                help="ID de tu cuenta publicitaria (incluye el prefijo 'act_')"
            )
            
            submitted = st.form_submit_button("💾 Guardar Configuración")
            
            if submitted:
                if access_token and ad_account_id:
                    config = {
                        'access_token': access_token,
                        'ad_account_id': ad_account_id
                    }
                    
                    success = manager.add_integration('meta', config)
                    
                    if success:
                        st.success("✅ Meta Ads configurado correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al configurar Meta Ads")
                else:
                    st.error("❌ Completa todos los campos")

def configure_shopify():
    """Configuración de Shopify"""
    manager = managers['integration_manager']
    
    st.markdown("### 🛍️ Shopify")
    
    if manager.is_configured('shopify'):
        st.success("✅ Shopify está configurado")
    else:
        with st.form("shopify_config"):
            shop_domain = st.text_input("Shop Domain", placeholder="tienda.myshopify.com")
            access_token = st.text_input("Access Token", type="password")
            
            submitted = st.form_submit_button("💾 Configurar Shopify")
            
            if submitted and shop_domain and access_token:
                config = {'shop_domain': shop_domain, 'access_token': access_token}
                if manager.add_integration('shopify', config):
                    st.success("✅ Shopify configurado")
                    st.rerun()

def configure_woocommerce():
    """Configuración de WooCommerce"""
    manager = managers['integration_manager']
    
    st.markdown("### 🛒 WooCommerce")
    
    if manager.is_configured('woocommerce'):
        st.success("✅ WooCommerce está configurado")
    else:
        with st.form("woo_config"):
            store_url = st.text_input("Store URL", placeholder="https://tusitio.com")
            consumer_key = st.text_input("Consumer Key")
            consumer_secret = st.text_input("Consumer Secret", type="password")
            
            submitted = st.form_submit_button("💾 Configurar WooCommerce")
            
            if submitted and store_url and consumer_key and consumer_secret:
                config = {
                    'store_url': store_url,
                    'consumer_key': consumer_key,
                    'consumer_secret': consumer_secret
                }
                if manager.add_integration('woocommerce', config):
                    st.success("✅ WooCommerce configurado")
                    st.rerun()

def configure_klaviyo():
    """Configuración de Klaviyo"""
    manager = managers['integration_manager']
    
    st.markdown("### 📧 Klaviyo")
    
    if manager.is_configured('klaviyo'):
        st.success("✅ Klaviyo configurado")
    else:
        with st.form("klaviyo_config"):
            api_key = st.text_input("API Key", type="password")
            submitted = st.form_submit_button("💾 Configurar")
            
            if submitted and api_key:
                if manager.add_integration('klaviyo', {'api_key': api_key}):
                    st.success("✅ Klaviyo configurado")
                    st.rerun()

def configure_mailchimp():
    """Configuración de Mailchimp"""
    manager = managers['integration_manager']
    
    st.markdown("### 🐵 Mailchimp")
    
    if manager.is_configured('mailchimp'):
        st.success("✅ Mailchimp configurado")
    else:
        with st.form("mailchimp_config"):
            api_key = st.text_input("API Key", type="password")
            server_prefix = st.text_input("Server Prefix", placeholder="us1")
            submitted = st.form_submit_button("💾 Configurar")
            
            if submitted and api_key and server_prefix:
                config = {'api_key': api_key, 'server_prefix': server_prefix}
                if manager.add_integration('mailchimp', config):
                    st.success("✅ Mailchimp configurado")
                    st.rerun()

def configure_mailerlite():
    """Configuración de MailerLite"""
    manager = managers['integration_manager']
    
    st.markdown("### 📮 MailerLite")
    
    if manager.is_configured('mailerlite'):
        st.success("✅ MailerLite configurado")
    else:
        with st.form("mailerlite_config"):
            api_key = st.text_input("API Key", type="password")
            submitted = st.form_submit_button("💾 Configurar")
            
            if submitted and api_key:
                if manager.add_integration('mailerlite', {'api_key': api_key}):
                    st.success("✅ MailerLite configurado")
                    st.rerun()

def configure_csv():
    """Configuración de CSV"""
    manager = managers['integration_manager']
    
    st.markdown("### 📄 CSV Upload")
    
    uploaded_file = st.file_uploader("Sube tu archivo CSV", type=['csv'])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("### Preview:")
        st.dataframe(df.head())
        
        with st.form("csv_mapping"):
            col1, col2 = st.columns(2)
            
            with col1:
                date_col = st.selectbox("Columna de fecha", df.columns)
                revenue_col = st.selectbox("Columna de ingresos", df.columns)
                quantity_col = st.selectbox("Columna de cantidad", df.columns)
            
            with col2:
                product_col = st.selectbox("Columna de producto", df.columns)
                category_col = st.selectbox("Columna de categoría", df.columns)
                customer_col = st.selectbox("Columna de cliente", df.columns)
            
            submitted = st.form_submit_button("💾 Guardar CSV")
            
            if submitted:
                config = {
                    'data': df.to_dict('records'),
                    'mapping': {
                        'date': date_col,
                        'revenue': revenue_col,
                        'quantity': quantity_col,
                        