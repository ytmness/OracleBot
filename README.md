# Oracle Bot - Automatización con Selenium

Bot de automatización para Oracle Academy usando Selenium WebDriver.

## Instalación

1. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

2. Verificar la configuración (recomendado):
```bash
python check_setup.py
```

Este script verificará:
- Versión de Python
- Dependencias instaladas
- Instalación de Google Chrome
- Configuración de ChromeDriver

## Uso

Ejecutar el script principal:
```bash
python main.py
```

El script solicitará:
- Nombre de usuario (email)
- Contraseña (se oculta mientras se escribe)

## Solución de Problemas

### Error: [WinError 193] %1 no es una aplicación Win32 válida

Este error generalmente ocurre cuando hay problemas con ChromeDriver. Soluciones:

1. **Ejecutar diagnóstico:**
   ```bash
   python check_setup.py
   ```

2. **Reinstalar dependencias:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Limpiar caché de webdriver-manager:**
   - Eliminar la carpeta: `%USERPROFILE%\.wdm`
   - O ejecutar manualmente:
   ```bash
   python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
   ```

4. **Verificar que Chrome esté instalado:**
   - Asegúrate de tener Google Chrome instalado en tu sistema
   - El bot necesita Chrome para funcionar

5. **Instalar ChromeDriver manualmente (último recurso):**
   - Descargar desde: https://chromedriver.chromium.org/
   - Colocar el ejecutable en una carpeta del PATH del sistema

## Estructura del Proyecto

```
OracleBot/
├── config/
│   ├── __init__.py
│   └── selectors.py          # Selectores CSS/XPath organizados
├── oracle_bot/
│   ├── __init__.py
│   └── login_handler.py      # Clase para manejar el login
├── main.py                    # Script principal
├── requirements.txt           # Dependencias del proyecto
└── README.md                  # Este archivo
```

## Características

- Login automatizado en Oracle Academy
- Verificación de login exitoso
- Manejo de errores y timeouts
- Interfaz de línea de comandos para credenciales
- Modo headless disponible (configurable en main.py)

## Próximos Pasos

- [ ] Implementar navegación a clases
- [ ] Implementar selección automática de clases
- [ ] Agregar logging detallado
- [ ] Agregar manejo de captchas si es necesario

