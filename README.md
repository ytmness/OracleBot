# Oracle Bot - Automatización con Selenium

Bot de automatización para Oracle Academy usando Selenium WebDriver.

## 🚨 Problema Actual

**El campo de usuario no permite escribir texto.** El cursor parpadea sobre el campo pero `send_keys()` no funciona. Se han probado múltiples métodos sin éxito.

### Síntomas:
- El campo tiene `autofocus` automático
- El cursor parpadea (campo está enfocado)
- `send_keys()` no escribe nada
- JavaScript directo tampoco funciona completamente
- No hay elementos visibles bloqueando el campo

### Métodos probados:
1. ✅ Escritura letra por letra con `send_keys()`
2. ✅ JavaScript directo con eventos
3. ✅ Actions (simulación humana)
4. ✅ JavaScript con eventos de teclado completos
5. ✅ Detección y remoción de overlays
6. ✅ Forzar habilitación del campo
7. ✅ Verificación de bloqueadores

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

## Estructura del Proyecto

```
OracleBot/
├── config/
│   ├── __init__.py
│   └── selectors.py          # Selectores CSS/XPath organizados
├── oracle_bot/
│   ├── __init__.py
│   └── login_handler.py      # Clase para manejar el login (PROBLEMA AQUÍ)
├── main.py                    # Script principal
├── check_setup.py             # Script de diagnóstico del entorno
├── test_selectors.py          # Script de prueba de selectores
├── test_writing.py            # Script de prueba de escritura
├── requirements.txt           # Dependencias del proyecto
└── README.md                  # Este archivo
```

## Información Técnica

### Selector del Campo de Usuario
- **ID**: `idcs-signin-basic-signin-form-username`
- **Selector CSS**: `#idcs-signin-basic-signin-form-username`
- **Tipo**: `<input type="text">`
- **Atributos**: `autocomplete="username"`, `autofocus=""`

### URL de Login
- **Landing Page**: https://academy.oracle.com/en/oa-web-overview.html
- **Student Hub**: https://academy.oracle.com/pls/f?p=63000

### Warnings de Consola
La página muestra múltiples warnings de "Duplicate ID fetched or added without merging" que son normales y no afectan la funcionalidad.

## Próximos Pasos

- [ ] **RESOLVER**: Problema de escritura en campo de usuario
- [ ] Implementar navegación a clases
- [ ] Implementar selección automática de clases
- [ ] Agregar logging detallado
- [ ] Agregar manejo de captchas si es necesario

## Repositorio

🔗 **GitHub**: https://github.com/ytmness/OracleBot

