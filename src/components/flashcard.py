from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont

class FlashCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(400)
        self.is_flipped = False
        self.animation = None
        
        # Create stacked widget for front and back
        self.stack = QStackedWidget()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)
        
        # Front of card (question with choices)
        self.front = QWidget()
        front_layout = QVBoxLayout(self.front)
        front_layout.setSpacing(15)
        
        # Question label
        self.question_label = QLabel()
        self.question_label.setFont(QFont('Helvetica', 16, QFont.Weight.Bold))
        self.question_label.setWordWrap(True)
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        front_layout.addWidget(self.question_label)
        
        # Choices container
        self.front_choices = QWidget()
        self.front_choices_layout = QVBoxLayout(self.front_choices)
        self.front_choices_layout.setSpacing(10)
        front_layout.addWidget(self.front_choices)
        
        self.stack.addWidget(self.front)
        
        # Back of card (just the answer)
        self.back = QWidget()
        back_layout = QVBoxLayout(self.back)
        back_layout.setSpacing(15)
        
        # Answer label
        self.answer_label = QLabel()
        self.answer_label.setFont(QFont('Helvetica', 24, QFont.Weight.Bold))
        self.answer_label.setWordWrap(True)
        self.answer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        back_layout.addWidget(self.answer_label)
        
        # Add some spacing at the top and bottom
        back_layout.addStretch()
        back_layout.addWidget(self.answer_label)
        back_layout.addStretch()
        
        self.stack.addWidget(self.back)
        
        # Style the card
        self.setStyleSheet(f"""
            FlashCard {{
                background-color: {self.parent().colors['card']};
                border-radius: 15px;
                border: 2px solid {self.parent().colors['border']};
            }}
            QLabel {{
                padding: 20px;
                color: {self.parent().colors['text']};
            }}
            .choice-label {{
                padding: 15px;
                border-radius: 8px;
                background-color: {self.parent().colors['background']};
                border: 1px solid {self.parent().colors['border']};
            }}
            #answer_label {{
                color: {self.parent().colors['success']};
                font-size: 24px;
                font-weight: bold;
            }}
        """)
        
        # Make the entire card clickable
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.flip()
    
    def flip(self):
        if self.animation and self.animation.state() == QPropertyAnimation.State.Running:
            return
            
        # Create flip animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Get current geometry
        current_geo = self.geometry()
        
        # Animate to flipped state
        if not self.is_flipped:
            self.animation.setStartValue(current_geo)
            self.animation.setEndValue(current_geo)
            self.stack.setCurrentIndex(1)
        else:
            self.animation.setStartValue(current_geo)
            self.animation.setEndValue(current_geo)
            self.stack.setCurrentIndex(0)
        
        self.animation.start()
        self.is_flipped = not self.is_flipped

    def clear_choices(self):
        # Clear front choices
        while self.front_choices_layout.count():
            item = self.front_choices_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def setContent(self, question, answer, options):
        # Set question
        self.question_label.setText(question)
        
        # Set answer (just the letter)
        self.answer_label.setText(answer)
        self.answer_label.setObjectName("answer_label")  # For styling
        
        # Clear previous choices
        self.clear_choices()
        
        # Add choices to front
        for key, value in options.items():
            choice_label = QLabel(f"{key}. {value}")
            choice_label.setFont(QFont('Helvetica', 14))
            choice_label.setWordWrap(True)
            choice_label.setProperty("class", "choice-label")
            self.front_choices_layout.addWidget(choice_label)
        
        # Reset card state
        self.is_flipped = False
        self.stack.setCurrentIndex(0) 