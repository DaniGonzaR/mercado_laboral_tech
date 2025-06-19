'''
Model training script for salary prediction.
This script loads processed job data, performs basic feature engineering and trains
an ML model (GradientBoostingRegressor) to predict salary based on job features.
The trained pipeline is persisted with joblib in models/salary_model.joblib so it
can be loaded by the Streamlit dashboard for inference.
'''
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
import logging
import re
import numpy as np

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error, median_absolute_error
from sklearn.model_selection import train_test_split, RandomizedSearchCV, KFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.feature_selection import SelectFromModel

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATA_PATH = Path('data') / 'processed' / 'jobs_processed.csv'
MODEL_DIR = Path('models')
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / 'salary_model.joblib'

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helper functions to detect column names
# ---------------------------------------------------------------------------

def determine_salary_column(df: pd.DataFrame) -> str | None:
    for col in ['salario_promedio', 'salary', 'salario']:
        if col in df.columns and df[col].notna().any():
            return col
    return None


def determine_location_column(df: pd.DataFrame) -> str | None:
    for col in ['ubicacion', 'location']:
        if col in df.columns and df[col].notna().any():
            return col
    return None


def determine_contract_column(df: pd.DataFrame) -> str | None:
    for col in ['tipo_contrato', 'jornada', 'contract_type']:
        if col in df.columns and df[col].notna().any():
            return col
    return None

def determine_title_column(df: pd.DataFrame) -> str | None:
    for col in ['titulo', 'job_title']:
        if col in df.columns and df[col].notna().any():
            return col
    return None

# ---------------------------------------------------------------------------
# Feature Engineering
# ---------------------------------------------------------------------------

def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Performs feature engineering on the raw data.
    - Extracts seniority, role type, and specific technologies from job title and description
    - Creates one-hot encoded features for technologies
    - Extracts location features
    - Creates numerical features from text data
    """
    logger.info("Iniciando preprocesamiento y feature engineering avanzado...")
    
    title_col = determine_title_column(data)
    desc_col = None
    for col in ['descripcion', 'description', 'requisitos', 'requirements']:
        if col in data.columns and data[col].notna().any():
            desc_col = col
            break

    # --- 1. Seniority and Role Type from Title ---
    if title_col:
        # Extraer nivel de seniority con categorías más específicas
        data['seniority_senior'] = data[title_col].str.contains(
            r'senior|sr\.|lead\b|principal|architect|head|staff|director', case=False, na=False).astype(int)
        data['seniority_mid'] = data[title_col].str.contains(
            r'\bmid|\bmiddle|\bII\b|\b2\b', case=False, na=False).astype(int)
        data['seniority_junior'] = data[title_col].str.contains(
            r'junior|jr\.|intern\b|trainee|graduate|entry|associate', case=False, na=False).astype(int)
        
        # Detectar tipos de roles técnicos específicos
        data['role_frontend'] = data[title_col].str.contains(
            r'front|frontend|front-end|ui|react|angular|vue', case=False, na=False).astype(int)
        data['role_backend'] = data[title_col].str.contains(
            r'back|backend|back-end|api|node|django|flask|spring', case=False, na=False).astype(int)
        data['role_fullstack'] = data[title_col].str.contains(
            r'full|fullstack|full-stack|full stack', case=False, na=False).astype(int)
        data['role_data'] = data[title_col].str.contains(
            r'data|analytic|business intelligence|bi|analyst', case=False, na=False).astype(int)
        data['role_devops'] = data[title_col].str.contains(
            r'devops|sre|reliability|cloud|aws|azure|platform', case=False, na=False).astype(int)
        data['role_manager'] = data[title_col].str.contains(
            r'manager|director|head|lead|chief|cto', case=False, na=False).astype(int)
        
        logger.info("Creadas columnas extendidas de seniority y tipo de rol")

    # --- 2. Extract information from description ---
    if desc_col:
        # Detectar años de experiencia requeridos
        exp_pattern = r'([0-9]+)[\s-]*(?:a[ñn]os?|years?|\+)[\s\w]*experienc[ei]a'
        data['required_years_exp'] = data[desc_col].str.extract(exp_pattern, flags=re.IGNORECASE)
        data['required_years_exp'] = pd.to_numeric(data['required_years_exp'], errors='coerce')
        # Si todos son NaN después de la conversión, crear una columna con un valor predeterminado de 2 años
        if data['required_years_exp'].isna().all():
            logger.info("No se encontraron años de experiencia en las descripciones. Usando valor predeterminado.")
            data['required_years_exp'] = 2
        else:
            data['required_years_exp'] = data['required_years_exp'].fillna(data['required_years_exp'].median())
        
        # Detectar características del trabajo remoto
        data['is_remote'] = data[desc_col].str.contains(
            r'remot[eo]|teletrabaj[oa]|work from home', case=False, na=False).astype(int)
        data['has_flexibility'] = data[desc_col].str.contains(
            r'flexi|horario flexible|flexible hours', case=False, na=False).astype(int)
        
        # Detectar educación requerida
        data['requires_degree'] = data[desc_col].str.contains(
            r'degree|título|licenciatura|grado|ingenier[íi]a|universidad', case=False, na=False).astype(int)
        
        logger.info("Extraída información de experiencia, trabajo remoto y educación de la descripción")

    # --- 3. Extended One-Hot Encoding for Technologies ---
    # Buscar tecnologías tanto en la columna dedicada como en la descripción
    all_tech_mentions = data['tecnologias'].fillna('') if 'tecnologias' in data.columns else pd.Series([''] * len(data))
    
    if desc_col:
        # Patrones de búsqueda para tecnologías populares
        tech_patterns = {
            'python': r'python\b',
            'javascript': r'javascript|js\b',
            'typescript': r'typescript|ts\b',
            'java': r'\bjava\b',
            'csharp': r'c#|c-sharp|csharp',
            'cpp': r'c\+\+|cpp',
            'php': r'php',
            'go': r'\bgo\b|golang',
            'ruby': r'ruby',
            'swift': r'swift',
            'kotlin': r'kotlin',
            'rust': r'rust',
            'react': r'react',
            'angular': r'angular',
            'vue': r'vue',
            'node': r'node\.?js',
            'django': r'django',
            'flask': r'flask',
            'spring': r'spring',
            'rails': r'rails',
            'laravel': r'laravel',
            'sql': r'sql\b',
            'mysql': r'mysql',
            'postgresql': r'postgres|postgresql',
            'mongodb': r'mongo|mongodb',
            'aws': r'aws|amazon web services',
            'azure': r'azure',
            'gcp': r'gcp|google cloud',
            'docker': r'docker',
            'kubernetes': r'kubernetes|k8s',
            'terraform': r'terraform',
            'git': r'git\b',
            'jira': r'jira',
            'scrum': r'scrum|agile',
        }
        
        # Extraer menciones de tecnologías de la descripción
        for tech, pattern in tech_patterns.items():
            data[f'tech_{tech}'] = data[desc_col].str.contains(pattern, case=False, na=False).astype(int)
        
        logger.info(f"Extraídas {len(tech_patterns)} tecnologías específicas de la descripción del puesto")

    # Procesamiento de la columna tecnologias si existe
    if 'tecnologias' in data.columns:
        tech_dummies = data['tecnologias'].fillna('').str.get_dummies(sep=',')
        
        cleaned_cols = {}
        for col in tech_dummies.columns:
            col_stripped = col.strip()
            if col_stripped:
                cleaned_name = f"skill_{re.sub(r'[^a-zA-Z0-9_]', '', col_stripped.lower())}"
                if cleaned_name in cleaned_cols:
                    cleaned_cols[cleaned_name] += tech_dummies[col]
                else:
                    cleaned_cols[cleaned_name] = tech_dummies[col]
        
        if cleaned_cols:
            tech_dummies_df = pd.DataFrame(cleaned_cols)
            tech_dummies_df = tech_dummies_df.loc[:, ~tech_dummies_df.columns.duplicated()]
            data = pd.concat([data, tech_dummies_df], axis=1)
            logger.info(f"Creadas {len(tech_dummies_df.columns)} columnas adicionales de skills")
    
    # Verificar que required_years_exp existe, si no, eliminarlo de futuras referencias
    if 'required_years_exp' not in data.columns:
        logger.warning("La columna 'required_years_exp' no se creó correctamente durante el preprocesamiento")

    # --- 4. Location Features ---
    location_col = determine_location_column(data)
    if location_col:
        # Ciudades principales
        for city in ['madrid', 'barcelona', 'valencia', 'malaga', 'sevilla', 'bilbao', 'zaragoza']:
            data[f'loc_{city}'] = data[location_col].str.contains(city, case=False, na=False).astype(int)
        
        # Tipo de ubicación
        data['is_capital'] = data[location_col].str.contains(
            r'madrid', case=False, na=False).astype(int)
        data['is_remote_location'] = data[location_col].str.contains(
            r'remot[eo]|teletrabajo|trabajo a distancia', case=False, na=False).astype(int)
        data['is_international'] = data[location_col].str.contains(
            r'internacional|international|europe|global', case=False, na=False).astype(int)
        
        logger.info("Creadas características de ubicación")

    return data

# ---------------------------------------------------------------------------
# Main training routine
# ---------------------------------------------------------------------------

def train_salary_model(data_path: Path = DATA_PATH, model_path: Path = MODEL_PATH) -> None:
    # --- 1. Carga de Datos ---
    try:
        df = pd.read_csv(data_path)
        logger.info(f"Datos cargados exitosamente desde {data_path}")
    except FileNotFoundError:
        logger.error(f"Error: El archivo {data_path} no fue encontrado. Ejecuta el pipeline ETL primero.")
        return



    # --- 2. Preprocesamiento y Feature Engineering ---
    df = preprocess_data(df)

    # --- 3. Selección de Características y División de Datos ---
    salary_col = determine_salary_column(df)
    location_col = determine_location_column(df)
    contract_col = determine_contract_column(df)
    title_col = determine_title_column(df)

    if not salary_col:
        logger.error("No se encontró una columna de salario válida.")
        return

    # --- Limpieza de datos de salario ---
    logger.info(f"Limpiando la columna de salarios '{salary_col}'...")
    df[salary_col] = pd.to_numeric(df[salary_col], errors='coerce')
    original_rows = len(df)
    df.dropna(subset=[salary_col], inplace=True)
    new_rows = len(df)
    logger.info(f"Se eliminaron {original_rows - new_rows} filas sin datos de salario válidos. Quedan {new_rows} filas.")

    if df.empty:
        logger.error("No hay datos de salario válidos para entrenar después de la limpieza.")
        return

    categorical_features = [col for col in [title_col, location_col, contract_col] if col]
    numerical_features = [col for col in df.columns if col.startswith('skill_') or col.startswith('seniority_')]
    
    feature_cols = categorical_features + numerical_features
    
    if not feature_cols:
        logger.error("No se encontraron características para entrenar. Revisa el preprocesamiento.")
        return

    feature_cols = list(dict.fromkeys(feature_cols))
    
    missing_cols = [col for col in feature_cols if col not in df.columns]
    if missing_cols:
        logger.error(f"Faltan las siguientes columnas en el DataFrame: {missing_cols}")
        return

    X = df[feature_cols]
    y = df[salary_col]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # --- 4. Pipeline de Preprocesamiento y Modelo Avanzado ---
    # Añadir más características derivadas
    role_features = [col for col in df.columns if col.startswith('role_')]  
    location_features = [col for col in df.columns if col.startswith('loc_')] 
    tech_features = [col for col in df.columns if col.startswith('tech_')]
    
    # Actualizar lista completa de características
    base_numerical_patterns = ['skill_', 'seniority_', 'role_', 'tech_']
    specific_numerical_cols = ['required_years_exp']
    
    # Determinar qué columnas existen realmente en el dataframe
    numerical_features = []
    
    # Añadir columnas que coinciden con patrones
    for pattern in base_numerical_patterns:
        numerical_features.extend([col for col in df.columns if col.startswith(pattern)])
    
    # Añadir columnas específicas solo si existen
    for col in specific_numerical_cols:
        if col in df.columns:
            numerical_features.append(col)
        else:
            logger.warning(f"Columna '{col}' no encontrada en el dataframe y será omitida")
    
    boolean_features = ['is_remote', 'has_flexibility', 'requires_degree', 
                       'is_remote_location', 'is_capital', 'is_international']
    
    numerical_features.extend([f for f in boolean_features if f in df.columns])
    
    # Añadir características de ubicación
    numerical_features.extend([f for f in location_features if f in df.columns])
    
    # Preprocesador más sofisticado
    # Verificar que todas las columnas especificadas existen en X
    valid_numerical_features = [col for col in numerical_features if col in X.columns]
    valid_categorical_features = [col for col in categorical_features if col in X.columns]
    
    logger.info(f"Utilizando {len(valid_numerical_features)} características numéricas y {len(valid_categorical_features)} categóricas")
    
    # Si no hay características válidas de un tipo, no incluir ese transformador
    transformers = []
    if valid_numerical_features:
        transformers.append(('num', StandardScaler(), valid_numerical_features))
    if valid_categorical_features:
        transformers.append(('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), valid_categorical_features))
    
    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder='passthrough'
    )

    # Probar múltiples algoritmos para comparar rendimiento
    from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
    from sklearn.linear_model import ElasticNet
    
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', HistGradientBoostingRegressor(random_state=42))  # Algoritmo más rápido y preciso que GBR
    ])

    # --- 5. Búsqueda de Hiperparámetros más exhaustiva ---
    param_dist = {
        'model__max_iter': [100, 200, 500],
        'model__learning_rate': [0.01, 0.05, 0.1, 0.2],
        'model__max_depth': [3, 5, 7, 10, None],  # None permite árboles de profundidad ilimitada
        'model__l2_regularization': [0, 0.1, 1.0, 10.0],
        'model__max_leaf_nodes': [None, 10, 20, 31]  # Control de la complejidad del modelo
    }

    # Usar múltiples métricas para evaluar rendimiento
    scoring = {
        'mae': 'neg_mean_absolute_error',
        'mse': 'neg_mean_squared_error',
        'r2': 'r2'
    }
    
    from sklearn.model_selection import KFold
    # Validación cruzada estratificada para resultados más robustos
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    
    random_search = RandomizedSearchCV(
        pipeline, 
        param_distributions=param_dist, 
        n_iter=20,  # Aumentar número de iteraciones
        cv=cv,
        scoring='neg_mean_absolute_error',  # Métrica principal para optimización
        n_jobs=-1, 
        random_state=42,
        verbose=1,
        return_train_score=True  # Para verificar overfitting
    )

    logger.info("Iniciando búsqueda de hiperparámetros con RandomizedSearchCV...")
    random_search.fit(X_train, y_train)

    logger.info(f"Mejores parámetros encontrados: {random_search.best_params_}")
    best_model_pipeline = random_search.best_estimator_

    # --- 6. Evaluación detallada del Modelo ---
    y_pred = best_model_pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    from sklearn.metrics import mean_squared_error, median_absolute_error
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)  # Calculamos RMSE manualmente para compatibilidad
    medae = median_absolute_error(y_test, y_pred)  # Menos sensible a outliers
    r2 = r2_score(y_test, y_pred)
    
    logger.info(f"Evaluación detallada del mejor modelo:")
    logger.info(f"  - MAE:    {mae:.2f}")
    logger.info(f"  - MedianAE: {medae:.2f}")
    logger.info(f"  - RMSE:   {rmse:.2f}")
    logger.info(f"  - R²:     {r2:.4f}")
    
    # Imprimir los features más importantes (si es posible)
    try:
        if hasattr(best_model_pipeline[-1], 'feature_importances_'):
            feature_names = numerical_features + categorical_features
            importances = best_model_pipeline[-1].feature_importances_
            # Solo mostrar las 10 características más importantes
            if len(importances) == len(feature_names):
                indices = np.argsort(importances)[::-1][:10]
                logger.info("Top 10 características más importantes:")
                for i in range(min(10, len(indices))):
                    logger.info(f"  - {feature_names[indices[i]]}: {importances[indices[i]]:.4f}")
    except Exception as e:
        logger.warning(f"No se pudieron extraer importancias de características: {e}")
        
    # Verificar diferencia train-test para detectar overfitting
    y_pred_train = best_model_pipeline.predict(X_train)
    mae_train = mean_absolute_error(y_train, y_pred_train)
    r2_train = r2_score(y_train, y_pred_train)
    logger.info(f"Métricas en train - MAE: {mae_train:.2f}, R²: {r2_train:.4f}")
    logger.info(f"Diferencia train-test - MAE: {mae_train-mae:.2f}, R²: {r2_train-r2:.4f}")

    # --- 7. Guardado del Modelo y Metadatos ---
    
    # Extraer explícitamente las columnas de tecnologías/skills
    skill_columns = [col for col in df.columns if col.startswith('skill_')]
    tech_columns = [col for col in df.columns if col.startswith('tech_')]
    
    # Extraer las características importantes específicamente para las columnas de skills
    important_skills = []
    try:
        if hasattr(best_model_pipeline[-1], 'feature_importances_'):
            # Obtener nombres de características después de transformación
            if hasattr(best_model_pipeline[0], 'get_feature_names_out'):
                feature_names_transformed = best_model_pipeline[0].get_feature_names_out()
            else:
                # Si no está disponible, usar los originales
                feature_names_transformed = numerical_features + categorical_features
                
            # Obtener importancias
            importances = best_model_pipeline[-1].feature_importances_
            
            # Mapear índices a nombres de características
            if len(importances) == len(feature_names_transformed):
                for i, imp in enumerate(importances):
                    if imp > 0.001:  # Umbral de importancia
                        feature_name = feature_names_transformed[i] if i < len(feature_names_transformed) else f"feature_{i}"
                        # Identificar explícitamente las skills importantes
                        for skill in skill_columns:
                            if skill in feature_name:
                                important_skills.append({
                                    'name': skill,
                                    'importance': float(imp)
                                })
                                break
    except Exception as e:
        logger.warning(f"Error al extraer importancias de skills: {e}")
    
    metadata = {
        'pipeline': best_model_pipeline,
        'feature_cols': feature_cols,
        'categorical_features': categorical_features,
        'numerical_features': numerical_features,
        'skill_columns': skill_columns,  # Añadir explícitamente las columnas de skills
        'tech_columns': tech_columns,    # Añadir explícitamente las columnas de tecnologías
        'important_skills': important_skills,  # Añadir skills con importancia
        'location_col': location_col,   # Añadir columna de ubicación
        'contract_col': contract_col,   # Añadir columna de tipo de contrato
        'title_col': title_col,         # Añadir columna de título
        'trained_at': datetime.now().isoformat(),
        'metrics': {
            'mae': mae,
            'median_ae': medae,
            'rmse': rmse,
            'r2': r2,
            'mae_train': mae_train,
            'r2_train': r2_train
        },
    }

    joblib.dump(metadata, model_path)
    logger.info(f"Modelo guardado exitosamente en {model_path}")


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    train_salary_model()
