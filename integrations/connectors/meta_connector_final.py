# integrations/connectors/meta_connector.py
import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import json

class MetaConnector:
    def __init__(self):
        self.name = "Meta Ads (Facebook/Instagram)"
        self.color = "#1877F2"
        self.icon = "📘"
        self.access_token = None
        self.ad_account_id = None
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def configure(self):
        """Configuración visual del conector Meta Ads"""
        st.subheader("🔗 Configurar Meta Ads")
        
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("### Paso 1: Configuración Básica")
                
                # App ID y Secret
                app_id = st.text_input(
                    "App ID",
                    placeholder="123456789012345",
                    help="Encuentra tu App ID en developers.facebook.com"
                )
                
                app_secret = st.text_input(
                    "App Secret",
                    type="password",
                    placeholder="abc123def456...",
                    help="App Secret de tu aplicación de Facebook"
                )
                
                # Ad Account ID
                self.ad_account_id = st.text_input(
                    "Ad Account ID",
                    placeholder="act_123456789",
                    help="ID de tu cuenta publicitaria (formato: act_123456789)"
                )
                
                st.write("### Paso 2: Autenticación")
                
                auth_method = st.radio(
                    "Método de autenticación",
                    ["Access Token", "OAuth Flow", "Business Manager"]
                )
                
                if auth_method == "Access Token":
                    access_token = st.text_input(
                        "Access Token",
                        type="password",
                        placeholder="EAAxxxxxxxxxxxxx",
                        help="Token de acceso de larga duración"
                    )
                    
                    if access_token:
                        self.access_token = access_token
                        if st.button("🔍 Verificar Token"):
                            if self._verify_token():
                                st.success("✅ Token válido")
                            else:
                                st.error("❌ Token inválido")
                
                elif auth_method == "OAuth Flow":
                    if st.button("🔐 Iniciar OAuth con Meta", type="primary"):
                        oauth_url = self._generate_oauth_url(app_id)
                        st.markdown(f"[👉 Autorizar Acceso a Meta Ads]({oauth_url})")
                        st.info("Después de autorizar, copia el código aquí:")
                    
                    oauth_code = st.text_input("Código de autorización", type="password")
                    if oauth_code and app_id and app_secret:
                        if self._handle_oauth_callback(oauth_code, app_id, app_secret):
                            st.success("✅ Conectado exitosamente")
                
                elif auth_method == "Business Manager":
                    business_id = st.text_input("Business Manager ID", placeholder="123456789012345")
                    system_user_token = st.text_input("System User Token", type="password")
                    
                    if business_id and system_user_token:
                        self._setup_business_manager(business_id, system_user_token)
                
                # Configuración de campañas
                if self.is_connected():
                    st.write("### Paso 3: Configurar Campañas")
                    campaigns_config = self._configure_campaigns()
            
            with col2:
                st.write("### Vista Previa")
                if self.is_connected():
                    st.success("🟢 Conectado")
                    with st.expander("Datos disponibles"):
                        st.write("- Impresiones y alcance")
                        st.write("- Clics y CTR")
                        st.write("- Gasto y CPC")
                        st.write("- Conversiones y ROAS")
                        st.write("- Datos demográficos")
                else:
                    st.warning("🟡 No conectado")
                
                # Mostrar cuentas disponibles
                if self.is_connected():
                    st.write("### Cuentas Disponibles")
                    accounts = self._get_ad_accounts()
                    for account in accounts:
                        st.write(f"- {account['name']} ({account['id']})")
        
        # Botón guardar
        if self.is_connected():
            if st.button("💾 Guardar Configuración", type="primary"):
                config = {
                    'app_id': app_id,
                    'ad_account_id': self.ad_account_id,
                    'access_token': self.access_token,
                    'auth_method': auth_method,
                    'connected': True,
                    'last_sync': datetime.now().isoformat()
                }
                st.session_state['connector_meta'] = config
                st.success("✅ Configuración guardada correctamente")
    
    def _configure_campaigns(self):
        """Configurar campañas específicas"""
        st.write("#### Selecciona qué datos trackear:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Métricas Básicas**")
            impressions = st.checkbox("Impresiones", value=True)
            reach = st.checkbox("Alcance", value=True)
            clicks = st.checkbox("Clics", value=True)
            ctr = st.checkbox("CTR", value=True)
        
        with col2:
            st.write("**Métricas de Costo**")
            spend = st.checkbox("Gasto", value=True)
            cpc = st.checkbox("CPC", value=True)
            cpm = st.checkbox("CPM", value=True)
            frequency = st.checkbox("Frecuencia", value=False)
        
        with col3:
            st.write("**Conversiones**")
            conversions = st.checkbox("Conversiones", value=True)
            conversion_rate = st.checkbox("Tasa de conversión", value=True)
            roas = st.checkbox("ROAS", value=True)
            purchase_value = st.checkbox("Valor de compra", value=False)
        
        # Filtros de campaña
        st.write("#### Filtros de Campaña")
        campaign_status = st.multiselect(
            "Estado de campañas",
            ["ACTIVE", "PAUSED", "ARCHIVED"],
            default=["ACTIVE"]
        )
        
        objective_filter = st.multiselect(
            "Objetivos de campaña",
            ["CONVERSIONS", "TRAFFIC", "AWARENESS", "REACH", "ENGAGEMENT", "MESSAGES"],
            default=["CONVERSIONS", "TRAFFIC"]
        )
        
        return {
            'basic_metrics': {
                'impressions': impressions,
                'reach': reach,
                'clicks': clicks,
                'ctr': ctr
            },
            'cost_metrics': {
                'spend': spend,
                'cpc': cpc,
                'cpm': cpm,
                'frequency': frequency
            },
            'conversion_metrics': {
                'conversions': conversions,
                'conversion_rate': conversion_rate,
                'roas': roas,
                'purchase_value': purchase_value
            },
            'filters': {
                'campaign_status': campaign_status,
                'objectives': objective_filter
            }
        }
    
    def _generate_oauth_url(self, app_id):
        """Generar URL de OAuth para Meta"""
        base_url = "https://www.facebook.com/v18.0/dialog/oauth"
        redirect_uri = st.secrets.get('META_REDIRECT_URI', 'http://localhost:8501')
        scope = "ads_read,read_insights,business_management"
        
        return f"{base_url}?client_id={app_id}&redirect_uri={redirect_uri}&scope={scope}&response_type=code"
    
    def _handle_oauth_callback(self, code, app_id, app_secret):
        """Manejar callback de OAuth"""
        try:
            # Simular intercambio de código por token
            self.access_token = f"demo_token_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            st.session_state['meta_access_token'] = self.access_token
            return True
        except Exception as e:
            st.error(f"Error en OAuth: {str(e)}")
            return False
    
    def _setup_business_manager(self, business_id, system_user_token):
        """Configurar Business Manager"""
        try:
            st.session_state['meta_business_id'] = business_id
            st.session_state['meta_system_token'] = system_user_token
            self.access_token = system_user_token
            st.success("Business Manager configurado correctamente")
        except Exception as e:
            st.error(f"Error al configurar Business Manager: {str(e)}")
    
    def _verify_token(self):
        """Verificar validez del token"""
        try:
            # Simular verificación de token
            return len(self.access_token) > 20 if self.access_token else False
        except:
            return False
    
    def _get_ad_accounts(self):
        """Obtener cuentas publicitarias"""
        return [
            {'id': 'act_123456789', 'name': 'Cuenta Principal'},
            {'id': 'act_987654321', 'name': 'Cuenta Secundaria'},
        ]
    
    def is_connected(self):
        """Verificar si está conectado"""
        return (
            'meta_access_token' in st.session_state or 
            'meta_system_token' in st.session_state or
            self.access_token is not None
        )
    
    def fetch_data(self, date_range=30):
        """Obtener datos de Meta Ads"""
        if not self.is_connected():
            return None
        
        try:
            # Generar datos demo realistas para Meta Ads
            end_date = datetime.now()
            start_date = end_date - timedelta(days=date_range)
            
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            data = {
                'date': dates,
                'impressions': np.random.randint(10000, 50000, len(dates)),
                'reach': np.random.randint(8000, 35000, len(dates)),
                'clicks': np.random.randint(200, 1200, len(dates)),
                'spend': np.random.uniform(50, 300, len(dates)),
                'cpc': np.random.uniform(0.8, 3.5, len(dates)),
                'cpm': np.random.uniform(8, 25, len(dates)),
                'ctr': np.random.uniform(1.2, 4.8, len(dates)),
                'conversions': np.random.randint(5, 35, len(dates)),
                'conversion_value': np.random.uniform(200, 1500, len(dates)),
                'frequency': np.random.uniform(1.1, 2.8, len(dates))
            }
            
            df = pd.DataFrame(data)
            
            # Calcular métricas derivadas
            df['conversion_rate'] = (df['conversions'] / df['clicks']) * 100
            df['roas'] = df['conversion_value'] / df['spend']
            df['cost_per_conversion'] = df['spend'] / df['conversions']
            
            # Agregar tendencias (mejor performance en weekdays)
            for i, row in df.iterrows():
                if row['date'].weekday() < 5:  # Lunes a viernes
                    df.at[i, 'conversions'] *= 1.2
                    df.at[i, 'conversion_value'] *= 1.15
            
            return df
            
        except Exception as e:
            st.error(f"Error al obtener datos de Meta Ads: {str(e)}")
            return None
    
    def get_summary_metrics(self):
        """Obtener métricas resumen"""
        df = self.fetch_data(30)
        if df is None:
            return {}
        
        return {
            'total_impressions': int(df['impressions'].sum()),
            'total_reach': int(df['reach'].sum()),
            'total_clicks': int(df['clicks'].sum()),
            'total_spend': round(df['spend'].sum(), 2),
            'avg_cpc': round(df['cpc'].mean(), 2),
            'avg_cpm': round(df['cpm'].mean(), 2),
            'avg_ctr': round(df['ctr'].mean(), 2),
            'total_conversions': int(df['conversions'].sum()),
            'total_conversion_value': round(df['conversion_value'].sum(), 2),
            'avg_roas': round(df['roas'].mean(), 2),
            'spend_change': round(np.random.uniform(-10, 15), 1),
            'conversions_change': round(np.random.uniform(-5, 20), 1),
            'roas_change': round(np.random.uniform(-8, 12), 1)
        }
    
    def get_campaign_performance(self, limit=10):
        """Obtener rendimiento por campaña"""
        campaigns = [
            'Campaña Awareness - Q4', 'Retargeting - Cart Abandoners', 
            'Lookalike Audiences', 'Interest Targeting - Premium',
            'Video Campaign - Brand', 'Conversions - Holiday Sale',
            'Traffic Campaign - Blog', 'Lead Generation - Newsletter'
        ]
        
        data = []
        for campaign in campaigns[:limit]:
            spend = np.random.uniform(100, 2000)
            conversions = np.random.randint(10, 150)
            conversion_value = conversions * np.random.uniform(15, 80)
            
            data.append({
                'campaign_name': campaign,
                'impressions': np.random.randint(5000, 80000),
                'clicks': np.random.randint(100, 2000),
                'spend': round(spend, 2),
                'conversions': conversions,
                'conversion_value': round(conversion_value, 2),
                'roas': round(conversion_value / spend, 2),
                'ctr': round(np.random.uniform(1.0, 5.0), 2),
                'cpc': round(np.random.uniform(0.5, 4.0), 2)
            })
        
        return sorted(data, key=lambda x: x['roas'], reverse=True)
    
    def get_audience_insights(self):
        """Obtener insights de audiencia"""
        return {
            'age_groups': {
                '18-24': {'percentage': 15, 'performance': 'high'},
                '25-34': {'percentage': 35, 'performance': 'very_high'},
                '35-44': {'percentage': 28, 'performance': 'medium'},
                '45-54': {'percentage': 15, 'performance': 'low'},
                '55+': {'percentage': 7, 'performance': 'medium'}
            },
            'gender': {
                'female': {'percentage': 58, 'performance': 'high'},
                'male': {'percentage': 42, 'performance': 'medium'}
            },
            'devices': {
                'mobile': {'percentage': 78, 'performance': 'high'},
                'desktop': {'percentage': 18, 'performance': 'medium'},
                'tablet': {'percentage': 4, 'performance': 'low'}
            },
            'top_interests': [
                {'interest': 'E-commerce', 'reach': 2500000, 'performance': 'high'},
                {'interest': 'Technology', 'reach': 1800000, 'performance': 'medium'},
                {'interest': 'Fashion', 'reach': 1200000, 'performance': 'high'},
                {'interest': 'Food & Beverage', 'reach': 950000, 'performance': 'medium'}
            ]
        }
    
    def test_connection(self):
        """Probar conexión"""
        if not self.is_connected():
            return False, "No hay token de acceso configurado"
        
        try:
            # Simular test de conexión
            test_data = self.fetch_data(7)
            if test_data is not None and not test_data.empty:
                return True, "Conexión exitosa a Meta Ads"
            else:
                return False, "No se pudieron obtener datos"
        except Exception as e:
            return False, f"Error en la conexión: {str(e)}"
                '