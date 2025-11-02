import json
from PyQt6.QtWidgets import QMessageBox
import sys

def load_exam_data(filename=None):
    """
    Load exam data from a JSON file.
    If filename is None, loads the default aws_mock_exam.json from exams folder
    """
    if filename is None:
        filename = "exams/aws_mock_exam.json"
    
    # If filename doesn't include path, assume it's in exams folder
    if not filename.startswith("exams/") and not "/" in filename:
        filename = f"exams/{filename}"
    
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to load exam data from {filename}: {str(e)}")
        sys.exit(1) 