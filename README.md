# Análisis del Mercado Laboral Tecnológico Español

Este proyecto analiza las tendencias actuales del mercado laboral en el sector tecnológico español, utilizando datos REALES obtenidos de APIs públicas y fuentes web. El proyecto proporciona insights valiosos sobre demanda de habilidades, niveles salariales y tendencias del mercado laboral tecnológico en España con visualizaciones interactivas y un dashboard completo.

## Preguntas de Investigación

1. **¿Qué tecnologías tienen mayor demanda en el mercado laboral actual?** 
   - Análisis de las habilidades técnicas más solicitadas en ofertas de empleo

2. **¿Cómo se relaciona la experiencia con el salario en trabajos tecnológicos?**
   - Correlación entre años de experiencia y compensación económica

3. **¿Existen diferencias significativas en salarios según las tecnologías dominadas?**
   - Comparación de salarios entre profesionales con distintas especializaciones técnicas

4. **¿Qué tipo de desarrolladores tienen mayor satisfacción laboral?**
   - Análisis de factores que influyen en la satisfacción de los profesionales tecnológicos

5. **¿Cómo varía la distribución salarial según ubicación y tipo de empleo?**
   - Análisis geográfico y por modalidad de contratación de las ofertas salariales

## Estructura del Proyecto

```
mercado_laboral_tech/
│
├── data/               # Archivos de datos
│   ├── raw/            # Datos sin procesar
│   └── processed/      # Datos procesados
│
├── notebooks/          # Jupyter notebooks de análisis
│
├── dashboards/         # Archivos para visualizaciones interactivas
│
├── src/                # Código fuente del proyecto
│   ├── etl.py          # Scripts para extracción y transformación de datos
│   ├── eda.py          # Análisis exploratorio de datos
│   └── stats.py        # Análisis estadístico
│
├── img/                # Visualizaciones generadas
│
├── main.py             # Script principal para ejecutar el pipeline completo
├── requirements.txt    # Dependencias del proyecto
├── .gitignore          # Archivos a ignorar en git
└── README.md           # Documentación del proyecto
```

## Fuentes de Datos

El proyecto prioriza datos REALES del mercado laboral tecnológico obtenidos de:

1. **APIs públicas**: Integración con APIs como Remotive para obtener ofertas de trabajo reales
2. **Stack Overflow Jobs Feed**: Datos de empleos tecnológicos
3. **Datos complementarios**: Generación de datos estructurados solo cuando es estrictamente necesario

## Instalación y Uso

### Requisitos

- Python 3.8+
- Conexión a Internet (para recopilar datos REALES)
- Librerías para análisis de datos y visualización

### Instalación

1. Clona el repositorio:
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd mercado_laboral_tech
   ```

2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

### Uso

#### Recopilación de Datos REALES

```bash
# Recolectar datos REALES del mercado laboral tecnológico
python main.py --real-data
```

#### Pipeline Completo

```bash
python main.py --all
```

#### Dashboard Interactivo

```bash
streamlit run dashboards/app.py
```

#### Componentes Individuales

```bash
# Recolectar datos REALES
python main.py --real-data

# Solo proceso ETL
python main.py --etl

# Solo Análisis Exploratorio
python main.py --eda

# Ejecutar notebook de análisis
jupyter notebook notebooks/exploratory_analysis.ipynb
```

#### Parámetros Importantes

- `--real-data`: Prioriza la obtención de datos REALES de APIs
- `--force-mock=False`: Evita el uso de datos simulados aunque no haya APIs disponibles
- `--output-dir`: Directorio de salida para los resultados (por defecto: `data/processed/`)

## Estructura del Proyecto

```
mercado_laboral_tech/
├── data/               # Archivos de datos
│   ├── raw/            # Datos sin procesar (incluye datos de web scraping)
│   └── processed/      # Datos procesados
│   └── external/       # Datos externos
│
├── notebooks/         # Jupyter notebooks de análisis
│
├── reports/           # Reportes generados
│
├── src/               # Código fuente del proyecto
│   ├── __init__.py
│   ├── scraper.py     # Módulo de web scraping
│   ├── etl.py         # Scripts para extracción y transformación de datos
│   ├── eda.py         # Análisis exploratorio de datos
│   └── stats.py       # Análisis estadístico
│
├── img/              # Visualizaciones generadas
│   ├── eda/          # Gráficos EDA
│   └── stats/        # Gráficos estadísticos
│
├── main.py            # Script principal para ejecutar el pipeline
├── requirements.txt    # Dependencias del proyecto
├── .gitignore         # Archivos a ignorar en git
└── README.md          # Documentación del proyecto
```

## Configuración

El archivo `config.py` contiene las configuraciones del proyecto, incluyendo:

- Rutas de archivos
- Parámetros de web scraping
- Configuración de visualizaciones

### Datasets Integrados

1. **Ofertas de empleo tecnológicas REALES**: Datos obtenidos de APIs públicas que incluyen:
   - Título del trabajo
   - Empresa contratante
   - Ubicación
   - Tipo de contrato y jornada
   - Rango salarial
   - Tecnologías requeridas
   - Fecha de publicación
   - URL de la oferta original

*Nota: Este proyecto utiliza datos REALES del mercado laboral tecnológico español, obtenidos directamente de fuentes online.*

## Metodología

### ETL (Extracción, Transformación y Carga)

1. **Extracción**: Obtención de datos REALES de APIs públicas y fuentes web abiertas.
2. **Transformación**: Normalización de campos, estandarización de valores, manejo de valores faltantes y enriquecimiento de datos.
3. **Carga**: Almacenamiento en formato CSV para optimizar el análisis posterior.

### Análisis Exploratorio (EDA)

1. **Distribución geográfica**: Análisis de ofertas por ubicación en España
2. **Análisis salarial**: Distribución y estadísticas de salarios en tecnología
3. **Tecnologías más demandadas**: Ranking de tecnologías solicitadas en el mercado
4. **Tipos de contratación**: Análisis de modalidades de contrato y jornada
5. **Empresas líderes**: Identificación de mayores empleadores tecnológicos

### Análisis Estadístico

1. **Estadística descriptiva**:
   - Medidas de tendencia central y dispersión para salarios
   - Estadísticas por grupos (tipo de trabajo, ubicación, educación)

2. **Estadística inferencial**:
   - Correlaciones entre experiencia y salario
   - Pruebas t para comparar salarios entre tecnologías
   - Regresión lineal para predicción salarial

## Resultados Clave

### Hallazgos Principales

1. **Tecnologías más demandadas**: Identificación de las habilidades técnicas con mayor demanda en el mercado español

2. **Distribución salarial**: Análisis detallado de rangos salariales en el sector tecnológico español

3. **Concentración geográfica**: Mapeo de las regiones con mayor número de ofertas tecnológicas

4. **Modalidades de contratación**: Identificación de tendencias en tipos de contrato y jornada laboral

5. **Principales empleadores**: Análisis de las empresas con mayor número de vacantes tecnológicas

Todos los resultados pueden explorarse interactivamente en el dashboard y consultarse en los notebooks de análisis disponibles en el directorio `notebooks/`.

## Dashboard Interactivo

Se ha creado un dashboard interactivo con Streamlit que permite explorar visualmente los datos REALES del mercado laboral tecnológico español. El dashboard incluye:

- **Indicador de datos REALES**: Muestra claramente cuando se trabaja con datos obtenidos de APIs
- **Métricas clave del mercado**: Número de ofertas, promedio salarial, tecnologías identificadas
- **Visualizaciones interactivas**:
  - Distribución geográfica de las ofertas
  - Tecnologías más demandadas
  - Análisis salarial con estadísticas detalladas
  - Distribución por tipo de contrato
- **Filtros interactivos** por ubicación, tipo de contrato y tecnología

Para ejecutar el dashboard:
```bash
streamlit run dashboards/app.py
```

## Replicación y Entrega del Proyecto

### Para replicar el proyecto

1. Clona el repositorio y sigue las instrucciones de instalación
2. Ejecuta el pipeline completo con `python main.py --all`
3. Explora los datos con el dashboard: `streamlit run dashboards/app.py`

### Para la entrega del proyecto

1. Verifica que los datos REALES estén correctamente procesados
2. Comprueba que todas las visualizaciones funcionen adecuadamente
3. Asegúrate de que el dashboard muestre correctamente los datos
4. Comprime el proyecto completo para su entrega

1. **Clonar el repositorio**:
   ```
   git clone https://github.com/DaniGonzaR/mercado_laboral_tech.git
   cd mercado_laboral_tech
   ```

2. **Instalar dependencias**:
   ```
   pip install -r requirements.txt
   ```

3. **Ejecutar el pipeline completo**:
   ```
   python main.py
   ```

4. **Explorar los notebooks** (opcional):
   ```
   jupyter notebook notebooks/
   ```

5. **Abrir el dashboard** en Streamlit utilizando el archivo en el directorio `dashboards/app.py`.

## Limitaciones y Trabajo Futuro

- Los datos utilizados son simulados y limitados en escala. Un análisis con datos reales proporcionaría insights más precisos.
- Sería valioso ampliar el análisis para incluir tendencias temporales y predicciones futuras.
- Se podría mejorar el modelo integrando datos adicionales como tamaño de empresa, industria específica o beneficios no salariales.

## Autor

Daniel González Rodríguez

## Licencia

Este proyecto está bajo la Licencia MIT.
