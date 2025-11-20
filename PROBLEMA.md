# Problema: Campo de Usuario No Permite Escribir

## Descripción del Problema

El campo de usuario (`idcs-signin-basic-signin-form-username`) en Oracle Academy no permite escribir texto usando Selenium. El cursor parpadea sobre el campo (indicando que está enfocado), pero ningún método de escritura funciona.

## Síntomas Observados

1. ✅ El campo tiene `autofocus` automático y se enfoca correctamente
2. ✅ El cursor parpadea sobre el campo (campo está activo)
3. ❌ `send_keys()` no escribe nada en el campo
4. ❌ JavaScript directo (`field.value = 'texto'`) tampoco funciona completamente
5. ✅ No hay elementos visibles bloqueando el campo (overlays removidos)
6. ✅ El campo está habilitado (`disabled=False`, `readonly=None`)

## HTML del Campo

```html
<input id="idcs-signin-basic-signin-form-username" 
       data-idcs-placeholder-translation-id="idcs-username-placeholder" 
       type="text" 
       class="oj-sm-12 oj-form-control oj-inputtext-nocomp idcs-signin-rw-floating-input" 
       autocapitalize="none" 
       autocomplete="username" 
       spellcheck="false" 
       autofocus="" 
       placeholder="" 
       data-bind="value: username" 
       data-idcs-enable-right-click="true">
```

## Label del Campo

```html
<oj-label for="idcs-signin-basic-signin-form-username" 
          data-idcs-text-translation-id="idcs-username-label" 
          class="idcs-signin-rw-floating-input-label oj-label oj-component oj-complete" 
          id="ui-id-2">
    <div class="oj-label-group">
        <label data-oj-internal="" 
               id="ui-id-2|label" 
               class="oj-component-initnode" 
               for="idcs-signin-basic-signin-form-username">
            Nombre de usuario o correo electrónico
        </label>
    </div>
</oj-label>
```

## Métodos Probados (Todos Fallaron)

### 1. Escritura Letra por Letra
```python
for char in username:
    username_field.send_keys(char)
    time.sleep(random.uniform(0.05, 0.15))
```
**Resultado**: No escribe nada

### 2. JavaScript Directo
```python
driver.execute_script("arguments[0].value = arguments[1];", field, username)
driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", field)
```
**Resultado**: El valor se establece pero no se mantiene o no es detectado por el framework

### 3. Actions (Simulación Humana)
```python
actions = ActionChains(driver)
actions.move_to_element(field)
actions.click()
actions.send_keys_to_element(field, username)
actions.perform()
```
**Resultado**: No escribe nada

### 4. JavaScript con Eventos de Teclado
```python
for char in username:
    field.send_keys(char)
    driver.execute_script("""
        field.dispatchEvent(new KeyboardEvent('keydown', { key: char, bubbles: true }));
        field.dispatchEvent(new KeyboardEvent('keypress', { key: char, bubbles: true }));
        field.dispatchEvent(new Event('input', { bubbles: true }));
        field.dispatchEvent(new KeyboardEvent('keyup', { key: char, bubbles: true }));
    """, field, char)
```
**Resultado**: No escribe nada

### 5. Remover Atributos Bloqueadores
```python
field.removeAttribute('readonly')
field.removeAttribute('disabled')
field.removeAttribute('autofocus')
field.style.pointerEvents = 'auto'
```
**Resultado**: No cambia el comportamiento

### 6. Detección de Bloqueadores
- Verificado con `elementFromPoint()`: No hay elementos bloqueando
- Verificado z-index: No hay elementos con z-index alto bloqueando
- Overlays removidos: No hay overlays visibles

## Información Técnica

### Framework Utilizado
- **Oracle JET (oj-label, oj-inputtext)**: Framework de Oracle para componentes UI
- **Knockout.js**: `data-bind="value: username"` sugiere uso de Knockout.js
- **Vue.js**: Posible uso de Vue.js basado en `:class` y `:placeholder`

### Posibles Causas

1. **Framework de Binding**: El campo usa `data-bind="value: username"` que puede estar interceptando eventos
2. **Oracle JET**: Los componentes `oj-inputtext` pueden tener listeners personalizados
3. **Eventos Bloqueados**: Algún listener de JavaScript está bloqueando `send_keys()`
4. **Timing**: El campo puede necesitar más tiempo para inicializarse completamente
5. **Iframe**: El formulario puede estar en un iframe (verificado pero no encontrado)

## Warnings de Consola

La página muestra múltiples warnings:
- `Autofocus processing was blocked because a document already has a focused element`
- `Duplicate ID fetched or added without merging` (múltiples IDs)

Estos warnings son normales y no deberían afectar la funcionalidad.

## Archivos Relevantes

- `oracle_bot/login_handler.py`: Línea 256-550 (método `fill_username`)
- `config/selectors.py`: Selectores del campo de usuario
- `test_writing.py`: Script de prueba de escritura

## URL de la Página

- **Landing Page**: https://academy.oracle.com/en/oa-web-overview.html
- **Login Page**: https://academy.oracle.com/pls/f?p=63000 (después de hacer clic en "Student Hub Sign In")

## Próximos Pasos Sugeridos

1. Investigar cómo Oracle JET maneja los eventos de input
2. Probar interceptar y modificar los listeners de JavaScript
3. Intentar usar `execute_script` para modificar directamente el binding de Knockout.js
4. Verificar si hay algún listener de `beforeinput` o `input` que esté bloqueando
5. Probar usar `dispatchEvent` con eventos más específicos del framework Oracle

## Comandos para Reproducir

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar script principal
python main.py

# O ejecutar script de prueba de escritura
python test_writing.py
```

