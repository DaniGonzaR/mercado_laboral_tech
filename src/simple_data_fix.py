"""
Script simple para crear un archivo jobs_processed.csv adecuado para el dashboard
"""
import os
import pandas as pd
import glob
import random
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Verificar y crear directorios
os.makedirs('data/processed', exist_ok=True)

# Buscar archivos de ofertas de España
files = glob.glob('data/raw/ofertas_tech_reales_*.csv')
logger.info(f"Encontrados {len(files)} archivos de ofertas")

# Lista para almacenar los datos
all_data = []

# Tecnologías comunes para generar datos simulados si es necesario
tech_list = [
    'Python', 'JavaScript', 'Java', 'C#', 'PHP', 'React', 'Angular', 'Vue', 
    'Node.js', 'Django', 'Flask', 'Spring', 'ASP.NET', 'HTML', 'CSS', 'SQL',
    'AWS', 'Azure', 'Docker', 'Kubernetes', 'Git', 'MongoDB', 'MySQL',
    'PostgreSQL', 'TypeScript'
]

# Ciudades de España
cities = [
    'Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Zaragoza', 
    'Málaga', 'Murcia', 'Palma', 'Las Palmas', 'Bilbao'
]

# Procesar cada archivo
total_rows = 0
for file in files:
    try:
        logger.info(f"Procesando archivo: {os.path.basename(file)}")
        df = pd.read_csv(file)
        logger.info(f"  - Leídas {len(df)} filas")
        total_rows += len(df)
        
        # En caso de error de memoria, podemos procesar solo algunas filas
        # df = df.head(100)  # Descomenta esta línea si hay problemas de memoria
        
        all_data.append(df)
    except Exception as e:
        logger.error(f"Error al procesar {file}: {e}")

# Si no se pudieron cargar datos, crear un conjunto de datos simulado
if not all_data or total_rows == 0:
    logger.warning("No se pudieron cargar datos. Creando datos simulados.")
    
    # Crear datos simulados
    n_rows = 800  # Generar 800 filas simuladas para España
    
    # Datos simulados
    sim_data = {
        'title': [f"Desarrollador {random.choice(['Senior', 'Junior', 'Full Stack', 'Backend', 'Frontend'])}" for _ in range(n_rows)],
        'salary': [random.randint(24000, 65000) for _ in range(n_rows)],
        'location': [f"{random.choice(cities)}, España" for _ in range(n_rows)],
        'tecnologias': [', '.join(random.sample(tech_list, random.randint(3, 8))) for _ in range(n_rows)],
        'company': [f"Empresa {i}" for i in range(1, n_rows+1)],
        'source': ['Datos simulados España'] * n_rows
    }
    
    processed_df = pd.DataFrame(sim_data)
    logger.info(f"Creados {n_rows} registros simulados")
    
else:
    # Intentar combinar los DataFrames
    try:
        processed_df = pd.concat(all_data, ignore_index=True)
        logger.info(f"Combinados {len(processed_df)} registros de todos los archivos")
        
        # Eliminar duplicados si hay columna de ID
        if 'id' in processed_df.columns:
            before_len = len(processed_df)
            processed_df.drop_duplicates(subset='id', keep='first', inplace=True)
            logger.info(f"Eliminados {before_len - len(processed_df)} duplicados")
        
        # Renombrar columnas para estandarizar
        column_mapping = {}
        for col in processed_df.columns:
            col_lower = col.lower()
            if 'title' in col_lower or 'puesto' in col_lower:
                column_mapping[col] = 'title'
            elif 'salary' in col_lower or 'salario' in col_lower:
                column_mapping[col] = 'salary'
            elif 'location' in col_lower or 'ubicacion' in col_lower:
                column_mapping[col] = 'location'
            elif 'company' in col_lower or 'empresa' in col_lower:
                column_mapping[col] = 'company'
            elif 'technolog' in col_lower or 'tecnologia' in col_lower:
                column_mapping[col] = 'tecnologias'
        
        if column_mapping:
            processed_df = processed_df.rename(columns=column_mapping)
        
        # Asegurar que existen las columnas necesarias
        required_cols = ['title', 'salary', 'location', 'tecnologias']
        for col in required_cols:
            if col not in processed_df.columns:
                if col == 'title':
                    processed_df[col] = 'Desarrollador'
                elif col == 'salary':
                    processed_df[col] = 40000
                elif col == 'location':
                    processed_df[col] = 'Madrid, España'
                elif col == 'tecnologias':
                    processed_df[col] = 'Python, JavaScript'
        
        # Asegurar que la columna de salario es numérica
        if 'salary' in processed_df.columns:
            processed_df['salary'] = pd.to_numeric(processed_df['salary'], errors='coerce')
            # Rellenar valores nulos con un valor predeterminado
            processed_df['salary'].fillna(35000, inplace=True)
        
    except Exception as e:
        logger.error(f"Error al procesar los datos: {e}")
        # Crear un DataFrame vacío con la estructura correcta
        processed_df = pd.DataFrame(columns=['title', 'salary', 'location', 'tecnologias', 'company', 'source'])

# Guardar los datos procesados
output_file = 'data/processed/jobs_processed.csv'
processed_df.to_csv(output_file, index=False)
logger.info(f"Guardados {len(processed_df)} registros en {output_file}")

# Generar archivo de conteo de tecnologías
if 'tecnologias' in processed_df.columns:
    tech_counts = {}
    
    for tech_str in processed_df['tecnologias'].astype(str):
        if tech_str and tech_str.lower() != 'nan':
            techs = [t.strip() for t in tech_str.split(',')]
            for tech in techs:
                if tech:
                    tech_counts[tech] = tech_counts.get(tech, 0) + 1
    
    # Crear DataFrame de conteos
    tech_df = pd.DataFrame({
        'tecnologia': list(tech_counts.keys()),
        'menciones': list(tech_counts.values())
    }).sort_values('menciones', ascending=False)
    
    # Guardar archivo
    tech_path = 'data/processed/technology_job_counts.csv'
    tech_df.to_csv(tech_path, index=False)
    logger.info(f"Guardado archivo de tecnologías con {len(tech_df)} entradas")

logger.info("Proceso completado con éxito")
