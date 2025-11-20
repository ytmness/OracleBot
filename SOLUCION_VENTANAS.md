# Problema Resuelto: Manejo de Ventanas en Automatización Web

## 📋 Contexto del Problema

**Fecha**: Enero 2025  
**Proyecto**: OracleBot - Automatización de login en Oracle Academy  
**Síntoma Principal**: El código no podía escribir en el campo de usuario aunque el cursor parpadeaba

## 🔍 Síntomas Observados

### Síntomas Iniciales (Engañosos)
- El cursor parpadeaba sobre el campo de usuario (indicaba que tenía autofocus)
- `send_keys()` no escribía nada en el campo
- JavaScript directo tampoco funcionaba
- El campo estaba visible, habilitado y sin atributos bloqueadores
- No había overlays visibles bloqueando

### Síntomas Reales (La Causa)
- **URL incorrecta**: El código reportaba estar en `https://academy.oracle.com/en/oa-web-overview.html` (landing page)
- **Elemento activo incorrecto**: `driver.switch_to.active_element` retornaba el enlace `studentsignin` (tag=a) en lugar del input
- **Múltiples ventanas**: El enlace abría una nueva ventana/pestaña pero el código seguía en la ventana original
- **URL real**: La página de login estaba en `https://signon.oracle.com/signin` en una ventana diferente

## 🎯 Causa Raíz

El enlace "Student Hub Sign In" tiene el atributo `target="_blank"`, lo que hace que se abra en una **nueva ventana/pestaña**. El código de Selenium seguía operando en la ventana original, intentando escribir en un campo que no existía en esa ventana.

### Código Problemático Original

```python
def click_student_signin(self):
    student_signin.click()
    # ❌ No verificaba si se abrió una nueva ventana
    # ❌ Seguía en la ventana original
    # ❌ Intentaba escribir en campo que no existía
```

## ✅ Solución Implementada

### 1. Detectar Apertura de Nueva Ventana

```python
# Guardar ventana actual ANTES del clic
original_window = self.driver.current_window_handle
window_count_before = len(self.driver.window_handles)

student_signin.click()
time.sleep(2)  # Esperar a que se abra la ventana

# Verificar si se abrió nueva ventana
window_count_after = len(self.driver.window_handles)
if window_count_after > window_count_before:
    # Cambiar a la nueva ventana
    for window_handle in self.driver.window_handles:
        if window_handle != original_window:
            self.driver.switch_to.window(window_handle)
            break
```

### 2. Verificar URL Correcta

```python
# Verificar que estamos en la página correcta
current_url = self.driver.current_url.lower()
is_login_page = (
    'signin' in current_url or 
    'signon.oracle.com' in current_url or
    '63000' in self.driver.current_url
)
```

### 3. Verificación Adicional en Métodos Posteriores

```python
def fill_username(self, username: str):
    # Si no estamos en la página correcta, buscar ventanas adicionales
    if not is_login_page and len(self.driver.window_handles) > 1:
        self.driver.switch_to.window(self.driver.window_handles[-1])
```

## 🔧 Cómo Detectar Este Problema en el Futuro

### Señales de Alerta

1. **URL no cambia después de un clic**
   - El código reporta estar en la misma URL después de hacer clic en un enlace
   - La URL esperada no aparece en `driver.current_url`

2. **Elemento activo incorrecto**
   - `driver.switch_to.active_element` retorna un elemento diferente al esperado
   - El elemento activo es un enlace (`tag=a`) cuando debería ser un input

3. **Selectores no encuentran elementos**
   - Todos los selectores fallan aunque el elemento existe visualmente
   - El código busca en iframes pero no encuentra nada

4. **Múltiples ventanas abiertas**
   - `len(driver.window_handles) > 1` después de hacer clic en un enlace
   - El navegador muestra múltiples pestañas abiertas

### Comandos de Diagnóstico

```python
# Verificar ventanas abiertas
print(f"Ventanas abiertas: {len(driver.window_handles)}")
for i, handle in enumerate(driver.window_handles):
    driver.switch_to.window(handle)
    print(f"  Ventana {i}: {driver.current_url}")

# Verificar elemento activo
active = driver.switch_to.active_element
print(f"Elemento activo: tag={active.tag_name}, id={active.get_attribute('id')}")

# Verificar URL actual
print(f"URL actual: {driver.current_url}")
```

## 📝 Patrones Comunes a Buscar

### En el HTML del Enlace

```html
<!-- Buscar estos atributos que abren nueva ventana -->
<a href="..." target="_blank">  <!-- ⚠️ Abre nueva ventana -->
<a href="..." target="_self">   <!-- ✅ Misma ventana -->
<a href="..." target="_parent"> <!-- ⚠️ Puede cambiar contexto -->
```

### En el Código JavaScript

```javascript
// Buscar estos métodos que pueden abrir ventanas
window.open(url, '_blank')  // ⚠️ Abre nueva ventana
window.open(url, '_self')   // ✅ Misma ventana
```

## 🛠️ Solución Genérica Reutilizable

### Función Helper para Manejar Clics que Abren Ventanas

```python
def click_and_switch_window(self, element, expected_url_keywords=None, timeout=10):
    """
    Hace clic en un elemento y cambia a la nueva ventana si se abre una.
    
    Args:
        element: WebElement en el que hacer clic
        expected_url_keywords: Lista de palabras clave que debe contener la URL esperada
        timeout: Tiempo máximo de espera en segundos
    """
    original_window = self.driver.current_window_handle
    window_count_before = len(self.driver.window_handles)
    
    element.click()
    time.sleep(2)  # Esperar a que se abra la ventana
    
    window_count_after = len(self.driver.window_handles)
    
    if window_count_after > window_count_before:
        # Cambiar a la nueva ventana
        for window_handle in self.driver.window_handles:
            if window_handle != original_window:
                self.driver.switch_to.window(window_handle)
                print(f"✓ Cambiado a nueva ventana - URL: {self.driver.current_url}")
                
                # Verificar URL si se especificaron keywords
                if expected_url_keywords:
                    current_url = self.driver.current_url.lower()
                    if any(keyword.lower() in current_url for keyword in expected_url_keywords):
                        print(f"✓ URL correcta verificada")
                    else:
                        print(f"⚠ URL no coincide con keywords esperadas")
                break
    else:
        # No se abrió nueva ventana, esperar cambio de URL
        if expected_url_keywords:
            try:
                self.wait.until(lambda driver: 
                    any(keyword.lower() in driver.current_url.lower() 
                        for keyword in expected_url_keywords))
                print(f"✓ URL cambió correctamente - {self.driver.current_url}")
            except:
                print(f"⚠ Timeout esperando cambio de URL")
    
    return self.driver.current_window_handle
```

### Uso de la Función Helper

```python
# Antes (problemático)
student_signin.click()

# Después (correcto)
self.click_and_switch_window(
    student_signin, 
    expected_url_keywords=['signin', 'signon.oracle.com']
)
```

## 🎓 Lecciones Aprendidas

1. **Siempre verificar ventanas después de clics**: Cualquier clic puede abrir una nueva ventana
2. **Verificar URL después de navegación**: No asumir que la URL cambió correctamente
3. **Usar `driver.window_handles` para diagnóstico**: Es la forma más confiable de detectar ventanas múltiples
4. **El elemento activo puede ser engañoso**: Si está en la ventana incorrecta, el elemento activo será incorrecto
5. **Los selectores fallan silenciosamente**: Si buscas en la ventana incorrecta, los elementos no existen

## 📌 Checklist para Problemas Similares

Cuando un elemento no se encuentra o no responde después de un clic:

- [ ] ¿Se abrió una nueva ventana? (`len(driver.window_handles) > 1`)
- [ ] ¿Estamos en la ventana correcta? (`driver.current_window_handle`)
- [ ] ¿La URL es la esperada? (`driver.current_url`)
- [ ] ¿El elemento activo es el correcto? (`driver.switch_to.active_element`)
- [ ] ¿El enlace tiene `target="_blank"`? (revisar HTML)
- [ ] ¿Hay JavaScript que abre ventanas? (`window.open`)

## 🔗 Referencias

- **Archivo donde se implementó**: `oracle_bot/login_handler.py`
- **Método corregido**: `click_student_signin()` (línea ~105)
- **Método que usa la solución**: `fill_username()` (línea ~398)
- **Commit**: "Detectar y cambiar a nueva ventana cuando se abre signon.oracle.com"

## 💡 Prompt para Asistente IA Futuro

Si encuentras un problema donde:
- Los selectores no encuentran elementos después de un clic
- La URL no cambia como se espera
- El elemento activo es incorrecto
- `send_keys()` no funciona aunque el campo parece estar enfocado

**Pregunta primero**: ¿Se abrió una nueva ventana/pestaña? Verifica con:
```python
print(f"Ventanas: {len(driver.window_handles)}")
print(f"URL actual: {driver.current_url}")
print(f"Elemento activo: {driver.switch_to.active_element.tag_name}")
```

Si hay múltiples ventanas, cambia a la correcta antes de intentar interactuar con elementos.

