"""
Selectores web para Oracle Academy
"""
from dataclasses import dataclass


@dataclass
class Selectors:
    """Clase que contiene todos los selectores CSS/XPath para Oracle Academy"""
    
    # URLs
    LANDING_PAGE_URL: str = "https://academy.oracle.com/en/oa-web-overview.html"
    STUDENT_HUB_URL: str = "https://academy.oracle.com/pls/f?p=63000"
    
    # Login - Hover Sign In
    HOVER_SIGN_IN: str = "a.u02user[href='#usermenu']"
    HOVER_SIGN_IN_XPATH: str = "//a[@href='#usermenu' and contains(@class, 'u02user')]"
    
    # Login - Redirección Student Hub
    STUDENT_SIGNIN_REDIRECTION: str = "a.oastudenthuburl#studentsignin"
    STUDENT_SIGNIN_REDIRECTION_XPATH: str = "//a[@id='studentsignin' and contains(@class, 'oastudenthuburl')]"
    
    # Login - Formulario de usuario
    # Selector principal por ID (más confiable)
    FILL_USER: str = "#idcs-signin-basic-signin-form-username"
    FILL_USER_XPATH: str = "//input[@id='idcs-signin-basic-signin-form-username']"
    # Selectores alternativos por atributos
    FILL_USER_XPATH_ALT: str = "//input[@id='idcs-signin-basic-signin-form-username' and @type='text' and @autocomplete='username']"
    FILL_USER_BY_AUTOCOMPLETE: str = "input[autocomplete='username'][type='text']"
    # Selector alternativo por data-bind (más robusto si cambia el ID)
    FILL_USER_DATABIND: str = "input[data-bind*='value: username']"
    # Label del campo de usuario (para verificación)
    USER_LABEL: str = "oj-label[for='idcs-signin-basic-signin-form-username']"
    USER_LABEL_XPATH: str = "//oj-label[@for='idcs-signin-basic-signin-form-username']"
    # Método alternativo: encontrar input usando el label
    USER_BY_LABEL_FOR: str = "//label[@for='idcs-signin-basic-signin-form-username']/following::input[1] | //oj-label[@for='idcs-signin-basic-signin-form-username']/following::input[1]"
    
    # Login - Botón Siguiente
    NEXT_SIGNIN_BUTTON: str = "button.oj-button-button[aria-labelledby='ui-id-3']"
    NEXT_SIGNIN_BUTTON_XPATH: str = "//button[@aria-labelledby='ui-id-3']//span[contains(text(), 'Siguiente')]"
    
    # Login - Campo de contraseña
    FILL_PASSWORD: str = "#idcs-auth-pwd-input|input"
    FILL_PASSWORD_XPATH: str = "//input[@id='idcs-auth-pwd-input|input' and @type='password']"
    
    # Login - Botón Conectar
    CONNECT_BUTTON: str = "button.oj-button-button[aria-labelledby='ui-id-2']"
    CONNECT_BUTTON_XPATH: str = "//button[@aria-labelledby='ui-id-2']//span[contains(text(), 'Conectar')]"
    
    # Verificación de clases
    MY_CLASSES_TITLE: str = "h3.t-Card-title"
    MY_CLASSES_TITLE_XPATH: str = "//h3[@class='t-Card-title' and contains(text(), 'My Classes')]"
    
    # Card View - Lista de clases
    CARD_VIEW_ITEMS: str = "ul.a-CardView-items.a-CardView-items--grid3col"
    CARD_VIEW_ITEMS_XPATH: str = "//ul[@class='a-CardView-items a-CardView-items--grid3col']"
    
    # Card View - Items individuales
    CARD_VIEW_ITEM: str = "li.a-CardView-item"
    CARD_VIEW_ITEM_XPATH: str = "//li[@class='a-CardView-item']"
    
    # Botón Take Class
    TAKE_CLASS_BUTTON: str = "a.a-CardView-button.t-Button--hot"
    TAKE_CLASS_BUTTON_XPATH: str = "//a[@class='a-CardView-button t-Button--hot']//span[contains(text(), 'Take Class')]"

