# dashboards/ecommerce_dashboard.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class EcommerceDashboard:
    def __init__(self, data_processor, ai_analyzer):
        self.data_processor = data_processor
        self.ai_analyzer = ai_analyzer
    
    def render(self, integration_manager):
        """Renderizar dashboard específico para e-commerce"""
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='background: linear-gradient(45deg, #667eea 0%, #764ba2 100%); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       font-size: 2.5rem; margin-bottom: 0.5rem;'>
                🛍️ E-commerce Dashboard
            </h1>
            <p style='color: #666; font-size: 1.1rem;'>
                Análisis completo de tu tienda online y performance de marketing
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Procesar datos
        processed_data = self.data_processor.process_multi_source_data(integration_manager)
        kpis = self.data_processor.get_kpi_metrics(processed_data)
        
        # Mostrar métricas principales
        self._render_kpi_section(kpis)
        
        # Mostrar gráficos principales
        self._render_main_charts(processed_data)
        
        # Análisis específicos de e-commerce
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_sales_analysis(processed_data)
            self._render_customer_analysis(processed_data)
        
        with col2:
            self._render_product_performance(processed_data)
            self._render_marketing_channels(processed_data)
        
        # Insights de IA
        self._render_ai_insights(processed_data)
    
    def _render_kpi_section(self, kpis):
        """Renderizar sección de KPIs principales"""
        st.markdown("### 📊 Métricas Principales")
        
        # Primera fila de KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            revenue = kpis['total_revenue']
            self._render_kpi_card(
                "💰 Revenue Total",
                f"${revenue['value']:,.0f}",
                revenue['trend'],
                "success" if revenue['trend'] > 0 else "error"
            )
        
        with col2:
            roas = kpis['overall_roas']
            self._render_kpi_card(
                "📈 ROAS Promedio",
                f"{roas['value']:.1f}x",
                roas['trend'],
                "success" if roas['value'] >= 3 else "warning" if roas['value'] >= 2 else "error"
            )
        
        with col3:
            conversions = kpis['total_conversions']
            self._render_kpi_card(
                "🎯 Conversiones",
                f"{conversions['value']:,}",
                conversions['trend'],
                "success" if conversions['trend'] > 0 else "error"
            )
        
        with col4:
            spend = kpis['total_spend']
            self._render_kpi_card(
                "💸 Gasto Publicitario",
                f"${spend['value']:,.0f}",
                spend['trend'],
                "error" if spend['trend'] > 20 else "warning" if spend['trend'] > 10 else "success"
            )
        
        # Segunda fila de KPIs (métricas específicas de e-commerce)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # AOV calculado
            aov = revenue['value'] / conversions['value'] if conversions['value'] > 0 else 0
            self._render_kpi_card(
                "🛒 AOV",
                f"${aov:.0f}",
                np.random.uniform(-5, 15),  # Simular tendencia
                "success"
            )
        
        with col2:
            ctr = kpis['overall_ctr']
            self._render_kpi_card(
                "👆 CTR Promedio",
                f"{ctr['value']:.1f}%",
                ctr['trend'],
                "success" if ctr['value'] >= 2 else "warning"
            )
        
        with col3:
            # CAC calculado
            cac = spend['value'] / conversions['value'] if conversions['value'] > 0 else 0
            self._render_kpi_card(
                "👥 CAC",
                f"${cac:.0f}",
                np.random.uniform(-10, 5),  # Simular tendencia
                "success" if cac < 50 else "warning"
            )
        
        with col4:
            conversion_rate = kpis['overall_conversion_rate']
            self._render_kpi_card(
                "⚡ Tasa Conversión",
                f"{conversion_rate['value']:.1f}%",
                conversion_rate['trend'],
                "success" if conversion_rate['value'] >= 2 else "warning"
            )
    
    def _render_kpi_card(self, title, value, trend, color_type):
        """Renderizar tarjeta KPI individual"""
        color_map = {
            "success": "#28a745",
            "warning": "#ffc107", 
            "error": "#dc3545",
            "info": "#17a2b8"
        }
        
        trend_icon = "↗️" if trend > 0 else "↘️" if trend < 0 else "➡️"
        trend_color = "#28a745" if trend > 0 else "#dc3545" if trend < 0 else "#6c757d"
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, white 0%, #f8f9fa 100%); 
                    border-left: 4px solid {color_map[color_type]}; 
                    border-radius: 10px; padding: 1rem; margin: 0.5rem 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <h6 style='margin: 0; color: #666; font-size: 0.9rem;'>{title}</h6>
            <h3 style='margin: 0.2rem 0; color: #333; font-weight: bold;'>{value}</h3>
            <p style='margin: 0; color: {trend_color}; font-size: 0.8rem;'>
                {trend_icon} {abs(trend):.1f}% vs período anterior
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_main_charts(self, processed_data):
        """Renderizar gráficos principales"""
        st.markdown("### 📈 Análisis de Tendencias")
        
        charts = self.data_processor.create_performance_charts(processed_data)
        
        # Gráfico de revenue y gasto en el tiempo
        col1, col2 = st.columns(2)
        
        with col1:
            if 'revenue_trend' in charts and charts['revenue_trend']:
                st.plotly_chart(charts['revenue_trend'], use_container_width=True)
            else:
                self._render_demo_revenue_chart()
        
        with col2:
            if 'channel_performance' in charts and charts['channel_performance']:
                st.plotly_chart(charts['channel_performance'], use_container_width=True)
            else:
                self._render_demo_channel_chart()
        
        # Gráfico de ROAS y funnel
        col1, col2 = st.columns(2)
        
        with col1:
            if 'roas_comparison' in charts and charts['roas_comparison']:
                st.plotly_chart(charts['roas_comparison'], use_container_width=True)
            else:
                self._render_demo_roas_chart()
        
        with col2:
            if 'conversion_funnel' in charts and charts['conversion_funnel']:
                st.plotly_chart(charts['conversion_funnel'], use_container_width=True)
            else:
                self._render_demo_funnel_chart()
    
    def _render_sales_analysis(self, processed_data):
        """Renderizar análisis de ventas"""
        with st.container():
            st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 10px; padding: 1rem; margin: 1rem 0;'>
                <h4 style='color: white; margin: 0;'>💰 Análisis de Ventas</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Simular datos de ventas por período
            periods = ['Última semana', 'Últimas 2 semanas', 'Último mes']
            sales_data = [25680, 48320, 89450]
            growth_rates = [12.5, 8.3, 15.2]
            
            for i, (period, sales, growth) in enumerate(zip(periods, sales_data, growth_rates)):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{period}:**")
                    st.write(f"${sales:,}")
                with col2:
                    if growth > 0:
                        st.success(f"+{growth}%")
                    else:
                        st.error(f"{growth}%")
            
            # Gráfico de ventas por día de la semana
            days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
            sales_by_day = [3200, 2800, 3100, 3400, 4200, 5800, 4500]
            
            fig = px.bar(
                x=days, 
                y=sales_by_day,
                title="Ventas por Día de la Semana",
                color=sales_by_day,
                color_continuous_scale='viridis'
            )
            fig.update_layout(
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_customer_analysis(self, processed_data):
        """Renderizar análisis de clientes"""
        with st.container():
            st.markdown("""
            <div style='background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                        border-radius: 10px; padding: 1rem; margin: 1rem 0;'>
                <h4 style='color: white; margin: 0;'>👥 Análisis de Clientes</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Métricas de clientes
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Nuevos Clientes", "1,247", "+18%")
                st.metric("Clientes Recurrentes", "856", "+12%")
            
            with col2:
                st.metric("LTV Promedio", "$385", "+8%")
                st.metric("Tasa de Retención", "34%", "+2%")
            
            # Segmentación de clientes
            segments = ['Nuevos', 'Ocasionales', 'Frecuentes', 'VIP']
            segment_values = [45, 30, 20, 5]
            
            fig = px.pie(
                values=segment_values,
                names=segments,
                title="Segmentación de Clientes",
                color_discrete_sequence=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
            )
            fig.update_layout(
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_product_performance(self, processed_data):
        """Renderizar análisis de productos"""
        with st.container():
            st.markdown("""
            <div style='background: linear-gradient(135deg, #ffc107 0%, #ff8c00 100%); 
                        border-radius: 10px; padding: 1rem; margin: 1rem 0;'>
                <h4 style='color: white; margin: 0;'>🏆 Top Productos</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Simular datos de productos top
            products = [
                {'name': 'Premium T-Shirt', 'sales': 1250, 'revenue': 31250},
                {'name': 'Wireless Headphones', 'sales': 856, 'revenue': 85600},
                {'name': 'Eco Water Bottle', 'sales': 742, 'revenue': 18550},
                {'name': 'Smart Watch', 'sales': 623, 'revenue': 124600},
                {'name': 'Yoga Mat Pro', 'sales': 589, 'revenue': 35340}
            ]
            
            for i, product in enumerate(products, 1):
                with st.expander(f"{i}. {product['name']}", expanded=i<=3):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Unidades:** {product['sales']:,}")
                    with col2:
                        st.write(f"**Revenue:** ${product['revenue']:,}")
                    
                    # Barra de progreso visual
                    max_sales = max(p['sales'] for p in products)
                    progress = product['sales'] / max_sales
                    st.progress(progress)
            
            # Categorías más vendidas
            st.write("**📊 Por Categorías:**")
            categories = ['Ropa', 'Electrónicos', 'Deportes', 'Hogar']
            cat_sales = [35, 28, 22, 15]
            
            for cat, sales in zip(categories, cat_sales):
                st.write(f"• {cat}: {sales}%")
    
    def _render_marketing_channels(self, processed_data):
        """Renderizar análisis de canales de marketing"""
        with st.container():
            st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 10px; padding: 1rem; margin: 1rem 0;'>
                <h4 style='color: white; margin: 0;'>📱 Canales de Marketing</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Performance por canal
            channels_data = [
                {'name': 'Meta Ads', 'spend': 4500, 'revenue': 18000, 'roas': 4.0, 'status': 'excellent'},
                {'name': 'Google Ads', 'spend': 3200, 'revenue': 9600, 'roas': 3.0, 'status': 'good'},
                {'name': 'Email Marketing', 'spend': 800, 'revenue': 3200, 'roas': 4.0, 'status': 'excellent'},
                {'name': 'Organic Social', 'spend': 0, 'revenue': 1200, 'roas': float('inf'), 'status': 'excellent'}
            ]
            
            for channel in channels_data:
                status_colors = {
                    'excellent': '#28a745',
                    'good': '#ffc107',
                    'poor': '#dc3545'
                }
                
                with st.expander(f"{channel['name']} - ROAS: {channel['roas']:.1f}x", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Gasto", f"${channel['spend']:,}")
                    with col2:
                        st.metric("Revenue", f"${channel['revenue']:,}")
                    with col3:
                        roas_delta = channel['roas'] - 3.0  # Benchmark
                        st.metric("ROAS", f"{channel['roas']:.1f}x", f"{roas_delta:+.1f}x")
                    
                    # Barra de performance
                    performance_score = min(100, (channel['roas'] / 5.0) * 100)
                    st.progress(performance_score / 100)
    
    def _render_ai_insights(self, processed_data):
        """Renderizar insights de IA específicos para e-commerce"""
        st.markdown("### 🤖 Insights de IA para E-commerce")
        
        # Generar insights específicos
        insights = self.ai_analyzer.analyze_performance_data(
            processed_data.get('raw_data', {})
        )
        
        # Mostrar insights en tabs
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Oportunidades", "📈 Escalado", "🛒 Productos", "👥 Audiencias"])
        
        with tab1:
            self._render_optimization_opportunities(insights)
        
        with tab2:
            self._render_scaling_recommendations(insights)
        
        with tab3:
            self._render_product_insights(insights)
        
        with tab4:
            self._render_audience_insights(insights)
    
    def _render_optimization_opportunities(self, insights):
        """Renderizar oportunidades de optimización"""
        opportunities = insights.get('optimization_opportunities', [])
        
        if opportunities:
            for i, opp in enumerate(opportunities[:3]):  # Mostrar top 3
                priority_colors = {
                    'alta': '#dc3545',
                    'media': '#ffc107',
                    'baja': '#28a745'
                }
                
                st.markdown(f"""
                <div style='border-left: 4px solid {priority_colors.get(opp.get("priority", "media"), "#ffc107")}; 
                            background: #f8f9fa; padding: 1rem; border-radius: 5px; margin: 1rem 0;'>
                    <h5 style='margin: 0; color: #333;'>{opp.get("title", "Oportunidad de Optimización")}</h5>
                    <p style='margin: 0.5rem 0; color: #666;'>{opp.get("description", "")}</p>
                    <p style='margin: 0; color: #28a745; font-weight: bold;'>
                        💡 Impacto potencial: {opp.get("potential_impact", "Mejora significativa")}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar acciones recomendadas
                actions = opp.get('actions', [])
                if actions:
                    st.write("**Acciones recomendadas:**")
                    for action in actions[:3]:
                        st.write(f"• {action}")
        else:
            st.info("🎉 ¡Excelente! No se detectaron oportunidades críticas de optimización.")
    
    def _render_scaling_recommendations(self, insights):
        """Renderizar recomendaciones de escalado"""
        scaling = insights.get('scaling_recommendations', [])
        
        for rec in scaling[:3]:
            scale_type = rec.get('type', 'scale_up')
            icon = "📈" if scale_type == 'scale_up' else "📉"
            color = "#28a745" if scale_type == 'scale_up' else "#dc3545"
            
            st.markdown(f"""
            <div style='border: 2px solid {color}; background: #f8f9fa; 
                        padding: 1rem; border-radius: 10px; margin: 1rem 0;'>
                <h5 style='margin: 0; color: {color};'>{icon} {rec.get("title", "Recomendación")}</h5>
                <p style='margin: 0.5rem 0;'><strong>Canal:</strong> {rec.get("channel", "N/A")}</p>
                <p style='margin: 0.5rem 0;'><strong>ROAS Actual:</strong> {rec.get("current_roas", 0):.1f}x</p>
                <p style='margin: 0.5rem 0;'><strong>Acción:</strong> {rec.get("recommended_action", "")}</p>
                <p style='margin: 0; color: #28a745;'><strong>Impacto:</strong> {rec.get("expected_impact", "")}</p>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_product_insights(self, insights):
        """Renderizar insights específicos de productos"""
        st.markdown("#### 🛒 Insights de Productos")
        
        # Simular insights de productos para e-commerce
        product_insights = [
            {
                'product': 'Premium T-Shirt',
                'insight': 'Producto estrella con margen del 65%',
                'recommendation': 'Expandir línea de colores y crear bundle',
                'impact': 'Potencial +40% en revenue'
            },
            {
                'product': 'Smart Watch',
                'insight': 'Alto valor pero baja rotación',
                'recommendation': 'Campaña específica para audiencia tech',
                'impact': 'Mejorar conversión en 25%'
            },
            {
                'product': 'Eco Water Bottle',
                'insight': 'Trending en audiencia millennials',
                'recommendation': 'Cross-sell con productos deportivos',
                'impact': 'Incrementar AOV en $15'
            }
        ]
        
        for insight in product_insights:
            with st.expander(f"💡 {insight['product']}", expanded=True):
                st.write(f"**Análisis:** {insight['insight']}")
                st.write(f"**Recomendación:** {insight['recommendation']}")
                st.success(f"**Impacto:** {insight['impact']}")
    
    def _render_audience_insights(self, insights):
        """Renderizar insights de audiencias"""
        audience_data = insights.get('audience_insights', [])
        
        if audience_data:
            for audience in audience_data[:3]:
                performance = audience.get('performance_rating', 'regular')
                
                # Color basado en performance
                colors = {
                    'excelente': '#28a745',
                    'bueno': '#17a2b8',
                    'regular': '#ffc107',
                    'bajo': '#dc3545'
                }
                
                color = colors.get(performance, '#ffc107')
                
                st.markdown(f"""
                <div style='border-left: 4px solid {color}; background: #f8f9fa; 
                            padding: 1rem; border-radius: 5px; margin: 1rem 0;'>
                    <h6 style='margin: 0; color: #333;'>{audience.get("audience_name", "Audiencia")}</h6>
                    <p style='margin: 0.3rem 0;'><strong>ROAS:</strong> {audience.get("roas", 0):.1f}x</p>
                    <p style='margin: 0.3rem 0;'><strong>% Presupuesto:</strong> {audience.get("spend_percentage", 0):.1f}%</p>
                    <p style='margin: 0; color: {color}; font-weight: bold;'>
                        {audience.get("recommendation", "Mantener configuración actual")}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Conecta tus fuentes de datos publicitarios para ver insights de audiencias")
    
    def _render_demo_revenue_chart(self):
        """Renderizar gráfico demo de revenue"""
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        revenue = np.random.uniform(1000, 4000, len(dates))
        
        # Agregar tendencia creciente
        trend = np.linspace(1, 1.3, len(dates))
        revenue = revenue * trend
        
        fig = px.line(x=dates, y=revenue, title="Tendencia de Revenue (30 días)")
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_demo_channel_chart(self):
        """Renderizar gráfico demo de canales"""
        channels = ['Meta Ads', 'Google Ads', 'Email', 'Organic']
        revenue = [18000, 9600, 3200, 1200]
        spend = [4500, 3200, 800, 0]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Revenue', x=channels, y=revenue, marker_color='#28a745'))
        fig.add_trace(go.Bar(name='Spend', x=channels, y=spend, marker_color='#dc3545'))
        
        fig.update_layout(
            title='Revenue vs Spend por Canal',
            barmode='group',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_demo_roas_chart(self):
        """Renderizar gráfico demo de ROAS"""
        channels = ['Meta Ads', 'Google Ads', 'Email', 'Organic']
        roas = [4.0, 3.0, 4.0, float('inf')]
        roas_display = [4.0, 3.0, 4.0, 5.0]  # Para visualización
        
        colors = ['#28a745' if r >= 3 else '#ffc107' if r >= 2 else '#dc3545' for r in roas_display]
        
        fig = go.Figure(data=[
            go.Bar(x=channels, y=roas_display, marker_color=colors)
        ])
        fig.update_layout(
            title='ROAS por Canal',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_demo_funnel_chart(self):
        """Renderizar gráfico demo de funnel"""
        stages = ['Impresiones', 'Clics', 'Visitas', 'Conversiones']
        values = [100000, 5000, 3500, 250]
        
        fig = go.Figure(go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial"
        ))
        fig.update_layout(
            title='Funnel de Conversión',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)