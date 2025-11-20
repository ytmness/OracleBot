"""
Script de prueba para verificar selectores web
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config.selectors import Selectors
import time


def test_username_field():
    """Prueba el selector del campo de usuario"""
    print("=" * 60)
    print("PRUEBA DE SELECTOR - Campo de Usuario")
    print("=" * 60)
    
    selectors = Selectors()
    driver = None
    
    try:
        # Configurar driver
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver_path = ChromeDriverManager().install()
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 15)
        
        # Navegar directamente a la página de login (si es posible)
        # O navegar a la landing page y seguir el flujo
        print("\n1. Navegando a la página de inicio...")
        driver.get(selectors.LANDING_PAGE_URL)
        time.sleep(2)
        
        # Hacer hover sobre Sign In
        print("2. Haciendo hover sobre Sign In...")
        from selenium.webdriver.common.action_chains import ActionChains
        actions = ActionChains(driver)
        
        sign_in = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selectors.HOVER_SIGN_IN))
        )
        actions.move_to_element(sign_in).perform()
        time.sleep(1)
        
        # Clic en Student Hub Sign In
        print("3. Haciendo clic en Student Hub Sign In...")
        student_signin = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selectors.STUDENT_SIGNIN_REDIRECTION))
        )
        student_signin.click()
        time.sleep(3)
        
        # Probar selectores del campo de usuario
        print("\n4. Probando selectores del campo de usuario...")
        
        selectors_to_test = [
            ("CSS por ID", By.CSS_SELECTOR, selectors.FILL_USER),
            ("XPath por ID", By.XPATH, selectors.FILL_USER_XPATH),
            ("XPath con atributos", By.XPATH, selectors.FILL_USER_XPATH_ALT),
            ("CSS por autocomplete", By.CSS_SELECTOR, selectors.FILL_USER_BY_AUTOCOMPLETE),
        ]
        
        found = False
        for name, by_type, selector in selectors_to_test:
            try:
                element = wait.until(
                    EC.presence_of_element_located((by_type, selector))
                )
                print(f"✓ {name}: ENCONTRADO")
                print(f"  - Visible: {element.is_displayed()}")
                print(f"  - Habilitado: {element.is_enabled()}")
                print(f"  - Tipo: {element.get_attribute('type')}")
                print(f"  - ID: {element.get_attribute('id')}")
                print(f"  - Autocomplete: {element.get_attribute('autocomplete')}")
                found = True
                break
            except Exception as e:
                print(f"✗ {name}: NO ENCONTRADO - {str(e)}")
        
        if found:
            print("\n✓ El selector del campo de usuario funciona correctamente")
        else:
            print("\n✗ Ningún selector funcionó. Verifica la página actual.")
            print(f"\nURL actual: {driver.current_url}")
            print("\nPresiona Enter para ver el HTML de la página...")
            input()
            print(driver.page_source[:2000])  # Primeros 2000 caracteres
        
        print("\nPresiona Enter para cerrar...")
        input()
        
    except Exception as e:
        print(f"\n✗ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    test_username_field()

