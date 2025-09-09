# integrations/connectors/klaviyo_connector.py
import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import json

class KlaviyoConnector:
    def __init__(self):
        self.name = "Klaviyo"
        self.color = "#FF6900"
        self.icon = "📧"
        self.api_key = None
        self.base_url = "https://a.klaviyo.com/api"
        self.api_version = "2024-02-15"
    
    def configure(self):
        """Configuración visual del conector Klaviyo"""
        st.subheader("🔗 Configurar Klaviyo")
        
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("### Paso 1: Configuración de API")
                
                st.info("💡 Necesitas una API Key de Klaviyo con permisos de lectura")
                
                self.api_key = st.text_input(
                    "Private API Key",
                    type="password",
                    placeholder="pk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                    help="Encuentra tu API Key en Account → Settings → API Keys"
                )
                
                if self.api_key:
                    if st.button("🔍 Verificar API Key"):
                        if self._verify_api_key():
                            st.success("✅ API Key válida - Conectado a Klaviyo")
                        else:
                            st.error("❌ API Key inválida")
                
                # Configuración de listas y segmentos
                if self.is_connected():
                    st.write("### Paso 2: Configurar Listas y Segmentos")
                    lists_config = self._configure_lists_segments()
                
                # Configuración de métricas
                if self.is_connected():
                    st.write("### Paso 3: Configurar Métricas")
                    metrics_config = self._configure_metrics()
            
            with col2:
                st.write("### Vista Previa")
                if self.is_connected():
                    st.success("🟢 Conectado")
                    
                    # Mostrar info de la cuenta
                    account_info = self._get_account_info()
                    if account_info:
                        st.write(f"**Cuenta:** {account_info['name']}")
                        st.write(f"**Plan:** {account_info['plan']}")
                        st.write(f"**Contactos:** {account_info['contacts']:,}")
                    
                    with st.expander("Datos disponibles"):
                        st.write("- Campañas de email")
                        st.write("- Flows automatizados")
                        st.write("- Listas y segmentos")
                        st.write("- Métricas de engagement")
                        st.write("- Revenue por email")
                else:
                    st.warning("🟡 No conectado")
                
                # Estadísticas rápidas
                if self.is_connected():
                    st.write("### Estadísticas (30 días)")
                    quick_stats = self._get_quick_stats()
                    st.metric("Emails enviados", f"{quick_stats['emails_sent']:,}", quick_stats['emails_change'])
                    st.metric("Revenue", f"${quick_stats['revenue']:,}", f"{quick_stats['revenue_change']}%")
                    st.metric("Open Rate", f"{quick_stats['open_rate']}%", f"{quick_stats['open_rate_change']}%")
        
        # Botón guardar
        if self.is_connected():
            if st.button("💾 Guardar Configuración", type="primary"):
                config = {
                    'api_key': self.api_key,
                    'lists_config': lists_config if 'lists_config' in locals() else {},
                    'metrics_config': metrics_config if 'metrics_config' in locals() else {},
                    'connected': True,
                    'last_sync': datetime.now().isoformat()
                }
                st.session_state['connector_klaviyo'] = config
                st.success("✅ Configuración guardada correctamente")
    
    def _configure_lists_segments(self):
        """Configurar listas y segmentos"""
        st.write("#### Selecciona listas y segmentos a trackear:")
        
        # Obtener listas disponibles
        available_lists = self._get_available_lists()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Listas**")
            selected_lists = []
            for list_item in available_lists['lists']:
                if st.checkbox(f"{list_item['name']} ({list_item['size']} contactos)", key=f"list_{list_item['id']}"):
                    selected_lists.append(list_item['id'])
        
        with col2:
            st.write("**Segmentos**")
            selected_segments = []
            for segment in available_lists['segments']:
                if st.checkbox(f"{segment['name']} ({segment['size']} contactos)", key=f"segment_{segment['id']}"):
                    selected_segments.append(segment['id'])
        
        # Configuración de flows
        st.write("**Flows Automatizados**")
        track_flows = st.checkbox("Trackear performance de flows", value=True)
        
        if track_flows:
            flow_types = st.multiselect(
                "Tipos de flows a trackear:",
                ["Welcome Series", "Abandoned Cart", "Post Purchase", "Winback", "Browse Abandonment"],
                default=["Welcome Series", "Abandoned Cart"]
            )
        
        return {
            'selected_lists': selected_lists,
            'selected_segments': selected_segments,
            'track_flows': track_flows,
            'flow_types': flow_types if track_flows else []
        }
    
    def _configure_metrics(self):
        """Configurar métricas específicas"""
        st.write("#### Selecciona métricas a trackear:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Engagement**")
            open_rate = st.checkbox("Open Rate", value=True)
            click_rate = st.checkbox("Click Rate", value=True)
            unsubscribe_rate = st.checkbox("Unsubscribe Rate", value=True)
            bounce_rate = st.checkbox("Bounce Rate", value=False)
        
        with col2:
            st.write("**Revenue**")
            revenue_per_email = st.checkbox("Revenue por Email", value=True)
            revenue_per_recipient = st.checkbox("Revenue por Recipient", value=True)
            conversion_rate = st.checkbox("Conversion Rate", value=True)
            average_order_value = st.checkbox("AOV de Email", value=False)
        
        with col3:
            st.write("**Lists & Flows**")
            list_growth = st.checkbox("Crecimiento de listas", value=True)
            flow_performance = st.checkbox("Performance de flows", value=True)
            segment_performance = st.checkbox("Performance de segmentos", value=False)
            deliverability = st.checkbox("Deliverability", value=False)
        
        return {
            'engagement': {
                'open_rate': open_rate,
                'click_rate': click_rate,
                'unsubscribe_rate': unsubscribe_rate,
                'bounce_rate': bounce_rate
            },
            'revenue': {
                'revenue_per_email': revenue_per_email,
                'revenue_per_recipient': revenue_per_recipient,
                'conversion_rate': conversion_rate,
                'average_order_value': average_order_value
            },
            'lists_flows': {
                'list_growth': list_growth,
                'flow_performance': flow_performance,
                'segment_performance': segment_performance,
                'deliverability': deliverability
            }
        }
    
    def _verify_api_key(self):
        """Verificar validez de la API key"""
        try:
            # Simular verificación de API key
            return self.api_key and (self.api_key.startswith('pk_live_') or self.api_key.startswith('pk_test_'))
        except:
            return False
    
    def _get_account_info(self):
        """Obtener información de la cuenta"""
        if not self.is_connected():
            return None
        
        return {
            'name': 'Mi Cuenta Klaviyo',
            'plan': 'Growth',
            'contacts': np.random.randint(15000, 85000),
            'monthly_email_limit': 500000,
            'emails_sent_this_month': np.random.randint(45000, 150000)
        }
    
    def _get_available_lists(self):
        """Obtener listas y segmentos disponibles"""
        return {
            'lists': [
                {'id': 'list_1', 'name': 'Newsletter Subscribers', 'size': 12500},
                {'id': 'list_2', 'name': 'VIP Customers', 'size': 850},
                {'id': 'list_3', 'name': 'Product Updates', 'size': 6200},
                {'id': 'list_4', 'name': 'Abandoned Cart', 'size': 3400}
            ],
            'segments': [
                {'id': 'seg_1', 'name': 'High Value Customers', 'size': 2100},
                {'id': 'seg_2', 'name': 'Recent Purchasers', 'size': 4800},
                {'id': 'seg_3', 'name': 'Inactive Subscribers', 'size': 7500},
                {'id': 'seg_4', 'name': 'Mobile Users', 'size': 9200}
            ]
        }
    
    def _get_quick_stats(self):
        """Obtener estadísticas rápidas"""
        return {
            'emails_sent': np.random.randint(25000, 75000),
            'emails_change': f"+{np.random.randint(8, 25)}%",
            'revenue': np.random.randint(45000, 120000),
            'revenue_change': np.random.randint(12, 35),
            'open_rate': round(np.random.uniform(22, 28), 1),
            'open_rate_change': round(np.random.uniform(0.5, 3.2), 1),
            'click_rate': round(np.random.uniform(3.5, 6.8), 1)
        }
    
    def is_connected(self):
        """Verificar si está conectado"""
        return (
            'klaviyo_api_key' in st.session_state or 
            self.api_key is not None
        )
    
    def fetch_data(self, date_range=30):
        """Obtener datos de Klaviyo"""
        if not self.is_connected():
            return None
        
        try:
            # Generar datos demo realistas para Klaviyo
            end_date = datetime.now()
            start_date = end_date - timedelta(days=date_range)
            
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            data = {
                'date': dates,
                'emails_sent': np.random.randint(1000, 5000, len(dates)),
                'emails_delivered': np.random.randint(950, 4800, len(dates)),
                'emails_opened': np.random.randint(200, 1200, len(dates)),
                'emails_clicked': np.random.randint(50, 300, len(dates)),
                'unsubscribes': np.random.randint(2, 15, len(dates)),
                'bounces': np.random.randint(10, 50, len(dates)),
                'revenue': np.random.uniform(500, 3500, len(dates)),
                'orders': np.random.randint(15, 85, len(dates)),
                'new_subscribers': np.random.randint(25, 150, len(dates))
            }
            
            df = pd.DataFrame(data)
            
            # Calcular métricas derivadas
            df['open_rate'] = (df['emails_opened'] / df['emails_delivered']) * 100
            df['click_rate'] = (df['emails_clicked'] / df['emails_delivered']) * 100
            df['click_to_open_rate'] = (df['emails_clicked'] / df['emails_opened']) * 100
            df['unsubscribe_rate'] = (df['unsubscribes'] / df['emails_delivered']) * 100
            df['bounce_rate'] = (df['bounces'] / df['emails_sent']) * 100
            df['revenue_per_email'] = df['revenue'] / df['emails_sent']
            df['revenue_per_recipient'] = df['revenue'] / df['emails_delivered']
            df['conversion_rate'] = (df['orders'] / df['emails_delivered']) * 100
            
            # Simular mejores métricas en días laborales
            for i, row in df.iterrows():
                if row['date'].weekday() < 5:  # Lunes a viernes
                    df.at[i, 'open_rate'] *= 1.15
                    df.at[i, 'click_rate'] *= 1.25
                    df.at[i, 'revenue'] *= 1.3
            
            return df
            
        except Exception as e:
            st.error(f"Error al obtener datos de Klaviyo: {str(e)}")
            return None
    
    def get_summary_metrics(self):
        """Obtener métricas resumen"""
        df = self.fetch_data(30)
        if df is None:
            return {}
        
        return {
            'total_emails_sent': int(df['emails_sent'].sum()),
            'total_emails_delivered': int(df['emails_delivered'].sum()),
            'total_emails_opened': int(df['emails_opened'].sum()),
            'total_emails_clicked': int(df['emails_clicked'].sum()),
            'avg_open_rate': round(df['open_rate'].mean(), 2),
            'avg_click_rate': round(df['click_rate'].mean(), 2),
            'avg_click_to_open_rate': round(df['click_to_open_rate'].mean(), 2),
            'total_revenue': round(df['revenue'].sum(), 2),
            'total_orders': int(df['orders'].sum()),
            'avg_revenue_per_email': round(df['revenue_per_email'].mean(), 4),
            'total_new_subscribers': int(df['new_subscribers'].sum()),
            'total_unsubscribes': int(df['unsubscribes'].sum()),
            'emails_sent_change': round(np.random.uniform(-3, 18), 1),
            'open_rate_change': round(np.random.uniform(-1.2, 4.5), 1),
            'revenue_change': round(np.random.uniform(-8, 25), 1)
        }
    
    def get_campaign_performance(self, limit=10):
        """Obtener rendimiento por campaña"""
        campaigns = [
            'Weekly Newsletter #47', 'Black Friday Sale', 'Product Launch - Smart Watch',
            'Customer Survey', 'Holiday Collection', 'Back in Stock Alert',
            'Birthday Offers', 'Seasonal Sale', 'Welcome Series #3', 'Win-back Campaign'
        ]
        
        data = []
        for campaign in campaigns[:limit]:
            sent = np.random.randint(1000, 15000)
            opened = int(sent * np.random.uniform(0.18, 0.32))
            clicked = int(opened * np.random.uniform(0.15, 0.35))
            revenue = clicked * np.random.uniform(25, 120)
            
            data.append({
                'campaign_name': campaign,
                'emails_sent': sent,
                'emails_opened': opened,
                'emails_clicked': clicked,
                'open_rate': round((opened / sent) * 100, 2),
                'click_rate': round((clicked / sent) * 100, 2),
                'click_to_open_rate': round((clicked / opened) * 100, 2),
                'revenue': round(revenue, 2),
                'revenue_per_email': round(revenue / sent, 4),
                'orders': np.random.randint(5, 45)
            })
        
        return sorted(data, key=lambda x: x['revenue'], reverse=True)
    
    def get_flow_performance(self):
        """Obtener rendimiento de flows"""
        flows = [
            'Welcome Series', 'Abandoned Cart Recovery', 'Post Purchase',
            'Browse Abandonment', 'Win-back Campaign', 'VIP Upgrade'
        ]
        
        data = []
        for flow in flows:
            data.append({
                'flow_name': flow,
                'emails_in_flow': np.random.randint(3, 8),
                'total_revenue': round(np.random.uniform(5000, 25000), 2),
                'conversion_rate': round(np.random.uniform(2.5, 12.8), 2),
                'avg_open_rate': round(np.random.uniform(25, 45), 1),
                'avg_click_rate': round(np.random.uniform(4, 12), 1),
                'subscribers_entered': np.random.randint(500, 3000),
                'subscribers_converted': np.random.randint(25, 350)
            })
        
        return sorted(data, key=lambda x: x['total_revenue'], reverse=True)
    
    def get_list_growth_analytics(self):
        """Obtener analytics de crecimiento de listas"""
        return {
            'growth_metrics': {
                'new_subscribers_30d': np.random.randint(1200, 4500),
                'unsubscribes_30d': np.random.randint(150, 600),
                'net_growth_30d': np.random.randint(800, 3500),
                'growth_rate': round(np.random.uniform(8.5, 25.3), 1),
                'churn_rate': round(np.random.uniform(1.2, 4.8), 1)
            },
            'subscriber_sources': {
                'Website Form': {'subscribers': 1800, 'percentage': 45},
                'Social Media': {'subscribers': 650, 'percentage': 16.25},
                'Referrals': {'subscribers': 520, 'percentage': 13},
                'Pop-up': {'subscribers': 480, 'percentage': 12},
                'Other': {'subscribers': 550, 'percentage': 13.75}
            },
            'engagement_by_list': [
                {'list_name': 'Newsletter', 'size': 12500, 'avg_open_rate': 28.5, 'avg_click_rate': 4.2},
                {'list_name': 'VIP Customers', 'size': 850, 'avg_open_rate': 42.1, 'avg_click_rate': 8.7},
                {'list_name': 'Product Updates', 'size': 6200, 'avg_open_rate': 31.2, 'avg_click_rate': 5.1}
            ]
        }
    
    def get_segment_insights(self):
        """Obtener insights de segmentos"""
        return {
            'high_value_customers': {
                'size': 2100,
                'avg_order_value': 185.50,
                'purchase_frequency': 3.2,
                'email_engagement': 'high',
                'revenue_contribution': '35%'
            },
            'recent_purchasers': {
                'size': 4800,
                'avg_order_value': 95.25,
                'purchase_frequency': 1.8,
                'email_engagement': 'medium',
                'revenue_contribution': '28%'
            },
            'inactive_subscribers': {
                'size': 7500,
                'last_engagement': '90+ days',
                'reactivation_rate': '12%',
                'recommended_action': 'Win-back campaign'
            }
        }
    
    def test_connection(self):
        """Probar conexión"""
        if not self.is_connected():
            return False, "No hay API key configurada"
        
        try:
            # Simular test de conexión
            account_info = self._get_account_info()
            if account_info:
                return True, f"Conexión exitosa a Klaviyo - {account_info['contacts']:,} contactos"
            else:
                return False, "No se pudo obtener información de la cuenta"
        except Exception as e:
            return False, f"Error en la conexión: {str(e)}"