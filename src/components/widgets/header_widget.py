from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from src.components.styles import Styles


class HeaderWidget(QWidget):
    """Header widget with dark mode toggle, pause button, and title."""
    
    dark_mode_toggled = pyqtSignal()
    pause_toggled = pyqtSignal()
    quit_clicked = pyqtSignal()
    
    def __init__(self, title: str, styles: Styles):
        super().__init__()
        self.styles = styles
        self.colors = styles.colors
        
        self.setup_ui(title)
    
    def setup_ui(self, title: str):
        """Set up the header UI."""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['card']};
                border-bottom: none;
            }}
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(30, 41, 59, 8))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 20)
        layout.setSpacing(12)
        
        # Button row
        button_row = QHBoxLayout()
        
        # Dark mode toggle button
        self.dark_mode_button = QPushButton("🌙")
        self.dark_mode_button.setFixedSize(40, 40)
        self.dark_mode_button.setToolTip("Toggle Dark Mode (Ctrl+D)")
        self.dark_mode_button.clicked.connect(self.dark_mode_toggled.emit)
        self.dark_mode_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['background']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['hover']};
            }}
        """)
        button_row.addWidget(self.dark_mode_button)
        
        # Pause button
        self.pause_button = QPushButton("⏸")
        self.pause_button.setFixedSize(40, 40)
        self.pause_button.setToolTip("Pause/Resume (Ctrl+P)")
        self.pause_button.clicked.connect(self.pause_toggled.emit)
        self.pause_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['background']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['hover']};
            }}
        """)
        button_row.addWidget(self.pause_button)
        
        # Quit Quiz button
        self.quit_button = QPushButton("Quit Quiz")
        self.quit_button.setFixedHeight(40)
        self.quit_button.setToolTip("Return to home page")
        self.quit_button.clicked.connect(self.quit_clicked.emit)
        self.quit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['background']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                font-size: 12px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['hover']};
            }}
        """)
        button_row.addWidget(self.quit_button)
        
        # Add button row to main layout
        layout.addLayout(button_row)
        
        # Title (centered)
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont('Helvetica', 18, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(self.styles.styles['label_title'])
        layout.addWidget(self.title_label)
    
    def update_dark_mode(self, is_dark: bool):
        """Update dark mode button icon."""
        self.dark_mode_button.setText("☀️" if is_dark else "🌙")
    
    def update_pause_state(self, is_paused: bool):
        """Update pause button state."""
        self.pause_button.setText("▶" if is_paused else "⏸")
        self.pause_button.setToolTip("Resume (Ctrl+P)" if is_paused else "Pause (Ctrl+P)")
    
    def set_practice_mode(self, enabled: bool):
        """Show or hide pause button based on practice mode."""
        self.pause_button.setVisible(not enabled)
    
    def update_colors(self, colors: dict):
        """Update colors when theme changes."""
        self.colors = colors
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['card']};
                border-bottom: none;
            }}
        """)
        self.dark_mode_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['background']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['hover']};
            }}
        """)
        self.pause_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['background']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['hover']};
            }}
        """)
        self.quit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['background']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                font-size: 12px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['hover']};
            }}
        """)

