from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.components.styles import Styles


class QuestionDisplayWidget(QWidget):
    """Widget for displaying question text and answer feedback."""
    
    def __init__(self, styles: Styles):
        super().__init__()
        self.styles = styles
        self.colors = styles.colors
        self._current_answer_state = None  # Track answer state for dark mode updates
        self._current_answer_text = None
        self._current_answer_type = None  # 'feedback', 'review', or None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the question display UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Question label
        self.question_label = QLabel()
        self.question_label.setFont(QFont('Helvetica', 16))
        self.question_label.setWordWrap(True)
        self.question_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.question_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text']};
                background-color: {self.colors['card']};
                padding: 20px;
                border-radius: 10px;
                border: 1px solid {self.colors['border']};
            }}
        """)
        layout.addWidget(self.question_label)
        
        # Selection indicator
        self.selection_indicator = QLabel()
        self.selection_indicator.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text_light']};
                font-size: 14px;
            }}
        """)
        self.selection_indicator.hide()
        layout.addWidget(self.selection_indicator)
        
        # Answer label
        self.answer_label = QLabel()
        self.answer_label.setFont(QFont('Helvetica', 14))
        self.answer_label.setWordWrap(True)
        self.answer_label.hide()
        layout.addWidget(self.answer_label)
    
    def set_question(self, question_text: str):
        """Set the question text."""
        self.question_label.setText(question_text)
        self.question_label.show()
    
    def set_selection(self, selection_text: str):
        """Set the selection indicator text."""
        if selection_text:
            self.selection_indicator.setText(selection_text)
            self.selection_indicator.show()
        else:
            self.selection_indicator.hide()
    
    def set_answer_feedback(self, feedback_text: str, is_correct: bool, style_class: str = ""):
        """Set the answer feedback text and style."""
        self.answer_label.setText(feedback_text)
        # Store state for dark mode updates
        self._current_answer_state = (is_correct, style_class)
        self._current_answer_text = feedback_text
        self._current_answer_type = 'feedback'
        
        if style_class == "correct":
            self.answer_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {self.colors['card']};
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid {self.colors['correct']};
                    color: {self.colors['correct']};
                }}
            """)
        elif style_class == "incorrect":
            self.answer_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {self.colors['card']};
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid {self.colors['warning']};
                    color: {self.colors['warning']};
                }}
            """)
        else:
            self.answer_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {self.colors['card']};
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid {self.colors['border']};
                    color: {self.colors['text']};
                }}
            """)
        
        self.answer_label.show()
    
    def set_review_answer(self, your_answer: str, correct_answer: str):
        """Set answer text for review mode."""
        answer_text = f"<b>Your Answer:</b> {your_answer}<br><br>"
        answer_text += f"<b>Correct Answer:</b> {correct_answer}"
        self.answer_label.setText(answer_text)
        # Store state for dark mode updates
        self._current_answer_state = (False, 'review')
        self._current_answer_text = (your_answer, correct_answer)
        self._current_answer_type = 'review'
        
        self.answer_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.colors['card']};
                padding: 20px;
                border-radius: 10px;
                border: 1px solid {self.colors['warning']};
                color: {self.colors['text']};
            }}
        """)
        self.answer_label.show()
    
    def hide_answer(self):
        """Hide the answer label."""
        self.answer_label.hide()
        self._current_answer_state = None
        self._current_answer_text = None
        self._current_answer_type = None
    
    def hide_selection(self):
        """Hide the selection indicator."""
        self.selection_indicator.hide()
    
    def update_colors(self, colors: dict):
        """Update colors when theme changes."""
        self.colors = colors
        self.question_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text']};
                background-color: {self.colors['card']};
                padding: 20px;
                border-radius: 10px;
                border: 1px solid {self.colors['border']};
            }}
        """)
        self.selection_indicator.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text_light']};
                font-size: 14px;
            }}
        """)
        
        # Update answer label if it's visible
        if self.answer_label.isVisible() and self._current_answer_type:
            if self._current_answer_type == 'feedback' and self._current_answer_state:
                is_correct, style_class = self._current_answer_state
                self.set_answer_feedback(self._current_answer_text, is_correct, style_class)
            elif self._current_answer_type == 'review' and isinstance(self._current_answer_text, tuple):
                your_answer, correct_answer = self._current_answer_text
                self.set_review_answer(your_answer, correct_answer)

