import cv2
import mediapipe as mp
import numpy as np
import pyautogui

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
color_mouse_pointer = (255, 0, 255)

X_Y_INI = 100
RECT_WIDTH = 300
RECT_HEIGHT = 200

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

                    # Tamaño de la pantalla
                    screen_width, screen_height = pyautogui.size()

                    # ⚡ Mapeo: del rectángulo → a la pantalla
                    xm = np.interp(x, (X_Y_INI_X, X_Y_INI_X + RECT_WIDTH), (5, screen_width-5))
                    ym = np.interp(y, (X_Y_INI_Y, X_Y_INI_Y + RECT_HEIGHT), (5, screen_height-5))

                    pyautogui.moveTo(int(xm), int(ym))

                    if detect_finger_down(hand_landmarks):
                        pyautogui.click()

                    # Dibujar marcador de la mano en el rectángulo
                    cv2.circle(output, (x, y), 10, color_mouse_pointer, 3)
                    cv2.circle(output, (x, y), 5, color_mouse_pointer, -1)

        cv2.imshow('output', output)
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()