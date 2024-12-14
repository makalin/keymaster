import sys
import json
import os
from pathlib import Path
from enum import Enum
from typing import Optional, Tuple, Dict

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QLabel, QPushButton, QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt, QPoint, QRect, QTimer, QEasingCurve, QPropertyAnimation
from PyQt6.QtGui import QPainter, QColor, QScreen, QKeyEvent, QMouseEvent, QIcon
import keyboard
import pyautogui

class MouseButton(Enum):
    LEFT = 'left'
    RIGHT = 'right'
    MIDDLE = 'middle'

class MouseAction(Enum):
    CLICK = 'click'
    DOUBLE_CLICK = 'double_click'
    DRAG = 'drag'

class Config:
    DEFAULT_CONFIG = {
        'grid_size': 8,
        'overlay_opacity': 0.5,
        'grid_color': '#FFFFFF',
        'background_color': '#000000',
        'font_size': 14,
        'smooth_movement': True,
        'movement_duration': 0.2,
        'hotkeys': {
            'show_grid': 'cmd',
            'dismiss_grid': 'esc',
            'right_click': 'right cmd',
            'middle_click': 'cmd+m',
            'start_drag': 'cmd+d'
        }
    }

    def __init__(self):
        self.config_path = Path.home() / '.keymaster' / 'config.json'
        self.load_config()

    def load_config(self):
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.settings = {**self.DEFAULT_CONFIG, **json.load(f)}
            else:
                self.settings = self.DEFAULT_CONFIG
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.settings = self.DEFAULT_CONFIG

    def save_config(self):
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

class SmoothCursor:
    def __init__(self, duration: float = 0.2):
        self.duration = duration
        self.animation = None

    def move_to(self, x: int, y: int):
        if not self.duration or self.duration <= 0:
            pyautogui.moveTo(x, y)
            return

        start_pos = pyautogui.position()
        steps = int(self.duration * 60)  # 60 FPS
        
        for i in range(steps + 1):
            t = i / steps
            # Use ease-out cubic function
            t = 1 - (1 - t) ** 3
            current_x = start_pos.x + (x - start_pos.x) * t
            current_y = start_pos.y + (y - start_pos.y) * t
            pyautogui.moveTo(current_x, current_y)
            QApplication.processEvents()

class GridOverlay(QWidget):
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                          Qt.WindowType.WindowStaysOnTopHint | 
                          Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.current_screen = 0
        self.screens = QApplication.screens()
        self.cursor = SmoothCursor(self.config.settings['movement_duration'])
        
        self.reset_state()
        self.setup_ui()

    def reset_state(self):
        self.first_key = None
        self.current_action = None
        self.drag_start = None
        self.current_button = MouseButton.LEFT
        self.active = False

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.update_screen_geometry()

    def update_screen_geometry(self):
        screen = self.screens[self.current_screen]
        self.screen_geometry = screen.geometry()
        self.setGeometry(self.screen_geometry)
        
        self.grid_size = self.config.settings['grid_size']
        self.cell_width = self.screen_geometry.width() // self.grid_size
        self.cell_height = self.screen_geometry.height() // self.grid_size
        
        self.labels = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                label = chr(65 + i) + str(j + 1)
                self.labels.append((label, QRect(
                    j * self.cell_width,
                    i * self.cell_height,
                    self.cell_width,
                    self.cell_height
                )))

    def paintEvent(self, event):
        if not self.active:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw semi-transparent background
        bg_color = QColor(self.config.settings['background_color'])
        bg_color.setAlphaF(self.config.settings['overlay_opacity'])
        painter.fillRect(self.rect(), bg_color)

        # Draw grid
        painter.setPen(QColor(self.config.settings['grid_color']))
        font = painter.font()
        font.setPointSize(self.config.settings['font_size'])
        painter.setFont(font)

        for i in range(self.grid_size + 1):
            x = i * self.cell_width
            y = i * self.cell_height
            painter.drawLine(x, 0, x, self.height())
            painter.drawLine(0, y, self.width(), y)

        # Draw cell labels
        for label, rect in self.labels:
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)

        # Draw current mode indicator
        mode_text = f"Mode: {self.current_button.value}"
        if self.current_action == MouseAction.DRAG:
            mode_text += " (Drag)"
        painter.drawText(10, 20, mode_text)

    def keyPressEvent(self, event: QKeyEvent):
        if not self.active:
            return

        key = event.text().upper()
        
        # Handle screen switching
        if event.key() == Qt.Key.Key_Left and self.current_screen > 0:
            self.current_screen -= 1
            self.update_screen_geometry()
            self.update()
            return
        elif event.key() == Qt.Key.Key_Right and self.current_screen < len(self.screens) - 1:
            self.current_screen += 1
            self.update_screen_geometry()
            self.update()
            return

        # Handle mouse button cycling
        if event.key() == Qt.Key.Key_Tab:
            self.cycle_mouse_button()
            self.update()
            return

        if not self.first_key:
            if key.isalpha():
                self.first_key = key
                self.update()
        else:
            if key.isdigit():
                cell = self.first_key + key
                self.perform_action(cell)
                self.reset_state()
                self.hide()

        if event.key() == Qt.Key.Key_Escape:
            self.reset_state()
            self.hide()

    def cycle_mouse_button(self):
        if self.current_button == MouseButton.LEFT:
            self.current_button = MouseButton.RIGHT
        elif self.current_button == MouseButton.RIGHT:
            self.current_button = MouseButton.MIDDLE
        else:
            self.current_button = MouseButton.LEFT

    def get_cell_center(self, cell: str) -> Optional[Tuple[int, int]]:
        for label, rect in self.labels:
            if label == cell:
                return (
                    rect.x() + rect.width() // 2 + self.screen_geometry.x(),
                    rect.y() + rect.height() // 2 + self.screen_geometry.y()
                )
        return None

    def perform_action(self, cell: str):
        coords = self.get_cell_center(cell)
        if not coords:
            return

        x, y = coords
        
        if self.config.settings['smooth_movement']:
            self.cursor.move_to(x, y)
        else:
            pyautogui.moveTo(x, y)

        if self.current_action == MouseAction.DRAG:
            if not self.drag_start:
                self.drag_start = (x, y)
                self.show()  # Keep overlay visible for end point
                return
            else:
                pyautogui.mouseDown(button=self.current_button.value)
                if self.config.settings['smooth_movement']:
                    self.cursor.move_to(x, y)
                else:
                    pyautogui.moveTo(x, y)
                pyautogui.mouseUp(button=self.current_button.value)
                self.drag_start = None
        else:
            if self.current_action == MouseAction.DOUBLE_CLICK:
                pyautogui.doubleClick(button=self.current_button.value)
            else:
                pyautogui.click(button=self.current_button.value)

class KeyMaster(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KeyMaster")
        self.config = Config()
        self.grid_overlay = GridOverlay(self.config)
        
        self.setup_tray()
        self.setup_global_hotkeys()

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("input-mouse"))
        
        tray_menu = QMenu()
        config_action = tray_menu.addAction("Settings")
        config_action.triggered.connect(self.show_settings)
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.quit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def setup_global_hotkeys(self):
        # Main grid activation
        keyboard.on_press_key(
            self.config.settings['hotkeys']['show_grid'],
            self.toggle_grid,
            suppress=True
        )
        
        # Right-click modifier
        keyboard.on_press_key(
            self.config.settings['hotkeys']['right_click'],
            lambda _: self.set_mouse_button(MouseButton.RIGHT),
            suppress=True
        )
        
        # Middle-click modifier
        keyboard.add_hotkey(
            self.config.settings['hotkeys']['middle_click'],
            lambda: self.set_mouse_button(MouseButton.MIDDLE),
            suppress=True
        )
        
        # Drag action
        keyboard.add_hotkey(
            self.config.settings['hotkeys']['start_drag'],
            lambda: self.start_drag(),
            suppress=True
        )

    def toggle_grid(self, e):
        if not self.grid_overlay.active:
            self.grid_overlay.active = True
            self.grid_overlay.show()
        else:
            self.grid_overlay.reset_state()
            self.grid_overlay.hide()

    def set_mouse_button(self, button: MouseButton):
        self.grid_overlay.current_button = button
        self.grid_overlay.update()

    def start_drag(self):
        self.grid_overlay.current_action = MouseAction.DRAG
        self.toggle_grid(None)

    def show_settings(self):
        # TODO: Implement settings dialog
        pass

def main():
    app = QApplication(sys.argv)
    window = KeyMaster()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()