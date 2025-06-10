import json
from PyQt6.QtWidgets import QMessageBox
import sys

def load_exam_data():
    try:
        with open("aws_mock_exam.json", "r") as f:
            return json.load(f)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to load exam data: {str(e)}")
        sys.exit(1) 