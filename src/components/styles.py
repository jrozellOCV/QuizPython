class Styles:
    def __init__(self):
        self.dark_mode = False
        self._init_colors()
        self._init_styles()
    
    def _init_colors(self):
        """Initialize color scheme based on dark mode state"""
        if self.dark_mode:
            self.colors = {
                'primary': '#3b82f6',      # Bright blue
                'primary_dark': '#2563eb', # Darker blue for hover
                'success': '#10b981',      # Green
                'success_dark': '#059669', # Darker green for hover
                'background': '#1e293b',   # Dark background
                'card': '#334155',         # Dark card
                'text': '#f1f5f9',         # Light text
                'text_light': '#cbd5e1',   # Lighter gray for secondary text
                'border': '#475569',       # Dark border
                'hover': '#475569',        # Dark hover
                'correct': '#10b981',      # Green for correct answers
                'disabled': '#64748b',     # Gray for disabled elements
                'warning': '#ef4444',      # Red for warnings
                'shadow': 'rgba(0, 0, 0, 0.3)'  # Darker shadow
            }
        else:
            self.colors = {
                'primary': '#2563eb',      # Bright blue
                'primary_dark': '#1d4ed8', # Darker blue for hover
                'success': '#059669',      # Green
                'success_dark': '#047857', # Darker green for hover
                'background': '#f8fafc',   # Light gray background
                'card': '#ffffff',       # White for cards
                'text': '#1e293b',         # Dark gray for text
                'text_light': '#64748b',   # Light gray for secondary text
                'border': '#e2e8f0',       # Light gray for borders
                'hover': '#f1f5f9',        # Light gray for hover states
                'correct': '#059669',      # Green for correct answers
                'disabled': '#94a3b8',     # Gray for disabled elements
                'warning': '#dc2626',      # Red for warnings
                'shadow': 'rgba(0, 0, 0, 0.1)'  # Subtle shadow
            }
    
    def toggle_dark_mode(self):
        """Toggle dark mode and regenerate styles"""
        self.dark_mode = not self.dark_mode
        self._init_colors()
        self._init_styles()
    
    def _init_styles(self):
        """Initialize styles based on current colors"""
        
        # Define standard styles
        self.styles = {
            'button': f"""
                QPushButton {{
                    background-color: {self.colors['primary']};
                    color: white;
                    padding: 12px 24px;
                    border-radius: 8px;
                    border: none;
                    font-weight: bold;
                    font-size: 14px;
                    min-height: 44px;
                    font-family: Helvetica, Arial;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['primary_dark']};
                }}
                QPushButton:pressed {{
                    background-color: {self.colors['primary_dark']};
                    padding-top: 13px;
                    padding-bottom: 11px;
                }}
                QPushButton:disabled {{
                    background-color: {self.colors['disabled']};
                }}
            """,
            'button_secondary': f"""
                QPushButton {{
                    background-color: {self.colors['card']};
                    color: {self.colors['text']};
                    padding: 12px 24px;
                    border-radius: 8px;
                    border: 1px solid {self.colors['border']};
                    font-weight: bold;
                    font-size: 14px;
                    min-height: 44px;
                    font-family: Helvetica, Arial;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['hover']};
                    border: 1px solid {self.colors['primary']};
                }}
                QPushButton:pressed {{
                    background-color: {self.colors['hover']};
                    border: 1px solid {self.colors['primary']};
                    padding-top: 13px;
                    padding-bottom: 11px;
                }}
                QPushButton:disabled {{
                    color: {self.colors['disabled']};
                }}
            """,
            'button_success': f"""
                QPushButton {{
                    background-color: {self.colors['success']};
                    color: white;
                    padding: 12px 24px;
                    border-radius: 8px;
                    border: none;
                    font-weight: bold;
                    font-size: 14px;
                    min-height: 44px;
                    font-family: Helvetica, Arial;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['success_dark']};
                }}
            """,
            'button_warning': f"""
                QPushButton {{
                    background-color: {self.colors['warning']};
                    color: white;
                    padding: 12px 24px;
                    border-radius: 8px;
                    border: none;
                    font-weight: bold;
                    font-size: 14px;
                    min-height: 44px;
                    font-family: Helvetica, Arial;
                }}
                QPushButton:hover {{
                    background-color: {'#dc2626' if not self.dark_mode else '#b91c1c'};
                }}
            """,
            'label': f"""
                QLabel {{
                    color: {self.colors['text']};
                    font-family: Helvetica, Arial;
                    padding: 5px;
                }}
            """,
            'label_title': f"""
                QLabel {{
                    color: {self.colors['primary']};
                    font-size: 28px;
                    font-weight: bold;
                    padding: 12px;
                    font-family: Helvetica, Arial;
                    line-height: 1.3;
                }}
            """,
            'label_subtitle': f"""
                QLabel {{
                    color: {self.colors['text']};
                    font-size: 18px;
                    padding: 8px;
                    font-family: Helvetica, Arial;
                    line-height: 1.4;
                }}
            """,
            'label_text': f"""
                QLabel {{
                    color: {self.colors['text']};
                    font-size: 15px;
                    padding: 6px;
                    font-family: Helvetica, Arial;
                    line-height: 1.5;
                }}
            """,
            'radio_button': f"""
                QRadioButton {{
                    padding: 16px;
                    margin: 8px 0;
                    background-color: {self.colors['card']};
                    border-radius: 8px;
                    border: 1px solid {self.colors['border']};
                    font-size: 14px;
                    min-height: 48px;
                    font-family: Helvetica, Arial;
                }}
                QRadioButton:hover {{
                    background-color: {self.colors['hover']};
                    border: 1px solid {self.colors['primary']};
                }}
                QRadioButton:pressed {{
                    background-color: {self.colors['hover']};
                    border: 1px solid {self.colors['primary']};
                    padding-top: 17px;
                    padding-bottom: 15px;
                }}
                QRadioButton::indicator {{
                    width: 22px;
                    height: 22px;
                    margin-right: 16px;
                    border-radius: 11px;
                }}
                QRadioButton::indicator:unchecked {{
                    border: 2px solid {self.colors['border']};
                    background-color: {self.colors['card']};
                }}
                QRadioButton::indicator:checked {{
                    border: 2px solid {self.colors['primary']};
                    background-color: {self.colors['primary']};
                }}
                QRadioButton:checked {{
                    background-color: {self.colors['hover']};
                    border: 1px solid {self.colors['primary']};
                    font-weight: bold;
                }}
            """,
            'card': f"""
                QWidget {{
                    background-color: {self.colors['card']};
                    border-radius: 12px;
                    border: 1px solid {self.colors['border']};
                    padding: 24px;
                    font-family: Helvetica, Arial;
                }}
            """
        }

    def get_application_style(self):
        return f"""
            QMainWindow {{
                background-color: {self.colors['background']};
            }}
            QWidget {{
                background-color: {self.colors['background']};
                color: {self.colors['text']};
                font-family: Helvetica, Arial;
            }}
            QScrollArea {{
                border: none;
                background-color: {self.colors['background']};
            }}
            QScrollBar:vertical {{
                border: none;
                background: {self.colors['background']};
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.colors['border']};
                min-height: 30px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self.colors['primary']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QProgressBar {{
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                text-align: center;
                height: 14px;
                background-color: {self.colors['card']};
                margin: 4px 0;
                font-family: Helvetica, Arial;
            }}
            QProgressBar::chunk {{
                background-color: {self.colors['primary']};
                border-radius: 8px;
            }}
            QStatusBar {{
                background-color: {self.colors['card']};
                border-top: 1px solid {self.colors['border']};
                padding: 10px;
                font-size: 14px;
                font-weight: 500;
                font-family: Helvetica, Arial;
            }}
        """ 