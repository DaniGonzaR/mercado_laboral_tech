"""
Módulo para generar datos simulados del mercado laboral tecnológico.
"""
import os
import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataGenerator:
    """Clase para generar datos simulados del mercado laboral tecnológico."""
    
    def __init__(self):
        """Inicializar el generador de datos."""
        self.empresas = [
            "TechSolutions", "DataMind", "CodeCraft", "DigitalWave", "InnovateTech",
            "ByteLogic", "CloudNative", "DevFusion", "ElectronMinds", "FutureCode",
            "GlobalTech", "HyperData", "IntelliSoft", "JavaPros", "KernelLabs",
            "LogicWorks", "MobileFirst", "NetArchitects", "OptimizeIT", "PixelWave",
            "QuantumSystems", "ReactMasters", "SecureTech", "TensorMinds", "UXPioneer",
            "VirtualVision", "WebWizards", "XenonData", "YieldTech", "ZenithCode"
        ]
        
        self.ubicaciones = [
            "Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao",
            "Málaga", "Zaragoza", "Alicante", "Murcia", "Las Palmas",
            "Remoto", "Híbrido (Madrid)", "Híbrido (Barcelona)", "Híbrido (Valencia)",
            "Remoto (Europa)", "Remoto (España)"
        ]
        
        self.tipos_contrato = [
            "Indefinido", "Temporal", "Prácticas", "Formativo", "Freelance",
            "Por obra y servicio", "Mercantil", "Temporal con posibilidad de indefinido"
        ]
        
        self.jornadas = [
            "Completa", "Parcial (mañanas)", "Parcial (tardes)", "Por horas",
            "Intensiva", "Flexible", "Turnos rotativos", "Fin de semana"
        ]
        
        self.lenguajes = [
            "Python", "JavaScript", "Java", "C#", "C++", "PHP", "Go", "Ruby",
            "Swift", "Kotlin", "TypeScript", "Scala", "Rust", "R", "Dart"
        ]
        
        self.frameworks = [
            "React", "Angular", "Vue.js", "Django", "Spring Boot", "Laravel",
            "Flask", "Express.js", "ASP.NET", "Ruby on Rails", "Flutter", "Next.js",
            "Symfony", "FastAPI", "TensorFlow", "PyTorch", "Pandas"
        ]
        
        self.bases_datos = [
            "MySQL", "PostgreSQL", "MongoDB", "SQL Server", "Oracle", "Redis",
            "Cassandra", "Elasticsearch", "SQLite", "DynamoDB", "Firebase",
            "Neo4j", "MariaDB", "Couchbase", "InfluxDB", "Snowflake", "BigQuery"
        ]
        
        self.herramientas = [
            "Docker", "Kubernetes", "Git", "Jenkins", "GitHub Actions", "AWS",
            "Azure", "Google Cloud", "Terraform", "Ansible", "Jira", "Confluence",
            "Prometheus", "Grafana", "ELK Stack", "Postman", "SonarQube"
        ]
        
        self.habilidades_blandas = [
            "Trabajo en equipo", "Comunicación", "Resolución de problemas",
            "Metodologías ágiles", "Scrum", "Kanban", "Liderazgo", "Gestión del tiempo",
            "Pensamiento crítico", "Adaptabilidad", "Creatividad", "Empatía",
            "Resiliencia", "Capacidad analítica", "Orientación a resultados"
        ]
        
        self.titulos = [
            "Desarrollador/a {lenguaje} {nivel}",
            "Programador/a {lenguaje} {nivel}",
            "Ingeniero/a de Software {nivel}",
            "Arquitecto/a de Software {nivel}",
            "Desarrollador/a {framework} {nivel}",
            "Ingeniero/a DevOps {nivel}",
            "Data Scientist {nivel}",
            "Data Engineer {nivel}",
            "Full Stack Developer {nivel}",
            "Frontend Developer {nivel}",
            "Backend Developer {nivel}",
            "Mobile Developer {lenguaje} {nivel}",
            "QA Engineer {nivel}",
            "UX/UI Designer {nivel}",
            "Product Manager {nivel}",
            "Technical Lead {nivel}",
            "Scrum Master {nivel}",
            "Machine Learning Engineer {nivel}",
            "Cloud Architect {nivel}",
            "Database Administrator {nivel}",
            "Systems Administrator {nivel}",
            "Network Engineer {nivel}",
            "Security Engineer {nivel}",
            "Business Intelligence Analyst {nivel}",
            "IT Project Manager {nivel}"
        ]
        
        self.niveles = ["Junior", "Semisenior", "Senior", "Lead", "Staff", "Principal"]
        
        # Rangos salariales aproximados en euros anuales
        self.rangos_salariales = {
            "Junior": (18000, 28000),
            "Semisenior": (28000, 38000),
            "Senior": (38000, 60000),
            "Lead": (50000, 75000),
            "Staff": (65000, 85000),
            "Principal": (80000, 120000)
        }
    
    def generar_ofertas_empleo(self, num_ofertas=100):
        """
        Generar datos simulados de ofertas de empleo en tecnología.
        
        Args:
            num_ofertas (int): Número de ofertas a generar.
            
        Returns:
            pd.DataFrame: DataFrame con las ofertas generadas.
        """
        logger.info(f"Generando {num_ofertas} ofertas de empleo simuladas...")
        
        ofertas = []
        fecha_actual = datetime.now()
        
        for _ in range(num_ofertas):
            # Seleccionar un nivel aleatorio
            nivel = random.choice(self.niveles)
            
            # Generar un lenguaje principal y otros aleatorios
            lenguaje_principal = random.choice(self.lenguajes)
            
            # Generar requisitos (tecnologías)
            requisitos_tecnicos = []
            
            # Agregar lenguaje principal
            requisitos_tecnicos.append(lenguaje_principal)
            
            # Agregar frameworks asociados (1-3)
            for _ in range(random.randint(1, 3)):
                framework = random.choice(self.frameworks)
                if framework not in requisitos_tecnicos:
                    requisitos_tecnicos.append(framework)
            
            # Agregar bases de datos (1-2)
            for _ in range(random.randint(1, 2)):
                db = random.choice(self.bases_datos)
                if db not in requisitos_tecnicos:
                    requisitos_tecnicos.append(db)
            
            # Agregar herramientas (1-3)
            for _ in range(random.randint(1, 3)):
                tool = random.choice(self.herramientas)
                if tool not in requisitos_tecnicos:
                    requisitos_tecnicos.append(tool)
            
            # Generar título de la oferta
            titulo_template = random.choice(self.titulos)
            titulo = titulo_template.replace("{lenguaje}", lenguaje_principal).replace("{framework}", 
                                             random.choice(self.frameworks)).replace("{nivel}", nivel)
            
            # Generar rango salarial basado en nivel
            min_salary, max_salary = self.rangos_salariales[nivel]
            salario_min = round(min_salary + random.uniform(-2000, 2000), -3)  # Redondear a miles
            salario_max = round(max_salary + random.uniform(-2000, 2000), -3)  # Redondear a miles
            
            # Asegurar que min < max
            if salario_min >= salario_max:
                salario_max = salario_min + 5000
            
            # Formato de salario
            salario = f"{salario_min:.0f} - {salario_max:.0f} € Bruto/año"
            
            # Generar fecha de publicación (últimos 30 días)
            dias_atras = random.randint(0, 30)
            fecha_publicacion = (fecha_actual - timedelta(days=dias_atras)).strftime("%d/%m/%Y")
            
            # Generar descripción aleatoria
            descripcion = self._generar_descripcion(nivel, requisitos_tecnicos)
            
            # Generar experiencia requerida basada en nivel
            experiencia = self._nivel_a_experiencia(nivel)
            
            # Crear oferta
            oferta = {
                "titulo": titulo,
                "empresa": random.choice(self.empresas),
                "ubicacion": random.choice(self.ubicaciones),
                "fecha_publicacion": fecha_publicacion,
                "tipo_contrato": random.choice(self.tipos_contrato),
                "jornada": random.choice(self.jornadas),
                "salario": salario,
                "salario_min": salario_min,
                "salario_max": salario_max,
                "experiencia": experiencia,
                "nivel": nivel,
                "descripcion": descripcion,
                "requisitos": ", ".join(requisitos_tecnicos),
                "tecnologias": requisitos_tecnicos,
                "url": f"https://ejemplo.com/oferta-{_+1}"
            }
            
            ofertas.append(oferta)
        
        # Convertir a DataFrame
        df = pd.DataFrame(ofertas)
        df['fecha_extraccion'] = datetime.now()
        
        # Guardar los datos
        output_path = os.path.join('data', 'raw', 'ofertas_tecnologia_simuladas.csv')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        logger.info(f"Generados {num_ofertas} ofertas simuladas en {output_path}")
        
        return df
    
    def generar_encuesta_desarrolladores(self, num_encuestas=200):
        """
        Generar datos simulados de encuestas a desarrolladores.
        
        Args:
            num_encuestas (int): Número de respuestas a generar.
            
        Returns:
            pd.DataFrame: DataFrame con las encuestas generadas.
        """
        logger.info(f"Generando {num_encuestas} encuestas simuladas de desarrolladores...")
        
        encuestas = []
        
        for _ in range(num_encuestas):
            # Edad típica de profesionales tecnológicos (22-65)
            edad = random.randint(22, 65)
            
            # Experiencia correlacionada con la edad
            max_experiencia = max(0, edad - 22)  # Considerando que se empieza a trabajar como mínimo a los 22
            experiencia = min(max_experiencia, random.randint(0, 25))  # Máximo 25 años de experiencia
            
            # Género (mantener diversidad)
            genero = random.choices(["Masculino", "Femenino", "No binario", "Prefiero no decirlo"], 
                                  weights=[0.65, 0.30, 0.03, 0.02])[0]
            
            # Nivel correlacionado con la experiencia
            nivel = self._experiencia_a_nivel(experiencia)
            
            # Stack tecnológico principal (elección de tecnologías principales)
            stack_principal = {
                "lenguaje_principal": random.choice(self.lenguajes),
                "framework_principal": random.choice(self.frameworks),
                "bd_principal": random.choice(self.bases_datos)
            }
            
            # Stack completo (todas las tecnologías que conoce)
            conocimientos = set()
            conocimientos.add(stack_principal["lenguaje_principal"])
            conocimientos.add(stack_principal["framework_principal"])
            conocimientos.add(stack_principal["bd_principal"])
            
            # Agregar lenguajes adicionales (0-4)
            for _ in range(random.randint(0, 4)):
                conocimientos.add(random.choice(self.lenguajes))
            
            # Agregar frameworks adicionales (0-5)
            for _ in range(random.randint(0, 5)):
                conocimientos.add(random.choice(self.frameworks))
            
            # Agregar bases de datos adicionales (0-3)
            for _ in range(random.randint(0, 3)):
                conocimientos.add(random.choice(self.bases_datos))
            
            # Agregar herramientas (0-6)
            for _ in range(random.randint(0, 6)):
                conocimientos.add(random.choice(self.herramientas))
            
            # Salario actual (correlacionado con nivel y experiencia)
            salario_base = self._salario_por_nivel(nivel)
            # Ajustar por experiencia (+2% por año adicional después del mínimo)
            min_exp = self._min_experiencia_por_nivel(nivel)
            ajuste_exp = max(0, experiencia - min_exp) * 0.02
            # Ajuste aleatorio (-10% a +20%)
            ajuste_aleatorio = random.uniform(-0.10, 0.20)
            
            salario_actual = salario_base * (1 + ajuste_exp + ajuste_aleatorio)
            
            # Satisfacción laboral (1-10)
            # Correlacionada con el salario (mayor salario, mayor satisfacción en promedio)
            # Pero con variabilidad
            salario_percentil = (salario_actual - 20000) / 80000  # Normalizado aproximadamente
            salario_percentil = max(0, min(1, salario_percentil))  # Limitar entre 0 y 1
            media_satisfaccion = 5 + (salario_percentil * 3)  # La media va de 5 a 8 según el salario
            satisfaccion = max(1, min(10, round(random.normalvariate(media_satisfaccion, 1.5))))
            
            # Ubicación
            # Remoto correlacionado con satisfacción (más probable con mayor satisfacción)
            prob_remoto = 0.2 + (satisfaccion / 30)  # Probabilidad base + bonificación por satisfacción
            es_remoto = random.random() < prob_remoto
            
            if es_remoto:
                ubicacion = random.choice(["Remoto", "Remoto (España)", "Remoto (Europa)", 
                                          "Híbrido (Madrid)", "Híbrido (Barcelona)"])
            else:
                ubicacion = random.choice([u for u in self.ubicaciones if "Remoto" not in u and "Híbrido" not in u])
            
            # Nivel de educación
            educacion = random.choices(
                ["Autodidacta", "Bootcamp", "Grado Superior", "Grado Universitario", "Máster", "Doctorado"],
                weights=[0.10, 0.15, 0.20, 0.40, 0.10, 0.05]
            )[0]
            
            # Horas de trabajo semanales
            # Base: 40 horas, con variaciones
            horas_semanales = random.choices(
                [35, 37.5, 40, 42.5, 45, 50, 55, 60],
                weights=[0.05, 0.10, 0.50, 0.15, 0.10, 0.05, 0.03, 0.02]
            )[0]
            
            # Crear encuesta
            encuesta = {
                "id": _+1,
                "edad": edad,
                "genero": genero,
                "experiencia_anios": experiencia,
                "nivel": nivel,
                "educacion": educacion,
                "ubicacion": ubicacion,
                "remoto": "Sí" if "Remoto" in ubicacion or "Híbrido" in ubicacion else "No",
                "lenguaje_principal": stack_principal["lenguaje_principal"],
                "framework_principal": stack_principal["framework_principal"],
                "bd_principal": stack_principal["bd_principal"],
                "conocimientos": ", ".join(conocimientos),
                "horas_semanales": horas_semanales,
                "salario_actual": round(salario_actual, -2),  # Redondear a centenas
                "satisfaccion_laboral": satisfaccion,
                "busca_trabajo": random.choices(["Sí", "No"], weights=[1-satisfaccion/12, satisfaccion/12])[0],
                "fecha_encuesta": datetime.now().strftime("%d/%m/%Y")
            }
            
            encuestas.append(encuesta)
        
        # Convertir a DataFrame
        df = pd.DataFrame(encuestas)
        
        # Guardar los datos
        output_path = os.path.join('data', 'raw', 'encuesta_desarrolladores_simulada.csv')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        logger.info(f"Generadas {num_encuestas} respuestas de encuesta simuladas en {output_path}")
        
        return df
    
    def _generar_descripcion(self, nivel, tecnologias):
        """Generar una descripción para la oferta de trabajo."""
        descripciones_base = [
            "Buscamos un {nivel} desarrollador/a con experiencia en {tecnologias_principales} para unirse a nuestro equipo. Trabajarás en proyectos innovadores utilizando las últimas tecnologías.",
            "¿Te apasiona la tecnología? Únete a nuestro equipo como {nivel} especialista en {tecnologias_principales}. Ofrecemos un ambiente de trabajo dinámico y posibilidades de crecimiento.",
            "Empresa líder en el sector tecnológico busca {nivel} programador/a con conocimientos de {tecnologias_principales} para importante proyecto. Valoramos la proactividad y el trabajo en equipo.",
            "¿Buscas un nuevo desafío profesional? Necesitamos un {nivel} ingeniero/a con experiencia en {tecnologias_principales} para desarrollar soluciones escalables y de alta calidad.",
            "Se precisa {nivel} desarrollador/a con sólidos conocimientos en {tecnologias_principales} para proyecto de transformación digital. Ofrecemos formación continua y buen ambiente laboral."
        ]
        
        descripcion_base = random.choice(descripciones_base)
        tecnologias_principales = ", ".join(tecnologias[:3])
        
        descripcion = descripcion_base.replace("{nivel}", nivel).replace("{tecnologias_principales}", tecnologias_principales)
        
        # Añadir requisitos
        descripcion += "\n\nRequisitos:\n"
        descripcion += f"- Experiencia de {self._nivel_a_experiencia(nivel)} con {tecnologias[0]}\n"
        for tech in tecnologias[1:4]:
            descripcion += f"- Conocimientos de {tech}\n"
        
        # Añadir habilidades blandas
        habilidades = random.sample(self.habilidades_blandas, k=3)
        for skill in habilidades:
            descripcion += f"- {skill}\n"
        
        # Añadir oferta
        descripcion += "\n\nOfrecemos:\n"
        descripcion += "- Contrato estable\n"
        descripcion += "- Horario flexible\n"
        descripcion += "- Posibilidad de trabajar en remoto\n"
        descripcion += "- Formación continua\n"
        descripcion += "- Buen ambiente de trabajo\n"
        
        return descripcion
    
    def _nivel_a_experiencia(self, nivel):
        """Convertir nivel a años de experiencia."""
        experiencia_por_nivel = {
            "Junior": "0-2 años",
            "Semisenior": "2-4 años",
            "Senior": "4-8 años",
            "Lead": "8-12 años",
            "Staff": "10-15 años",
            "Principal": "15+ años"
        }
        return experiencia_por_nivel.get(nivel, "1-3 años")
    
    def _experiencia_a_nivel(self, experiencia):
        """Convertir años de experiencia a nivel."""
        if experiencia < 2:
            return "Junior"
        elif experiencia < 4:
            return "Semisenior"
        elif experiencia < 8:
            return "Senior"
        elif experiencia < 12:
            return "Lead"
        elif experiencia < 15:
            return "Staff"
        else:
            return "Principal"
    
    def _salario_por_nivel(self, nivel):
        """Devolver salario base por nivel."""
        salarios_base = {
            "Junior": 22000,
            "Semisenior": 32000,
            "Senior": 45000,
            "Lead": 60000,
            "Staff": 75000,
            "Principal": 90000
        }
        return salarios_base.get(nivel, 30000)
    
    def _min_experiencia_por_nivel(self, nivel):
        """Devolver experiencia mínima por nivel."""
        min_experiencia = {
            "Junior": 0,
            "Semisenior": 2,
            "Senior": 4,
            "Lead": 8,
            "Staff": 10,
            "Principal": 15
        }
        return min_experiencia.get(nivel, 0)

def generar_datos_simulados(num_ofertas=100, num_encuestas=200):
    """Generar datos simulados de ofertas de empleo y encuestas."""
    generator = DataGenerator()
    
    # Generar ofertas de empleo
    ofertas_df = generator.generar_ofertas_empleo(num_ofertas)
    
    # Generar encuestas
    encuestas_df = generator.generar_encuesta_desarrolladores(num_encuestas)
    
    return ofertas_df, encuestas_df

if __name__ == "__main__":
    generar_datos_simulados()
