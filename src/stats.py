"""
Módulo de estadísticas para el proyecto de Análisis del Mercado Laboral Tecnológico.

Este módulo contiene funciones para el análisis estadístico de los datos del mercado laboral
y datos de encuestas a desarrolladores, incluyendo estadísticas descriptivas, estadísticas inferenciales,
y análisis de correlación.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
from sklearn.linear_model import LinearRegression
import logging

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
    Cargar conjuntos de datos procesados para análisis estadístico.
    
    Returns:
        tuple: Tupla que contiene DataFrames procesados (jobs_df, survey_df)
    """
    logger.info("Cargando datos procesados para análisis estadístico...")
    
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

def descriptive_stats_jobs(jobs_df):
    """
    Generar estadísticas descriptivas para datos de empleos.
    
    Args:
        jobs_df (pd.DataFrame): DataFrame procesado de empleos
        
    Returns:
        dict: Diccionario que contiene estadísticas descriptivas
    """
    logger.info("Generando estadísticas descriptivas para datos de empleos...")
    
    stats_results = {}
    
    # Numerical variables statistics
    numerical_cols = jobs_df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    if numerical_cols:
        stats_results['numerical'] = jobs_df[numerical_cols].describe().to_dict()
    
    # Categorical variables statistics
    categorical_cols = jobs_df.select_dtypes(include=['object', 'category']).columns.tolist()
    categorical_stats = {}
    for col in categorical_cols:
        if col != 'technology':  # Skip list columns
            categorical_stats[col] = {
                'count': jobs_df[col].count(),
                'unique': jobs_df[col].nunique(),
                'top': jobs_df[col].value_counts().index[0] if not jobs_df[col].empty else None,
                'freq': jobs_df[col].value_counts().iloc[0] if not jobs_df[col].empty else 0
            }
    
    stats_results['categorical'] = categorical_stats
    
    # Estadísticas de salario por tipo de trabajo si están disponibles
    if 'salary' in jobs_df.columns and 'type' in jobs_df.columns:
        salary_by_type = {}
        for job_type in jobs_df['type'].unique():
            subset = jobs_df[jobs_df['type'] == job_type]['salary']
            salary_by_type[job_type] = {
                'count': subset.count(),
                'mean': subset.mean(),
                'median': subset.median(),
                'std': subset.std(),
                'min': subset.min(),
                'max': subset.max()
            }
        stats_results['salary_by_job_type'] = salary_by_type
    
    # Estadísticas de salario por ubicación si están disponibles
    if 'salary' in jobs_df.columns and 'location' in jobs_df.columns:
        # Obtener ubicaciones principales
        top_locations = jobs_df['location'].value_counts().head(5).index.tolist()
        salary_by_location = {}
        for location in top_locations:
            subset = jobs_df[jobs_df['location'] == location]['salary']
            salary_by_location[location] = {
                'count': subset.count(),
                'mean': subset.mean(),
                'median': subset.median(),
                'std': subset.std(),
                'min': subset.min(),
                'max': subset.max()
            }
        stats_results['salary_by_location'] = salary_by_location
    
    return stats_results

def descriptive_stats_survey(survey_df):
    """
    Generar estadísticas descriptivas para datos de encuesta a desarrolladores.
    
    Args:
        survey_df (pd.DataFrame): DataFrame procesado de encuesta
        
    Returns:
        dict: Diccionario que contiene estadísticas descriptivas
    """
    logger.info("Generando estadísticas descriptivas para datos de encuesta...")
    
    stats_results = {}
    
    # Numerical variables statistics
    numerical_cols = survey_df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    if numerical_cols:
        stats_results['numerical'] = survey_df[numerical_cols].describe().to_dict()
    
    # Categorical variables statistics
    categorical_cols = survey_df.select_dtypes(include=['object', 'category']).columns.tolist()
    categorical_stats = {}
    for col in categorical_cols:
        if col != 'languages':  # Skip list columns
            categorical_stats[col] = {
                'count': survey_df[col].count(),
                'unique': survey_df[col].nunique(),
                'top': survey_df[col].value_counts().index[0] if not survey_df[col].empty else None,
                'freq': survey_df[col].value_counts().iloc[0] if not survey_df[col].empty else 0
            }
    
    stats_results['categorical'] = categorical_stats
    
    # Estadísticas de salario por tipo de desarrollador si están disponibles
    if 'salary' in survey_df.columns and 'developer_type' in survey_df.columns:
        salary_by_dev_type = {}
        for dev_type in survey_df['developer_type'].unique():
            subset = survey_df[survey_df['developer_type'] == dev_type]['salary']
            salary_by_dev_type[dev_type] = {
                'count': subset.count(),
                'mean': subset.mean(),
                'median': subset.median(),
                'std': subset.std(),
                'min': subset.min(),
                'max': subset.max()
            }
        stats_results['salary_by_developer_type'] = salary_by_dev_type
    
    # Estadísticas de salario por nivel educativo si están disponibles
    if 'salary' in survey_df.columns and 'education' in survey_df.columns:
        salary_by_education = {}
        for edu in survey_df['education'].unique():
            subset = survey_df[survey_df['education'] == edu]['salary']
            salary_by_education[edu] = {
                'count': subset.count(),
                'mean': subset.mean(),
                'median': subset.median(),
                'std': subset.std(),
                'min': subset.min(),
                'max': subset.max()
            }
        stats_results['salary_by_education'] = salary_by_education
    
    return stats_results

def correlation_analysis(df, target_col, numerical_cols=None):
    """
    Realizar análisis de correlación entre una columna objetivo y columnas numéricas.
    
    Args:
        df (pd.DataFrame): DataFrame a analizar
        target_col (str): Nombre de la columna objetivo
        numerical_cols (list, optional): Lista de nombres de columnas numéricas
        
    Returns:
        dict: Diccionario que contiene resultados de correlación
    """
    if target_col not in df.columns:
        logger.warning(f"Columna objetivo '{target_col}' no encontrada en el DataFrame")
        return {}
    
    if numerical_cols is None:
        numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        # Eliminar columna objetivo de numerical_cols si está presente
        if target_col in numerical_cols:
            numerical_cols.remove(target_col)
    
    correlation_results = {}
    
    # Correlación de Pearson
    pearson_corrs = {}
    for col in numerical_cols:
        if col in df.columns:
            # Asegurarse de que ambas columnas tengan la misma longitud después de eliminar NaNs
            temp_df = df[[target_col, col]].dropna()
            if len(temp_df) < 2:
                continue  # No se puede calcular la correlación con menos de 2 puntos de datos
            
            corr, p_value = stats.pearsonr(temp_df[target_col], temp_df[col])
            pearson_corrs[col] = {
                'correlation': corr,
                'p_value': p_value,
                'significance': 'Significativo' if p_value < 0.05 else 'No significativo'
            }
    
    correlation_results['pearson'] = pearson_corrs
    
    # Crear mapa de calor de correlación
    corr_columns = [target_col] + numerical_cols
    corr_df = df[corr_columns].dropna()
    
    if len(corr_df) > 1:  # Se necesitan al menos 2 muestras para la correlación
        corr_matrix = corr_df.corr()
        
        plt.figure(figsize=(10, 8))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, cmap='coolwarm', annot=True, fmt='.2f', linewidths=0.5)
        plt.title(f'Correlation Matrix with {target_col}', fontsize=16)
        plt.tight_layout()
        
        ensure_dirs()
        corr_path = os.path.join(IMG_DIR, f'correlation_{target_col}.png')
        plt.savefig(corr_path)
        plt.close()
        
        correlation_results['heatmap_path'] = corr_path
    
    return correlation_results

def salary_regression_analysis(df, predictor_col):
    """
    Realizar análisis de regresión lineal simple para predicción de salario.
    
    Args:
        df (pd.DataFrame): DataFrame a analizar
        predictor_col (str): Nombre de la columna predictora
        
    Returns:
        dict: Diccionario que contiene resultados de regresión
    """
    if 'salary' not in df.columns or predictor_col not in df.columns:
        logger.warning(f"Columnas requeridas no encontradas en el DataFrame")
        return {}
    
    # Preparar datos
    X = df[predictor_col].dropna().values.reshape(-1, 1)
    y = df.loc[df[predictor_col].notna(), 'salary'].values
    
    if len(X) < 2:  # Se necesitan al menos 2 muestras para la regresión
        logger.warning(f"No hay suficientes puntos de datos para la regresión")
        return {}
    
    # Ajustar modelo de regresión lineal
    model = LinearRegression()
    model.fit(X, y)
    
    # Obtener parámetros del modelo
    slope = model.coef_[0]
    intercept = model.intercept_
    
    # Hacer predicciones
    y_pred = model.predict(X)
    
    # Calcular métricas
    r_squared = model.score(X, y)
    
    # Crear gráfico de regresión
    plt.figure(figsize=(10, 6))
    plt.scatter(X, y, alpha=0.5)
    plt.plot(X, y_pred, color='red', linewidth=2)
    plt.title(f'Salary vs {predictor_col.capitalize()} - Linear Regression', fontsize=16)
    plt.xlabel(predictor_col.capitalize(), fontsize=12)
    plt.ylabel('Salary', fontsize=12)
    plt.text(0.05, 0.95, f'y = {slope:.2f}x + {intercept:.2f}\nR² = {r_squared:.2f}',
             transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.tight_layout()
    
    ensure_dirs()
    reg_path = os.path.join(IMG_DIR, f'regression_salary_{predictor_col}.png')
    plt.savefig(reg_path)
    plt.close()
    
    regression_results = {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_squared,
        'equation': f'salario = {slope:.2f} * {predictor_col} + {intercept:.2f}',
        'interpretation': f'Por cada unidad de aumento en {predictor_col}, el salario aumenta en {slope:.2f}',
        'plot_path': reg_path
    }
    
    return regression_results

def tech_salary_comparison(jobs_df):
    """
    Comparar salarios para diferentes tecnologías.
    
    Args:
        jobs_df (pd.DataFrame): DataFrame procesado de empleos
        
    Returns:
        dict: Diccionario que contiene resultados de comparación
    """
    tech_columns = [col for col in jobs_df.columns if col.startswith('has_')]
    
    if not tech_columns or 'salary' not in jobs_df.columns:
        logger.warning("Columnas requeridas no encontradas para la comparación de salarios por tecnología")
        return {}
    
    comparison_results = {}
    
    # Calcular salario medio para cada tecnología
    for col in tech_columns:
        tech_name = col.replace('has_', '')
        salary_with_tech = jobs_df[jobs_df[col] == True]['salary']
        salary_without_tech = jobs_df[jobs_df[col] == False]['salary']
        
        if len(salary_with_tech) > 0 and len(salary_without_tech) > 0:
            # Estadísticas descriptivas
            comparison_results[tech_name] = {
                'with_tech': {
                    'count': len(salary_with_tech),
                    'mean': salary_with_tech.mean(),
                    'median': salary_with_tech.median(),
                    'std': salary_with_tech.std()
                },
                'without_tech': {
                    'count': len(salary_without_tech),
                    'mean': salary_without_tech.mean(),
                    'median': salary_without_tech.median(),
                    'std': salary_without_tech.std()
                }
            }
            
            # Prueba T para diferencia significativa
            try:
                t_stat, p_value = stats.ttest_ind(salary_with_tech.dropna(), salary_without_tech.dropna(),
                                                equal_var=False)
                comparison_results[tech_name]['t_test'] = {
                    't_statistic': t_stat,
                    'p_value': p_value,
                    'significant_difference': p_value < 0.05  # Diferencia significativa
                }
            except:
                comparison_results[tech_name]['t_test'] = {
                    'error': 'No se pudo realizar la prueba t'
                }
    
    # Crear visualización
    if comparison_results:
        techs = list(comparison_results.keys())
        mean_with_tech = [comparison_results[tech]['with_tech']['mean'] for tech in techs]
        mean_without_tech = [comparison_results[tech]['without_tech']['mean'] for tech in techs]
        
        plt.figure(figsize=(12, 8))
        
        x = np.arange(len(techs))
        width = 0.35
        
        plt.bar(x - width/2, mean_with_tech, width, label='With Technology')
        plt.bar(x + width/2, mean_without_tech, width, label='Without Technology')
        
        plt.xlabel('Technology', fontsize=12)
        plt.ylabel('Mean Salary', fontsize=12)
        plt.title('Salary Comparison by Technology', fontsize=16)
        plt.xticks(x, [tech.capitalize() for tech in techs], rotation=45)
        plt.legend()
        plt.tight_layout()
        
        ensure_dirs()
        comp_path = os.path.join(IMG_DIR, 'technology_salary_comparison.png')
        plt.savefig(comp_path)
        plt.close()
        
        comparison_results['plot_path'] = comp_path
    
    return comparison_results

def run_statistical_analysis():
    """Ejecutar el proceso completo de análisis estadístico."""
    logger.info("Iniciando Análisis Estadístico...")
    
    # Cargar datos procesados
    jobs_df, survey_df = load_processed_data()
    
    # Descriptive statistics
    job_stats = descriptive_stats_jobs(jobs_df)
    survey_stats = descriptive_stats_survey(survey_df)
    
    # Análisis de correlación
    salary_correlations_jobs = {}
    if 'salary' in jobs_df.columns:
        numerical_cols = [col for col in jobs_df.select_dtypes(include=['int64', 'float64']).columns 
                        if col != 'salary']
        salary_correlations_jobs = correlation_analysis(jobs_df, 'salary', numerical_cols)
    
    salary_correlations_survey = {}
    if 'salary' in survey_df.columns:
        numerical_cols = [col for col in survey_df.select_dtypes(include=['int64', 'float64']).columns 
                        if col != 'salary']
        salary_correlations_survey = correlation_analysis(survey_df, 'salary', numerical_cols)
    
    # Análisis de regresión
    salary_regression = {}
    if 'salary' in survey_df.columns and 'years_coding' in survey_df.columns:
        salary_regression = salary_regression_analysis(survey_df, 'years_coding')
    
    # Comparación de salarios por tecnología
    tech_salary_comp = {}
    if 'salary' in jobs_df.columns:
        tech_salary_comp = tech_salary_comparison(jobs_df)
    
    # Compilar todos los resultados
    analysis_results = {
        'job_stats': job_stats,
        'survey_stats': survey_stats,
        'salary_correlations_jobs': salary_correlations_jobs,
        'salary_correlations_survey': salary_correlations_survey,
        'salary_regression': salary_regression,
        'tech_salary_comparison': tech_salary_comp
    }
    
    logger.info("Análisis estadístico completado exitosamente.")
    
    return analysis_results

if __name__ == "__main__":
    run_statistical_analysis()
