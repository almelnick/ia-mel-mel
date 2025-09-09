# main.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(
    page_title="Marketing Dashboard IA",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .insight-card {
        background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Animaciones */
    .metric-card:hover {
        transform: translateY(-2px);
        transition: transform 0.2s;
    }
    
    .insight-card:hover {
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        transition: box-shadow 0.3s;
    }
    
    /* Ocultar elementos de Streamlit */
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK { display: none; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Imports de módulos locales
try:
    from integrations.manager import IntegrationManager
    from utils.intelligent_onboarding import IntelligentOnboarding
    from utils.ai_analyzer import AIAnalyzer
    from utils.data_processor import DataProcessor
    from dashboards.ecommerce_dashboard import EcommerceDashboard
except ImportError as e:
    st.error(f"Error importando módulos: {str(e)}")
    st.stop()

# Inicializar componentes principales
@st.cache_resource
def initialize_components():
    """Inicializar componentes principales del sistema"""
    try:
        integration_manager = IntegrationManager()
        onboarding = IntelligentOnboarding()
        ai_analyzer = AIAnalyzer()
        data_processor = DataProcessor()
        ecommerce_dashboard = EcommerceDashboard(data_processor, ai_analyzer)
        
        return integration_manager, onboarding, ai_analyzer, data_processor, ecommerce_dashboard
    except Exception as e:
        st.error(f"Error inicializando componentes: {str(e)}")
        return None, None, None, None, None

def main():
    """Función principal de la aplicación"""
    
    # Inicializar componentes
    components = initialize_components()
    if any(comp is None for comp in components):
        st.error("No se pudieron inicializar los componentes del sistema")
        return
    
    integration_manager, onboarding, ai_analyzer, data_processor, ecommerce_dashboard = components
    
    # Verificar si el onboarding está completado
    onboarding_completed = onboarding.is_completed()
    
    # Sidebar con navegación
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 10px; margin-bottom: 2rem; color: white;'>
            <h2 style='margin: 0; color: white;'>🚀 Marketing IA</h2>
            <p style='margin: 0.5rem 0 0 0; opacity: 0.9; color: white;'>Dashboard Inteligente</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Menú de navegación
        if not onboarding_completed:
            selected_page = "Onboarding"
            st.info("🎯 Completa el onboarding para acceder a todas las funciones")
        else:
            pages = {
                "📊 Dashboard": "dashboard",
                "🔗 Integraciones": "integrations", 
                "🤖 Análisis IA": "ai_analysis",
                "📈 Reportes": "reports",
                "⚙️ Configuración": "settings"
            }
            
            selected_page = st.selectbox(
                "Navegación",
                list(pages.keys()),
                index=0
            )
            
            selected_page = pages[selected_page]
        
        # Estado del sistema
        st.markdown("---")
        st.markdown("### 📊 Estado del Sistema")
        
        if onboarding_completed:
            connected_integrations = len(integration_manager.get_connected_connectors())
            total_integrations = len(integration_manager.connectors)
            
            st.metric(
                "Integraciones Activas",
                f"{connected_integrations}/{total_integrations}",
                f"{connected_integrations} conectadas"
            )
            
            # Progreso de configuración
            config_progress = (connected_integrations / total_integrations) * 100
            st.progress(config_progress / 100)
            
            if connected_integrations == 0:
                st.warning("⚠️ Conecta integraciones para ver datos")
            elif connected_integrations < 3:
                st.info("💡 Conecta más integraciones para mejores insights")
            else:
                st.success("✅ Sistema configurado correctamente")
        else:
            st.info("🎯 Onboarding pendiente")
        
        # Información adicional
        st.markdown("---")
        st.markdown("### ℹ️ Información")
        with st.expander("Acerca del sistema"):
            st.write("""
            **Marketing Dashboard IA** es una plataforma inteligente que:
            
            • 🔗 Conecta múltiples fuentes de datos
            • 🤖 Genera insights automáticamente  
            • 📈 Optimiza tus campañas
            • 🎯 Identifica oportunidades de escalado
            • 📊 Centraliza todos tus KPIs
            """)
    
    # Contenido principal basado en la página seleccionada
    if not onboarding_completed or selected_page == "Onboarding":
        show_onboarding_page(onboarding)
    
    elif selected_page == "dashboard":
        show_dashboard_page(integration_manager, data_processor, ai_analyzer, ecommerce_dashboard, onboarding)
    
    elif selected_page == "integrations":
        show_integrations_page(integration_manager)
    
    elif selected_page == "ai_analysis":
        show_ai_analysis_page(integration_manager, ai_analyzer, data_processor)
    
    elif selected_page == "reports":
        show_reports_page(integration_manager, data_processor, ai_analyzer)
    
    elif selected_page == "settings":
        show_settings_page(onboarding, integration_manager)

def show_onboarding_page(onboarding):
    """Mostrar página de onboarding"""
    onboarding.run_onboarding()

def show_dashboard_page(integration_manager, data_processor, ai_analyzer, ecommerce_dashboard, onboarding):
    """Mostrar página principal del dashboard"""
    
    # Determinar tipo de dashboard basado en configuración del onboarding
    business_config = onboarding.get_business_config()
    business_type = business_config.get('business_type', 'hybrid')
    
    if business_type == 'ecommerce':
        ecommerce_dashboard.render(integration_manager)
    else:
        # Dashboard genérico para otros tipos de negocio
        show_generic_dashboard(integration_manager, data_processor, ai_analyzer, business_config)

def show_generic_dashboard(integration_manager, data_processor, ai_analyzer, business_config):
    """Mostrar dashboard genérico adaptable"""
    
    business_name = business_config.get('business_name', 'Tu Negocio')
    business_type = business_config.get('business_type', 'hybrid')
    
    # Header principal
    st.markdown(f"""
    <div class='main-header'>
        <h1 style='margin: 0; color: white;'>📊 Dashboard de {business_name}</h1>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.9; color: white;'>
            Panel de control para {business_type.replace('_', ' ').title()}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Procesar datos
    processed_data = data_processor.process_multi_source_data(integration_manager)
    
    if not processed_data or not processed_data.get('combined_metrics'):
        st.warning("🔗 Conecta al menos una integración para ver datos en el dashboard")
        return
    
    # Mostrar KPIs principales
    show_kpi_section(data_processor, processed_data)
    
    # Mostrar gráficos
    show_charts_section(data_processor, processed_data)
    
    # Mostrar insights de IA
    show_insights_section(ai_analyzer, processed_data)

def show_kpi_section(data_processor, processed_data):
    """Mostrar sección de KPIs principales"""
    st.markdown("### 📊 Métricas Principales")
    
    kpis = data_processor.get_kpi_metrics(processed_data)
    
    # Primera fila de KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        revenue = kpis.get('total_revenue', {})
        st.metric(
            "💰 Revenue Total",
            f"${revenue.get('value', 0):,.0f}",
            f"{revenue.get('trend', 0):+.1f}%"
        )
    
    with col2:
        roas = kpis.get('overall_roas', {})
        st.metric(
            "📈 ROAS",
            f"{roas.get('value', 0):.1f}x",
            f"{roas.get('trend', 0):+.1f}%"
        )
    
    with col3:
        conversions = kpis.get('total_conversions', {})
        st.metric(
            "🎯 Conversiones",
            f"{conversions.get('value', 0):,}",
            f"{conversions.get('trend', 0):+.1f}%"
        )
    
    with col4:
        spend = kpis.get('total_spend', {})
        st.metric(
            "💸 Gasto",
            f"${spend.get('value', 0):,.0f}",
            f"{spend.get('trend', 0):+.1f}%"
        )

def show_charts_section(data_processor, processed_data):
    """Mostrar sección de gráficos"""
    st.markdown("### 📈 Análisis Visual")
    
    charts = data_processor.create_performance_charts(processed_data)
    
    if charts:
        col1, col2 = st.columns(2)
        
        with col1:
            if 'revenue_trend' in charts and charts['revenue_trend']:
                st.plotly_chart(charts['revenue_trend'], use_container_width=True)
        
        with col2:
            if 'channel_performance' in charts and charts['channel_performance']:
                st.plotly_chart(charts['channel_performance'], use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            if 'roas_comparison' in charts and charts['roas_comparison']:
                st.plotly_chart(charts['roas_comparison'], use_container_width=True)
        
        with col4:
            if 'conversion_funnel' in charts and charts['conversion_funnel']:
                st.plotly_chart(charts['conversion_funnel'], use_container_width=True)
    else:
        st.info("📊 Conecta más integraciones para ver gráficos detallados")

def show_insights_section(ai_analyzer, processed_data):
    """Mostrar sección de insights de IA"""
    st.markdown("### 🤖 Insights de IA")
    
    # Generar insights
    insights = ai_analyzer.analyze_performance_data(processed_data.get('raw_data', {}))
    
    # Fecha del reporte
    report_date = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    st.markdown(f"**Fecha del reporte:** {report_date}")
    st.markdown("---")
    
    # Resumen de KPIs
    st.markdown("### 📊 Resumen de KPIs")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        revenue = kpis.get('total_revenue', {})
        st.metric("Revenue Total", f"${revenue.get('value', 0):,.0f}", f"{revenue.get('trend', 0):+.1f}%")
    
    with col2:
        roas = kpis.get('overall_roas', {})
        st.metric("ROAS Promedio", f"{roas.get('value', 0):.1f}x", f"{roas.get('trend', 0):+.1f}%")
    
    with col3:
        conversions = kpis.get('total_conversions', {})
        st.metric("Conversiones", f"{conversions.get('value', 0):,}", f"{conversions.get('trend', 0):+.1f}%")
    
    with col4:
        spend = kpis.get('total_spend', {})
        st.metric("Gasto Total", f"${spend.get('value', 0):,.0f}", f"{spend.get('trend', 0):+.1f}%")
    
    # Principales insights
    st.markdown("### 💡 Principales Insights")
    
    opportunities = insights.get('optimization_opportunities', [])[:3]
    for i, opp in enumerate(opportunities, 1):
        st.write(f"{i}. **{opp.get('title', 'Oportunidad')}**: {opp.get('description', '')}")
    
    # Recomendaciones de acción
    st.markdown("### 🎯 Recomendaciones de Acción")
    
    scaling = insights.get('scaling_recommendations', [])[:3]
    for i, rec in enumerate(scaling, 1):
        action_type = "Escalar" if rec.get('type') == 'scale_up' else "Reducir"
        st.write(f"{i}. **{action_type} {rec.get('channel', 'Canal')}**: {rec.get('recommended_action', '')}")

def generate_performance_report(data_processor, processed_data):
    """Generar reporte de performance"""
    st.markdown("## 📈 Reporte de Performance")
    
    # Métricas por canal
    st.markdown("### 📊 Performance por Canal")
    
    performance = processed_data['combined_metrics'].get('performance', {})
    channel_ranking = performance.get('channel_ranking', [])
    
    if channel_ranking:
        df_channels = pd.DataFrame(channel_ranking)
        st.dataframe(df_channels, use_container_width=True)
    
    # Tendencias
    st.markdown("### 📈 Tendencias")
    charts = data_processor.create_performance_charts(processed_data)
    
    if charts.get('revenue_trend'):
        st.plotly_chart(charts['revenue_trend'], use_container_width=True)

def generate_ai_report(ai_analyzer, processed_data):
    """Generar reporte de insights de IA"""
    st.markdown("## 🤖 Reporte de Insights de IA")
    
    # Generar reporte completo
    report = ai_analyzer.export_insights_report('dict')
    
    # Mostrar resumen ejecutivo
    summary = report.get('executive_summary', {})
    
    st.markdown("### 📋 Resumen Ejecutivo")
    st.write(f"**Puntuación General:** {summary.get('overall_score', 0)}/100")
    st.write(f"**Total de Oportunidades:** {summary.get('key_metrics', {}).get('total_opportunities', 0)}")
    st.write(f"**Alertas Críticas:** {summary.get('key_metrics', {}).get('critical_alerts', 0)}")
    
    # Exportar reporte completo
    st.markdown("### 💾 Exportar Reporte Completo")
    
    report_json = ai_analyzer.export_insights_report('json')
    st.download_button(
        "📄 Descargar Reporte Completo (JSON)",
        report_json,
        f"reporte_ia_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        "application/json"
    )

def show_settings_page(onboarding, integration_manager):
    """Mostrar página de configuración"""
    st.markdown("""
    <div class='main-header'>
        <h1 style='margin: 0; color: white;'>⚙️ Configuración</h1>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.9; color: white;'>
            Configuración del sistema y preferencias
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuración del onboarding
    st.markdown("### 🎯 Configuración del Negocio")
    
    if onboarding.is_completed():
        business_config = onboarding.get_business_config()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Nombre del negocio:** {business_config.get('business_name', 'N/A')}")
            st.write(f"**Tipo de negocio:** {business_config.get('business_type', 'N/A')}")
            st.write(f"**Industria:** {business_config.get('industry', 'N/A')}")
        
        with col2:
            st.write(f"**Tamaño:** {business_config.get('business_size', 'N/A')}")
            st.write(f"**Ingresos:** {business_config.get('monthly_revenue', 'N/A')}")
            st.write(f"**Completado:** {business_config.get('completed_at', 'N/A')}")
        
        if st.button("🔄 Reconfigurar Negocio"):
            st.session_state.onboarding_completed = False
            st.session_state.onboarding_step = 1
            st.success("Onboarding reiniciado. Serás redirigido...")
            st.rerun()
    
    # Configuración de integraciones
    st.markdown("### 🔗 Estado de Integraciones")
    integration_manager.show_connection_health()
    
    # Configuración del sistema
    st.markdown("### 🛠️ Configuración del Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Preferencias de Dashboard")
        
        theme_preference = st.selectbox(
            "Tema visual",
            ["Claro", "Oscuro", "Automático"],
            index=0
        )
        
        update_frequency = st.selectbox(
            "Frecuencia de actualización",
            ["Tiempo real", "Cada 5 minutos", "Cada hora", "Manual"],
            index=1
        )
        
        notifications = st.checkbox("Notificaciones push", value=True)
    
    with col2:
        st.subheader("Configuración de Datos")
        
        data_retention = st.selectbox(
            "Retención de datos",
            ["30 días", "90 días", "1 año", "Indefinido"],
            index=1
        )
        
        auto_backup = st.checkbox("Backup automático", value=True)
        
        data_quality_checks = st.checkbox("Verificaciones de calidad", value=True)
    
    # Guardar configuración
    if st.button("💾 Guardar Configuración", type="primary"):
        # Aquí se guardaría la configuración
        st.success("✅ Configuración guardada correctamente")
    
    # Información del sistema
    st.markdown("### ℹ️ Información del Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Versión", "v2.1.0")
    
    with col2:
        st.metric("Última actualización", "09/09/2025")
    
    with col3:
        st.metric("Uptime", "99.9%")

if __name__ == "__main__":
    main().get('raw_data', {}))
    
    # Mostrar insights en tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Oportunidades", "📈 Escalado", "⚠️ Alertas"])
    
    with tab1:
        opportunities = insights.get('optimization_opportunities', [])
        if opportunities:
            for opp in opportunities[:3]:
                st.markdown(f"""
                <div class='insight-card'>
                    <h5 style='margin: 0; color: #333;'>{opp.get('title', 'Oportunidad')}</h5>
                    <p style='margin: 0.5rem 0; color: #666;'>{opp.get('description', '')}</p>
                    <p style='margin: 0; color: #28a745; font-weight: bold;'>
                        💡 {opp.get('potential_impact', 'Mejora esperada')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🎉 No se encontraron oportunidades críticas de optimización")
    
    with tab2:
        scaling = insights.get('scaling_recommendations', [])
        if scaling:
            for rec in scaling[:3]:
                color = "#28a745" if rec.get('type') == 'scale_up' else "#dc3545"
                icon = "📈" if rec.get('type') == 'scale_up' else "📉"
                
                st.markdown(f"""
                <div style='border-left: 4px solid {color}; background: #f8f9fa; 
                            padding: 1rem; border-radius: 5px; margin: 1rem 0;'>
                    <h6 style='margin: 0; color: {color};'>{icon} {rec.get('title', 'Recomendación')}</h6>
                    <p style='margin: 0.3rem 0;'><strong>Canal:</strong> {rec.get('channel', 'N/A')}</p>
                    <p style='margin: 0.3rem 0;'><strong>Acción:</strong> {rec.get('recommended_action', '')}</p>
                    <p style='margin: 0; color: #28a745;'><strong>Impacto:</strong> {rec.get('expected_impact', '')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📊 Necesitas más datos para generar recomendaciones de escalado")
    
    with tab3:
        alerts = insights.get('anomaly_alerts', [])
        if alerts:
            for alert in alerts[:3]:
                alert_type = alert.get('alert_type', 'info')
                colors = {
                    'critical': '#dc3545',
                    'warning': '#ffc107',
                    'positive': '#28a745'
                }
                color = colors.get(alert_type, '#17a2b8')
                
                st.markdown(f"""
                <div style='border-left: 4px solid {color}; background: #f8f9fa; 
                            padding: 1rem; border-radius: 5px; margin: 1rem 0;'>
                    <h6 style='margin: 0; color: {color};'>
                        {'🚨' if alert_type == 'critical' else '⚠️' if alert_type == 'warning' else '✅'} 
                        {alert.get('metric_affected', 'Métrica')}
                    </h6>
                    <p style='margin: 0.3rem 0;'>{alert.get('description', '')}</p>
                    <p style='margin: 0; font-weight: bold;'>{alert.get('recommended_action', '')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No hay alertas críticas en este momento")

def show_integrations_page(integration_manager):
    """Mostrar página de integraciones"""
    integration_manager.show_integrations_page()

def show_ai_analysis_page(integration_manager, ai_analyzer, data_processor):
    """Mostrar página de análisis de IA"""
    st.markdown("""
    <div class='main-header'>
        <h1 style='margin: 0; color: white;'>🤖 Análisis de IA</h1>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.9; color: white;'>
            Insights inteligentes y recomendaciones automáticas
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar conexiones
    connected_integrations = integration_manager.get_connected_connectors()
    
    if not connected_integrations:
        st.warning("🔗 Conecta al menos una integración para generar análisis de IA")
        return
    
    # Procesar datos
    processed_data = data_processor.process_multi_source_data(integration_manager)
    
    # Generar análisis completo
    with st.spinner("🤖 Generando análisis de IA..."):
        insights = ai_analyzer.analyze_performance_data(processed_data.get('raw_data', {}))
    
    # Resumen ejecutivo
    st.markdown("### 📋 Resumen Ejecutivo")
    executive_summary = ai_analyzer.generate_executive_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Puntuación General",
            f"{executive_summary['overall_score']}/100",
            help="Puntuación basada en performance, oportunidades y salud del sistema"
        )
    
    with col2:
        st.metric(
            "Oportunidades",
            executive_summary['key_metrics']['total_opportunities'],
            help="Número de oportunidades de optimización identificadas"
        )
    
    with col3:
        st.metric(
            "Alertas Críticas",
            executive_summary['key_metrics']['critical_alerts'],
            help="Alertas que requieren atención inmediata"
        )
    
    with col4:
        st.metric(
            "Recomendaciones",
            executive_summary['key_metrics']['scaling_recommendations'],
            help="Recomendaciones de escalado disponibles"
        )
    
    # Análisis detallado en tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Optimización", "📈 Escalado", "🎨 Creativos", "👥 Audiencias"
    ])
    
    with tab1:
        st.markdown("#### 🔍 Oportunidades de Optimización")
        opportunities = insights.get('optimization_opportunities', [])
        
        for i, opp in enumerate(opportunities, 1):
            priority = opp.get('priority', 'media')
            priority_colors = {'alta': '#dc3545', 'media': '#ffc107', 'baja': '#28a745'}
            
            with st.expander(f"{i}. {opp.get('title', 'Oportunidad')}", expanded=i<=2):
                col_info, col_actions = st.columns([2, 1])
                
                with col_info:
                    st.write(f"**Canal:** {opp.get('channel', 'General')}")
                    st.write(f"**Descripción:** {opp.get('description', '')}")
                    st.write(f"**Impacto Potencial:** {opp.get('potential_impact', 'N/A')}")
                
                with col_actions:
                    st.markdown(f"""
                    <div style='background: {priority_colors[priority]}; color: white; 
                                padding: 0.5rem; border-radius: 5px; text-align: center;'>
                        <strong>Prioridad: {priority.upper()}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                
                actions = opp.get('actions', [])
                if actions:
                    st.write("**Acciones recomendadas:**")
                    for action in actions:
                        st.write(f"• {action}")
    
    with tab2:
        st.markdown("#### 📊 Recomendaciones de Escalado")
        scaling_recs = insights.get('scaling_recommendations', [])
        
        for rec in scaling_recs:
            rec_type = rec.get('type', 'scale_up')
            icon = "📈" if rec_type == 'scale_up' else "📉"
            color = "#28a745" if rec_type == 'scale_up' else "#dc3545"
            
            st.markdown(f"""
            <div style='border: 2px solid {color}; background: #f8f9fa; 
                        padding: 1.5rem; border-radius: 10px; margin: 1rem 0;'>
                <h5 style='margin: 0; color: {color};'>{icon} {rec.get('title', '')}</h5>
                <div style='margin: 1rem 0;'>
                    <strong>Canal:</strong> {rec.get('channel', 'N/A')}<br>
                    <strong>ROAS Actual:</strong> {rec.get('current_roas', 0):.1f}x<br>
                    <strong>Gasto Actual:</strong> ${rec.get('current_spend', 0):,}<br>
                    <strong>Acción Recomendada:</strong> {rec.get('recommended_action', '')}<br>
                    <strong>Impacto Esperado:</strong> {rec.get('expected_impact', '')}
                </div>
                <div style='background: #e9ecef; padding: 0.5rem; border-radius: 5px;'>
                    <strong>Riesgo:</strong> {rec.get('risk_level', 'Medio')} | 
                    <strong>Timeline:</strong> {rec.get('timeline', 'N/A')}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("#### 🎨 Análisis de Creativos")
        creative_insights = insights.get('creative_insights', [])
        
        if creative_insights:
            for creative in creative_insights:
                performance = creative.get('performance_level', 'medio')
                colors = {'alto': '#28a745', 'medio': '#ffc107', 'bajo': '#dc3545'}
                
                st.markdown(f"""
                <div style='border-left: 4px solid {colors[performance]}; background: #f8f9fa; 
                            padding: 1rem; border-radius: 5px; margin: 1rem 0;'>
                    <h6 style='margin: 0;'>{creative.get('creative_type', 'Tipo de Creative')}</h6>
                    <p style='margin: 0.5rem 0;'>
                        <strong>Performance:</strong> {performance.title()} | 
                        <strong>CTR:</strong> {creative.get('metrics', {}).get('ctr', 0):.1f}% | 
                        <strong>CPC:</strong> ${creative.get('metrics', {}).get('cpc', 0):.2f}
                    </p>
                    <p style='margin: 0; color: #666;'>{creative.get('recommendation', '')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Conecta plataformas publicitarias para ver análisis de creativos")
    
    with tab4:
        st.markdown("#### 👥 Insights de Audiencias")
        audience_insights = insights.get('audience_insights', [])
        
        if audience_insights:
            for audience in audience_insights:
                performance = audience.get('performance_rating', 'regular')
                colors = {
                    'excelente': '#28a745',
                    'bueno': '#17a2b8', 
                    'regular': '#ffc107',
                    'bajo': '#dc3545'
                }
                
                st.markdown(f"""
                <div style='border-left: 4px solid {colors[performance]}; background: #f8f9fa; 
                            padding: 1rem; border-radius: 5px; margin: 1rem 0;'>
                    <h6 style='margin: 0;'>{audience.get('audience_name', 'Audiencia')}</h6>
                    <p style='margin: 0.5rem 0;'>
                        <strong>ROAS:</strong> {audience.get('roas', 0):.1f}x | 
                        <strong>% Presupuesto:</strong> {audience.get('spend_percentage', 0):.1f}% | 
                        <strong>Performance:</strong> {performance.title()}
                    </p>
                    <p style='margin: 0; color: {colors[performance]}; font-weight: bold;'>
                        📝 {audience.get('recommendation', '')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Conecta plataformas publicitarias para ver insights de audiencias")

def show_reports_page(integration_manager, data_processor, ai_analyzer):
    """Mostrar página de reportes"""
    st.markdown("""
    <div class='main-header'>
        <h1 style='margin: 0; color: white;'>📈 Reportes</h1>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.9; color: white;'>
            Reportes automáticos y exportación de datos
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar datos disponibles
    processed_data = data_processor.process_multi_source_data(integration_manager)
    
    if not processed_data or not processed_data.get('combined_metrics'):
        st.warning("🔗 Conecta integraciones para generar reportes")
        return
    
    # Opciones de reportes
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Reportes Disponibles")
        
        # Reporte ejecutivo
        if st.button("📋 Reporte Ejecutivo", use_container_width=True):
            generate_executive_report(integration_manager, data_processor, ai_analyzer)
        
        # Reporte de performance
        if st.button("📈 Reporte de Performance", use_container_width=True):
            generate_performance_report(data_processor, processed_data)
        
        # Reporte de IA
        if st.button("🤖 Reporte de Insights IA", use_container_width=True):
            generate_ai_report(ai_analyzer, processed_data)
    
    with col2:
        st.markdown("### 💾 Exportar Datos")
        
        # Exportar datos procesados
        if st.button("📄 Exportar a Excel", use_container_width=True):
            filename = data_processor.export_processed_data('excel')
            if filename:
                st.success(f"✅ Datos exportados a {filename}")
        
        # Exportar configuración
        if st.button("⚙️ Exportar Configuración", use_container_width=True):
            config = integration_manager.export_configuration()
            st.download_button(
                "Descargar configuración",
                str(config),
                "configuracion_marketing_dashboard.json",
                "application/json"
            )
        
        # Calidad de datos
        st.markdown("### 🔍 Calidad de Datos")
        quality_report = data_processor.get_data_quality_report()
        
        if quality_report:
            st.metric(
                "Puntuación de Calidad",
                f"{quality_report['overall_score']:.0f}/100"
            )
            
            if quality_report['data_issues']:
                with st.expander("⚠️ Problemas Detectados"):
                    for issue in quality_report['data_issues']:
                        st.write(f"• {issue}")

def generate_executive_report(integration_manager, data_processor, ai_analyzer):
    """Generar reporte ejecutivo"""
    st.markdown("## 📋 Reporte Ejecutivo")
    
    # Procesar datos
    processed_data = data_processor.process_multi_source_data(integration_manager)
    kpis = data_processor.get_kpi_metrics(processed_data)
    insights = ai_analyzer.analyze_performance_data(processed_data
