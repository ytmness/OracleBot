"""
Manejador de login para Oracle Academy
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.selectors import Selectors


class LoginHandler:
    """Clase para manejar el proceso de login en Oracle Academy"""
    
    def __init__(self, driver: webdriver.Chrome):
        """
        Inicializa el manejador de login
        
        Args:
            driver: Instancia del WebDriver de Selenium
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.selectors = Selectors()
        self.actions = ActionChains(driver)
        self.in_iframe = False  # Rastrear si estamos dentro de un iframe
    
    def suppress_console_warnings(self):
        """Suprime warnings de consola de Oracle"""
        try:
            self.driver.execute_script("""
                (function() {
                    // Suprimir console.warn para mensajes específicos de Oracle
                    if (window.console && window.console.warn) {
                        const originalWarn = console.warn;
                        console.warn = function(...args) {
                            const message = args.join(' ').toLowerCase();
                            // Suprimir warnings específicos de Oracle
                            if (message.includes('duplicate id') || 
                                message.includes('autofocus processing') ||
                                message.includes('signin.js') ||
                                message.includes('without merging')) {
                                return;
                            }
                            originalWarn.apply(console, args);
                        };
                    }
                    
                    // También suprimir console.error para algunos casos
                    if (window.console && window.console.error) {
                        const originalError = console.error;
                        console.error = function(...args) {
                            const message = args.join(' ').toLowerCase();
                            // Suprimir solo warnings que son realmente informativos
                            if (message.includes('duplicate id fetched') || 
                                message.includes('without merging') ||
                                message.includes('signin.js')) {
                                return;
                            }
                            originalError.apply(console, args);
                        };
                    }
                    
                    // Interceptar el método _write si existe (usado por signin.js:2158)
                    try {
                        if (window.e && typeof window.e._write === 'function') {
                            const originalWrite = window.e._write;
                            window.e._write = function(...args) {
                                const message = args.join(' ').toLowerCase();
                                if (message.includes('duplicate id')) {
                                    return;
                                }
                                return originalWrite.apply(this, args);
                            };
                        }
                    } catch(e) {}
                })();
            """)
        except:
            pass  # Si falla, no es crítico
    
    def navigate_to_landing_page(self):
        """Navega a la página de inicio de Oracle Academy"""
        print("Navegando a la página de inicio...")
        self.driver.get(self.selectors.LANDING_PAGE_URL)
        time.sleep(2)
        # Suprimir warnings después de cargar la página
        self.suppress_console_warnings()
    
    def hover_sign_in(self):
        """Realiza hover sobre el botón de Sign In"""
        try:
            print("Haciendo hover sobre Sign In...")
            sign_in_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors.HOVER_SIGN_IN))
            )
            self.actions.move_to_element(sign_in_element).perform()
            time.sleep(1)
        except TimeoutException:
            print("Error: No se pudo encontrar el elemento de Sign In")
            raise
    
    def click_student_signin(self):
        """Hace clic en el enlace de Student Hub Sign In"""
        try:
            print("Haciendo clic en Student Hub Sign In...")
            student_signin = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors.STUDENT_SIGNIN_REDIRECTION))
            )
            
            # Scroll al elemento antes de hacer clic
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", student_signin)
            time.sleep(0.3)
            
            student_signin.click()
            
            # Esperar a que la nueva página cargue completamente
            print("Esperando a que cargue la página de login...")
            
            # Esperar a que la URL cambie o aparezca algún elemento de la página de login
            try:
                self.wait.until(lambda driver: 'signin' in driver.current_url.lower() or 
                              len(driver.find_elements(By.TAG_NAME, "input")) > 0)
                print(f"✓ Página de login detectada - URL: {self.driver.current_url}")
            except:
                print(f"⚠ Timeout esperando cambio de URL, pero continuando... URL actual: {self.driver.current_url}")
            
            # Esperar adicional para que se complete cualquier inicialización de JavaScript
            # y que el campo de usuario tenga autofocus
            print("Esperando a que el campo de usuario tenga autofocus...")
            time.sleep(3)  # Dar tiempo para que el autofocus se active
            
            # Verificar que el campo de usuario esté presente y tenga autofocus
            try:
                username_field = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors.FILL_USER))
                )
                print("✓ Campo de usuario encontrado en la página")
                
                # Esperar a que tenga autofocus (verificar elemento activo)
                for i in range(5):
                    active = self.driver.switch_to.active_element
                    if active and active.get_attribute('id') == 'idcs-signin-basic-signin-form-username':
                        print("✓ Campo de usuario tiene autofocus activo")
                        break
                    time.sleep(0.5)
            except:
                print("⚠ No se pudo verificar el campo de usuario, pero continuando...")
            
            # Ejecutar script para suprimir warnings de consola
            self.suppress_console_warnings()
            print("✓ Script de supresión de warnings ejecutado")
            
            print(f"URL actual: {self.driver.current_url}")
        except TimeoutException:
            print("Error: No se pudo encontrar el enlace de Student Hub Sign In")
            raise
    
    def switch_to_iframe_if_needed(self):
        """Cambia al iframe si el formulario de login está dentro de uno"""
        try:
            # Primero intentar encontrar el campo en el contenido principal
            try:
                from selenium.webdriver.support.ui import WebDriverWait as WDWait
                quick_wait = WDWait(self.driver, 2)
                test_field = quick_wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors.FILL_USER))
                )
                print("✓ Campo de usuario encontrado en contenido principal (sin iframe)")
                return False
            except:
                pass
            
            # Si no está en el contenido principal, buscar en iframes
            self.driver.switch_to.default_content()  # Asegurarse de estar en contenido principal
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            print(f"Encontrados {len(iframes)} iframes en la página")
            
            for i, iframe in enumerate(iframes):
                try:
                    # Intentar cambiar al iframe
                    self.driver.switch_to.frame(iframe)
                    print(f"Cambiado al iframe {i+1}")
                    
                    # Verificar si el campo de usuario está en este iframe
                    try:
                        from selenium.webdriver.support.ui import WebDriverWait as WDWait
                        quick_wait = WDWait(self.driver, 3)
                        test_field = quick_wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors.FILL_USER))
                        )
                        if test_field:
                            print(f"✓ Campo de usuario encontrado en iframe {i+1}")
                            return True
                    except:
                        pass
                    
                    # Volver al contenido principal para probar el siguiente iframe
                    self.driver.switch_to.default_content()
                except Exception as e:
                    print(f"Error al cambiar al iframe {i+1}: {str(e)}")
                    try:
                        self.driver.switch_to.default_content()
                    except:
                        pass
            
            # Si no se encontró en ningún iframe, volver al contenido principal
            self.driver.switch_to.default_content()
            return False
        except Exception as e:
            print(f"Error al buscar iframes: {str(e)}")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False
    
    def verify_login_page_loaded(self) -> bool:
        """
        Verifica que la página de login esté cargada buscando el label del campo de usuario
        
        Returns:
            True si la página está cargada, False en caso contrario
        """
        try:
            # Buscar el label del campo de usuario como indicador de que la página cargó
            from selenium.webdriver.support.ui import WebDriverWait as WDWait
            quick_wait = WDWait(self.driver, 5)
            
            try:
                label = quick_wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors.USER_LABEL))
                )
                label_text = label.text
                print(f"✓ Página de login detectada - Label encontrado: '{label_text}'")
                return True
            except:
                # Intentar con XPath
                try:
                    label = quick_wait.until(
                        EC.presence_of_element_located((By.XPATH, self.selectors.USER_LABEL_XPATH))
                    )
                    label_text = label.text
                    print(f"✓ Página de login detectada - Label encontrado: '{label_text}'")
                    return True
                except:
                    return False
        except Exception as e:
            print(f"Error al verificar página de login: {str(e)}")
            return False
    
    def remove_overlays(self):
        """Intenta remover overlays o elementos que puedan estar bloqueando la interacción"""
        try:
            # Buscar y ocultar overlays comunes
            overlays_removed = self.driver.execute_script("""
                var overlays = document.querySelectorAll('[class*="overlay"], [class*="modal"], [class*="backdrop"], [id*="overlay"], [id*="modal"], [class*="loading"], [class*="spinner"]');
                var count = 0;
                overlays.forEach(function(overlay) {
                    var style = window.getComputedStyle(overlay);
                    if (style.display !== 'none' && style.visibility !== 'hidden') {
                        overlay.style.display = 'none';
                        overlay.style.visibility = 'hidden';
                        overlay.style.opacity = '0';
                        overlay.style.pointerEvents = 'none';
                        count++;
                    }
                });
                return count;
            """)
            if overlays_removed > 0:
                print(f"✓ Removidos {overlays_removed} overlays que podrían estar bloqueando")
        except:
            pass
    
    def check_and_remove_blockers(self, element):
        """Verifica y remueve elementos que puedan estar bloqueando el campo"""
        try:
            print("\n=== VERIFICANDO BLOQUEADORES ===")
            
            # Verificar si hay elementos encima del campo
            blockers = self.driver.execute_script("""
                var field = arguments[0];
                var rect = field.getBoundingClientRect();
                var centerX = rect.left + rect.width / 2;
                var centerY = rect.top + rect.height / 2;
                var elementAtPoint = document.elementFromPoint(centerX, centerY);
                
                var blockers = [];
                if (elementAtPoint && elementAtPoint !== field) {
                    blockers.push({
                        tag: elementAtPoint.tagName,
                        id: elementAtPoint.id || '',
                        className: elementAtPoint.className || '',
                        zIndex: window.getComputedStyle(elementAtPoint).zIndex
                    });
                }
                
                // Buscar elementos con z-index alto que puedan estar encima
                var allElements = document.querySelectorAll('*');
                var highZElements = [];
                allElements.forEach(function(el) {
                    var style = window.getComputedStyle(el);
                    var zIndex = parseInt(style.zIndex) || 0;
                    if (zIndex > 1000 && el !== field) {
                        var elRect = el.getBoundingClientRect();
                        if (elRect.left <= centerX && elRect.right >= centerX &&
                            elRect.top <= centerY && elRect.bottom >= centerY) {
                            highZElements.push({
                                tag: el.tagName,
                                id: el.id || '',
                                className: el.className || '',
                                zIndex: zIndex
                            });
                        }
                    }
                });
                
                return {
                    elementAtPoint: blockers,
                    highZIndex: highZElements
                };
            """, element)
            
            if blockers['elementAtPoint']:
                print(f"⚠ Elemento bloqueando en el punto del campo: {blockers['elementAtPoint']}")
            if blockers['highZIndex']:
                print(f"⚠ Elementos con z-index alto cerca: {blockers['highZIndex']}")
            
            # Intentar remover elementos bloqueadores
            removed = self.driver.execute_script("""
                var field = arguments[0];
                var rect = field.getBoundingClientRect();
                var centerX = rect.left + rect.width / 2;
                var centerY = rect.top + rect.height / 2;
                var elementAtPoint = document.elementFromPoint(centerX, centerY);
                
                var count = 0;
                if (elementAtPoint && elementAtPoint !== field) {
                    // Verificar si es un overlay o elemento no esencial
                    var tag = elementAtPoint.tagName.toLowerCase();
                    var className = (elementAtPoint.className || '').toLowerCase();
                    var id = (elementAtPoint.id || '').toLowerCase();
                    
                    if (className.includes('overlay') || className.includes('backdrop') || 
                        className.includes('loading') || className.includes('spinner') ||
                        id.includes('overlay') || id.includes('backdrop')) {
                        elementAtPoint.style.display = 'none';
                        elementAtPoint.style.visibility = 'hidden';
                        elementAtPoint.style.pointerEvents = 'none';
                        count++;
                    }
                }
                return count;
            """, element)
            
            if removed > 0:
                print(f"✓ Removidos {removed} elementos bloqueadores")
            else:
                print("✓ No se encontraron elementos bloqueadores obvios")
            
            print("================================\n")
            
        except Exception as e:
            print(f"⚠ Error al verificar bloqueadores: {str(e)}")
    
    def force_enable_field(self, element):
        """Fuerza la habilitación del campo removiendo atributos bloqueadores"""
        try:
            print("Forzando habilitación del campo...")
            self.driver.execute_script("""
                var field = arguments[0];
                
                // Remover atributos bloqueadores
                field.removeAttribute('readonly');
                field.removeAttribute('disabled');
                field.removeAttribute('autofocus');
                
                // Forzar estilos que permitan interacción
                field.style.pointerEvents = 'auto';
                field.style.opacity = '1';
                field.style.visibility = 'visible';
                field.style.display = 'block';
                
                // Remover listeners que puedan estar bloqueando (si es posible)
                var newField = field.cloneNode(true);
                field.parentNode.replaceChild(newField, field);
                newField.value = '';
                
                return newField;
            """, element)
            print("✓ Campo forzado a estar habilitado")
        except Exception as e:
            print(f"⚠ Error al forzar habilitación: {str(e)}")
    
    def fill_username(self, username: str):
        """
        Llena el campo de usuario
        
        Args:
            username: Nombre de usuario
        """
        try:
            print(f"\n{'='*60}")
            print(f"LLENANDO CAMPO DE USUARIO: {username}")
            print(f"{'='*60}")
            print(f"URL actual: {self.driver.current_url}")
            
            # Verificar que estamos en la página de login (no en la landing page)
            if 'signin' not in self.driver.current_url.lower() and '63000' not in self.driver.current_url:
                print("⚠ ERROR: No estamos en la página de login!")
                print(f"   URL actual: {self.driver.current_url}")
                print("   Esperando a que cargue la página de login...")
                # Esperar a que la URL cambie
                try:
                    self.wait.until(lambda driver: 'signin' in driver.current_url.lower() or '63000' in driver.current_url)
                    print(f"✓ Página de login cargada - URL: {self.driver.current_url}")
                    time.sleep(2)  # Esperar adicional para que se complete la carga
                except:
                    print("⚠ Timeout esperando página de login, pero continuando...")
            
            # Verificar que la página de login esté cargada
            if not self.verify_login_page_loaded():
                print("⚠ Advertencia: No se pudo verificar que la página de login esté completamente cargada")
            
            # Remover overlays que puedan estar bloqueando
            self.remove_overlays()
            
            # --- INTENTO 0: usar directamente el elemento activo (ya tiene autofocus) ---
            # Esperar a que el campo de usuario esté enfocado (puede tardar un poco después de cargar)
            try:
                from selenium.webdriver.common.keys import Keys
                import time
                
                # Esperar hasta que el elemento activo sea el campo de usuario
                print("\n[Intento 0] Esperando a que el campo de usuario tenga autofocus...")
                max_attempts = 10
                active_input = None
                
                for attempt in range(max_attempts):
                    active = self.driver.switch_to.active_element
                    active_tag = active.tag_name if active else "None"
                    active_id = active.get_attribute('id') if active else "None"
                    
                    if active and active.tag_name.lower() == 'input' and 'username' in active_id.lower():
                        active_input = active
                        print(f"✓ Campo de usuario encontrado como elemento activo: tag={active_tag}, id={active_id}")
                        break
                    else:
                        if attempt < max_attempts - 1:
                            print(f"  Intento {attempt + 1}/{max_attempts}: Elemento activo es {active_tag} (id: {active_id}), esperando...")
                            time.sleep(0.5)
                        else:
                            print(f"  ⚠ Después de {max_attempts} intentos, el elemento activo sigue siendo {active_tag} (id: {active_id})")
                
                if active_input:
                    # Limpiar por si tiene algo
                    active_input.send_keys(Keys.CONTROL + "a")
                    time.sleep(0.1)
                    active_input.send_keys(Keys.DELETE)
                    time.sleep(0.2)
                    
                    # Escribir el username directamente
                    print(f"Escribiendo '{username}' directamente en el elemento activo...")
                    active_input.send_keys(username)
                    time.sleep(0.5)
                    
                    written = active_input.get_attribute("value")
                    print(f"Valor escrito vía active_element: '{written}'")
                    
                    if written == username:
                        print("✓ Escritura exitosa usando el elemento activo (sin selectores extra)")
                        return
                    else:
                        print(f"⚠ El elemento activo no aceptó correctamente el texto (esperado: '{username}', obtenido: '{written}'), sigo con el método largo...")
                else:
                    print("⚠ No se encontró el campo de usuario como elemento activo, sigo con el método largo...")
            except Exception as e:
                print(f"⚠ No se pudo escribir usando el elemento activo: {e}")
                # Si falla, seguimos con el flujo normal (selectores, etc.)
            
            # Verificar si hay iframes y cambiar si es necesario
            self.in_iframe = self.switch_to_iframe_if_needed()
            
            # Lista de selectores a probar en orden
            selectors_to_try = [
                ("CSS por ID", By.CSS_SELECTOR, self.selectors.FILL_USER),
                ("XPath por ID", By.XPATH, self.selectors.FILL_USER_XPATH),
                ("CSS por data-bind", By.CSS_SELECTOR, self.selectors.FILL_USER_DATABIND),
                ("XPath con atributos", By.XPATH, self.selectors.FILL_USER_XPATH_ALT),
                ("CSS por autocomplete", By.CSS_SELECTOR, self.selectors.FILL_USER_BY_AUTOCOMPLETE),
                ("XPath usando label 'for'", By.XPATH, self.selectors.USER_BY_LABEL_FOR),
            ]
            
            username_field = None
            selector_used = None
            
            # Intentar cada selector
            for name, by_type, selector in selectors_to_try:
                try:
                    print(f"Intentando selector: {name}...")
                    username_field = self.wait.until(
                        EC.presence_of_element_located((by_type, selector))
                    )
                    selector_used = name
                    print(f"✓ Campo encontrado con selector: {name}")
                    break
                except TimeoutException:
                    print(f"✗ Selector {name} no funcionó")
                    continue
            
            if not username_field:
                # Último intento: buscar cualquier input (más flexible, no solo type="text")
                print("Intentando búsqueda genérica de input (mejorada)...")
                try:
                    inputs = self.driver.find_elements(By.CSS_SELECTOR, "input")
                    print(f"Encontrados {len(inputs)} inputs en la página")
                    for inp in inputs:
                        input_type = (inp.get_attribute('type') or '').lower()
                        input_id = (inp.get_attribute('id') or '').lower()
                        placeholder = (inp.get_attribute('placeholder') or '').lower()
                        autocomplete = (inp.get_attribute('autocomplete') or '').lower()
                        print(f"  - ID: {input_id}, type: {input_type}, placeholder: {placeholder}, autocomplete: {autocomplete}")
                        if (
                            'username' in input_id
                            or 'user' in input_id
                            or 'correo' in placeholder
                            or 'email' in placeholder
                            or 'username' in autocomplete
                            or (input_type in ['text', 'email'] and ('username' in input_id or 'user' in input_id))
                        ):
                            username_field = inp
                            selector_used = "Búsqueda genérica mejorada"
                            print(f"✓ Campo encontrado por búsqueda genérica mejorada")
                            break
                except Exception as e:
                    print(f"Error en búsqueda genérica: {str(e)}")
            
            if not username_field:
                raise TimeoutException("No se pudo encontrar el campo de usuario con ningún selector")
            
            # Asegurarse de que el campo esté visible y habilitado
            print("Esperando a que el campo sea clickeable...")
            try:
                self.wait.until(EC.element_to_be_clickable(username_field))
            except:
                print("⚠ Campo no es clickeable, intentando forzar habilitación...")
                self.force_enable_field(username_field)
                # Re-buscar el campo después de clonarlo
                username_field = self.driver.find_element(By.CSS_SELECTOR, self.selectors.FILL_USER)
            
            # Verificar estado del campo
            print("\n=== DIAGNÓSTICO DEL CAMPO ===")
            print(f"Visible: {username_field.is_displayed()}")
            print(f"Habilitado: {username_field.is_enabled()}")
            print(f"Readonly: {username_field.get_attribute('readonly')}")
            print(f"Disabled: {username_field.get_attribute('disabled')}")
            print(f"Value actual: '{username_field.get_attribute('value')}'")
            print(f"ID: {username_field.get_attribute('id')}")
            
            # Verificar estilos CSS
            try:
                styles = self.driver.execute_script("""
                    var field = arguments[0];
                    var style = window.getComputedStyle(field);
                    return {
                        pointerEvents: style.pointerEvents,
                        opacity: style.opacity,
                        visibility: style.visibility,
                        display: style.display,
                        zIndex: style.zIndex
                    };
                """, username_field)
                print(f"Estilos CSS: {styles}")
            except:
                pass
            
            print("============================\n")
            
            # Verificar y remover bloqueadores
            self.check_and_remove_blockers(username_field)
            
            # Scroll al elemento si es necesario
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", username_field)
            time.sleep(0.5)
            
            # Remover atributos que puedan bloquear la escritura
            try:
                self.driver.execute_script("""
                    arguments[0].removeAttribute('autofocus');
                    arguments[0].removeAttribute('readonly');
                    arguments[0].removeAttribute('disabled');
                    arguments[0].style.pointerEvents = 'auto';
                    arguments[0].style.opacity = '1';
                """, username_field)
                print("✓ Atributos bloqueadores removidos")
            except Exception as e:
                print(f"⚠ Error al remover atributos: {str(e)}")
            
            # Intentar forzar habilitación si el campo está deshabilitado
            if not username_field.is_enabled():
                print("⚠ Campo está deshabilitado, intentando forzar habilitación...")
                self.force_enable_field(username_field)
                username_field = self.driver.find_element(By.CSS_SELECTOR, self.selectors.FILL_USER)
            
            # MÉTODO PRINCIPAL: Escritura humana letra por letra
            # Como el campo tiene autofocus, solo necesitamos escribir carácter por carácter
            print("\n[Método 1] Escribiendo letra por letra (simulación humana)...")
            try:
                import random
                from selenium.webdriver.common.keys import Keys
                
                # Verificar si el campo está realmente enfocado
                focused_element = self.driver.switch_to.active_element
                print(f"Elemento enfocado actualmente: {focused_element.tag_name if focused_element else 'None'}")
                
                # Asegurarse de que el campo esté enfocado
                print("Enfocando el campo...")
                try:
                    # Intentar múltiples métodos de enfoque
                    username_field.click()
                    time.sleep(0.1)
                    self.driver.execute_script("arguments[0].focus();", username_field)
                    time.sleep(0.1)
                    username_field.send_keys("")  # Enviar tecla vacía para forzar enfoque
                    time.sleep(0.2)
                except Exception as e:
                    print(f"⚠ Error al enfocar: {str(e)}")
                
                # Verificar enfoque nuevamente
                focused_element = self.driver.switch_to.active_element
                if focused_element != username_field:
                    print(f"⚠ El campo no está enfocado. Elemento enfocado: {focused_element.get_attribute('id') if focused_element else 'None'}")
                    # Forzar enfoque con JavaScript
                    self.driver.execute_script("arguments[0].focus(); arguments[0].click();", username_field)
                    time.sleep(0.2)
                
                # Limpiar el campo primero (por si tiene algo)
                print("Limpiando campo...")
                try:
                    username_field.send_keys(Keys.CONTROL + "a")
                    time.sleep(0.1)
                    username_field.send_keys(Keys.DELETE)
                    time.sleep(0.1)
                    username_field.clear()
                    time.sleep(0.1)
                except Exception as e:
                    print(f"⚠ Error al limpiar: {str(e)}")
                    # Intentar con JavaScript
                    self.driver.execute_script("arguments[0].value = '';", username_field)
                    time.sleep(0.2)
                
                # Verificar que el campo esté vacío
                current_value = username_field.get_attribute('value')
                print(f"Valor después de limpiar: '{current_value}'")
                
                # Escribir carácter por carácter con pausas aleatorias (como humano)
                print(f"\nEscribiendo '{username}' carácter por carácter...")
                for i, char in enumerate(username):
                    try:
                        print(f"  Escribiendo carácter {i+1}/{len(username)}: '{char}'", end='\r')
                        username_field.send_keys(char)
                        # Pausa aleatoria entre 0.05 y 0.15 segundos (simula velocidad humana)
                        pause_time = random.uniform(0.05, 0.15)
                        time.sleep(pause_time)
                        
                        # Verificar después de cada carácter (solo los primeros 3 para no ser muy lento)
                        if i < 3:
                            check_value = username_field.get_attribute('value')
                            if check_value and len(check_value) > 0:
                                print(f"\n  ✓ Caracteres escritos hasta ahora: '{check_value}'")
                    except Exception as e:
                        print(f"\n  ✗ Error al escribir carácter '{char}': {str(e)}")
                        # Intentar con JavaScript para este carácter
                        self.driver.execute_script("""
                            arguments[0].value += arguments[1];
                            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                        """, username_field, char)
                
                print()  # Nueva línea después del progreso
                
                # Pequeña pausa final
                time.sleep(0.3)
                
                # Verificar que se escribió correctamente
                written_value = username_field.get_attribute('value')
                print(f"\nValor final en el campo: '{written_value}'")
                print(f"Valor esperado: '{username}'")
                
                if written_value == username:
                    print(f"✓ Escritura exitosa - Valor: '{written_value}'")
                    time.sleep(0.5)
                    return  # Éxito, salir del método
                else:
                    print(f"⚠ Valor escrito no coincide. Diferencia: {len(username) - len(written_value) if written_value else len(username)} caracteres")
                    # Intentar una vez más con método alternativo
                    raise Exception(f"Valor no coincide: '{written_value}' != '{username}'")
                    
            except Exception as e:
                print(f"\n✗ Error con escritura letra por letra: {str(e)}")
                print("Intentando método alternativo con JavaScript...")
                
                # MÉTODO ALTERNATIVO: JavaScript directo con eventos
                try:
                    import random
                    print("\n[Método 2] JavaScript directo con eventos de teclado...")
                    
                    # Limpiar primero
                    self.driver.execute_script("arguments[0].value = '';", username_field)
                    self.driver.execute_script("arguments[0].focus();", username_field)
                    time.sleep(0.2)
                    
                    # Escribir carácter por carácter usando JavaScript pero disparando eventos reales
                    for i, char in enumerate(username):
                        # Escribir con send_keys primero
                        username_field.send_keys(char)
                        # Disparar eventos JavaScript adicionales
                        self.driver.execute_script("""
                            var field = arguments[0];
                            var char = arguments[1];
                            field.dispatchEvent(new KeyboardEvent('keydown', { key: char, bubbles: true }));
                            field.dispatchEvent(new KeyboardEvent('keypress', { key: char, bubbles: true }));
                            field.dispatchEvent(new Event('input', { bubbles: true }));
                            field.dispatchEvent(new KeyboardEvent('keyup', { key: char, bubbles: true }));
                        """, username_field, char)
                        # Pausa aleatoria
                        pause_time = random.uniform(0.05, 0.15)
                        time.sleep(pause_time)
                    
                    # Eventos finales
                    self.driver.execute_script("""
                        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                        arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
                        arguments[0].focus();
                    """, username_field)
                    time.sleep(0.3)
                    
                    # Verificar
                    written_value = username_field.get_attribute('value')
                    if written_value == username:
                        print(f"✓ Escritura exitosa con método alternativo - Valor: '{written_value}'")
                        return
                    else:
                        raise Exception(f"Valor no coincide: '{written_value}' != '{username}'")
                except Exception as e2:
                    print(f"✗ Error con método alternativo: {str(e2)}")
                    
                    # ÚLTIMO RECURSO: JavaScript puro sin eventos
                    print("\n[Método 3] Último recurso - JavaScript puro...")
                    try:
                        self.driver.execute_script("arguments[0].value = arguments[1];", username_field, username)
                        self.driver.execute_script("arguments[0].focus();", username_field)
                        time.sleep(0.5)
                        written_value = self.driver.execute_script("return arguments[0].value;", username_field)
                        if written_value == username:
                            print(f"✓ Escritura exitosa con JavaScript puro - Valor: '{written_value}'")
                            return
                        else:
                            raise Exception(f"JavaScript puro también falló: '{written_value}' != '{username}'")
                    except Exception as e3:
                        print(f"✗ Error con JavaScript puro: {str(e3)}")
            
            # Si todos los métodos fallaron, lanzar excepción con información detallada
            final_value = username_field.get_attribute('value')
            print(f"\n✗ ERROR: No se pudo escribir en el campo con ningún método")
            print(f"Valor final en el campo: '{final_value}'")
            print(f"Valor esperado: '{username}'")
            raise Exception(f"No se pudo escribir '{username}' en el campo. Valor actual: '{final_value}'")
            
        except TimeoutException as e:
            print(f"\n✗ Error: No se pudo encontrar el campo de usuario")
            print(f"Selectores probados: {[s[0] for s in selectors_to_try]}")
            print(f"URL actual: {self.driver.current_url}")
            
            # Intentar hacer screenshot para debugging
            try:
                screenshot_path = "error_screenshot.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"Screenshot guardado en: {screenshot_path}")
            except:
                pass
            
            # Si estábamos en un iframe, mantener el contexto para debugging
            # No cambiar aquí porque puede ser necesario para el siguiente paso
            
            raise
    
    def click_next_button(self):
        """Hace clic en el botón Siguiente"""
        try:
            print("Haciendo clic en el botón Siguiente...")
            # Si estamos en un iframe, buscar el botón ahí, si no, en contenido principal
            try:
                next_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, self.selectors.NEXT_SIGNIN_BUTTON_XPATH))
                )
            except TimeoutException:
                # Intentar con selector CSS alternativo
                next_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors.NEXT_SIGNIN_BUTTON))
                )
            
            # Scroll al botón si es necesario
            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(0.3)
            
            next_button.click()
            time.sleep(2)  # Esperar a que aparezca el campo de contraseña
        except TimeoutException:
            print("Error: No se pudo encontrar el botón Siguiente")
            print(f"¿Estamos en iframe? {self.in_iframe}")
            raise
    
    def fill_password(self, password: str):
        """
        Llena el campo de contraseña
        
        Args:
            password: Contraseña del usuario
        """
        try:
            print("Llenando campo de contraseña...")
            password_field = self.wait.until(
                EC.presence_of_element_located((By.XPATH, self.selectors.FILL_PASSWORD_XPATH))
            )
            
            # Asegurarse de que el campo esté visible y habilitado
            self.wait.until(EC.element_to_be_clickable(password_field))
            
            # Scroll al elemento
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", password_field)
            time.sleep(0.3)
            
            # Remover autofocus si existe
            try:
                self.driver.execute_script("arguments[0].removeAttribute('autofocus');", password_field)
            except:
                pass
            
            # Enfocar el campo
            try:
                password_field.click()
                time.sleep(0.2)
            except:
                self.driver.execute_script("arguments[0].focus();", password_field)
                time.sleep(0.2)
            
            # Limpiar y escribir la contraseña
            self.driver.execute_script("arguments[0].value = '';", password_field)
            time.sleep(0.2)
            password_field.send_keys(password)
            time.sleep(0.5)
            
        except TimeoutException:
            print("Error: No se pudo encontrar el campo de contraseña")
            raise
    
    def click_connect_button(self):
        """Hace clic en el botón Conectar"""
        try:
            print("Haciendo clic en el botón Conectar...")
            connect_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, self.selectors.CONNECT_BUTTON_XPATH))
            )
            connect_button.click()
            time.sleep(5)  # Esperar a que se complete el login
        except TimeoutException:
            print("Error: No se pudo encontrar el botón Conectar")
            raise
    
    def verify_login_success(self) -> bool:
        """
        Verifica si el login fue exitoso buscando el título "My Classes"
        
        Returns:
            True si el login fue exitoso, False en caso contrario
        """
        try:
            print("Verificando si el login fue exitoso...")
            my_classes = self.wait.until(
                EC.presence_of_element_located((By.XPATH, self.selectors.MY_CLASSES_TITLE_XPATH))
            )
            print("✓ Login exitoso - Se encontró 'My Classes'")
            return True
        except TimeoutException:
            print("⚠ Advertencia: No se pudo verificar el login (puede que aún esté cargando)")
            return False
    
    def login(self, username: str, password: str) -> bool:
        """
        Ejecuta el proceso completo de login
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            True si el login fue exitoso, False en caso contrario
        """
        try:
            self.navigate_to_landing_page()
            self.hover_sign_in()
            self.click_student_signin()
            self.fill_username(username)
            self.click_next_button()
            self.fill_password(password)
            self.click_connect_button()
            return self.verify_login_success()
        except Exception as e:
            print(f"Error durante el proceso de login: {str(e)}")
            return False

