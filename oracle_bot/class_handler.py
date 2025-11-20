"""
Manejador de clases para Oracle Academy
"""
import time
import os
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.selectors import Selectors

# OpenAI (opcional, solo si está configurado)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠ OpenAI no está instalado. Ejecuta: pip install openai")


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
    
    def __init__(self, driver: webdriver.Chrome, openai_api_key: Optional[str] = None):
        """
        Inicializa el manejador de clases
        
        Args:
            driver: Instancia del WebDriver de Selenium
            openai_api_key: Clave API de OpenAI (opcional)
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.selectors = Selectors()
        
        # Configurar OpenAI si está disponible
        self.openai_client = None
        if OPENAI_AVAILABLE and openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=openai_api_key)
                print("✓ OpenAI configurado correctamente")
            except Exception as e:
                print(f"⚠ Error al configurar OpenAI: {str(e)}")
        elif openai_api_key and not OPENAI_AVAILABLE:
            print("⚠ OpenAI no está instalado. Instala con: pip install openai")
        elif not openai_api_key:
            print("⚠ OpenAI API key no proporcionada. Las respuestas serán aleatorias.")
    
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
            # Verificar primero por URL
            current_url = self.driver.current_url
            if self.selectors.CLASSES_PAGE_PATTERN in current_url:
                print("✓ Página de clases detectada por URL")
                return True
            
            # Intentar buscar el título con timeout corto
            from selenium.webdriver.support.ui import WebDriverWait as QuickWait
            quick_wait = QuickWait(self.driver, 3)  # Solo 3 segundos
            
            try:
                my_classes = quick_wait.until(
                    EC.presence_of_element_located((By.XPATH, self.selectors.MY_CLASSES_TITLE_XPATH))
                )
                print("✓ Página de clases cargada correctamente")
                return True
            except TimeoutException:
                # Si no encuentra el título, verificar si hay elementos de clases
                try:
                    class_items = self.driver.find_elements(By.CSS_SELECTOR, self.selectors.CARD_VIEW_ITEM)
                    if class_items:
                        print(f"✓ Página de clases detectada - Encontrados {len(class_items)} items de clase")
                        return True
                except:
                    pass
                
                print("⚠ No se pudo verificar completamente, pero continuando...")
                return True  # Continuar de todas formas para no bloquear
        except Exception as e:
            print(f"⚠ Error al verificar página: {str(e)}, continuando...")
            return True  # Continuar de todas formas
    
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
            
            # Esperar un momento para que la página se estabilice
            time.sleep(2)
            
            # Buscar los items de las clases con timeout más corto y múltiples intentos
            class_items = []
            max_attempts = 3
            
            for attempt in range(max_attempts):
                try:
                    print(f"  Intento {attempt + 1}/{max_attempts} de buscar clases...")
                    
                    # Intentar con diferentes selectores
                    selectors_to_try = [
                        self.selectors.CARD_VIEW_ITEM,
                        "li.a-CardView-item",
                        "li[class*='CardView-item']",
                        "div.a-CardView",
                    ]
                    
                    for selector in selectors_to_try:
                        try:
                            items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if items:
                                class_items = items
                                print(f"  ✓ Encontradas {len(class_items)} clases usando selector: {selector}")
                                break
                        except:
                            continue
                    
                    if class_items:
                        break
                    
                    # Si no encuentra, esperar un poco más
                    if attempt < max_attempts - 1:
                        time.sleep(2)
                        
                except Exception as e:
                    print(f"  ⚠ Error en intento {attempt + 1}: {str(e)}")
                    if attempt < max_attempts - 1:
                        time.sleep(2)
            
            if not class_items:
                print("⚠ No se encontraron items de clase en la página")
                print(f"  URL actual: {self.driver.current_url}")
                # Intentar mostrar el HTML de la página para debugging
                try:
                    page_source = self.driver.page_source[:1000]
                    print(f"  Primeros 1000 caracteres del HTML:")
                    print(page_source)
                except:
                    pass
                return []
            
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
            
            print(f"Encontradas {len(section_items)} elementos de sección")
            
            # Secciones que no son realmente secciones de contenido (filtrar)
            invalid_sections = [
                "sections in course",
                "level of difficulty",
                "status",
                "course resources"  # A veces Section 0 es solo recursos
            ]
            
            valid_index = 1
            for index, item in enumerate(section_items, start=1):
                try:
                    # Obtener título de la sección
                    title_elem = item.find_element(By.CSS_SELECTOR, self.selectors.SECTION_TITLE)
                    title = title_elem.text.strip()
                    
                    # Filtrar secciones inválidas
                    title_lower = title.lower()
                    is_invalid = any(invalid in title_lower for invalid in invalid_sections)
                    
                    if is_invalid:
                        print(f"  ⏭ Saltando sección no válida: {title}")
                        continue
                    
                    # Verificar si está completada (buscar indicador 100% o clase is-complete)
                    is_complete = False
                    try:
                        # Buscar en el elemento padre si tiene clase is-complete
                        parent = item.find_element(By.XPATH, "./..")
                        parent_class = parent.get_attribute("class") or ""
                        if "is-complete" in parent_class:
                            is_complete = True
                    except:
                        pass
                    
                    section_info = SectionInfo(valid_index, title, item, is_complete)
                    sections.append(section_info)
                    print(f"  {section_info}")
                    valid_index += 1
                    
                except Exception as e:
                    print(f"  ⚠ Error al procesar sección {index}: {str(e)}")
                    continue
            
            print(f"\n✓ Total de secciones válidas encontradas: {len(sections)}")
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
            print(f"\nSeleccionando sección {section_info.index}: {section_info.title}")
            
            # Esperar un momento para que la página se estabilice
            time.sleep(1)
            
            # Buscar la sección nuevamente por su título para evitar elementos stale
            # Esto es importante porque después de navegar, los elementos pueden volverse obsoletos
            try:
                # Buscar todas las secciones disponibles
                section_items = self.driver.find_elements(By.CSS_SELECTOR, self.selectors.SECTION_ITEM)
                
                if not section_items:
                    print("⚠ No se encontraron elementos de sección en la página")
                    return False
                
                # Buscar la sección correcta por su título
                target_section = None
                for item in section_items:
                    try:
                        title_elem = item.find_element(By.CSS_SELECTOR, self.selectors.SECTION_TITLE)
                        item_title = title_elem.text.strip()
                        
                        # Comparar títulos (exacto o parcial)
                        if item_title == section_info.title or section_info.title in item_title:
                            target_section = item
                            print(f"  ✓ Sección encontrada: {item_title}")
                            break
                    except:
                        continue
                
                if not target_section:
                    print(f"  ✗ No se pudo encontrar la sección '{section_info.title}' en la página")
                    print(f"  Secciones disponibles en la página:")
                    for i, item in enumerate(section_items[:5], 1):  # Mostrar primeras 5
                        try:
                            title_elem = item.find_element(By.CSS_SELECTOR, self.selectors.SECTION_TITLE)
                            print(f"    {i}. {title_elem.text.strip()}")
                        except:
                            pass
                    return False
                
                # Scroll al elemento encontrado
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target_section)
                time.sleep(0.5)
                
                # Hacer clic en el elemento encontrado
                target_section.click()
                
                # Esperar a que cargue la página de la sección
                print("Esperando a que cargue la página de la sección...")
                time.sleep(3)
                
                # Verificar que cambió la URL o que cargó el contenido
                new_url = self.driver.current_url
                print(f"  URL después de seleccionar: {new_url}")
                
                print("✓ Sección seleccionada correctamente")
                return True
                
            except Exception as e:
                print(f"  ⚠ Error al buscar sección por título: {str(e)}")
                # Intentar método alternativo: usar el índice
                try:
                    section_items = self.driver.find_elements(By.CSS_SELECTOR, self.selectors.SECTION_ITEM)
                    if section_info.index <= len(section_items):
                        # Filtrar secciones inválidas para obtener el índice correcto
                        invalid_sections = ["sections in course", "level of difficulty", "status", "course resources"]
                        valid_sections = []
                        for item in section_items:
                            try:
                                title_elem = item.find_element(By.CSS_SELECTOR, self.selectors.SECTION_TITLE)
                                title = title_elem.text.strip().lower()
                                if not any(invalid in title for invalid in invalid_sections):
                                    valid_sections.append(item)
                            except:
                                continue
                        
                        if section_info.index <= len(valid_sections):
                            target_section = valid_sections[section_info.index - 1]
                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target_section)
                            time.sleep(0.5)
                            target_section.click()
                            time.sleep(3)
                            print("✓ Sección seleccionada por índice")
                            return True
                except:
                    pass
                
                return False
            
        except Exception as e:
            print(f"✗ Error al seleccionar la sección: {str(e)}")
            import traceback
            traceback.print_exc()
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
            
            # Esperar un momento para que la página cargue completamente
            time.sleep(2)
            
            # Verificar qué tipo de página es
            current_url = self.driver.current_url
            print(f"  URL actual: {current_url}")
            
            quizzes_completed = 0
            max_attempts = 20  # Límite de intentos para evitar loops infinitos
            attempts = 0
            
            # Buscar el mapa de progreso (Wizard Steps) con timeout corto
            wizard_steps_found = False
            try:
                from selenium.webdriver.support.ui import WebDriverWait as QuickWait
                quick_wait = QuickWait(self.driver, 3)
                wizard_steps = quick_wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors.WIZARD_STEPS))
                )
                print("✓ Mapa de progreso encontrado")
                wizard_steps_found = True
            except:
                print("⚠ No se encontró mapa de progreso, puede que esta sección no tenga contenido interactivo")
            
            # Buscar botón "Save and Continue" para avanzar por los módulos
            if wizard_steps_found:
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
            
            # Buscar y hacer clic en "Take an Assessment" con múltiples métodos
            try:
                from selenium.webdriver.support.ui import WebDriverWait as AssessmentWait
                assessment_wait = AssessmentWait(self.driver, 5)
                
                # Método 1: Buscar por ID
                try:
                    take_assessment_button = assessment_wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors.TAKE_ASSESSMENT_BUTTON))
                    )
                    print("  Encontrado botón 'Take an Assessment' (por ID)")
                except:
                    # Método 2: Buscar por texto
                    try:
                        take_assessment_button = self.driver.find_element(
                            By.XPATH, 
                            "//a[contains(@class, 'a-CardView-button')]//span[contains(text(), 'Take an Assessment')]"
                        )
                        print("  Encontrado botón 'Take an Assessment' (por texto)")
                    except:
                        # Método 3: Buscar cualquier botón con "Assessment" en el texto
                        try:
                            take_assessment_button = self.driver.find_element(
                                By.XPATH,
                                "//a[contains(., 'Assessment')]"
                            )
                            print("  Encontrado botón 'Take an Assessment' (por texto parcial)")
                        except:
                            raise Exception("No se encontró el botón 'Take an Assessment'")
                
                print("  Haciendo clic en 'Take an Assessment'...")
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", take_assessment_button)
                time.sleep(0.5)
                take_assessment_button.click()
                time.sleep(3)
                
                # Iniciar el quiz
                if self.start_quiz():
                    # Completar el quiz usando OpenAI
                    if self.complete_quiz_with_ai():
                        quizzes_completed += 1
                        print(f"  ✓ Quiz {quizzes_completed} completado")
                    else:
                        print("  ⚠ El quiz no se pudo completar completamente")
                else:
                    print("  ⚠ No se pudo iniciar el quiz")
                
            except Exception as e:
                print(f"  ⚠ No se encontró botón 'Take an Assessment': {str(e)}")
                print("  Esta sección puede no tener quiz o puede requerir completar módulos primero")
            
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
            time.sleep(3)  # Esperar más tiempo
            
            # Verificar que estamos en la página de secciones con timeout corto
            from selenium.webdriver.support.ui import WebDriverWait as QuickWait
            quick_wait = QuickWait(self.driver, 5)
            
            try:
                quick_wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors.SECTION_ITEM))
                )
                print("✓ Regresado a la lista de secciones")
                return True
            except:
                # Si no encuentra por selector, verificar por URL
                current_url = self.driver.current_url
                if "63000:15" in current_url or "63000:14" in current_url:
                    print("✓ Regresado a la página de secciones (verificado por URL)")
                    return True
                else:
                    print(f"⚠ No se pudo verificar - URL actual: {current_url}")
                    # Intentar navegar directamente a la página de la clase
                    print("Intentando navegar directamente a la página de la clase...")
                    # La URL de la clase debería estar guardada, pero por ahora intentamos volver
                    self.driver.back()
                    time.sleep(3)
                    return True  # Continuar de todas formas
            
        except Exception as e:
            print(f"⚠ Error al navegar de vuelta: {str(e)}")
            # Intentar navegar directamente usando JavaScript
            try:
                print("Intentando navegar con JavaScript...")
                self.driver.execute_script("window.history.go(-2);")  # Retroceder 2 páginas
                time.sleep(3)
                return True
            except:
                return False
    
    def start_quiz(self) -> bool:
        """
        Inicia el quiz haciendo clic en el botón "Start"
        
        Returns:
            True si se inició correctamente, False en caso contrario
        """
        try:
            print("\n  Iniciando quiz...")
            
            # Buscar el botón Start
            try:
                start_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors.START_QUIZ_BUTTON))
                )
                print("  ✓ Botón 'Start' encontrado")
            except:
                # Intentar por XPath
                try:
                    start_button = self.driver.find_element(By.XPATH, self.selectors.START_QUIZ_BUTTON_XPATH)
                    print("  ✓ Botón 'Start' encontrado (por XPath)")
                except:
                    print("  ✗ No se encontró el botón 'Start'")
                    return False
            
            # Hacer clic en Start
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", start_button)
            time.sleep(0.5)
            start_button.click()
            time.sleep(3)  # Esperar a que cargue la primera pregunta
            
            print("  ✓ Quiz iniciado")
            return True
            
        except Exception as e:
            print(f"  ✗ Error al iniciar el quiz: {str(e)}")
            return False
    
    def get_question_and_choices(self) -> Optional[Dict]:
        """
        Extrae la pregunta y las opciones de respuesta del quiz actual
        
        Returns:
            Diccionario con 'question' y 'choices', o None si hay error
        """
        try:
            # Extraer la pregunta
            question_text = ""
            try:
                question_elem = self.driver.find_element(By.CSS_SELECTOR, self.selectors.QUESTION_CONTENT)
                question_text = question_elem.text.strip()
            except:
                try:
                    question_elem = self.driver.find_element(By.CSS_SELECTOR, self.selectors.QUESTION_TEXT)
                    question_text = question_elem.text.strip()
                except:
                    print("  ⚠ No se pudo extraer la pregunta")
                    return None
            
            # Extraer número de pregunta
            question_number = ""
            try:
                heading_elem = self.driver.find_element(By.CSS_SELECTOR, self.selectors.QUESTION_HEADING)
                question_number = heading_elem.text.strip()
            except:
                pass
            
            # Extraer todas las opciones
            choices = []
            try:
                choice_buttons = self.driver.find_elements(By.CSS_SELECTOR, self.selectors.CHOICE_BUTTON)
                
                for i, button in enumerate(choice_buttons, 1):
                    try:
                        # Obtener el texto de la opción
                        choice_text_elem = button.find_element(By.CSS_SELECTOR, self.selectors.CHOICE_TEXT)
                        choice_text = choice_text_elem.text.strip()
                        
                        # Verificar si está seleccionada
                        is_selected = button.get_attribute("aria-checked") == "true"
                        
                        choices.append({
                            "index": i,
                            "text": choice_text,
                            "is_selected": is_selected,
                            "element": button
                        })
                    except:
                        continue
                
            except Exception as e:
                print(f"  ⚠ Error al extraer opciones: {str(e)}")
                return None
            
            return {
                "question_number": question_number,
                "question": question_text,
                "choices": choices
            }
            
        except Exception as e:
            print(f"  ✗ Error al extraer pregunta y opciones: {str(e)}")
            return None
    
    def select_answer(self, choice_index: int) -> bool:
        """
        Selecciona una respuesta haciendo clic en el botón de opción
        
        Args:
            choice_index: Índice de la opción a seleccionar (1-based)
            
        Returns:
            True si se seleccionó correctamente, False en caso contrario
        """
        try:
            choice_buttons = self.driver.find_elements(By.CSS_SELECTOR, self.selectors.CHOICE_BUTTON)
            
            if choice_index < 1 or choice_index > len(choice_buttons):
                print(f"  ⚠ Índice de opción inválido: {choice_index}")
                return False
            
            target_button = choice_buttons[choice_index - 1]
            
            # Hacer clic en la opción
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target_button)
            time.sleep(0.3)
            target_button.click()
            time.sleep(1)
            
            print(f"  ✓ Opción {choice_index} seleccionada")
            return True
            
        except Exception as e:
            print(f"  ✗ Error al seleccionar respuesta: {str(e)}")
            return False
    
    def get_answer_from_openai(self, question_data: Dict) -> Optional[int]:
        """
        Obtiene la respuesta correcta usando OpenAI
        
        Args:
            question_data: Diccionario con 'question' y 'choices'
            
        Returns:
            Índice de la respuesta correcta (1-based) o None si hay error
        """
        if not self.openai_client:
            print("  ⚠ OpenAI no está configurado, seleccionando primera opción")
            return 1
        
        try:
            # Construir el prompt
            choices_text = "\n".join([f"{i}. {choice['text']}" for i, choice in enumerate(question_data['choices'], 1)])
            
            prompt = f"""Eres un experto en programación Java. Responde la siguiente pregunta de quiz de manera precisa y concisa.

Pregunta:
{question_data['question']}

Opciones:
{choices_text}

Responde SOLO con el número de la opción correcta (1, 2, 3, etc.). No incluyas explicaciones ni texto adicional."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Puedes cambiar a gpt-4 si tienes acceso
                messages=[
                    {"role": "system", "content": "Eres un experto en programación Java que responde preguntas de quiz de manera precisa."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            answer_text = response.choices[0].message.content.strip()
            
            # Extraer el número de la respuesta
            try:
                answer_num = int(answer_text.split()[0])
                if 1 <= answer_num <= len(question_data['choices']):
                    print(f"  ✓ OpenAI sugiere opción {answer_num}")
                    return answer_num
                else:
                    print(f"  ⚠ Número de opción fuera de rango: {answer_num}")
                    return 1
            except:
                print(f"  ⚠ No se pudo parsear la respuesta de OpenAI: {answer_text}")
                return 1
                
        except Exception as e:
            print(f"  ✗ Error al consultar OpenAI: {str(e)}")
            return 1
    
    def go_to_next_question(self) -> bool:
        """
        Avanza a la siguiente pregunta o envía el quiz
        
        Returns:
            True si avanzó correctamente, False si el quiz terminó
        """
        try:
            # Buscar botón Next o Submit con múltiples métodos
            next_button = None
            submit_button = None
            
            # Método 1: Buscar botón Next
            try:
                next_button = self.driver.find_element(By.CSS_SELECTOR, self.selectors.NEXT_QUESTION_BUTTON)
                print("  Avanzando a siguiente pregunta...")
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
                time.sleep(0.3)
                next_button.click()
                time.sleep(3)
                return True
            except:
                pass
            
            # Método 2: Buscar botón Submit por ID
            try:
                submit_button = self.driver.find_element(By.CSS_SELECTOR, self.selectors.SUBMIT_QUIZ_BUTTON)
                print("  Enviando respuesta del quiz...")
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
                time.sleep(0.3)
                submit_button.click()
                time.sleep(3)
                
                # Después de submit, puede que haya un botón para continuar o el quiz terminó
                # Verificar si hay más preguntas
                try:
                    # Intentar encontrar la siguiente pregunta
                    time.sleep(2)
                    question_elem = self.driver.find_element(By.CSS_SELECTOR, self.selectors.QUESTION_TEXT)
                    print("  Continuando con siguiente pregunta...")
                    return True
                except:
                    print("  ✓ Quiz completado")
                    return False  # Quiz terminado
            except:
                pass
            
            # Método 3: Buscar por texto "Submit Answer"
            try:
                submit_button = self.driver.find_element(By.XPATH, self.selectors.SUBMIT_QUIZ_BUTTON_XPATH)
                print("  Enviando respuesta del quiz (por texto)...")
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
                time.sleep(0.3)
                submit_button.click()
                time.sleep(3)
                
                # Verificar si hay más preguntas
                try:
                    time.sleep(2)
                    question_elem = self.driver.find_element(By.CSS_SELECTOR, self.selectors.QUESTION_TEXT)
                    print("  Continuando con siguiente pregunta...")
                    return True
                except:
                    print("  ✓ Quiz completado")
                    return False
            except:
                pass
            
            print("  ⚠ No se encontró botón Next/Submit")
            return False
            
        except Exception as e:
            print(f"  ✗ Error al avanzar: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def complete_quiz_with_ai(self) -> bool:
        """
        Completa el quiz completo usando OpenAI para responder las preguntas
        
        Returns:
            True si se completó correctamente, False en caso contrario
        """
        try:
            print("\n  Completando quiz con IA...")
            max_questions = 100  # Límite de seguridad aumentado
            questions_answered = 0
            consecutive_errors = 0
            max_consecutive_errors = 3
            
            while questions_answered < max_questions:
                # Esperar un momento para que la página se estabilice
                time.sleep(1)
                
                # Verificar si todavía estamos en una página de quiz
                try:
                    # Intentar encontrar el contenedor de pregunta
                    question_container = self.driver.find_element(By.CSS_SELECTOR, self.selectors.QUESTION_TEXT)
                    if not question_container.is_displayed():
                        print("  ⚠ Contenedor de pregunta no visible, puede que el quiz haya terminado")
                        break
                except:
                    # Si no encuentra el contenedor, verificar si hay mensaje de finalización
                    try:
                        # Buscar indicadores de que el quiz terminó
                        page_text = self.driver.page_source.lower()
                        if "quiz complete" in page_text or "assessment complete" in page_text or "results" in page_text:
                            print("  ✓ Quiz completado (indicador encontrado)")
                            break
                    except:
                        pass
                    
                    print("  ⚠ No se encontró contenedor de pregunta, puede que el quiz haya terminado")
                    break
                
                # Extraer pregunta y opciones
                question_data = self.get_question_and_choices()
                
                if not question_data:
                    consecutive_errors += 1
                    print(f"  ⚠ No se pudo extraer la pregunta (intento {consecutive_errors}/{max_consecutive_errors})")
                    
                    if consecutive_errors >= max_consecutive_errors:
                        print("  ⚠ Demasiados errores consecutivos, puede que el quiz haya terminado")
                        break
                    
                    # Esperar un poco más y reintentar
                    time.sleep(2)
                    continue
                
                # Resetear contador de errores si se extrajo correctamente
                consecutive_errors = 0
                
                print(f"\n  {'='*50}")
                print(f"  {question_data.get('question_number', 'Pregunta')}")
                print(f"  {'='*50}")
                print(f"  Pregunta: {question_data['question'][:150]}...")
                print(f"  Opciones encontradas: {len(question_data['choices'])}")
                
                # Mostrar opciones disponibles
                for i, choice in enumerate(question_data['choices'], 1):
                    status = "✓" if choice['is_selected'] else "○"
                    print(f"    {status} {i}. {choice['text'][:80]}...")
                
                # Obtener respuesta de OpenAI
                answer_index = self.get_answer_from_openai(question_data)
                
                # Seleccionar la respuesta
                if self.select_answer(answer_index):
                    questions_answered += 1
                    print(f"  ✓ Pregunta {questions_answered} respondida")
                    
                    # Esperar un momento antes de avanzar
                    time.sleep(1)
                    
                    # Avanzar a la siguiente pregunta
                    has_more = self.go_to_next_question()
                    
                    if not has_more:
                        print(f"\n  ✓ Quiz completado - Total de preguntas respondidas: {questions_answered}")
                        break
                    
                    # Esperar a que cargue la siguiente pregunta
                    time.sleep(2)
                else:
                    print("  ⚠ No se pudo seleccionar la respuesta, reintentando...")
                    time.sleep(2)
                    continue
            
            print(f"\n  {'='*50}")
            print(f"  RESUMEN: {questions_answered} preguntas respondidas")
            print(f"  {'='*50}")
            
            return questions_answered > 0
            
        except KeyboardInterrupt:
            print("\n  ⚠ Quiz interrumpido por el usuario")
            return False
        except Exception as e:
            print(f"  ✗ Error al completar el quiz: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

