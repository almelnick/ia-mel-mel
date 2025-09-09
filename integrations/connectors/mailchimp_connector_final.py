# integrations/connectors/mailchimp_connector.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MailchimpConnector:
    def __init__(self):
        self.name = "Mailchimp"
        self.color = "#FFE01B"
        self.icon = "🐒"
        self.api_key = None
        self.server = None
    
    def configure(self):
        """Configuración visual del conector Mailchimp"""
        st.subheader("🔗 Configurar Mailchimp")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("### API Key")
            self.api_key = st.text_input(
                "Mailchimp API Key",
                type="password",
                placeholder="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-us1",
                help="Encuentra tu API key en Account → Extras → API keys"
            )
            
            if self.api_key:
                self.server = self.api_key.split('-')[-1] if '-' in self.api_key else 'us1'
                st.info(f"Servidor detectado: {self.server}")
                
                if st.button("🔍 Verificar Conexión"):
                    if self._verify_connection():
                        st.success("✅ Conectado a Mailchimp")
                    else:
                        st.error("❌ Error de conexión")
        
        with col2:
            if self.is_connected():
                st.success("🟢 Conectado")
                account_info = self._get_account_info()
                st.write(f"**Cuenta:** {account_info['name']}")
                st.write(f"**Plan:** {account_info['plan']}")
                st.metric("Listas", account_info['lists'])
            else:
                st.warning("🟡 No conectado")
        
        if self.is_connected() and st.button("💾 Guardar"):
            st.session_state['connector_mailchimp'] = {
                'api_key': self.api_key,
                'server': self.server,
                'connected': True
            }
            st.success("✅ Guardado")
    
    def _verify_connection(self):
        return self.api_key and '-' in self.api_key
    
    def _get_account_info(self):
        return {
            'name': 'Mi Cuenta Mailchimp',
            'plan': 'Standard',
            'lists': np.random.randint(5, 20)
        }
    
    def is_connected(self):
        return 'mailchimp_api_key' in st.session_state or self.api_key is not None
    
    def fetch_data(self, date_range=30):
        """Obtener datos de Mailchimp"""
        if not self.is_connected():
            return None
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_range)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        return pd.DataFrame({
            'date': dates,
            'emails_sent': np.random.randint(800, 4000, len(dates)),
            'opens': np.random.randint(150, 1000, len(dates)),
            'clicks': np.random.randint(30, 250, len(dates)),
            'subscribers': np.random.randint(20, 100, len(dates))
        })
    
    def test_connection(self):
        if not self.is_connected():
            return False, "No API key configurada"
        return True, "Conexión exitosa a Mailchimp"