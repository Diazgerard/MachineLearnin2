import sys
import subprocess
import os
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QLabel, QPushButton, QAbstractItemView, QFrame,
    QGridLayout, QListWidgetItem
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap, QIcon

class DropZone(QFrame):
    def __init__(self, command: str, parent=None):
        super().__init__(parent)
        self.command = command
        self.is_protected = (command == "Presionar ESC")  # Proteger el comando ESC
        
        # Solo permitir drops si no está protegido
        self.setAcceptDrops(not self.is_protected)
        
        layout = QVBoxLayout(self)
        
        # Crear el cuadrado para soltar
        self.box = QLabel()
        self.box.setFixedSize(110, 110)  # Reducimos un poco el tamaño para mejor distribución
        
        # Configurar cursor y tooltip según protección
        if self.is_protected:
            self.box.setCursor(Qt.CursorShape.ForbiddenCursor)
            self.box.setToolTip("🔒 ZONA PROTEGIDA: Este comando no se puede cambiar")
        else:
            self.box.setCursor(Qt.CursorShape.PointingHandCursor)
            self.box.setToolTip("Haz clic para limpiar la letra")
        
        # Estilo inicial
        base_style = """
            QLabel {
                background-color: #ffffff;
                border: 3px dashed #6c757d;
                border-radius: 15px;
                font-size: 48px;
                qproperty-alignment: AlignCenter;
            }
        """
        
        # Si está protegido, usar estilo especial
        if self.is_protected:
            base_style = """
                QLabel {
                    background-color: #ffebee;
                    border: 3px solid #f44336;
                    border-radius: 15px;
                    font-size: 48px;
                    qproperty-alignment: AlignCenter;
                    color: #d32f2f;
                }
            """
        
        self.box.setStyleSheet(base_style)
        layout.addWidget(self.box, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Etiqueta para el comando con color especial si está protegido
        self.label = QLabel(command)
        label_style = """
            font-size: 12px;
            color: white;
            font-weight: bold;
        """
        
        if self.is_protected:
            label_style = """
                font-size: 12px;
                color: #f44336;
                font-weight: bold;
                background-color: rgba(244, 67, 54, 0.1);
                padding: 2px;
                border-radius: 4px;
            """
        
        self.label.setStyleSheet(label_style)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
    def mousePressEvent(self, event):
        # No permitir limpiar zonas protegidas
        if self.is_protected:
            return
        
        # Determinar qué letra devolver
        letter_to_return = None
        if self.box.text():  # Si hay texto
            letter_to_return = self.box.text()
        elif hasattr(self, 'current_letter'):  # Si hay imagen
            letter_to_return = self.current_letter
        
        if letter_to_return:  # Solo si hay una letra asignada
            # Limpiar el cuadro
            self.box.setText("")
            self.box.setPixmap(QPixmap())  # Limpiar imagen
            if hasattr(self, 'current_letter'):
                delattr(self, 'current_letter')  # Limpiar la letra guardada
            
            self.box.setStyleSheet("""
                QLabel {
                    background-color: #ffffff;
                    border: 3px dashed #6c757d;
                    border-radius: 15px;
                    font-size: 48px;
                    qproperty-alignment: AlignCenter;
                }
            """)
            
            # Devolver la letra a la lista disponible
            main_window = self.get_main_window()
            if main_window:
                main_window.return_gesture_to_list(letter_to_return)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.box.setStyleSheet("""
                QLabel {
                    background-color: #e3f2fd;
                    border: 3px solid #2196f3;
                    border-radius: 15px;
                    font-size: 48px;
                    qproperty-alignment: AlignCenter;
                }
            """)
    
    def dragLeaveEvent(self, event):
        self.box.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                border: 3px dashed #6c757d;
                border-radius: 15px;
                font-size: 48px;
                qproperty-alignment: AlignCenter;
            }
        """)
    
    def dropEvent(self, event):
        if event.mimeData().hasText():
            letter = event.mimeData().text()
            
            # Verificar si la letra ya está asignada en otra zona
            main_window = self.get_main_window()
            if main_window and main_window.is_gesture_assigned(letter, self):
                return  # No permitir la asignación si ya está usado
            
            # Si había una letra anterior, devolverla a la lista
            if self.box.text() or hasattr(self.box, 'pixmap') and self.box.pixmap():
                # Si hay texto, devolverlo
                if self.box.text():
                    main_window.return_gesture_to_list(self.box.text())
                # Si hay imagen, obtener la letra del data attribute
                elif hasattr(self, 'current_letter'):
                    main_window.return_gesture_to_list(self.current_letter)
            
            # Cargar y mostrar la imagen de la letra
            current_dir = os.path.dirname(os.path.abspath(__file__))
            signs_dir = os.path.join(current_dir, "Sign_Images")
            image_path = os.path.join(signs_dir, f"{letter}.jpeg")
            
            if os.path.exists(image_path):
                # Cargar la imagen y escalarla para que llene el cuadro
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # Escalar la imagen para que llene casi todo el cuadro (dejando un poco de margen)
                    scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.box.setPixmap(scaled_pixmap)
                    self.box.setText("")  # Limpiar cualquier texto
                    self.current_letter = letter  # Guardar la letra actual
                    
                    # Cambiar el estilo para acomodar la imagen
                    self.box.setStyleSheet("""
                        QLabel {
                            background-color: #e8f5e9;
                            border: 3px solid #4caf50;
                            border-radius: 15px;
                            padding: 5px;
                            qproperty-alignment: AlignCenter;
                        }
                    """)
            else:
                # Fallback: mostrar solo la letra si no se encuentra la imagen
                self.box.setText(letter)
                self.box.setPixmap(QPixmap())  # Limpiar cualquier imagen
                self.current_letter = letter
                self.box.setStyleSheet("""
                    QLabel {
                        background-color: #e8f5e9;
                        border: 3px solid #4caf50;
                        border-radius: 15px;
                        padding: 10px;
                        font-size: 48px;
                        font-weight: bold;
                        color: black;
                        qproperty-alignment: AlignCenter;
                    }
                """)
            
            # Remover la letra de la lista disponible
            if main_window:
                main_window.remove_gesture_from_list(letter)
            
            event.acceptProposedAction()
    
    def get_main_window(self):
        # Buscar la ventana principal navegando por los padres
        widget = self
        while widget:
            if isinstance(widget, MainWindow):
                return widget
            widget = widget.parent()
        return None

class DnDListWidget(QListWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName(title)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.setDefaultDropAction(QtCore.Qt.DropAction.CopyAction)
        # Establecer el tamaño de los íconos para que las imágenes se vean grandes
        self.setIconSize(QSize(120, 120))
        # Establecer el tamaño de los íconos para que las imágenes se vean grandes
        self.setIconSize(QSize(120, 120))
        self.setStyleSheet("""
            QListWidget {
                background-color: #1e293b;  /* Color de fondo del panel - azul oscuro */
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 5px;
                margin: 5px;
                background-color: transparent;  /* Sin fondo para el item */
                border: none;  /* Sin borde */
                min-height: 130px;  /* Altura mínima para acomodar íconos de 120px */
                text-align: center;
            }
            QListWidget::item:selected {
                background-color: rgba(59, 130, 246, 0.3);  /* Fondo semitransparente cuando está seleccionado */
                border-radius: 8px;
            }
            QListWidget::item:hover {
                background-color: rgba(37, 99, 235, 0.2);  /* Fondo semitransparente al pasar el mouse */
                border-radius: 8px;
            }
        """)

    def startDrag(self, actions):
        item = self.currentItem()
        if item:
            # Obtener la letra desde el data del item
            letter = item.data(Qt.ItemDataRole.UserRole)
            if letter:
                drag = QtGui.QDrag(self)
                mimeData = QtCore.QMimeData()
                mimeData.setText(letter)  # Enviar solo la letra
                drag.setMimeData(mimeData)
                drag.exec(QtCore.Qt.DropAction.CopyAction)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aprendizaje de Maquina ll - Proyecto")
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # Establecer el color de fondo de la ventana principal
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QWidget {
                background-color: #1a1a1a;
            }
        """)
        
        info = QLabel(
            "• Arrastra las letras (A-Z) de la izquierda a las zonas de comando de la derecha\n"
            "• Cada letra puede asignarse a un comando específico\n"
            "• Personaliza el control gestual usando el lenguaje de señas ASL"
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: white; font-size: 14px; font-weight: bold; padding: 10px;")
        root.addWidget(info)

        # Contenedor principal
        container = QHBoxLayout()
        root.addLayout(container)

        # Panel izquierdo
        left_panel = QVBoxLayout()
        left_label = QLabel("Letras disponibles")
        left_label.setStyleSheet("font-size: 16px; color: white; font-weight: bold; margin-bottom: 10px;")
        left_panel.addWidget(left_label)
        
        self.left = DnDListWidget("left")
        
        # Cargar imágenes de las letras desde la carpeta Sign_Images
        self.load_sign_images()
        
        self.left.setFixedWidth(250)  # Aumentar el ancho para las imágenes más grandes
        left_panel.addWidget(self.left)
        container.addLayout(left_panel)

        # Panel derecho con grid de zonas para soltar y scroll
        right_panel = QVBoxLayout()
        right_label = QLabel("Asigna letras a comandos:")
        right_panel.addWidget(right_label)
        
        # Crear un widget con scroll
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f1f1;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #888;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # Widget contenedor para el grid
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(15)  # Reducimos un poco el espaciado
        grid.setContentsMargins(10, 10, 10, 10)
        
        commands = [
            "Copiar",
            "Pegar",
            "Desahacer",
            "Rehacer",
            "Screenshot",
            "Screenshot Portapeles",
            "Cambiar Ventana",
            "Buscar",
            "Nueva Pestaña",
            "Cerrar Pestaña",
            "Subir Volumen",
            "Bajar Volumen",
            "Silenciar",
            "Abrir Bloc",
            "Abrir Calculadora",
            "Abrir Explorador",
            "Escribir Texto",
            "Refrescar",
            "Borrar",
            "Scroll Arriba",
            "Scroll Abajo",
            "Abrir Chrome",
            "Abrir Excel",
            "Presionar ESC",
            "Abrir Word"
        ]
        
        # Calcular número óptimo de columnas basado en el número de comandos
        num_columns = 4  # Aumentamos a 4 columnas
        
        self.drop_zones = []
        for i, cmd in enumerate(commands):
            row = i // num_columns
            col = i % num_columns
            zone = DropZone(cmd)
            self.drop_zones.append(zone)
            grid.addWidget(zone, row, col)
        
        # Configurar el scroll area
        scroll_area.setWidget(grid_widget)
        right_panel.addWidget(scroll_area)

        container.addLayout(right_panel)

        # Botones de control
        btns = QHBoxLayout()
        root.addLayout(btns)
        
        # Botón de iniciar programa
        self.start_btn = QPushButton("🚀 Iniciar Control Gestual")
        self.start_btn.clicked.connect(self.start_gesture_control)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                border: 2px solid #2ecc71;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
                border-color: #58d68d;
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background-color: #229954;
                transform: translateY(0px);
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                border-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        btns.addWidget(self.start_btn)
        
        # Botón de reinicio
        self.reset_btn = QPushButton("🔄 Reiniciar todo")
        self.reset_btn.clicked.connect(self.reset)
        btns.addWidget(self.reset_btn)
        
        # Botón de guardar
        self.save_btn = QPushButton("💾 Guardar configuración")
        self.save_btn.clicked.connect(self.save_configuration)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                border: 2px solid #5dade2;
            }
            QPushButton:hover {
                background-color: #5dade2;
                border-color: #85c1e9;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                border-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        btns.addWidget(self.save_btn)
        
        # Botón para parar el control gestual
        self.stop_btn = QPushButton("⏹️ Parar Control")
        self.stop_btn.clicked.connect(self.stop_gesture_control)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                border: 2px solid #c0392b;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #c0392b;
                border-color: #a93226;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                border-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.stop_btn.setEnabled(False)  # Inicialmente deshabilitado
        btns.addWidget(self.stop_btn)
        
        btns.addStretch()

        # Un pequeño estilo para que se vea mejor
        self.setStyleSheet("""
            QLabel { 
                font-size: 14px;
                color: white;
                font-weight: bold;
            }
            QPushButton { 
                padding: 10px 16px; 
                border-radius: 8px;
                background-color: #2c3e50;
                border: 2px solid #6c757d;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34495e;
                border-color: #95a5a6;
                color: white;
            }
            QPushButton:pressed {
                background-color: #2c3e50;
                color: #bdc3c7;
            }
        """)

        self.setMinimumSize(1200, 800)  # Aumentamos el tamaño de la ventana para el nuevo layout
        
        # Cargar configuración existente si existe
        self.load_existing_configuration()

    def load_sign_images(self):
        """Cargar las imágenes de las letras desde la carpeta Sign_Images"""
        # Obtener la ruta de la carpeta Sign_Images
        current_dir = os.path.dirname(os.path.abspath(__file__))
        signs_dir = os.path.join(current_dir, "Sign_Images")
        
        if not os.path.exists(signs_dir):
            print(f"Carpeta Sign_Images no encontrada en: {signs_dir}")
            return
        
        # Cargar imágenes para cada letra A-Z
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for letter in letters:
            image_path = os.path.join(signs_dir, f"{letter}.jpeg")
            
            if os.path.exists(image_path):
                # Crear el item con la imagen
                item = QListWidgetItem()
                
                # Cargar y redimensionar la imagen
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # Hacer las imágenes más grandes en la lista
                    scaled_pixmap = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    icon = QIcon(scaled_pixmap)
                    item.setIcon(icon)
                
                # Configurar el texto y datos del item
                item.setText("")  # Sin texto, solo imagen
                item.setData(Qt.ItemDataRole.UserRole, letter)  # Guardar la letra en el data
                item.setToolTip(f"Gesto para la letra {letter}")
                
                # Agregar el item a la lista
                self.left.addItem(item)

    def is_gesture_assigned(self, letter, current_zone):
        """Verificar si una letra ya está asignada en otra zona"""
        for zone in self.drop_zones:
            if zone != current_zone:
                # Verificar tanto texto como imagen
                zone_letter = None
                if zone.box.text():
                    zone_letter = zone.box.text()
                elif hasattr(zone, 'current_letter'):
                    zone_letter = zone.current_letter
                
                if zone_letter == letter:
                    return True
        return False
    
    def remove_gesture_from_list(self, letter):
        """Remover una letra de la lista de gestos disponibles"""
        for i in range(self.left.count()):
            item = self.left.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == letter:
                self.left.takeItem(i)
                break
    
    def return_gesture_to_list(self, letter):
        """Devolver una letra a la lista de gestos disponibles"""
        # Verificar que no esté ya en la lista
        for i in range(self.left.count()):
            item = self.left.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == letter:
                return  # Ya está en la lista
        
        # Cargar la imagen de la letra y agregarla de vuelta
        current_dir = os.path.dirname(os.path.abspath(__file__))
        signs_dir = os.path.join(current_dir, "Sign_Images")
        image_path = os.path.join(signs_dir, f"{letter}.jpeg")
        
        if os.path.exists(image_path):
            # Crear el item con la imagen
            item = QListWidgetItem()
            
            # Cargar y redimensionar la imagen
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon = QIcon(scaled_pixmap)
                item.setIcon(icon)
            
            # Configurar el texto y datos del item
            item.setText("")  # Sin texto, solo imagen
            item.setData(Qt.ItemDataRole.UserRole, letter)
            item.setToolTip(f"Gesto para la letra {letter}")
            
            # Agregar el item a la lista
            self.left.addItem(item)

    def load_existing_configuration(self):
        """Cargar configuración existente desde configuracion_gestos.json si existe"""
        import json
        import os
        
        # PRIMERO: Configurar siempre la zona protegida X → "Presionar ESC"
        self.configure_protected_zone()
        
        config_file = "configuracion_gestos.json"
        if not os.path.exists(config_file):
            return  # No hay configuración previa, pero ya configuramos la zona protegida
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Determinar si es formato nuevo o antiguo
            if isinstance(data, dict) and 'comandos' in data:
                config = data['comandos']  # Formato nuevo
            else:
                config = data  # Formato antiguo
            
            # Aplicar configuración a las zonas (excepto la protegida)
            for num_str, comando in config.items():
                try:
                    # Saltar la configuración protegida (#23)
                    if num_str == "23":
                        continue
                    
                    letra = chr(int(num_str) + ord('A'))  # Convertir número a letra
                    
                    # Buscar la zona de comando correspondiente
                    target_zone = None
                    for zone in self.drop_zones:
                        if zone.command == comando and not zone.is_protected:
                            target_zone = zone
                            break
                    
                    if target_zone:
                        # Cargar imagen de la letra
                        current_dir = os.path.dirname(os.path.abspath(__file__))
                        signs_dir = os.path.join(current_dir, "Sign_Images")
                        image_path = os.path.join(signs_dir, f"{letra}.jpeg")
                        
                        if os.path.exists(image_path):
                            # Cargar la imagen y aplicarla a la zona
                            pixmap = QPixmap(image_path)
                            if not pixmap.isNull():
                                scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                                target_zone.box.setPixmap(scaled_pixmap)
                                target_zone.box.setText("")
                                target_zone.current_letter = letra
                                
                                # Aplicar estilo visual
                                target_zone.box.setStyleSheet("""
                                    QLabel {
                                        background-color: #e8f5e9;
                                        border: 3px solid #4caf50;
                                        border-radius: 15px;
                                        padding: 5px;
                                        qproperty-alignment: AlignCenter;
                                    }
                                """)
                                
                                # Remover la letra de la lista disponible (excepto X que ya se removió)
                                if letra != 'X':
                                    self.remove_gesture_from_list(letra)
                        
                except (ValueError, IndexError):
                    continue  # Saltar entradas inválidas
                    
            print(f"✅ Configuración cargada: {len(config)} comandos aplicados")
            
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"⚠️ Error al cargar configuración: {e}")
        except Exception as e:
            print(f"❌ Error inesperado al cargar configuración: {e}")

    def configure_protected_zone(self):
        """Configurar automáticamente la zona protegida X → Presionar ESC"""
        # Buscar la zona de "Presionar ESC"
        protected_zone = None
        for zone in self.drop_zones:
            if zone.command == "Presionar ESC":
                protected_zone = zone
                break
        
        if protected_zone:
            # Cargar imagen de la letra X
            current_dir = os.path.dirname(os.path.abspath(__file__))
            signs_dir = os.path.join(current_dir, "Sign_Images")
            image_path = os.path.join(signs_dir, "X.jpeg")
            
            if os.path.exists(image_path):
                # Cargar la imagen de X
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    protected_zone.box.setPixmap(scaled_pixmap)
                    protected_zone.box.setText("")
                    protected_zone.current_letter = 'X'
                    
                    # Aplicar estilo protegido especial
                    protected_zone.box.setStyleSheet("""
                        QLabel {
                            background-color: #ffebee;
                            border: 3px solid #f44336;
                            border-radius: 15px;
                            padding: 5px;
                            qproperty-alignment: AlignCenter;
                        }
                    """)
                    
                    # Remover X de la lista disponible
                    self.remove_gesture_from_list('X')
                    print("🔒 Zona protegida configurada: X → Presionar ESC")

    def reset(self):
        self.left.clear()
        # Recargar todas las imágenes de las letras
        self.load_sign_images()
        self.clear_zones()

    def clear_zones(self):
        # Esta función solo se usa para el reset completo
        for zone in self.drop_zones:
            # Determinar qué letra devolver
            letter_to_return = None
            if zone.box.text():
                letter_to_return = zone.box.text()
            elif hasattr(zone, 'current_letter'):
                letter_to_return = zone.current_letter
            
            if letter_to_return:  # Si hay una letra asignada, devolverla a la lista
                self.return_gesture_to_list(letter_to_return)
            
            # Limpiar la zona
            zone.box.setText("")
            zone.box.setPixmap(QPixmap())  # Limpiar imagen
            if hasattr(zone, 'current_letter'):
                delattr(zone, 'current_letter')  # Limpiar la letra guardada
            
            zone.box.setStyleSheet("""
                QLabel {
                    background-color: #ffffff;
                    border: 3px dashed #6c757d;
                    border-radius: 15px;
                    font-size: 48px;
                    qproperty-alignment: AlignCenter;
                }
            """)
    
    def save_configuration(self):
        # Crear un diccionario con las asignaciones actuales
        config = {}
        config_details = {}
        
        # SIEMPRE incluir la configuración protegida
        config["23"] = "Presionar ESC"
        config_details["23"] = {
            "letra": "X",
            "numero": 23,
            "comando": "Presionar ESC",
            "descripcion": "Seña 'X' (número 23) ejecuta: Presionar ESC (PROTEGIDO)"
        }
        
        for zone in self.drop_zones:
            # Obtener la letra asignada (texto o imagen)
            letter = None
            if zone.box.text():
                letter = zone.box.text()
            elif hasattr(zone, 'current_letter'):
                letter = zone.current_letter
            
            if letter:  # Solo guardar si hay una letra asignada
                # Convertir letra a número (A=0, B=1, C=2, etc.)
                letter_number = str(ord(letter.upper()) - ord('A'))
                # Formato: "número": "comando"
                config[letter_number] = zone.command
                
                # Agregar información detallada para referencia
                config_details[letter_number] = {
                    "letra": letter.upper(),
                    "numero": int(letter_number),
                    "comando": zone.command,
                    "descripcion": f"Seña '{letter.upper()}' (número {letter_number}) ejecuta: {zone.command}"
                }
        
        # Crear JSON con información completa
        import time
        full_config = {
            "comandos": config,
            "detalles": config_details,
            "info": {
                "total_configurados": len(config),
                "formato": "letra A=0, B=1, C=2, ..., Z=25",
                "fecha_creacion": time.strftime("%Y-%m-%d %H:%M:%S"),
                "instrucciones": "El programa lee la sección 'comandos' para ejecutar los gestos",
                "configuracion_protegida": "X (#23) → Presionar ESC está siempre fijo"
            }
        }
        
        # Abrir diálogo para guardar archivo
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Guardar configuración",
            "configuracion_gestos.json",
            "Archivos JSON (*.json)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(full_config, f, ensure_ascii=False, indent=4)
                
                QtWidgets.QMessageBox.information(
                    self,
                    "Éxito",
                    f"✅ Configuración guardada exitosamente en:\n{file_path}\n\n"
                    f"📊 Resumen:\n"
                    f"• {len(config)} comandos configurados\n"
                    f"• Información detallada incluida\n"
                    f"• Formato: letra → número → comando",
                    QtWidgets.QMessageBox.StandardButton.Ok
                )
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al guardar la configuración:\n{str(e)}",
                    QtWidgets.QMessageBox.StandardButton.Ok
                )

    def start_gesture_control(self):
        """Iniciar el programa de control gestual"""
        try:
            # Bloquear botones mientras el control está activo
            self.start_btn.setEnabled(False)
            self.reset_btn.setEnabled(False)
            self.save_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            
            # Obtener la ruta del directorio actual
            current_dir = os.path.dirname(os.path.abspath(__file__))
            program_path = os.path.join(current_dir, "program.py")
            venv_path = os.path.join(current_dir, "venv_ml2", "Scripts", "python.exe")
            
            # Verificar si existe el entorno virtual
            if os.path.exists(venv_path):
                # Ejecutar con el entorno virtual
                self.gesture_process = subprocess.Popen([venv_path, program_path], cwd=current_dir)
                
                # Mostrar mensaje de confirmación
                QtWidgets.QMessageBox.information(
                    self,
                    "Control Gestual Iniciado",
                    "🎥 El control gestual se ha iniciado correctamente.\n\n"
                    "📋 Instrucciones:\n"
                    "• Usa tu mano izquierda para gestos ASL\n"
                    "• Usa tu mano derecha para control del cursor\n"
                    "• Mueve la mano derecha en el rectángulo azul\n"
                    "• Baja el dedo índice derecho para hacer clic\n"
                    "• Presiona ESC en la ventana del programa para salir\n\n"
                    "⚠️ Si no ves la ventana, revisa tu barra de tareas.\n"
                    "💡 Usa el botón 'Parar Control' para terminar desde aquí.",
                    QtWidgets.QMessageBox.StandardButton.Ok
                )
            else:
                # Ejecutar con Python del sistema
                self.gesture_process = subprocess.Popen([sys.executable, program_path], cwd=current_dir)
                
                QtWidgets.QMessageBox.information(
                    self,
                    "Control Gestual Iniciado",
                    "🎥 El control gestual se ha iniciado.\n\n"
                    "📋 Instrucciones:\n"
                    "• Usa tu mano izquierda para gestos ASL\n"
                    "• Usa tu mano derecha para control del cursor\n"
                    "• Mueve la mano derecha en el rectángulo azul\n"
                    "• Baja el dedo índice derecho para hacer clic\n"
                    "• Presiona ESC en la ventana del programa para salir\n\n"
                    "⚠️ Si hay errores, usa el entorno virtual (venv_ml2).\n"
                    "💡 Usa el botón 'Parar Control' para terminar desde aquí.",
                    QtWidgets.QMessageBox.StandardButton.Ok
                )
                
        except Exception as e:
            # Reactivar botones si hay error
            self.start_btn.setEnabled(True)
            self.reset_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            
            QtWidgets.QMessageBox.critical(
                self,
                "Error al Iniciar",
                f"❌ Error al iniciar el control gestual:\n\n{str(e)}\n\n"
                "💡 Sugerencias:\n"
                "• Verifica que program.py existe\n"
                "• Asegúrate de que las dependencias estén instaladas\n"
                "• Usa el entorno virtual (venv_ml2) si es necesario",
                QtWidgets.QMessageBox.StandardButton.Ok
            )

    def stop_gesture_control(self):
        """Parar el programa de control gestual"""
        try:
            if hasattr(self, 'gesture_process') and self.gesture_process:
                self.gesture_process.terminate()
                self.gesture_process = None
            
            # Reactivar botones
            self.start_btn.setEnabled(True)
            self.reset_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            
            QtWidgets.QMessageBox.information(
                self,
                "Control Detenido",
                "⏹️ El control gestual ha sido detenido correctamente.",
                QtWidgets.QMessageBox.StandardButton.Ok
            )
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self,
                "Advertencia",
                f"⚠️ Hubo un problema al detener el proceso:\n{str(e)}\n\n"
                "El proceso puede haber terminado por sí solo.",
                QtWidgets.QMessageBox.StandardButton.Ok
            )

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
