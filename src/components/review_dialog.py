from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QApplication
from PyQt6.QtGui import QFont

class ReviewDialog(QDialog):
    def __init__(self, wrong_answers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Review Incorrect Answers")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Create text area for review
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setFont(QFont('Helvetica', 12))
        
        # Format the review content
        content = ""
        for i, wa in enumerate(wrong_answers, 1):
            content += f"Question {i}:\n"
            content += f"Q: {wa['question']}\n"
            content += f"Your Answer: {wa['your_answer']}\n"
            content += f"Correct Answer: {wa['correct_answer']}\n"
            content += "-" * 50 + "\n\n"
        
        # Store content for clipboard copying
        self.content = content
        
        text_area.setText(content)
        layout.addWidget(text_area)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Copy to clipboard button
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(copy_button)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def copy_to_clipboard(self):
        """Copy the review content to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.content) 