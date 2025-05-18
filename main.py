"""
Script principal para el proyecto de Análisis del Mercado Laboral Tecnológico.

Este script ejecuta el pipeline completo de datos incluyendo:
1. Web Scraping de ofertas de empleo
2. ETL (Extracción, Transformación, Carga)
3. EDA (Análisis Exploratorio de Datos)
4. Análisis Estadístico

Ejecuta este script para procesar el flujo de trabajo completo del proyecto.
"""

import os
import sys
import logging
import time
import argparse
from pathlib import Path

# Agregar el directorio raíz al path para importaciones
sys.path.append(str(Path(__file__).parent))

# Importar funciones esenciales
from src.data_generator import generar_datos_simulados
from src.data_collector import fetch_real_job_data
from src.etl import run_etl_pipeline
from src.eda import run_eda
from src.stats import run_statistical_analysis

# Importar JobScraper solo si existe selenium (importación condicional)
def get_job_scraper():
    """Obtener la clase JobScraper si selenium está disponible."""
    try:
        from src.scraper import JobScraper
        return JobScraper
    except ImportError:
        logger.warning("Selenium no está instalado. La funcionalidad de web scraping no estará disponible.")
        return None

# Configurar el registro
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('job_analysis.log')
    ]
)
logger = logging.getLogger(__name__)

def setup_directories():
    """Crear los directorios necesarios para el proyecto."""
    dirs = [
        'data/raw',
        'data/processed',
        'data/external',
        'notebooks',
        'reports',
        'img/eda',
        'img/stats'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        logger.debug(f"Directorio creado/verificado: {dir_path}")

def run_scraping(keywords=None, max_pages=2, headless=True):
    """Ejecutar el proceso de web scraping.
    
    Args:
        keywords (list): Lista de palabras clave para buscar.
        max_pages (int): Número máximo de páginas a extraer por palabra clave.
        headless (bool): Si es True, ejecuta el navegador en modo sin interfaz.
    """
    # Obtener la clase JobScraper si está disponible
    JobScraperClass = get_job_scraper()
    if JobScraperClass is None:
        logger.error("No se puede realizar web scraping: Selenium no está instalado.")
        logger.info("Sugerencia: Ejecute 'pip install selenium webdriver-manager' o use la opción '--simulacion' para generar datos simulados.")
        return
    
    if keywords is None:
        keywords = [
            'desarrollador', 
            'data scientist', 
            'analista datos', 
            'ingeniero software',
            'devops'
        ]
    
    logger.info("Iniciando proceso de web scraping...")
    scraper = JobScraperClass(headless=headless)
    
    try:
        scraper.scrape_infojobs(
            keyword=keywords[0],  # Usar solo la primera palabra clave para el ejemplo
            max_pages=min(max_pages, 3)  # Limitar a 3 páginas como máximo
        )
        logger.info("Proceso de web scraping completado exitosamente.")
    except Exception as e:
        logger.error(f"Error durante el web scraping: {str(e)}", exc_info=True)
    finally:
        scraper.close_driver()

def run_simulation(num_ofertas=100, num_encuestas=200):
    """Generar datos simulados para el análisis.
    
    Args:
        num_ofertas (int): Número de ofertas de empleo simuladas a generar.
        num_encuestas (int): Número de encuestas simuladas a generar.
    """
    logger.info(f"Iniciando generación de datos simulados ({num_ofertas} ofertas, {num_encuestas} encuestas)...")
    try:
        ofertas_df, encuestas_df = generar_datos_simulados(num_ofertas, num_encuestas)
        logger.info(f"Generados {len(ofertas_df)} ofertas de empleo simuladas")
        logger.info(f"Generadas {len(encuestas_df)} encuestas de desarrolladores simuladas")
        logger.info("Proceso de generación de datos simulados completado exitosamente.")
    except Exception as e:
        logger.error(f"Error durante la generación de datos simulados: {str(e)}", exc_info=True)

def run_real_data_collection():
    """Recopilar datos REALES de ofertas de empleo de la web para el análisis del mercado laboral."""
    logger.info("Iniciando recopilación de datos REALES para análisis de mercado laboral...")
    try:
        # Definir consultas para abarcar diversos tipos de empleos tecnológicos
        keywords = [
            'python developer', 
            'data scientist',
            'software engineer',
            'frontend developer', 
            'backend developer',
            'machine learning', 
            'devops',
            'full stack developer'
        ]
        
        logger.info("Obteniendo datos REALES de la web... (esto puede tardar un momento)")
        
        # Obtener datos REALES (no simulados) de la web
        jobs_df, survey_df = fetch_real_job_data(use_apis=True, download_survey=True, keywords=keywords)
        
        if not jobs_df.empty:
            logger.info(f"Obtenidas {len(jobs_df)} ofertas de empleo REALES para análisis")
        else:
            logger.warning("No se pudieron obtener ofertas de empleo reales")
            
        if not survey_df.empty:
            # Por ahora, los datos de encuesta son simulados porque las encuestas reales son difíciles de obtener
            logger.info(f"Datos de encuesta generados con {len(survey_df)} respuestas")
        else:
            logger.warning("No se pudieron obtener datos de encuesta")
            
        logger.info("Proceso de recopilación de datos REALES completado.")
        
    except Exception as e:
        logger.error(f"Error durante la recopilación de datos reales: {str(e)}", exc_info=True)

def parse_arguments():
    """Parsear los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description='Analizar el mercado laboral tecnológico')
    
    # Grupo de fuentes de datos (opciones mutuamente excluyentes)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--scrape', action='store_true', help='Ejecutar web scraping (Opción 1)')
    group.add_argument('--simulacion', action='store_true', help='Generar datos simulados (Opción 2)')
    group.add_argument('--datos-reales', action='store_true', help='Recopilar datos reales de APIs (Opción 3 - Recomendada)')
    
    # Parámetros para simulación
    parser.add_argument('--num-ofertas', type=int, default=100, help='Número de ofertas simuladas a generar')
    parser.add_argument('--num-encuestas', type=int, default=200, help='Número de encuestas simuladas a generar')
    
    # Parámetros para web scraping
    parser.add_argument('--headless', action='store_true', help='Ejecutar navegador en modo sin interfaz')
    parser.add_argument('--max-pages', type=int, default=2, help='Número máximo de páginas a extraer')
    
    # Etapas de análisis
    parser.add_argument('--etl', action='store_true', help='Ejecutar ETL')
    parser.add_argument('--eda', action='store_true', help='Ejecutar análisis exploratorio')
    parser.add_argument('--stats', action='store_true', help='Ejecutar análisis estadístico')
    parser.add_argument('--all', action='store_true', help='Ejecutar todo el pipeline')
    
    return parser.parse_args()

def main():
    """Ejecutar el pipeline completo de datos."""
    start_time = time.time()
    args = parse_arguments()
    
    # Configurar nivel de logging
    logging.getLogger().setLevel(logging.INFO)
    
    logger.info("Iniciando el pipeline de Análisis del Mercado Laboral Tecnológico...")
    
    # Configurar directorios
    setup_directories()
    
    # Flag para saber si se obtuvieron datos
    datos_obtenidos = False
    
    # Ejecutar procesos según los argumentos:
    # 1. Primero recolectar/generar los datos según la opción seleccionada
    
    # OPCIÓN 3 (PRIORITARIA): Datos reales de APIs (sin captchas ni bloqueos)
    if args.datos_reales or (args.all and not (args.scrape or args.simulacion)):
        logger.info("Usando fuente de datos REAL a través de APIs (sin captchas ni bloqueos)")
        run_real_data_collection()
        datos_obtenidos = True
    
    # OPCIÓN 2: Datos simulados (si no se usa la opción de datos reales)
    elif args.simulacion:
        logger.info("Usando fuente de datos SIMULADOS (datos sintéticos de alta calidad)")
        run_simulation(num_ofertas=args.num_ofertas, num_encuestas=args.num_encuestas)
        datos_obtenidos = True
    
    # OPCIÓN 1: Web Scraping (ahora en última prioridad debido a los captchas y bloqueos)
    elif args.scrape:
        logger.warning("ADVERTENCIA: El web scraping puede ser bloqueado por captchas")
        logger.info("Se recomienda usar '--datos-reales' para evitar bloqueos")
        prompt = input("¿Desea continuar con web scraping a pesar del riesgo de captchas? (s/n): ")
        if prompt.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            run_scraping(max_pages=args.max_pages, headless=args.headless)
            datos_obtenidos = True
        else:
            logger.info("Se recomienda usar: python main.py --datos-reales --all")
            return
    else:
        # Si no se especificó ninguna fuente de datos pero se pidió análisis
        if any([args.etl, args.eda, args.stats]):
            # Usar datos reales por defecto
            logger.info("No se especificó fuente de datos. Usando DATOS REALES por defecto.")
            run_real_data_collection()
            datos_obtenidos = True
        else:
            # No se especificó ninguna acción
            logger.info("No se especificó ninguna acción o fuente de datos.")
            logger.info("Se recomienda: python main.py --datos-reales --all")
            return
        
    # Verificar si se obtuvieron datos
    if not datos_obtenidos:
        logger.error("No se pudieron obtener datos. El pipeline no puede continuar.")
        return
    
    # 2. Luego procesar y analizar los datos
    
    # Proceso ETL
    if args.all or args.etl:
        logger.info("Iniciando proceso ETL...")
        try:
            run_etl_pipeline()
            logger.info("Proceso ETL completado exitosamente.")
        except Exception as e:
            logger.error(f"Error durante el ETL: {str(e)}", exc_info=True)
    
    # Análisis Exploratorio
    if args.all or args.eda:
        logger.info("Iniciando Análisis Exploratorio de Datos...")
        try:
            run_eda()
            logger.info("Análisis Exploratorio completado exitosamente.")
        except Exception as e:
            logger.error(f"Error durante el EDA: {str(e)}", exc_info=True)
    
    # Análisis Estadístico
    if args.all or args.stats:
        logger.info("Iniciando Análisis Estadístico...")
        try:
            run_statistical_analysis()
            logger.info("Análisis Estadístico completado exitosamente.")
        except Exception as e:
            logger.error(f"Error durante el análisis estadístico: {str(e)}", exc_info=True)
    
    # Mostrar resumen
    execution_time = (time.time() - start_time) / 60
    logger.info(f"Proceso completado en {execution_time:.2f} minutos")
    
    # Mensaje final
    print("\n" + "="*80)
    print("RESULTADO DEL ANÁLISIS DEL MERCADO LABORAL TECNOLÓGICO")
    print("="*80)
    print(f"Tiempo de ejecución: {execution_time:.2f} minutos")
    print("\nResultados disponibles en:")
    print("- Datos procesados: ./data/processed/")
    print("- Visualizaciones: ./img/")
    print("- Informes: ./reports/")
    print("\nPara ver análisis detallados, ejecute el notebook:")
    print("jupyter notebook ./notebooks/exploratory_analysis.ipynb")
    print("="*80)

if __name__ == "__main__":
    main()
