# 🤖 Sistema de Control Gestual ASL - Machine Learning 2

## 📋 Descripción del Proyecto

Este proyecto implementa un **sistema de control gestual inteligente** que utiliza el **Lenguaje de Señas Americano (ASL)** para controlar comandos de computadora en tiempo real. Combina tecnologías avanzadas de **Machine Learning**, **Computer Vision** y **interfaces gráficas** para crear una experiencia de usuario innovadora y accesible.

## 🎯 Características Principales

### 🖐️ **Reconocimiento de Gestos Dual**
- **Mano Izquierda**: Reconocimiento de letras ASL (A-Z) para ejecutar comandos
- **Mano Derecha**: Control del cursor y clicks del mouse
- **Detección en Tiempo Real**: ~120ms de respuesta para detección visual

### 🎮 **Control por Comandos**
- **25 Comandos Configurables**: Desde acciones básicas hasta aplicaciones específicas
- **Comando Protegido**: Letra X siempre ejecuta "Presionar ESC" (no editable)
- **Cooldown Inteligente**: 3 segundos entre ejecuciones para evitar activaciones accidentales

### 🖥️ **Interfaz de Configuración Visual**
- **Drag & Drop**: Arrastra letras ASL a comandos específicos
- **Visualización de Imágenes**: Muestra las señas ASL reales para cada letra
- **Configuración Persistente**: Guarda y carga configuraciones en formato JSON
- **Control de Estado**: Botones se bloquean durante la ejecución del control gestual

### 🔍 **Sistema de Recomendaciones**
- **Paneles Horizontales**: Muestra 2 recomendaciones al lado de la cámara
- **Actualización Inteligente**: Cambia recomendaciones solo cuando detecta una nueva seña
- **Feedback Visual**: Información en tiempo real sobre gestos detectados

## 🛠️ Tecnologías Utilizadas

### **Machine Learning & Computer Vision**
- **TensorFlow 2.19.1**: Clasificación de gestos ASL
- **MediaPipe**: Detección y tracking de manos en tiempo real
- **OpenCV**: Procesamiento de imágenes y video
- **NumPy**: Operaciones matemáticas y manipulación de arrays

### **Interfaz Gráfica**
- **PySide6**: Aplicación de configuración moderna con Qt6
- **Drag & Drop**: Interfaz intuitiva para asignación de comandos

### **Automatización del Sistema**
- **PyAutoGUI**: Control del mouse y acciones del sistema
- **keyboard**: Ejecución de comandos de teclado y shortcuts
- **win32gui/win32con**: Integración avanzada con Windows

## 📁 Estructura del Proyecto

```
MachineLearnin2/
├── 📄 app.py                      # Interfaz de configuración visual
├── 📄 program.py                  # Motor principal de reconocimiento gestual
├── 📄 configuracion_gestos.json   # Configuración de comandos personalizada
├── 📄 requirements.txt            # Dependencias del proyecto
├── 📄 pyrightconfig.json         # Configuración del linter Python
├── 📁 models/                     # Modelos de Machine Learning
├── 📁 Sign_Images/               # Imágenes de referencia ASL
│   ├── A.jpeg                    # Señas A-Z del alfabeto ASL
│   ├── B.jpeg
│   └── ... (Z.jpeg)
└── 📁 venv_ml2/                  # Entorno virtual Python
    ├── Scripts/
    └── Lib/
```

## 🚀 Comandos Disponibles

| #  | Letra ASL | Comando | Descripción |
|----|-----------|---------|-------------|
| 0  | A | Copiar | Ctrl+C |
| 1  | B | Pegar | Ctrl+V |
| 2  | C | Deshacer | Ctrl+Z |
| 3  | D | Rehacer | Ctrl+Y |
| 4  | E | Screenshot | Captura de pantalla |
| 5  | F | Screenshot Portapapeles | Print Screen |
| 6  | G | Cambiar Ventana | Alt+Tab |
| 7  | H | Buscar | Ctrl+F |
| 8  | I | Nueva Pestaña | Ctrl+T |
| 9  | J | Cerrar Pestaña | Ctrl+W |
| 10 | K | Subir Volumen | Volume Up |
| 11 | L | Bajar Volumen | Volume Down |
| 12 | M | Silenciar | Volume Mute |
| 13 | N | Abrir Bloc de Notas | notepad |
| 14 | O | Abrir Calculadora | calc |
| 15 | P | Abrir Explorador | explorer |
| 16 | Q | Escribir Texto | "Hola desde IA!" |
| 17 | R | Refrescar | F5 |
| 18 | S | Borrar | Delete |
| 19 | T | Scroll Arriba | Scroll Up |
| 20 | U | Scroll Abajo | Scroll Down |
| 21 | V | Abrir Chrome | start chrome |
| 22 | W | Abrir Excel | start excel |
| 23 | X | **Presionar ESC** | **🔒 PROTEGIDO** |
| 24 | Y | Abrir Word | start winword |

## 🔧 Instalación y Configuración

### **Prerrequisitos**
- **Python 3.10+**
- **Webcam** funcionando
- **Windows 10/11** (optimizado para Windows)

### **1. Clonar el Repositorio**
```bash
git clone https://github.com/Diazgerard/MachineLearnin2.git
cd MachineLearnin2
```

### **2. Crear Entorno Virtual**
```bash
python -m venv venv_ml2
venv_ml2\Scripts\activate
```

### **3. Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### **4. Verificar Estructura**
Asegúrate de que existan:
- `📁 Sign_Images/` con imágenes A.jpeg a Z.jpeg
- `📁 models/` con los archivos .h5 y .keras
- `📄 configuracion_gestos.json`

## 🎮 Cómo Usar

### **1. Configurar Comandos**
```bash
# Activar entorno virtual
venv_ml2\Scripts\activate

# Abrir interfaz de configuración
python app.py
```

**En la interfaz:**
- 🖱️ **Arrastra letras** desde el panel izquierdo a los comandos deseados
- 💾 **Guarda la configuración** con el botón "Guardar configuración"
- 🚀 **Inicia el control gestual** con "Iniciar Control Gestual"

### **2. Control Gestual en Tiempo Real**
```bash
# O ejecutar directamente
python program.py
```

**Durante el uso:**
- 🤚 **Mano Izquierda**: Hacer señas ASL para ejecutar comandos
- 🖱️ **Mano Derecha**: Mover cursor en el rectángulo azul
- 👆 **Dedo Índice Abajo**: Click del mouse
- ⌨️ **ESC**: Salir del programa

### **3. Paneles de Información**
El sistema muestra en tiempo real:
- 📊 **Estado**: Configuraciones cargadas, último comando ejecutado
- ⏱️ **Cooldown**: Tiempo restante antes del próximo comando
- 🔍 **Detección**: Letra detectada con nivel de confianza
- 💡 **Recomendaciones**: Sugerencias de señas disponibles

## ⚙️ Configuración Avanzada

### **Ajustar Tiempos de Respuesta**
En `program.py`, línea ~228:
```python
EXEC_COOLDOWN = 3.0  # Segundos entre comandos (ajustable)
```

### **Modificar Confianza de Detección**
En `program.py`, función `main()`:
```python
min_detection_confidence=0.5  # 0.1 (más sensible) a 0.9 (más estricto)
```

### **Personalizar Comandos**
Edita la función `actions` en `program.py` para agregar comandos personalizados:
```python
"Mi Comando": lambda: os.system("mi_aplicacion.exe"),
```

## 🔬 Arquitectura Técnica

### **Flujo de Procesamiento**
1. **Captura de Video** → OpenCV + DirectShow
2. **Detección de Manos** → MediaPipe (50% confianza mínima)
3. **Extracción de Landmarks** → 21 puntos de referencia por mano
4. **Clasificación ASL** → TensorFlow CNN (~75ms)
5. **Ejecución de Comando** → PyAutoGUI/keyboard
6. **Feedback Visual** → OpenCV + Recomendaciones

### **Modelos de IA**
- **Modelo Principal**: `asl_alphabet_model.h5`
- **Modelo Alternativo**: `EfficientNetB5_gesture_classifier.keras`
- **Entrada**: Landmarks de mano (21 puntos x,y,z)
- **Salida**: Clasificación A-Z (26 clases)

## 🚨 Solución de Problemas

### **Error: "No se encuentra el modelo"**
```bash
# Verificar que el archivo existe
dir models\*.h5
dir models\*.keras
```

### **Error: "Cámara no detectada"**
- Verificar que la webcam esté conectada
- Cerrar otras aplicaciones que usen la cámara
- Cambiar el índice de cámara en `program.py`:
```python
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # Cambiar 0 por 1
```

### **Error: "Dependencias faltantes"**
```bash
# Reinstalar dependencias
pip install --force-reinstall -r requirements.txt
```

### **Gestos no se detectan bien**
- 🌟 **Iluminación**: Usar buena iluminación frontal
- 📏 **Distancia**: Mantener la mano a 30-60cm de la cámara
- 🤚 **Claridad**: Hacer gestos ASL claros y definidos
- ⏱️ **Tiempo**: Mantener la seña por 1-2 segundos

