import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import win32gui
import win32con

# --- Configuración ---
RECT_WIDTH = 160
RECT_HEIGHT = 100
COLOR_MOUSE_POINTER = (255, 0, 255)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


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
    """Procesa la mano detectada y controla el mouse si es la derecha."""
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

def set_window_always_on_top(window_title):
    """Establece la ventana con el título dado como siempre en la parte superior."""
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    else:
        print(f"No se encontró la ventana con el título: {window_title}")


# --- Función principal ---
def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 420)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 340)

    with mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5) as hands:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            height, width, _ = frame.shape
            frame = cv2.flip(frame, 1)
            output = frame.copy()

            # Procesar manos
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    if handedness.classification[0].label == 'Right':
                        output = process_hand_right(hand_landmarks, frame, width, height)

            cv2.imshow('Hand Mouse Control', output)
            cv2.moveWindow('Hand Mouse Control', 0, 0)

            set_window_always_on_top('Hand Mouse Control')
            

            if cv2.waitKey(1) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()