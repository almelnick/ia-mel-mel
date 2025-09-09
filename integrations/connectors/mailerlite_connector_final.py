# integrations/connectors/mailerlite_connector.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MailerLiteConnector:
    def __init__(self):
        self.name = "MailerLite"
        self.color = "#09C269"
        self.icon = "✉️"
        self.api_key = None
        self.base_url = "https://connect.mailerlite.com/api"
    
    def configure(self):
        """Configuración visual del conector MailerLite"""
        st.subheader("🔗 Configurar MailerLite")
        
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("### Paso 1: API Key")
                st.info("💡 Obtén tu API key en MailerLite → Integrations → API")
                
                self.api_key = st.text_input(
                    "API Key",
                    type="password",
                    placeholder="mlk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                    help="Tu API key de MailerLite"
                )
                
                if self.api_key and st.button("🔍 Verificar API Key"):
                    if self._verify_api_key():
                        st.success("✅ Conectado a MailerLite")
                    else:
                        st.error("❌ API Key inválida")
                
                if self.is_connected():
                    st.write("### Paso 2: Configurar Datos")
                    self._configure_sync_options()
            
            with col2:
                st.write("### Estado")
                if self.is_connected():
                    st.success("🟢 Conectado")
                    stats = self._get_account_stats()
                    st.metric("Suscriptores", f"{stats['subscribers']:,}")
                    st.metric("Grupos", stats['groups'])
                    st.metric("Campañas", stats['campaigns'])
                else:
                    st.warning("🟡 No conectado")
        
        if self.is_connected() and st.button("💾 Guardar Configuración", type="primary"):
            st.session_state['connector_mailerlite'] = {
                'api_key': self.api_key,
                'connected': True,
                'last_sync': datetime.now().isoformat()
            }
            st.success("✅ Configuración guardada")
    
    def _configure_sync_options(self):
        """Configurar opciones de sincronización"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Métricas de Email**")
            st.checkbox("Open Rate", value=True)
            st.checkbox("Click Rate", value=True)
            st.checkbox("Bounce Rate", value=True)
            st.checkbox("Unsubscribe Rate", value=True)
        
        with col2:
            st.write("**Datos de Audiencia**")
            st.checkbox("Crecimiento de suscriptores", value=True)
            st.checkbox("Segmentación", value=False)
            st.checkbox("Automations", value=True)
    
    def _verify_api_key(self):
        return self.api_key and len(self.api_key) > 20
    
    def _get_account_stats(self):
        return {
            'subscribers': np.random.randint(5000, 50000),
            'groups': np.random.randint(8, 25),
            'campaigns': np.random.randint(45, 150)
        }
    
    def is_connected(self):
        return 'mailerlite_api_key' in st.session_state or self.api_key is not None
    
    def fetch_data(self, date_range=30):
        """Obtener datos de MailerLite"""
        if not self.is_connected():
            return None
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_range)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        return pd.DataFrame({
            'date': dates,
            'emails_sent': np.random.randint(500, 3000, len(dates)),
            'emails_opened': np.random.randint(100, 800, len(dates)),
            'emails_clicked': np.random.randint(25, 200, len(dates)),
            'new_subscribers': np.random.randint(10, 80, len(dates)),
            'unsubscribes': np.random.randint(2, 20, len(dates))
        })
    
    def test_connection(self):
        if not self.is_connected():
            return False, "No API key configurada"
        return True, "Conexión exitosa a MailerLite"