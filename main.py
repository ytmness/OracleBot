"""
Script principal para automatización de Oracle Academy
"""
import getpass
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from oracle_bot.login_handler import LoginHandler
from oracle_bot.class_handler import ClassHandler, ClassInfo, SectionInfo


def setup_driver(headless: bool = False) -> webdriver.Chrome:
    """
    Configura y retorna una instancia del WebDriver de Chrome
    
    Args:
        headless: Si es True, ejecuta el navegador en modo headless
        
    Returns:
        Instancia configurada de Chrome WebDriver
    """
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Suprimir warnings de consola (opcional, comentar si necesitas ver los logs)
    chrome_options.add_argument("--log-level=3")  # Solo errores críticos
    chrome_options.add_argument("--disable-logging")  # Deshabilitar logging adicional
    
    # Preferencias para suprimir mensajes de consola
    prefs = {
        "logging": {
            "level": "SEVERE"  # Solo errores severos
        }
    }
    chrome_options.add_experimental_option('prefs', prefs)
    
    # Configurar user agent para evitar detección
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        print("Descargando/configurando ChromeDriver...")
        # Intentar obtener el driver path de forma más robusta
        driver_path = ChromeDriverManager().install()
        print(f"ChromeDriver encontrado en: {driver_path}")
        
        # Verificar que el archivo existe
        if not os.path.exists(driver_path):
            raise FileNotFoundError(f"ChromeDriver no encontrado en: {driver_path}")
        
        # Verificar que es el ejecutable correcto (no THIRD_PARTY_NOTICES)
        if 'THIRD_PARTY_NOTICES' in driver_path or not driver_path.endswith('.exe'):
            # Buscar chromedriver.exe en el mismo directorio
            driver_dir = os.path.dirname(driver_path)
            chromedriver_exe = os.path.join(driver_dir, 'chromedriver.exe')
            if os.path.exists(chromedriver_exe):
                print(f"Usando chromedriver.exe encontrado en: {chromedriver_exe}")
                driver_path = chromedriver_exe
            else:
                # Buscar en subdirectorios
                for root, dirs, files in os.walk(driver_dir):
                    if 'chromedriver.exe' in files:
                        chromedriver_exe = os.path.join(root, 'chromedriver.exe')
                        print(f"Usando chromedriver.exe encontrado en: {chromedriver_exe}")
                        driver_path = chromedriver_exe
                        break
        
        # Verificar que el archivo es ejecutable (tiene extensión .exe en Windows)
        if os.name == 'nt' and not driver_path.endswith('.exe'):
            raise FileNotFoundError(f"ChromeDriver debe ser un archivo .exe: {driver_path}")
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Ejecutar script para ocultar webdriver
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
        
        return driver
        
    except Exception as e:
        print(f"\nError al configurar ChromeDriver: {str(e)}")
        print("\nIntentando método alternativo...")
        
        # Método alternativo: usar el driver del sistema si está disponible
        try:
            # Intentar usar ChromeDriver desde PATH del sistema
            service = Service()  # Sin path, busca en PATH del sistema
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            print("✓ ChromeDriver encontrado en PATH del sistema")
            return driver
            
        except Exception as e2:
            print(f"\nError con método alternativo: {str(e2)}")
            print("\nPor favor, asegúrate de que:")
            print("1. Google Chrome está instalado")
            print("2. ChromeDriver está instalado y disponible en PATH")
            print("3. O ejecuta: pip install --upgrade webdriver-manager")
            raise


def get_credentials():
    """
    Solicita las credenciales al usuario de forma segura
    
    Returns:
        Tupla con (username, password)
    """
    print("=" * 50)
    print("Oracle Academy - Automatización de Login")
    print("=" * 50)
    print()
    
    username = input("Ingrese su nombre de usuario (email): ").strip()
    
    # Usar getpass para ocultar la contraseña mientras se escribe
    password = getpass.getpass("Ingrese su contraseña: ").strip()
    
    return username, password


def run_class_menu(driver: webdriver.Chrome, class_handler: ClassHandler):
    """
    Menú interactivo para seleccionar clases y secciones
    
    Args:
        driver: Instancia del WebDriver
        class_handler: Instancia del ClassHandler
    """
    try:
        while True:
            print("\n" + "=" * 60)
            print("MENÚ PRINCIPAL")
            print("=" * 60)
            print("1. Ver clases disponibles")
            print("2. Seleccionar clase y completar secciones")
            print("3. Salir")
            
            choice = input("\nSeleccione una opción (1-3): ").strip()
            
            if choice == "1":
                # Ver clases disponibles
                classes = class_handler.get_available_classes()
                if classes:
                    print(f"\n✓ Total de clases encontradas: {len(classes)}")
                else:
                    print("\n⚠ No se encontraron clases disponibles")
            
            elif choice == "2":
                # Seleccionar clase y completar secciones
                classes = class_handler.get_available_classes()
                
                if not classes:
                    print("\n⚠ No hay clases disponibles")
                    continue
                
                # Mostrar clases y permitir selección
                print("\n" + "=" * 60)
                print("CLASES DISPONIBLES")
                print("=" * 60)
                for cls in classes:
                    print(f"\n{cls}")
                
                try:
                    class_choice = int(input(f"\nSeleccione el número de clase (1-{len(classes)}): ").strip())
                    
                    if class_choice < 1 or class_choice > len(classes):
                        print("⚠ Selección inválida")
                        continue
                    
                    selected_class = classes[class_choice - 1]
                    
                    # Seleccionar la clase
                    if class_handler.select_class(selected_class):
                        # Obtener secciones
                        sections = class_handler.get_sections()
                        
                        if not sections:
                            print("\n⚠ No se encontraron secciones")
                            continue
                        
                        # Mostrar secciones y permitir selección
                        print("\n" + "=" * 60)
                        print("SECCIONES DISPONIBLES")
                        print("=" * 60)
                        for section in sections:
                            print(f"\n{section}")
                        
                        try:
                            section_choice = int(input(f"\nSeleccione hasta qué sección completar (1-{len(sections)}): ").strip())
                            
                            if section_choice < 1 or section_choice > len(sections):
                                print("⚠ Selección inválida")
                                continue
                            
                            # Completar secciones hasta la seleccionada
                            for i in range(section_choice):
                                # Verificar que el índice es válido
                                if i >= len(sections):
                                    print(f"\n⚠ No hay más secciones disponibles (índice {i+1} fuera de rango)")
                                    break
                                
                                section = sections[i]
                                
                                if section.is_complete:
                                    print(f"\n⏭ Sección {i+1} ya está completada, saltando...")
                                    continue
                                
                                print(f"\n{'='*60}")
                                print(f"PROCESANDO SECCIÓN {i+1}/{section_choice}: {section.title}")
                                print(f"{'='*60}")
                                
                                # Seleccionar sección
                                if class_handler.select_section(section):
                                    # Completar la sección (hacer el primer quiz)
                                    class_handler.complete_section(max_quizzes=1)
                                    
                                    # Volver a la lista de secciones
                                    if not class_handler.go_back_to_sections():
                                        print("⚠ No se pudo volver a la lista de secciones, intentando refrescar...")
                                        # Intentar refrescar la página
                                        class_handler.driver.refresh()
                                        time.sleep(3)
                                    
                                    # Refrescar la lista de secciones
                                    print("\nRefrescando lista de secciones...")
                                    sections = class_handler.get_sections()
                                    
                                    if not sections:
                                        print("⚠ No se pudieron obtener las secciones, deteniendo...")
                                        break
                                
                        except ValueError:
                            print("⚠ Por favor ingrese un número válido")
                        except KeyboardInterrupt:
                            print("\n\nOperación cancelada por el usuario")
                            break
                    
                except ValueError:
                    print("⚠ Por favor ingrese un número válido")
                except KeyboardInterrupt:
                    print("\n\nOperación cancelada por el usuario")
                    break
            
            elif choice == "3":
                print("\nSaliendo...")
                break
            
            else:
                print("⚠ Opción inválida, por favor seleccione 1, 2 o 3")
    
    except KeyboardInterrupt:
        print("\n\nProceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n✗ Error en el menú: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Función principal"""
    driver = None
    
    try:
        # Solicitar credenciales
        username, password = get_credentials()
        
        if not username or not password:
            print("Error: Usuario y contraseña son requeridos")
            return
        
        # Configurar driver
        print("\nInicializando navegador...")
        driver = setup_driver(headless=False)  # Cambiar a True para modo headless
        
        # Crear manejador de login
        login_handler = LoginHandler(driver)
        
        # Ejecutar login
        print("\nIniciando proceso de login...\n")
        success = login_handler.login(username, password)
        
        if success:
            print("\n✓ Login exitoso")
            
            # Esperar un momento para que la página se estabilice
            time.sleep(2)
            
            # Crear manejador de clases
            class_handler = ClassHandler(driver)
            
            # Navegar a la página de clases inmediatamente después del login
            print("\nNavegando a la página de clases después del login...")
            if class_handler.navigate_to_classes():
                print("✓ Navegación a clases completada")
            else:
                print("⚠ No se pudo navegar a clases, pero continuando...")
            
            # Menú interactivo para seleccionar clases y secciones
            run_class_menu(driver, class_handler)
        else:
            print("\n✗ El proceso de login no se completó correctamente")
            print("\nPresione Enter para cerrar el navegador...")
            input()
            
    except KeyboardInterrupt:
        print("\n\nProceso interrumpido por el usuario")
    except FileNotFoundError as e:
        print(f"\n✗ Error: Archivo no encontrado - {str(e)}")
        print("\nSolución:")
        print("1. Asegúrate de tener Google Chrome instalado")
        print("2. Ejecuta: pip install --upgrade webdriver-manager selenium")
        print("3. O descarga ChromeDriver manualmente desde: https://chromedriver.chromium.org/")
    except Exception as e:
        print(f"\n✗ Error inesperado: {str(e)}")
        print(f"Tipo de error: {type(e).__name__}")
        import traceback
        print("\nDetalles técnicos:")
        traceback.print_exc()
    finally:
        if driver:
            try:
                driver.quit()
                print("\nNavegador cerrado")
            except:
                pass


if __name__ == "__main__":
    main()

