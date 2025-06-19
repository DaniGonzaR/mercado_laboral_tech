# 📊 Análisis del Mercado Laboral Tecnológico Mundial

Proyecto de análisis basado en **datos HÍBRIDOS** del mercado laboral tecnológico mundial. Incluye insights sobre demanda de tecnologías, rangos salariales, y tendencias de contratación, mediante un dashboard interactivo y un modelo de predicción de salarios basado en machine learning.

---

## 🔍 Preguntas de Investigación

1. **¿Qué tecnologías son actualmente las más demandadas en el mercado global?**
   A partir de más de 3300 ofertas híbridas, se identifican las tecnologías más solicitadas, como Python, JavaScript, React, Java y tecnologías cloud.
2. **¿Cómo se distribuyen los salarios en empleos tecnológicos en el mundo?**
   Análisis de rangos salariales por ubicación (Madrid, Barcelona, Valencia, etc.) y nivel de experiencia.
3. **¿Qué impacto tienen las tecnologías en la predicción salarial?**
   Evaluación mediante un modelo de machine learning integrado en el dashboard que identifica las tecnologías con mayor impacto en el salario.
4. **¿Qué tipo de contrato predomina en las ofertas tecnológicas en el mundo?**
   Estudio de modalidades laborales (indefinido, temporal, remoto, híbrido) y su relación con la oferta y el salario.
5. **¿Cuál es la distribución geográfica de las ofertas tecnológicas en el mundo?**
   Análisis de la concentración de ofertas por ciudades y regiones.

---

## 💻 Estructura del Proyecto

```
mercado_laboral_tech/
├── data/               # Datos brutos, procesados y externos
│   ├── processed/       # Datos procesados listos para análisis
│   │   ├── jobs_processed.csv       # Ofertas de empleo procesadas (3305 registros)
│   │   └── technology_job_counts.csv # Conteo de tecnologías
│   └── raw/            # Datos crudos sin procesar
├── dashboards/         # Dashboard interactivo (Streamlit)
│   └── app.py          # Aplicación principal del dashboard
├── src/                # Código fuente del proyecto
│   ├── model_salary.py  # Modelo de predicción salarial
│   ├── generate_spain_data.py # Generación de datos para España
│   ├── fix_real_salaries.py # Corrección de salarios para datos reales
│   ├── update_job_metadata.py # Actualización de metadatos de ofertas
│   └── update_locations.py # Actualización de ubicaciones para datos simulados
├── models/             # Modelos entrenados (.joblib)
├── logs/               # Archivos de registro
├── ejecutar_pipeline.py # Script unificado para ejecutar todo el flujo
├── requirements.txt    # Dependencias del entorno
└── README.md           # Documentación del proyecto

---

## 💻 Fuëntes de Datos

- **Datos híbridos**: Combinación de datos reales y simulados para el mercado mundial
- **APIs de empleo**: [Adzuna](https://developer.adzuna.com/) y [Jooble](https://jooble.org/api/about)
- **Datos simulados**: Generados para complementar y enriquecer el análisis con ofertas relevantes para el mundo

---

## ⚙️ Instalación y Uso

### Estado Actual del Proyecto

El proyecto se encuentra en su estado final, con las siguientes funcionalidades implementadas:

- **Dashboard interactivo**: Visualización de más de 3300 ofertas de empleo tecnológico en el mundo
- **Datos híbridos**: Combinación de datos reales de Adzuna y Jooble con datos simulados de alta calidad
- **Predicción de salarios**: Modelo de machine learning entrenado que predice salarios basado en ubicación, tecnologías y tipo de contrato
- **Análisis de tendencias**: Visualización de tecnologías más demandadas, distribución geográfica y tipos de contrato predominantes
- **ETL optimizado**: Pipeline de datos que procesa y combina múltiples fuentes en un formato unificado

### 🔧 Requisitos
- Python ≥ 3.8  
- Pandas, Scikit-learn, Streamlit, Matplotlib, Seaborn
- Conexión a Internet (opcional, solo para recolectar datos nuevos)

### 💻 Ejecución

1. **Instalación de dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecutar el pipeline completo con script unificado:**
   ```bash
   python ejecutar_pipeline.py --todo
   ```

3. **Ejecutar solo el dashboard:**
   ```bash
   python ejecutar_pipeline.py --dashboard
   # o directamente:
   streamlit run dashboards/app.py
   ```

### 🌟 Características Principales

- **Visualización interactiva**: Dashboard completo con filtros, gráficos dinámicos y tabla de datos detallados
- **Predicción de salarios**: Modelo de machine learning entrenado con métricas de rendimiento (MAE, R²)
- **Análisis de tecnologías**: Identificación y conteo de tecnologías mencionadas en ofertas de empleo
- **Datos geolocalizados**: Análisis por ubicación mundial para identificar tendencias regionales
- **Estadísticas de contratos**: Análisis por tipo de contrato y modalidad de trabajo

### 🚀 Uso del Script Unificado

El proyecto incluye un script unificado (`ejecutar_pipeline.py`) que facilita la ejecución de todo el flujo de trabajo:

#### Pipeline completo (ETL + entrenamiento + dashboard):
```bash
python ejecutar_pipeline.py --todo
```

#### Solo pipeline ETL:
```bash
python ejecutar_pipeline.py --etl
```

#### Ejecutar dashboard interactivo:
```bash
python ejecutar_pipeline.py --dashboard
```

#### Analizar datos procesados:
```bash
python ejecutar_pipeline.py --analizar
```

#### Ejecutar pasos individuales:
```bash
python ejecutar_pipeline.py --generar-datos        # Generar datos simulados
python ejecutar_pipeline.py --corregir-salarios     # Corregir salarios
python ejecutar_pipeline.py --actualizar-metadatos  # Actualizar metadatos
python ejecutar_pipeline.py --actualizar-ubicaciones # Actualizar ubicaciones
python ejecutar_pipeline.py --entrenar-modelo       # Entrenar modelo
```

#### Parámetros adicionales:
- `--puerto`: Especifica el puerto para el dashboard (por defecto: 8501)

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

## 📊 Resultados y Conclusiones

El análisis del mercado laboral tecnológico español revela importantes hallazgos:

- La demanda de profesionales tecnológicos continúa en aumento, especialmente en Madrid, Barcelona y Valencia
- Las tecnologías más solicitadas incluyen Python, JavaScript, Java, tecnologías cloud y frameworks modernos
- El modelo de predicción salarial alcanza un rendimiento aceptable con métricas que indican capacidad adecuada para estimar salarios
- Existe una predominancia del trabajo remoto e híbrido frente al presencial tradicional
- La combinación de datos reales (Adzuna, Jooble) e híbridos ha permitido un análisis más completo y representativo del mercado laboral español

## 💪 Estado Final del Proyecto

El proyecto ha alcanzado su estado final con todas las funcionalidades implementadas:

- Dashboard interactivo completamente funcional con más de 3300 ofertas de empleo
- Datos híbridos (combinación de Adzuna, Jooble y simulados) procesados y estructurados correctamente
- Todas las ofertas simuladas de España tienen ubicación correctamente asignada como "Spain"
- No hay datos con fuente "API Real" (reemplazados por Adzuna/Jooble)
- Todos los registros tienen salarios válidos y asignados
- Modelo de predicción salarial entrenado y listo para usar en el dashboard
- Visualizaciones dinámicas de tendencias tecnológicas actualizadas
- Script unificado `ejecutar_pipeline.py` que facilita la ejecución de todo el flujo de trabajo
- Sistema de filtrado por ubicación, tecnologías y tipo de contrato

---

## 💾 Replicación y Entrega

1. Clona el repositorio
2. Ejecuta `python ejecutar_pipeline.py --todo`
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