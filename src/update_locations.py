"""
Script para actualizar la ubicación de todos los registros con fuente "Datos Simulados España"
para que tengan ubicación "Spain"
"""
import pandas as pd
import os

print("Actualizando ubicaciones de ofertas simuladas...")

# Cargar el archivo actual
jobs_path = 'data/processed/jobs_processed.csv'
jobs_df = pd.read_csv(jobs_path)

print(f"Archivo cargado: {len(jobs_df)} registros en total")

# Identificar registros con fuente "Datos Simulados España"
datos_simulados_mask = jobs_df['fuente'] == 'Datos Simulados España'
datos_simulados_count = datos_simulados_mask.sum()
print(f"Encontrados {datos_simulados_count} registros con fuente 'Datos Simulados España'")

# Verificar que exista la columna de ubicación
location_cols = [col for col in jobs_df.columns if col.lower() in ['ubicacion', 'location']]

if not location_cols:
    print("Error: No se encontró una columna de ubicación en el DataFrame")
    exit(1)

location_col = location_cols[0]
print(f"Se utilizará la columna '{location_col}' para actualizar las ubicaciones")

# Actualizar la ubicación a "Spain" para todos los registros con fuente "Datos Simulados España"
jobs_df.loc[datos_simulados_mask, location_col] = 'Spain'

# Verificar que no queden registros con fuente "Datos Simulados España" y otra ubicación
verificacion = jobs_df.loc[datos_simulados_mask, location_col].ne('Spain').sum()
print(f"Verificación: {verificacion} registros con fuente 'Datos Simulados España' y ubicación distinta a 'Spain'")

# Guardar el DataFrame actualizado
jobs_df.to_csv(jobs_path, index=False, encoding='utf-8')

print(f"Archivo guardado con {len(jobs_df)} registros")
print(f"Se actualizaron {datos_simulados_count} registros para tener ubicación 'Spain'")
print("Proceso completado con éxito.")
