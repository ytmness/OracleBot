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
    
    def navigate_to_classes(self) -> bool:
        """
        Navega a la página de clases haciendo clic en la tarjeta de materiales del curso
        o navegando directamente a la URL
        
        Returns:
            True si se navegó correctamente, False en caso contrario
        """
        try:
            print("\n" + "="*60)
            print("NAVEGANDO A LA PÁGINA DE CLASES")
            print("="*60)
            
            # Verificar si ya estamos en la página de clases
            current_url = self.driver.current_url
            print(f"URL actual: {current_url}")
            
            if self.selectors.CLASSES_PAGE_PATTERN in current_url:
                print(f"✓ Ya estamos en la página de clases")
                return True
            
            # Método 1: Buscar enlace en la página que apunte a 63000:100
            print("\n[Método 1] Buscando enlace a página de clases en la página actual...")
            try:
                # Buscar todos los enlaces que contengan el patrón 63000:100
                links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '63000:100')]")
                
                if links:
                    print(f"  Encontrados {len(links)} enlaces a página de clases")
                    # Usar el primer enlace encontrado
                    link = links[0]
                    link_url = link.get_attribute('href')
                    print(f"  Enlace encontrado: {link_url}")
                    
                    # Hacer clic en el enlace
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", link)
                    time.sleep(0.5)
                    link.click()
                    time.sleep(5)
                    
                    new_url = self.driver.current_url
                    print(f"  URL después del clic: {new_url}")
                    
                    if self.selectors.CLASSES_PAGE_PATTERN in new_url:
                        print(f"✓ Navegación por enlace exitosa")
                        return True
                else:
                    print("  No se encontraron enlaces con el patrón 63000:100")
            except Exception as e:
                print(f"  ⚠ Error buscando enlaces: {str(e)}")
            
            # Método 2: Intentar navegar directamente a la URL de clases
            print("\n[Método 2] Navegación directa a URL de clases...")
            try:
                print(f"  Navegando a: {self.selectors.CLASSES_PAGE_URL}")
                self.driver.get(self.selectors.CLASSES_PAGE_URL)
                time.sleep(5)  # Esperar más tiempo para que cargue
                
                new_url = self.driver.current_url
                print(f"  URL después de navegación: {new_url}")
                
                # Verificar que cargó correctamente
                if self.selectors.CLASSES_PAGE_PATTERN in new_url:
                    print(f"✓ Navegación directa exitosa")
                    return True
                else:
                    print(f"  ⚠ URL no coincide con el patrón esperado")
            except Exception as e:
                print(f"  ✗ Error en navegación directa: {str(e)}")
                import traceback
                traceback.print_exc()
            
            # Método 3: Usar JavaScript para navegar
            print("\n[Método 3] Navegación mediante JavaScript...")
            try:
                self.driver.execute_script(f"window.location.href = '{self.selectors.CLASSES_PAGE_URL}';")
                time.sleep(5)
                
                new_url = self.driver.current_url
                print(f"  URL después de JavaScript: {new_url}")
                
                if self.selectors.CLASSES_PAGE_PATTERN in new_url:
                    print(f"✓ Navegación por JavaScript exitosa")
                    return True
            except Exception as e:
                print(f"  ⚠ Error en navegación JavaScript: {str(e)}")
            
            # Método 4: Buscar y hacer clic en la tarjeta de "View course materials assigned by a faculty member"
            print("\n[Método 4] Buscando tarjeta de materiales del curso...")
            try:
                # Intentar encontrar el div con el texto específico
                course_materials_card = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, self.selectors.COURSE_MATERIALS_CARD_XPATH))
                )
                
                # Buscar el contenedor padre (t-Card-body) para hacer clic
                card_body = course_materials_card.find_element(By.XPATH, "./ancestor::div[@class='t-Card-body']")
                
                print("✓ Tarjeta de materiales del curso encontrada")
                
                # Scroll al elemento
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", card_body)
                time.sleep(0.5)
                
                # Hacer clic en la tarjeta
                card_body.click()
                
                # Esperar a que cargue la página de clases
                print("Esperando a que cargue la página de clases...")
                time.sleep(3)
                
                # Verificar que estamos en la página de clases
                if self.selectors.CLASSES_PAGE_PATTERN in self.driver.current_url:
                    print(f"✓ Página de clases cargada correctamente - URL: {self.driver.current_url}")
                    return True
                else:
                    # Verificar por elemento
                    try:
                        self.wait.until(
                            EC.presence_of_element_located((By.XPATH, self.selectors.MY_CLASSES_TITLE_XPATH))
                        )
                        print("✓ Página de clases cargada correctamente (verificado por elemento)")
                        return True
                    except:
                        print("⚠ No se pudo verificar la carga de la página de clases")
                        return True  # Continuar de todas formas
                    
            except TimeoutException:
                # Si no se encuentra, intentar buscar cualquier div.t-Card-body clickeable
                try:
                    print("Buscando tarjeta alternativa...")
                    card_bodies = self.driver.find_elements(By.CSS_SELECTOR, self.selectors.COURSE_MATERIALS_CARD)
                    
                    for card in card_bodies:
                        try:
                            desc = card.find_element(By.CSS_SELECTOR, "div.t-Card-desc")
                            if "course materials" in desc.text.lower() or "faculty member" in desc.text.lower():
                                print("✓ Tarjeta encontrada por texto alternativo")
                                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", card)
                                time.sleep(0.5)
                                card.click()
                                time.sleep(3)
                                
                                if self.selectors.CLASSES_PAGE_PATTERN in self.driver.current_url:
                                    print(f"✓ Página de clases cargada - URL: {self.driver.current_url}")
                                    return True
                        except:
                            continue
                    
                    print("⚠ No se encontró la tarjeta de materiales del curso")
                    return False
                except:
                    print("⚠ Error al buscar tarjeta alternativa")
                    return False
                    
        except Exception as e:
            print(f"✗ Error al navegar a clases: {str(e)}")
            return False
    
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
            
            # Primero navegar a la página de clases si no estamos ahí
            if not self.verify_classes_page_loaded():
                print("No estamos en la página de clases, navegando...")
                if not self.navigate_to_classes():
                    print("⚠ No se pudo navegar a la página de clases")
                    return []
            
            # Verificar que la página esté cargada
            self.verify_classes_page_loaded()
            
            # Buscar los items de las clases
            class_items = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.selectors.CARD_VIEW_ITEM))
            )
            
            print(f"Encontradas {len(class_items)} clases")
            
            # Debugging: mostrar estructura HTML del primer item
            if class_items:
                try:
                    first_item_html = class_items[0].get_attribute('outerHTML')
                    print(f"\n[DEBUG] Estructura HTML del primer item (primeros 500 caracteres):")
                    print(first_item_html[:500])
                    print("...")
                except:
                    pass
            
            for index, item in enumerate(class_items, start=1):
                try:
                    print(f"\n  Procesando clase {index}...")
                    
                    # Debugging: mostrar todos los elementos dentro del item
                    try:
                        all_h3 = item.find_elements(By.CSS_SELECTOR, "h3")
                        print(f"    [DEBUG] Encontrados {len(all_h3)} elementos h3:")
                        for i, h3 in enumerate(all_h3):
                            print(f"      h3[{i}]: clase='{h3.get_attribute('class')}', texto='{h3.text[:50]}'")
                    except:
                        pass
                    
                    # Obtener título - intentar múltiples métodos
                    title = ""
                    try:
                        title_elem = item.find_element(By.CSS_SELECTOR, self.selectors.CLASS_TITLE)
                        title = title_elem.text.strip()
                    except:
                        # Método alternativo 1: buscar cualquier h3 dentro del item
                        try:
                            title_elem = item.find_element(By.CSS_SELECTOR, "h3")
                            title = title_elem.text.strip()
                        except:
                            # Método alternativo 2: buscar por XPath
                            try:
                                title_elem = item.find_element(By.XPATH, ".//h3[@class='a-CardView-title']")
                                title = title_elem.text.strip()
                            except:
                                # Método alternativo 3: buscar cualquier texto destacado
                                try:
                                    title_elem = item.find_element(By.XPATH, ".//h3")
                                    title = title_elem.text.strip()
                                except:
                                    # Último recurso: obtener texto del item completo
                                    item_text = item.text.strip()
                                    if item_text:
                                        # Tomar las primeras líneas como título
                                        lines = item_text.split('\n')
                                        title = lines[0] if lines else "Sin título"
                    
                    if not title:
                        print(f"    ⚠ No se pudo obtener título, usando texto del elemento completo")
                        title = item.text.strip()[:50] if item.text else "Sin título"
                    
                    # Obtener subtítulo
                    subtitle = ""
                    try:
                        subtitle_elem = item.find_element(By.CSS_SELECTOR, self.selectors.CLASS_SUBTITLE)
                        subtitle = subtitle_elem.text.strip()
                    except:
                        try:
                            subtitle_elem = item.find_element(By.CSS_SELECTOR, "h4")
                            subtitle = subtitle_elem.text.strip()
                        except:
                            pass
                    
                    # Obtener cuerpo/descripción
                    body = ""
                    try:
                        body_elem = item.find_element(By.CSS_SELECTOR, self.selectors.CLASS_BODY)
                        body = body_elem.text.strip()
                    except:
                        try:
                            body_elem = item.find_element(By.CSS_SELECTOR, "div.a-CardView-mainContent")
                            body = body_elem.text.strip()
                        except:
                            # Intentar obtener cualquier div con contenido
                            try:
                                body_elems = item.find_elements(By.CSS_SELECTOR, "div")
                                for div in body_elems:
                                    div_text = div.text.strip()
                                    if div_text and len(div_text) > 20:  # Texto sustancial
                                        body = div_text
                                        break
                            except:
                                pass
                    
                    # Buscar el botón "Take Class" para verificar que es una clase válida
                    take_class_button = None
                    try:
                        take_class_button = item.find_element(
                            By.XPATH, 
                            ".//a[@class='a-CardView-button t-Button--hot']//span[contains(text(), 'Take Class')]"
                        )
                    except:
                        # Intentar método alternativo
                        try:
                            take_class_button = item.find_element(
                                By.CSS_SELECTOR,
                                "a.a-CardView-button"
                            )
                        except:
                            pass
                    
                    if not take_class_button:
                        print(f"    ⚠ No se encontró botón 'Take Class' en esta clase, puede que no sea una clase válida")
                    
                    class_info = ClassInfo(index, title, subtitle, body, item)
                    classes.append(class_info)
                    print(f"  ✓ {class_info}")
                    
                except Exception as e:
                    print(f"  ⚠ Error al procesar clase {index}: {str(e)}")
                    # Mostrar información de debugging
                    try:
                        print(f"    HTML del item: {item.get_attribute('outerHTML')[:200]}...")
                    except:
                        pass
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

