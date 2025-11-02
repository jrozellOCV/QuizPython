from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QListWidget, 
                            QDialogButtonBox, QPushButton, QSizePolicy)
from PyQt6.QtCore import Qt

class SessionSelectDialog(QDialog):
    def __init__(self, sessions, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resume Study Session")
        self.setMinimumSize(500, 500)
        self.sessions = sessions
        
        layout = QVBoxLayout(self)
        
        # Add description
        description = QLabel("Select a previous study session to resume:")
        description.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(description)
        
        # Create list widget for sessions
        self.session_list = QListWidget()
        self.session_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.session_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e0e0e0;
            }
        """)
        
        # Add sessions to list
        for session in sessions:
            self.session_list.addItem(session["session_date"])
        
        layout.addWidget(self.session_list, stretch=1)
        
        # Add buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_selected_session_index(self):
        """Return the index of the selected session."""
        return self.session_list.currentRow() 