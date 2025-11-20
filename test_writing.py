"""
Script de diagnóstico para probar la escritura en el campo de usuario
"""
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from config.selectors import Selectors
import time


def setup_driver():
    """Configura el driver de Chrome"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver_path = ChromeDriverManager().install()
    # Buscar chromedriver.exe si es necesario
    if 'THIRD_PARTY_NOTICES' in driver_path or not driver_path.endswith('.exe'):
        import os
        driver_dir = os.path.dirname(driver_path)
        chromedriver_exe = os.path.join(driver_dir, 'chromedriver.exe')
        if os.path.exists(chromedriver_exe):
            driver_path = chromedriver_exe
    
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def test_writing():
    """Prueba diferentes métodos de escritura"""
    print("=" * 60)
    print("DIAGNÓSTICO DE ESCRITURA EN CAMPO DE USUARIO")
    print("=" * 60)
    
    driver = None
    try:
        username = input("\nIngrese su nombre de usuario para probar: ").strip()
        if not username:
            username = "test@example.com"
            print(f"Usando usuario de prueba: {username}")
        
        driver = setup_driver()
        wait = WebDriverWait(driver, 20)
        selectors = Selectors()
        
        # Navegar a la página
        print("\n1. Navegando a la página de inicio...")
        driver.get(selectors.LANDING_PAGE_URL)
        time.sleep(2)
        
        # Hacer hover y clic en Student Hub
        print("2. Navegando al formulario de login...")
        from selenium.webdriver.common.action_chains import ActionChains
        actions = ActionChains(driver)
        
        sign_in = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selectors.HOVER_SIGN_IN))
        )
        actions.move_to_element(sign_in).perform()
        time.sleep(1)
        
        student_signin = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selectors.STUDENT_SIGNIN_REDIRECTION))
        )
        student_signin.click()
        time.sleep(5)
        
        # Buscar el campo
        print("\n3. Buscando el campo de usuario...")
        username_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selectors.FILL_USER))
        )
        
        print("\n=== INFORMACIÓN DEL CAMPO ===")
        print(f"Visible: {username_field.is_displayed()}")
        print(f"Habilitado: {username_field.is_enabled()}")
        print(f"Readonly: {username_field.get_attribute('readonly')}")
        print(f"Disabled: {username_field.get_attribute('disabled')}")
        print(f"ID: {username_field.get_attribute('id')}")
        print(f"Type: {username_field.get_attribute('type')}")
        print(f"Value inicial: '{username_field.get_attribute('value')}'")
        print("============================\n")
        
        # Scroll al campo
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", username_field)
        time.sleep(1)
        
        # Remover atributos bloqueadores
        driver.execute_script("""
            arguments[0].removeAttribute('autofocus');
            arguments[0].removeAttribute('readonly');
            arguments[0].removeAttribute('disabled');
        """, username_field)
        
        # MÉTODO 1: JavaScript directo
        print("\n[MÉTODO 1] JavaScript directo...")
        try:
            driver.execute_script("""
                var field = arguments[0];
                var value = arguments[1];
                field.value = '';
                field.focus();
                field.value = value;
                field.dispatchEvent(new Event('input', { bubbles: true }));
                field.dispatchEvent(new Event('change', { bubbles: true }));
            """, username_field, username)
            time.sleep(1)
            value = driver.execute_script("return arguments[0].value;", username_field)
            print(f"  Resultado: '{value}'")
            if value == username:
                print("  ✓ ÉXITO")
            else:
                print("  ✗ FALLÓ")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
        
        # Limpiar para siguiente prueba
        driver.execute_script("arguments[0].value = '';", username_field)
        time.sleep(0.5)
        
        # MÉTODO 2: Click + Clear + Send Keys
        print("\n[MÉTODO 2] Click + Clear + Send Keys...")
        try:
            username_field.click()
            time.sleep(0.2)
            username_field.clear()
            time.sleep(0.2)
            username_field.send_keys(Keys.CONTROL + "a")
            username_field.send_keys(Keys.DELETE)
            time.sleep(0.2)
            username_field.send_keys(username)
            time.sleep(1)
            value = username_field.get_attribute('value')
            print(f"  Resultado: '{value}'")
            if value == username:
                print("  ✓ ÉXITO")
            else:
                print("  ✗ FALLÓ")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
        
        # Limpiar para siguiente prueba
        driver.execute_script("arguments[0].value = '';", username_field)
        time.sleep(0.5)
        
        # MÉTODO 3: Actions
        print("\n[MÉTODO 3] Actions (simulación humana)...")
        try:
            actions = ActionChains(driver)
            actions.move_to_element(username_field)
            actions.click()
            actions.pause(0.2)
            actions.send_keys_to_element(username_field, username)
            actions.perform()
            time.sleep(1)
            value = username_field.get_attribute('value')
            print(f"  Resultado: '{value}'")
            if value == username:
                print("  ✓ ÉXITO")
            else:
                print("  ✗ FALLÓ")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
        
        # Limpiar para siguiente prueba
        driver.execute_script("arguments[0].value = '';", username_field)
        time.sleep(0.5)
        
        # MÉTODO 4: JavaScript con eventos de teclado
        print("\n[MÉTODO 4] JavaScript con eventos de teclado...")
        try:
            driver.execute_script("""
                var field = arguments[0];
                var value = arguments[1];
                field.value = '';
                field.focus();
                for (var i = 0; i < value.length; i++) {
                    field.value += value[i];
                    field.dispatchEvent(new Event('input', { bubbles: true }));
                }
                field.dispatchEvent(new Event('change', { bubbles: true }));
            """, username_field, username)
            time.sleep(1)
            value = driver.execute_script("return arguments[0].value;", username_field)
            print(f"  Resultado: '{value}'")
            if value == username:
                print("  ✓ ÉXITO")
            else:
                print("  ✗ FALLÓ")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
        
        print("\n" + "=" * 60)
        print("DIAGNÓSTICO COMPLETADO")
        print("=" * 60)
        print("\nPresiona Enter para cerrar el navegador...")
        input()
        
    except Exception as e:
        print(f"\n✗ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    test_writing()

