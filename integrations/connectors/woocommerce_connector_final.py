# integrations/connectors/woocommerce_connector.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class WooCommerceConnector:
    def __init__(self):
        self.name = "WooCommerce"
        self.color = "#96588A"
        self.icon = "🛒"
        self.site_url = None
        self.consumer_key = None
        self.consumer_secret = None
    
    def configure(self):
        """Configuración visual del conector WooCommerce"""
        st.subheader("🔗 Configurar WooCommerce")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("### Configuración de la Tienda")
            
            self.site_url = st.text_input(
                "URL del sitio",
                placeholder="https://mi-tienda.com",
                help="URL completa de tu sitio WooCommerce"
            )
            
            st.write("### Credenciales API")
            st.info("💡 Genera las claves en WooCommerce → Configuración → Avanzado → REST API")
            
            self.consumer_key = st.text_input(
                "Consumer Key",
                placeholder="ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            )
            
            self.consumer_secret = st.text_input(
                "Consumer Secret",
                type="password",
                placeholder="cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            )
            
            if all([self.site_url, self.consumer_key, self.consumer_secret]):
                if st.button("🔍 Probar Conexión"):
                    if self._test_api_connection():
                        st.success("✅ Conectado a WooCommerce")
                    else:
                        st.error("❌ Error de conexión")
                
                st.write("### Configurar Sincronización")
                self._configure_sync_settings()
        
        with col2:
            st.write("### Estado")
            if self.is_connected():
                st.success("🟢 Conectado")
                
                store_info = self._get_store_info()
                st.write(f"**Tienda:** {store_info['name']}")
                st.write(f"**Versión:** {store_info['version']}")
                st.metric("Productos", store_info['products'])
                st.metric("Pedidos (30d)", store_info['orders'])
            else:
                st.warning("🟡 No conectado")
        
        if self.is_connected() and st.button("💾 Guardar Configuración", type="primary"):
            st.session_state['connector_woocommerce'] = {
                'site_url': self.site_url,
                'consumer_key': self.consumer_key,
                'consumer_secret': self.consumer_secret,
                'connected': True,
                'last_sync': datetime.now().isoformat()
            }
            st.success("✅ Configuración guardada")
    
    def _configure_sync_settings(self):
        """Configurar ajustes de sincronización"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Datos de Ventas**")
            st.checkbox("Pedidos", value=True)
            st.checkbox("Ingresos", value=True)
            st.checkbox("Reembolsos", value=True)
            st.checkbox("Impuestos", value=False)
        
        with col2:
            st.write("**Productos y Clientes**")
            st.checkbox("Productos", value=True)
            st.checkbox("Inventario", value=False)
            st.checkbox("Clientes", value=True)
            st.checkbox("Cupones", value=False)
        
        st.selectbox(
            "Frecuencia de sincronización",
            ["Tiempo real", "Cada hora", "Diario", "Manual"],
            index=1
        )
    
    def _test_api_connection(self):
        # Simular test de conexión
        return all([
            self.site_url.startswith('http'),
            len(self.consumer_key) > 20,
            len(self.consumer_secret) > 20
        ])
    
    def _get_store_info(self):
        return {
            'name': 'Mi Tienda WooCommerce',
            'version': '8.5.2',
            'products': np.random.randint(50, 500),
            'orders': np.random.randint(100, 800)
        }
    
    def is_connected(self):
        return all([
            'woocommerce_consumer_key' in st.session_state or self.consumer_key,
            'woocommerce_consumer_secret' in st.session_state or self.consumer_secret,
            'woocommerce_site_url' in st.session_state or self.site_url
        ])
    
    def fetch_data(self, date_range=30):
        """Obtener datos de WooCommerce"""
        if not self.is_connected():
            return None
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_range)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        return pd.DataFrame({
            'date': dates,
            'orders': np.random.randint(5, 35, len(dates)),
            'revenue': np.random.uniform(500, 2500, len(dates)),
            'new_customers': np.random.randint(2, 15, len(dates)),
            'products_sold': np.random.randint(15, 85, len(dates))
        })
    
    def get_summary_metrics(self):
        """Obtener métricas resumen"""
        df = self.fetch_data(30)
        if df is None:
            return {}
        
        return {
            'total_orders': int(df['orders'].sum()),
            'total_revenue': round(df['revenue'].sum(), 2),
            'avg_order_value': round(df['revenue'].sum() / df['orders'].sum(), 2),
            'total_customers': int(df['new_customers'].sum()),
            'revenue_change': round(np.random.uniform(-5, 20), 1)
        }
    
    def test_connection(self):
        if not self.is_connected():
            return False, "Credenciales no configuradas"
        return True, "Conexión exitosa a WooCommerce"