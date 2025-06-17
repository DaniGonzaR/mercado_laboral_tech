"""
Módulo para recopilar datos reales de empleo en tecnología desde APIs públicas.
"""
import os
import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime
import json
import random
import logging
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno si el archivo existe
try:
    load_dotenv()
except Exception as e:
    logger.warning(f"No se pudo cargar el archivo .env: {str(e)}")
    logger.info("Las credenciales para APIs pueden ser configuradas como variables de entorno")

class JobDataCollector:
    """Clase para recopilar datos de empleo desde APIs públicas o generar datos simulados."""
    
    def __init__(self, force_mock=True):
        """Inicializar el colector de datos.
        
        Args:
            force_mock (bool): Si es True, siempre usará datos simulados independientemente de las credenciales.
        """
        # API de Adzuna
        self.adzuna_app_id = os.getenv('ADZUNA_APP_ID')
        self.adzuna_api_key = os.getenv('ADZUNA_API_KEY')
        
        # Si no hay credenciales o force_mock es True, usar datos simulados
        self.use_mock = force_mock or not (self.adzuna_app_id and self.adzuna_api_key)
        
        if self.use_mock:
            logger.info("Usando datos simulados de empleo para el análisis.")
        else:
            logger.info("Usando API de Adzuna para obtener datos reales de empleo.")
    
    def get_tech_jobs_adzuna(self, country_code='es', results_per_page=50, max_pages=20, 
                           what='developer OR programmer OR engineer OR data', 
                           where='madrid OR barcelona'):
        """
        Obtener ofertas de empleo tecnológico desde la API de Adzuna.
        
        Args:
            country_code (str): Código de país (es=España, gb=Reino Unido, etc.)
            results_per_page (int): Resultados por página (máx. 50 en plan gratuito)
            max_pages (int): Número máximo de páginas a solicitar
            what (str): Términos de búsqueda para el puesto
            where (str): Localización geográfica
            
        Returns:
            pd.DataFrame: DataFrame con las ofertas de empleo
        """
        # Si no hay credenciales, usar datos simulados pero con estructura real
        if self.use_mock:
            logger.info("Generando datos simulados con la estructura de Adzuna API...")
            return self._generate_mock_adzuna_data(results_per_page * max_pages)
        
        base_url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search"
        
        all_jobs = []
        
        try:
            for page in range(1, max_pages + 1):
                logger.info(f"Obteniendo página {page} de {max_pages}...")
                
                params = {
                    'app_id': self.adzuna_app_id,
                    'app_key': self.adzuna_api_key,
                    'results_per_page': results_per_page,
                    'what': what,
                    'where': where,
                    'page': page,
                    'content-type': 'application/json',
                    'salary_include_unknown': 0  # No incluir ofertas sin salario
                }
                
                response = requests.get(base_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if not data.get('results'):
                        logger.info(f"No se encontraron más resultados en la página {page}")
                        break
                    
                    all_jobs.extend(data['results'])
                    logger.info(f"Obtenidos {len(data['results'])} empleos de la página {page}")
                    
                    # Verificar si hay más resultados
                    if len(data['results']) < results_per_page:
                        logger.info("No hay más resultados disponibles")
                        break
                    
                    # Esperar para no sobrecargar la API
                    time.sleep(1)
                else:
                    logger.error(f"Error al obtener datos: {response.status_code} - {response.text}")
                    break
            
            # Convertir a DataFrame
            df = self._process_adzuna_data(all_jobs)
            
            # Guardar datos crudos
            output_path = os.path.join('data', 'raw', 'ofertas_adzuna.csv')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_csv(output_path, index=False, encoding='utf-8')
            
            logger.info(f"Datos guardados en {output_path}")
            return df
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de Adzuna: {str(e)}", exc_info=True)
            return pd.DataFrame()

    def _process_adzuna_data(self, adzuna_jobs):
        """Procesar datos de Adzuna para crear un DataFrame."""
        processed_jobs = pd.DataFrame({
            'id': [job.get('id') for job in adzuna_jobs],
            'titulo': [job.get('title') for job in adzuna_jobs],
            'descripcion': [job.get('description') for job in adzuna_jobs],
            'empresa': [job.get('company', {}).get('display_name') for job in adzuna_jobs],
            'ubicacion': [job.get('location', {}).get('display_name') for job in adzuna_jobs],
            'tipo_contrato': [job.get('contract_type') for job in adzuna_jobs],
            'salario': [job.get('salary_max') for job in adzuna_jobs], # O 'salary_min', o un promedio
            'fecha_publicacion': [job.get('created') for job in adzuna_jobs],
            'url': [job.get('redirect_url') for job in adzuna_jobs],
        })
        
        # Agregar timestamp
        processed_jobs['fecha_extraccion'] = datetime.now()
        
        return processed_jobs
    
    def get_tech_jobs(self, keywords='python developer', location='', results_per_page=50, max_pages=5):
        """
        Obtener ofertas de trabajo del sector tecnológico desde la API de Reed UK (sin autenticación compleja).
        
        Args:
            keywords (str): Palabras clave para la búsqueda
            location (str): Ubicación geográfica (opcional)
            results_per_page (int): Resultados por página
            max_pages (int): Máximo número de páginas a obtener
            
        Returns:
            pd.DataFrame: DataFrame con ofertas de empleo reales
        """
        logger.info(f"Obteniendo ofertas de empleo reales para '{keywords}'...")
        
        base_url = "https://remotive.com/api/remote-jobs"
        
        all_jobs = []
        
        try:
            params = {
                'search': keywords,
                'limit': 100  # Obtener máximo número de resultados
            }
            
            response = requests.get(base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('jobs', [])
                
                if jobs:
                    logger.info(f"Obtenidas {len(jobs)} ofertas de trabajo reales")
                    all_jobs.extend(jobs)
                else:
                    logger.warning("No se encontraron ofertas con esos criterios")
            else:
                logger.error(f"Error en la solicitud: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error obteniendo datos: {str(e)}")
            
        # Si no hay resultados, intentar con GitHub Jobs API (ahora RSS feed)
        if not all_jobs:
            try:
                github_jobs_url = "https://stackoverflow.com/jobs/feed"
                response = requests.get(github_jobs_url)
                
                if response.status_code == 200:
                    # Procesar el feed RSS
                    import xml.etree.ElementTree as ET
                    from io import StringIO
                    
                    root = ET.fromstring(response.content)
                    items = root.findall('.//item')
                    
                    for item in items:
                        title = item.find('title').text if item.find('title') is not None else 'No title'
                        link = item.find('link').text if item.find('link') is not None else ''
                        description = item.find('description').text if item.find('description') is not None else ''
                        pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                        
                        job = {
                            'title': title,
                            'company': 'StackOverflow Jobs',
                            'description': description,
                            'url': link,
                            'publication_date': pub_date
                        }
                        
                        all_jobs.append(job)
                    
                    logger.info(f"Obtenidas {len(all_jobs)} ofertas de Stack Overflow Jobs")
                else:
                    logger.error(f"Error obteniendo datos de Stack Overflow: {response.status_code}")
            except Exception as e:
                logger.error(f"Error procesando datos de Stack Overflow: {str(e)}")
        
        # Si aún no hay resultados, intentar con Hacker News Who's Hiring
        if not all_jobs:
            try:
                hn_url = "https://hacker-news.firebaseio.com/v0/item/27715057.json"
                response = requests.get(hn_url)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'kids' in data:
                        comment_ids = data['kids'][:100]  # Limitar a 100 comentarios
                        
                        for comment_id in comment_ids:
                            try:
                                comment_url = f"https://hacker-news.firebaseio.com/v0/item/{comment_id}.json"
                                comment_response = requests.get(comment_url)
                                
                                if comment_response.status_code == 200:
                                    comment_data = comment_response.json()
                                    
                                    if 'text' in comment_data:
                                        # Extraer información del comentario
                                        text = comment_data['text']
                                        
                                        # Añadir al conjunto de datos
                                        job = {
                                            'title': self._extract_job_title(text),
                                            'company': self._extract_company(text),
                                            'location': self._extract_location(text),
                                            'description': text,
                                            'url': f"https://news.ycombinator.com/item?id={comment_id}",
                                            'publication_date': datetime.fromtimestamp(comment_data.get('time', 0)).strftime('%Y-%m-%d')
                                        }
                                        
                                        all_jobs.append(job)
                            except Exception as e:
                                logger.error(f"Error procesando comentario {comment_id}: {str(e)}")
                                continue
                                
                        logger.info(f"Obtenidas {len(all_jobs)} ofertas de HN Who's Hiring")
            except Exception as e:
                logger.error(f"Error procesando datos de HN: {str(e)}")
                
        # Procesar resultados
        if not all_jobs:
            logger.warning("No se pudieron obtener datos reales de ninguna fuente.")
            return pd.DataFrame()
            
        logger.info(f"Procesando {len(all_jobs)} ofertas de empleo...")
        
        # Extraer información relevante
        processed_jobs = []
        
        for job in all_jobs:
            try:
                # Extraer tecnologías mencionadas
                description = job.get('description', '')
                technologies = self._extract_technologies(description)
                
                # Crear registro procesado
                processed_job = {
                    'titulo': job.get('title', 'No especificado'),
                    'empresa': job.get('company', 'No especificado'),
                    'ubicacion': job.get('location', job.get('candidate_required_location', 'Remote')),
                    'fecha_publicacion': job.get('publication_date', job.get('created_at', '')),
                    'tipo_contrato': job.get('job_type', 'No especificado'),
                    'salario': job.get('salary', 'No especificado'),
                    'descripcion': description,
                    'tecnologias': ', '.join(technologies),
                    'url': job.get('url', job.get('link', '')),
                    'id': job.get('id', str(hash(str(job)))),
                    'fuente': 'Remotive/HN/StackOverflow'
                }
                
                processed_jobs.append(processed_job)
                
            except Exception as e:
                logger.error(f"Error procesando oferta: {str(e)}")
                continue
        
        # Convertir a DataFrame
        df = pd.DataFrame(processed_jobs)
        
        # Agregar timestamp
        df['fecha_extraccion'] = datetime.now()
        
        return df
        
    def _extract_job_title(self, text):
        """Extraer título del trabajo de la descripción."""
        import re
        
        # Patrones comunes para títulos de trabajo
        patterns = [
            r'hiring.+?([\w\s]+?(developer|engineer|scientist|architect|designer|manager|lead|analyst|admin|sre|devops|programmer|consultant)[\w\s]*)',
            r'hiring.+?([\w\s]+(developer|engineer|scientist|architect|designer|manager|lead|analyst|admin|sre|devops|programmer|consultant)[\w\s]*)',
            r'([\w\s]+(developer|engineer|scientist|architect|designer|manager|lead|analyst|admin|sre|devops|programmer|consultant)[\w\s]*)',
        ]
        
        for pattern in patterns:
            matches = re.search(pattern, text, re.IGNORECASE)
            if matches and matches.group(1):
                return matches.group(1).strip()
                
        return "Tech Position"
        
    def _extract_company(self, text):
        """Extraer nombre de la empresa."""
        import re
        
        # Patrones para nombres de empresa
        company_patterns = [
            r'(.+?)(is hiring|hiring for|hiring|looking for)',
            r'at (.+?)(\.|,|\|)',
            r'\| (.+?) \|',
        ]
        
        for pattern in company_patterns:
            matches = re.search(pattern, text, re.IGNORECASE)
            if matches and matches.group(1):
                company = matches.group(1).strip()
                # Limpiar caracteres no deseados
                company = re.sub(r'[\|\-\[\]\(\)\{\}]', '', company).strip()
                if len(company) > 3 and len(company) < 50:
                    return company
        
        return "Unknown Company"
        
    def _extract_location(self, text):
        """Extraer ubicación del trabajo."""
        import re
        
        # Buscar patrón REMOTE o ubicaciones
        if re.search(r'\bREMOTE\b', text, re.IGNORECASE):
            return "Remote"
            
        # Patrones comunes para ubicaciones
        location_patterns = [
            r'\bin ([\w\s]+?,\s*[\w\s]+)\b',
            r'\blocation[\s:]+([\w\s]+?,\s*[\w\s]+)\b',
            r'\b(san francisco|new york|berlin|london|tokyo|paris|madrid|barcelona|amsterdam|toronto|vancouver|sydney|singapore)\b'
        ]
        
        for pattern in location_patterns:
            matches = re.search(pattern, text, re.IGNORECASE)
            if matches and matches.group(1):
                return matches.group(1).strip()
                
        return "Location not specified"
    
    def _extract_technologies(self, description):
        """Extraer tecnologías de la descripción del trabajo."""
        common_techs = [
            # Lenguajes
            'Python', 'JavaScript', 'Java', 'C#', 'C++', 'PHP', 'Go', 'Ruby', 'Swift', 
            'Kotlin', 'TypeScript', 'Scala', 'Rust', 'R', 'Dart', 'SQL',
            
            # Frameworks
            'React', 'Angular', 'Vue', 'Django', 'Spring', 'Laravel', 'Flask', 'Express',
            'ASP.NET', 'Rails', 'Flutter', 'Next.js', 'Symfony', 'FastAPI', 'jQuery',
            
            # Bases de datos
            'MySQL', 'PostgreSQL', 'MongoDB', 'SQL Server', 'Oracle', 'Redis', 'Cassandra',
            'Elasticsearch', 'SQLite', 'DynamoDB', 'Firebase', 'Neo4j', 'MariaDB',
            
            # Cloud
            'AWS', 'Azure', 'Google Cloud', 'GCP', 'Heroku', 'Docker', 'Kubernetes',
            'Jenkins', 'GitLab', 'GitHub Actions', 'Terraform', 'Ansible',
            
            # Otras tecnologías
            'Machine Learning', 'AI', 'Deep Learning', 'DevOps', 'CI/CD', 'Agile',
            'Scrum', 'REST', 'GraphQL', 'Microservices', 'API', 'JSON', 'XML',
            'AJAX', 'UI/UX', 'Frontend', 'Backend', 'Full Stack', 'SPA', 'PWA',
            'TDD', 'BDD', 'ETL', 'Hadoop', 'Spark', 'Tableau', 'Power BI', 'Looker',
            'Excel', 'VBA', 'JIRA', 'Confluence', 'Git', 'Linux', 'Windows', 'macOS'
        ]
        
        technologies = []
        for tech in common_techs:
            if tech.lower() in description.lower():
                # Comprobar que es una palabra completa
                technologies.append(tech)
        
        return technologies
    
    def _generate_mock_adzuna_data(self, num_jobs=100):
        """Generar datos simulados con estructura similar a la API de Adzuna."""
        logger.info(f"Generando {num_jobs} ofertas de empleo simuladas...")
        
        # Listas de datos simulados
        job_titles = [
            "Desarrollador Python Senior", "Frontend Developer React", "Data Scientist", 
            "DevOps Engineer", "Ingeniero de Software Java", "Full Stack Developer",
            "Backend Developer Node.js", "UX/UI Designer", "CTO", "Product Manager",
            "Mobile Developer", "Machine Learning Engineer", "QA Engineer",
            "Data Engineer", "Technical Lead", "Cloud Architect", "Scrum Master",
            "Software Architect", "Site Reliability Engineer", "Cybersecurity Analyst"
        ]
        
        companies = [
            "TechCorp", "DataMinds", "CodeFusion", "InnovateTech", "ByteLogic",
            "CloudNative", "DevFusion", "ElectronMinds", "FutureCode", "GlobalTech",
            "HyperData", "IntelliSoft", "JavaPros", "KernelLabs", "LogicWorks"
        ]
        
        locations = [
            "Madrid", "Barcelona", "Valencia", "Sevilla", "Málaga", "Bilbao",
            "Zaragoza", "Alicante", "Remoto", "Híbrido (Madrid)", "Híbrido (Barcelona)"
        ]
        
        contract_types = ["Completa", "Parcial", "Indefinido", "Temporal", "Freelance", "Prácticas"]
        categories = ["IT Jobs", "Tecnología", "Desarrollo de Software", "Data Science", "DevOps", "UX/UI"]
        
        # Generar datos
        mock_jobs = []
        for i in range(num_jobs):
            # Salario aleatorio
            salary_min = round(25000 + 5000 * np.random.random() * 10, -3)
            salary_max = round(salary_min + 5000 * np.random.random() * 10, -3)
            
            # Fecha aleatoria en los últimos 30 días
            created_date = pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(0, 30))
            
            # Tecnologías aleatorias
            tech_pool = [
                "Python", "JavaScript", "Java", "SQL", "React", "Docker", "AWS",
                "Angular", "Node.js", "Spring", "Git", "MongoDB", "Linux",
                "TypeScript", "Kubernetes", "Django", "Flask", "Vue.js",
                "Express", "PostgreSQL", "MySQL", "Azure", "GCP", "REST API",
                "GitLab", "GitHub Actions", "CI/CD", "Jira", "Agile", "Scrum"
            ]
            
            techs = np.random.choice(tech_pool, size=np.random.randint(3, 8), replace=False)
            
            # Descripción simulada
            tech_description = ", ".join(techs)
            description = (
                f"Estamos buscando un profesional con experiencia en {tech_description}. "
                f"La persona seleccionada se incorporará a un equipo dinámico para desarrollar "
                f"soluciones tecnológicas innovadoras. Se requiere experiencia de 2+ años, "
                f"capacidad de trabajo en equipo y metodologías ágiles."
            )
            
            # Crear oferta
            job = {
                'id': f"job-{i+1000}",
                'title': np.random.choice(job_titles),
                'description': description,
                'company': {'display_name': np.random.choice(companies)},
                'location': {'display_name': np.random.choice(locations)},
                'contract_type': np.random.choice(contract_types),
                'salary_max': salary_max,
                'created': created_date.strftime("%Y-%m-%d"),
                'redirect_url': f"https://www.ejemplo.com/job/{i+1000}",
            }
            
            mock_jobs.append(job)
        
        # Convertir a DataFrame
        df = self._process_adzuna_data(mock_jobs)
        
        # Guardar datos simulados
        output_path = os.path.join('data', 'raw', 'ofertas_adzuna_mock.csv')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        logger.info(f"Datos simulados guardados en {output_path}")
        
        return df
    
    def get_stack_overflow_survey(self, year=2023):
        """
        Generar datos de encuesta simulados en lugar de intentar descargar la encuesta real,
        ya que la descarga puede fallar por diversas razones.
        
        Args:
            year (int): Año simulado de la encuesta
            
        Returns:
            pd.DataFrame: DataFrame con datos simulados de la encuesta
        """
        logger.info(f"Generando datos simulados de la encuesta de Stack Overflow {year}...")
        
        # Número de respuestas a generar
        num_responses = 300
        
        # Listas de datos
        programming_languages = [
            "JavaScript", "HTML/CSS", "Python", "SQL", "TypeScript", "Java", "C#", "Bash/Shell", 
            "C++", "PHP", "C", "PowerShell", "Go", "Rust", "Ruby", "Dart", "Assembly", "Swift", 
            "Kotlin", "R", "VBA", "MATLAB", "Lua", "Groovy", "Delphi", "Scala", "Objective-C"
        ]
        
        databases = [
            "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Microsoft SQL Server", 
            "Elasticsearch", "Oracle", "DynamoDB", "MariaDB", "Firebase Realtime Database", 
            "Cassandra", "IBM DB2", "Neo4j", "Couchbase", "Supabase", "CouchDB", "InfluxDB"
        ]
        
        web_frameworks = [
            "React", "jQuery", "Express", "Angular", "Vue.js", "ASP.NET Core", "Flask", 
            "Django", "Spring Boot", "Laravel", "Symfony", "Ruby on Rails", "Next.js", 
            "FastAPI", "Svelte", "Gatsby", "NestJS", "Nuxt.js", "Blazor", "Phoenix"
        ]
        
        tools = [
            "Git", "Docker", "npm", "Yarn", "Kubernetes", "Terraform", "Ansible", "Jenkins", 
            "GitHub Actions", "CircleCI", "Azure DevOps", "Webpack", "Rollup", "Vite", "Gradle", 
            "Maven", "CMake", "Bash", "PowerShell", "Pulumi", "Chef", "Puppet", "Prometheus"
        ]
        
        education = [
            "Licenciatura en Informática", "Máster en Ciencias de la Computación", 
            "Grado en Ingeniería Informática", "Autodidacta", "Bootcamp de programación", 
            "Formación Profesional", "Doctorado en Informática", "Curso online", "Licenciatura en Matemáticas"
        ]
        
        experience_levels = ["0-1 años", "1-3 años", "3-5 años", "5-10 años", "10-15 años", "15+ años"]
        
        job_titles = [
            "Desarrollador Full-stack", "Desarrollador Back-end", "Desarrollador Front-end", 
            "DevOps", "Científico de Datos", "Ingeniero de Machine Learning", "Administrador de BD", 
            "Arquitecto de Software", "SRE", "CTO", "Desarrollador Móvil", "QA Engineer", 
            "Product Manager", "UX/UI Designer", "Desarrollador de Videojuegos", "Analista de Sistemas"
        ]
        
        countries = [
            "España", "Estados Unidos", "Alemania", "Reino Unido", "Francia", "Canadá", 
            "Brasil", "India", "Australia", "Japón", "México", "Argentina", "Colombia", 
            "Portugal", "Italia", "Países Bajos", "Suecia", "Suiza", "Polonia", "Finlandia"
        ]
        
        # Generar datos
        data = []
        for i in range(num_responses):
            # Características básicas
            age = np.random.randint(18, 65)
            years_coding = min(age - 15, np.random.randint(0, 30))  # No más años programando que edad - 15
            
            # Lenguajes utilizados (2-5 lenguajes)
            num_langs = np.random.randint(2, 6)
            used_languages = np.random.choice(programming_languages, size=num_langs, replace=False).tolist()
            main_language = np.random.choice(used_languages)
            
            # Bases de datos (1-3 bases de datos)
            num_dbs = np.random.randint(1, 4)
            used_dbs = np.random.choice(databases, size=num_dbs, replace=False).tolist()
            main_db = np.random.choice(used_dbs)
            
            # Frameworks (1-4 frameworks)
            num_frameworks = np.random.randint(1, 5)
            used_frameworks = np.random.choice(web_frameworks, size=num_frameworks, replace=False).tolist()
            main_framework = np.random.choice(used_frameworks)
            
            # Herramientas (2-6 herramientas)
            num_tools = np.random.randint(2, 7)
            used_tools = np.random.choice(tools, size=num_tools, replace=False).tolist()
            
            # Características profesionales
            job_title = np.random.choice(job_titles)
            country = np.random.choice(countries)
            exp_level = np.random.choice(experience_levels, p=[0.15, 0.25, 0.25, 0.20, 0.10, 0.05])
            education_level = np.random.choice(education)
            company_size = np.random.choice(["1-10", "11-50", "51-100", "101-500", "501-1000", "1000+"])
            work_mode = np.random.choice(["Remoto", "Presencial", "Híbrido"], p=[0.4, 0.2, 0.4])
            
            # Compensación
            if "0-1" in exp_level:
                salary_base = 25000
                salary_range = 10000
            elif "1-3" in exp_level:
                salary_base = 35000
                salary_range = 15000
            elif "3-5" in exp_level:
                salary_base = 45000
                salary_range = 20000
            elif "5-10" in exp_level:
                salary_base = 65000
                salary_range = 25000
            elif "10-15" in exp_level:
                salary_base = 85000
                salary_range = 30000
            else:  # 15+
                salary_base = 100000
                salary_range = 40000
                
            # Ajuste por país (mayor en países con mayor coste de vida)
            country_factor = 1.0
            if country in ["Estados Unidos", "Suiza", "Australia", "Reino Unido"]:
                country_factor = 1.5
            elif country in ["Alemania", "Canadá", "Japón", "Suecia", "Finlandia"]:
                country_factor = 1.3
            elif country in ["España", "Italia", "Portugal"]:
                country_factor = 0.8
            elif country in ["México", "Brasil", "Colombia", "Argentina"]:
                country_factor = 0.6
                
            salary = round((salary_base + np.random.randn() * salary_range) * country_factor, -2)
            
            # Satisfacción laboral (1-10)
            job_satisfaction = min(10, max(1, round(5 + 2 * np.random.randn())))
            
            # Crear registro
            record = {
                "ResponseId": f"R_{i+1000}",
                "Edad": age,
                "AniosProgramando": years_coding,
                "País": country,
                "Educación": education_level,
                "PuestoTrabajo": job_title,
                "TamañoEmpresa": company_size,
                "ModoTrabajo": work_mode,
                "NivelExperiencia": exp_level,
                "LenguajePrincipal": main_language,
                "LenguajesUtilizados": ", ".join(used_languages),
                "BaseDatosPrincipal": main_db,
                "BasesDatosUtilizadas": ", ".join(used_dbs),
                "FrameworkPrincipal": main_framework,
                "FrameworksUtilizados": ", ".join(used_frameworks),
                "HerramientasUtilizadas": ", ".join(used_tools),
                "SalarioAnual": salary,
                "SatisfacciónLaboral": job_satisfaction,
                "HorasTrabajoSemanal": np.random.choice([35, 37.5, 40, 42.5, 45, 50, 55], p=[0.1, 0.15, 0.4, 0.15, 0.1, 0.05, 0.05]),
                "AñoEncuesta": year
            }
            
            data.append(record)
        
        # Crear DataFrame
        df = pd.DataFrame(data)
        
        # Guardar datos como referencia
        output_path = os.path.join('data', 'external', f"stack-overflow-survey-results-{year}.csv")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        logger.info(f"Datos simulados de encuesta generados y guardados en {output_path}")
        logger.info(f"Total de respuestas: {len(df)}")
        
        return df

def fetch_real_job_data(use_apis=True, download_survey=True, keywords=None):
    """
    Recopilar datos REALES de empleo para análisis del mercado laboral.
    
    Args:
        use_apis (bool): Si es True, obtendrá datos reales desde APIs públicas.
        download_survey (bool): Si es True, obtendrá datos de encuestas (o generará datos similares si no es posible).
        keywords (list): Lista de palabras clave para la búsqueda.
        
    Returns:
        tuple: (jobs_df, survey_df) - DataFrames con los datos recolectados
    """
    logger.info("Iniciando recopilación de datos REALES para análisis...")
    
    # Crear colector sin forzar datos simulados
    collector = JobDataCollector(force_mock=False)
    jobs_df = pd.DataFrame()
    survey_df = pd.DataFrame()
    
    # Usar palabras clave por defecto si no se proporcionan
    if keywords is None:
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
    
    # Obtener datos REALES de empleos de múltiples fuentes
    if use_apis:
        all_jobs_data = []
        
        for keyword in keywords:
            try:
                logger.info(f"Obteniendo datos reales para búsqueda: {keyword}")
                # Usar el nuevo método que obtiene datos reales
                keyword_jobs = collector.get_tech_jobs(keywords=keyword)
                
                if not keyword_jobs.empty:
                    logger.info(f"Obtenidas {len(keyword_jobs)} ofertas reales para '{keyword}'")
                    all_jobs_data.append(keyword_jobs)
                else:
                    logger.warning(f"No se encontraron ofertas reales para '{keyword}'")
                    
                # Esperar un poco entre búsquedas para no sobrecargar las APIs
                time.sleep(1.5)
                
            except Exception as e:
                logger.error(f"Error obteniendo datos para '{keyword}': {str(e)}")
                continue
        
        # Combinar todos los resultados
        if all_jobs_data:
            jobs_df = pd.concat(all_jobs_data, ignore_index=True)
            
            # Eliminar duplicados si hay
            if 'id' in jobs_df.columns:
                jobs_df = jobs_df.drop_duplicates(subset=['id'])
            else:
                jobs_df = jobs_df.drop_duplicates(subset=['titulo', 'empresa'])
            
            # Guardar datos en el directorio raw
            raw_dir = os.path.join('data', 'raw')
            os.makedirs(raw_dir, exist_ok=True)
            
            csv_path = os.path.join(raw_dir, 'ofertas_tech_reales.csv')
            jobs_df.to_csv(csv_path, index=False)
            
            logger.info(f"Datos REALES de empleos guardados en {csv_path} ({len(jobs_df)} ofertas)")
        else:
            logger.warning("No se pudieron obtener datos reales de ninguna búsqueda. Intenta más tarde.")
    
    # Obtener datos de encuesta (por ahora usamos simulados porque las encuestas reales son difíciles de obtener)
    if download_survey:
        try:
            # Intentar obtener datos de Stack Overflow Developer Survey (si tenemos acceso)
            # Para datos reales, necesitaríamos acceder a la encuesta oficial de Stack Overflow
            logger.warning("Stack Overflow Developer Survey requiere descarga manual.")
            logger.info("Usando datos simulados de encuesta como alternativa")
            survey_df = collector.get_stack_overflow_survey()
            logger.info(f"Datos de encuesta generados con {len(survey_df)} registros")
        except Exception as e:
            logger.error(f"Error obteniendo datos de encuesta: {str(e)}")
    
    return jobs_df, survey_df

if __name__ == "__main__":
    fetch_real_job_data(force_mock=True)
