"""
Script de diagnóstico para verificar la configuración del entorno
"""
import sys
import os
import platform


def check_python_version():
    """Verifica la versión de Python"""
    print("=" * 60)
    print("DIAGNÓSTICO DE CONFIGURACIÓN - Oracle Bot")
    print("=" * 60)
    print(f"\n✓ Python versión: {sys.version}")
    print(f"✓ Plataforma: {platform.platform()}")
    print(f"✓ Arquitectura: {platform.machine()}")
    print(f"✓ Sistema operativo: {platform.system()}")


def check_imports():
    """Verifica que las dependencias estén instaladas"""
    print("\n" + "=" * 60)
    print("VERIFICANDO DEPENDENCIAS")
    print("=" * 60)
    
    dependencies = {
        'selenium': 'selenium',
        'webdriver_manager': 'webdriver_manager'
    }
    
    missing = []
    for module_name, package_name in dependencies.items():
        try:
            __import__(module_name)
            print(f"✓ {package_name} está instalado")
        except ImportError:
            print(f"✗ {package_name} NO está instalado")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠ Faltan dependencias: {', '.join(missing)}")
        print("Ejecuta: pip install -r requirements.txt")
        return False
    return True


def check_chrome_installation():
    """Verifica si Chrome está instalado"""
    print("\n" + "=" * 60)
    print("VERIFICANDO GOOGLE CHROME")
    print("=" * 60)
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✓ Chrome encontrado en: {path}")
            chrome_found = True
            break
    
    if not chrome_found:
        print("✗ Chrome no encontrado en las ubicaciones comunes")
        print("  Por favor, asegúrate de tener Google Chrome instalado")
        return False
    
    return True


def check_webdriver_manager():
    """Verifica webdriver-manager"""
    print("\n" + "=" * 60)
    print("VERIFICANDO WEBDRIVER MANAGER")
    print("=" * 60)
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("✓ webdriver_manager importado correctamente")
        
        try:
            print("\nIntentando descargar/configurar ChromeDriver...")
            driver_path = ChromeDriverManager().install()
            print(f"✓ ChromeDriver configurado en: {driver_path}")
            
            if os.path.exists(driver_path):
                file_size = os.path.getsize(driver_path)
                print(f"✓ Archivo existe, tamaño: {file_size} bytes")
                
                # Verificar que sea ejecutable (en Windows, verificar extensión)
                if driver_path.endswith('.exe') or os.name != 'nt':
                    print("✓ Formato de archivo correcto")
                    return True
                else:
                    print("⚠ El archivo puede no ser ejecutable")
                    return False
            else:
                print("✗ El archivo no existe después de la instalación")
                return False
                
        except Exception as e:
            print(f"✗ Error al configurar ChromeDriver: {str(e)}")
            print(f"  Tipo: {type(e).__name__}")
            return False
            
    except ImportError as e:
        print(f"✗ Error al importar webdriver_manager: {str(e)}")
        return False


def main():
    """Función principal de diagnóstico"""
    check_python_version()
    
    if not check_imports():
        print("\n⚠ Por favor, instala las dependencias faltantes antes de continuar")
        return
    
    chrome_ok = check_chrome_installation()
    webdriver_ok = check_webdriver_manager()
    
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    
    if chrome_ok and webdriver_ok:
        print("\n✓ Todo está configurado correctamente!")
        print("  Puedes ejecutar: python main.py")
    else:
        print("\n⚠ Hay problemas con la configuración:")
        if not chrome_ok:
            print("  - Chrome no está instalado o no se encontró")
        if not webdriver_ok:
            print("  - Hay problemas con ChromeDriver")
        print("\nSoluciones sugeridas:")
        print("1. Reinstalar dependencias: pip install --upgrade -r requirements.txt")
        print("2. Asegurarse de tener Google Chrome instalado")
        print("3. Limpiar caché de webdriver-manager:")
        print("   - Eliminar carpeta: %USERPROFILE%\\.wdm")
        print("   - O ejecutar: python -c \"from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()\"")


if __name__ == "__main__":
    main()

