#!/usr/bin/env python
"""
Script unificado para ejecutar el pipeline completo o partes específicas
del proyecto de análisis del mercado laboral tecnológico español.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def ejecutar_script(nombre_script, descripcion):
    """
    Ejecuta un script Python del proyecto.
    
    Args:
        nombre_script: Nombre del script en la carpeta src/
        descripcion: Descripción de lo que hace el script
    """
    ruta_script = os.path.join("src", nombre_script)
    
    if not os.path.exists(ruta_script):
        print(f"Error: No se encuentra el script {ruta_script}")
        return False
    
    print(f"\n{'='*60}")
    print(f"Ejecutando: {descripcion}")
    print(f"{'='*60}")
    
    try:
        # Ejecutar el script directamente y mostrar su salida en tiempo real
        proceso = subprocess.Popen(
            [sys.executable, ruta_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Mostrar la salida en tiempo real
        for linea in iter(proceso.stdout.readline, ''):
            sys.stdout.write(linea)
        
        # Esperar a que termine el proceso y obtener el código de salida
        proceso.wait()
        
        if proceso.returncode == 0:
            print(f"\n✅ {descripcion} completado con éxito")
            return True
        else:
            print(f"\n❌ Error en {descripcion}")
            return False
    except Exception as e:
        print(f"\n❌ Error al ejecutar {descripcion}: {e}")
        return False

def ejecutar_etl():
    """Ejecuta el pipeline completo de ETL."""
    print("\n" + "="*70)
    print(" "*20 + "PIPELINE DE ETL - INICIO")
    print("="*70)
    
    # Definir pasos del pipeline ETL
    pasos = [
        ("generate_spain_data.py", "Generación de datos simulados para España"),
        ("fix_real_salaries.py", "Corrección de salarios en datos reales"),
        ("update_job_metadata.py", "Actualización de metadatos (puestos y fuentes)"),
        ("update_locations.py", "Actualización de ubicaciones para datos simulados")
    ]
    
    # Ejecutar cada paso
    exitos = []
    for script, descripcion in pasos:
        exito = ejecutar_script(script, descripcion)
        exitos.append(exito)
    
    # Reportar resultado
    if all(exitos):
        print("\n✅ Pipeline ETL completado con éxito")
    else:
        print("\n⚠️ Pipeline ETL completado con errores")
    
    return all(exitos)

def ejecutar_entrenamiento():
    """Entrena el modelo de predicción de salarios."""
    return ejecutar_script("model_salary.py", "Entrenamiento del modelo de predicción de salarios")

def ejecutar_dashboard(puerto=8501):
    """
    Ejecuta el dashboard interactivo.
    
    Args:
        puerto: Puerto en el que se ejecutará el dashboard
    """
    ruta_dashboard = os.path.join("dashboards", "app.py")
    
    if not os.path.exists(ruta_dashboard):
        print(f"Error: No se encuentra el dashboard en {ruta_dashboard}")
        return False
    
    print("\n" + "="*70)
    print(" "*20 + "INICIANDO DASHBOARD")
    print("="*70)
    
    print(f"\n🌐 Dashboard disponible en: http://localhost:{puerto}")
    print("⚠️ Presiona Ctrl+C para detener el dashboard\n")
    
    try:
        # Ejecutar streamlit directamente
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", 
             ruta_dashboard, "--server.port", str(puerto)],
            check=True
        )
        return True
    except KeyboardInterrupt:
        print("\n✅ Dashboard detenido por el usuario")
        return True
    except Exception as e:
        print(f"\n❌ Error al ejecutar el dashboard: {e}")
        return False

def analizar_datos():
    """Analiza los datos procesados y muestra estadísticas básicas."""
    try:
        import pandas as pd
        
        # Rutas a los archivos de datos
        ruta_jobs = os.path.join("data", "processed", "jobs_processed.csv")
        ruta_tech = os.path.join("data", "processed", "technology_job_counts.csv")
        
        if not os.path.exists(ruta_jobs):
            print(f"Error: No se encuentra el archivo {ruta_jobs}")
            return False
        
        # Cargar datos
        print("\n" + "="*60)
        print(" "*20 + "ANÁLISIS DE DATOS")
        print("="*60 + "\n")
        
        jobs_df = pd.read_csv(ruta_jobs)
        print(f"📊 Total de ofertas de trabajo: {len(jobs_df)}")
        
        # Distribución por fuente
        print("\n📊 Distribución por fuente:")
        fuentes = jobs_df['fuente'].value_counts()
        for fuente, conteo in fuentes.items():
            print(f"  - {fuente}: {conteo} ({conteo/len(jobs_df)*100:.1f}%)")
        
        # Tecnologías más demandadas
        if os.path.exists(ruta_tech):
            tech_df = pd.read_csv(ruta_tech)
            print("\n📊 Top 10 tecnologías más demandadas:")
            top_tech = tech_df.sort_values('menciones', ascending=False).head(10)
            for _, row in top_tech.iterrows():
                print(f"  - {row['tecnologia']}: {row['menciones']} menciones")
        
        # Estadísticas de salario
        columna_salario = None
        for col in ['salario_promedio', 'salario', 'salary']:
            if col in jobs_df.columns:
                columna_salario = col
                break
        
        if columna_salario:
            salarios_validos = jobs_df[columna_salario].dropna()
            salarios_validos = salarios_validos[salarios_validos > 0]
            
            print(f"\n📊 Estadísticas de salario ({columna_salario}):")
            print(f"  - Promedio: ${salarios_validos.mean():,.2f}")
            print(f"  - Mediana: ${salarios_validos.median():,.2f}")
            print(f"  - Mínimo: ${salarios_validos.min():,.2f}")
            print(f"  - Máximo: ${salarios_validos.max():,.2f}")
        
        # Verificar modelo
        ruta_modelo = os.path.join("models", "salary_model.joblib")
        estado_modelo = "✅ Disponible" if os.path.exists(ruta_modelo) else "❌ No disponible"
        print(f"\n🤖 Modelo de predicción: {estado_modelo}")
        
        print("\n" + "="*60)
        print(" "*20 + "FIN DEL ANÁLISIS")
        print("="*60)
        
        return True
    except Exception as e:
        print(f"\nError en el análisis de datos: {e}")
        return False

def main():
    """Función principal para ejecutar desde línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Ejecuta el pipeline completo o componentes específicos del proyecto",
        epilog="""
Ejemplos de uso:
  python ejecutar_pipeline.py --etl                # Ejecuta el pipeline ETL completo
  python ejecutar_pipeline.py --dashboard          # Inicia el dashboard interactivo
  python ejecutar_pipeline.py --todo               # Ejecuta ETL, entrenamiento y dashboard
  python ejecutar_pipeline.py --analizar           # Muestra estadísticas de los datos
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--etl", action="store_true", 
                      help="Ejecuta el pipeline completo de ETL")
    parser.add_argument("--entrenamiento", action="store_true", 
                      help="Entrena el modelo de predicción")
    parser.add_argument("--dashboard", action="store_true", 
                      help="Inicia el dashboard interactivo")
    parser.add_argument("--puerto", type=int, default=8501,
                      help="Puerto para el dashboard (por defecto: 8501)")
    parser.add_argument("--analizar", action="store_true",
                      help="Analiza los datos procesados")
    parser.add_argument("--todo", action="store_true",
                      help="Ejecuta ETL, entrenamiento y dashboard")
    
    args = parser.parse_args()
    
    # Si no se especifica ninguna acción
    if not any([args.etl, args.entrenamiento, args.dashboard, args.analizar, args.todo]):
        print("\n" + "="*70)
        print(" "*15 + "MERCADO LABORAL TECNOLÓGICO ESPAÑOL")
        print("="*70)
        print("\nNinguna acción especificada. Use --help para ver las opciones.\n")
        print("Comandos principales:")
        print("  python ejecutar_pipeline.py --etl        # Ejecuta el pipeline ETL")
        print("  python ejecutar_pipeline.py --dashboard  # Inicia el dashboard")
        print("  python ejecutar_pipeline.py --analizar   # Analiza los datos")
        print("  python ejecutar_pipeline.py --todo       # Ejecuta todo el proceso\n")
        return
    
    # Ejecutar acciones según los argumentos
    if args.todo or args.etl:
        exito_etl = ejecutar_etl()
        if not exito_etl and not args.todo:
            print("\n⚠️ El pipeline ETL tuvo errores. Revise los logs para más detalles.")
            return
    
    if args.todo or args.entrenamiento:
        ejecutar_entrenamiento()
    
    if args.analizar:
        analizar_datos()
    
    if args.todo or args.dashboard:
        ejecutar_dashboard(args.puerto)

if __name__ == "__main__":
    main()
