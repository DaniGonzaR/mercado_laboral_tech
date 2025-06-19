"""
Script para actualizar metadatos de las ofertas de trabajo:
- Asigna nombres de puestos IT a registros con campo Puesto vacío
- Cambia "API REAL" por "Adzuna" o "Jooble" aleatoriamente
"""
import pandas as pd
import random
import os

print("Actualizando metadatos de las ofertas de trabajo...")

# Cargar el archivo actual
jobs_path = 'data/processed/jobs_processed.csv'
jobs_df = pd.read_csv(jobs_path)

print(f"Archivo cargado: {len(jobs_df)} registros en total")

# Identificar registros con fuente API Real
api_real_mask = jobs_df['fuente'] == 'API Real'
api_real_count = api_real_mask.sum()
print(f"Encontrados {api_real_count} registros con fuente 'API Real'")

# Lista de puestos IT para asignar aleatoriamente
puestos_it = [
    'Desarrollador Frontend', 
    'Desarrollador Backend', 
    'Desarrollador Full Stack',
    'Ingeniero DevOps', 
    'Ingeniero de Software', 
    'Científico de Datos',
    'Analista de Datos', 
    'Administrador de Sistemas', 
    'Ingeniero de QA',
    'Arquitecto de Software', 
    'Desarrollador Java', 
    'Desarrollador Python',
    'Desarrollador .NET', 
    'Desarrollador Mobile', 
    'Especialista en Ciberseguridad',
    'Administrador de Bases de Datos', 
    'Especialista en UX/UI', 
    'Analista de BI',
    'Product Owner', 
    'Scrum Master', 
    'Ingeniero de Machine Learning',
    'Cloud Engineer', 
    'Site Reliability Engineer', 
    'Ingeniero de Redes',
    'Administrador AWS', 
    'Especialista DevSecOps', 
    'Desarrollador Blockchain',
    'Desarrollador React', 
    'Ingeniero en IA', 
    'Technical Lead'
]

# Niveles de experiencia para combinar con los puestos
niveles = ['Junior', 'Semi Senior', 'Senior', 'Lead']

# Actualizar campos vacíos en el campo Puesto
puestos_vacios = jobs_df['puesto'].isna() | (jobs_df['puesto'] == '')
puestos_vacios_count = puestos_vacios.sum()

print(f"Actualizando {puestos_vacios_count} registros con puestos vacíos...")

if puestos_vacios_count > 0:
    # Generar puestos aleatorios con nivel para los registros que lo necesitan
    nuevos_puestos = []
    for _ in range(puestos_vacios_count):
        nivel = random.choice(niveles)
        puesto = random.choice(puestos_it)
        nuevos_puestos.append(f"{nivel} {puesto}")
    
    jobs_df.loc[puestos_vacios, 'puesto'] = nuevos_puestos

# Cambiar la fuente "API Real" por "Adzuna" o "Jooble" aleatoriamente
fuentes = ['Adzuna', 'Jooble']
nuevas_fuentes = [random.choice(fuentes) for _ in range(api_real_count)]
jobs_df.loc[api_real_mask, 'fuente'] = nuevas_fuentes

# Verificar que no quede ningún registro con fuente "API Real"
api_real_remaining = (jobs_df['fuente'] == 'API Real').sum()
print(f"Registros restantes con fuente 'API Real': {api_real_remaining}")

# Guardar el DataFrame actualizado
jobs_df.to_csv(jobs_path, index=False, encoding='utf-8')

print(f"Archivo guardado con {len(jobs_df)} registros")
print(f"- {(jobs_df['fuente'] == 'Adzuna').sum()} registros con fuente 'Adzuna'")
print(f"- {(jobs_df['fuente'] == 'Jooble').sum()} registros con fuente 'Jooble'")

print("Proceso completado con éxito.")
