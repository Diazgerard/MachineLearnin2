import sys
import subprocess
import os
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QLabel, QPushButton, QAbstractItemView, QFrame,
    QGridLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont

class DropZone(QFrame):
    def __init__(self, command: str, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.command = command
        
        layout = QVBoxLayout(self)
        
        # Crear el cuadrado para soltar
        self.box = QLabel()
        self.box.setFixedSize(110, 110)  # Reducimos un poco el tamaño para mejor distribución
        self.box.setCursor(Qt.CursorShape.PointingHandCursor)  # Cambiar cursor al pasar por encima
        self.box.setToolTip("Haz clic para limpiar el gesto")  # Tooltip informativo
        self.box.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                border: 3px dashed #6c757d;
                border-radius: 15px;
                font-size: 48px;
                qproperty-alignment: AlignCenter;
            }
        """)
        layout.addWidget(self.box, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Etiqueta para el comando
        self.label = QLabel(command)
        self.label.setStyleSheet("""
            font-size: 12px;
            color: white;
            font-weight: bold;
        """)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
    def mousePressEvent(self, event):
        if self.box.text():  # Solo si hay un gesto asignado
            gesture_to_return = self.box.text()
            self.box.setText("")
            self.box.setStyleSheet("""
                QLabel {
                    background-color: #ffffff;
                    border: 3px dashed #6c757d;
                    border-radius: 15px;
                    font-size: 48px;
                    qproperty-alignment: AlignCenter;
                }
            """)
            
            # Devolver el gesto a la lista disponible
            main_window = self.get_main_window()
            if main_window:
                main_window.return_gesture_to_list(gesture_to_return)
        
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
            gesture = event.mimeData().text()
            
            # Verificar si el gesto ya está asignado en otra zona
            main_window = self.get_main_window()
            if main_window and main_window.is_gesture_assigned(gesture, self):
                return  # No permitir la asignación si ya está usado
            
            # Si había un gesto anterior, devolverlo a la lista
            if self.box.text():
                main_window.return_gesture_to_list(self.box.text())
            
            self.box.setText(gesture)
            self.box.setStyleSheet("""
                QLabel {
                    background-color: #e8f5e9;
                    border: 3px solid #4caf50;
                    border-radius: 15px;
                    padding: 10px;
                    font-size: 48px;
                    qproperty-alignment: AlignCenter;
                }
            """)
            
            # Remover el gesto de la lista disponible
            if main_window:
                main_window.remove_gesture_from_list(gesture)
            
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
        self.setStyleSheet("""
            QListWidget {
                background-color: #1e293b;  /* Color de fondo del panel - azul oscuro */
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                margin: 4px;
                background-color: #334155;  /* Color de fondo de cada item - azul medio */
                border: 2px solid #475569;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                color: #f1f5f9;  /* Color del texto - blanco suave */
            }
            QListWidget::item:selected {
                background-color: #3b82f6;  /* Color cuando está seleccionado - azul brillante */
                border-color: #60a5fa;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #2563eb;  /* Color al pasar el mouse - azul más claro */
                border-color: #93c5fd;
                color: #ffffff;
            }
        """)

    def startDrag(self, actions):
        item = self.currentItem()
        if item:
            # Extraer solo el emoji (primer carácter) del texto
            emoji = item.text().split()[0]
            drag = QtGui.QDrag(self)
            mimeData = QtCore.QMimeData()
            mimeData.setText(emoji)
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
            "• Arrastra los gestos de la izquierda a las zonas de la derecha\n"
            "• Cada gesto puede asignarse a un comando\n"
            "• Personaliza el control gestual de tu computadora"
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: white; font-size: 14px; font-weight: bold; padding: 10px;")
        root.addWidget(info)

        # Contenedor principal
        container = QHBoxLayout()
        root.addLayout(container)

        # Panel izquierdo
        left_panel = QVBoxLayout()
        left_label = QLabel("Gestos disponibles:")
        left_panel.addWidget(left_label)
        
        self.left = DnDListWidget("left")
        gestures = [
            ("✋ Mano abierta", "Gesto de mano abierta"),
            ("✊ Puño cerrado", "Gesto de puño cerrado"),
            ("👍 Pulgar arriba", "Gesto de pulgar arriba"),
            ("👆 Señalando", "Gesto señalando"),
            ("🤏 Pellizco", "Gesto de pellizco"),
            ("✌️ Paz y amor", "Gesto de paz y amor"),
            ("🤙 Llamando", "Gesto de llamada"),
            ("👉 Señalando hacia la derecha", "Gesto señalando a la derecha"),
            ("👈 Señalando hacia la izquierda", "Gesto señalando a la izquierda"),
            ("👆 Señalando hacia arriba", "Gesto señalando arriba"),
            ("👇 Señalando hacia abajo", "Gesto señalando abajo"),
            ("🫳 Palma Abajo", "Gesto de palma hacia abajo"),
            ("👌 Ok", "Gesto de OK"),
            ("🤟 Cuernos", "Gesto de cuernos")
        ]
        self.left.addItems([g[0] for g in gestures])
        # Agregar tooltips
        for i, (_, tooltip) in enumerate(gestures):
            item = self.left.item(i)
            if item:
                item.setToolTip(tooltip)
        self.left.setFixedWidth(200)
        left_panel.addWidget(self.left)
        container.addLayout(left_panel)

        # Panel derecho con grid de zonas para soltar y scroll
        right_panel = QVBoxLayout()
        right_label = QLabel("Asigna gestos a comandos:")
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
            "Clic izquierdo",
            "Clic derecho",
            "Copiar (Ctrl+C)",
            "Pegar (Ctrl+V)",
            "Deshacer (Ctrl+Z)",
            "Alt+Tab",
            "Cerrar Ventana",
            "Windows",
            "Grabar Pantalla",
            "Subir Volumen",
            "Bajar Volumen",
            "Silenciar",
            "Captura de Pantalla",
            "Cerrar Sesion",
            "Abrir Explorador de Archivos",
            "Minimizar Ventana"
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
        start_btn = QPushButton("🚀 Iniciar Control Gestual")
        start_btn.clicked.connect(self.start_gesture_control)
        start_btn.setStyleSheet("""
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
        """)
        btns.addWidget(start_btn)
        
        # Botón de reinicio
        reset_btn = QPushButton("🔄 Reiniciar todo")
        reset_btn.clicked.connect(self.reset)
        btns.addWidget(reset_btn)
        
        # Botón de guardar
        save_btn = QPushButton("💾 Guardar configuración")
        save_btn.clicked.connect(self.save_configuration)
        save_btn.setStyleSheet("""
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
        """)
        btns.addWidget(save_btn)
        
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

    def is_gesture_assigned(self, gesture, current_zone):
        """Verificar si un gesto ya está asignado en otra zona"""
        for zone in self.drop_zones:
            if zone != current_zone and zone.box.text() == gesture:
                return True
        return False
    
    def remove_gesture_from_list(self, gesture):
        """Remover un gesto de la lista de gestos disponibles"""
        for i in range(self.left.count()):
            item = self.left.item(i)
            if item and item.text().startswith(gesture):
                self.left.takeItem(i)
                break
    
    def return_gesture_to_list(self, gesture):
        """Devolver un gesto a la lista de gestos disponibles"""
        # Encontrar el nombre completo del gesto
        gesture_names = {
            "✋": ("✋ Mano abierta", "Gesto de mano abierta"),
            "✊": ("✊ Puño cerrado", "Gesto de puño cerrado"),
            "👍": ("👍 Pulgar arriba", "Gesto de pulgar arriba"),
            "👆": ("👆 Señalando", "Gesto señalando"),
            "🤏": ("🤏 Pellizco", "Gesto de pellizco"),
            "✌️": ("✌️ Paz y amor", "Gesto de paz y amor"),
            "🤙": ("🤙 Llamando", "Gesto de llamada"),
            "👉": ("👉 Señalando hacia la derecha", "Gesto señalando a la derecha"),
            "👈": ("👈 Señalando hacia la izquierda", "Gesto señalando a la izquierda"),
            "👇": ("👇 Señalando hacia abajo", "Gesto señalando abajo"),
            "🫳": ("🫳 Palma Abajo", "Gesto de palma hacia abajo"),
            "👌": ("👌 Ok", "Gesto de OK"),
            "🤟": ("🤟 Cuernos", "Gesto de cuernos")
        }
        
        if gesture in gesture_names:
            full_text, tooltip = gesture_names[gesture]
            # Verificar que no esté ya en la lista
            for i in range(self.left.count()):
                item = self.left.item(i)
                if item and item.text().startswith(gesture):
                    return  # Ya está en la lista
            
            # Agregar de vuelta a la lista
            self.left.addItem(full_text)
            # Agregar tooltip al último item agregado
            last_item = self.left.item(self.left.count() - 1)
            if last_item:
                last_item.setToolTip(tooltip)

    def reset(self):
        self.left.clear()
        gestures = [
            ("✋ Mano abierta", "Gesto de mano abierta"),
            ("✊ Puño cerrado", "Gesto de puño cerrado"),
            ("👍 Pulgar arriba", "Gesto de pulgar arriba"),
            ("👆 Señalando", "Gesto señalando"),
            ("🤏 Pellizco", "Gesto de pellizco"),
            ("✌️ Paz y amor", "Gesto de paz y amor"),
            ("🤙 Llamando", "Gesto de llamada"),
            ("👉 Señalando hacia la derecha", "Gesto señalando a la derecha"),
            ("👈 Señalando hacia la izquierda", "Gesto señalando a la izquierda"),
            ("👆 Señalando hacia arriba", "Gesto señalando arriba"),
            ("👇 Señalando hacia abajo", "Gesto señalando abajo"),
            ("🫳 Palma Abajo", "Gesto de palma hacia abajo"),
            ("👌 Ok", "Gesto de OK"),
            ("🤟 Cuernos", "Gesto de cuernos")
        ]
        self.left.addItems([g[0] for g in gestures])
        # Agregar tooltips
        for i, (_, tooltip) in enumerate(gestures):
            item = self.left.item(i)
            if item:
                item.setToolTip(tooltip)
        self.clear_zones()

    def clear_zones(self):
        # Esta función solo se usa para el reset completo
        for zone in self.drop_zones:
            if zone.box.text():  # Si hay un gesto asignado, devolverlo a la lista
                self.return_gesture_to_list(zone.box.text())
            zone.box.setText("")
            zone.box.setStyleSheet("""
                QLabel {
                    background-color: #ffffff;
                    border: 3px dashed #6c757d;
                    border-radius: 15px;
                    font-size: 48px;
                    qproperty-alignment: AlignCenter;
                }
            """)
    
    def get_gesture_names(self):
        # Obtener los nombres de los gestos del listado original
        gesture_names = {}
        for i in range(self.left.count()):
            item = self.left.item(i)
            if item:
                text = item.text()
                # El emoji es el primer carácter, el resto es el nombre
                emoji = text.split()[0]
                name = ' '.join(text.split()[1:])
                gesture_names[emoji] = name
        return gesture_names

    def save_configuration(self):
        # Crear un diccionario con las asignaciones actuales
        config = {}
        
        # Mapeo de emojis a nombres completos de gestos
        emoji_to_gesture_name = {
            "✋": "Mano abierta",
            "✊": "Puño cerrado", 
            "👍": "Pulgar arriba",
            "👆": "Señalando",
            "🤏": "Pellizco",
            "✌️": "Paz y amor",
            "🤙": "Llamando",
            "👉": "Señalando hacia la derecha",
            "👈": "Señalando hacia la izquierda", 
            "👇": "Señalando hacia abajo",
            "🫳": "Palma Abajo",
            "👌": "Ok",
            "🤟": "Cuernos"
        }
        
        for zone in self.drop_zones:
            gesture_emoji = zone.box.text()
            if gesture_emoji:  # Solo guardar si hay un gesto asignado
                # Convertir emoji a nombre del gesto
                gesture_name = emoji_to_gesture_name.get(gesture_emoji, gesture_emoji)
                config[zone.command] = gesture_name
        
        if not config:
            # Si no hay asignaciones, mostrar mensaje
            QtWidgets.QMessageBox.warning(
                self,
                "Configuración vacía",
                "No hay gestos asignados para guardar.",
                QtWidgets.QMessageBox.StandardButton.Ok
            )
            return
        
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
                    json.dump(config, f, ensure_ascii=False, indent=4)
                
                QtWidgets.QMessageBox.information(
                    self,
                    "Éxito",
                    f"Configuración guardada exitosamente en:\n{file_path}",
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
            # Obtener la ruta del directorio actual
            current_dir = os.path.dirname(os.path.abspath(__file__))
            program_path = os.path.join(current_dir, "program.py")
            venv_path = os.path.join(current_dir, "venv_ml2", "Scripts", "python.exe")
            
            # Verificar si existe el entorno virtual
            if os.path.exists(venv_path):
                # Ejecutar con el entorno virtual
                subprocess.Popen([venv_path, program_path], cwd=current_dir)
                
                # Mostrar mensaje de confirmación
                QtWidgets.QMessageBox.information(
                    self,
                    "Control Gestual Iniciado",
                    "🎥 El control gestual se ha iniciado correctamente.\n\n"
                    "📋 Instrucciones:\n"
                    "• Usa tu mano derecha frente a la cámara\n"
                    "• Mueve la mano en el rectángulo azul para controlar el cursor\n"
                    "• Baja el dedo índice para hacer clic\n"
                    "• Presiona ESC para salir\n\n"
                    "⚠️ Si no ves la ventana, revisa tu barra de tareas.",
                    QtWidgets.QMessageBox.StandardButton.Ok
                )
            else:
                # Ejecutar con Python del sistema
                subprocess.Popen([sys.executable, program_path], cwd=current_dir)
                
                QtWidgets.QMessageBox.information(
                    self,
                    "Control Gestual Iniciado",
                    "🎥 El control gestual se ha iniciado.\n\n"
                    "📋 Instrucciones:\n"
                    "• Usa tu mano derecha frente a la cámara\n"
                    "• Mueve la mano en el rectángulo azul para controlar el cursor\n"
                    "• Baja el dedo índice para hacer clic\n"
                    "• Presiona ESC para salir\n\n"
                    "⚠️ Si hay errores, usa el entorno virtual (venv_ml2).",
                    QtWidgets.QMessageBox.StandardButton.Ok
                )
                
        except Exception as e:
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

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
