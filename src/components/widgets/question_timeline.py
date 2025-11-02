from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QScrollArea
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from src.components.styles import Styles


class QuestionTimelineWidget(QWidget):
    """Timeline widget displaying all questions as clickable buttons for practice mode."""
    
    question_selected = pyqtSignal(int)  # question_index
    
    def __init__(self, styles: Styles, total_questions: int):
        super().__init__()
        self.styles = styles
        self.colors = styles.colors
        self.total_questions = total_questions
        self.current_index = 0
        self.answered_questions = set()
        self.wrong_question_indices = set()
        self.buttons = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the timeline UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Create scroll area for horizontal scrolling
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: {self.colors['background']};
                height: 8px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: {self.colors['border']};
                min-width: 30px;
                border-radius: 4px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {self.colors['primary']};
            }}
        """)
        
        # Container for buttons
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(4, 4, 4, 4)
        buttons_layout.setSpacing(6)
        
        # Create buttons for each question
        for i in range(self.total_questions):
            button = QPushButton(str(i + 1))
            button.setFixedSize(36, 36)
            button.setFont(QFont('Helvetica', 11, QFont.Weight.Bold))
            button.clicked.connect(lambda checked, idx=i: self.on_button_clicked(idx))
            self._update_button_style(button, i)
            buttons_layout.addWidget(button)
            self.buttons.append(button)
        
        buttons_layout.addStretch()
        scroll.setWidget(buttons_widget)
        layout.addWidget(scroll)
    
    def _update_button_style(self, button: QPushButton, index: int):
        """Update button style based on question state."""
        is_current = index == self.current_index
        is_answered = index in self.answered_questions
        is_wrong = index in self.wrong_question_indices
        
        if is_current:
            # Current question - highlighted
            bg_color = self.colors['primary']
            text_color = 'white'
            border_color = self.colors['primary']
            border_width = 2
        elif is_wrong:
            # Wrong answer - red
            bg_color = self.colors['card']
            text_color = self.colors['warning']
            border_color = self.colors['warning']
            border_width = 2
        elif is_answered:
            # Answered correctly - green
            bg_color = self.colors['card']
            text_color = self.colors['correct']
            border_color = self.colors['correct']
            border_width = 2
        else:
            # Unanswered - default
            bg_color = self.colors['card']
            text_color = self.colors['text']
            border_color = self.colors['border']
            border_width = 1
        
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: {border_width}px solid {border_color};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['hover']};
                border: {border_width}px solid {self.colors['primary']};
            }}
        """)
    
    def on_button_clicked(self, index: int):
        """Handle button click to jump to question."""
        self.question_selected.emit(index)
    
    def update_current_index(self, index: int):
        """Update the current question index."""
        if 0 <= self.current_index < len(self.buttons):
            # Reset previous button
            self._update_button_style(self.buttons[self.current_index], self.current_index)
        
        self.current_index = index
        
        if 0 <= index < len(self.buttons):
            # Update new current button
            self._update_button_style(self.buttons[index], index)
    
    def update_answered_questions(self, answered_indices: set):
        """Update the set of answered questions."""
        self.answered_questions = answered_indices.copy()
        # Refresh all button styles
        for i, button in enumerate(self.buttons):
            self._update_button_style(button, i)
    
    def update_wrong_questions(self, wrong_indices: set):
        """Update the set of wrong answer question indices."""
        self.wrong_question_indices = wrong_indices.copy()
        # Refresh all button styles
        for i, button in enumerate(self.buttons):
            self._update_button_style(button, i)
    
    def update_colors(self, colors: dict):
        """Update colors when theme changes."""
        self.colors = colors
        # Refresh all button styles with new colors
        for i, button in enumerate(self.buttons):
            self._update_button_style(button, i)
