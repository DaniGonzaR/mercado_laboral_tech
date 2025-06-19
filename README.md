# 📊 Análisis del Mercado Laboral Tecnológico Español

Proyecto de análisis basado en **datos REALES** del mercado laboral tecnológico en todo el mundo. Incluye insights sobre demanda de tecnologías, rangos salariales, satisfacción laboral y tendencias de contratación, mediante un dashboard interactivo y análisis estadísticos avanzados.

---

## 🔍 Preguntas de Investigación

1. **¿Qué tecnologías son actualmente las más demandadas en el mercado global?**
   A partir de más de 400 ofertas reales, se identifican las stacks y herramientas más solicitadas, como R, API, AI, Go y Python.
2. **¿Cómo se distribuyen los salarios en empleos tecnológicos en función de la ubicación?**
   Análisis comparativo entre países y regiones (España, USA, Europa, etc.) respecto a ofertas y rangos salariales.
3. **¿Qué impacto tienen las tecnologías dominadas en la predicción salarial?**
   Evaluación de cómo ciertas herramientas elevan o reducen el salario esperado según el modelo de IA integrado en el dashboard.
4. **¿Qué tipo de contrato predomina en las ofertas tecnológicas actuales?**
   Estudio de modalidades laborales (jornada completa, autónomo, prácticas, etc.) y su relación con la oferta y el salario.
5. **¿Qué patrones emergen en los perfiles técnicos más demandados?**
   Identificación de los roles con mayor presencia (como Python Developer, Software Engineer, QA Tester) y sus características comunes.

---

## 🗂️ Estructura del Proyecto

```
mercado_laboral_tech/
├── dashboards/
│   └── app.py                         # Dashboard interactivo (Streamlit)
│
├── data/
│   ├── external/                      # Datos externos (encuestas, feeds)
│   │   └── stack-overflow-survey-results-2023.csv
│   ├── processed/                     # Datos ya transformados y listos para análisis
│   │   ├── jobs_processed.csv
│   │   └── survey_processed.csv
│   └── raw/                           # Datos crudos sin procesar
│       ├── ofertas_tech_reales_*.csv
│       └── stackoverflow_survey_raw.csv
│
├── img/                               # Visualizaciones generadas
│
├── logs/
│   └── job_analysis.log               # Registro del análisis de ejecución
│
├── models/
│   └── salary_model.joblib           # Modelo de predicción salarial entrenado
│
├── notebooks/
│   └── exploratory_analysis.ipynb    # Análisis exploratorio (EDA)
│
├── reports/                           # (Opcional) Reportes generados automáticamente
│
├── src/                               # Código fuente
│   ├── data_collector.py              # Recolección desde APIs
│   ├── data_generator.py              # Generación de datos sintéticos (si se requiere)
│   ├── eda.py                         # Análisis exploratorio de datos
│   ├── etl.py                         # Extracción, transformación y carga de datos
│   ├── model_salary.py                # Lógica del modelo predictivo
│   ├── scraper.py                     # Web scraping (opcional)
│   └── stats.py                       # Análisis estadístico
│
├── .env                               # Variables de entorno
├── .gitignore                         # Archivos ignorados por Git
├── job_analysis.log                   # Log principal del pipeline
├── main.py                            # Script principal del proyecto
├── README.md                          # Documentación
└── requirements.txt                   # Dependencias
```

mercado_laboral_tech/
├── data/               # Datos brutos, procesados y externos
├── notebooks/          # Notebooks de análisis exploratorio
├── dashboards/         # Dashboard interactivo (Streamlit)
├── reports/            # Reportes y resultados generados
├── src/                # Código fuente del proyecto
│   ├── etl.py          # Extracción y transformación de datos
│   ├── eda.py          # Análisis exploratorio
│   ├── model_salary.py # Modelo de predicción salarial
│   ├── scraper.py      # Scraping de datos web
│   └── stats.py        # Análisis estadístico
├── models/             # Modelos entrenados (.joblib)
├── img/                # Visualizaciones generadas (EDA, stats)
├── config.py           # Configuraciones del proyecto
├── main.py             # Script principal para el pipeline completo
├── requirements.txt    # Dependencias del entorno
└── README.md           # Documentación del proyecto
```

---

## 📡 Fuentes de Datos Reales

- **APIs públicas**: [Remotive](https://remotive.io), [Adzuna](https://developer.adzuna.com/), [Jooble](https://jooble.org/api/about)
- **Stack Overflow Jobs Feed** (archivado, como referencia histórica)
- **Datos estructurados generados solo si es necesario**

---

## ⚙️ Instalación y Uso

### 🔧 Requisitos
- Python ≥ 3.8  
- Conexión a Internet (para obtener datos reales)  
- Librerías: `pandas`, `scikit-learn`, `matplotlib`, `streamlit`, etc.

### 🛠️ Instalación

```bash
git clone https://github.com/DaniGonzaR/mercado_laboral_tech.git
cd mercado_laboral_tech
python -m venv venv
source venv/bin/activate  # (Windows: .\venv\Scripts\activate)
pip install -r requirements.txt
```

### 🚀 Uso

#### Pipeline completo:
```bash
python main.py --all
```

#### Ejecutar dashboard interactivo:
```bash
streamlit run dashboards/app.py
```

#### Ejecución personalizada:
```bash
python main.py --datos-reales --all    # Datos reales vía API
python main.py --etl                   # Solo ETL
python main.py --eda                   # Solo análisis exploratorio
jupyter notebook notebooks/            # Abrir notebooks
```

#### Parámetros clave:
- `--real-data`: Fuerza la descarga de datos reales desde APIs
- `--force-mock=False`: Evita el uso de datos simulados
- `--output-dir`: Ruta de salida (por defecto: `data/processed/`)

---

## 📈 Metodología

### 🔄 ETL (Extracción, Transformación y Carga)
- Obtención desde APIs/web
- Limpieza, estandarización y enriquecimiento
- Exportación en CSV para análisis reproducible

### 🧪 EDA (Análisis Exploratorio)
- Distribución geográfica
- Niveles salariales
- Tecnologías más demandadas
- Modalidades de contrato
- Principales empleadores

### 📊 Análisis Estadístico
- **Descriptivo**: medias, desviaciones, histogramas
- **Inferencial**: regresión lineal, correlaciones, pruebas t

### 🤖 Predicción Salarial
Modelo de Gradient Boosting entrenado con datos reales:
- Predice salarios en función de experiencia, ubicación, tecnologías
- Integra visualmente en el dashboard

---

## 📊 Dashboard Interactivo (Streamlit)

- 📌 Indicador de **datos reales** activos
- 📍 Filtros por ubicación, tecnología, modalidad
- 📈 Visualizaciones dinámicas:
  - Mapa geográfico de empleos
  - Ranking de tecnologías más demandadas
  - Estadísticas salariales detalladas

Ejecuta con:
```bash
streamlit run dashboards/app.py
```

---

## 📌 Resultados Clave

- 🔝 **Tecnologías más demandadas**: Python, JavaScript, AWS, SQL, Docker
- 💰 **Distribución salarial**: Rango amplio según seniority y stack
- 🗺️ **Zonas con más ofertas**: Madrid, Barcelona, Valencia
- 🤝 **Modalidad preferida**: Contrato indefinido, jornada completa
- 🏢 **Empresas líderes**: Multinacionales y startups tecnológicas

---

## 📦 Replicación y Entrega

1. Clona el repositorio
2. Ejecuta `python main.py --all`
3. Visualiza los resultados con el dashboard
4. Verifica visualizaciones, datos y predicciones
5. Comprime y entrega la carpeta del proyecto

---

## 🧩 Limitaciones y Futuro

- Los datos disponibles pueden no cubrir todo el mercado (limitaciones por API)
- Ampliar con series temporales para análisis predictivos
- Incluir variables como beneficios, tipo de empresa o tamaño del equipo

---

## 👤 Autor

**Daniel González Rodríguez**  
[GitHub](https://github.com/DaniGonzaR)

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia MIT.