#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pipeline completo para optimización del modelo de predicción de salarios:
1. Ejecuta el scraping de datos desde InfoJobs y otras fuentes
2. Ejecuta el proceso ETL para transformar los datos
3. Entrena un modelo optimizado de predicción de salarios
"""
import logging
import os
import sys
import time
from pathlib import Path

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'pipeline_{int(time.time())}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('pipeline_trainer')

def run_data_collection():
    """Ejecuta el proceso de recolección de datos desde múltiples fuentes"""
    logger.info("="*80)
    logger.info("FASE 1: RECOLECCIÓN DE DATOS")
    logger.info("="*80)
    
    # Scraper de InfoJobs
    try:
        from src.scraper import main as run_scraper
        logger.info("Ejecutando scraper de InfoJobs...")
        run_scraper()
        logger.info("Scraper de InfoJobs completado con éxito.")
    except Exception as e:
        logger.error(f"Error al ejecutar el scraper de InfoJobs: {str(e)}")
    
    # Recolección desde APIs y encuestas
    try:
        from src.data_collector import fetch_real_job_data
        logger.info("Recopilando datos desde APIs y encuestas...")
        fetch_real_job_data(use_apis=True, download_survey=True)
        logger.info("Recolección desde APIs y encuestas completada.")
    except Exception as e:
        logger.error(f"Error en la recolección de datos desde APIs: {str(e)}")
    
    logger.info("Fase de recolección de datos finalizada.")
    
def run_etl_process():
    """Ejecuta el proceso ETL para transformar y cargar los datos"""
    logger.info("\n" + "="*80)
    logger.info("FASE 2: PROCESO ETL")
    logger.info("="*80)
    
    try:
        from src.etl import run_etl
        logger.info("Ejecutando proceso ETL...")
        run_etl()
        logger.info("Proceso ETL completado con éxito.")
    except Exception as e:
        logger.error(f"Error en el proceso ETL: {str(e)}")
        raise
    
def train_model():
    """Entrena el modelo de predicción de salarios optimizado"""
    logger.info("\n" + "="*80)
    logger.info("FASE 3: ENTRENAMIENTO DEL MODELO")
    logger.info("="*80)
    
    try:
        from src.model_salary import train_salary_model
        logger.info("Entrenando modelo de predicción de salarios...")
        train_salary_model()
        logger.info("Entrenamiento del modelo completado con éxito.")
    except Exception as e:
        logger.error(f"Error en el entrenamiento del modelo: {str(e)}")
        raise

def verify_model_improvement():
    """Verifica la mejora del modelo comparando métricas"""
    logger.info("\n" + "="*80)
    logger.info("FASE 4: VERIFICACIÓN DE MEJORAS")
    logger.info("="*80)
    
    try:
        import joblib
        import pandas as pd
        from pathlib import Path
        
        model_path = Path('models/salary_model.joblib')
        if not model_path.exists():
            logger.error("No se encontró el modelo entrenado para verificar.")
            return
        
        metadata = joblib.load(model_path)
        metrics = metadata.get('metrics', {})
        
        logger.info("Métricas del modelo actual:")
        logger.info(f"  - MAE: {metrics.get('mae', 'N/A'):.2f}")
        logger.info(f"  - RMSE: {metrics.get('rmse', 'N/A'):.2f}")
        logger.info(f"  - R²: {metrics.get('r2', 'N/A'):.4f}")
        
        # Comparativa con métricas anteriores (si existen)
        csv_path = Path('models/performance_history.csv')
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                if not df.empty:
                    last_metrics = df.iloc[-1]
                    logger.info("\nComparativa con modelo anterior:")
                    mae_diff = metrics.get('mae', 0) - last_metrics.get('mae', 0)
                    r2_diff = metrics.get('r2', 0) - last_metrics.get('r2', 0)
                    logger.info(f"  - Cambio en MAE: {mae_diff:.2f} ({'-' if mae_diff < 0 else '+'}{abs(mae_diff/last_metrics.get('mae', 1)*100):.1f}%)")
                    logger.info(f"  - Cambio en R²: {r2_diff:.4f} ({'+' if r2_diff > 0 else '-'}{abs(r2_diff/max(0.001, last_metrics.get('r2', 0.001))*100):.1f}%)")
            except Exception as e:
                logger.warning(f"No se pudieron comparar con métricas anteriores: {str(e)}")
        
        # Guardar métricas actuales para comparaciones futuras
        df_new = pd.DataFrame([{
            'timestamp': pd.Timestamp.now().isoformat(),
            'mae': metrics.get('mae', 0),
            'median_ae': metrics.get('median_ae', 0),
            'rmse': metrics.get('rmse', 0),
            'r2': metrics.get('r2', 0),
            'mae_train': metrics.get('mae_train', 0),
            'r2_train': metrics.get('r2_train', 0),
        }])
        
        if csv_path.exists():
            df_existing = pd.read_csv(csv_path)
            df_combined = pd.concat([df_existing, df_new])
            df_combined.to_csv(csv_path, index=False)
        else:
            Path('models').mkdir(exist_ok=True)
            df_new.to_csv(csv_path, index=False)
            
        logger.info(f"Métricas guardadas en {csv_path}")
        
    except Exception as e:
        logger.error(f"Error al verificar mejoras del modelo: {str(e)}")

def run_full_pipeline():
    """Ejecuta el pipeline completo de entrenamiento"""
    start_time = time.time()
    logger.info("Iniciando pipeline completo de entrenamiento...")
    
    try:
        # Fase 1: Recolección de datos 
        run_data_collection()
        
        # Fase 2: Proceso ETL
        run_etl_process()
        
        # Fase 3: Entrenamiento del modelo
        train_model()
        
        # Fase 4: Verificación de mejoras
        verify_model_improvement()
        
        elapsed_time = time.time() - start_time
        logger.info(f"Pipeline completo ejecutado con éxito en {elapsed_time:.2f} segundos.")
        
    except Exception as e:
        logger.error(f"Error en el pipeline completo: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    run_full_pipeline()
