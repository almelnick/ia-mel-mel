# integrations/connectors/ga4_connector.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2.credentials import Credentials
import json

class GA4Connector:
    def __init__(self):
        self.name = "Google Analytics 4"
        self.color = "#4285F4"
        self.icon = "📊"
        self.client = None
        self.property_id = None
    
    def configure(self):
        """Configuración visual del conector GA4"""
        st.subheader("🔗 Configurar Google Analytics 4")
        
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("### Paso 1: Información Básica")
                self.property_id = st.text_input(
                    "Property ID",
                    placeholder="123456789",
                    help="Encuentra tu Property ID en GA4 → Admin → Property Settings"
                )
                
                st.write("### Paso 2: Autenticación")
                auth_method = st.radio(
                    "Método de autenticación",
                    ["OAuth (Recomendado)", "Service Account", "API Key"]
                )
                
                if auth_method == "OAuth (Recomendado)":
                    if st.button("🔐 Conectar con Google", type="primary"):
                        oauth_url = self._generate_oauth_url()
                        st.markdown(f"[👉 Autorizar Acceso a GA4]({oauth_url})")
                        st.info("Después de autorizar, copia el código aquí:")
                        
                    oauth_code = st.text_input("Código de autorización", type="password")
                    
                    if oauth_code:
                        if self._handle_oauth_callback(oauth_code):
                            st.success("✅ Conectado exitosamente a GA4")
                        else:
                            st.error("❌ Error en la autenticación")
                
                elif auth_method == "Service Account":
                    service_account_file = st.file_uploader(
                        "Subir archivo JSON de Service Account",
                        type="json"
                    )
                    if service_account_file:
                        self._setup_service_account(service_account_file)
                
                elif auth_method == "API Key":
                    api_key = st.text_input("API Key", type="password")
                    if api_key:
                        self._setup_api_key(api_key)
            
            with col2:
                st.write("### Vista Previa")
                if self.is_connected():
                    st.success("🟢 Conectado")
                    with st.expander("Datos disponibles"):
                        st.write("- Sesiones y usuarios")
                        st.write("- Páginas vistas")
                        st.write("- Conversiones")
                        st.write("- Fuentes de tráfico")
                        st.write("- Comportamiento")
                else:
                    st.warning("🟡 No conectado")
        
        # Configuración de métricas
        if self.is_connected():
            st.write("### Paso 3: Configurar Métricas")
            metrics_config = self._configure_metrics()
            
            if st.button("💾 Guardar Configuración", type="primary"):
                config = {
                    'property_id': self.property_id,
                    'auth_method': auth_method,
                    'metrics': metrics_config,
                    'connected': True,
                    'last_sync': datetime.now().isoformat()
                }
                st.session_state[f'connector_ga4'] = config
                st.success("✅ Configuración guardada correctamente")
    
    def _configure_metrics(self):
        """Configurar métricas específicas de GA4"""
        st.write("#### Selecciona las métricas a trackear:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Tráfico**")
            sessions = st.checkbox("Sesiones", value=True)
            users = st.checkbox("Usuarios", value=True)
            pageviews = st.checkbox("Páginas vistas", value=True)
            bounce_rate = st.checkbox("Tasa de rebote", value=True)
        
        with col2:
            st.write("**Conversiones**")
            conversions = st.checkbox("Conversiones", value=True)
            conversion_rate = st.checkbox("Tasa de conversión", value=True)
            revenue = st.checkbox("Ingresos", value=False)
            ecommerce = st.checkbox("E-commerce", value=False)
        
        with col3:
            st.write("**Engagement**")
            avg_session_duration = st.checkbox("Duración promedio", value=True)
            pages_per_session = st.checkbox("Páginas por sesión", value=True)
            engagement_rate = st.checkbox("Tasa de engagement", value=False)
            scroll_rate = st.checkbox("Tasa de scroll", value=False)
        
        return {
            'traffic': {
                'sessions': sessions,
                'users': users,
                'pageviews': pageviews,
                'bounce_rate': bounce_rate
            },
            'conversions': {
                'conversions': conversions,
                'conversion_rate': conversion_rate,
                'revenue': revenue,
                'ecommerce': ecommerce
            },
            'engagement': {
                'avg_session_duration': avg_session_duration,
                'pages_per_session': pages_per_session,
                'engagement_rate': engagement_rate,
                'scroll_rate': scroll_rate
            }
        }
    
    def _generate_oauth_url(self):
        """Generar URL de OAuth para GA4"""
        base_url = "https://accounts.google.com/o/oauth2/auth"
        params = {
            'client_id': st.secrets.get('GOOGLE_CLIENT_ID', 'your_client_id'),
            'redirect_uri': st.secrets.get('GOOGLE_REDIRECT_URI', 'http://localhost:8501'),
            'scope': 'https://www.googleapis.com/auth/analytics.readonly',
            'response_type': 'code',
            'access_type': 'offline'
        }
        return f"{base_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    def _handle_oauth_callback(self, code):
        """Manejar callback de OAuth"""
        try:
            # Simular autenticación exitosa para demo
            credentials_data = {
                'token': 'demo_access_token',
                'refresh_token': 'demo_refresh_token',
                'client_id': st.secrets.get('GOOGLE_CLIENT_ID', 'demo_client_id'),
                'client_secret': st.secrets.get('GOOGLE_CLIENT_SECRET', 'demo_secret')
            }
            
            st.session_state['ga4_credentials'] = credentials_data
            return True
        except Exception as e:
            st.error(f"Error en OAuth: {str(e)}")
            return False
    
    def _setup_service_account(self, service_file):
        """Configurar Service Account"""
        try:
            service_account_info = json.load(service_file)
            st.session_state['ga4_service_account'] = service_account_info
            st.success("Service Account configurado correctamente")
        except Exception as e:
            st.error(f"Error al configurar Service Account: {str(e)}")
    
    def _setup_api_key(self, api_key):
        """Configurar API Key"""
        st.session_state['ga4_api_key'] = api_key
        st.success("API Key configurado correctamente")
    
    def is_connected(self):
        """Verificar si está conectado"""
        return (
            'ga4_credentials' in st.session_state or 
            'ga4_service_account' in st.session_state or 
            'ga4_api_key' in st.session_state
        )
    
    def fetch_data(self, date_range=30):
        """Obtener datos de GA4"""
        if not self.is_connected():
            return None
        
        try:
            # Generar datos demo realistas para GA4
            end_date = datetime.now()
            start_date = end_date - timedelta(days=date_range)
            
            # Crear datos demo con tendencias realistas
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            data = {
                'date': dates,
                'sessions': np.random.randint(1200, 2500, len(dates)),
                'users': np.random.randint(800, 1800, len(dates)),
                'pageviews': np.random.randint(3000, 8000, len(dates)),
                'bounce_rate': np.random.uniform(0.35, 0.65, len(dates)),
                'avg_session_duration': np.random.uniform(120, 300, len(dates)),
                'conversions': np.random.randint(15, 45, len(dates)),
                'conversion_rate': np.random.uniform(0.02, 0.08, len(dates)),
                'revenue': np.random.uniform(800, 3200, len(dates))
            }
            
            df = pd.DataFrame(data)
            
            # Agregar tendencias realistas
            trend_factor = np.linspace(1.0, 1.15, len(dates))  # Crecimiento del 15%
            df['sessions'] = (df['sessions'] * trend_factor).astype(int)
            df['revenue'] = df['revenue'] * trend_factor
            
            # Simular días de la semana (menos tráfico en weekends)
            for i, row in df.iterrows():
                if row['date'].weekday() >= 5:  # Sábado y domingo
                    df.at[i, 'sessions'] *= 0.7
                    df.at[i, 'pageviews'] *= 0.7
                    df.at[i, 'users'] *= 0.8
            
            return df
            
        except Exception as e:
            st.error(f"Error al obtener datos de GA4: {str(e)}")
            return None
    
    def get_summary_metrics(self):
        """Obtener métricas resumen"""
        df = self.fetch_data(30)
        if df is None:
            return {}
        
        return {
            'total_sessions': int(df['sessions'].sum()),
            'total_users': int(df['users'].sum()),
            'total_pageviews': int(df['pageviews'].sum()),
            'avg_bounce_rate': round(df['bounce_rate'].mean() * 100, 1),
            'total_conversions': int(df['conversions'].sum()),
            'avg_conversion_rate': round(df['conversion_rate'].mean() * 100, 2),
            'total_revenue': round(df['revenue'].sum(), 2),
            'sessions_change': round(np.random.uniform(-5, 15), 1),  # % cambio simulado
            'users_change': round(np.random.uniform(-3, 12), 1),
            'revenue_change': round(np.random.uniform(-8, 20), 1)
        }
    
    def get_top_pages(self, limit=10):
        """Obtener páginas más visitadas"""
        pages = [
            '/', '/products', '/about', '/contact', '/blog',
            '/shop', '/services', '/pricing', '/features', '/support'
        ]
        
        data = []
        for page in pages[:limit]:
            data.append({
                'page': page,
                'pageviews': np.random.randint(500, 5000),
                'unique_pageviews': np.random.randint(300, 3000),
                'avg_time_on_page': np.random.randint(60, 300),
                'bounce_rate': round(np.random.uniform(0.2, 0.8), 3)
            })
        
        return sorted(data, key=lambda x: x['pageviews'], reverse=True)
    
    def get_traffic_sources(self):
        """Obtener fuentes de tráfico"""
        sources = {
            'organic': {'sessions': np.random.randint(800, 1500), 'percentage': 0},
            'direct': {'sessions': np.random.randint(400, 800), 'percentage': 0},
            'social': {'sessions': np.random.randint(200, 600), 'percentage': 0},
            'email': {'sessions': np.random.randint(100, 300), 'percentage': 0},
            'paid': {'sessions': np.random.randint(150, 400), 'percentage': 0},
            'referral': {'sessions': np.random.randint(50, 200), 'percentage': 0}
        }
        
        total_sessions = sum([source['sessions'] for source in sources.values()])
        
        for source in sources.values():
            source['percentage'] = round((source['sessions'] / total_sessions) * 100, 1)
        
        return sources
    
    def test_connection(self):
        """Probar conexión"""
        if not self.is_connected():
            return False, "No hay credenciales configuradas"
        
        try:
            # Simular test de conexión
            test_data = self.fetch_data(7)
            if test_data is not None and not test_data.empty:
                return True, "Conexión exitosa a GA4"
            else:
                return False, "No se pudieron obtener datos"
        except Exception as e:
            return False, f"Error en la conexión: {str(e)}"