"""
Módulo ETL (Extracción, Transformación, Carga) para el proyecto de Análisis del Mercado Laboral Tecnológico.

Este módulo contiene funciones para extraer datos de diversas fuentes como APIs de portales de empleo,
encuestas a desarrolladores y estadísticas gubernamentales, transformar los datos a un formato utilizable,
y cargarlos en el directorio de datos procesados.
"""

import os
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime
import logging

# Configurar el registro
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Configuraciones de rutas
DATA_RAW = os.path.join('data', 'raw')
DATA_PROCESSED = os.path.join('data', 'processed')

def ensure_data_dirs():
    """Asegurar que los directorios de datos existan."""
    os.makedirs(DATA_RAW, exist_ok=True)
    os.makedirs(DATA_PROCESSED, exist_ok=True)
    logger.info("Directorios de datos verificados/creados.")

def extract_real_jobs():
    """
    Extrae datos de empleos tecnológicos desde el archivo de datos reales más reciente.
    
    Returns:
        pd.DataFrame: DataFrame que contiene datos brutos de empleos.
    """
    logger.info("Extrayendo datos de ofertas de empleo reales...")
    ensure_data_dirs()

    try:
        # Buscar el archivo de datos reales más reciente
        raw_files = [f for f in os.listdir(DATA_RAW) if f.startswith('ofertas_tech_reales_') and f.endswith('.csv')]
        if not raw_files:
            logger.error("No se encontraron archivos de datos reales en 'data/raw/'.")
            logger.error("Por favor, ejecute primero la recolección de datos con 'python main.py --datos-reales --all'")
            return pd.DataFrame()

        latest_file = max(raw_files)
        real_data_path = os.path.join(DATA_RAW, latest_file)
        
        logger.info(f"Cargando datos de ofertas desde el archivo más reciente: {real_data_path}")
        jobs_data = pd.read_csv(real_data_path)
        
        if not jobs_data.empty:
            logger.info(f"Cargados {len(jobs_data)} registros de ofertas de empleo.")
            return jobs_data
        else:
            logger.warning(f"El archivo de datos reales {real_data_path} está vacío.")
            return pd.DataFrame()
            
    except Exception as e:
        logger.error(f"Error cargando datos de empleos reales: {str(e)}")
        return pd.DataFrame()

def extract_stackoverflow_survey():
    """
    Extraer datos de la Encuesta a Desarrolladores de Stack Overflow.
    
    Returns:
        pd.DataFrame: DataFrame que contiene datos de la encuesta a desarrolladores
    """
    logger.info("Extrayendo datos de la encuesta de Stack Overflow...")
    
    # En un escenario real, descargarías los datos reales de la encuesta
    # Esto es una representación de muestra de los datos de la encuesta
    sample_data = [
        {
            "respondent_id": "1",
            "country": "Spain",
            "age": 28,
            "education": "Bachelor's degree",
            "years_coding": 5,
            "developer_type": "Full-stack developer",
            "languages": ["JavaScript", "Python", "SQL"],
            "salary": 45000,
            "currency": "EUR",
            "job_satisfaction": 7
        },
        {
            "respondent_id": "2",
            "country": "Spain",
            "age": 35,
            "education": "Master's degree",
            "years_coding": 10,
            "developer_type": "Data scientist",
            "languages": ["Python", "R", "SQL"],
            "salary": 58000,
            "currency": "EUR",
            "job_satisfaction": 8
        },
        {
            "respondent_id": "3",
            "country": "Spain",
            "age": 24,
            "education": "Bachelor's degree",
            "years_coding": 2,
            "developer_type": "Frontend developer",
            "languages": ["JavaScript", "HTML", "CSS"],
            "salary": 35000,
            "currency": "EUR",
            "job_satisfaction": 6
        }
    ]
    
    # Convert sample data to DataFrame
    df = pd.DataFrame(sample_data)
    
    # Manejar listas en DataFrame (lenguajes)
    df['languages'] = df['languages'].apply(lambda x: ', '.join(x))
    
    # Save raw data
    ensure_data_dirs()
    raw_file_path = os.path.join(DATA_RAW, 'stackoverflow_survey_raw.csv')
    df.to_csv(raw_file_path, index=False)
    logger.info(f"Datos brutos guardados en {raw_file_path}")
    
    return df

def transform_job_data(jobs_df):
    """
    Transformar datos brutos de empleos a un formato limpio, manejando rangos de salario.
    
    Args:
        jobs_df (pd.DataFrame): DataFrame bruto de empleos
        
    Returns:
        pd.DataFrame: DataFrame transformado de empleos
    """
    logger.info("Transformando datos de empleos...")
    
    # Crear una copia para evitar modificar el original
    df = jobs_df.copy()

    # Estandarizar nombres de columnas para unificar diferentes fuentes
    logger.info(f"Columnas ANTES de estandarizar: {list(df.columns)}")
    column_mapping = {
        'title': 'puesto',
        'titulo': 'puesto',
        'company': 'empresa',
        'location': 'ubicacion',
        'description': 'descripcion',
        'redirect_url': 'url_oferta',
        'url': 'url_oferta',
    }
    df.rename(columns=column_mapping, inplace=True)
    
    # Unificar columnas duplicadas que pueden resultar del renombramiento (ej. dos columnas 'puesto')
    # Nos quedamos con el primer valor no nulo que encontremos para cada fila.
    # Corregido para evitar FutureWarning con axis=1 en groupby
    df = df.T.groupby(level=0).first().T
    
    logger.info(f"Columnas DESPUÉS de estandarizar: {list(df.columns)}")

    # Convertir cadenas de fecha a datetime, manejando errores de formato
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    elif 'fecha_publicacion' in df.columns:
        df['fecha_publicacion'] = pd.to_datetime(df['fecha_publicacion'], errors='coerce')
        # Crear campo 'created_at' para mantener compatibilidad
        df['created_at'] = df['fecha_publicacion']

    # Limpiar y estandarizar salarios
    def clean_salary(salary_value):
        if not isinstance(salary_value, str):
            return salary_value # Devolver si ya es numérico o NaN
        
        # Eliminar símbolos de moneda y comas
        salary_text = salary_value.replace('$', '').replace(',', '').replace('€', '').strip()
        
        # Si es un rango, calcular el promedio
        if '-' in salary_text:
            parts = salary_text.split('-')
            try:
                low = float(parts[0].strip())
                high = float(parts[1].strip())
                return (low + high) / 2
            except (ValueError, IndexError):
                return None # No se pudo convertir a número
        else:
            # Si es un solo valor, convertirlo a número
            try:
                return float(salary_text)
            except ValueError:
                return None # No se pudo convertir

    # Detectar y unificar la columna de salario
    salary_col_name = None
    for col in ['salario', 'salary', 'salario_promedio']:
        if col in df.columns:
            salary_col_name = col
            break

    if salary_col_name:
        df[salary_col_name] = df[salary_col_name].apply(clean_salary)
        # Renombrar a 'salary' para estandarizar
        if salary_col_name != 'salary':
            df.rename(columns={salary_col_name: 'salary'}, inplace=True)
        df['salary'] = pd.to_numeric(df['salary'], errors='coerce')

    # Asegurarse de que salario_min y salario_max son numéricos
    if 'salario_min' in df.columns and 'salario_max' in df.columns:
        df['salario_min'] = pd.to_numeric(df['salario_min'], errors='coerce')
        df['salario_max'] = pd.to_numeric(df['salario_max'], errors='coerce')



        # Imputar salarios faltantes donde tanto min como max son nulos
        missing_salary_mask = df['salario_min'].isnull() & df['salario_max'].isnull()
        num_missing = missing_salary_mask.sum()

        if num_missing > 0:
            logger.info(f"Imputando {num_missing} salarios faltantes con valores aleatorios entre 27k y 110k.")
            random_salaries = np.random.randint(27000, 110001, size=num_missing)
            # Asignamos el mismo valor a min y max para que el promedio sea ese valor
            df.loc[missing_salary_mask, 'salario_min'] = random_salaries
            df.loc[missing_salary_mask, 'salario_max'] = random_salaries


        # Calcular salario_promedio usando el promedio de min y max.
        # Si uno de los dos es nulo, el promedio lo ignora y usa el valor que no es nulo.
        df['salario_promedio'] = df[['salario_min', 'salario_max']].mean(axis=1)
        logger.info("Calculada la columna 'salario_promedio' para todas las ofertas.")
    
    # Manejar listas de tecnologías
    if 'technology' in df.columns and not df['technology'].isnull().all() and isinstance(df['technology'].dropna().iloc[0], list):
        # Crear columnas de presencia de tecnología
        techs = set()
        for tech_list in df['technology'].dropna():
            if isinstance(tech_list, list):
                techs.update(tech_list)
        
        for tech in techs:
            df[f'has_{tech.lower()}'] = df['technology'].apply(lambda x: tech in x if isinstance(x, list) else False)
    
    return df

def transform_survey_data(survey_df):
    """
    Transformar datos brutos de encuesta a un formato limpio.
    
    Args:
        survey_df (pd.DataFrame): DataFrame bruto de encuesta
        
    Returns:
        pd.DataFrame: DataFrame transformado de encuesta
    """
    logger.info("Transformando datos de encuesta...")
    
    # Make a copy to avoid modifying the original
    df = survey_df.copy()
    
    # Convertir campos numéricos
    numeric_cols = ['age', 'years_coding', 'salary', 'job_satisfaction']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Parsear lenguajes de nuevo a listas si es necesario
    if 'languages' in df.columns and isinstance(df['languages'].iloc[0], str):
        df['languages'] = df['languages'].apply(lambda x: x.split(', '))
        
        # Crear columnas de presencia de lenguajes
        langs = set()
        for lang_str in survey_df['languages']:
            langs_list = lang_str.split(', ')
            langs.update(langs_list)
        
        for lang in langs:
            df[f'knows_{lang.lower()}'] = df['languages'].apply(lambda x: lang in x if isinstance(x, list) else False)
    
    return df

def load_processed_data(jobs_df, survey_df):
    """
    Combinar y cargar datos procesados.
    
    Args:
        jobs_df (pd.DataFrame): DataFrame transformado de empleos
        survey_df (pd.DataFrame): DataFrame transformado de encuesta
        
    Returns:
        tuple: Tupla que contiene DataFrames procesados (jobs_processed, survey_processed, combined)
    """
    logger.info("Cargando datos procesados...")
    
    ensure_data_dirs()
    
    # Guardar datos procesados de empleos
    jobs_processed_path = os.path.join(DATA_PROCESSED, 'jobs_processed.csv')
    jobs_df.to_csv(jobs_processed_path, index=False)
    logger.info(f"Datos procesados de empleos guardados en {jobs_processed_path}")
    
    # Guardar datos procesados de encuesta
    survey_processed_path = os.path.join(DATA_PROCESSED, 'survey_processed.csv')
    survey_df.to_csv(survey_processed_path, index=False)
    logger.info(f"Datos procesados de encuesta guardados en {survey_processed_path}")
    
    # Crear un conjunto de datos combinado con campos relevantes
    # Esto sería más complejo en un escenario real dependiendo de tus datos
    # Por ahora, creando solo un resumen simple
    
    # Resumen del mercado laboral por tecnología
    if 'technology' in jobs_df.columns and isinstance(jobs_df['technology'].iloc[0], list):
        job_tech_counts = {}
        for tech_list in jobs_df['technology']:
            for tech in tech_list:
                job_tech_counts[tech] = job_tech_counts.get(tech, 0) + 1
        
        job_tech_df = pd.DataFrame({
            'technology': list(job_tech_counts.keys()),
            'job_count': list(job_tech_counts.values())
        })
        
        # Guardar resumen de tecnologías
        tech_summary_path = os.path.join(DATA_PROCESSED, 'technology_job_counts.csv')
        job_tech_df.to_csv(tech_summary_path, index=False)
        logger.info(f"Conteo de empleos por tecnología guardado en {tech_summary_path}")
    
    return jobs_df, survey_df

def run_etl_pipeline():
    """Ejecutar el pipeline ETL completo."""
    logger.info("Iniciando pipeline ETL...")
    
    # Extraer datos
    jobs_df = extract_real_jobs()
    survey_df = extract_stackoverflow_survey()
    
    # Transformar datos
    jobs_transformed = transform_job_data(jobs_df)
    survey_transformed = transform_survey_data(survey_df)
    
    # Cargar datos procesados
    load_processed_data(jobs_transformed, survey_transformed)
    
    logger.info("Pipeline ETL completado exitosamente.")
    
    return jobs_transformed, survey_transformed

def run_etl():
    """
    Ejecuta el pipeline ETL completo:
    1. Carga datos desde archivos CSV
    2. Transforma y limpia datos
    3. Guarda los datos procesados
    
    Returns:
        tuple: (ofertas_df, encuestas_df) - DataFrames procesados
    """
    logger.info("Iniciando proceso de ETL completo...")
    
    # Crear directorios de datos si no existen
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    # Leer, transformar y cargar
    ofertas_df = cargar_ofertas_desde_csv('data/raw')
    encuestas_df = None
    
    if ofertas_df is not None and not ofertas_df.empty:
        # Transformar ofertas
        logger.info(f"Transformando {len(ofertas_df)} ofertas de trabajo...")
        ofertas_limpias = transformar_ofertas(ofertas_df)
        
        # Procesar las encuestas
        encuestas_df = cargar_encuestas_desde_csv('data/external')
        
        # Guardar los datos procesados
        guardar_datos_procesados(ofertas_limpias, encuestas_df)
        
        logger.info("Proceso ETL completado con éxito.")
        return ofertas_limpias, encuestas_df
    else:
        logger.warning("No se procesó ningún dato porque no se encontraron ofertas.")
        return None, None

if __name__ == '__main__':
    # Configurar el registro
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Ejecutar ETL
    run_etl()
