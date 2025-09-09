# integrations/connectors/shopify_connector.py
import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import json

class ShopifyConnector:
    def __init__(self):
        self.name = "Shopify"
        self.color = "#96BF47"
        self.icon = "🛍️"
        self.shop_url = None
        self.access_token = None
        self.api_version = "2023-10"
    
    def configure(self):
        """Configuración visual del conector Shopify"""
        st.subheader("🔗 Configurar Shopify")
        
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("### Paso 1: Información de la Tienda")
                
                self.shop_url = st.text_input(
                    "URL de la tienda",
                    placeholder="mi-tienda.myshopify.com",
                    help="URL de tu tienda Shopify (sin https://)"
                )
                
                st.write("### Paso 2: Autenticación")
                
                auth_method = st.radio(
                    "Método de autenticación",
                    ["Private App Token", "OAuth App", "Admin API Key"]
                )
                
                if auth_method == "Private App Token":
                    st.info("💡 Recomendado: Más seguro y fácil de configurar")
                    
                    private_token = st.text_input(
                        "Private App Access Token",
                        type="password",
                        placeholder="shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                        help="Crea una Private App en tu admin de Shopify"
                    )
                    
                    if private_token:
                        self.access_token = private_token
                        if st.button("🔍 Verificar Token"):
                            if self._verify_token():
                                st.success("✅ Token válido - Conectado a Shopify")
                            else:
                                st.error("❌ Token inválido")
                
                elif auth_method == "OAuth App":
                    api_key = st.text_input("API Key", placeholder="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                    api_secret = st.text_input("API Secret", type="password")
                    
                    if api_key and api_secret:
                        if st.button("🔐 Iniciar OAuth", type="primary"):
                            oauth_url = self._generate_oauth_url(api_key)
                            st.markdown(f"[👉 Autorizar Acceso a Shopify]({oauth_url})")
                        
                        oauth_code = st.text_input("Código de autorización", type="password")
                        if oauth_code:
                            if self._handle_oauth_callback(oauth_code, api_key, api_secret):
                                st.success("✅ Conectado exitosamente")
                
                elif auth_method == "Admin API Key":
                    st.warning("⚠️ Método legacy - No recomendado para nuevas integraciones")
                    api_key = st.text_input("Admin API Key", type="password")
                    password = st.text_input("Password", type="password")
                    
                    if api_key and password:
                        self._setup_admin_api(api_key, password)
                
                # Configuración de datos
                if self.is_connected():
                    st.write("### Paso 3: Configurar Datos")
                    data_config = self._configure_data_sync()
            
            with col2:
                st.write("### Vista Previa")
                if self.is_connected():
                    st.success("🟢 Conectado")
                    
                    # Mostrar info de la tienda
                    shop_info = self._get_shop_info()
                    if shop_info:
                        st.write(f"**Tienda:** {shop_info['name']}")
                        st.write(f"**Plan:** {shop_info['plan']}")
                        st.write(f"**Moneda:** {shop_info['currency']}")
                    
                    with st.expander("Datos disponibles"):
                        st.write("- Pedidos y ventas")
                        st.write("- Productos e inventario")
                        st.write("- Clientes")
                        st.write("- Tráfico de la tienda")
                        st.write("- Métricas financieras")
                else:
                    st.warning("🟡 No conectado")
                
                # Estadísticas rápidas
                if self.is_connected():
                    st.write("### Estadísticas (30 días)")
                    quick_stats = self._get_quick_stats()
                    st.metric("Pedidos", quick_stats['orders'], quick_stats['orders_change'])
                    st.metric("Ventas", f"${quick_stats['sales']:,}", f"{quick_stats['sales_change']}%")
        
        # Botón guardar
        if self.is_connected():
            if st.button("💾 Guardar Configuración", type="primary"):
                config = {
                    'shop_url': self.shop_url,
                    'access_token': self.access_token,
                    'auth_method': auth_method,
                    'api_version': self.api_version,
                    'connected': True,
                    'last_sync': datetime.now().isoformat()
                }
                st.session_state['connector_shopify'] = config
                st.success("✅ Configuración guardada correctamente")
    
    def _configure_data_sync(self):
        """Configurar sincronización de datos"""
        st.write("#### Selecciona qué datos sincronizar:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Ventas y Pedidos**")
            orders = st.checkbox("Pedidos", value=True)
            sales_data = st.checkbox("Datos de ventas", value=True)
            refunds = st.checkbox("Reembolsos", value=True)
            abandoned_carts = st.checkbox("Carritos abandonados", value=False)
        
        with col2:
            st.write("**Productos**")
            products = st.checkbox("Catálogo de productos", value=True)
            inventory = st.checkbox("Inventario", value=False)
            variants = st.checkbox("Variantes", value=False)
            collections = st.checkbox("Colecciones", value=False)
        
        with col3:
            st.write("**Clientes y Marketing**")
            customers = st.checkbox("Datos de clientes", value=True)
            customer_segments = st.checkbox("Segmentos de clientes", value=False)
            discounts = st.checkbox("Descuentos", value=False)
            marketing_events = st.checkbox("Eventos de marketing", value=False)
        
        # Configuración de frecuencia
        st.write("#### Frecuencia de sincronización:")
        sync_frequency = st.selectbox(
            "¿Qué tan seguido sincronizar?",
            ["Tiempo real", "Cada hora", "Cada 6 horas", "Diario", "Manual"]
        )
        
        # Rango de datos históricos
        historical_range = st.slider(
            "Días de datos históricos a importar:",
            min_value=30,
            max_value=365,
            value=90
        )
        
        return {
            'sales_orders': {
                'orders': orders,
                'sales_data': sales_data,
                'refunds': refunds,
                'abandoned_carts': abandoned_carts
            },
            'products': {
                'products': products,
                'inventory': inventory,
                'variants': variants,
                'collections': collections
            },
            'customers_marketing': {
                'customers': customers,
                'customer_segments': customer_segments,
                'discounts': discounts,
                'marketing_events': marketing_events
            },
            'sync_frequency': sync_frequency,
            'historical_range': historical_range
        }
    
    def _generate_oauth_url(self, api_key):
        """Generar URL de OAuth para Shopify"""
        shop_domain = self.shop_url.replace('.myshopify.com', '') if self.shop_url else 'demo-shop'
        scopes = "read_orders,read_products,read_customers,read_analytics"
        redirect_uri = st.secrets.get('SHOPIFY_REDIRECT_URI', 'http://localhost:8501')
        
        return f"https://{shop_domain}.myshopify.com/admin/oauth/authorize?client_id={api_key}&scope={scopes}&redirect_uri={redirect_uri}&response_type=code"
    
    def _handle_oauth_callback(self, code, api_key, api_secret):
        """Manejar callback de OAuth"""
        try:
            # Simular intercambio de código por token
            self.access_token = f"shpat_demo_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            st.session_state['shopify_access_token'] = self.access_token
            return True
        except Exception as e:
            st.error(f"Error en OAuth: {str(e)}")
            return False
    
    def _setup_admin_api(self, api_key, password):
        """Configurar Admin API (legacy)"""
        try:
            st.session_state['shopify_api_key'] = api_key
            st.session_state['shopify_password'] = password
            st.success("Admin API configurado correctamente")
        except Exception as e:
            st.error(f"Error al configurar Admin API: {str(e)}")
    
    def _verify_token(self):
        """Verificar validez del token"""
        try:
            # Simular verificación de token
            return self.access_token and self.access_token.startswith('shpat_')
        except:
            return False
    
    def _get_shop_info(self):
        """Obtener información de la tienda"""
        if not self.is_connected():
            return None
        
        return {
            'name': 'Mi Tienda Demo',
            'plan': 'Shopify Plus',
            'currency': 'USD',
            'domain': self.shop_url or 'mi-tienda.myshopify.com',
            'country': 'US',
            'timezone': 'America/New_York'
        }
    
    def _get_quick_stats(self):
        """Obtener estadísticas rápidas"""
        return {
            'orders': np.random.randint(150, 500),
            'orders_change': f"+{np.random.randint(5, 25)}%",
            'sales': np.random.randint(15000, 45000),
            'sales_change': np.random.randint(8, 28),
            'customers': np.random.randint(1200, 3500),
            'products': np.random.randint(50, 300)
        }
    
    def is_connected(self):
        """Verificar si está conectado"""
        return (
            'shopify_access_token' in st.session_state or 
            'shopify_api_key' in st.session_state or
            self.access_token is not None
        )
    
    def fetch_data(self, date_range=30):
        """Obtener datos de Shopify"""
        if not self.is_connected():
            return None
        
        try:
            # Generar datos demo realistas para Shopify
            end_date = datetime.now()
            start_date = end_date - timedelta(days=date_range)
            
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            data = {
                'date': dates,
                'orders': np.random.randint(10, 45, len(dates)),
                'sales': np.random.uniform(800, 3500, len(dates)),
                'units_sold': np.random.randint(25, 120, len(dates)),
                'average_order_value': np.random.uniform(45, 120, len(dates)),
                'new_customers': np.random.randint(5, 25, len(dates)),
                'returning_customers': np.random.randint(8, 35, len(dates)),
                'refunds': np.random.uniform(50, 300, len(dates)),
                'shipping_revenue': np.random.uniform(80, 250, len(dates)),
                'tax_collected': np.random.uniform(60, 280, len(dates))
            }
            
            df = pd.DataFrame(data)
            
            # Calcular métricas derivadas
            df['total_customers'] = df['new_customers'] + df['returning_customers']
            df['conversion_rate'] = np.random.uniform(2.1, 5.8, len(dates))
            df['refund_rate'] = (df['refunds'] / df['sales']) * 100
            df['net_sales'] = df['sales'] - df['refunds']
            
            # Simular patrones de fin de semana (más ventas)
            for i, row in df.iterrows():
                if row['date'].weekday() >= 5:  # Sábado y domingo
                    df.at[i, 'orders'] *= 1.3
                    df.at[i, 'sales'] *= 1.25
                    df.at[i, 'units_sold'] *= 1.2
            
            return df
            
        except Exception as e:
            st.error(f"Error al obtener datos de Shopify: {str(e)}")
            return None
    
    def get_summary_metrics(self):
        """Obtener métricas resumen"""
        df = self.fetch_data(30)
        if df is None:
            return {}
        
        return {
            'total_orders': int(df['orders'].sum()),
            'total_sales': round(df['sales'].sum(), 2),
            'total_units_sold': int(df['units_sold'].sum()),
            'avg_order_value': round(df['average_order_value'].mean(), 2),
            'total_customers': int(df['total_customers'].sum()),
            'new_customers': int(df['new_customers'].sum()),
            'returning_customers': int(df['returning_customers'].sum()),
            'total_refunds': round(df['refunds'].sum(), 2),
            'avg_conversion_rate': round(df['conversion_rate'].mean(), 2),
            'net_sales': round(df['net_sales'].sum(), 2),
            'sales_change': round(np.random.uniform(-5, 18), 1),
            'orders_change': round(np.random.uniform(-3, 22), 1),
            'aov_change': round(np.random.uniform(-8, 15), 1)
        }
    
    def get_top_products(self, limit=10):
        """Obtener productos más vendidos"""
        products = [
            'Premium T-Shirt', 'Wireless Headphones', 'Eco Water Bottle',
            'Smart Watch', 'Organic Coffee Beans', 'Yoga Mat Pro',
            'LED Desk Lamp', 'Bluetooth Speaker', 'Canvas Tote Bag',
            'Protein Powder', 'Running Shoes', 'Skincare Set'
        ]
        
        data = []
        for product in products[:limit]:
            units_sold = np.random.randint(50, 500)
            price = np.random.uniform(25, 150)
            revenue = units_sold * price
            
            data.append({
                'product_name': product,
                'units_sold': units_sold,
                'revenue': round(revenue, 2),
                'price': round(price, 2),
                'profit_margin': round(np.random.uniform(25, 65), 1),
                'inventory_level': np.random.randint(10, 200),
                'conversion_rate': round(np.random.uniform(2.1, 8.5), 2)
            })
        
        return sorted(data, key=lambda x: x['revenue'], reverse=True)
    
    def get_customer_analytics(self):
        """Obtener analytics de clientes"""
        return {
            'customer_segments': {
                'new_customers': {'count': 850, 'percentage': 35, 'avg_order_value': 75},
                'returning_customers': {'count': 1200, 'percentage': 50, 'avg_order_value': 95},
                'vip_customers': {'count': 360, 'percentage': 15, 'avg_order_value': 180}
            },
            'geographic_distribution': {
                'United States': {'percentage': 65, 'sales': 28500},
                'Canada': {'percentage': 15, 'sales': 6800},
                'United Kingdom': {'percentage': 8, 'sales': 3200},
                'Australia': {'percentage': 7, 'sales': 2900},
                'Others': {'percentage': 5, 'sales': 2100}
            },
            'customer_lifetime_value': {
                'average_clv': 245.50,
                'median_clv': 180.25,
                'top_10_percent_clv': 850.75
            }
        }
    
    def get_abandoned_carts(self):
        """Obtener carritos abandonados"""
        return {
            'total_abandoned_carts': np.random.randint(150, 400),
            'abandoned_cart_value': round(np.random.uniform(8500, 15000), 2),
            'recovery_rate': round(np.random.uniform(12, 28), 1),
            'average_time_to_abandon': '14 minutos',
            'top_abandonment_reasons': [
                {'reason': 'Gastos de envío altos', 'percentage': 35},
                {'reason': 'Solo navegando', 'percentage': 28},
                {'reason': 'Proceso de checkout largo', 'percentage': 18},
                {'reason': 'Falta de métodos de pago', 'percentage': 12},
                {'reason': 'Otros', 'percentage': 7}
            ]
        }
    
    def test_connection(self):
        """Probar conexión"""
        if not self.is_connected():
            return False, "No hay token de acceso configurado"
        
        try:
            # Simular test de conexión
            shop_info = self._get_shop_info()
            if shop_info:
                return True, f"Conexión exitosa a {shop_info['name']}"
            else:
                return False, "No se pudo obtener información de la tienda"
        except Exception as e:
            return False, f"Error en la conexión: {str(e)}"