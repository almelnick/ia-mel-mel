# utils/intelligent_onboarding.py
import streamlit as st
from datetime import datetime

class IntelligentOnboarding:
    def __init__(self):
        self.business_types = {
            'ecommerce': {
                'name': 'E-commerce',
                'description': 'Tienda online que vende productos físicos o digitales',
                'integrations': ['shopify', 'woocommerce', 'ga4', 'meta', 'klaviyo', 'google_ads'],
                'metrics': ['revenue', 'aov', 'conversion_rate', 'roas', 'customer_acquisition'],
                'icon': '🛍️'
            },
            'lead_generation': {
                'name': 'Lead Generation',
                'description': 'Genera leads y los convierte en clientes potenciales',
                'integrations': ['ga4', 'meta', 'google_ads', 'mailchimp', 'klaviyo'],
                'metrics': ['cost_per_lead', 'conversion_rate', 'lead_quality', 'pipeline_value'],
                'icon': '🎯'
            },
            'saas': {
                'name': 'SaaS/Software',
                'description': 'Software como servicio con suscripciones recurrentes',
                'integrations': ['ga4', 'meta', 'google_ads', 'klaviyo', 'csv'],
                'metrics': ['mrr', 'churn_rate', 'ltv', 'cac', 'trial_conversion'],
                'icon': '💻'
            },
            'local_business': {
                'name': 'Negocio Local',
                'description': 'Negocio físico con presencia local',
                'integrations': ['ga4', 'meta', 'google_ads', 'mailchimp'],
                'metrics': ['store_visits', 'phone_calls', 'local_conversions', 'brand_awareness'],
                'icon': '🏪'
            },
            'content_creator': {
                'name': 'Creator/Influencer',
                'description': 'Creador de contenido que monetiza su audiencia',
                'integrations': ['ga4', 'meta', 'klaviyo', 'csv'],
                'metrics': ['engagement_rate', 'follower_growth', 'sponsored_revenue', 'content_performance'],
                'icon': '🎨'
            },
            'hybrid': {
                'name': 'Híbrido/Múltiple',
                'description': 'Combina varios modelos de negocio',
                'integrations': ['ga4', 'meta', 'shopify', 'klaviyo', 'google_ads', 'csv'],
                'metrics': ['revenue', 'leads', 'engagement', 'roi'],
                'icon': '🔀'
            }
        }
    
    def run_onboarding(self):
        """Ejecutar proceso de onboarding inteligente"""
        if 'onboarding_completed' not in st.session_state:
            st.session_state.onboarding_completed = False
            st.session_state.onboarding_step = 1
        
        if not st.session_state.onboarding_completed:
            self._show_onboarding_flow()
        else:
            self._show_onboarding_summary()
    
    def _show_onboarding_flow(self):
        """Mostrar flujo de onboarding paso a paso"""
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='background: linear-gradient(45deg, #667eea 0%, #764ba2 100%); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       font-size: 3rem; margin-bottom: 0.5rem;'>
                🚀 Marketing Dashboard IA
            </h1>
            <p style='font-size: 1.2rem; color: #666; margin-bottom: 2rem;'>
                Configuremos tu dashboard personalizado en 3 simples pasos
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        progress = (st.session_state.onboarding_step - 1) / 2
        st.progress(progress)
        st.write(f"**Paso {st.session_state.onboarding_step} de 3**")
        
        if st.session_state.onboarding_step == 1:
            self._step_1_business_info()
        elif st.session_state.onboarding_step == 2:
            self._step_2_goals_and_metrics()
        elif st.session_state.onboarding_step == 3:
            self._step_3_integrations()
    
    def _step_1_business_info(self):
        """Paso 1: Información del negocio"""
        st.markdown("### 📊 Cuéntanos sobre tu negocio")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Información básica
            business_name = st.text_input(
                "Nombre de tu negocio",
                placeholder="Mi Empresa Increíble",
                help="Este nombre aparecerá en tu dashboard"
            )
            
            industry = st.selectbox(
                "Industria/Sector",
                [
                    "E-commerce/Retail", "SaaS/Technology", "Marketing/Advertising",
                    "Educación", "Salud/Wellness", "Finanzas", "Real Estate",
                    "Food & Beverage", "Fashion", "Travel", "Automotive", "Otro"
                ]
            )
            
            business_size = st.selectbox(
                "Tamaño del negocio",
                ["Solo/Freelancer", "Startup (2-10 empleados)", "Pequeña empresa (11-50)", 
                 "Mediana empresa (51-200)", "Gran empresa (200+)"]
            )
            
            monthly_revenue = st.selectbox(
                "Ingresos mensuales aproximados",
                ["< $1,000", "$1,000 - $10,000", "$10,000 - $50,000", 
                 "$50,000 - $100,000", "$100,000 - $500,000", "$500,000+", "Prefiero no decir"]
            )
            
            # Detectar tipo de negocio automáticamente
            detected_type = self._detect_business_type(industry, business_size, monthly_revenue)
            
            st.info(f"💡 Basado en tu información, detectamos que tienes un negocio tipo: **{self.business_types[detected_type]['name']}**")
        
        with col2:
            st.markdown("### 🎯 ¿Qué tipo de negocio tienes?")
            
            # Mostrar tipos de negocio
            for type_key, type_info in self.business_types.items():
                with st.expander(f"{type_info['icon']} {type_info['name']}"):
                    st.write(type_info['description'])
                    if type_key == detected_type:
                        st.success("✅ Tipo detectado automáticamente")
        
        # Permitir override manual
        st.markdown("### 🔧 Confirmación")
        business_type = st.selectbox(
            "¿Es correcto el tipo detectado o prefieres otro?",
            list(self.business_types.keys()),
            format_func=lambda x: f"{self.business_types[x]['icon']} {self.business_types[x]['name']}",
            index=list(self.business_types.keys()).index(detected_type)
        )
        
        if st.button("➡️ Continuar al Paso 2", type="primary", disabled=not business_name):
            # Guardar información
            st.session_state.onboarding_data = {
                'business_name': business_name,
                'industry': industry,
                'business_size': business_size,
                'monthly_revenue': monthly_revenue,
                'business_type': business_type,
                'detected_type': detected_type
            }
            st.session_state.onboarding_step = 2
            st.rerun()
    
    def _step_2_goals_and_metrics(self):
        """Paso 2: Objetivos y métricas"""
        st.markdown("### 🎯 ¿Cuáles son tus objetivos principales?")
        
        business_type = st.session_state.onboarding_data['business_type']
        type_info = self.business_types[business_type]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info(f"Configurando para negocio tipo: **{type_info['icon']} {type_info['name']}**")
            
            # Objetivos principales
            primary_goals = st.multiselect(
                "Selecciona tus 3 objetivos principales:",
                [
                    "Aumentar ventas/ingresos",
                    "Reducir costo de adquisición (CAC)",
                    "Mejorar retorno de inversión (ROI/ROAS)",
                    "Incrementar tráfico web",
                    "Mejorar tasa de conversión",
                    "Hacer crecer base de clientes",
                    "Optimizar campañas publicitarias",
                    "Automatizar reportes",
                    "Identificar mejores canales",
                    "Escalar operaciones"
                ],
                default=["Aumentar ventas/ingresos", "Mejorar retorno de inversión (ROI/ROAS)", "Optimizar campañas publicitarias"][:3],
                max_selections=3
            )
            
            # Métricas clave basadas en el tipo de negocio
            st.markdown("### 📈 Métricas más importantes para ti:")
            recommended_metrics = type_info['metrics']
            
            selected_metrics = []
            for metric in recommended_metrics:
                metric_names = {
                    'revenue': 'Ingresos/Ventas',
                    'aov': 'Valor Promedio del Pedido',
                    'conversion_rate': 'Tasa de Conversión',
                    'roas': 'Return on Ad Spend (ROAS)',
                    'customer_acquisition': 'Costo de Adquisición (CAC)',
                    'cost_per_lead': 'Costo por Lead',
                    'lead_quality': 'Calidad de Leads',
                    'pipeline_value': 'Valor del Pipeline',
                    'mrr': 'Ingresos Recurrentes Mensuales',
                    'churn_rate': 'Tasa de Cancelación',
                    'ltv': 'Valor de Vida del Cliente',
                    'cac': 'Costo de Adquisición',
                    'trial_conversion': 'Conversión de Trial',
                    'store_visits': 'Visitas a Tienda',
                    'phone_calls': 'Llamadas Telefónicas',
                    'local_conversions': 'Conversiones Locales',
                    'brand_awareness': 'Conocimiento de Marca',
                    'engagement_rate': 'Tasa de Engagement',
                    'follower_growth': 'Crecimiento de Seguidores',
                    'sponsored_revenue': 'Ingresos por Patrocinios',
                    'content_performance': 'Performance de Contenido',
                    'leads': 'Generación de Leads',
                    'engagement': 'Engagement',
                    'roi': 'Retorno de Inversión'
                }
                
                if st.checkbox(metric_names.get(metric, metric), value=True, key=f"metric_{metric}"):
                    selected_metrics.append(metric)
            
            # Frecuencia de reportes
            report_frequency = st.selectbox(
                "¿Con qué frecuencia quieres ver reportes?",
                ["Tiempo real", "Diario", "Semanal", "Mensual"]
            )
        
        with col2:
            st.markdown("### 💡 Recomendaciones")
            st.success(f"Para negocios {type_info['name']}, recomendamos enfocarse en:")
            for metric in recommended_metrics[:4]:
                metric_names = {
                    'revenue': '💰 Ingresos/Ventas',
                    'aov': '🛒 Valor Promedio del Pedido',
                    'conversion_rate': '📈 Tasa de Conversión',
                    'roas': '💹 Return on Ad Spend',
                    'customer_acquisition': '👥 Costo de Adquisición',
                    'cost_per_lead': '🎯 Costo por Lead',
                    'mrr': '🔄 Ingresos Recurrentes',
                    'ltv': '⭐ Valor de Vida del Cliente'
                }
                st.write(f"• {metric_names.get(metric, metric)}")
        
        col_back, col_next = st.columns([1, 1])
        with col_back:
            if st.button("⬅️ Volver al Paso 1"):
                st.session_state.onboarding_step = 1
                st.rerun()
        
        with col_next:
            if st.button("➡️ Continuar al Paso 3", type="primary", disabled=len(primary_goals) == 0):
                # Guardar información
                st.session_state.onboarding_data.update({
                    'primary_goals': primary_goals,
                    'selected_metrics': selected_metrics,
                    'report_frequency': report_frequency
                })
                st.session_state.onboarding_step = 3
                st.rerun()
    
    def _step_3_integrations(self):
        """Paso 3: Configurar integraciones"""
        st.markdown("### 🔗 Configuremos tus integraciones")
        
        business_type = st.session_state.onboarding_data['business_type']
        type_info = self.business_types[business_type]
        
        st.info(f"Basado en tu tipo de negocio **{type_info['name']}**, estas son las integraciones recomendadas:")
        
        # Integraciones recomendadas
        recommended_integrations = type_info['integrations']
        
        integration_info = {
            'ga4': {'name': 'Google Analytics 4', 'icon': '📊', 'priority': 'alta', 'description': 'Tráfico web y comportamiento'},
            'meta': {'name': 'Meta Ads', 'icon': '📘', 'priority': 'alta', 'description': 'Campañas de Facebook e Instagram'},
            'google_ads': {'name': 'Google Ads', 'icon': '🎯', 'priority': 'alta', 'description': 'Campañas de búsqueda y display'},
            'shopify': {'name': 'Shopify', 'icon': '🛍️', 'priority': 'alta', 'description': 'Datos de ventas y productos'},
            'woocommerce': {'name': 'WooCommerce', 'icon': '🛒', 'priority': 'alta', 'description': 'Tienda WordPress'},
            'klaviyo': {'name': 'Klaviyo', 'icon': '📧', 'priority': 'media', 'description': 'Email marketing avanzado'},
            'mailchimp': {'name': 'Mailchimp', 'icon': '🐒', 'priority': 'media', 'description': 'Email marketing básico'},
            'mailerlite': {'name': 'MailerLite', 'icon': '✉️', 'priority': 'baja', 'description': 'Email marketing simple'},
            'csv': {'name': 'CSV Upload', 'icon': '📄', 'priority': 'baja', 'description': 'Datos personalizados'}
        }
        
        selected_integrations = []
        
        # Mostrar integraciones por prioridad
        priorities = ['alta', 'media', 'baja']
        priority_colors = {'alta': 'success', 'media': 'warning', 'baja': 'info'}
        
        for priority in priorities:
            priority_integrations = [
                integration for integration in recommended_integrations 
                if integration_info.get(integration, {}).get('priority') == priority
            ]
            
            if priority_integrations:
                st.markdown(f"#### Prioridad {priority.title()}")
                
                cols = st.columns(min(3, len(priority_integrations)))
                for i, integration in enumerate(priority_integrations):
                