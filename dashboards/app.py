"""
Dashboard Interactivo del Mercado Laboral Tecnológico
====================================================

Este dashboard muestra análisis interactivos de datos REALES del mercado laboral tecnológico,
permitiendo filtrar por ubicación, tecnología, y tipo de contrato.

"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
from datetime import datetime

# Añadir directorio raíz al path para importar módulos del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configuración de la página
st.set_page_config(
    page_title="Análisis del Mercado Laboral Tech",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #3498db;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #2980b9;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #ecf0f1;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-container {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #ecf0f1;
        color: #95a5a6;
        font-size: 0.8rem;
    }
    .highlight {
        background-color: #e8f4f8;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #3498db;
        color: #000;
    }
</style>
""", unsafe_allow_html=True)

# Funciones auxiliares
def load_data():
    """Carga los datos procesados desde el directorio data/processed/"""
    try:
        jobs_path = os.path.join('data', 'processed', 'jobs_processed.csv')
        tech_counts_path = os.path.join('data', 'processed', 'technology_job_counts.csv')
        
        jobs_df = pd.read_csv(jobs_path)
            
        # Intentar cargar tech counts si existen
        try:
            tech_counts_df = pd.read_csv(tech_counts_path)
        except:
            tech_counts_df = None
            
        return jobs_df, tech_counts_df
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        st.info("Por favor ejecuta primero el pipeline ETL con 'python main.py' para generar los datos necesarios.")
        return None, None

def extract_technologies(jobs_df):
    """Extrae y cuenta las tecnologías de las ofertas de trabajo"""
    # Verificar si ya tenemos una columna de tecnologías
    if 'tecnologias' not in jobs_df.columns or jobs_df['tecnologias'].isna().all():
        return pd.DataFrame(columns=['tecnologia', 'menciones'])
    
    # Extraer todas las tecnologías mencionadas
    all_techs = []
    for techs in jobs_df['tecnologias'].dropna():
        if isinstance(techs, str):
            all_techs.extend([t.strip() for t in techs.split(',')])
    
    # Contar frecuencia de tecnologías
    tech_counts = pd.Series(all_techs).value_counts().reset_index()
    tech_counts.columns = ['tecnologia', 'menciones']
    
    return tech_counts

def determine_salary_column(jobs_df):
    """Determina qué columna usar para datos de salario"""
    salary_cols = ['salario_promedio', 'salary', 'salario']
    for col in salary_cols:
        if col in jobs_df.columns and not jobs_df[col].isna().all():
            return col
    return None

def determine_location_column(jobs_df):
    """Determina qué columna usar para datos de ubicación"""
    location_cols = ['ubicacion', 'location']
    for col in location_cols:
        if col in jobs_df.columns and not jobs_df[col].isna().all():
            return col
    return None

def is_real_data(jobs_df):
    """Determina si los datos son reales o simulados"""
    if 'fuente' not in jobs_df.columns:
        return "Desconocido"
    
    # Verificar las fuentes de datos
    sources = jobs_df['fuente'].astype(str).str.lower()
    
    if sources.str.contains('simulado').any():
        simulated_count = sources.str.contains('simulado').sum()
        total_count = len(jobs_df)
        if simulated_count == total_count:
            return "100% Simulados"
        else:
            real_percentage = round(100 - (simulated_count / total_count * 100), 1)
            return f"{real_percentage}% Reales, {100-real_percentage}% Simulados"
    else:
        return "100% Reales"

# Función principal del dashboard
def run_dashboard():
    # Cargar datos
    jobs_df, tech_counts_df = load_data()
    
    if jobs_df is None:
        return
    
    # Determinar columnas para análisis
    salary_col = determine_salary_column(jobs_df)
    location_col = determine_location_column(jobs_df)
    
    # Extraer tecnologías si no tenemos tech_counts_df
    if tech_counts_df is None:
        tech_counts_df = extract_technologies(jobs_df)
    
    # Verificar si tenemos datos reales o simulados
    data_type = is_real_data(jobs_df)
    
    # Header
    st.markdown("<h1 class='main-header'>Dashboard del Mercado Laboral Tecnológico</h1>", unsafe_allow_html=True)
    
    # Información sobre el tipo de datos
    data_status = "🟢 DATOS REALES" if "100% Reales" in data_type else "🟠 DATOS MIXTOS" if "Reales" in data_type else "🔴 DATOS SIMULADOS"
    st.markdown(f"<p style='text-align: center; font-size: 1.2rem;'><strong>{data_status}</strong> - Análisis de {len(jobs_df)} ofertas de empleo</p>", unsafe_allow_html=True)
    
    # Métricas generales
    st.markdown("<h2 class='sub-header'>Métricas Clave</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Total de ofertas
    with col1:
        st.metric(
            label="Ofertas Analizadas",
            value=f"{len(jobs_df):,}",
            delta=None
        )
    
    # Salario promedio
    with col2:
        if salary_col:
            avg_salary = int(jobs_df[salary_col].dropna().mean())
            st.metric(
                label="Salario Promedio",
                value=f"{avg_salary:,} €",
                delta=None
            )
        else:
            st.metric(
                label="Salario Promedio",
                value="No disponible",
                delta=None
            )
    
    # Tecnologías únicas
    with col3:
        if 'tecnologias' in jobs_df.columns:
            unique_techs = set()
            for techs in jobs_df['tecnologias'].dropna():
                if isinstance(techs, str):
                    unique_techs.update([t.strip() for t in techs.split(',')])
            st.metric(
                label="Tecnologías Identificadas",
                value=f"{len(unique_techs):,}",
                delta=None
            )
        else:
            st.metric(
                label="Tecnologías Identificadas",
                value="No disponible",
                delta=None
            )
    
    # Ubicaciones únicas
    with col4:
        if location_col:
            unique_locations = jobs_df[location_col].nunique()
            st.metric(
                label="Ubicaciones",
                value=f"{unique_locations:,}",
                delta=None
            )
        else:
            st.metric(
                label="Ubicaciones",
                value="No disponible",
                delta=None
            )
    
    # Añadir separación
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Filtros en la barra lateral
    st.sidebar.markdown("## Filtros")
    
    # Filtro por ubicación
    if location_col:
        locations = ['Todas'] + sorted(jobs_df[location_col].dropna().unique().tolist())
        selected_location = st.sidebar.selectbox("Ubicación", locations)
    else:
        selected_location = "Todas"
    
    # Filtro por tipo de contrato
    if 'tipo_contrato' in jobs_df.columns:
        contract_types = ['Todos'] + sorted(jobs_df['tipo_contrato'].dropna().unique().tolist())
        selected_contract = st.sidebar.selectbox("Tipo de Contrato", contract_types)
    elif 'jornada' in jobs_df.columns:
        contract_types = ['Todos'] + sorted(jobs_df['jornada'].dropna().unique().tolist())
        selected_contract = st.sidebar.selectbox("Jornada", contract_types)
    else:
        selected_contract = "Todos"
    
    # Filtro por tecnología
    if 'tecnologias' in jobs_df.columns:
        all_techs = set()
        for techs in jobs_df['tecnologias'].dropna():
            if isinstance(techs, str):
                all_techs.update([t.strip() for t in techs.split(',')])
        tech_options = ['Todas'] + sorted(all_techs)
        selected_tech = st.sidebar.selectbox("Tecnología", tech_options)
    else:
        selected_tech = "Todas"
    
    # Aplicar filtros
    filtered_df = jobs_df.copy()
    
    if selected_location != "Todas" and location_col:
        filtered_df = filtered_df[filtered_df[location_col] == selected_location]
    
    if selected_contract != "Todos":
        if 'tipo_contrato' in jobs_df.columns:
            filtered_df = filtered_df[filtered_df['tipo_contrato'] == selected_contract]
        elif 'jornada' in jobs_df.columns:
            filtered_df = filtered_df[filtered_df['jornada'] == selected_contract]
    
    if selected_tech != "Todas" and 'tecnologias' in jobs_df.columns:
        filtered_df = filtered_df[filtered_df['tecnologias'].fillna('').apply(lambda x: selected_tech in x.split(',') if isinstance(x, str) else False)]
    
    # Mostrar información de filtros aplicados
    if selected_location != "Todas" or selected_contract != "Todos" or selected_tech != "Todas":
        filters_applied = []
        if selected_location != "Todas":
            filters_applied.append(f"Ubicación: {selected_location}")
        if selected_contract != "Todos":
            filters_applied.append(f"Contrato: {selected_contract}")
        if selected_tech != "Todas":
            filters_applied.append(f"Tecnología: {selected_tech}")
        
        st.markdown(f"<div class='highlight'><strong>Filtros aplicados:</strong> {', '.join(filters_applied)} (Mostrando {len(filtered_df)} de {len(jobs_df)} ofertas)</div>", unsafe_allow_html=True)
    
    # Visualizaciones principales (2 columnas)
    st.markdown("<h2 class='sub-header'>Tendencias del Mercado</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # Gráfico 1: Distribución por ubicación
    with col1:
        if location_col and not filtered_df[location_col].isna().all():
            st.markdown("### 📍 Distribución por Ubicación")
            location_counts = filtered_df[location_col].value_counts().head(10)
            
            fig = px.bar(
                x=location_counts.values,
                y=location_counts.index,
                orientation='h',
                labels={'x': 'Número de ofertas', 'y': 'Ubicación'},
                color=location_counts.values,
                color_continuous_scale='blues'
            )
            
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=30, b=20),
                coloraxis_showscale=False,
                yaxis={'categoryorder': 'total ascending'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("### 📍 Distribución por Ubicación")
            st.info("No hay datos de ubicación disponibles")
    
    # Gráfico 2: Tecnologías más demandadas
    with col2:
        if 'tecnologias' in filtered_df.columns and not filtered_df['tecnologias'].isna().all():
            st.markdown("### 💻 Tecnologías Más Demandadas")
            
            # Extraer tecnologías del dataframe filtrado
            all_techs = []
            for techs in filtered_df['tecnologias'].dropna():
                if isinstance(techs, str):
                    all_techs.extend([t.strip() for t in techs.split(',')])
            
            tech_counts = pd.Series(all_techs).value_counts().head(10)
            
            fig = px.bar(
                x=tech_counts.values,
                y=tech_counts.index,
                orientation='h',
                labels={'x': 'Número de menciones', 'y': 'Tecnología'},
                color=tech_counts.values,
                color_continuous_scale='viridis'
            )
            
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=30, b=20),
                coloraxis_showscale=False,
                yaxis={'categoryorder': 'total ascending'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("### 💻 Tecnologías Más Demandadas")
            st.info("No hay datos de tecnologías disponibles")
    
    # Gráficos adicionales (2 columnas)
    col1, col2 = st.columns(2)
    
    # Gráfico 3: Análisis de Salarios
    with col1:
        if salary_col and not filtered_df[salary_col].isna().all():
            st.markdown("### 💰 Distribución de Salarios")
            
            # Filtrar valores extremos
            salary_data = filtered_df[salary_col].dropna()
            q1 = salary_data.quantile(0.05)
            q3 = salary_data.quantile(0.95)
            iqr = q3 - q1
            salary_filtered = salary_data[(salary_data >= q1 - 1.5 * iqr) & (salary_data <= q3 + 1.5 * iqr)]
            
            fig = px.histogram(
                salary_filtered,
                labels={'value': 'Salario', 'count': 'Frecuencia'},
                color_discrete_sequence=['#3498db'],
                marginal='box'
            )
            
            # Añadir líneas para la media y mediana con anotaciones posicionadas para no solaparse
            mean_value = int(salary_filtered.mean())
            median_value = int(salary_filtered.median())
            
            # Línea de la media
            fig.add_vline(
                x=mean_value,
                line_color='red',
                line_dash='dash',
                annotation=dict(
                    text=f"Media: {mean_value:,}€",
                    yshift=25,  # Desplazar hacia arriba
                    showarrow=False,
                    font=dict(color='red', size=12),
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor='red',
                    borderwidth=1,
                    borderpad=4
                )
            )
            
            # Línea de la mediana
            fig.add_vline(
                x=median_value,
                line_color='green',
                line_dash='dash',
                annotation=dict(
                    text=f"Mediana: {median_value:,}€",
                    yshift=-25,  # Desplazar hacia abajo
                    showarrow=False,
                    font=dict(color='green', size=12),
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor='green',
                    borderwidth=1,
                    borderpad=4
                )
            )
            
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Estadísticas salariales complementarias
            stat_col1, stat_col2 = st.columns(2)
            
            with stat_col1:
                st.metric("Rango salarial", f"{int(salary_filtered.max() - salary_filtered.min()):,}€")
                st.metric("Mínimo", f"{int(salary_filtered.min()):,}€")
            with stat_col2:
                st.metric("Desviación estándar", f"{int(salary_filtered.std()):,}€")
                st.metric("Máximo", f"{int(salary_filtered.max()):,}€")
        else:
            st.markdown("### 💰 Distribución de Salarios")
            st.info("No hay datos de salario disponibles")
    
    # Gráfico 4: Tipos de contrato
    with col2:
        contract_col = None
        if 'tipo_contrato' in filtered_df.columns and not filtered_df['tipo_contrato'].isna().all():
            contract_col = 'tipo_contrato'
            title = "Tipos de Contrato"
        elif 'jornada' in filtered_df.columns and not filtered_df['jornada'].isna().all():
            contract_col = 'jornada'
            title = "Tipos de Jornada"
        
        if contract_col:
            st.markdown(f"### 📝 {title}")
            
            contract_counts = filtered_df[contract_col].value_counts()
            
            fig = px.pie(
                values=contract_counts.values,
                names=contract_counts.index,
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.4
            )
            
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("### 📝 Tipos de Contrato")
            st.info("No hay datos de tipos de contrato disponibles")
    
    # Sección de información adicional
    st.markdown("<h2 class='sub-header'>Datos detallados</h2>", unsafe_allow_html=True)
    
    # Mostrar datos en formato tabular
    if st.checkbox("Mostrar tabla de datos"):
        st.dataframe(filtered_df.head(100))
        st.caption("Mostrando las primeras 100 filas. El conjunto completo tiene {:,} filas.".format(len(filtered_df)))
    
    # Espacio adicional antes del footer
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Footer mejorado (sin rectángulo blanco adicional)
    st.markdown("""
    <div class='footer' style='background-color: transparent; margin-bottom: 0; padding-bottom: 0;'>
        <p>Dashboard creado con Streamlit para el Análisis del Mercado Laboral Tecnológico</p>
        <p>Datos actualizados el: {}</p>
    </div>
    """.format(datetime.now().strftime("%d/%m/%Y")), unsafe_allow_html=True)

# Ejecutar el dashboard
if __name__ == "__main__":
    run_dashboard()
