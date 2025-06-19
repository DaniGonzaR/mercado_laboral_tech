"""
Script para generar datos simulados de ofertas de trabajo en España
para permitir que el dashboard y el modelo funcionen correctamente.
"""
import os
import pandas as pd
import random
from datetime import datetime

# Crear los directorios necesarios
os.makedirs('data/processed', exist_ok=True)

# Definir datos simulados para España
n_jobs = 800  # 800 ofertas de trabajo

# Tecnologías comunes en desarrollo de software
technologies = [
    'Python', 'JavaScript', 'TypeScript', 'Java', 'C#', 'PHP', 'React', 'Angular', 
    'Vue.js', 'Node.js', 'Django', 'ASP.NET', 'Spring', 'Flask', 'Express', 
    'Ruby on Rails', 'HTML', 'CSS', 'SASS', 'SQL', 'PostgreSQL', 'MySQL', 
    'MongoDB', 'Redis', 'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes',
    'Jenkins', 'Git', 'Terraform', 'Ansible'
]

# Ciudades españolas
cities = [
    'Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Zaragoza', 'Málaga', 
    'Murcia', 'Palma', 'Las Palmas', 'Bilbao', 'Alicante', 'Córdoba', 
    'Valladolid', 'Vigo', 'Gijón', 'Vitoria', 'A Coruña', 'Granada', 
    'Elche', 'Oviedo', 'Terrassa', 'Badalona', 'Cartagena', 'Jerez',
    'Sabadell', 'Móstoles', 'Alcalá de Henares', 'Pamplona'
]

# Tipos de puestos
job_titles = [
    'Desarrollador Frontend', 'Desarrollador Backend', 'Desarrollador Full Stack',
    'Ingeniero de Software', 'Data Scientist', 'DevOps Engineer', 'Arquitecto de Software',
    'QA Engineer', 'Site Reliability Engineer', 'UX/UI Designer', 'Product Manager',
    'Technical Lead', 'Scrum Master', 'Analista Programador', 'Data Engineer',
    'Machine Learning Engineer', 'Mobile Developer', 'Cloud Engineer'
]

# Niveles de experiencia
experience_levels = ['Junior', 'Semi Senior', 'Senior', 'Lead', 'Principal', 'Director']

# Tipos de empresa
company_types = [
    'Startup', 'Empresa Tecnológica', 'Consultora IT', 'Multinacional', 
    'Agencia Digital', 'Fintech', 'Empresa de Telecomunicaciones',
    'E-commerce', 'Health Tech', 'Empresa de Software', 'Banco', 'Aseguradora'
]

# Generar datos
print("Generando datos simulados para España...")

# Generar puestos de trabajo
jobs_data = []
for i in range(n_jobs):
    # Generar un título realista combinando nivel y puesto
    title = f"{random.choice(experience_levels)} {random.choice(job_titles)}"
    
    # Salario dentro de rangos realistas según nivel de experiencia
    if 'Junior' in title:
        salary = random.randint(18000, 28000)
    elif 'Semi Senior' in title:
        salary = random.randint(28000, 40000)
    elif 'Senior' in title:
        salary = random.randint(38000, 55000)
    elif 'Lead' in title or 'Principal' in title:
        salary = random.randint(50000, 70000)
    else:
        salary = random.randint(65000, 90000)
    
    # Ubicación en España
    location = f"{random.choice(cities)}, España"
    
    # Entre 3 y 8 tecnologías aleatorias
    num_techs = random.randint(3, 8)
    job_techs = random.sample(technologies, num_techs)
    tecnologias = ", ".join(job_techs)
    
    # Nombre de empresa
    company = f"{random.choice(company_types)} {random.randint(1, 100)}"
    
    # Tipo de contrato
    contract = random.choice(['Indefinido', 'Temporal', 'Freelance', 'Prácticas'])
    
    # Modalidad
    workmode = random.choice(['Presencial', 'Remoto', 'Híbrido'])
    
    # Fuente de datos
    source = 'Datos Simulados España'
    
    # Añadir el registro
    jobs_data.append({
        'puesto': title,
        'salario_promedio': salary,
        'ubicacion': location,
        'tecnologias': tecnologias,
        'empresa': company,
        'tipo_contrato': contract,
        'modalidad': workmode,
        'fuente': source,
        'fecha_publicacion': datetime.now().strftime('%Y-%m-%d')
    })

# Crear DataFrame
jobs_df = pd.DataFrame(jobs_data)

# Guardar el DataFrame como CSV
output_file = 'data/processed/jobs_processed.csv'
jobs_df.to_csv(output_file, index=False, encoding='utf-8')
print(f"Guardados {len(jobs_df)} registros en {output_file}")

# Generar conteo de tecnologías
tech_counts = {}
for tech_list in jobs_df['tecnologias']:
    techs = [t.strip() for t in tech_list.split(',')]
    for tech in techs:
        if tech:
            tech_counts[tech] = tech_counts.get(tech, 0) + 1

# Crear y guardar DataFrame de tecnologías
tech_df = pd.DataFrame({
    'tecnologia': list(tech_counts.keys()),
    'menciones': list(tech_counts.values())
}).sort_values('menciones', ascending=False)

tech_file = 'data/processed/technology_job_counts.csv'
tech_df.to_csv(tech_file, index=False, encoding='utf-8')
print(f"Guardado archivo de conteo de tecnologías con {len(tech_df)} tecnologías")

print("Datos generados con éxito. Ahora puede proceder a entrenar el modelo y ejecutar el dashboard.")
