"""
Manejador de clases para Oracle Academy
"""
import time
import os
import re
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
                    
                    # Verificar si está completada (buscar múltiples indicadores)
                    is_complete = False
                    
                    # Método 1: Buscar indicador "100%" en el texto del elemento o sus hijos
                    try:
                        item_text = item.text.lower()
                        if "100%" in item_text:
                            is_complete = True
                    except:
                        pass
                    
                    # Método 2: Buscar badge de completado (div con 100%)
                    if not is_complete:
                        try:
                            # Buscar en el elemento y sus hijos cualquier div con "100%"
                            badge_elements = item.find_elements(By.XPATH, ".//div[contains(text(), '100%')]")
                            if badge_elements:
                                is_complete = True
                        except:
                            pass
                    
                    # Método 3: Buscar clase "is-complete" en el elemento padre
                    if not is_complete:
                        try:
                            parent = item.find_element(By.XPATH, "./..")
                            parent_class = parent.get_attribute("class") or ""
                            if "is-complete" in parent_class.lower():
                                is_complete = True
                        except:
                            pass
                    
                    # Método 4: Buscar badge o indicador visual de completado
                    if not is_complete:
                        try:
                            # Buscar badge con clase que indique completado
                            badges = item.find_elements(By.CSS_SELECTOR, "span.t-MediaList-badge, div.t-MediaList-badgeWrap")
                            for badge in badges:
                                badge_text = badge.text.strip().lower()
                                badge_class = badge.get_attribute("class") or ""
                                if "100%" in badge_text or "complete" in badge_class.lower():
                                    is_complete = True
                                    break
                        except:
                            pass
                    
                    # Método 5: Buscar en el elemento mismo si tiene clase de completado
                    if not is_complete:
                        try:
                            item_class = item.get_attribute("class") or ""
                            if "complete" in item_class.lower() and "incomplete" not in item_class.lower():
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
            
            # Buscar todas las secciones disponibles y filtrar las inválidas
            section_items = self.driver.find_elements(By.CSS_SELECTOR, self.selectors.SECTION_ITEM)
            
            if not section_items:
                print("⚠ No se encontraron elementos de sección en la página")
                return False
            
            # Filtrar secciones inválidas para obtener solo las válidas
            invalid_sections = ["sections in course", "level of difficulty", "status", "course resources"]
            valid_sections = []
            valid_titles = []
            
            for item in section_items:
                try:
                    title_elem = item.find_element(By.CSS_SELECTOR, self.selectors.SECTION_TITLE)
                    title = title_elem.text.strip()
                    title_lower = title.lower()
                    
                    # Verificar si es una sección inválida
                    is_invalid = any(invalid in title_lower for invalid in invalid_sections)
                    
                    if not is_invalid:
                        valid_sections.append(item)
                        valid_titles.append(title)
                except:
                    continue
            
            print(f"  📋 Secciones válidas encontradas: {len(valid_sections)}")
            for idx, title in enumerate(valid_titles, 1):
                marker = ">>>" if idx == section_info.index else "   "
                print(f"    {marker} {idx}. {title}")
            
            # Verificar que el índice es válido
            if section_info.index < 1 or section_info.index > len(valid_sections):
                print(f"  ✗ Índice {section_info.index} fuera de rango (rango válido: 1-{len(valid_sections)})")
                return False
            
            # Usar el índice válido para seleccionar la sección correcta
            target_section = valid_sections[section_info.index - 1]
            target_title = valid_titles[section_info.index - 1]
            
            print(f"  ✓ Seleccionando sección {section_info.index}: {target_title}")
            
            # Scroll al elemento encontrado
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target_section)
            time.sleep(0.5)
            
            # Verificar que el título coincide (doble verificación)
            try:
                title_elem = target_section.find_element(By.CSS_SELECTOR, self.selectors.SECTION_TITLE)
                actual_title = title_elem.text.strip()
                if actual_title != target_title:
                    print(f"  ⚠ Advertencia: Título esperado '{target_title}' pero encontrado '{actual_title}'")
            except:
                pass
            
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
            
            # Buscar y hacer clic en "Take an Assessment" o "Finish Assessment"
            try:
                from selenium.webdriver.support.ui import WebDriverWait as AssessmentWait
                assessment_wait = AssessmentWait(self.driver, 5)
                
                assessment_button = None
                is_finish_assessment = False
                
                # Primero verificar si el assessment ya está empezado (Finish Assessment)
                try:
                    finish_button = self.driver.find_element(
                        By.XPATH,
                        self.selectors.FINISH_ASSESSMENT_BUTTON_XPATH
                    )
                    assessment_button = finish_button
                    is_finish_assessment = True
                    print("  ✓ Encontrado botón 'Finish Assessment' - El assessment ya está en progreso")
                except:
                    # Si no encuentra "Finish", buscar "Take an Assessment"
                    # Método 1: Buscar por ID
                    try:
                        assessment_button = assessment_wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors.TAKE_ASSESSMENT_BUTTON))
                        )
                        # Verificar el texto del botón
                        button_text = assessment_button.find_element(By.CSS_SELECTOR, "span.a-CardView-buttonLabel").text.strip()
                        if "Finish" in button_text:
                            is_finish_assessment = True
                            print("  ✓ Encontrado botón 'Finish Assessment' (por ID)")
                        else:
                            print("  ✓ Encontrado botón 'Take an Assessment' (por ID)")
                    except:
                        # Método 2: Buscar por texto "Take an Assessment"
                        try:
                            assessment_button = self.driver.find_element(
                                By.XPATH, 
                                self.selectors.TAKE_ASSESSMENT_BUTTON_XPATH
                            )
                            print("  ✓ Encontrado botón 'Take an Assessment' (por texto)")
                        except:
                            # Método 3: Buscar cualquier botón con "Assessment" en el texto
                            try:
                                assessment_button = self.driver.find_element(
                                    By.XPATH,
                                    "//a[@id='open_assess_id']"
                                )
                                # Verificar el texto
                                button_text_elem = assessment_button.find_element(By.CSS_SELECTOR, "span.a-CardView-buttonLabel")
                                button_text = button_text_elem.text.strip()
                                if "Finish" in button_text:
                                    is_finish_assessment = True
                                    print("  ✓ Encontrado botón 'Finish Assessment' (por texto parcial)")
                                else:
                                    print("  ✓ Encontrado botón 'Take an Assessment' (por texto parcial)")
                            except:
                                raise Exception("No se encontró el botón de Assessment")
                
                if not assessment_button:
                    raise Exception("No se pudo encontrar el botón de Assessment")
                
                # Hacer clic en el botón
                button_action = "Finish Assessment" if is_finish_assessment else "Take an Assessment"
                print(f"  Haciendo clic en '{button_action}'...")
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", assessment_button)
                time.sleep(0.5)
                assessment_button.click()
                time.sleep(3)
                
                # Si es "Finish Assessment", continuar desde donde quedó
                # Si es "Take an Assessment", iniciar nuevo quiz
                if is_finish_assessment:
                    print("  Continuando assessment en progreso...")
                    # Completar el quiz usando OpenAI (continuará desde donde quedó)
                    if self.complete_quiz_with_ai():
                        quizzes_completed += 1
                        print(f"  ✓ Assessment completado")
                    else:
                        print("  ⚠ El assessment no se pudo completar completamente")
                else:
                    # Iniciar el quiz nuevo
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
            # Intentar navegar directamente usando JavaScript1
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
            Diccionario con 'question', 'choices', y 'allows_multiple', o None si hay error
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
            
            # Detectar si permite múltiples respuestas
            allows_multiple = False
            try:
                # Buscar el contenedor de opciones para verificar el tipo
                choice_container = self.driver.find_element(By.CSS_SELECTOR, "div.choice-Container")
                parent = choice_container.find_element(By.XPATH, "./ancestor::div[contains(@id, 'Choices')]")
                
                # Verificar si dice "multiple" o "checkbox" en algún lugar
                container_text = parent.get_attribute("aria-label") or ""
                page_text = self.driver.page_source.lower()
                
                if "multiple" in container_text.lower() or "checkbox" in page_text or "select all" in page_text:
                    allows_multiple = True
                    print("  ℹ Detectado: Permite múltiples respuestas")
            except:
                # Por defecto, asumir que es de una sola respuesta (radio buttons)
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
                        
                        # Verificar el tipo de respuesta (radio vs checkbox)
                        response_type = button.get_attribute("data-response-type") or "1"
                        role = button.get_attribute("role") or ""
                        
                        choices.append({
                            "index": i,
                            "text": choice_text,
                            "is_selected": is_selected,
                            "element": button,
                            "response_type": response_type,
                            "role": role
                        })
                    except:
                        continue
                
            except Exception as e:
                print(f"  ⚠ Error al extraer opciones: {str(e)}")
                return None
            
            return {
                "question_number": question_number,
                "question": question_text,
                "choices": choices,
                "allows_multiple": allows_multiple
            }
            
        except Exception as e:
            print(f"  ✗ Error al extraer pregunta y opciones: {str(e)}")
            return None
    
    def select_answer(self, choice_index: int, allow_multiple: bool = False) -> bool:
        """
        Selecciona una respuesta haciendo clic en el botón de opción
        
        Args:
            choice_index: Índice de la opción a seleccionar (1-based)
            allow_multiple: Si es True, permite seleccionar múltiples opciones
            
        Returns:
            True si se seleccionó correctamente, False en caso contrario
        """
        try:
            # Primero, quitar cualquier overlay que pueda estar bloqueando
            try:
                overlays = self.driver.find_elements(By.CSS_SELECTOR, "div.ui-widget-overlay")
                for overlay in overlays:
                    is_visible = self.driver.execute_script(
                        "return arguments[0].offsetParent !== null && "
                        "window.getComputedStyle(arguments[0]).display !== 'none';",
                        overlay
                    )
                    if is_visible:
                        print("  🔧 Detectado overlay bloqueando, removiéndolo...")
                        self.driver.execute_script("arguments[0].style.display = 'none';", overlay)
                        time.sleep(0.5)
            except:
                pass
            
            choice_buttons = self.driver.find_elements(By.CSS_SELECTOR, self.selectors.CHOICE_BUTTON)
            
            if choice_index < 1 or choice_index > len(choice_buttons):
                print(f"  ⚠ Índice de opción inválido: {choice_index}")
                return False
            
            # Re-encontrar el botón para evitar elementos stale
            choice_buttons = self.driver.find_elements(By.CSS_SELECTOR, self.selectors.CHOICE_BUTTON)
            target_button = choice_buttons[choice_index - 1]
            
            # Verificar si ya está seleccionada (solo para múltiples)
            if allow_multiple:
                is_already_selected = target_button.get_attribute("aria-checked") == "true"
                if is_already_selected:
                    print(f"  ℹ Opción {choice_index} ya está seleccionada")
                    return True
            
            # Hacer scroll y esperar
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target_button)
            time.sleep(0.5)
            
            # Intentar hacer clic con múltiples métodos
            try:
                target_button.click()
            except Exception as e1:
                print(f"  ⚠ Clic normal falló: {str(e1)[:100]}, intentando con JavaScript...")
                try:
                    # Quitar overlay nuevamente si aparece
                    self.driver.execute_script("""
                        var overlays = document.querySelectorAll('div.ui-widget-overlay');
                        overlays.forEach(function(overlay) {
                            overlay.style.display = 'none';
                        });
                    """)
                    time.sleep(0.3)
                    self.driver.execute_script("arguments[0].click();", target_button)
                except Exception as e2:
                    print(f"  ⚠ Clic JavaScript falló: {str(e2)[:100]}, intentando con eventos...")
                    # Último recurso: disparar eventos manualmente
                    self.driver.execute_script("""
                        var btn = arguments[0];
                        var evt = new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        btn.dispatchEvent(evt);
                    """, target_button)
            
            time.sleep(1)
            
            print(f"  ✓ Opción {choice_index} seleccionada")
            return True
            
        except Exception as e:
            print(f"  ✗ Error al seleccionar respuesta: {str(e)}")
            return False
    
    def select_multiple_answers(self, choice_indices: List[int]) -> bool:
        """
        Selecciona múltiples respuestas
        
        Args:
            choice_indices: Lista de índices de opciones a seleccionar (1-based)
            
        Returns:
            True si se seleccionaron correctamente, False en caso contrario
        """
        try:
            success_count = 0
            for index in choice_indices:
                if self.select_answer(index, allow_multiple=True):
                    success_count += 1
                    time.sleep(0.5)  # Pequeña pausa entre selecciones
            
            print(f"  ✓ {success_count}/{len(choice_indices)} opciones seleccionadas")
            return success_count > 0
            
        except Exception as e:
            print(f"  ✗ Error al seleccionar múltiples respuestas: {str(e)}")
            return False
    
    def get_answer_from_openai(self, question_data: Dict) -> List[int]:
        """
        Obtiene la respuesta correcta usando OpenAI
        
        Args:
            question_data: Diccionario con 'question' y 'choices'
            
        Returns:
            Lista de índices de respuestas correctas (1-based). Si solo permite una, retorna lista con un elemento.
        """
        if not self.openai_client:
            print("  ⚠ OpenAI no está configurado, seleccionando primera opción")
            return [1]
        
        try:
            # Construir el prompt
            allows_multiple = question_data.get('allows_multiple', False)
            choices_text = "\n".join([f"{i}. {choice['text']}" for i, choice in enumerate(question_data['choices'], 1)])
            
            if allows_multiple:
                prompt = f"""Eres un experto en programación Java. Responde la siguiente pregunta de quiz de manera precisa y concisa.

Pregunta:
{question_data['question']}

Opciones:
{choices_text}

Esta pregunta permite MÚLTIPLES respuestas correctas. Responde con los números de TODAS las opciones correctas separadas por comas (ej: 1, 3, 5). Si solo hay una correcta, responde solo ese número. No incluyas explicaciones ni texto adicional."""
            else:
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
                max_tokens=20 if allows_multiple else 10
            )
            
            answer_text = response.choices[0].message.content.strip()
            print(f"  📝 Respuesta cruda de OpenAI: '{answer_text}'")
            
            # Extraer los números de las respuestas
            try:
                # Buscar todos los números en la respuesta usando regex
                # Esto maneja casos como "1", "1, 3, 5", "opción 2", "la respuesta es 3", etc.
                numbers = re.findall(r'\b(\d+)\b', answer_text)
                
                if not numbers:
                    print(f"  ⚠ No se encontraron números en la respuesta: '{answer_text}'")
                    return [1]
                
                # Convertir a enteros y filtrar por rango válido
                answer_nums = []
                for num_str in numbers:
                    try:
                        num = int(num_str)
                        if 1 <= num <= len(question_data['choices']):
                            answer_nums.append(num)
                        else:
                            print(f"  ⚠ Número fuera de rango ignorado: {num} (rango válido: 1-{len(question_data['choices'])})")
                    except ValueError:
                        continue
                
                # Si no hay números válidos, usar el primero encontrado aunque esté fuera de rango
                if not answer_nums and numbers:
                    try:
                        first_num = int(numbers[0])
                        if first_num > 0:
                            # Ajustar al rango válido si es necesario
                            adjusted_num = min(max(1, first_num), len(question_data['choices']))
                            answer_nums = [adjusted_num]
                            print(f"  ⚠ Número ajustado al rango válido: {first_num} -> {adjusted_num}")
                    except:
                        pass
                
                # Si aún no hay números válidos, usar fallback
                if not answer_nums:
                    print(f"  ⚠ No se pudieron extraer números válidos de: '{answer_text}'")
                    return [1]
                
                # Eliminar duplicados manteniendo el orden
                unique_answers = []
                for num in answer_nums:
                    if num not in unique_answers:
                        unique_answers.append(num)
                
                if unique_answers:
                    if allows_multiple:
                        print(f"  ✓ OpenAI sugiere opciones: {', '.join(map(str, unique_answers))}")
                    else:
                        print(f"  ✓ OpenAI sugiere opción {unique_answers[0]}")
                    return unique_answers
                else:
                    print(f"  ⚠ No se encontraron respuestas válidas después del procesamiento")
                    return [1]
            except Exception as e:
                print(f"  ⚠ Error al parsear la respuesta de OpenAI: '{answer_text}' - Error: {str(e)}")
                import traceback
                traceback.print_exc()
                return [1]
                
        except Exception as e:
            print(f"  ✗ Error al consultar OpenAI: {str(e)}")
            return [1]
    
    def click_complete_assessment_button(self) -> bool:
        """
        Busca y hace clic en el botón "Complete Assessment" con múltiples métodos
        Maneja modales/popups que puedan contener el botón
        
        Returns:
            True si encontró y clickeó el botón, False en caso contrario
        """
        try:
            # Verificar si se abrió una nueva ventana/pestaña (como en el login)
            original_window = self.driver.current_window_handle
            window_count_before = len(self.driver.window_handles)
            
            # Verificar URL actual para ver si estamos en página de resultados
            current_url = self.driver.current_url
            print(f"  🔍 URL actual al buscar botón: {current_url[:100]}...")
            
            # Si estamos en página de resultados (p=63000:192, NO p=63000:190 que es el quiz), esperar más tiempo
            is_results_page = ':192:' in current_url or 'P192' in current_url
            if is_results_page:
                print("  📋 Detectada página de resultados (p=63000:192), esperando carga completa...")
                time.sleep(5)  # Esperar más tiempo en página de resultados
            
            # Esperar un momento para que cualquier modal/popup se abra o nueva ventana
            print("  ⏳ Esperando a que aparezca el modal/botón...")
            
            # Esperar múltiples veces con verificaciones intermedias
            for wait_attempt in range(5):
                time.sleep(2)
                print(f"  ⏳ Espera {wait_attempt + 1}/5...")
                
                # Verificar si el botón ya está disponible
                try:
                    complete_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-otel-label='CONFIRMCOMPLETE']")
                    if complete_button:
                        print("  ✓ Botón encontrado durante la espera")
                        break
                except:
                    pass
                
                # Verificar si el overlay está visible
                try:
                    overlay = self.driver.find_element(By.CSS_SELECTOR, "div.ui-widget-overlay")
                    if overlay.is_displayed():
                        print("  ✓ Overlay detectado durante la espera")
                        break
                except:
                    pass
                
                # Verificar si la URL cambió
                new_url = self.driver.current_url
                if new_url != current_url:
                    print(f"  📋 URL cambió durante la espera: {new_url[:100]}...")
                    current_url = new_url
                    time.sleep(2)  # Esperar a que cargue la nueva página
            
            window_count_after = len(self.driver.window_handles)
            if window_count_after > window_count_before:
                print(f"  📋 Se detectó nueva ventana/pestaña ({window_count_after} ventanas)")
                # Cambiar a la nueva ventana
                for window_handle in self.driver.window_handles:
                    if window_handle != original_window:
                        self.driver.switch_to.window(window_handle)
                        print(f"  ✓ Cambiado a nueva ventana - URL: {self.driver.current_url}")
                        break
            
            # Usar WebDriverWait para esperar que aparezca el botón o modal
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            wait_modal = WebDriverWait(self.driver, 15)
            
            # DEBUG: Mostrar información de la página actual
            print(f"  🔍 DEBUG - URL actual: {self.driver.current_url}")
            print(f"  🔍 DEBUG - Título de la página: {self.driver.title}")
            
            # Buscar TODOS los botones visibles en la página para debugging
            try:
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                visible_buttons = []
                for btn in all_buttons:
                    try:
                        if btn.is_displayed():
                            btn_text = btn.text.strip()
                            btn_id = btn.get_attribute('id') or ''
                            btn_data_label = btn.get_attribute('data-otel-label') or ''
                            if 'complete' in btn_text.lower() or 'CONFIRMCOMPLETE' in btn_data_label:
                                visible_buttons.append({
                                    'text': btn_text,
                                    'id': btn_id,
                                    'data-otel-label': btn_data_label
                                })
                    except:
                        continue
                
                if visible_buttons:
                    print(f"  🔍 DEBUG - Encontrados {len(visible_buttons)} botón(es) con 'Complete' o CONFIRMCOMPLETE:")
                    for idx, btn_info in enumerate(visible_buttons[:5], 1):
                        print(f"    {idx}. texto='{btn_info['text']}', id='{btn_info['id']}', data-otel-label='{btn_info['data-otel-label']}'")
            except:
                pass
            
            # Método PRIMERO: Buscar directamente el botón por ID quiz-submit (más específico)
            complete_button = None
            try:
                print("  🔍 Buscando botón por id='quiz-submit'...")
                complete_button = wait_modal.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button#quiz-submit"))
                )
                print("  ✓ Botón encontrado por ID quiz-submit")
            except Exception:
                # Método PRIMERO.5: Buscar por data-otel-label='SUBMIT'
                try:
                    print("  🔍 Buscando botón por data-otel-label='SUBMIT'...")
                    complete_button = wait_modal.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-otel-label='SUBMIT']"))
                    )
                    print("  ✓ Botón encontrado por data-otel-label='SUBMIT'")
                except Exception:
                    # Método PRIMERO.6: Buscar por data-otel-label='CONFIRMCOMPLETE'
                    try:
                        print("  🔍 Buscando botón por data-otel-label='CONFIRMCOMPLETE'...")
                        complete_button = wait_modal.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-otel-label='CONFIRMCOMPLETE']"))
                        )
                        print("  ✓ Botón encontrado por data-otel-label='CONFIRMCOMPLETE'")
                    except Exception:
                        complete_button = None
            
            if complete_button:
                # Verificar visibilidad con JavaScript
                is_visible = self.driver.execute_script(
                    "return arguments[0].offsetParent !== null && "
                    "window.getComputedStyle(arguments[0]).display !== 'none' && "
                    "window.getComputedStyle(arguments[0]).visibility !== 'hidden';",
                    complete_button
                )
                
                # Verificar el texto del botón para confirmar que es "Complete Assessment"
                button_text = ""
                try:
                    button_text = complete_button.find_element(By.CSS_SELECTOR, "span.t-Button-label").text.strip()
                except Exception:
                    button_text = complete_button.text.strip()
                
                print(f"  📋 Texto del botón encontrado: '{button_text}'")
                
                if is_visible and ("Complete Assessment" in button_text or "Complete" in button_text):
                    print("  ✓ Botón 'Complete Assessment' encontrado y visible")
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", complete_button)
                    time.sleep(1)
                    
                    # Intentar hacer clic con JavaScript si el clic normal falla
                    try:
                        complete_button.click()
                        print("  ✓ Clic realizado con método normal")
                    except Exception:
                        print("  ⚠ Clic normal falló, intentando con JavaScript...")
                        self.driver.execute_script("arguments[0].click();", complete_button)
                        print("  ✓ Clic realizado con JavaScript")
                    
                    time.sleep(4)
                    print("  ✓ Clic en 'Complete Assessment' realizado")
                    # Si cambiamos de ventana, volver a la original
                    if window_count_after > window_count_before:
                        self.driver.switch_to.window(original_window)
                    return True
                else:
                    print(f"  ⚠ Botón encontrado pero no está visible o no tiene el texto correcto (visible={is_visible}, texto='{button_text}')")
            
            # Intentar esperar a que aparezca el overlay ui-widget-overlay (jQuery UI modal)
            try:
                overlay = wait_modal.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.ui-widget-overlay"))
                )
                if overlay.is_displayed():
                    print("  ✓ Overlay ui-widget-overlay detectado, buscando modal y botón dentro...")
                    # Buscar el modal dentro del overlay o después de él
                    try:
                        # El modal generalmente está después del overlay en el DOM
                        modal = self.driver.find_element(By.CSS_SELECTOR, 
                            "div.ui-dialog, div[role='dialog'], div.t-Dialog")
                        if modal.is_displayed():
                            print("  ✓ Modal encontrado dentro del overlay")
                    except:
                        pass
            except:
                pass
            
            # Intentar esperar a que aparezca un modal/dialog
            try:
                modal = wait_modal.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 
                        "div[role='dialog'], div.ui-dialog, div.modal, div.popup, div.t-Dialog, div[class*='Dialog'], div[class*='Modal']"))
                )
                if modal.is_displayed():
                    print("  ✓ Modal/dialog detectado, buscando botón dentro...")
            except:
                pass
            
            # Método 0: Buscar en div.t-ButtonRegion-buttons (como en el HTML proporcionado)
            try:
                button_regions = self.driver.find_elements(By.CSS_SELECTOR, "div.t-ButtonRegion-buttons")
                print(f"  📋 Encontrados {len(button_regions)} div.t-ButtonRegion-buttons")
                for idx, region in enumerate(button_regions):
                    try:
                        # Verificar si está visible usando JavaScript (más confiable)
                        is_visible = self.driver.execute_script(
                            "return arguments[0].offsetParent !== null && "
                            "window.getComputedStyle(arguments[0]).display !== 'none' && "
                            "window.getComputedStyle(arguments[0]).visibility !== 'hidden';",
                            region
                        )
                        
                        if is_visible:
                            print(f"  📋 t-ButtonRegion {idx+1} está visible")
                            # Buscar el botón dentro del div
                            complete_button = region.find_element(By.CSS_SELECTOR, 
                                "button[data-otel-label='CONFIRMCOMPLETE']")
                            
                            if complete_button:
                                button_visible = self.driver.execute_script(
                                    "return arguments[0].offsetParent !== null && "
                                    "window.getComputedStyle(arguments[0]).display !== 'none';",
                                    complete_button
                                )
                                if button_visible:
                                    print("  ✓ Encontrado botón 'Complete Assessment' en t-ButtonRegion")
                                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", complete_button)
                                    time.sleep(0.8)
                                    complete_button.click()
                                    time.sleep(4)
                                    print("  ✓ Clic en 'Complete Assessment' realizado")
                                    # Si cambiamos de ventana, volver a la original
                                    if window_count_after > window_count_before:
                                        self.driver.switch_to.window(original_window)
                                    return True
                    except Exception as e:
                        print(f"  ⚠ Error en t-ButtonRegion {idx+1}: {str(e)}")
                        continue
            except Exception as e:
                print(f"  ⚠ Error buscando t-ButtonRegion: {str(e)}")
                pass
            
            # Método 0.5: Buscar específicamente cuando ui-widget-overlay está visible
            try:
                overlays = self.driver.find_elements(By.CSS_SELECTOR, "div.ui-widget-overlay")
                print(f"  📋 Encontrados {len(overlays)} overlay(s) ui-widget-overlay")
                for idx, overlay in enumerate(overlays):
                    try:
                        is_visible = self.driver.execute_script(
                            "return arguments[0].offsetParent !== null && "
                            "window.getComputedStyle(arguments[0]).display !== 'none' && "
                            "window.getComputedStyle(arguments[0]).visibility !== 'hidden' && "
                            "parseFloat(window.getComputedStyle(arguments[0]).opacity) > 0;",
                            overlay
                        )
                        
                        if is_visible:
                            print(f"  📋 Overlay ui-widget-overlay {idx+1} está visible (z-index: {overlay.value_of_css_property('z-index')})")
                            
                            # Cuando el overlay está visible, buscar el modal que generalmente está después en el DOM
                            # o buscar directamente el botón en toda la página
                            try:
                                # Buscar el modal ui-dialog que está después del overlay
                                modal = self.driver.find_element(By.XPATH, 
                                    "//div[@class='ui-widget-overlay']/following-sibling::div[contains(@class, 'ui-dialog')] | "
                                    "//div[@class='ui-widget-overlay']/following-sibling::div[@role='dialog']")
                                
                                if modal:
                                    print(f"  📋 Modal encontrado después del overlay {idx+1}")
                                    complete_button = modal.find_element(By.CSS_SELECTOR, 
                                        "button[data-otel-label='CONFIRMCOMPLETE']")
                                    
                                    if complete_button:
                                        button_visible = self.driver.execute_script(
                                            "return arguments[0].offsetParent !== null && "
                                            "window.getComputedStyle(arguments[0]).display !== 'none';",
                                            complete_button
                                        )
                                        if button_visible:
                                            print("  ✓ Encontrado botón 'Complete Assessment' en modal dentro de ui-widget-overlay")
                                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", complete_button)
                                            time.sleep(0.8)
                                            complete_button.click()
                                            time.sleep(4)
                                            print("  ✓ Clic en 'Complete Assessment' realizado")
                                            if window_count_after > window_count_before:
                                                self.driver.switch_to.window(original_window)
                                            return True
                            except:
                                # Si no encuentra el modal, buscar el botón directamente cuando el overlay está visible
                                try:
                                    complete_button = self.driver.find_element(By.CSS_SELECTOR, 
                                        "button[data-otel-label='CONFIRMCOMPLETE']")
                                    
                                    if complete_button:
                                        button_visible = self.driver.execute_script(
                                            "return arguments[0].offsetParent !== null && "
                                            "window.getComputedStyle(arguments[0]).display !== 'none' && "
                                            "window.getComputedStyle(arguments[0]).zIndex > 900;",
                                            complete_button
                                        )
                                        if button_visible:
                                            print("  ✓ Encontrado botón 'Complete Assessment' cuando overlay está visible")
                                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", complete_button)
                                            time.sleep(0.8)
                                            complete_button.click()
                                            time.sleep(4)
                                            print("  ✓ Clic en 'Complete Assessment' realizado")
                                            if window_count_after > window_count_before:
                                                self.driver.switch_to.window(original_window)
                                            return True
                                except:
                                    pass
                    except Exception as e:
                        print(f"  ⚠ Error en overlay {idx+1}: {str(e)}")
                        continue
            except Exception as e:
                print(f"  ⚠ Error buscando ui-widget-overlay: {str(e)}")
                pass
            
            # Método 1: Buscar modales/popups primero y cambiar el contexto si es necesario
            try:
                # Buscar modales comunes (dialog, modal, popup)
                modal_selectors = [
                    "div.ui-dialog",  # Prioridad alta para jQuery UI
                    "div[role='dialog']",
                    "div.modal",
                    "div.popup",
                    "div.t-Dialog",
                    "div[class*='Dialog']",
                    "div[class*='Modal']",
                    "div[class*='dialog']",
                    "div[class*='popup']"
                ]
                
                all_modals = []
                for selector in modal_selectors:
                    try:
                        modals = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        all_modals.extend(modals)
                    except:
                        continue
                
                if all_modals:
                    print(f"  📋 Encontrados {len(all_modals)} modal(es)/popup(s), buscando botón dentro...")
                    for idx, modal in enumerate(all_modals):
                        try:
                            is_visible = self.driver.execute_script(
                                "return arguments[0].offsetParent !== null && "
                                "window.getComputedStyle(arguments[0]).display !== 'none' && "
                                "window.getComputedStyle(arguments[0]).visibility !== 'hidden' && "
                                "window.getComputedStyle(arguments[0]).opacity !== '0';",
                                modal
                            )
                            
                            if is_visible:
                                print(f"  📋 Modal {idx+1} está visible")
                                # Buscar el botón dentro del modal
                                complete_button = modal.find_element(By.CSS_SELECTOR, 
                                    "button[data-otel-label='CONFIRMCOMPLETE']")
                                
                                if complete_button:
                                    button_visible = self.driver.execute_script(
                                        "return arguments[0].offsetParent !== null && "
                                        "window.getComputedStyle(arguments[0]).display !== 'none';",
                                        complete_button
                                    )
                                    if button_visible:
                                        print("  ✓ Encontrado botón 'Complete Assessment' en modal")
                                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", complete_button)
                                        time.sleep(0.8)
                                        complete_button.click()
                                        time.sleep(4)
                                        print("  ✓ Clic en 'Complete Assessment' realizado")
                                        # Si cambiamos de ventana, volver a la original
                                        if window_count_after > window_count_before:
                                            self.driver.switch_to.window(original_window)
                                        return True
                        except Exception as e:
                            print(f"  ⚠ Error en modal {idx+1}: {str(e)}")
                            continue
            except Exception as e:
                print(f"  ⚠ Error buscando modales: {str(e)}")
                pass
            
            # Método 2: Buscar por data-otel-label (más específico, debe ser prioritario)
            try:
                complete_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-otel-label='CONFIRMCOMPLETE']")
                if complete_button.is_displayed():
                    print("  ✓ Encontrado botón 'Complete Assessment' (por data-otel-label)")
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", complete_button)
                    time.sleep(0.8)
                    complete_button.click()
                    time.sleep(4)
                    print("  ✓ Clic en 'Complete Assessment' realizado")
                    return True
            except:
                pass
            
            # Método 3: Buscar por ID que empiece con B y data-otel-label
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[id^='B'][data-otel-label='CONFIRMCOMPLETE']")
                for button in buttons:
                    if button.is_displayed():
                        print("  ✓ Encontrado botón 'Complete Assessment' (por ID y data-otel-label)")
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                        time.sleep(0.8)
                        button.click()
                        time.sleep(4)
                        print("  ✓ Clic en 'Complete Assessment' realizado")
                        return True
            except:
                pass
            
            # Método 4: Buscar cualquier botón con texto "Complete Assessment"
            try:
                complete_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Complete Assessment')]")
                if complete_button.is_displayed():
                    print("  ✓ Encontrado botón 'Complete Assessment' (por texto)")
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", complete_button)
                    time.sleep(0.8)
                    complete_button.click()
                    time.sleep(4)
                    print("  ✓ Clic en 'Complete Assessment' realizado")
                    return True
            except:
                pass
            
            # Método 5: Buscar por selector CSS estándar
            try:
                complete_button = self.driver.find_element(By.CSS_SELECTOR, self.selectors.COMPLETE_ASSESSMENT_BUTTON)
                if complete_button.is_displayed():
                    button_text = complete_button.find_element(By.CSS_SELECTOR, "span.t-Button-label").text.strip()
                    if "Complete Assessment" in button_text or "Complete" in button_text:
                        print("  ✓ Encontrado botón 'Complete Assessment' (por CSS)")
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", complete_button)
                        time.sleep(0.8)
                        complete_button.click()
                        time.sleep(4)
                        print("  ✓ Clic en 'Complete Assessment' realizado")
                        return True
            except:
                pass
            
            # Método 6: Buscar por XPath con texto
            try:
                complete_button = self.driver.find_element(By.XPATH, self.selectors.COMPLETE_ASSESSMENT_BUTTON_XPATH)
                if complete_button.is_displayed():
                    print("  ✓ Encontrado botón 'Complete Assessment' (por XPath)")
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", complete_button)
                    time.sleep(0.8)
                    complete_button.click()
                    time.sleep(4)
                    print("  ✓ Clic en 'Complete Assessment' realizado")
                    return True
            except:
                pass
            
            # Debug: mostrar información sobre la página actual
            print("  🔍 Información de depuración:")
            print(f"    - URL actual: {self.driver.current_url}")
            print(f"    - Ventanas abiertas: {len(self.driver.window_handles)}")
            print(f"    - Ventana actual: {self.driver.current_window_handle}")
            
            # Buscar TODOS los botones en la página (visibles y no visibles)
            try:
                print("  🔍 Buscando TODOS los botones en la página...")
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                print(f"    - Total de botones encontrados: {len(all_buttons)}")
                
                complete_buttons = []
                confirmcomplete_buttons = []
                
                for btn in all_buttons:
                    try:
                        btn_text = btn.text.strip().lower()
                        btn_id = btn.get_attribute('id') or ''
                        btn_data_label = btn.get_attribute('data-otel-label') or ''
                        
                        # Buscar por texto
                        if "complete assessment" in btn_text or "complete" in btn_text:
                            is_visible = btn.is_displayed()
                            complete_buttons.append({
                                'element': btn,
                                'text': btn.text.strip(),
                                'id': btn_id,
                                'data-otel-label': btn_data_label,
                                'visible': is_visible
                            })
                        
                        # Buscar por data-otel-label
                        if 'CONFIRMCOMPLETE' in btn_data_label or 'confirmcomplete' in btn_data_label.lower():
                            is_visible = btn.is_displayed()
                            confirmcomplete_buttons.append({
                                'element': btn,
                                'text': btn.text.strip(),
                                'id': btn_id,
                                'data-otel-label': btn_data_label,
                                'visible': is_visible
                            })
                    except:
                        continue
                
                # Mostrar botones encontrados
                if complete_buttons:
                    print(f"    - Encontrados {len(complete_buttons)} botón(es) con 'Complete' en el texto:")
                    for idx, btn_info in enumerate(complete_buttons[:5], 1):
                        print(f"      {idx}. texto='{btn_info['text'][:60]}', id='{btn_info['id']}', data-otel-label='{btn_info['data-otel-label']}', visible={btn_info['visible']}")
                
                if confirmcomplete_buttons:
                    print(f"    - Encontrados {len(confirmcomplete_buttons)} botón(es) con CONFIRMCOMPLETE:")
                    for idx, btn_info in enumerate(confirmcomplete_buttons[:5], 1):
                        print(f"      {idx}. texto='{btn_info['text'][:60]}', id='{btn_info['id']}', data-otel-label='{btn_info['data-otel-label']}', visible={btn_info['visible']}")
                
                # Intentar hacer clic en el primer botón encontrado con CONFIRMCOMPLETE
                if confirmcomplete_buttons:
                    for btn_info in confirmcomplete_buttons:
                        try:
                            btn = btn_info['element']
                            print(f"  🎯 Intentando hacer clic en botón: id='{btn_info['id']}', texto='{btn_info['text']}'")
                            
                            # Forzar visibilidad y habilitación del botón
                            print("  🔧 Forzando visibilidad del botón...")
                            self.driver.execute_script("""
                                arguments[0].style.display = 'block';
                                arguments[0].style.visibility = 'visible';
                                arguments[0].style.opacity = '1';
                                arguments[0].style.zIndex = '9999';
                                arguments[0].disabled = false;
                                arguments[0].removeAttribute('disabled');
                            """, btn)
                            time.sleep(1)
                            
                            # Scroll al botón
                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
                            time.sleep(1)
                            
                            # Múltiples intentos de clic
                            clicked = False
                            
                            # Intento 1: Clic normal
                            try:
                                btn.click()
                                print("  ✓ Clic realizado con método normal")
                                clicked = True
                            except Exception as e1:
                                print(f"  ⚠ Clic normal falló: {str(e1)}")
                                
                                # Intento 2: Clic con JavaScript
                                try:
                                    self.driver.execute_script("arguments[0].click();", btn)
                                    print("  ✓ Clic realizado con JavaScript")
                                    clicked = True
                                except Exception as e2:
                                    print(f"  ⚠ Clic JavaScript falló: {str(e2)}")
                                    
                                    # Intento 3: Disparar eventos manualmente
                                    try:
                                        self.driver.execute_script("""
                                            var evt = new MouseEvent('click', {
                                                bubbles: true,
                                                cancelable: true,
                                                view: window
                                            });
                                            arguments[0].dispatchEvent(evt);
                                        """, btn)
                                        print("  ✓ Evento click disparado manualmente")
                                        clicked = True
                                    except Exception as e3:
                                        print(f"  ⚠ Disparo de evento falló: {str(e3)}")
                            
                            if clicked:
                                time.sleep(4)
                                print("  ✓ Clic en 'Complete Assessment' realizado exitosamente")
                                if window_count_after > window_count_before:
                                    self.driver.switch_to.window(original_window)
                                return True
                        except Exception as e:
                            print(f"  ⚠ Error al hacer clic en botón: {str(e)}")
                            import traceback
                            traceback.print_exc()
                            continue
                
            except Exception as e:
                print(f"  ⚠ Error buscando botones: {str(e)}")
                import traceback
                traceback.print_exc()
                pass
            
            print("  ⚠ No se encontró el botón 'Complete Assessment' en ningún lugar")
            
            # Si cambiamos de ventana, volver a la original
            if window_count_after > window_count_before:
                self.driver.switch_to.window(original_window)
            
            return False
            
        except Exception as e:
            print(f"  ⚠ Error al buscar botón 'Complete Assessment': {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Si cambiamos de ventana, volver a la original
            try:
                if window_count_after > window_count_before:
                    self.driver.switch_to.window(original_window)
            except:
                pass
            
            return False
    
    def go_to_next_question(self) -> bool:
        """
        Avanza a la siguiente pregunta o envía el quiz
        
        Returns:
            True si avanzó correctamente, False si el quiz terminó
        """
        try:
            # Verificar si es la última pregunta ANTES de hacer submit
            is_last_question = False
            try:
                question_heading = self.driver.find_element(By.CSS_SELECTOR, self.selectors.QUESTION_HEADING)
                heading_text = question_heading.text.strip()
                # Verificar si dice "Question X of X" donde ambos números son iguales
                match = re.search(r'Question\s+(\d+)\s+of\s+(\d+)', heading_text, re.IGNORECASE)
                if match:
                    current_q = int(match.group(1))
                    total_q = int(match.group(2))
                    if current_q == total_q:
                        is_last_question = True
                        print(f"  📋 Detectada última pregunta ({current_q} de {total_q})")
            except:
                pass
            
            # Si es la última pregunta, buscar el botón "Complete Assessment" ANTES de hacer submit
            if is_last_question:
                print("  🔍 Es la última pregunta, buscando botón 'Complete Assessment'...")
                try:
                    # Buscar el botón en el breadcrumb (id="quiz-submit" o data-otel-label="SUBMIT")
                    complete_button = None
                    
                    # Método 1: Por ID quiz-submit
                    try:
                        complete_button = self.driver.find_element(By.CSS_SELECTOR, "button#quiz-submit")
                        button_text = ""
                        try:
                            button_text = complete_button.find_element(By.CSS_SELECTOR, "span.t-Button-label").text.strip()
                        except:
                            button_text = complete_button.text.strip()
                        
                        if "Complete Assessment" in button_text:
                            print("  ✓ Encontrado botón 'Complete Assessment' en breadcrumb (por ID)")
                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", complete_button)
                            time.sleep(0.5)
                            complete_button.click()
                            time.sleep(4)
                            print("  ✓ Clic en 'Complete Assessment' realizado")
                            return False  # Quiz terminado
                    except:
                        pass
                    
                    # Método 2: Por data-otel-label="SUBMIT"
                    try:
                        submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[data-otel-label='SUBMIT']")
                        for btn in submit_buttons:
                            try:
                                button_text = btn.find_element(By.CSS_SELECTOR, "span.t-Button-label").text.strip()
                                if "Complete Assessment" in button_text:
                                    print("  ✓ Encontrado botón 'Complete Assessment' en breadcrumb (por data-otel-label)")
                                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
                                    time.sleep(0.5)
                                    btn.click()
                                    time.sleep(4)
                                    print("  ✓ Clic en 'Complete Assessment' realizado")
                                    return False  # Quiz terminado
                            except:
                                continue
                    except:
                        pass
                except Exception as e:
                    print(f"  ⚠ Error buscando botón Complete Assessment: {str(e)[:100]}")
            
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
            
            # Método 2: Buscar botón Submit por ID (solo si NO es la última pregunta)
            if not is_last_question:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, self.selectors.SUBMIT_QUIZ_BUTTON)
                    button_text = ""
                    try:
                        button_text = submit_button.find_element(By.CSS_SELECTOR, "span.t-Button-label").text.strip()
                    except:
                        button_text = submit_button.text.strip()
                    
                    # Solo usar si NO dice "Complete Assessment"
                    if "Complete Assessment" not in button_text:
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
            
            # Método 3: Buscar por texto "Submit Answer" (solo si NO es la última pregunta o si no encontramos Complete Assessment)
            if not is_last_question:
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
            
            # Método 4: Si es la última pregunta y no encontramos Complete Assessment antes, buscar ahora
            if is_last_question:
                print("  🔍 Última pregunta: buscando botón 'Complete Assessment' como último recurso...")
                complete_clicked = self.click_complete_assessment_button()
                if complete_clicked:
                    return False  # Quiz terminado
            
            print("  ⚠ No se encontró botón Next/Submit/Complete")
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
                    # Si no encuentra el contenedor, verificar si hay mensaje de finalización o botón Complete
                    try:
                        # Buscar indicadores de que el quiz terminó
                        page_text = self.driver.page_source.lower()
                        if "quiz complete" in page_text or "assessment complete" in page_text or "results" in page_text:
                            print("  ✓ Quiz completado (indicador encontrado en página)")
                            # Intentar hacer clic en Complete Assessment
                            time.sleep(2)
                            if self.click_complete_assessment_button():
                                print("  ✓ Botón 'Complete Assessment' clickeado")
                            break
                        
                        # También buscar el botón Complete Assessment directamente
                        time.sleep(2)
                        if self.click_complete_assessment_button():
                            print("  ✓ Botón 'Complete Assessment' encontrado y clickeado")
                            break
                    except:
                        pass
                    
                    print("  ⚠ No se encontró contenedor de pregunta, puede que el quiz haya terminado")
                    # Último intento de buscar Complete Assessment
                    time.sleep(2)
                    if self.click_complete_assessment_button():
                        print("  ✓ Botón 'Complete Assessment' encontrado al final")
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
                
                # Obtener respuesta(s) de OpenAI
                answer_indices = self.get_answer_from_openai(question_data)
                
                # Debug: mostrar qué respuestas se van a seleccionar
                print(f"  🔍 Respuestas a seleccionar: {answer_indices}")
                
                # Seleccionar la(s) respuesta(s)
                answer_selected = False
                if question_data.get('allows_multiple', False):
                    # Seleccionar múltiples respuestas
                    print(f"  📌 Modo: Múltiples respuestas permitidas")
                    if self.select_multiple_answers(answer_indices):
                        questions_answered += 1
                        print(f"  ✓ Pregunta {questions_answered} respondida (múltiples opciones: {answer_indices})")
                        answer_selected = True
                    else:
                        print(f"  ⚠ No se pudieron seleccionar las respuestas múltiples: {answer_indices}")
                        consecutive_errors += 1
                        if consecutive_errors >= max_consecutive_errors:
                            break
                        continue
                else:
                    # Seleccionar una sola respuesta
                    print(f"  📌 Modo: Una sola respuesta permitida")
                    if len(answer_indices) > 0:
                        selected_index = answer_indices[0]
                        print(f"  🎯 Seleccionando opción {selected_index} de {len(question_data['choices'])} disponibles")
                        if self.select_answer(selected_index, allow_multiple=False):
                            questions_answered += 1
                            print(f"  ✓ Pregunta {questions_answered} respondida (opción {selected_index})")
                            answer_selected = True
                        else:
                            print(f"  ⚠ No se pudo seleccionar la respuesta {selected_index}")
                            consecutive_errors += 1
                            if consecutive_errors >= max_consecutive_errors:
                                break
                            continue
                    else:
                        print("  ⚠ No se obtuvo respuesta de OpenAI (lista vacía)")
                        consecutive_errors += 1
                        if consecutive_errors >= max_consecutive_errors:
                            break
                        continue
                
                # Si se seleccionó la respuesta correctamente, avanzar
                if answer_selected:
                    # Resetear contador de errores
                    consecutive_errors = 0
                    
                    # Guardar URL actual antes de avanzar
                    url_before = self.driver.current_url
                    
                    # Esperar un momento antes de avanzar
                    time.sleep(1.5)
                    
                    # Avanzar a la siguiente pregunta
                    has_more = self.go_to_next_question()
                    
                    # Esperar a que la página se actualice
                    time.sleep(3)
                    
                    # Verificar si la URL cambió (puede indicar que se movió a página de resultados)
                    url_after = self.driver.current_url
                    url_changed = url_before != url_after
                    
                    if url_changed:
                        print(f"  📋 URL cambió después de avanzar:")
                        print(f"    Antes: {url_before[:100]}...")
                        print(f"    Después: {url_after[:100]}...")
                        
                        # Verificar si estamos en página de resultados (p=63000:192, NO p=63000:190 que es el quiz)
                        # p=63000:190 es la página del quiz, p=63000:192 es la página de resultados
                        if ':192:' in url_after or 'P192' in url_after:
                            print("  📋 Detectada página de resultados (p=63000:192)")
                            # Esperar a que cargue completamente la nueva página
                            time.sleep(5)
                            # Buscar el botón en esta nueva página
                            complete_clicked = self.click_complete_assessment_button()
                            
                            if complete_clicked:
                                print(f"\n  ✓ Quiz completado exitosamente - Total de preguntas respondidas: {questions_answered}")
                                break
                        else:
                            # Si cambió pero sigue siendo página del quiz (p=63000:190), solo continuar
                            print("  📋 URL cambió pero sigue siendo página del quiz, continuando...")
                    
                    if not has_more:
                        print(f"\n  ✓ Última pregunta respondida - Total: {questions_answered}")
                        
                        # Verificar que realmente sea la última pregunta leyendo el heading
                        is_really_last = False
                        try:
                            question_heading = self.driver.find_element(By.CSS_SELECTOR, self.selectors.QUESTION_HEADING)
                            heading_text = question_heading.text.strip()
                            match = re.search(r'Question\s+(\d+)\s+of\s+(\d+)', heading_text, re.IGNORECASE)
                            if match:
                                current_q = int(match.group(1))
                                total_q = int(match.group(2))
                                if current_q == total_q:
                                    is_really_last = True
                                    print(f"  ✓ Confirmado: Es la última pregunta ({current_q} de {total_q})")
                        except:
                            pass
                        
                        # Solo buscar Complete Assessment si realmente es la última pregunta
                        if is_really_last:
                            # Esperar más tiempo para que aparezca el botón o cambie la página
                            print("  ⏳ Esperando a que aparezca el botón o cambie la página...")
                            for wait_attempt in range(5):
                                time.sleep(2)
                                current_url = self.driver.current_url
                                
                                # Verificar si cambió a página de resultados (p=63000:192)
                                if ':192:' in current_url or 'P192' in current_url:
                                    print(f"  📋 Página cambió a resultados: {current_url[:100]}...")
                                    time.sleep(3)  # Esperar a que cargue
                                    break
                                
                                # Intentar buscar el botón en la página del quiz
                                try:
                                    btn = self.driver.find_element(By.CSS_SELECTOR, "button#quiz-submit")
                                    button_text = ""
                                    try:
                                        button_text = btn.find_element(By.CSS_SELECTOR, "span.t-Button-label").text.strip()
                                    except:
                                        button_text = btn.text.strip()
                                    
                                    if "Complete Assessment" in button_text:
                                        print("  ✓ Botón 'Complete Assessment' encontrado durante la espera")
                                        break
                                except:
                                    pass
                            
                            # Buscar explícitamente el botón "Complete Assessment"
                            print("  🔍 Buscando botón 'Complete Assessment'...")
                            complete_clicked = self.click_complete_assessment_button()
                            
                            if complete_clicked:
                                print(f"\n  ✓ Quiz completado exitosamente - Total de preguntas respondidas: {questions_answered}")
                            else:
                                print(f"\n  ⚠ Quiz completado pero no se encontró el botón 'Complete Assessment'")
                                print(f"  Total de preguntas respondidas: {questions_answered}")
                                print(f"  URL actual: {self.driver.current_url}")
                        else:
                            print(f"  ⚠ go_to_next_question() retornó False pero no es la última pregunta")
                            print(f"  Continuando con siguiente pregunta...")
                        
                        break
                    
                    # Esperar a que cargue la siguiente pregunta
                    time.sleep(2.5)
            
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

