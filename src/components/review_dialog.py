from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
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
        
        text_area.setText(content)
        layout.addWidget(text_area)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button) 