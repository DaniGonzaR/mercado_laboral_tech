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
from sklearn.model_selection import train_test_split
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
# Main training routine
# ---------------------------------------------------------------------------

def train_salary_model(data_path: Path = DATA_PATH, model_path: Path = MODEL_PATH) -> None:
    # Cargar datos procesados
    try:
        data = pd.read_csv(data_path)
        logger.info(f"Datos cargados exitosamente desde {data_path}")
    except FileNotFoundError:
        logger.error(f"Error: El archivo {data_path} no fue encontrado. Ejecuta el pipeline ETL primero.")
        return

    # Detectar columnas dinámicamente
    salary_col = determine_salary_column(data)
    location_col = determine_location_column(data)
    contract_col = determine_contract_column(data)
    title_col = determine_title_column(data)

    # Asegurarse de que la columna de salario exista y no tenga nulos
    if not salary_col:
        logger.error("No se encontró una columna de salario en los datos procesados.")
        return
    
    data.dropna(subset=[salary_col], inplace=True)
    if data.empty:
        logger.error("No hay datos de salario válidos para entrenar el modelo después de eliminar nulos.")
        return

    # Feature Engineering: Crear columnas 'skill_' a partir de 'tecnologias'
    if 'tecnologias' in data.columns:
        # Rellenar NaNs para evitar errores y obtener dummies
        tech_dummies = data['tecnologias'].fillna('').str.get_dummies(sep=',')
        
        # Limpiar los nombres de las columnas para que sean válidos y consistentes
        cleaned_cols = {}
        for col in tech_dummies.columns:
            if col.strip(): # Ignorar columnas vacías que pueden surgir de comas extra
                cleaned_name = f"skill_{re.sub(r'[^a-zA-Z0-9_]', '', col.strip().lower())}"
                # Si el nombre ya existe, suma las columnas (ej. 'python' y 'Python')
                if cleaned_name in cleaned_cols:
                    cleaned_cols[cleaned_name] = cleaned_cols[cleaned_name] + tech_dummies[col]
                else:
                    cleaned_cols[cleaned_name] = tech_dummies[col]
        
        if cleaned_cols:
            tech_dummies = pd.DataFrame(cleaned_cols)
            # Unir los dummies al dataframe principal
            data = pd.concat([data, tech_dummies], axis=1)
            logger.info(f"Creadas {len(tech_dummies.columns)} columnas de skills a partir de 'tecnologias'.")

    # Definir las características (features) dinámicamente
    features = []
    categorical_features = []
    
    if title_col:
        features.append(title_col)
        categorical_features.append(title_col)
    if location_col:
        features.append(location_col)
        categorical_features.append(location_col)
    if contract_col:
        features.append(contract_col)
        categorical_features.append(contract_col)

    # Añadir nuevas características extraídas si existen
    skill_cols = [col for col in data.columns if col.startswith('skill_')]
    features.extend(skill_cols)
    if 'experience_years' in data.columns:
        features.append('experience_years')
    if 'seniority_senior' in data.columns:
        features.append('seniority_senior')
    if 'seniority_junior' in data.columns:
        features.append('seniority_junior')

    numeric_features = [f for f in features if f not in categorical_features]

    if not features:
        logger.error("No se encontraron características válidas para entrenar el modelo.")
        return

    X = data[features]
    y = data[salary_col]

    # Dividir los datos en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Preprocesamiento para características categóricas y numéricas
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])

    # Crear y entrenar el pipeline del modelo
    model = Pipeline(steps=[('preprocessor', preprocessor),
                            ('model', GradientBoostingRegressor(random_state=42))])

    # Train
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f'Model performance:\nMAE: {mae:,.0f}  |  R²: {r2:.2f}')

    # Persist
    metadata = {
        'pipeline': model,
        'feature_cols': features,
        'trained_at': datetime.now().isoformat(),
        'metrics': {'mae': mae, 'r2': r2},
    }

    joblib.dump(metadata, model_path)
    print(f'Model saved to {model_path}')


if __name__ == '__main__':
    train_salary_model()
