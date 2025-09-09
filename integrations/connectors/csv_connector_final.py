# integrations/connectors/csv_connector.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io

class CSVConnector:
    def __init__(self):
        self.name = "CSV Upload"
        self.color = "#28A745"
        self.icon = "📄"
        self.uploaded_files = []
        self.processed_data = {}
    
    def configure(self):
        """Configuración visual del conector CSV"""
        st.subheader("🔗 Configurar Datos CSV")
        
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("### Subir Archivos CSV")
                
                uploaded_files = st.file_uploader(
                    "Selecciona archivos CSV",
                    type=['csv'],
                    accept_multiple_files=True,
                    help="Puedes subir múltiples archivos CSV con datos de ventas, clientes, productos, etc."
                )
                
                if uploaded_files:
                    self.uploaded_files = uploaded_files
                    
                    for i, file in enumerate(uploaded_files):
                        with st.expander(f"📁 {file.name}"):
                            # Leer y mostrar preview del archivo
                            try:
                                df = pd.read_csv(file)
                                st.write(f"**Filas:** {len(df)} | **Columnas:** {len(df.columns)}")
                                
                                # Mostrar preview
                                st.write("**Preview:**")
                                st.dataframe(df.head(3), use_container_width=True)
                                
                                # Configurar tipo de datos
                                st.write("**Configuración:**")
                                data_type = st.selectbox(
                                    "Tipo de datos",
                                    ["Ventas/Pedidos", "Clientes", "Productos", "Marketing", "Otro"],
                                    key=f"type_{i}"
                                )
                                
                                # Mapear columnas
                                self._configure_column_mapping(df, data_type, i)
                                
                                # Procesar archivo
                                if st.button(f"✅ Procesar {file.name}", key=f"process_{i}"):
                                    processed_df = self._process_csv_file(df, data_type)
                                    self.processed_data[file.name] = {
                                        'data': processed_df,
                                        'type': data_type,
                                        'processed_at': datetime.now()
                                    }
                                    st.success(f"✅ Archivo {file.name} procesado correctamente")
                                
                            except Exception as e:
                                st.error(f"Error al leer {file.name}: {str(e)}")
                
                # Configuración adicional
                if self.uploaded_files:
                    st.write("### Configuración Avanzada")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        auto_refresh = st.checkbox("Auto-refrescar datos", value=False)
                        date_format = st.selectbox(
                            "Formato de fecha",
                            ["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY", "Auto-detectar"]
                        )
                    
                    with col_b:
                        encoding = st.selectbox("Codificación", ["UTF-8", "Latin-1", "CP-1252"])
                        separator = st.selectbox("Separador", [",", ";", "|", "Tab"])
            
            with col2:
                st.write("### Estado")
                if self.uploaded_files:
                    st.success(f"🟢 {len(self.uploaded_files)} archivo(s) cargado(s)")
                    
                    # Mostrar archivos procesados
                    if self.processed_data:
                        st.write("### Archivos Procesados")
                        for filename, info in self.processed_data.items():
                            st.write(f"📊 **{filename}**")
                            st.write(f"Tipo: {info['type']}")
                            st.write(f"Filas: {len(info['data'])}")
                            st.write("---")
                else:
                    st.warning("🟡 No hay archivos cargados")
                
                # Estadísticas rápidas
                if self.processed_data:
                    st.write("### Resumen")
                    total_rows = sum(len(info['data']) for info in self.processed_data.values())
                    st.metric("Total de registros", f"{total_rows:,}")
                    st.metric("Archivos procesados", len(self.processed_data))
        
        # Botón guardar
        if self.uploaded_files and st.button("💾 Guardar Configuración", type="primary"):
            config = {
                'files_uploaded': len(self.uploaded_files),
                'processed_data': len(self.processed_data),
                'connected': True,
                'last_sync': datetime.now().isoformat()
            }
            st.session_state['connector_csv'] = config
            st.success("✅ Configuración guardada correctamente")
    
    def _configure_column_mapping(self, df, data_type, file_index):
        """Configurar mapeo de columnas según el tipo de datos"""
        st.write("**Mapeo de Columnas:**")
        
        if data_type == "Ventas/Pedidos":
            mapping_fields = {
                'fecha': 'Columna de fecha',
                'monto': 'Columna de monto/ventas',
                'cantidad': 'Columna de cantidad',
                'producto': 'Columna de producto (opcional)',
                'cliente': 'Columna de cliente (opcional)'
            }
        elif data_type == "Clientes":
            mapping_fields = {
                'cliente_id': 'ID del cliente',
                'email': 'Email',
                'fecha_registro': 'Fecha de registro',
                'total_gastado': 'Total gastado (opcional)'
            }
        elif data_type == "Productos":
            mapping_fields = {
                'producto_id': 'ID del producto',
                'nombre': 'Nombre del producto',
                'precio': 'Precio',
                'categoria': 'Categoría (opcional)'
            }
        elif data_type == "Marketing":
            mapping_fields = {
                'fecha': 'Fecha',
                'canal': 'Canal de marketing',
                'gasto': 'Gasto publicitario',
                'impresiones': 'Impresiones (opcional)',
                'clics': 'Clics (opcional)'
            }
        else:
            mapping_fields = {'columna_principal': 'Columna principal'}
        
        # Crear selectboxes para mapeo
        column_mapping = {}
        for field, description in mapping_fields.items():
            options = ['-- No seleccionar --'] + list(df.columns)
            selected = st.selectbox(
                description,
                options,
                key=f"mapping_{field}_{file_index}"
            )
            if selected != '-- No seleccionar --':
                column_mapping[field] = selected
        
        return column_mapping
    
    def _process_csv_file(self, df, data_type):
        """Procesar archivo CSV según su tipo"""
        try:
            # Limpiar datos básicos
            processed_df = df.copy()
            
            # Convertir fechas si existen
            date_columns = processed_df.select_dtypes(include=['object']).columns
            for col in date_columns:
                if any(keyword in col.lower() for keyword in ['fecha', 'date', 'time']):
                    try:
                        processed_df[col] = pd.to_datetime(processed_df[col], errors='coerce')
                    except:
                        pass
            
            # Limpiar valores numéricos
            numeric_columns = processed_df.select_dtypes(include=['object']).columns
            for col in numeric_columns:
                if any(keyword in col.lower() for keyword in ['monto', 'precio', 'gasto', 'amount', 'price', 'cost']):
                    try:
                        # Remover símbolos de moneda y convertir a numérico
                        processed_df[col] = processed_df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
                        processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce')
                    except:
                        pass
            
            # Remover filas vacías
            processed_df = processed_df.dropna(how='all')
            
            # Agregar metadatos
            processed_df['_file_type'] = data_type
            processed_df['_processed_at'] = datetime.now()
            
            return processed_df
            
        except Exception as e:
            st.error(f"Error al procesar datos: {str(e)}")
            return df
    
    def is_connected(self):
        """Verificar si hay archivos cargados"""
        return len(self.uploaded_files) > 0 or len(self.processed_data) > 0
    
    def fetch_data(self, date_range=30, file_type=None):
        """Obtener datos de los archivos CSV procesados"""
        if not self.processed_data:
            return None
        
        try:
            # Si se especifica un tipo, filtrar por ese tipo
            if file_type:
                relevant_data = {k: v for k, v in self.processed_data.items() 
                               if v['type'] == file_type}
            else:
                relevant_data = self.processed_data
            
            if not relevant_data:
                return None
            
            # Combinar todos los datos relevantes
            combined_data = []
            for filename, info in relevant_data.items():
                df = info['data'].copy()
                df['_source_file'] = filename
                combined_data.append(df)
            
            if combined_data:
                result_df = pd.concat(combined_data, ignore_index=True)
                
                # Filtrar por rango de fechas si hay columnas de fecha
                date_columns = result_df.select_dtypes(include=['datetime64']).columns
                if len(date_columns) > 0 and date_range:
                    date_col = date_columns[0]  # Usar la primera columna de fecha encontrada
                    cutoff_date = datetime.now() - timedelta(days=date_range)
                    result_df = result_df[result_df[date_col] >= cutoff_date]
                
                return result_df
            
            return None
            
        except Exception as e:
            st.error(f"Error al obtener datos CSV: {str(e)}")
            return None
    
    def get_summary_metrics(self):
        """Obtener métricas resumen de los datos CSV"""
        if not self.processed_data:
            return {}
        
        try:
            sales_data = self.fetch_data(file_type="Ventas/Pedidos")
            customers_data = self.fetch_data(file_type="Clientes")
            products_data = self.fetch_data(file_type="Productos")
            marketing_data = self.fetch_data(file_type="Marketing")
            
            metrics = {}
            
            # Métricas de ventas
            if sales_data is not None and not sales_data.empty:
                numeric_cols = sales_data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    # Buscar columna de monto/ventas
                    amount_col = None
                    for col in numeric_cols:
                        if any(keyword in col.lower() for keyword in ['monto', 'venta', 'amount', 'sales', 'revenue']):
                            amount_col = col
                            break
                    
                    if amount_col:
                        metrics['total_sales'] = round(sales_data[amount_col].sum(), 2)
                        metrics['avg_order_value'] = round(sales_data[amount_col].mean(), 2)
                    
                    metrics['total_orders'] = len(sales_data)
            
            # Métricas de clientes
            if customers_data is not None and not customers_data.empty:
                metrics['total_customers'] = len(customers_data)
            
            # Métricas de productos
            if products_data is not None and not products_data.empty:
                metrics['total_products'] = len(products_data)
            
            # Métricas de marketing
            if marketing_data is not None and not marketing_data.empty:
                numeric_cols = marketing_data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    spend_col = None
                    for col in numeric_cols:
                        if any(keyword in col.lower() for keyword in ['gasto', 'spend', 'cost', 'budget']):
                            spend_col = col
                            break
                    
                    if spend_col:
                        metrics['total_ad_spend'] = round(marketing_data[spend_col].sum(), 2)
            
            # Información general
            metrics['files_processed'] = len(self.processed_data)
            metrics['total_records'] = sum(len(info['data']) for info in self.processed_data.values())
            
            return metrics
            
        except Exception as e:
            st.error(f"Error al calcular métricas: {str(e)}")
            return {}
    
    def get_data_by_type(self, data_type):
        """Obtener datos específicos por tipo"""
        return self.fetch_data(file_type=data_type)
    
    def get_available_files(self):
        """Obtener lista de archivos disponibles"""
        return list(self.processed_data.keys())
    
    def get_file_info(self, filename):
        """Obtener información específica de un archivo"""
        if filename in self.processed_data:
            info = self.processed_data[filename]
            return {
                'type': info['type'],
                'rows': len(info['data']),
                'columns': list(info['data'].columns),
                'processed_at': info['processed_at']
            }
        return None
    
    def test_connection(self):
        """Probar la disponibilidad de datos"""
        if not self.processed_data:
            return False, "No hay archivos CSV procesados"
        
        try:
            total_records = sum(len(info['data']) for info in self.processed_data.values())
            return True, f"Datos CSV disponibles - {total_records:,} registros en {len(self.processed_data)} archivo(s)"
        except Exception as e:
            return False, f"Error al acceder a los datos: {str(e)}"