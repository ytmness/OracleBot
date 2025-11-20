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
    CLASSES_PAGE_URL: str = "https://academy.oracle.com/pls/f?p=63000:100"
    CLASSES_PAGE_PATTERN: str = "63000:100"  # Patrón para detectar página de clases
    
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
    
    # Card para acceder a las clases (después del login)
    COURSE_MATERIALS_CARD: str = "div.t-Card-body"
    COURSE_MATERIALS_CARD_XPATH: str = "//div[@class='t-Card-body']//div[contains(text(), 'View course materials assigned by a faculty member')]"
    COURSE_MATERIALS_CARD_CONTAINER: str = "div.t-Card-body:has(div.t-Card-desc:contains('View course materials'))"
    
    # Card View - Lista de clases
    CARD_VIEW_ITEMS: str = "ul.a-CardView-items.a-CardView-items--grid3col"
    CARD_VIEW_ITEMS_XPATH: str = "//ul[@class='a-CardView-items a-CardView-items--grid3col']"
    
    # Card View - Items individuales
    CARD_VIEW_ITEM: str = "li.a-CardView-item"
    CARD_VIEW_ITEM_XPATH: str = "//li[@class='a-CardView-item']"
    
    # Información de clase en Card
    CLASS_TITLE: str = "h3.a-CardView-title"
    CLASS_TITLE_XPATH: str = "//h3[@class='a-CardView-title']"
    CLASS_SUBTITLE: str = "h4.a-CardView-subTitle"
    CLASS_BODY: str = "div.a-CardView-mainContent"
    
    # Botón Take Class
    TAKE_CLASS_BUTTON: str = "a.a-CardView-button.t-Button--hot"
    TAKE_CLASS_BUTTON_XPATH: str = "//a[@class='a-CardView-button t-Button--hot']//span[contains(text(), 'Take Class')]"
    
    # Secciones de clase
    SECTION_ITEM: str = "a.t-MediaList-itemWrap"
    SECTION_ITEM_XPATH: str = "//a[@class='t-MediaList-itemWrap']"
    SECTION_TITLE: str = "h3.t-MediaList-title"
    SECTION_TITLE_XPATH: str = "//h3[@class='t-MediaList-title']"
    
    # Indicador de completado (100%)
    COMPLETED_INDICATOR: str = "div:contains('100%')"
    COMPLETED_INDICATOR_XPATH: str = "//div[contains(text(), '100%')]"
    
    # Botón Save and Continue
    SAVE_AND_CONTINUE_BUTTON: str = "button#nextModButton"
    SAVE_AND_CONTINUE_BUTTON_XPATH: str = "//button[@id='nextModButton']//span[contains(text(), 'Save and Continue')]"
    
    # Mapa de progreso (Wizard Steps)
    WIZARD_STEPS: str = "ul.t-WizardSteps"
    WIZARD_STEP: str = "li.t-WizardSteps-step"
    WIZARD_STEP_COMPLETE: str = "li.t-WizardSteps-step.is-complete"
    WIZARD_STEP_ACTIVE: str = "li.t-WizardSteps-step.is-active-module"
    WIZARD_STEP_LABEL: str = "span.t-WizardSteps-label"
    
    # Botón Save Progress (en quiz)
    SAVE_PROGRESS_BUTTON: str = "button[id^='B'][data-otel-label='SAVE']"
    SAVE_PROGRESS_BUTTON_XPATH: str = "//button[@data-otel-label='SAVE']//span[contains(text(), 'Save Progress')]"
    
    # Botón Take an Assessment
    TAKE_ASSESSMENT_BUTTON: str = "a#open_assess_id"
    TAKE_ASSESSMENT_BUTTON_XPATH: str = "//a[@id='open_assess_id']//span[contains(text(), 'Take an Assessment')]"
    
    # Botón Start Quiz
    START_QUIZ_BUTTON: str = "button[data-otel-label='START']"
    START_QUIZ_BUTTON_XPATH: str = "//button[@data-otel-label='START']//span[contains(text(), 'Start')]"
    
    # Pregunta del quiz
    QUESTION_TEXT: str = "div#question-Text"
    QUESTION_HEADING: str = "h2#question-Text_heading"
    QUESTION_CONTENT: str = "div#question-Text div.t-ContentBlock-body"
    
    # Opciones de respuesta
    CHOICE_CONTAINER: str = "div.choice-Container"
    CHOICE_BUTTON: str = "button.choice-SelectArea"
    CHOICE_TEXT: str = "span.choice-Text"
    CHOICE_SELECTED: str = "button.choice-SelectArea[aria-checked='true']"
    
    # Botón Next/Submit (para avanzar después de responder)
    NEXT_QUESTION_BUTTON: str = "button[data-otel-label='NEXT']"
    SUBMIT_QUIZ_BUTTON: str = "button#quiz-submit"
    SUBMIT_QUIZ_BUTTON_XPATH: str = "//button[@id='quiz-submit']//span[contains(text(), 'Submit Answer')]"
    SUBMIT_ANSWER_BUTTON: str = "button#quiz-submit"  # Alias para claridad
    
    # Botón Complete Assessment (al final del quiz)
    COMPLETE_ASSESSMENT_BUTTON: str = "button[data-otel-label='CONFIRMCOMPLETE']"
    COMPLETE_ASSESSMENT_BUTTON_XPATH: str = "//button[@data-otel-label='CONFIRMCOMPLETE']//span[contains(text(), 'Complete Assessment')]"

