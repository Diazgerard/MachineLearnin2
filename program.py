import json
import os
import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import win32gui
import win32con
import keyboard
import time
import tensorflow as tf
import random

# --- Configuración de las acciones del teclado ---
actions = {
    "Copiar": lambda: keyboard.send("ctrl+c"),                 # 0
    "Pegar": lambda: keyboard.send("ctrl+v"),                  # 1
    "Desahacer": lambda: keyboard.send("ctrl+z"),              # 2
    "Rehacer": lambda: keyboard.send("ctrl+y"),                # 3
    "Screenshot": lambda: pyautogui.screenshot("screenshot.png"), # 4
    "Screenshot Portapeles": lambda: keyboard.send("print screen"), # 5
    "Cambiar Ventana": lambda: keyboard.send("alt+tab"),       # 6
    "Buscar": lambda: keyboard.send("ctrl+f"),                 # 7
    "Nueva Pestaña": lambda: keyboard.send("ctrl+t"),          # 8
    "Cerrar Pestaña": lambda: keyboard.send("ctrl+w"),         # 9
    "Subir Volumen": lambda: keyboard.send("volume up"),       # 10
    "Bajar Volumen": lambda: keyboard.send("volume down"),     # 11
    "Silenciar": lambda: keyboard.send("volume mute"),         # 12
    "Abrir Bloc": lambda: os.system("notepad"),                # 13
    "Abrir Calculadora": lambda: os.system("calc"),            # 14
    "Abrir Explorador": lambda: os.system("explorer"),         # 15
    "Escribir Texto": lambda: pyautogui.typewrite("Hola desde IA!"), # 16
    "Refrescar": lambda: pyautogui.press("f5"),                # 17
    "Borrar": lambda: pyautogui.press("delete"),               # 18
    "Scroll Arriba": lambda: pyautogui.scroll(500),            # 19
    "Scroll Abajo": lambda: pyautogui.scroll(-500),            # 20
    "Abrir Chrome": lambda: os.system("start chrome"),         # 21
    "Abrir Excel": lambda: os.system("start excel"),           # 22
    "Presionar ESC": lambda: pyautogui.press('escape'),        # 23
    "Abrir Word": lambda: os.system("start winword")           # 24
}

# --- Cargar configuración desde archivo JSON ----
def load_gesture_config():
    """Carga la configuración de gestos desde el archivo JSON"""
    try:
        with open("configuracion_gestos.json", "r", encoding='utf-8') as f:
            data = json.load(f)
        
        # Verificar si es el formato nuevo (con secciones) o antiguo (solo comandos)
        if isinstance(data, dict) and 'comandos' in data:
            # Formato nuevo con información detallada
            config = data['comandos']
            print("🔧 CONFIGURACIÓN CARGADA (formato detallado):")
            print(f"📅 Fecha de creación: {data.get('info', {}).get('fecha_creacion', 'No disponible')}")
            print(f"📊 Total de comandos: {data.get('info', {}).get('total_configurados', len(config))}")
            print("📋 Mappings letra → comando:")
            
            # Mostrar detalles si están disponibles
            if 'detalles' in data:
                for num_str, details in data['detalles'].items():
                    letra = details.get('letra', chr(int(num_str) + ord('A')))
                    comando = details.get('comando', config.get(num_str, 'Desconocido'))
                    print(f"   🔤 {letra} (#{num_str}) → {comando}")
            else:
                # Si no hay detalles, mostrar formato básico
                for num_str, comando in config.items():
                    letra = chr(int(num_str) + ord('A'))
                    print(f"   🔤 {letra} (#{num_str}) → {comando}")
        else:
            # Formato antiguo (solo comandos)
            config = data
            print("🔧 CONFIGURACIÓN CARGADA (formato básico):")
            print(f"📊 Total de comandos: {len(config)}")
            print("📋 Mappings letra → comando:")
            for num_str, comando in config.items():
                letra = chr(int(num_str) + ord('A'))
                print(f"   🔤 {letra} (#{num_str}) → {comando}")
        
        print("=" * 50)
        
        # --- CONFIGURACIÓN FORZADA: ESC siempre en posición 23 ---
        config["23"] = "Presionar ESC"
        print("🔒 CONFIGURACIÓN PROTEGIDA: X (#23) → Presionar ESC (FIJO)")
        
        return config
        
    except FileNotFoundError:
        print("⚠️  Archivo configuracion_gestos.json no encontrado")
        print("💡 Usa app.py para crear la configuración")
        # Crear configuración mínima con ESC protegido
        config = {"23": "Presionar ESC"}
        print("🔒 CONFIGURACIÓN MÍNIMA: X (#23) → Presionar ESC (FIJO)")
        return config
    except json.JSONDecodeError as e:
        print(f"❌ Error al leer JSON: {e}")
        # Crear configuración mínima con ESC protegido
        config = {"23": "Presionar ESC"}
        print("🔒 CONFIGURACIÓN MÍNIMA: X (#23) → Presionar ESC (FIJO)")
        return config
    except Exception as e:
        print(f"❌ Error inesperado al cargar configuración: {e}")
        # Crear configuración mínima con ESC protegido
        config = {"23": "Presionar ESC"}
        print("🔒 CONFIGURACIÓN MÍNIMA: X (#23) → Presionar ESC (FIJO)")
        return config

# Cargar la configuración
config = load_gesture_config()

# --- Variables globales para recomendaciones ---
recommendation_windows = []
current_recommendations = []
last_recommendation_update = 0
RECOMMENDATION_UPDATE_INTERVAL = 5  # Actualizar cada 5 segundos
last_detected_gesture = None  # Para rastrear cuando cambia la seña detectada

def create_recommendation_panels():
    """Crear paneles de recomendaciones con imágenes ASL"""
    global current_recommendations
    
    # Obtener 2 comandos aleatorios de la configuración
    if len(config) >= 2:
        available_configs = list(config.items())
        selected = random.sample(available_configs, 2)
        current_recommendations = selected
        
        # Crear paneles de recomendaciones
        recommendation_windows.clear()
        for i, (class_id, command) in enumerate(selected):
            letter = chr(int(class_id) + ord('A'))
            panel = create_recommendation_panel(letter, command, i)
            if panel is not None:
                recommendation_windows.append(panel)

def create_recommendation_panel(letter, command, index):
    """Crear un panel individual de recomendación"""
    try:
        # Cargar imagen de la seña
        current_dir = os.path.dirname(os.path.abspath(__file__))
        signs_dir = os.path.join(current_dir, "Sign_Images")
        image_path = os.path.join(signs_dir, f"{letter}.jpeg")
        
        if not os.path.exists(image_path):
            return None
            
        # Cargar y redimensionar imagen
        sign_image = cv2.imread(image_path)
        if sign_image is None:
            return None
            
        # Redimensionar imagen para que sea más compacta horizontalmente
        sign_image = cv2.resize(sign_image, (120, 120))
        
        # Crear panel más estrecho para disposición horizontal
        panel_height = 180
        panel_width = 160
        panel = np.zeros((panel_height, panel_width, 3), dtype=np.uint8)
        panel.fill(40)  # Fondo gris oscuro
        
        # Agregar imagen en la parte superior (centrada)
        img_start_x = (panel_width - 120) // 2
        panel[10:130, img_start_x:img_start_x+120] = sign_image
        
        # Agregar texto - Letra (centrado)
        text_size = cv2.getTextSize(f"Letra: {letter}", cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        text_x = (panel_width - text_size[0]) // 2
        cv2.putText(panel, f"Letra: {letter}", (text_x, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Agregar texto - Comando (centrado y dividido si es necesario)
        if len(command) > 12:
            command_line1 = command[:12]
            command_line2 = command[12:]
            
            text1_size = cv2.getTextSize(command_line1, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
            text1_x = (panel_width - text1_size[0]) // 2
            cv2.putText(panel, command_line1, (text1_x, 165), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
            
            text2_size = cv2.getTextSize(command_line2, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
            text2_x = (panel_width - text2_size[0]) // 2
            cv2.putText(panel, command_line2, (text2_x, 175), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        else:
            text_size = cv2.getTextSize(command, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            text_x = (panel_width - text_size[0]) // 2
            cv2.putText(panel, command, (text_x, 170), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        return panel
        
    except Exception as e:
        print(f"Error creando panel para {letter}: {e}")
        return None

def update_recommendation_panels_on_gesture(detected_gesture):
    """Actualizar los paneles solo cuando se detecta una nueva seña"""
    global last_detected_gesture, recommendation_windows, current_recommendations
    
    # Solo actualizar si se detectó una seña diferente
    if detected_gesture != last_detected_gesture:
        print(f"🔄 Nueva seña detectada: {detected_gesture}, actualizando recomendaciones...")
        
        # Limpiar ventanas anteriores
        recommendation_windows.clear()
        
        # Crear nuevas recomendaciones
        create_recommendation_panels()
        last_detected_gesture = detected_gesture

def show_recommendation_panels():
    """Mostrar los paneles de recomendaciones en pantalla horizontalmente"""
    if len(recommendation_windows) >= 2:
        # Posición horizontal: cámara (420px) → recomendación 1 → recomendación 2
        
        # Mostrar primer panel (inmediatamente al lado de la cámara)
        cv2.imshow('Recomendacion 1', recommendation_windows[0])
        cv2.moveWindow('Recomendacion 1', 430, 0)  # Al lado de la cámara
        
        # Mostrar segundo panel (al lado de la primera recomendación)
        cv2.imshow('Recomendacion 2', recommendation_windows[1])
        cv2.moveWindow('Recomendacion 2', 600, 0)  # Al lado de la recomendación 1
        
        # Mantener ventanas al frente
        set_window_always_on_top('Recomendacion 1')
        set_window_always_on_top('Recomendacion 2')

# --- Cargar modelo entrenado ---
gesture_model = tf.keras.models.load_model('models/asl_alphabet_model.h5')
print("Modelo EfficientNetB5 cargado exitosamente")


# --- Configuración ---
RECT_WIDTH = 160
RECT_HEIGHT = 100
COLOR_MOUSE_POINTER = (255, 0, 255)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

EXEC_COOLDOWN = 5.0

# --- Funciones auxiliares ---
def calculate_distance(x1, y1, x2, y2):
    p1, p2 = np.array([x1, y1]), np.array([x2, y2])
    return np.linalg.norm(p1 - p2)


def detect_finger_down(hand_landmarks, width, height, output):
    """Detecta si el dedo índice está abajo (para click)."""
    finger_down = False
    color_base, color_index = (255, 0, 112), (255, 198, 82)

    # Coordenadas base y dedo índice
    x_base1, y_base1 = int(hand_landmarks.landmark[0].x * width), int(hand_landmarks.landmark[0].y * height)
    x_base2, y_base2 = int(hand_landmarks.landmark[9].x * width), int(hand_landmarks.landmark[9].y * height)
    x_index, y_index = int(hand_landmarks.landmark[8].x * width), int(hand_landmarks.landmark[8].y * height)

    # Distancias
    d_base = calculate_distance(x_base1, y_base1, x_base2, y_base2)
    d_base_index = calculate_distance(x_base1, y_base1, x_index, y_index)

    # Si el índice está abajo
    if d_base_index < d_base:
        finger_down = True
        color_base = color_index = (255, 0, 255)

    # Dibujos
    cv2.circle(output, (x_base1, y_base1), 5, color_base, 2)
    cv2.circle(output, (x_index, y_index), 5, color_index, 2)
    cv2.line(output, (x_base1, y_base1), (x_base2, y_base2), color_base, 3)
    cv2.line(output, (x_base1, y_base1), (x_index, y_index), color_index, 3)

    return finger_down


def process_hand_right(hand_landmarks, frame, width, height):
    """Controla el mouse si es la derecha."""
    output = frame.copy()

    # Rectángulo de control
    x_ini, y_ini = width - RECT_WIDTH - 50, height - RECT_HEIGHT - 50
    cv2.rectangle(output, (x_ini, y_ini), (x_ini + RECT_WIDTH, y_ini + RECT_HEIGHT), (255, 0, 0), 2)

    # Coordenadas de la mano
    x, y = int(hand_landmarks.landmark[9].x * width), int(hand_landmarks.landmark[9].y * height)

    # Mapeo a pantalla
    screen_w, screen_h = pyautogui.size()
    xm = np.interp(x, (x_ini, x_ini + RECT_WIDTH), (5, screen_w - 5))
    ym = np.interp(y, (y_ini, y_ini + RECT_HEIGHT), (5, screen_h - 5))
    pyautogui.moveTo(int(xm), int(ym))

    # Click si índice abajo
    if detect_finger_down(hand_landmarks, width, height, output):
        pyautogui.click()

    # Marcador en la mano
    cv2.circle(output, (x, y), 10, COLOR_MOUSE_POINTER, 3)
    cv2.circle(output, (x, y), 5, COLOR_MOUSE_POINTER, -1)

    return output

def process_hand_left(hand_landmarks, frame, width, height, model):
    output = frame.copy()

    # Bounding box de la mano
    x_coords = [int(lm.x * width) for lm in hand_landmarks.landmark]
    y_coords = [int(lm.y * height) for lm in hand_landmarks.landmark]
    x_min, x_max = max(min(x_coords)-20, 0), min(max(x_coords)+20, width)
    y_min, y_max = max(min(y_coords)-20, 0), min(max(y_coords)+20, height)

    # Recorte y preprocesamiento
    hand_roi = frame[y_min:y_max, x_min:x_max]
    if hand_roi.size == 0:
        return output, None  # si el ROI sale vacío

    # Si no hay modelo disponible, solo mostrar el bounding box
    if model is None:
        cv2.rectangle(output, (x_min, y_min), (x_max, y_max), (0, 255, 255), 2)
        cv2.putText(output, "Modelo no disponible",
                    (x_min, y_min - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        return output, None

    hand_resized = cv2.resize(hand_roi, (128, 128))
    hand_array = hand_resized.astype("float32")
    hand_array = np.expand_dims(hand_array, axis=0)  # (1,128,128,3)

    try:
        # Predicción
        preds = model.predict(hand_array, verbose=0)
        class_idx = np.argmax(preds)
        pred_conf = preds[0][class_idx]
        
        # Convertir clase a letra para mostrar
        letter = chr(int(class_idx) + ord('A'))
        
        # Verificar si hay comando configurado
        class_str = str(int(class_idx))
        command_text = "Sin configurar"
        text_color = (0, 0, 255)  # Rojo por defecto
        
        if class_str in config:
            command_text = config[class_str]
            text_color = (0, 255, 0)  # Verde si está configurado

        print(f"Predicción: Letra {letter} (clase {class_idx}) con confianza {pred_conf:.2f} → {command_text}")

        # Mostrar resultado en pantalla con más información
        cv2.rectangle(output, (x_min, y_min), (x_max, y_max), text_color, 2)
        
        # Línea 1: Letra y confianza
        cv2.putText(output, f"Letra {letter} ({pred_conf:.2f})",
                    (x_min, y_min - 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
        
        # Línea 2: Comando configurado
        cv2.putText(output, f"Cmd: {command_text}",
                    (x_min, y_min - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)

        return output, class_idx
    except Exception as e:
        print(f"Error en predicción: {e}")
        cv2.rectangle(output, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)
        cv2.putText(output, f"Error predicción",
                    (x_min, y_min - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return output, None

def set_window_always_on_top(window_title):
    """Establece la ventana con el título dado como siempre en la parte superior."""
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    else:
        print(f"No se encontró la ventana con el título: {window_title}")
    
def executive_command(class_id):
    if class_id is None:
        return
    
    class_str = str(int(class_id))  # Convertir a int y luego a string
    letter = chr(int(class_id) + ord('A'))  # Convertir número a letra
    
    print(f"\n🔍 DETECTADO: Letra {letter} (clase {class_id})")
    
    if class_str in config:
        action = config[class_str]
        print(f"📋 CONFIGURADO: {action}")
        
        if action in actions:
            print(f"✅ EJECUTANDO: '{action}' para letra {letter}")
            try:
                actions[action]()
                print(f"✅ ÉXITO: Comando '{action}' ejecutado correctamente")
            except Exception as e:
                print(f"❌ ERROR ejecutando '{action}': {e}")
        else:
            print(f"❌ ERROR: Acción '{action}' no está definida en el diccionario de acciones")
            print(f"📝 Acciones disponibles: {list(actions.keys())}")
    else:
        print(f"⚠️  NO CONFIGURADO: No hay comando para letra {letter} (clase {class_id})")
        print(f"📝 Clases configuradas: {list(config.keys())}")
    print("-" * 50)

# --- Función principal ---
def main():
    last_exec_time = time.time()
    last_command = "Ninguno"
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 420)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 340)

    # Crear recomendaciones iniciales
    create_recommendation_panels()

    with mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5) as hands:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            height, width, _ = frame.shape
            frame = cv2.flip(frame, 1)
            output = frame.copy()

            # Agregar información de estado en la parte superior
            cv2.putText(output, f"Configuraciones: {len(config)}", (10, 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(output, f"Ultimo comando: {last_command}", (10, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Mostrar tiempo restante de cooldown
            time_left = max(0, EXEC_COOLDOWN - (time.time() - last_exec_time))
            if time_left > 0:
                cv2.putText(output, f"Cooldown: {time_left:.1f}s", (10, 75), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            # Procesar manos
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)
            pred = None

            if results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    if handedness.classification[0].label == 'Right':
                        output = process_hand_right(hand_landmarks, frame, width, height)
                    if handedness.classification[0].label == 'Left':
                        output, pred = process_hand_left(hand_landmarks, frame, width, height, gesture_model)

            # Actualizar recomendaciones solo cuando se detecta una nueva seña
            if pred is not None:
                update_recommendation_panels_on_gesture(pred)
            
            # Mostrar paneles de recomendaciones
            show_recommendation_panels()

            cv2.imshow('Hand Control', output)
            cv2.moveWindow('Hand Control', 0, 0)
            set_window_always_on_top('Hand Control')

            if pred is not None:
                now = time.time()
                if now - last_exec_time > EXEC_COOLDOWN:
                    # Actualizar último comando ejecutado
                    class_str = str(int(pred))
                    if class_str in config:
                        last_command = config[class_str]
                    else:
                        last_command = f"Letra {chr(int(pred) + ord('A'))} (no config)"
                    
                    executive_command(pred)
                    last_exec_time = now  

            if cv2.waitKey(1) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()