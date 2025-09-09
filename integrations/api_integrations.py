# api_integrations.py - Funciones para conectar con APIs reales

import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# ==== META ADS (FACEBOOK/INSTAGRAM) ====
def connect_meta_ads():
    """Conectar con Meta Ads API"""
    try:
        from facebook_business.api import FacebookAdsApi
        from facebook_business.adobjects.adaccount import AdAccount
        from facebook_business.adobjects.adsinsights import AdsInsights
        
        # Credenciales desde configuración
        config = st.session_state.user_config
        app_id = config.get('Meta Ads (Facebook/Instagram)_app_id')
        app_secret = config.get('Meta Ads (Facebook/Instagram)_secret')
        access_token = config.get('Meta Ads (Facebook/Instagram)_token')
        ad_account_id = config.get('Meta Ads (Facebook/Instagram)_account')
        
        # Inicializar API
        FacebookAdsApi.init(app_id, app_secret, access_token)
        
        # Obtener datos de la cuenta publicitaria
        account = AdAccount(ad_account_id)
        
        # Obtener insights de los últimos 30 días
        insights = account.get_insights(
            fields=[
                AdsInsights.Field.spend,
                AdsInsights.Field.impressions,
                AdsInsights.Field.clicks,
                AdsInsights.Field.ctr,
                AdsInsights.Field.cpc,
                AdsInsights.Field.actions
            ],
            params={
                'time_range': {
                    'since': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                    'until': datetime.now().strftime('%Y-%m-%d')
                },
                'level': 'campaign'
            }
        )
        
        # Convertir a DataFrame
        data = []
        for insight in insights:
            data.append({
                'campaign_id': insight.get('campaign_id'),
                'spend': float(insight.get('spend', 0)),
                'impressions': int(insight.get('impressions', 0)),
                'clicks': int(insight.get('clicks', 0)),
                'ctr': float(insight.get('ctr', 0)),
                'cpc': float(insight.get('cpc', 0))
            })
        
        return pd.DataFrame(data)
        
    except ImportError:
        st.error("Por favor instala: pip install facebook-business")
        return None
    except Exception as e:
        st.error(f"Error conectando con Meta Ads: {e}")
        return None

# ==== GOOGLE ADS ====
def connect_google_ads():
    """Conectar con Google Ads API"""
    try:
        from google.ads.googleads.client import GoogleAdsClient
        
        config = st.session_state.user_config
        
        # Configuración de Google Ads
        google_ads_config = {
            'developer_token': 'YOUR_DEVELOPER_TOKEN',
            'client_id': config.get('Google Ads_client_id'),
            'client_secret': config.get('Google Ads_client_secret'),
            'refresh_token': config.get('Google Ads_refresh_token'),
            'customer_id': config.get('Google Ads_customer_id')
        }
        
        # Inicializar cliente
        client = GoogleAdsClient.load_from_dict(google_ads_config)
        
        # Query GAQL para obtener datos de campaña
        query = """
        SELECT
            campaign.id,
            campaign.name,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.ctr,
            metrics.average_cpc
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
        """
        
        ga_service = client.get_service("GoogleAdsService")
        response = ga_service.search(
            customer_id=google_ads_config['customer_id'],
            query=query
        )
        
        # Procesar respuesta
        data = []
        for row in response:
            data.append({
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'impressions': row.metrics.impressions,
                'clicks': row.metrics.clicks,
                'cost': row.metrics.cost_micros / 1_000_000,  # Convertir de micros
                'ctr': row.metrics.ctr,
                'avg_cpc': row.metrics.average_cpc / 1_000_000
            })
        
        return pd.DataFrame(data)
        
    except ImportError:
        st.error("Por favor instala: pip install google-ads")
        return None
    except Exception as e:
        st.error(f"Error conectando con Google Ads: {e}")
        return None

# ==== SHOPIFY ====
def connect_shopify():
    """Conectar con Shopify API"""
    try:
        import shopify
        
        config = st.session_state.user_config
        shop_domain = config.get('Shopify_domain')
        api_token = config.get('Shopify_token')
        
        # Configurar sesión de Shopify
        shop_url = f"https://{api_token}@{shop_domain}"
        shopify.ShopifyResource.set_site(shop_url)
        
        # Obtener órdenes de los últimos 30 días
        orders = shopify.Order.find(
            status='any',
            created_at_min=(datetime.now() - timedelta(days=30)).isoformat(),
            limit=250
        )
        
        # Procesar órdenes
        data = []
        for order in orders:
            data.append({
                'order_id': order.id,
                'order_number': order.order_number,
                'total_price': float(order.total_price),
                'created_at': order.created_at,
                'customer_id': order.customer.id if order.customer else None,
                'line_items_count': len(order.line_items)
            })
        
        return pd.DataFrame(data)
        
    except ImportError:
        st.error("Por favor instala: pip install ShopifyAPI")
        return None
    except Exception as e:
        st.error(f"Error conectando con Shopify: {e}")
        return None

# ==== GOOGLE ANALYTICS ====
def connect_google_analytics():
    """Conectar con Google Analytics 4"""
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
        from google.oauth2 import service_account
        
        config = st.session_state.user_config
        property_id = config.get('Google Analytics_property')
        
        # Configurar credenciales (en producción, usar archivo JSON subido)
        credentials = service_account.Credentials.from_service_account_file(
            'path/to/service-account-key.json'
        )
        
        client = BetaAnalyticsDataClient(credentials=credentials)
        
        # Configurar reporte
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[
                Dimension(name="date"),
                Dimension(name="sourceMedium")
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="screenPageViews"),
                Metric(name="conversions")
            ],
            date_ranges=[DateRange(start_date="30daysAgo", end_date="today")]
        )
        
        response = client.run_report(request)
        
        # Procesar respuesta
        data = []
        for row in response.rows:
            data.append({
                'date': row.dimension_values[0].value,
                'source_medium': row.dimension_values[1].value,
                'sessions': int(row.metric_values[0].value),
                'users': int(row.metric_values[1].value),
                'pageviews': int(row.metric_values[2].value),
                'conversions': float(row.metric_values[3].value)
            })
        
        return pd.DataFrame(data)
        
    except ImportError:
        st.error("Por favor instala: pip install google-analytics-data")
        return None
    except Exception as e:
        st.error(f"Error conectando con Google Analytics: {e}")
        return None

# ==== HUBSPOT ====
def connect_hubspot():
    """Conectar con HubSpot API"""
    try:
        from hubspot import HubSpot
        
        config = st.session_state.user_config
        access_token = config.get('HubSpot_token')
        
        api_client = HubSpot(access_token=access_token)
        
        # Obtener deals (oportunidades)
        deals = api_client.crm.deals.basic_api.get_page(
            properties=['dealname', 'amount', 'dealstage', 'createdate', 'closedate'],
            limit=100
        )
        
        # Procesar deals
        data = []
        for deal in deals.results:
            props = deal.properties
            data.append({
                'deal_id': deal.id,
                'deal_name': props.get('dealname'),
                'amount': float(props.get('amount', 0)) if props.get('amount') else 0,
                'stage': props.get('dealstage'),
                'created_date': props.get('createdate'),
                'close_date': props.get('closedate')
            })
        
        return pd.DataFrame(data)
        
    except ImportError:
        st.error("Por favor instala: pip install hubspot-api-client")
        return None
    except Exception as e:
        st.error(f"Error conectando con HubSpot: {e}")
        return None

# ==== FUNCIÓN PRINCIPAL PARA CARGAR DATOS ====
def load_data_from_apis():
    """Cargar datos de todas las APIs configuradas"""
    config = st.session_state.user_config
    selected_apis = config.get('selected_apis', [])
    
    all_data = {}
    
    for api in selected_apis:
        st.write(f"Cargando datos de {api}...")
        
        if api == "Meta Ads (Facebook/Instagram)":
            data = connect_meta_ads()
            if data is not None:
                all_data['meta_ads'] = data
        
        elif api == "Google Ads":
            data = connect_google_ads()
            if data is not None:
                all_data['google_ads'] = data
        
        elif api == "Shopify":
            data = connect_shopify()
            if data is not None:
                all_data['shopify'] = data
        
        elif api == "Google Analytics":
            data = connect_google_analytics()
            if data is not None:
                all_data['google_analytics'] = data
        
        elif api == "HubSpot":
            data = connect_hubspot()
            if data is not None:
                all_data['hubspot'] = data
    
    return all_data

# ==== FUNCIONES PARA MOSTRAR DATOS ====
def show_meta_ads_metrics(data):
    """Mostrar métricas de Meta Ads"""
    if data is None or data.empty:
        return
    
    st.subheader("📱 Meta Ads (Facebook/Instagram)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_spend = data['spend'].sum()
        st.metric("Gasto Total", f"${total_spend:,.2f}")
    
    with col2:
        total_impressions = data['impressions'].sum()
        st.metric("Impresiones", f"{total_impressions:,}")
    
    with col3:
        total_clicks = data['clicks'].sum()
        st.metric("Clics", f"{total_clicks:,}")
    
    with col4:
        avg_ctr = data['ctr'].mean()
        st.metric("CTR Promedio", f"{avg_ctr:.2f}%")

def show_google_ads_metrics(data):
    """Mostrar métricas de Google Ads"""
    if data is None or data.empty:
        return
    
    st.subheader("🔍 Google Ads")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cost = data['cost'].sum()
        st.metric("Costo Total", f"${total_cost:,.2f}")
    
    with col2:
        total_impressions = data['impressions'].sum()
        st.metric("Impresiones", f"{total_impressions:,}")
    
    with col3:
        total_clicks = data['clicks'].sum()
        st.metric("Clics", f"{total_clicks:,}")
    
    with col4:
        avg_cpc = data['avg_cpc'].mean()
        st.metric("CPC Promedio", f"${avg_cpc:.2f}")

def show_shopify_metrics(data):
    """Mostrar métricas de Shopify"""
    if data is None or data.empty:
        return
    
    st.subheader("🛒 Shopify")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = data['total_price'].sum()
        st.metric("Ingresos Totales", f"${total_revenue:,.2f}")
    
    with col2:
        total_orders = len(data)
        st.metric("Total Órdenes", f"{total_orders:,}")
    
    with col3:
        avg_order_value = data['total_price'].mean()
        st.metric("Valor Promedio", f"${avg_order_value:.2f}")
    
    with col4:
        total_items = data['line_items_count'].sum()
        st.metric("Items Vendidos", f"{total_items:,}")

# Agregar al dashboard principal
def show_api_dashboard():
    """Mostrar dashboard con datos de APIs"""
    config = st.session_state.user_config
    selected_apis = config.get('selected_apis', [])
    
    if not selected_apis:
        st.info("No hay APIs configuradas. Ve a configuración para agregar integraciones.")
        return
    
    st.title("📊 Dashboard de Marketing Integrado")
    
    # Botón para actualizar datos
    if st.button("🔄 Actualizar Datos"):
        with st.spinner("Cargando datos de APIs..."):
            api_data = load_data_from_apis()
            st.session_state.api_data = api_data
    
    # Mostrar métricas de cada API
    api_data = st.session_state.get('api_data', {})
    
    if 'meta_ads' in api_data:
        show_meta_ads_metrics(api_data['meta_ads'])
        st.markdown("---")
    
    if 'google_ads' in api_data:
        show_google_ads_metrics(api_data['google_ads'])
        st.markdown("---")
    
    if 'shopify' in api_data:
        show_shopify_metrics(api_data['shopify'])
        st.markdown("---")
