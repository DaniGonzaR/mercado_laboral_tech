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

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

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
    - Extracts seniority from job title.
    - Creates one-hot encoded features for technologies.
    """
    logger.info("Iniciando preprocesamiento y feature engineering...")
    
    title_col = determine_title_column(data)

    # --- 1. Seniority from Title ---
    if title_col:
        data['seniority_senior'] = data[title_col].str.contains(r'senior|sr\.|lead\b|principal', case=False, na=False).astype(int)
        data['seniority_junior'] = data[title_col].str.contains(r'junior|jr\.|intern\b|trainee', case=False, na=False).astype(int)
        logger.info("Creadas columnas 'seniority_senior' y 'seniority_junior'.")

    # --- 2. One-Hot Encoding for Technologies ---
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
            logger.info(f"Creadas {len(tech_dummies_df.columns)} columnas de skills.")

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
    
    df.dropna(subset=[salary_col], inplace=True)
    if df.empty:
        logger.error("No hay datos de salario válidos para entrenar.")
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

    # --- 4. Pipeline de Preprocesamiento y Modelo ---
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ],
        remainder='passthrough'
    )

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', GradientBoostingRegressor(random_state=42))
    ])

    # --- 5. Búsqueda de Hiperparámetros ---
    param_dist = {
        'model__n_estimators': [100, 200, 300],
        'model__learning_rate': [0.01, 0.1, 0.2],
        'model__max_depth': [3, 5, 7],
        'model__subsample': [0.8, 0.9, 1.0]
    }

    random_search = RandomizedSearchCV(
        pipeline, 
        param_distributions=param_dist, 
        n_iter=10, 
        cv=5, 
        scoring='neg_mean_absolute_error', 
        n_jobs=-1, 
        random_state=42,
        verbose=1
    )

    logger.info("Iniciando búsqueda de hiperparámetros con RandomizedSearchCV...")
    random_search.fit(X_train, y_train)

    logger.info(f"Mejores parámetros encontrados: {random_search.best_params_}")
    best_model_pipeline = random_search.best_estimator_

    # --- 6. Evaluación del Modelo ---
    y_pred = best_model_pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    logger.info(f"Evaluación del mejor modelo: MAE = {mae:.2f}, R^2 = {r2:.2f}")

    # --- 7. Guardado del Modelo y Metadatos ---
    metadata = {
        'pipeline': best_model_pipeline,
        'feature_cols': feature_cols,
        'trained_at': datetime.now().isoformat(),
        'metrics': {'mae': mae, 'r2': r2},
    }

    joblib.dump(metadata, model_path)
    logger.info(f"Modelo guardado exitosamente en {model_path}")


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    train_salary_model()
