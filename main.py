"""
Script principal para automatización de Oracle Academy
"""
import getpass
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from oracle_bot.login_handler import LoginHandler


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
            print("\n✓ Proceso completado exitosamente")
            print("\nPresione Enter para cerrar el navegador...")
            input()
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

