"""
Módulo de Análisis Exploratorio de Datos (EDA) para el proyecto de Análisis del Mercado Laboral Tecnológico.

Este módulo contiene funciones para explorar y visualizar los datos del mercado laboral
y encuestas a desarrolladores para identificar patrones, tendencias y conocimientos.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from pathlib import Path

# Configurar el registro
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Configuraciones de rutas
DATA_PROCESSED = os.path.join('data', 'processed')
IMG_DIR = 'img'

def ensure_dirs():
    """Asegurar que los directorios necesarios existan."""
    os.makedirs(DATA_PROCESSED, exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)
    logger.info("Directorios verificados/creados.")

def load_processed_data():
    """
    Cargar conjuntos de datos procesados para análisis.
    
    Returns:
        tuple: Tupla que contiene DataFrames procesados (jobs_df, survey_df)
    """
    logger.info("Cargando datos procesados para EDA...")
    
    jobs_path = os.path.join(DATA_PROCESSED, 'jobs_processed.csv')
    survey_path = os.path.join(DATA_PROCESSED, 'survey_processed.csv')
    
    jobs_df = pd.read_csv(jobs_path)
    survey_df = pd.read_csv(survey_path)
    
    # Convertir fechas si es necesario
    if 'created_at' in jobs_df.columns:
        jobs_df['created_at'] = pd.to_datetime(jobs_df['created_at'])
    
    logger.info(f"Datos de empleos cargados con {len(jobs_df)} registros")
    logger.info(f"Datos de encuesta cargados con {len(survey_df)} registros")
    
    return jobs_df, survey_df

def explore_job_data(jobs_df):
    """
    Realizar análisis exploratorio en datos de empleos.
    
    Args:
        jobs_df (pd.DataFrame): DataFrame procesado de empleos
        
    Returns:
        dict: Diccionario que contiene resultados de exploración
    """
    logger.info("Explorando datos de empleos...")
    
    results = {}
    
    # Basic info
    results['shape'] = jobs_df.shape
    results['columns'] = jobs_df.columns.tolist()
    results['dtypes'] = jobs_df.dtypes.to_dict()
    results['missing_values'] = jobs_df.isnull().sum().to_dict()
    
    # Desglose de tipos de empleo
    if 'type' in jobs_df.columns:
        results['job_types'] = jobs_df['type'].value_counts().to_dict()
    
    # Análisis de ubicación
    if 'location' in jobs_df.columns:
        results['locations'] = jobs_df['location'].value_counts().to_dict()
    
    # Estadísticas de salario
    if 'salary' in jobs_df.columns:
        results['salary_stats'] = {
            'mean': jobs_df['salary'].mean(),
            'median': jobs_df['salary'].median(),
            'min': jobs_df['salary'].min(),
            'max': jobs_df['salary'].max(),
            'std': jobs_df['salary'].std()
        }
    
    # Demanda de tecnología
    tech_columns = [col for col in jobs_df.columns if col.startswith('has_')]
    if tech_columns:
        tech_demand = {}
        for col in tech_columns:
            tech_name = col.replace('has_', '')
            tech_demand[tech_name] = jobs_df[col].sum()
        results['technology_demand'] = tech_demand
    
    return results

def explore_survey_data(survey_df):
    """
    Realizar análisis exploratorio en datos de encuesta a desarrolladores.
    
    Args:
        survey_df (pd.DataFrame): DataFrame procesado de encuesta
        
    Returns:
        dict: Diccionario que contiene resultados de exploración
    """
    logger.info("Explorando datos de encuesta...")
    
    results = {}
    
    # Basic info
    results['shape'] = survey_df.shape
    results['columns'] = survey_df.columns.tolist()
    results['dtypes'] = survey_df.dtypes.to_dict()
    results['missing_values'] = survey_df.isnull().sum().to_dict()
    
    # Datos demográficos
    if 'age' in survey_df.columns:
        results['age_stats'] = {
            'mean': survey_df['age'].mean(),
            'median': survey_df['age'].median(),
            'min': survey_df['age'].min(),
            'max': survey_df['age'].max(),
            'std': survey_df['age'].std()
        }
    
    if 'education' in survey_df.columns:
        results['education'] = survey_df['education'].value_counts().to_dict()
    
    if 'developer_type' in survey_df.columns:
        results['developer_types'] = survey_df['developer_type'].value_counts().to_dict()
    
    # Experiencia y salario
    if 'years_coding' in survey_df.columns:
        results['years_coding_stats'] = {
            'mean': survey_df['years_coding'].mean(),
            'median': survey_df['years_coding'].median(),
            'min': survey_df['years_coding'].min(),
            'max': survey_df['years_coding'].max(),
            'std': survey_df['years_coding'].std()
        }
    
    if 'salary' in survey_df.columns:
        results['salary_stats'] = {
            'mean': survey_df['salary'].mean(),
            'median': survey_df['salary'].median(),
            'min': survey_df['salary'].min(),
            'max': survey_df['salary'].max(),
            'std': survey_df['salary'].std()
        }
    
    # Conocimiento de tecnología
    tech_columns = [col for col in survey_df.columns if col.startswith('knows_')]
    if tech_columns:
        tech_knowledge = {}
        for col in tech_columns:
            tech_name = col.replace('knows_', '')
            tech_knowledge[tech_name] = survey_df[col].sum()
        results['technology_knowledge'] = tech_knowledge
    
    # Satisfacción laboral
    if 'job_satisfaction' in survey_df.columns:
        results['job_satisfaction_stats'] = {
            'mean': survey_df['job_satisfaction'].mean(),
            'median': survey_df['job_satisfaction'].median(),
            'min': survey_df['job_satisfaction'].min(),
            'max': survey_df['job_satisfaction'].max(),
            'std': survey_df['job_satisfaction'].std()
        }
    
    return results

def visualize_job_market(jobs_df):
    """
    Crear visualizaciones para datos del mercado laboral.
    
    Args:
        jobs_df (pd.DataFrame): DataFrame procesado de empleos
        
    Returns:
        list: Lista de rutas a visualizaciones generadas
    """
    logger.info("Creando visualizaciones del mercado laboral...")
    ensure_dirs()
    
    visualization_paths = []
    
    # Set style
    sns.set(style="whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)
    
    # 1. Distribución de tipos de empleo
    if 'type' in jobs_df.columns:
        plt.figure()
        job_type_counts = jobs_df['type'].value_counts()
        sns.barplot(x=job_type_counts.index, y=job_type_counts.values)
        plt.title('Distribution of Job Types', fontsize=16)
        plt.xlabel('Job Type', fontsize=12)
        plt.ylabel('Count', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save figure
        job_types_path = os.path.join(IMG_DIR, 'job_types_distribution.png')
        plt.savefig(job_types_path)
        plt.close()
        visualization_paths.append(job_types_path)
    
    # 2. Distribución de salarios
    if 'salary' in jobs_df.columns:
        plt.figure()
        sns.histplot(jobs_df['salary'].dropna(), kde=True)
        plt.title('Salary Distribution in Tech Jobs', fontsize=16)
        plt.xlabel('Salary', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.tight_layout()
        
        # Save figure
        salary_dist_path = os.path.join(IMG_DIR, 'salary_distribution.png')
        plt.savefig(salary_dist_path)
        plt.close()
        visualization_paths.append(salary_dist_path)
    
    # 3. Demanda de tecnología
    tech_columns = [col for col in jobs_df.columns if col.startswith('has_')]
    if tech_columns:
        tech_demand = {}
        for col in tech_columns:
            tech_name = col.replace('has_', '').capitalize()
            tech_demand[tech_name] = jobs_df[col].sum()
        
        plt.figure()
        tech_df = pd.DataFrame({
            'Technology': list(tech_demand.keys()),
            'Job Count': list(tech_demand.values())
        }).sort_values('Job Count', ascending=False)
        
        sns.barplot(x='Job Count', y='Technology', data=tech_df)
        plt.title('Most In-Demand Technologies', fontsize=16)
        plt.xlabel('Number of Job Listings', fontsize=12)
        plt.ylabel('Technology', fontsize=12)
        plt.tight_layout()
        
        # Save figure
        tech_demand_path = os.path.join(IMG_DIR, 'technology_demand.png')
        plt.savefig(tech_demand_path)
        plt.close()
        visualization_paths.append(tech_demand_path)
    
    # 4. Distribución de ubicación
    if 'location' in jobs_df.columns:
        plt.figure()
        location_counts = jobs_df['location'].value_counts().head(10)  # Top 10 locations
        sns.barplot(x=location_counts.values, y=location_counts.index)
        plt.title('Top 10 Locations for Tech Jobs', fontsize=16)
        plt.xlabel('Number of Job Listings', fontsize=12)
        plt.ylabel('Location', fontsize=12)
        plt.tight_layout()
        
        # Save figure
        location_dist_path = os.path.join(IMG_DIR, 'location_distribution.png')
        plt.savefig(location_dist_path)
        plt.close()
        visualization_paths.append(location_dist_path)
    
    logger.info(f"Creadas {len(visualization_paths)} visualizaciones del mercado laboral")
    return visualization_paths

def visualize_survey_data(survey_df):
    """
    Crear visualizaciones para datos de encuesta a desarrolladores.
    
    Args:
        survey_df (pd.DataFrame): DataFrame procesado de encuesta
        
    Returns:
        list: Lista de rutas a visualizaciones generadas
    """
    logger.info("Creando visualizaciones de encuesta a desarrolladores...")
    ensure_dirs()
    
    visualization_paths = []
    
    # Set style
    sns.set(style="whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)
    
    # 1. Distribución de edad
    if 'age' in survey_df.columns:
        plt.figure()
        sns.histplot(survey_df['age'].dropna(), kde=True, bins=20)
        plt.title('Age Distribution of Developers', fontsize=16)
        plt.xlabel('Age', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.tight_layout()
        
        # Save figure
        age_dist_path = os.path.join(IMG_DIR, 'age_distribution.png')
        plt.savefig(age_dist_path)
        plt.close()
        visualization_paths.append(age_dist_path)
    
    # 2. Nivel educativo
    if 'education' in survey_df.columns:
        plt.figure()
        edu_counts = survey_df['education'].value_counts()
        sns.barplot(x=edu_counts.values, y=edu_counts.index)
        plt.title('Education Levels of Developers', fontsize=16)
        plt.xlabel('Number of Developers', fontsize=12)
        plt.ylabel('Education Level', fontsize=12)
        plt.tight_layout()
        
        # Save figure
        edu_dist_path = os.path.join(IMG_DIR, 'education_distribution.png')
        plt.savefig(edu_dist_path)
        plt.close()
        visualization_paths.append(edu_dist_path)
    
    # 3. Tipos de desarrolladores
    if 'developer_type' in survey_df.columns:
        plt.figure()
        dev_type_counts = survey_df['developer_type'].value_counts()
        sns.barplot(x=dev_type_counts.values, y=dev_type_counts.index)
        plt.title('Types of Developers', fontsize=16)
        plt.xlabel('Number of Developers', fontsize=12)
        plt.ylabel('Developer Type', fontsize=12)
        plt.tight_layout()
        
        # Save figure
        dev_type_path = os.path.join(IMG_DIR, 'developer_types.png')
        plt.savefig(dev_type_path)
        plt.close()
        visualization_paths.append(dev_type_path)
    
    # 4. Años de experiencia vs. Salario
    if 'years_coding' in survey_df.columns and 'salary' in survey_df.columns:
        plt.figure()
        sns.scatterplot(x='years_coding', y='salary', data=survey_df)
        plt.title('Relationship Between Experience and Salary', fontsize=16)
        plt.xlabel('Years of Coding Experience', fontsize=12)
        plt.ylabel('Salary', fontsize=12)
        plt.tight_layout()
        
        # Save figure
        exp_salary_path = os.path.join(IMG_DIR, 'experience_vs_salary.png')
        plt.savefig(exp_salary_path)
        plt.close()
        visualization_paths.append(exp_salary_path)
    
    # 5. Conocimiento de tecnología
    tech_columns = [col for col in survey_df.columns if col.startswith('knows_')]
    if tech_columns:
        tech_knowledge = {}
        for col in tech_columns:
            tech_name = col.replace('knows_', '').capitalize()
            tech_knowledge[tech_name] = survey_df[col].sum()
        
        plt.figure()
        tech_df = pd.DataFrame({
            'Technology': list(tech_knowledge.keys()),
            'Developer Count': list(tech_knowledge.values())
        }).sort_values('Developer Count', ascending=False)
        
        sns.barplot(x='Developer Count', y='Technology', data=tech_df)
        plt.title('Most Common Technologies Among Developers', fontsize=16)
        plt.xlabel('Number of Developers', fontsize=12)
        plt.ylabel('Technology', fontsize=12)
        plt.tight_layout()
        
        # Save figure
        tech_knowledge_path = os.path.join(IMG_DIR, 'technology_knowledge.png')
        plt.savefig(tech_knowledge_path)
        plt.close()
        visualization_paths.append(tech_knowledge_path)
    
    logger.info(f"Creadas {len(visualization_paths)} visualizaciones de encuesta a desarrolladores")
    return visualization_paths

def run_eda():
    """Ejecutar el proceso completo de EDA."""
    logger.info("Iniciando Análisis Exploratorio de Datos...")
    
    # Cargar datos procesados
    jobs_df, survey_df = load_processed_data()
    
    # Explorar datos
    job_results = explore_job_data(jobs_df)
    survey_results = explore_survey_data(survey_df)
    
    # Crear visualizaciones
    job_viz_paths = visualize_job_market(jobs_df)
    survey_viz_paths = visualize_survey_data(survey_df)
    
    logger.info("EDA completado exitosamente.")
    
    return {
        'job_results': job_results,
        'survey_results': survey_results,
        'job_visualizations': job_viz_paths,
        'survey_visualizations': survey_viz_paths
    }

if __name__ == "__main__":
    run_eda()
