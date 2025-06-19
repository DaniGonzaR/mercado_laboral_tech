"""
Módulo para realizar web scraping de portales de empleo.
"""
import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JobScraper:
    """Clase para realizar web scraping de ofertas de empleo."""
    
    def __init__(self, headless=True):
        """Inicializar el scraper con opciones de Chrome."""
        self.options = Options()
        
        # Configuración básica
        if headless:
            self.options.add_argument('--headless=new')
            
        # Configuración para evitar detección
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        # Encabezados para parecer un navegador real
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--disable-infobars')
        self.options.add_argument('--disable-notifications')
        self.options.add_argument('--disable-popup-blocking')
        self.options.add_argument('--disable-web-security')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--start-maximized')
        self.options.add_argument('--window-size=1920,1080')
        
        # User-Agent de un navegador real
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = None
    
    def start_driver(self):
        """Iniciar el navegador controlado por Selenium."""
        logger.info("Iniciando navegador...")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )
        self.driver.maximize_window()
    
    def close_driver(self):
        """Cerrar el navegador."""
        if self.driver:
            logger.info("Cerrando navegador...")
            self.driver.quit()
    
    def scrape_infojobs(self, keyword='desarrollador', location='España', max_pages=3):
        """
        Extraer ofertas de empleo de InfoJobs.
        
        Args:
            keyword (str): Palabra clave para la búsqueda (ej: 'desarrollador', 'data scientist').
            location (str): Ubicación para la búsqueda.
            max_pages (int): Número máximo de páginas a extraer.
            
        Returns:
            pd.DataFrame: DataFrame con las ofertas de empleo.
        """
        self.start_driver()
        base_url = "https://www.infojobs.net"
        search_url = f"{base_url}/ofertas-trabajo/{keyword.replace(' ', '-')}_{location}"
        
        logger.info(f"Iniciando scraping de InfoJobs para: {keyword} en {location}")
        
        all_jobs = []
        
        try:
            # Configurar tiempo de espera
            self.driver.set_page_load_timeout(30)
            self.driver.set_script_timeout(30)
            
            # Navegar a la página inicial
            logger.info("Cargando página inicial...")
            self.driver.get("https://www.infojobs.net")
            time.sleep(random.uniform(2, 4))
            
            # Aceptar cookies si aparece el banner
            self._handle_cookies()
            
            # Navegar a la búsqueda
            logger.info(f"Buscando ofertas de {keyword}...")
            self.driver.get(search_url)
            time.sleep(random.uniform(3, 5))
            
            # Aceptar cookies nuevamente por si aparece después de la navegación
            self._handle_cookies()
            
            for page in range(1, max_pages + 1):
                if page > 1:
                    url = f"{search_url}?page={page}"
                    logger.info(f"Extrayendo página {page}...")
                    self.driver.get(url)
                    time.sleep(random.uniform(3, 5))
                
                # Extraer enlaces a las ofertas
                job_cards = self.driver.find_elements(
                    By.CSS_SELECTOR, "div[data-deal='job'] h2 a"
                )
                
                if not job_cards:
                    logger.warning(f"No se encontraron ofertas en la página {page}")
                    break
                
                logger.info(f"Encontradas {len(job_cards)} ofertas en la página {page}")
                
                # Extraer información de cada oferta (limitado a 10 por página para evitar bloqueos)
                for i, card in enumerate(job_cards[:10], 1):
                    try:
                        job_url = card.get_attribute('href')
                        if job_url:
                            logger.info(f"Procesando oferta {i}/{min(3, len(job_cards))}")
                            job_info = self._scrape_job_details(job_url)
                            if job_info:
                                all_jobs.append(job_info)
                            time.sleep(random.uniform(2, 4))  # Espera aleatoria entre ofertas
                    except Exception as e:
                        logger.error(f"Error al procesar oferta {i}: {str(e)}")
                        continue
                
                logger.info(f"Página {page} procesada. Ofertas recolectadas: {len(all_jobs)}")
                
                # Verificar si hay más páginas
                if not self._has_next_page():
                    logger.info("No hay más páginas disponibles")
                    break
                
                # Espera aleatoria antes de la siguiente página
                time.sleep(random.uniform(3, 6))
        
        except Exception as e:
            logger.error(f"Error durante el scraping: {str(e)}", exc_info=True)
        
        finally:
            self.close_driver()
        
        # Convertir a DataFrame y guardar
        if all_jobs:
            df = pd.DataFrame(all_jobs)
            df['fecha_extraccion'] = pd.Timestamp.now()
            output_path = 'data/raw/ofertas_infojobs.csv'
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Guardar los datos
            df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"Datos guardados exitosamente en {output_path}")
            logger.info(f"Total de ofertas recolectadas: {len(df)}")
            
            # Mostrar un resumen de los datos
            if not df.empty:
                logger.info("\nResumen de las ofertas recolectadas:")
                logger.info(f"- Total de ofertas: {len(df)}")
                if 'empresa' in df.columns:
                    logger.info(f"- Empresas: {df['empresa'].nunique()}")
                if 'ubicacion' in df.columns:
                    logger.info(f"- Ubicaciones: {df['ubicacion'].nunique()}")
        else:
            logger.warning("No se recolectaron ofertas de empleo.")
            df = pd.DataFrame()
        
        return df
    
    def _handle_cookies(self):
        """Manejar el banner de cookies si está presente."""
        try:
            # Intentar diferentes selectores para el botón de aceptar cookies
            selectors = [
                (By.ID, "didomi-notice-agree-button"),
                (By.CSS_SELECTOR, "button#didomi-notice-agree-button"),
                (By.CSS_SELECTOR, "button[aria-label='Aceptar todo']"),
                (By.XPATH, "//button[contains(., 'Aceptar todo')]")
            ]
            
            for by, selector in selectors:
                try:
                    cookie_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    if cookie_button.is_displayed():
                        cookie_button.click()
                        logger.info("Banner de cookies aceptado")
                        time.sleep(1)
                        break
                except:
                    continue
        except Exception as e:
            logger.debug(f"No se pudo manejar el banner de cookies: {str(e)}")
    
    def _has_next_page(self):
        """Verificar si hay una siguiente página disponible."""
        try:
            next_button = self.driver.find_element(
                By.CSS_SELECTOR, "a[data-test='pagination-next']"
            )
            return next_button.is_enabled() and next_button.is_displayed()
        except NoSuchElementException:
            return False
    
    def _scrape_job_details(self, url):
        """Extraer detalles específicos de una oferta de empleo."""
        try:
            self.driver.get(url)
            time.sleep(random.uniform(1, 2))
            
            # Extraer información principal
            job_info = {
                'titulo': self.driver.find_element(By.CSS_SELECTOR, "h1").text.strip(),
                'empresa': self.driver.find_element(By.CSS_SELECTOR, "div[data-test='CompanyName']").text.strip(),
                'ubicacion': self.driver.find_element(By.CSS_SELECTOR, "div[data-test='Location']").text.strip(),
                'fecha_publicacion': self.driver.find_element(By.CSS_SELECTOR, "div[data-test='date']").text.strip(),
                'tipo_contrato': self.driver.find_element(By.CSS_SELECTOR, "div[data-test='ContractType']").text.strip(),
                'jornada': self.driver.find_element(By.CSS_SELECTOR, "div[data-test='WorkDay']").text.strip(),
                'salario': self.driver.find_element(By.CSS_SELECTOR, "div[data-test='Salary']").text.strip(),
                'url': url
            }
            
            # Intentar extraer la descripción
            try:
                job_info['descripcion'] = self.driver.find_element(
                    By.CSS_SELECTOR, "div[data-test='Description']"
                ).text.strip()
            except NoSuchElementException:
                job_info['descripcion'] = ""
            
            # Intentar extraer requisitos
            try:
                job_info['requisitos'] = self.driver.find_element(
                    By.CSS_SELECTOR, "div[data-test='Requirements']"
                ).text.strip()
            except NoSuchElementException:
                job_info['requisitos'] = ""
            
            return job_info
            
        except Exception as e:
            logger.error(f"Error al extraer detalles de {url}: {str(e)}")
            return None

def main():
    """Función principal para ejecutar el scraping."""
    scraper = JobScraper(headless=True)  # Modo sin interfaz para mayor eficiencia
    
    # Palabras clave de búsqueda extendidas
    keywords = [
        'desarrollador', 
        'data scientist', 
        'analista datos', 
        'ingeniero software',
        'devops',
        'frontend developer',
        'backend developer',
        'full stack',
        'machine learning',
        'tech lead',
        'qa',
        'programador',
        'analista programador',
        'cloud engineer',
        'data engineer',
        'ciberseguridad',
        'javascript',
        'python',
        'java',
        'react'
    ]
    
    # Ubicaciones específicas para ampliar la búsqueda
    locations = ['España', 'Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Bilbao', 'Málaga', 'Zaragoza', 'Remoto']
    
    all_jobs = []
    
    try:
        for keyword in keywords:
            for location in locations:
                logger.info(f"Buscando ofertas para: {keyword} en {location}")
                jobs = scraper.scrape_infojobs(keyword=keyword, location=location, max_pages=5)
                if not jobs.empty:
                    all_jobs.append(jobs)
                time.sleep(random.uniform(3, 5))  # Espera entre búsquedas
        
        # Combinar todos los resultados
        if all_jobs:
            final_df = pd.concat(all_jobs, ignore_index=True)
            final_df = final_df.drop_duplicates(subset=['titulo', 'empresa', 'url'])
            
            # Guardar resultados finales
            output_path = 'data/raw/ofertas_tecnologia_consolidadas.csv'
            final_df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"Proceso completado. Total de ofertas únicas: {len(final_df)}")
            logger.info(f"Resultados guardados en: {output_path}")
        
    except Exception as e:
        logger.error(f"Error en el proceso principal: {str(e)}")
    
    finally:
        scraper.close_driver()

if __name__ == "__main__":
    main()
