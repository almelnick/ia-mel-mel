# utils/ai_analyzer.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class AIAnalyzer:
    def __init__(self):
        self.insights_cache = {}
        self.last_analysis = None
    
    def analyze_performance_data(self, data_sources):
        """Analizar datos de performance de múltiples fuentes"""
        try:
            # Combinar datos de todas las fuentes
            combined_metrics = self._combine_data_sources(data_sources)
            
            if not combined_metrics:
                return self._generate_demo_insights()
            
            # Generar insights
            insights = {
                'performance_insights': self._analyze_performance_trends(combined_metrics),
                'optimization_opportunities': self._identify_optimization_opportunities(combined_metrics),
                'scaling_recommendations': self._generate_scaling_recommendations(combined_metrics),
                'creative_insights': self._analyze_creative_performance(combined_metrics),
                'audience_insights': self._analyze_audience_performance(combined_metrics),
                'budget_recommendations': self._analyze_budget_allocation(combined_metrics),
                'anomaly_alerts': self._detect_anomalies(combined_metrics),
                'predictive_insights': self._generate_predictive_insights(combined_metrics)
            }
            
            # Cachear resultados
            self.insights_cache = insights
            self.last_analysis = datetime.now()
            
            return insights
            
        except Exception as e:
            st.error(f"Error en análisis IA: {str(e)}")
            return self._generate_demo_insights()
    
    def _combine_data_sources(self, data_sources):
        """Combinar datos de múltiples fuentes en métricas unificadas"""
        combined = {
            'total_spend': 0,
            'total_revenue': 0,
            'total_impressions': 0,
            'total_clicks': 0,
            'total_conversions': 0,
            'channels': {},
            'trends': {},
            'demographics': {}
        }
        
        for source_name, source_data in data_sources.items():
            if source_data and not source_data.empty:
                # Extraer métricas relevantes según la fuente
                if source_name == 'meta_ads':
                    combined['total_spend'] += source_data.get('spend', 0).sum() if 'spend' in source_data.columns else 0
                    combined['total_impressions'] += source_data.get('impressions', 0).sum() if 'impressions' in source_data.columns else 0
                    combined['total_clicks'] += source_data.get('clicks', 0).sum() if 'clicks' in source_data.columns else 0
                    combined['channels']['meta'] = self._extract_channel_metrics(source_data, 'meta')
                
                elif source_name == 'google_ads':
                    combined['total_spend'] += source_data.get('cost', 0).sum() if 'cost' in source_data.columns else 0
                    combined['total_clicks'] += source_data.get('clicks', 0).sum() if 'clicks' in source_data.columns else 0
                    combined['channels']['google'] = self._extract_channel_metrics(source_data, 'google')
                
                elif source_name in ['shopify', 'woocommerce']:
                    combined['total_revenue'] += source_data.get('revenue', 0).sum() if 'revenue' in source_data.columns else 0
                    combined['total_conversions'] += source_data.get('orders', 0).sum() if 'orders' in source_data.columns else 0
                
                elif source_name in ['klaviyo', 'mailchimp', 'mailerlite']:
                    email_revenue = source_data.get('revenue', 0).sum() if 'revenue' in source_data.columns else 0
                    combined['total_revenue'] += email_revenue
                    combined['channels']['email'] = self._extract_channel_metrics(source_data, 'email')
        
        return combined
    
    def _extract_channel_metrics(self, data, channel_type):
        """Extraer métricas específicas por canal"""
        metrics = {'channel': channel_type}
        
        if channel_type == 'meta':
            metrics.update({
                'spend': data.get('spend', 0).sum() if 'spend' in data.columns else 0,
                'impressions': data.get('impressions', 0).sum() if 'impressions' in data.columns else 0,
                'clicks': data.get('clicks', 0).sum() if 'clicks' in data.columns else 0,
                'ctr': data.get('ctr', 0).mean() if 'ctr' in data.columns else 0,
                'cpc': data.get('cpc', 0).mean() if 'cpc' in data.columns else 0,
                'roas': data.get('roas', 0).mean() if 'roas' in data.columns else 0
            })
        elif channel_type == 'google':
            metrics.update({
                'spend': data.get('cost', 0).sum() if 'cost' in data.columns else 0,
                'clicks': data.get('clicks', 0).sum() if 'clicks' in data.columns else 0,
                'impressions': data.get('impressions', 0).sum() if 'impressions' in data.columns else 0,
                'ctr': data.get('ctr', 0).mean() if 'ctr' in data.columns else 0,
                'cpc': data.get('cpc', 0).mean() if 'cpc' in data.columns else 0
            })
        elif channel_type == 'email':
            metrics.update({
                'emails_sent': data.get('emails_sent', 0).sum() if 'emails_sent' in data.columns else 0,
                'open_rate': data.get('open_rate', 0).mean() if 'open_rate' in data.columns else 0,
                'click_rate': data.get('click_rate', 0).mean() if 'click_rate' in data.columns else 0,
                'revenue': data.get('revenue', 0).sum() if 'revenue' in data.columns else 0
            })
        
        return metrics
    
    def _analyze_performance_trends(self, combined_metrics):
        """Analizar tendencias de performance"""
        insights = []
        
        # Calcular ROAS general
        total_spend = combined_metrics.get('total_spend', 0)
        total_revenue = combined_metrics.get('total_revenue', 0)
        
        if total_spend > 0:
            roas = total_revenue / total_spend
            
            if roas > 4.0:
                insights.append({
                    'type': 'positive',
                    'title': 'ROAS Excelente',
                    'description': f'Tu ROAS de {roas:.1f}x está por encima del benchmark de la industria (3.0x)',
                    'impact': 'alto',
                    'action': 'Considera escalar las campañas con mejor performance'
                })
            elif roas > 2.0:
                insights.append({
                    'type': 'neutral',
                    'title': 'ROAS Saludable',
                    'description': f'Tu ROAS de {roas:.1f}x está en rango aceptable',
                    'impact': 'medio',
                    'action': 'Busca oportunidades de optimización para mejorarlo'
                })
            else:
                insights.append({
                    'type': 'warning',
                    'title': 'ROAS Bajo',
                    'description': f'Tu ROAS de {roas:.1f}x está por debajo del objetivo (2.0x)',
                    'impact': 'alto',
                    'action': 'Revisa segmentación de audiencias y creativos'
                })
        
        # Analizar distribución de canales
        channels = combined_metrics.get('channels', {})
        if len(channels) > 1:
            best_channel = max(channels.items(), key=lambda x: x[1].get('roas', 0))
            insights.append({
                'type': 'info',
                'title': f'Mejor Canal: {best_channel[0].title()}',
                'description': f'El canal {best_channel[0]} está generando el mejor ROAS',
                'impact': 'medio',
                'action': f'Considera redistribuir presupuesto hacia {best_channel[0]}'
            })
        
        return insights
    
    def _identify_optimization_opportunities(self, combined_metrics):
        """Identificar oportunidades de optimización"""
        opportunities = []
        
        channels = combined_metrics.get('channels', {})
        
        for channel_name, channel_data in channels.items():
            if channel_name == 'meta':
                ctr = channel_data.get('ctr', 0)
                cpc = channel_data.get('cpc', 0)
                
                if ctr < 2.0:  # CTR bajo
                    opportunities.append({
                        'channel': 'Meta Ads',
                        'type': 'creative_optimization',
                        'priority': 'alta',
                        'title': 'Optimizar Creativos de Meta',
                        'description': f'CTR de {ctr:.1f}% está por debajo del benchmark (2.5%)',
                        'potential_impact': '+25% en CTR',
                        'actions': [
                            'Probar nuevos formatos de video',
                            'A/B testear headlines',
                            'Actualizar imágenes de producto',
                            'Revisar copy de anuncios'
                        ]
                    })
                
                if cpc > 2.0:  # CPC alto
                    opportunities.append({
                        'channel': 'Meta Ads',
                        'type': 'audience_optimization',
                        'priority': 'media',
                        'title': 'Optimizar Audiencias de Meta',
                        'description': f'CPC de ${cpc:.2f} es superior al benchmark ($1.50)',
                        'potential_impact': '-20% en CPC',
                        'actions': [
                            'Refinar targeting de intereses',
                            'Excluir audiencias con bajo rendimiento',
                            'Probar lookalike audiences',
                            'Ajustar pujas automáticas'
                        ]
                    })
            
            elif channel_name == 'email':
                open_rate = channel_data.get('open_rate', 0)
                click_rate = channel_data.get('click_rate', 0)
                
                if open_rate < 20:
                    opportunities.append({
                        'channel': 'Email Marketing',
                        'type': 'deliverability_optimization',
                        'priority': 'media',
                        'title': 'Mejorar Open Rate de Emails',
                        'description': f'Open rate de {open_rate:.1f}% está por debajo del promedio (22%)',
                        'potential_impact': '+15% en Open Rate',
                        'actions': [
                            'Optimizar líneas de asunto',
                            'Segmentar mejor las listas',
                            'Limpiar listas inactivas',
                            'Probar diferentes horarios de envío'
                        ]
                    })
        
        return opportunities
    
    def _generate_scaling_recommendations(self, combined_metrics):
        """Generar recomendaciones para escalar"""
        recommendations = []
        
        total_spend = combined_metrics.get('total_spend', 0)
        total_revenue = combined_metrics.get('total_revenue', 0)
        channels = combined_metrics.get('channels', {})
        
        if total_spend > 0:
            roas = total_revenue / total_spend
            
            # Identificar campañas/canales para escalar
            for channel_name, channel_data in channels.items():
                channel_roas = channel_data.get('roas', 0)
                channel_spend = channel_data.get('spend', 0)
                
                if channel_roas > 3.0 and channel_spend > 500:  # Buen ROAS y volumen significativo
                    recommendations.append({
                        'type': 'scale_up',
                        'channel': channel_name.title(),
                        'priority': 'alta',
                        'title': f'Escalar {channel_name.title()}',
                        'current_roas': channel_roas,
                        'current_spend': channel_spend,
                        'recommended_action': f'Incrementar presupuesto en 50-100%',
                        'expected_impact': f'Potencial de +{channel_spend * 0.75:.0f} en revenue adicional',
                        'risk_level': 'bajo',
                        'timeline': '1-2 semanas'
                    })
                
                elif channel_roas < 1.5:  # ROAS muy bajo
                    recommendations.append({
                        'type': 'scale_down',
                        'channel': channel_name.title(),
                        'priority': 'alta',
                        'title': f'Reducir Inversión en {channel_name.title()}',
                        'current_roas': channel_roas,
                        'current_spend': channel_spend,
                        'recommended_action': 'Pausar o reducir presupuesto 70%',
                        'expected_impact': f'Ahorrar ${channel_spend * 0.7:.0f} en gasto ineficiente',
                        'risk_level': 'bajo',
                        'timeline': 'Inmediato'
                    })
        
        return recommendations
    
    def _analyze_creative_performance(self, combined_metrics):
        """Analizar performance de creativos"""
        creative_insights = []
        
        # Simular análisis de creativos con datos demo
        creative_types = [
            {
                'type': 'Video Carousel',
                'performance': 'alto',
                'ctr': 4.2,
                'cpc': 1.35,
                'recommendation': 'Crear más creativos de este tipo'
            },
            {
                'type': 'critical',
                'metric': 'Conversion Rate',
                'channel': 'Google Ads',
                'description': 'Tasa de conversión cayó 25% ayer',
                'impact': 'alto',
                'recommendation': 'Verificar landing pages y tracking'
            },
            {
                'type': 'positive',
                'metric': 'ROAS',
                'channel': 'Email Marketing',
                'description': 'ROAS de email aumentó 60% esta semana',
                'impact': 'alto',
                'recommendation': 'Analizar qué cambió para replicar'
            }
        ]
        
        for anomaly in anomalies:
            alerts.append({
                'alert_type': anomaly['type'],
                'metric_affected': anomaly['metric'],
                'channel': anomaly['channel'],
                'description': anomaly['description'],
                'impact_level': anomaly['impact'],
                'recommended_action': anomaly['recommendation'],
                'detected_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'urgency': 'high' if anomaly['type'] == 'critical' else 'medium'
            })
        
        return alerts
    
    def _generate_predictive_insights(self, combined_metrics):
        """Generar insights predictivos"""
        predictions = []
        
        total_spend = combined_metrics.get('total_spend', 0)
        total_revenue = combined_metrics.get('total_revenue', 0)
        
        if total_spend > 0:
            current_roas = total_revenue / total_spend
            
            # Predicciones de performance
            predictions.append({
                'type': 'revenue_forecast',
                'title': 'Proyección de Revenue - Próximos 30 días',
                'current_value': total_revenue,
                'predicted_value': total_revenue * 1.15,  # 15% crecimiento proyectado
                'confidence': 78,
                'factors': [
                    'Tendencia histórica positiva',
                    'Optimizaciones recientes',
                    'Seasonality favorable'
                ]
            })
            
            predictions.append({
                'type': 'efficiency_forecast',
                'title': 'Proyección de ROAS - Próximas 2 semanas',
                'current_value': current_roas,
                'predicted_value': current_roas * 1.08,  # 8% mejora proyectada
                'confidence': 65,
                'factors': [
                    'Optimizaciones de audiencias',
                    'Nuevos creativos en testing',
                    'Pausar campañas con bajo rendimiento'
                ]
            })
        
        # Predicciones por canal
        channels = combined_metrics.get('channels', {})
        for channel_name, channel_data in channels.items():
            channel_roas = channel_data.get('roas', 0)
            if channel_roas > 0:
                predictions.append({
                    'type': 'channel_forecast',
                    'title': f'Proyección {channel_name.title()} - 7 días',
                    'channel': channel_name,
                    'current_roas': channel_roas,
                    'predicted_roas': channel_roas * np.random.uniform(0.95, 1.12),
                    'confidence': np.random.randint(60, 85),
                    'trend': 'up' if np.random.random() > 0.4 else 'stable'
                })
        
        return predictions
    
    def _generate_demo_insights(self):
        """Generar insights demo cuando no hay datos reales"""
        return {
            'performance_insights': [
                {
                    'type': 'positive',
                    'title': 'Performance General Sólido',
                    'description': 'ROAS promedio de 3.2x está por encima del benchmark',
                    'impact': 'alto',
                    'action': 'Mantener estrategia actual y buscar oportunidades de escalado'
                },
                {
                    'type': 'neutral',
                    'title': 'Distribución de Canales Balanceada',
                    'description': 'Meta Ads (45%), Google Ads (35%), Email (20%)',
                    'impact': 'medio',
                    'action': 'Considerar redistribuir hacia canales de mejor performance'
                }
            ],
            'optimization_opportunities': [
                {
                    'channel': 'Meta Ads',
                    'type': 'creative_optimization',
                    'priority': 'alta',
                    'title': 'Optimizar Creativos de Video',
                    'description': 'Los videos superan a las imágenes estáticas en 40%',
                    'potential_impact': '+25% en CTR',
                    'actions': [
                        'Crear más videos cortos (15-30s)',
                        'Probar formatos UGC',
                        'Incluir captions automáticos',
                        'Testear diferentes hooks en los primeros 3s'
                    ]
                },
                {
                    'channel': 'Google Ads',
                    'type': 'keyword_optimization',
                    'priority': 'media',
                    'title': 'Expandir Keywords de Alto Rendimiento',
                    'description': 'Keywords long-tail muestran 35% mejor conversión',
                    'potential_impact': '+20% en conversiones',
                    'actions': [
                        'Investigar variaciones de keywords exitosas',
                        'Agregar negative keywords',
                        'Probar match types más específicos',
                        'Optimizar ad extensions'
                    ]
                }
            ],
            'scaling_recommendations': [
                {
                    'type': 'scale_up',
                    'channel': 'Meta Ads',
                    'priority': 'alta',
                    'title': 'Escalar Campaña Premium',
                    'current_roas': 4.1,
                    'current_spend': 1200,
                    'recommended_action': 'Incrementar presupuesto en 75%',
                    'expected_impact': 'Potencial de +$2,100 en revenue adicional',
                    'risk_level': 'bajo',
                    'timeline': '1-2 semanas'
                },
                {
                    'type': 'scale_down',
                    'channel': 'Google Display',
                    'priority': 'media',
                    'title': 'Reducir Display Network',
                    'current_roas': 1.8,
                    'current_spend': 600,
                    'recommended_action': 'Reducir presupuesto 50%',
                    'expected_impact': 'Ahorrar $300 para redistribuir',
                    'risk_level': 'bajo',
                    'timeline': 'Inmediato'
                }
            ],
            'creative_insights': [
                {
                    'creative_type': 'Video Carousel',
                    'performance_level': 'alto',
                    'metrics': {'ctr': 4.2, 'cpc': 1.35},
                    'recommendation': 'Crear más creativos de este formato',
                    'priority': 'alta'
                },
                {
                    'creative_type': 'UGC Videos',
                    'performance_level': 'alto',
                    'metrics': {'ctr': 3.8, 'cpc': 1.52},
                    'recommendation': 'Solicitar más contenido de usuarios',
                    'priority': 'alta'
                },
                {
                    'creative_type': 'Imagen + Texto',
                    'performance_level': 'bajo',
                    'metrics': {'ctr': 1.1, 'cpc': 3.21},
                    'recommendation': 'Revisar diseño y copy',
                    'priority': 'media'
                }
            ],
            'audience_insights': [
                {
                    'audience_name': 'Lookalike 1% - Compradores VIP',
                    'performance_rating': 'excelente',
                    'roas': 4.8,
                    'spend_percentage': 35,
                    'recommendation': 'Escalar presupuesto +50%',
                    'action_priority': 'alta'
                },
                {
                    'audience_name': 'Retargeting - Cart Abandoners',
                    'performance_rating': 'bueno',
                    'roas': 3.6,
                    'spend_percentage': 25,
                    'recommendation': 'Crear secuencias más personalizadas',
                    'action_priority': 'media'
                },
                {
                    'audience_name': 'Cold Audience - Intereses Amplios',
                    'performance_rating': 'regular',
                    'roas': 2.3,
                    'spend_percentage': 40,
                    'recommendation': 'Refinar targeting y creativos',
                    'action_priority': 'alta'
                }
            ],
            'budget_recommendations': [
                {
                    'channel': 'Meta Ads',
                    'current_allocation': 45.0,
                    'recommended_allocation': 55.0,
                    'change': 10.0,
                    'reason': 'ROAS excelente - incrementar inversión',
                    'priority': 'alta'
                },
                {
                    'channel': 'Google Ads',
                    'current_allocation': 35.0,
                    'recommended_allocation': 30.0,
                    'change': -5.0,
                    'reason': 'ROAS saludable - redistribuir parcialmente',
                    'priority': 'media'
                },
                {
                    'channel': 'Email Marketing',
                    'current_allocation': 20.0,
                    'recommended_allocation': 15.0,
                    'change': -5.0,
                    'reason': 'Eficiente pero menor volumen',
                    'priority': 'baja'
                }
            ],
            'anomaly_alerts': [
                {
                    'alert_type': 'warning',
                    'metric_affected': 'CPC',
                    'channel': 'Meta Ads',
                    'description': 'CPC incrementó 35% en los últimos 2 días',
                    'impact_level': 'medio',
                    'recommended_action': 'Revisar pujas y competencia en Black Friday',
                    'detected_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'urgency': 'medium'
                },
                {
                    'alert_type': 'positive',
                    'metric_affected': 'Open Rate',
                    'channel': 'Email Marketing',
                    'description': 'Open rate aumentó 28% después de optimización de subject lines',
                    'impact_level': 'alto',
                    'recommended_action': 'Documentar elementos exitosos para replicar',
                    'detected_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'urgency': 'low'
                }
            ],
            'predictive_insights': [
                {
                    'type': 'revenue_forecast',
                    'title': 'Proyección de Revenue - Próximos 30 días',
                    'current_value': 45280,
                    'predicted_value': 52072,
                    'confidence': 78,
                    'factors': [
                        'Optimizaciones de campaña implementadas',
                        'Seasonality de holidays favorable',
                        'Nuevo producto con alta demanda'
                    ]
                },
                {
                    'type': 'efficiency_forecast',
                    'title': 'Proyección de ROAS - Próximas 2 semanas',
                    'current_value': 3.2,
                    'predicted_value': 3.6,
                    'confidence': 72,
                    'factors': [
                        'Mejoras en segmentación de audiencias',
                        'Nuevos creativos con mejor CTR',
                        'Pausa de campañas underperforming'
                    ]
                }
            ]
        }
    
    def get_actionable_recommendations(self, priority_filter=None):
        """Obtener recomendaciones accionables filtradas por prioridad"""
        if not self.insights_cache:
            return []
        
        recommendations = []
        
        # Recopilar recomendaciones de todas las secciones
        for section_name, section_data in self.insights_cache.items():
            if isinstance(section_data, list):
                for item in section_data:
                    if isinstance(item, dict):
                        priority = item.get('priority', 'media')
                        if priority_filter is None or priority == priority_filter:
                            recommendations.append({
                                'section': section_name,
                                'priority': priority,
                                'title': item.get('title', ''),
                                'description': item.get('description', ''),
                                'action': item.get('action', item.get('recommended_action', '')),
                                'impact': item.get('impact', item.get('potential_impact', '')),
                                'channel': item.get('channel', 'General')
                            })
        
        # Ordenar por prioridad
        priority_order = {'alta': 0, 'media': 1, 'baja': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 2))
        
        return recommendations
    
    def generate_executive_summary(self):
        """Generar resumen ejecutivo de insights"""
        if not self.insights_cache:
            insights = self._generate_demo_insights()
        else:
            insights = self.insights_cache
        
        # Contar insights por tipo
        positive_insights = sum(1 for insight in insights.get('performance_insights', []) 
                              if insight.get('type') == 'positive')
        opportunities = len(insights.get('optimization_opportunities', []))
        critical_alerts = sum(1 for alert in insights.get('anomaly_alerts', []) 
                            if alert.get('alert_type') == 'critical')
        
        # Calcular scores
        performance_score = min(100, (positive_insights * 20) + 60)
        opportunity_score = min(100, opportunities * 15)
        health_score = max(0, 100 - (critical_alerts * 25))
        
        summary = {
            'overall_score': round((performance_score + opportunity_score + health_score) / 3),
            'performance_score': performance_score,
            'opportunity_score': opportunity_score,
            'health_score': health_score,
            'key_metrics': {
                'total_opportunities': opportunities,
                'critical_alerts': critical_alerts,
                'scaling_recommendations': len(insights.get('scaling_recommendations', []))
            },
            'top_priorities': self.get_actionable_recommendations('alta')[:3],
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return summary
    
    def export_insights_report(self, format='json'):
        """Exportar reporte completo de insights"""
        if not self.insights_cache:
            insights = self._generate_demo_insights()
        else:
            insights = self.insights_cache
        
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'analysis_period': '30 days',
                'data_sources': ['Meta Ads', 'Google Ads', 'Email Marketing', 'E-commerce'],
                'ai_model': 'Marketing Intelligence v2.1'
            },
            'executive_summary': self.generate_executive_summary(),
            'detailed_insights': insights,
            'actionable_recommendations': self.get_actionable_recommendations()
        }
        
        if format == 'json':
            return json.dumps(report, indent=2, default=str)
        elif format == 'dict':
            return report
        
        return report
            {
                'type': 'Imagen Estática',
                'performance': 'medio',
                'ctr': 2.1,
                'cpc': 2.15,
                'recommendation': 'Optimizar copy y call-to-action'
            },
            {
                'type': 'Video Single',
                'performance': 'bajo',
                'ctr': 1.3,
                'cpc': 3.45,
                'recommendation': 'Considerar pausar o rediseñar'
            }
        ]
        
        for creative in creative_types:
            creative_insights.append({
                'creative_type': creative['type'],
                'performance_level': creative['performance'],
                'metrics': {
                    'ctr': creative['ctr'],
                    'cpc': creative['cpc']
                },
                'recommendation': creative['recommendation'],
                'priority': 'alta' if creative['performance'] in ['alto', 'bajo'] else 'media'
            })
        
        return creative_insights
    
    def _analyze_audience_performance(self, combined_metrics):
        """Analizar performance de audiencias"""
        audience_insights = []
        
        # Simullar insights de audiencias
        audiences = [
            {
                'name': 'Lookalike 1% - Compradores',
                'performance': 'excelente',
                'roas': 4.8,
                'spend_share': 35,
                'recommendation': 'Escalar presupuesto +50%'
            },
            {
                'name': 'Intereses - Tecnología',
                'performance': 'bueno',
                'roas': 3.2,
                'spend_share': 25,
                'recommendation': 'Mantener y optimizar creativos'
            },
            {
                'name': 'Retargeting - Visitantes Web',
                'performance': 'regular',
                'roas': 2.1,
                'spend_share': 20,
                'recommendation': 'Segmentar por tiempo de visita'
            },
            {
                'name': 'Broad Targeting',
                'performance': 'bajo',
                'roas': 1.4,
                'spend_share': 20,
                'recommendation': 'Pausar y redistribuir presupuesto'
            }
        ]
        
        for audience in audiences:
            audience_insights.append({
                'audience_name': audience['name'],
                'performance_rating': audience['performance'],
                'roas': audience['roas'],
                'spend_percentage': audience['spend_share'],
                'recommendation': audience['recommendation'],
                'action_priority': 'alta' if audience['performance'] in ['excelente', 'bajo'] else 'media'
            })
        
        return audience_insights
    
    def _analyze_budget_allocation(self, combined_metrics):
        """Analizar distribución de presupuesto"""
        budget_recommendations = []
        
        channels = combined_metrics.get('channels', {})
        total_spend = sum(channel.get('spend', 0) for channel in channels.values())
        
        if total_spend > 0:
            for channel_name, channel_data in channels.items():
                channel_spend = channel_data.get('spend', 0)
                channel_roas = channel_data.get('roas', 0)
                current_allocation = (channel_spend / total_spend) * 100
                
                # Calcular asignación recomendada basada en ROAS
                if channel_roas > 3.5:
                    recommended_allocation = min(current_allocation * 1.5, 60)  # Máximo 60%
                elif channel_roas > 2.0:
                    recommended_allocation = current_allocation * 1.1
                else:
                    recommended_allocation = current_allocation * 0.7
                
                budget_recommendations.append({
                    'channel': channel_name.title(),
                    'current_allocation': round(current_allocation, 1),
                    'recommended_allocation': round(recommended_allocation, 1),
                    'change': round(recommended_allocation - current_allocation, 1),
                    'reason': self._get_allocation_reason(channel_roas),
                    'priority': 'alta' if abs(recommended_allocation - current_allocation) > 10 else 'media'
                })
        
        return budget_recommendations
    
    def _get_allocation_reason(self, roas):
        """Obtener razón para cambio de asignación"""
        if roas > 3.5:
            return 'ROAS excelente - incrementar inversión'
        elif roas > 2.0:
            return 'ROAS saludable - mantener o incrementar ligeramente'
        else:
            return 'ROAS bajo - reducir inversión'
    
    def _detect_anomalies(self, combined_metrics):
        """Detectar anomalías en los datos"""
        alerts = []
        
        # Simular detección de anomalías
        anomalies = [
            {
                'type': 'warning',
                'metric': 'CPC',
                'channel': 'Meta Ads',
                'description': 'CPC incrementó 45% en los últimos 3 días',
                'impact': 'medio',
                'recommendation': 'Revisar pujas y competencia'