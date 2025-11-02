from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, QPushButton, 
                            QHBoxLayout, QLabel)
from PyQt6.QtGui import QFont
from src.components.styles import BUTTON_SUCCESS, BUTTON_WARNING, BUTTON_SECONDARY

class ReviewDialog(QDialog):
    def __init__(self, question, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Review Question")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Create text area for review
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setFont(QFont('Helvetica', 12))
        
        # Format the review content
        content = f"Q: {question['question']}\n\n"
        content += "Options:\n"
        for key, value in question['options'].items():
            content += f"{key}. {value}\n"
        content += f"\nCorrect Answer: {question['options'][question['answer']]}"
        
        text_area.setText(content)
        layout.addWidget(text_area)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Known/Unknown buttons (for flashcard mode)
        self.known_button = QPushButton("✓ I Know This")
        self.known_button.setStyleSheet(BUTTON_SUCCESS)
        button_layout.addWidget(self.known_button)
        
        self.unknown_button = QPushButton("✗ Need More Review")
        self.unknown_button.setStyleSheet(BUTTON_WARNING)
        button_layout.addWidget(self.unknown_button)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet(BUTTON_SECONDARY)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout) 