# utils/data_processor.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class DataProcessor:
    def __init__(self):
        self.processed_cache = {}
        self.chart_cache = {}
    
    def process_multi_source_data(self, integration_manager):
        """Procesar datos de múltiples fuentes de integración"""
        try:
            processed_data = {}
            
            # Obtener datos de cada conector activo
            for connector_name, connector in integration_manager.connectors.items():
                if connector.is_connected():
                    try:
                        raw_data = connector.fetch_data(30)  # 30 días de datos
                        if raw_data is not None and not raw_data.empty:
                            processed_data[connector_name] = self._standardize_data_format(
                                raw_data, connector_name
                            )
                    except Exception as e:
                        st.warning(f"Error al procesar datos de {connector_name}: {str(e)}")
                        continue
            
            # Generar métricas combinadas
            combined_metrics = self._combine_metrics(processed_data)
            
            # Cachear resultados
            self.processed_cache = {
                'raw_data': processed_data,
                'combined_metrics': combined_metrics,
                'last_updated': datetime.now()
            }
            
            return self.processed_cache
            
        except Exception as e:
            st.error(f"Error en procesamiento de datos: {str(e)}")
            return self._generate_demo_data()
    
    def _standardize_data_format(self, data, source_type):
        """Estandarizar formato de datos según la fuente"""
        standardized = data.copy()
        
        # Asegurar que hay columna de fecha
        if 'date' not in standardized.columns:
            date_columns = [col for col in standardized.columns 
                          if 'date' in col.lower() or 'fecha' in col.lower()]
            if date_columns:
                standardized['date'] = pd.to_datetime(standardized[date_columns[0]])
            else:
                # Crear fechas dummy si no existen
                standardized['date'] = pd.date_range(
                    end=datetime.now(), 
                    periods=len(standardized), 
                    freq='D'
                )
        
        # Mapear columnas según el tipo de fuente
        if source_type in ['meta', 'google_ads']:
            standardized = self._standardize_ads_data(standardized, source_type)
        elif source_type in ['shopify', 'woocommerce']:
            standardized = self._standardize_ecommerce_data(standardized)
        elif source_type in ['klaviyo', 'mailchimp', 'mailerlite']:
            standardized = self._standardize_email_data(standardized)
        elif source_type == 'ga4':
            standardized = self._standardize_analytics_data(standardized)
        elif source_type == 'csv':
            standardized = self._standardize_csv_data(standardized)
        
        # Agregar metadatos
        standardized['source'] = source_type
        standardized['processed_at'] = datetime.now()
        
        return standardized
    
    def _standardize_ads_data(self, data, platform):
        """Estandarizar datos de plataformas publicitarias"""
        # Mapeo común de métricas publicitarias
        column_mapping = {
            'spend': ['spend', 'cost', 'gasto'],
            'impressions': ['impressions', 'impresiones'],
            'clicks': ['clicks', 'clics'],
            'conversions': ['conversions', 'conversion', 'purchases'],
            'revenue': ['revenue', 'purchase_value', 'conversion_value'],
            'cpc': ['cpc', 'avg_cpc'],
            'cpm': ['cpm', 'avg_cpm'],
            'ctr': ['ctr', 'click_through_rate'],
            'roas': ['roas', 'return_on_ad_spend']
        }
        
        return self._apply_column_mapping(data, column_mapping)
    
    def _standardize_ecommerce_data(self, data):
        """Estandarizar datos de e-commerce"""
        column_mapping = {
            'revenue': ['revenue', 'sales', 'ventas', 'total_sales'],
            'orders': ['orders', 'pedidos', 'order_count'],
            'units_sold': ['units_sold', 'quantity', 'cantidad'],
            'customers': ['customers', 'clientes', 'new_customers'],
            'aov': ['aov', 'average_order_value', 'valor_promedio']
        }
        
        standardized = self._apply_column_mapping(data, column_mapping)
        
        # Calcular AOV si no existe
        if 'aov' not in standardized.columns and 'revenue' in standardized.columns and 'orders' in standardized.columns:
            standardized['aov'] = standardized['revenue'] / standardized['orders']
        
        return standardized
    
    def _standardize_email_data(self, data):
        """Estandarizar datos de email marketing"""
        column_mapping = {
            'emails_sent': ['emails_sent', 'sent', 'enviados'],
            'opens': ['opens', 'emails_opened', 'aperturas'],
            'clicks': ['clicks', 'emails_clicked', 'clics'],
            'unsubscribes': ['unsubscribes', 'unsubs', 'bajas'],
            'bounces': ['bounces', 'rebotes'],
            'revenue': ['revenue', 'email_revenue', 'ingresos']
        }
        
        standardized = self._apply_column_mapping(data, column_mapping)
        
        # Calcular rates si no existen
        if 'open_rate' not in standardized.columns and 'opens' in standardized.columns and 'emails_sent' in standardized.columns:
            standardized['open_rate'] = (standardized['opens'] / standardized['emails_sent']) * 100
        
        if 'click_rate' not in standardized.columns and 'clicks' in standardized.columns and 'emails_sent' in standardized.columns:
            standardized['click_rate'] = (standardized['clicks'] / standardized['emails_sent']) * 100
        
        return standardized
    
    def _standardize_analytics_data(self, data):
        """Estandarizar datos de Google Analytics"""
        column_mapping = {
            'sessions': ['sessions', 'sesiones'],
            'users': ['users', 'usuarios', 'unique_users'],
            'pageviews': ['pageviews', 'page_views', 'vistas'],
            'bounce_rate': ['bounce_rate', 'tasa_rebote'],
            'conversions': ['conversions', 'goals', 'objetivos'],
            'revenue': ['revenue', 'ecommerce_revenue', 'ingresos']
        }
        
        return self._apply_column_mapping(data, column_mapping)
    
    def _standardize_csv_data(self, data):
        """Estandarizar datos de CSV (flexibilidad máxima)"""
        # Para CSV, intentar detectar automáticamente las columnas
        standardized = data.copy()
        
        # Detectar columnas numéricas que podrían ser métricas
        numeric_columns = standardized.select_dtypes(include=[np.number]).columns
        
        # Intentar mapear columnas comunes
        common_patterns = {
            'revenue': ['revenue', 'sales', 'ventas', 'ingresos', 'total'],
            'cost': ['cost', 'spend', 'gasto', 'inversion'],
            'conversions': ['conversions', 'purchases', 'orders', 'pedidos'],
            'impressions': ['impressions', 'views', 'vistas'],
            'clicks': ['clicks', 'clics']
        }
        
        for metric, patterns in common_patterns.items():
            for col in standardized.columns:
                if any(pattern in col.lower() for pattern in patterns):
                    if col in numeric_columns:
                        standardized[metric] = standardized[col]
                        break
        
        return standardized
    
    def _apply_column_mapping(self, data, mapping):
        """Aplicar mapeo de columnas"""
        standardized = data.copy()
        
        for standard_name, possible_names in mapping.items():
            for col_name in data.columns:
                if col_name.lower() in [name.lower() for name in possible_names]:
                    if col_name != standard_name:
                        standardized[standard_name] = standardized[col_name]
                    break
        
        return standardized
    
    def _combine_metrics(self, processed_data):
        """Combinar métricas de múltiples fuentes"""
        combined = {
            'overview': {},
            'channels': {},
            'trends': {},
            'performance': {}
        }
        
        # Métricas generales
        total_spend = 0
        total_revenue = 0
        total_conversions = 0
        total_impressions = 0
        total_clicks = 0
        
        # Procesar cada fuente
        for source, data in processed_data.items():
            if data is None or data.empty:
                continue
            
            # Sumar métricas totales
            if 'spend' in data.columns:
                total_spend += data['spend'].sum()
            if 'revenue' in data.columns:
                total_revenue += data['revenue'].sum()
            if 'conversions' in data.columns:
                total_conversions += data['conversions'].sum()
            if 'impressions' in data.columns:
                total_impressions += data['impressions'].sum()
            if 'clicks' in data.columns:
                total_clicks += data['clicks'].sum()
            
            # Métricas por canal
            combined['channels'][source] = self._calculate_channel_metrics(data, source)
        
        # Calcular métricas derivadas
        combined['overview'] = {
            'total_spend': round(total_spend, 2),
            'total_revenue': round(total_revenue, 2),
            'total_conversions': int(total_conversions),
            'total_impressions': int(total_impressions),
            'total_clicks': int(total_clicks),
            'overall_roas': round(total_revenue / total_spend, 2) if total_spend > 0 else 0,
            'overall_ctr': round((total_clicks / total_impressions) * 100, 2) if total_impressions > 0 else 0,
            'overall_conversion_rate': round((total_conversions / total_clicks) * 100, 2) if total_clicks > 0 else 0
        }
        
        # Tendencias temporales
        combined['trends'] = self._calculate_trends(processed_data)
        
        # Performance comparativa
        combined['performance'] = self._calculate_performance_metrics(processed_data)
        
        return combined
    
    def _calculate_channel_metrics(self, data, source):
        """Calcular métricas específicas por canal"""
        metrics = {'source': source}
        
        # Métricas básicas
        for metric in ['spend', 'revenue', 'conversions', 'impressions', 'clicks']:
            if metric in data.columns:
                metrics[f'total_{metric}'] = data[metric].sum()
                metrics[f'avg_{metric}'] = round(data[metric].mean(), 2)
        
        # Métricas derivadas
        if 'spend' in data.columns and 'revenue' in data.columns:
            total_spend = data['spend'].sum()
            total_revenue = data['revenue'].sum()
            metrics['roas'] = round(total_revenue / total_spend, 2) if total_spend > 0 else 0
        
        if 'clicks' in data.columns and 'impressions' in data.columns:
            total_clicks = data['clicks'].sum()
            total_impressions = data['impressions'].sum()
            metrics['ctr'] = round((total_clicks / total_impressions) * 100, 2) if total_impressions > 0 else 0
        
        if 'spend' in data.columns and 'clicks' in data.columns:
            total_spend = data['spend'].sum()
            total_clicks = data['clicks'].sum()
            metrics['cpc'] = round(total_spend / total_clicks, 2) if total_clicks > 0 else 0
        
        # Tendencia (comparar primera vs segunda mitad del período)
        if len(data) > 7:
            mid_point = len(data) // 2
            first_half = data.iloc[:mid_point]
            second_half = data.iloc[mid_point:]
            
            if 'revenue' in data.columns:
                first_revenue = first_half['revenue'].mean()
                second_revenue = second_half['revenue'].mean()
                metrics['revenue_trend'] = round(((second_revenue - first_revenue) / first_revenue) * 100, 1) if first_revenue > 0 else 0
        
        return metrics
    
    def _calculate_trends(self, processed_data):
        """Calcular tendencias temporales"""
        trends = {}
        
        # Combinar datos por fecha
        all_dates_data = []
        for source, data in processed_data.items():
            if data is not None and not data.empty and 'date' in data.columns:
                daily_data = data.groupby('date').agg({
                    col: 'sum' for col in data.columns 
                    if col in ['spend', 'revenue', 'conversions', 'clicks', 'impressions'] and col in data.columns
                }).reset_index()
                daily_data['source'] = source
                all_dates_data.append(daily_data)
        
        if all_dates_data:
            combined_daily = pd.concat(all_dates_data, ignore_index=True)
            
            # Agrupar por fecha total
            daily_totals = combined_daily.groupby('date').agg({
                col: 'sum' for col in combined_daily.columns 
                if col in ['spend', 'revenue', 'conversions', 'clicks', 'impressions']
            }).reset_index()
            
            # Calcular tendencias
            if len(daily_totals) > 1:
                for metric in ['spend', 'revenue', 'conversions']:
                    if metric in daily_totals.columns:
                        values = daily_totals[metric].values
                        if len(values) > 7:
                            # Calcular tendencia de últimos 7 días vs 7 días anteriores
                            recent_avg = values[-7:].mean()
                            previous_avg = values[-14:-7].mean() if len(values) >= 14 else values[:-7].mean()
                            
                            if previous_avg > 0:
                                trend_pct = ((recent_avg - previous_avg) / previous_avg) * 100
                                trends[f'{metric}_trend'] = {
                                    'percentage': round(trend_pct, 1),
                                    'direction': 'up' if trend_pct > 0 else 'down',
                                    'recent_avg': round(recent_avg, 2),
                                    'previous_avg': round(previous_avg, 2)
                                }
            
            trends['daily_data'] = daily_totals
        
        return trends
    
    def _calculate_performance_metrics(self, processed_data):
        """Calcular métricas de performance comparativa"""
        performance = {}
        
        # Comparar performance entre canales
        channel_performance = []
        for source, data in processed_data.items():
            if data is not None and not data.empty:
                channel_metrics = self._calculate_channel_metrics(data, source)
                channel_performance.append({
                    'channel': source,
                    'roas': channel_metrics.get('roas', 0),
                    'spend': channel_metrics.get('total_spend', 0),
                    'revenue': channel_metrics.get('total_revenue', 0),
                    'ctr': channel_metrics.get('ctr', 0),
                    'cpc': channel_metrics.get('cpc', 0)
                })
        
        if channel_performance:
            # Ordenar por ROAS
            channel_performance.sort(key=lambda x: x['roas'], reverse=True)
            performance['channel_ranking'] = channel_performance
            
            # Identificar mejor y peor canal
            performance['best_channel'] = channel_performance[0] if channel_performance else None
            performance['worst_channel'] = channel_performance[-1] if len(channel_performance) > 1 else None
            
            # Calcular distribución de spend
            total_spend = sum(ch['spend'] for ch in channel_performance)
            if total_spend > 0:
                for channel in channel_performance:
                    channel['spend_percentage'] = round((channel['spend'] / total_spend) * 100, 1)
        
        return performance
    
    def _generate_demo_data(self):
        """Generar datos demo cuando falla el procesamiento real"""
        # Crear datos demo realistas
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        demo_data = {
            'meta': pd.DataFrame({
                'date': dates,
                'spend': np.random.uniform(100, 500, len(dates)),
                'revenue': np.random.uniform(300, 1500, len(dates)),
                'impressions': np.random.randint(5000, 25000, len(dates)),
                'clicks': np.random.randint(150, 800, len(dates)),
                'conversions': np.random.randint(10, 50, len(dates))
            }),
            'google_ads': pd.DataFrame({
                'date': dates,
                'spend': np.random.uniform(80, 400, len(dates)),
                'revenue': np.random.uniform(200, 1200, len(dates)),
                'impressions': np.random.randint(3000, 20000, len(dates)),
                'clicks': np.random.randint(100, 600, len(dates)),
                'conversions': np.random.randint(8, 40, len(dates))
            }),
            'email': pd.DataFrame({
                'date': dates,
                'emails_sent': np.random.randint(1000, 5000, len(dates)),
                'opens': np.random.randint(200, 1200, len(dates)),
                'clicks': np.random.randint(50, 300, len(dates)),
                'revenue': np.random.uniform(100, 800, len(dates))
            })
        }
        
        # Procesar datos demo
        processed_demo = {}
        for source, data in demo_data.items():
            processed_demo[source] = self._standardize_data_format(data, source)
        
        combined_metrics = self._combine_metrics(processed_demo)
        
        return {
            'raw_data': processed_demo,
            'combined_metrics': combined_metrics,
            'last_updated': datetime.now(),
            'is_demo': True
        }
    
    def create_performance_charts(self, processed_data=None):
        """Crear gráficos de performance"""
        if processed_data is None:
            processed_data = self.processed_cache
        
        if not processed_data or 'combined_metrics' not in processed_data:
            processed_data = self._generate_demo_data()
        
        charts = {}
        
        try:
            # 1. Gráfico de Revenue por día
            charts['revenue_trend'] = self._create_revenue_trend_chart(processed_data)
            
            # 2. Gráfico de performance por canal
            charts['channel_performance'] = self._create_channel_performance_chart(processed_data)
            
            # 3. Gráfico de ROAS por canal
            charts['roas_comparison'] = self._create_roas_comparison_chart(processed_data)
            
            # 4. Gráfico de gasto vs revenue
            charts['spend_vs_revenue'] = self._create_spend_vs_revenue_chart(processed_data)
            
            # 5. Funnel de conversión
            charts['conversion_funnel'] = self._create_conversion_funnel_chart(processed_data)
            
            # Cachear gráficos
            self.chart_cache = charts
            
        except Exception as e:
            st.error(f"Error creando gráficos: {str(e)}")
            charts = self._create_demo_charts()
        
        return charts
    
    def _create_revenue_trend_chart(self, processed_data):
        """Crear gráfico de tendencia de revenue"""
        trends = processed_data['combined_metrics'].get('trends', {})
        daily_data = trends.get('daily_data')
        
        if daily_data is not None and not daily_data.empty:
            fig = px.line(
                daily_data, 
                x='date', 
                y='revenue',
                title='Tendencia de Revenue (30 días)',
                labels={'revenue': 'Revenue ($)', 'date': 'Fecha'}
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                title_font_size=16
            )
            
            # Agregar línea de tendencia
            fig.add_scatter(
                x=daily_data['date'],
                y=daily_data['revenue'].rolling(window=7).mean(),
                mode='lines',
                name='Tendencia (7 días)',
                line=dict(color='red', dash='dash')
            )
            
            return fig
        
        return None
    
    def _create_channel_performance_chart(self, processed_data):
        """Crear gráfico de performance por canal"""
        performance = processed_data['combined_metrics'].get('performance', {})
        channel_ranking = performance.get('channel_ranking', [])
        
        if channel_ranking:
            channels = [ch['channel'].title() for ch in channel_ranking]
            revenue = [ch['revenue'] for ch in channel_ranking]
            spend = [ch['spend'] for ch in channel_ranking]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Revenue',
                x=channels,
                y=revenue,
                marker_color='#28a745'
            ))
            
            fig.add_trace(go.Bar(
                name='Spend',
                x=channels,
                y=spend,
                marker_color='#dc3545'
            ))
            
            fig.update_layout(
                title='Revenue vs Spend por Canal',
                xaxis_title='Canal',
                yaxis_title='Monto ($)',
                barmode='group',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333')
            )
            
            return fig
        
        return None
    
    def _create_roas_comparison_chart(self, processed_data):
        """Crear gráfico de comparación de ROAS"""
        performance = processed_data['combined_metrics'].get('performance', {})
        channel_ranking = performance.get('channel_ranking', [])
        
        if channel_ranking:
            channels = [ch['channel'].title() for ch in channel_ranking]
            roas_values = [ch['roas'] for ch in channel_ranking]
            
            # Colores basados en performance
            colors = []
            for roas in roas_values:
                if roas >= 3.0:
                    colors.append('#28a745')  # Verde
                elif roas >= 2.0:
                    colors.append('#ffc107')  # Amarillo
                else:
                    colors.append('#dc3545')  # Rojo
            
            fig = go.Figure(data=[
                go.Bar(
                    x=channels,
                    y=roas_values,
                    marker_color=colors,
                    text=[f'{roas:.1f}x' for roas in roas_values],
                    textposition='outside'
                )
            ])
            
            fig.update_layout(
                title='ROAS por Canal',
                xaxis_title='Canal',
                yaxis_title='ROAS',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333')
            )
            
            # Agregar línea de objetivo (ROAS = 3.0)
            fig.add_hline(y=3.0, line_dash="dash", line_color="gray", 
                         annotation_text="Objetivo (3.0x)")
            
            return fig
        
        return None
    
    def _create_spend_vs_revenue_chart(self, processed_data):
        """Crear gráfico scatter de gasto vs revenue"""
        performance = processed_data['combined_metrics'].get('performance', {})
        channel_ranking = performance.get('channel_ranking', [])
        
        if channel_ranking:
            fig = px.scatter(
                x=[ch['spend'] for ch in channel_ranking],
                y=[ch['revenue'] for ch in channel_ranking],
                color=[ch['roas'] for ch in channel_ranking],
                size=[ch['spend'] for ch in channel_ranking],
                hover_name=[ch['channel'].title() for ch in channel_ranking],
                labels={'x': 'Spend ($)', 'y': 'Revenue ($)', 'color': 'ROAS'},
                title='Relación Spend vs Revenue por Canal',
                color_continuous_scale='RdYlGn'
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333')
            )
            
            return fig
        
        return None
    
    def _create_conversion_funnel_chart(self, processed_data):
        """Crear gráfico de funnel de conversión"""
        overview = processed_data['combined_metrics'].get('overview', {})
        
        # Simular datos de funnel
        impressions = overview.get('total_impressions', 100000)
        clicks = overview.get('total_clicks', 5000)
        conversions = overview.get('total_conversions', 250)
        
        stages = ['Impresiones', 'Clics', 'Conversiones']
        values = [impressions, clicks, conversions]
        
        fig = go.Figure(go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial",
            marker={"color": ["#3498db", "#f39c12", "#e74c3c"]}
        ))
        
        fig.update_layout(
            title='Funnel de Conversión',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333')
        )
        
        return fig
    
    def _create_demo_charts(self):
        """Crear gráficos demo"""
        demo_data = self._generate_demo_data()
        return self.create_performance_charts(demo_data)
    
    def get_kpi_metrics(self, processed_data=None):
        """Obtener métricas KPI principales"""
        if processed_data is None:
            processed_data = self.processed_cache
        
        if not processed_data or 'combined_metrics' not in processed_data:
            processed_data = self._generate_demo_data()
        
        overview = processed_data['combined_metrics'].get('overview', {})
        trends = processed_data['combined_metrics'].get('trends', {})
        
        kpis = {
            'total_revenue': {
                'value': overview.get('total_revenue', 0),
                'format': 'currency',
                'trend': trends.get('revenue_trend', {}).get('percentage', 0),
                'label': 'Revenue Total'
            },
            'total_spend': {
                'value': overview.get('total_spend', 0),
                'format': 'currency',
                'trend': trends.get('spend_trend', {}).get('percentage', 0),
                'label': 'Gasto Publicitario'
            },
            'overall_roas': {
                'value': overview.get('overall_roas', 0),
                'format': 'multiplier',
                'trend': self._calculate_roas_trend(trends),
                'label': 'ROAS Promedio'
            },
            'total_conversions': {
                'value': overview.get('total_conversions', 0),
                'format': 'number',
                'trend': trends.get('conversions_trend', {}).get('percentage', 0),
                'label': 'Conversiones Totales'
            },
            'overall_ctr': {
                'value': overview.get('overall_ctr', 0),
                'format': 'percentage',
                'trend': 0,  # Calcular si es necesario
                'label': 'CTR Promedio'
            },
            'overall_conversion_rate': {
                'value': overview.get('overall_conversion_rate', 0),
                'format': 'percentage',
                'trend': 0,  # Calcular si es necesario
                'label': 'Tasa de Conversión'
            }
        }
        
        return kpis
    
    def _calculate_roas_trend(self, trends):
        """Calcular tendencia de ROAS"""
        revenue_trend = trends.get('revenue_trend', {})
        spend_trend = trends.get('spend_trend', {})
        
        if revenue_trend and spend_trend:
            revenue_pct = revenue_trend.get('percentage', 0)
            spend_pct = spend_trend.get('percentage', 0)
            
            # Aproximación de la tendencia de ROAS
            if spend_pct != 0:
                return round(revenue_pct - spend_pct, 1)
        
        return 0
    
    def export_processed_data(self, format='excel'):
        """Exportar datos procesados"""
        if not self.processed_cache:
            return None
        
        try:
            if format == 'excel':
                # Crear archivo Excel con múltiples hojas
                with pd.ExcelWriter('marketing_data_export.xlsx', engine='openpyxl') as writer:
                    # Hoja de resumen
                    overview_df = pd.DataFrame([self.processed_cache['combined_metrics']['overview']])
                    overview_df.to_excel(writer, sheet_name='Resumen', index=False)
                    
                    # Hojas por fuente de datos
                    for source, data in self.processed_cache['raw_data'].items():
                        if data is not None and not data.empty:
                            data.to_excel(writer, sheet_name=source.title(), index=False)
                
                return 'marketing_data_export.xlsx'
            
            elif format == 'csv':
                # Combinar todos los datos en un CSV
                all_data = []
                for source, data in self.processed_cache['raw_data'].items():
                    if data is not None and not data.empty:
                        data_copy = data.copy()
                        data_copy['data_source'] = source
                        all_data.append(data_copy)
                
                if all_data:
                    combined_df = pd.concat(all_data, ignore_index=True)
                    combined_df.to_csv('marketing_data_export.csv', index=False)
                    return 'marketing_data_export.csv'
            
        except Exception as e:
            st.error(f"Error exportando datos: {str(e)}")
        
        return None
    
    def get_data_quality_report(self):
        """Generar reporte de calidad de datos"""
        if not self.processed_cache:
            return None
        
        quality_report = {
            'total_sources': len(self.processed_cache['raw_data']),
            'active_sources': 0,
            'data_completeness': {},
            'data_issues': [],
            'recommendations': []
        }
        
        for source, data in self.processed_cache['raw_data'].items():
            if data is not None and not data.empty:
                quality_report['active_sources'] += 1
                
                # Analizar completitud de datos
                missing_percentage = (data.isnull().sum() / len(data)) * 100
                quality_report['data_completeness'][source] = {
                    'total_records': len(data),
                    'missing_data_percentage': round(missing_percentage.mean(), 1),
                    'date_range': f"{data['date'].min()} - {data['date'].max()}" if 'date' in data.columns else 'N/A'
                }
                
                # Identificar problemas de datos
                if missing_percentage.mean() > 20:
                    quality_report['data_issues'].append(f"{source}: Alto porcentaje de datos faltantes ({missing_percentage.mean():.1f}%)")
                
                if len(data) < 7:
                    quality_report['data_issues'].append(f"{source}: Datos insuficientes para análisis de tendencias")
        
        # Generar recomendaciones
        if quality_report['active_sources'] < 3:
            quality_report['recommendations'].append("Conectar más fuentes de datos para obtener una vista más completa")
        
        if quality_report['data_issues']:
            quality_report['recommendations'].append("Revisar la calidad de los datos y completar información faltante")
        
        quality_report['overall_score'] = min(100, (quality_report['active_sources'] / 5) * 100 - len(quality_report['data_issues']) * 10)
        
        return quality_report