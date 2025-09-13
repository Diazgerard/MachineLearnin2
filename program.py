import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import json
import os
import subprocess
import time

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
color_mouse_pointer = (255, 0, 255)

X_Y_INI = 100
RECT_WIDTH = 300
RECT_HEIGHT = 200

# Cargar configuración de gestos
def load_gesture_config():
    config_path = "configuracion_gestos.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
    return {}

# Ejecutar comandos según la configuración
def execute_command(command):
    try:
        if command == "Clic izquierdo":
            pyautogui.click()
        elif command == "Clic derecho":
            pyautogui.rightClick()
        elif command == "Copiar (Ctrl+C)":
            pyautogui.hotkey('ctrl', 'c')
        elif command == "Pegar (Ctrl+V)":
            pyautogui.hotkey('ctrl', 'v')
        elif command == "Deshacer (Ctrl+Z)":
            pyautogui.hotkey('ctrl', 'z')
        elif command == "Alt+Tab":
            pyautogui.hotkey('alt', 'tab')
        elif command == "Cerrar Ventana":
            pyautogui.hotkey('alt', 'f4')
        elif command == "Windows":
            pyautogui.press('win')
        elif command == "Grabar Pantalla":
            pyautogui.hotkey('win', 'g')
        elif command == "Subir Volumen":
            pyautogui.press('volumeup')
        elif command == "Bajar Volumen":
            pyautogui.press('volumedown')
        elif command == "Silenciar":
            pyautogui.press('volumemute')
        elif command == "Captura de Pantalla":
            pyautogui.hotkey('win', 'shift', 's')
        elif command == "Cerrar Sesion":
            pyautogui.hotkey('win', 'l')
        elif command == "Abrir Explorador de Archivos":
            pyautogui.hotkey('win', 'e')
        elif command == "Minimizar Ventana":
            pyautogui.hotkey('win', 'down')
        else:
            print(f"Comando no reconocido: {command}")
            return
        
        print(f"Ejecutando: {command}")
    except Exception as e:
        print(f"Error ejecutando comando {command}: {e}")

def calculate_distance(x1, y1, x2, y2):
    p1 = np.array([x1, y1])
    p2 = np.array([x2, y2])
    return np.linalg.norm(p1 - p2)

def detect_finger_down(hand_landmarks):
    finger_down = False
    color_base = (255, 0, 112)
    color_index = (255, 198, 82)
    x_base1 = int(hand_landmarks.landmark[0].x * width)
    y_base1 = int(hand_landmarks.landmark[0].y * height)
    x_base2 = int(hand_landmarks.landmark[9].x * width)
    y_base2 = int(hand_landmarks.landmark[9].y * height)
    x_index = int(hand_landmarks.landmark[8].x * width)
    y_index = int(hand_landmarks.landmark[8].y * height)
    d_base = calculate_distance(x_base1, y_base1, x_base2, y_base2)
    d_base_index = calculate_distance(x_base1, y_base1, x_index, y_index)
    if d_base_index < d_base:
        finger_down = True
        color_base = (255, 0, 255)
        color_index = (255, 0, 255)
    cv2.circle(output, (x_base1, y_base1), 5, color_base, 2)
    cv2.circle(output, (x_index, y_index), 5, color_index, 2)
    cv2.line(output, (x_base1, y_base1), (x_base2, y_base2), color_base, 3)
    cv2.line(output, (x_base1, y_base1), (x_index, y_index), color_index, 3)
    return finger_down

def detect_gesture(hand_landmarks):
    """Detectar el gesto actual basado en las posiciones de los landmarks"""
    # Obtener puntos importantes
    landmarks = []
    for lm in hand_landmarks.landmark:
        landmarks.append([lm.x, lm.y])
    
    # Puntas de los dedos
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    
    # Bases/articulaciones de los dedos
    thumb_pip = landmarks[3]
    index_pip = landmarks[6]
    middle_pip = landmarks[10]
    ring_pip = landmarks[14]
    pinky_pip = landmarks[18]
    
    # Punto de referencia (muñeca)
    wrist = landmarks[0]
    
    # Verificar qué dedos están levantados
    fingers_up = []
    
    # Pulgar (lógica especial por orientación)
    if thumb_tip[0] > thumb_pip[0]:  # Para mano derecha
        fingers_up.append(1)
    else:
        fingers_up.append(0)
    
    # Otros dedos (comparar Y - punta vs articulación)
    for tip, pip in [(index_tip, index_pip), (middle_tip, middle_pip), 
                     (ring_tip, ring_pip), (pinky_tip, pinky_pip)]:
        if tip[1] < pip[1]:  # Punta más arriba que la articulación
            fingers_up.append(1)
        else:
            fingers_up.append(0)
    
    # Detectar gestos específicos
    total_fingers = sum(fingers_up)
    
    # Gestos basados en dedos levantados
    if total_fingers == 5:
        return "Mano abierta"
    elif total_fingers == 0:
        return "Puño cerrado"
    elif fingers_up == [1, 0, 0, 0, 0]:
        return "Pulgar arriba"
    elif fingers_up == [0, 1, 0, 0, 0]:
        return "Señalando"
    elif fingers_up == [0, 1, 1, 0, 0]:
        return "Paz y amor"
    elif fingers_up == [1, 0, 0, 0, 1]:
        return "Llamando"
    elif fingers_up == [0, 1, 0, 0, 1]:
        return "Cuernos"
    elif fingers_up == [1, 1, 0, 0, 0]:
        return "Pellizco"
    
    # Gestos más específicos basados en combinaciones
    elif total_fingers == 3:
        if fingers_up[1:4] == [1, 1, 1]:  # índice, medio, anular
            return "Ok"
    
    # Gestos direccionales (basados en la posición de la mano)
    elif fingers_up == [0, 1, 0, 0, 0]:  # Solo índice
        # Verificar dirección basada en la posición del índice relativa a la muñeca
        index_x_diff = index_tip[0] - wrist[0]
        index_y_diff = index_tip[1] - wrist[1]
        
        if abs(index_x_diff) > abs(index_y_diff):
            if index_x_diff > 0:
                return "Señalando hacia la derecha"
            else:
                return "Señalando hacia la izquierda"
        else:
            if index_y_diff < 0:
                return "Señalando hacia arriba"
            else:
                return "Señalando hacia abajo"
    
    # Palma hacia abajo (detectar orientación de la mano)
    elif total_fingers >= 4:
        # Calcular si la palma está hacia abajo basándose en la posición de los landmarks
        middle_mcp = landmarks[9]  # Base del dedo medio
        if middle_mcp[1] < wrist[1]:  # Si la base está más arriba que la muñeca
            return "Palma Abajo"
    
    return "Desconocido"

# Cargar configuración al inicio
gesture_config = load_gesture_config()
print("Configuración cargada:", gesture_config)

# Variables para control de tiempo y detección
last_gesture = ""
gesture_start_time = 0
GESTURE_HOLD_TIME = 1.5  # Tiempo en segundos para mantener el gesto
last_command_time = 0
COMMAND_COOLDOWN = 2.0  # Tiempo de espera entre comandos

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5) as hands:
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        height, width, _ = frame.shape
        frame = cv2.flip(frame, 1)

        X_Y_INI_X = width - RECT_WIDTH - 50
        X_Y_INI_Y = height - RECT_HEIGHT - 50

        output = frame.copy()

        # Procesar manos con MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        current_time = time.time()

        if results.multi_hand_landmarks is not None:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):

                # Nombre de la mano detectada
                hand_label = handedness.classification[0].label
                hand_score = handedness.classification[0].score
                
                if hand_label == "Right":
                    # Dibujar el rectángulo de control
                    aux_image = frame.copy()
                    cv2.rectangle(aux_image, (X_Y_INI_X, X_Y_INI_Y),
                      (X_Y_INI_X + RECT_WIDTH, X_Y_INI_Y + RECT_HEIGHT),
                      (255, 0, 0), 2)
                    output = aux_image

                    # Coordenadas de la mano en la cámara
                    x = int(hand_landmarks.landmark[9].x * width)
                    y = int(hand_landmarks.landmark[9].y * height)

                    # Control del cursor (solo si está en el rectángulo)
                    if (X_Y_INI_X <= x <= X_Y_INI_X + RECT_WIDTH and 
                        X_Y_INI_Y <= y <= X_Y_INI_Y + RECT_HEIGHT):
                        
                        # Tamaño de la pantalla
                        screen_width, screen_height = pyautogui.size()

                        # Mapeo: del rectángulo → a la pantalla
                        xm = np.interp(x, (X_Y_INI_X, X_Y_INI_X + RECT_WIDTH), (5, screen_width-5))
                        ym = np.interp(y, (X_Y_INI_Y, X_Y_INI_Y + RECT_HEIGHT), (5, screen_height-5))

                        pyautogui.moveTo(int(xm), int(ym))

                        # Detectar clic con dedo índice
                        if detect_finger_down(hand_landmarks):
                            if current_time - last_command_time > COMMAND_COOLDOWN:
                                pyautogui.click()
                                last_command_time = current_time

                    # Detectar gesto para comandos configurados
                    detected_gesture = detect_gesture(hand_landmarks)
                    
                    # Mostrar gesto detectado en pantalla
                    cv2.putText(output, f"Gesto: {detected_gesture}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Lógica de mantenimiento de gesto
                    if detected_gesture == last_gesture and detected_gesture != "Desconocido":
                        # Continuar manteniendo el mismo gesto
                        elapsed_time = current_time - gesture_start_time
                        if elapsed_time >= GESTURE_HOLD_TIME:
                            # Ejecutar comando si el gesto se mantiene el tiempo suficiente
                            for command, gesture_name in gesture_config.items():
                                if gesture_name == detected_gesture:
                                    if current_time - last_command_time > COMMAND_COOLDOWN:
                                        execute_command(command)
                                        last_command_time = current_time
                                        break
                        
                        # Mostrar barra de progreso
                        progress = min(elapsed_time / GESTURE_HOLD_TIME, 1.0)
                        bar_width = 200
                        bar_height = 20
                        cv2.rectangle(output, (10, 60), (10 + bar_width, 60 + bar_height), (50, 50, 50), -1)
                        cv2.rectangle(output, (10, 60), (10 + int(bar_width * progress), 60 + bar_height), (0, 255, 0), -1)
                        cv2.putText(output, f"Manteniendo: {detected_gesture}", (10, 100), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                    
                    elif detected_gesture != "Desconocido":
                        # Nuevo gesto detectado
                        last_gesture = detected_gesture
                        gesture_start_time = current_time
                    
                    else:
                        # No hay gesto válido
                        last_gesture = ""
                        gesture_start_time = 0

                    # Dibujar marcador de la mano en el rectángulo
                    cv2.circle(output, (x, y), 10, color_mouse_pointer, 3)
                    cv2.circle(output, (x, y), 5, color_mouse_pointer, -1)

        # Mostrar configuración cargada en pantalla
        if gesture_config:
            y_offset = height - 150
            cv2.putText(output, "Configuracion activa:", (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            for i, (command, gesture) in enumerate(list(gesture_config.items())[:5]):  # Mostrar solo 5
                cv2.putText(output, f"{gesture} -> {command}", (10, y_offset + 20 + i*15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # Instrucciones
        cv2.putText(output, "Presiona ESC para salir", (width - 200, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        cv2.imshow('Control Gestual', output)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir
            break

cap.release()
cv2.destroyAllWindows()