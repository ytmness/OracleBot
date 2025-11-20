"""
Manejador de clases para Oracle Academy
"""
import time
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.selectors import Selectors


class ClassInfo:
    """Información de una clase"""
    def __init__(self, index: int, title: str, subtitle: str, body: str, element):
        self.index = index
        self.title = title
        self.subtitle = subtitle
        self.body = body
        self.element = element  # WebElement del card
    
    def __str__(self):
        return f"{self.index}. {self.title}\n   {self.subtitle}\n   {self.body[:100]}..."


class SectionInfo:
    """Información de una sección"""
    def __init__(self, index: int, title: str, element, is_complete: bool = False):
        self.index = index
        self.title = title
        self.element = element  # WebElement del enlace
        self.is_complete = is_complete
    
    def __str__(self):
        status = "✓ Completada" if self.is_complete else "○ Pendiente"
        return f"{self.index}. {self.title} [{status}]"


class ClassHandler:
    """Clase para manejar clases y secciones en Oracle Academy"""
    
    def __init__(self, driver: webdriver.Chrome):
        """
        Inicializa el manejador de clases
        
        Args:
            driver: Instancia del WebDriver de Selenium
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.selectors = Selectors()
    
    def verify_classes_page_loaded(self) -> bool:
        """
        Verifica que la página de clases esté cargada
        
        Returns:
            True si la página está cargada, False en caso contrario
        """
        try:
            my_classes = self.wait.until(
                EC.presence_of_element_located((By.XPATH, self.selectors.MY_CLASSES_TITLE_XPATH))
            )
            print("✓ Página de clases cargada correctamente")
            return True
        except TimeoutException:
            print("⚠ No se pudo verificar que la página de clases esté cargada")
            return False
    
    def get_available_classes(self) -> List[ClassInfo]:
        """
        Obtiene la lista de clases disponibles
        
        Returns:
            Lista de objetos ClassInfo con la información de cada clase
        """
        classes = []
        
        try:
            print("\nBuscando clases disponibles...")
            
            # Verificar que la página esté cargada
            self.verify_classes_page_loaded()
            
            # Buscar los items de las clases
            class_items = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.selectors.CARD_VIEW_ITEM))
            )
            
            print(f"Encontradas {len(class_items)} clases")
            
            for index, item in enumerate(class_items, start=1):
                try:
                    # Obtener título
                    title_elem = item.find_element(By.CSS_SELECTOR, self.selectors.CLASS_TITLE)
                    title = title_elem.text.strip()
                    
                    # Obtener subtítulo
                    try:
                        subtitle_elem = item.find_element(By.CSS_SELECTOR, self.selectors.CLASS_SUBTITLE)
                        subtitle = subtitle_elem.text.strip()
                    except:
                        subtitle = ""
                    
                    # Obtener cuerpo/descripción
                    try:
                        body_elem = item.find_element(By.CSS_SELECTOR, self.selectors.CLASS_BODY)
                        body = body_elem.text.strip()
                    except:
                        body = ""
                    
                    class_info = ClassInfo(index, title, subtitle, body, item)
                    classes.append(class_info)
                    print(f"  {class_info}")
                    
                except Exception as e:
                    print(f"  ⚠ Error al procesar clase {index}: {str(e)}")
                    continue
            
            return classes
            
        except TimeoutException:
            print("✗ No se encontraron clases disponibles")
            return []
        except Exception as e:
            print(f"✗ Error al obtener clases: {str(e)}")
            return []
    
    def select_class(self, class_info: ClassInfo) -> bool:
        """
        Selecciona una clase haciendo clic en el botón "Take Class"
        
        Args:
            class_info: Objeto ClassInfo de la clase a seleccionar
            
        Returns:
            True si se seleccionó correctamente, False en caso contrario
        """
        try:
            print(f"\nSeleccionando clase: {class_info.title}")
            
            # Buscar el botón "Take Class" dentro del card de la clase
            take_class_button = class_info.element.find_element(
                By.XPATH, 
                ".//a[@class='a-CardView-button t-Button--hot']//span[contains(text(), 'Take Class')]"
            )
            
            # Scroll al botón
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", take_class_button)
            time.sleep(0.5)
            
            # Hacer clic
            take_class_button.click()
            
            # Esperar a que cargue la página de la clase
            print("Esperando a que cargue la página de la clase...")
            time.sleep(3)
            
            # Verificar que estamos en la página de la clase (buscar secciones)
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors.SECTION_ITEM))
                )
                print("✓ Página de la clase cargada correctamente")
                return True
            except:
                print("⚠ No se pudo verificar la carga de la página de la clase")
                return True  # Continuar de todas formas
            
        except NoSuchElementException:
            print(f"✗ No se encontró el botón 'Take Class' para la clase {class_info.title}")
            return False
        except Exception as e:
            print(f"✗ Error al seleccionar la clase: {str(e)}")
            return False
    
    def get_sections(self) -> List[SectionInfo]:
        """
        Obtiene la lista de secciones de la clase actual
        
        Returns:
            Lista de objetos SectionInfo con la información de cada sección
        """
        sections = []
        
        try:
            print("\nBuscando secciones de la clase...")
            
            # Buscar los items de las secciones
            section_items = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.selectors.SECTION_ITEM))
            )
            
            print(f"Encontradas {len(section_items)} secciones")
            
            for index, item in enumerate(section_items, start=1):
                try:
                    # Obtener título de la sección
                    title_elem = item.find_element(By.CSS_SELECTOR, self.selectors.SECTION_TITLE)
                    title = title_elem.text.strip()
                    
                    # Verificar si está completada (buscar indicador 100% o clase is-complete)
                    is_complete = False
                    try:
                        # Buscar en el elemento padre si tiene clase is-complete
                        parent = item.find_element(By.XPATH, "./..")
                        if "is-complete" in parent.get_attribute("class"):
                            is_complete = True
                    except:
                        pass
                    
                    section_info = SectionInfo(index, title, item, is_complete)
                    sections.append(section_info)
                    print(f"  {section_info}")
                    
                except Exception as e:
                    print(f"  ⚠ Error al procesar sección {index}: {str(e)}")
                    continue
            
            return sections
            
        except TimeoutException:
            print("✗ No se encontraron secciones")
            return []
        except Exception as e:
            print(f"✗ Error al obtener secciones: {str(e)}")
            return []
    
    def select_section(self, section_info: SectionInfo) -> bool:
        """
        Selecciona una sección haciendo clic en ella
        
        Args:
            section_info: Objeto SectionInfo de la sección a seleccionar
            
        Returns:
            True si se seleccionó correctamente, False en caso contrario
        """
        try:
            print(f"\nSeleccionando sección: {section_info.title}")
            
            # Scroll al elemento
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", section_info.element)
            time.sleep(0.5)
            
            # Hacer clic
            section_info.element.click()
            
            # Esperar a que cargue la página de la sección
            print("Esperando a que cargue la página de la sección...")
            time.sleep(3)
            
            print("✓ Sección seleccionada correctamente")
            return True
            
        except Exception as e:
            print(f"✗ Error al seleccionar la sección: {str(e)}")
            return False
    
    def complete_section(self, max_quizzes: int = 1) -> bool:
        """
        Completa una sección navegando por los módulos y completando quizzes
        
        Args:
            max_quizzes: Número máximo de quizzes a completar (por defecto 1)
            
        Returns:
            True si se completó correctamente, False en caso contrario
        """
        try:
            print(f"\nCompletando sección (máximo {max_quizzes} quiz/quizzes)...")
            
            quizzes_completed = 0
            max_attempts = 20  # Límite de intentos para evitar loops infinitos
            attempts = 0
            
            # Buscar el mapa de progreso (Wizard Steps)
            try:
                wizard_steps = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors.WIZARD_STEPS))
                )
                print("✓ Mapa de progreso encontrado")
            except:
                print("⚠ No se encontró mapa de progreso, continuando...")
            
            # Buscar botón "Save and Continue" para avanzar por los módulos
            while quizzes_completed < max_quizzes and attempts < max_attempts:
                attempts += 1
                
                try:
                    # Buscar botón "Save and Continue" con timeout corto
                    from selenium.webdriver.support.ui import WebDriverWait as WDWait
                    quick_wait = WDWait(self.driver, 2)
                    
                    save_continue_button = quick_wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors.SAVE_AND_CONTINUE_BUTTON))
                    )
                    
                    print(f"  [{attempts}] Encontrado botón 'Save and Continue', avanzando...")
                    save_continue_button.click()
                    time.sleep(2)
                    
                except TimeoutException:
                    # Si no hay más "Save and Continue", buscar quiz
                    print("  No hay más módulos con 'Save and Continue', buscando quiz...")
                    break
            
            # Buscar y hacer clic en "Take an Assessment"
            try:
                take_assessment_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors.TAKE_ASSESSMENT_BUTTON))
                )
                
                print("  Encontrado botón 'Take an Assessment'")
                take_assessment_button.click()
                time.sleep(2)
                
                # Guardar progreso del quiz
                try:
                    save_progress_button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors.SAVE_PROGRESS_BUTTON))
                    )
                    print("  Guardando progreso del quiz...")
                    save_progress_button.click()
                    time.sleep(1)
                    quizzes_completed += 1
                    print(f"  ✓ Quiz {quizzes_completed} completado")
                except:
                    print("  ⚠ No se encontró botón 'Save Progress'")
                
            except TimeoutException:
                print("  ⚠ No se encontró botón 'Take an Assessment'")
            
            print(f"✓ Sección procesada ({quizzes_completed} quiz/quizzes completados)")
            return True
            
        except Exception as e:
            print(f"✗ Error al completar la sección: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def go_back_to_sections(self) -> bool:
        """
        Navega de vuelta a la lista de secciones
        
        Returns:
            True si se navegó correctamente, False en caso contrario
        """
        try:
            print("\nNavegando de vuelta a la lista de secciones...")
            
            # Intentar usar el botón de retroceso del navegador
            self.driver.back()
            time.sleep(2)
            
            # Verificar que estamos en la página de secciones
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors.SECTION_ITEM))
                )
                print("✓ Regresado a la lista de secciones")
                return True
            except:
                print("⚠ No se pudo verificar que estamos en la lista de secciones")
                return True  # Continuar de todas formas
            
        except Exception as e:
            print(f"⚠ Error al navegar de vuelta: {str(e)}")
            return False

