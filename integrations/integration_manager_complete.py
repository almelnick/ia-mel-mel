# integrations/manager.py
import streamlit as st
from integrations.connectors.ga4_connector import GA4Connector
from integrations.connectors.meta_connector import MetaConnector
from integrations.connectors.shopify_connector import ShopifyConnector
from integrations.connectors.woocommerce_connector import WooCommerceConnector
from integrations.connectors.klaviyo_connector import KlaviyoConnector
from integrations.connectors.mailerlite_connector import MailerLiteConnector
from integrations.connectors.mailchimp_connector import MailchimpConnector
from integrations.connectors.csv_connector import CSVConnector

class IntegrationManager:
    def __init__(self):
        self.connectors = {
            'ga4': GA4Connector(),
            'meta': MetaConnector(),
            'shopify': ShopifyConnector(),
            'woocommerce': WooCommerceConnector(),
            'klaviyo': KlaviyoConnector(),
            'mailerlite': MailerLiteConnector(),
            'mailchimp': MailchimpConnector(),
            'csv': CSVConnector()
        }
        
        self.connector_info = {
            'ga4': {
                'name': 'Google Analytics 4',
                'description': 'Datos de tráfico web y comportamiento de usuarios',
                'category': 'analytics',
                'priority': 'high'
            },
            'meta': {
                'name': 'Meta Ads (Facebook/Instagram)',
                'description': 'Campañas publicitarias en Facebook e Instagram',
                'category': 'advertising',
                'priority': 'high'
            },
            'shopify': {
                'name': 'Shopify',
                'description': 'Datos de ventas, productos y clientes',
                'category': 'ecommerce',
                'priority': 'high'
            },
            'woocommerce': {
                'name': 'WooCommerce',
                'description': 'Tienda WordPress con datos de ventas',
                'category': 'ecommerce',
                'priority': 'high'
            },
            'klaviyo': {
                'name': 'Klaviyo',
                'description': 'Email marketing avanzado y automatización',
                'category': 'email',
                'priority': 'medium'
            },
            'mailerlite': {
                'name': 'MailerLite',
                'description': 'Email marketing simple y efectivo',
                'category': 'email',
                'priority': 'low'
            },
            'mailchimp': {
                'name': 'Mailchimp',
                'description': 'Email marketing y automatización',
                'category': 'email',
                'priority': 'medium'
            },
            'csv': {
                'name': 'CSV Upload',
                'description': 'Subir datos personalizados desde archivos CSV',
                'category': 'data',
                'priority': 'low'
            }
        }
    
    def show_integrations_page(self):
        """Mostrar página principal de integraciones"""
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='background: linear-gradient(45deg, #667eea 0%, #764ba2 100%); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       font-size: 2.5rem; margin-bottom: 0.5rem;'>
                🔗 Integraciones
            </h1>
            <p style='color: #666; font-size: 1.1rem;'>
                Conecta tus herramientas de marketing para obtener insights inteligentes
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar resumen de conexiones
        self._show_connection_summary()
        
        # Mostrar integraciones por categoría
        self._show_integrations_by_category()
    
    def _show_connection_summary(self):
        """Mostrar resumen de conexiones activas"""
        st.markdown("### 📊 Estado de Conexiones")
        
        total_connectors = len(self.connectors)
        connected_count = sum(1 for connector in self.connectors.values() if connector.is_connected())
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Integraciones",
                total_connectors,
                help="Número total de conectores disponibles"
            )
        
        with col2:
            st.metric(
                "Conectadas",
                connected_count,
                f"+{connected_count}" if connected_count > 0 else None,
                help="Integraciones activas y funcionando"
            )
        
        with col3:
            connection_rate = (connected_count / total_connectors) * 100 if total_connectors > 0 else 0
            st.metric(
                "Tasa de Conexión",
                f"{connection_rate:.0f}%",
                help="Porcentaje de integraciones conectadas"
            )
        
        with col4:
            pending = total_connectors - connected_count
            st.metric(
                "Pendientes",
                pending,
                f"-{pending}" if pending > 0 else None,
                help="Integraciones disponibles para conectar"
            )
        
        # Barra de progreso visual
        progress = connected_count / total_connectors if total_connectors > 0 else 0
        st.progress(progress)
        
        if connected_count == 0:
            st.warning("💡 **Conecta al menos 2-3 integraciones** para obtener insights completos de tu marketing")
        elif connected_count < 3:
            st.info("🚀 **¡Buen comienzo!** Conecta más integraciones para obtener una vista 360° de tu performance")
        else:
            st.success("🎉 **¡Excelente!** Tienes suficientes integraciones para análisis completos")
    
    def _show_integrations_by_category(self):
        """Mostrar integraciones organizadas por categoría"""
        categories = {
            'analytics': {'name': '📊 Analytics', 'description': 'Datos de tráfico y comportamiento'},
            'advertising': {'name': '📢 Publicidad', 'description': 'Campañas y performance publicitaria'},
            'ecommerce': {'name': '🛍️ E-commerce', 'description': 'Ventas, productos y clientes'},
            'email': {'name': '📧 Email Marketing', 'description': 'Campañas de email y automatización'},
            'data': {'name': '📄 Datos Personalizados', 'description': 'Importar datos desde archivos'}
        }
        
        # Agrupar conectores por categoría
        connectors_by_category = {}
        for connector_key, info in self.connector_info.items():
            category = info['category']
            if category not in connectors_by_category:
                connectors_by_category[category] = []
            connectors_by_category[category].append(connector_key)
        
        # Mostrar cada categoría
        for category_key, category_info in categories.items():
            if category_key in connectors_by_category:
                st.markdown(f"### {category_info['name']}")
                st.write(category_info['description'])
                
                # Mostrar conectores de esta categoría en columnas
                category_connectors = connectors_by_category[category_key]
                cols = st.columns(min(3, len(category_connectors)))
                
                for i, connector_key in enumerate(category_connectors):
                    with cols[i % len(cols)]:
                        self._show_connector_card(connector_key)
                
                st.markdown("---")
    
    def _show_connector_card(self, connector_key):
        """Mostrar tarjeta individual de conector"""
        connector = self.connectors[connector_key]
        info = self.connector_info[connector_key]
        is_connected = connector.is_connected()
        
        # Determinar colores y estado
        if is_connected:
            status_color = "#28a745"
            status_text = "🟢 Conectado"
            button_text = "⚙️ Configurar"
            button_type = "secondary"
        else:
            status_color = "#6c757d"
            status_text = "⚪ No conectado"
            button_text = "🔗 Conectar"
            button_type = "primary"
        
        # Prioridad visual
        priority_colors = {
            'high': '#dc3545',
            'medium': '#ffc107',
            'low': '#28a745'
        }
        priority_color = priority_colors.get(info['priority'], '#6c757d')
        
        # Tarjeta del conector
        st.markdown(f"""
        <div style='border: 2px solid {status_color}; border-radius: 15px; padding: 1.5rem; 
                    margin: 1rem 0; background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
                <h4 style='margin: 0; color: #333;'>{connector.icon} {info['name']}</h4>
                <span style='background: {priority_color}; color: white; padding: 0.2rem 0.5rem; 
                            border-radius: 10px; font-size: 0.8rem; font-weight: bold;'>
                    {info['priority'].upper()}
                </span>
            </div>
            <p style='color: #666; margin: 0.5rem 0; font-size: 0.9rem;'>{info['description']}</p>
            <p style='margin: 0; color: {status_color}; font-weight: bold; font-size: 0.9rem;'>{status_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón de acción
        if st.button(
            button_text, 
            key=f"btn_{connector_key}",
            type=button_type,
            use_container_width=True
        ):
            st.session_state[f'configure_{connector_key}'] = True
            st.rerun()
        
        # Mostrar configuración si está seleccionada
        if st.session_state.get(f'configure_{connector_key}', False):
            with st.expander(f"⚙️ Configurar {info['name']}", expanded=True):
                try:
                    connector.configure()
                    
                    # Botón para cerrar configuración
                    if st.button(f"✅ Finalizar configuración de {info['name']}", key=f"close_{connector_key}"):
                        st.session_state[f'configure_{connector_key}'] = False
                        st.success(f"Configuración de {info['name']} completada")
                        st.rerun()
                
                except Exception as e:
                    st.error(f"Error en la configuración de {info['name']}: {str(e)}")
                    if st.button(f"❌ Cerrar", key=f"error_close_{connector_key}"):
                        st.session_state[f'configure_{connector_key}'] = False
                        st.rerun()
    
    def get_connected_connectors(self):
        """Obtener lista de conectores activos"""
        return {
            name: connector for name, connector in self.connectors.items() 
            if connector.is_connected()
        }
    
    def get_all_data(self, date_range=30):
        """Obtener datos de todos los conectores activos"""
        all_data = {}
        
        for name, connector in self.connectors.items():
            if connector.is_connected():
                try:
                    data = connector.fetch_data(date_range)
                    if data is not None:
                        all_data[name] = data
                except Exception as e:
                    st.warning(f"Error al obtener datos de {name}: {str(e)}")
        
        return all_data
    
    def test_all_connections(self):
        """Probar todas las conexiones activas"""
        results = {}
        
        for name, connector in self.connectors.items():
            if connector.is_connected():
                try:
                    success, message = connector.test_connection()
                    results[name] = {
                        'success': success,
                        'message': message,
                        'connector_name': self.connector_info[name]['name']
                    }
                except Exception as e:
                    results[name] = {
                        'success': False,
                        'message': f"Error en test: {str(e)}",
                        'connector_name': self.connector_info[name]['name']
                    }
        
        return results
    
    def show_connection_health(self):
        """Mostrar estado de salud de las conexiones"""
        st.markdown("### 🏥 Estado de Salud de Conexiones")
        
        test_results = self.test_all_connections()
        
        if not test_results:
            st.info("No hay conexiones activas para probar")
            return
        
        for connector_key, result in test_results.items():
            icon = "✅" if result['success'] else "❌"
            status = "Funcionando" if result['success'] else "Error"
            color = "#28a745" if result['success'] else "#dc3545"
            
            st.markdown(f"""
            <div style='border-left: 4px solid {color}; background: #f8f9fa; 
                        padding: 1rem; margin: 0.5rem 0; border-radius: 5px;'>
                <strong>{icon} {result['connector_name']}</strong> - {status}<br>
                <small style='color: #666;'>{result['message']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    def export_configuration(self):
        """Exportar configuración de integraciones"""
        config = {
            'timestamp': st.session_state.get('last_config_export', 'Never'),
            'connected_integrations': []
        }
        
        for name, connector in self.connectors.items():
            if connector.is_connected():
                config['connected_integrations'].append({
                    'name': name,
                    'display_name': self.connector_info[name]['name'],
                    'category': self.connector_info[name]['category'],
                    'last_tested': 'Recently'  # Placeholder
                })
        
        return config
    
    def get_integration_analytics(self):
        """Obtener analytics de uso de integraciones"""
        analytics = {
            'total_integrations': len(self.connectors),
            'connected_integrations': len(self.get_connected_connectors()),
            'by_category': {},
            'by_priority': {}
        }
        
        # Analytics por categoría
        for name, info in self.connector_info.items():
            category = info['category']
            priority = info['priority']
            is_connected = self.connectors[name].is_connected()
            
            # Por categoría
            if category not in analytics['by_category']:
                analytics['by_category'][category] = {'total': 0, 'connected': 0}
            analytics['by_category'][category]['total'] += 1
            if is_connected:
                analytics['by_category'][category]['connected'] += 1
            
            # Por prioridad
            if priority not in analytics['by_priority']:
                analytics['by_priority'][priority] = {'total': 0, 'connected': 0}
            analytics['by_priority'][priority]['total'] += 1
            if is_connected:
                analytics['by_priority'][priority]['connected'] += 1
        
        return analytics