from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QDialogButtonBox, QTabWidget, QWidget, QGridLayout)
from PyQt6.QtCore import Qt

class SessionStatsDialog(QDialog):
    def __init__(self, session_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Session Statistics")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Overview tab
        overview_tab = QWidget()
        overview_layout = QGridLayout(overview_tab)
        
        # Session info
        session_date = datetime.fromisoformat(session_data["session_date"])
        overview_layout.addWidget(QLabel("Session Date:"), 0, 0)
        overview_layout.addWidget(QLabel(session_date.strftime("%Y-%m-%d %H:%M")), 0, 1)
        
        overview_layout.addWidget(QLabel("Exam Title:"), 1, 0)
        overview_layout.addWidget(QLabel(session_data["exam_title"]), 1, 1)
        
        overview_layout.addWidget(QLabel("Total Questions:"), 2, 0)
        overview_layout.addWidget(QLabel(str(session_data["total_questions"])), 2, 1)
        
        # Quiz stats
        quiz_data = session_data["quiz_mode"]
        if quiz_data["total_answered"] > 0:
            correct_percentage = (quiz_data["score"] / quiz_data["total_answered"]) * 100
            overview_layout.addWidget(QLabel("Quiz Score:"), 3, 0)
            overview_layout.addWidget(QLabel(f"{quiz_data['score']}/{quiz_data['total_answered']} ({correct_percentage:.1f}%)"), 3, 1)
            
            overview_layout.addWidget(QLabel("Completion Rate:"), 4, 0)
            completion_rate = (quiz_data["total_answered"] / session_data["total_questions"]) * 100
            overview_layout.addWidget(QLabel(f"{completion_rate:.1f}%"), 4, 1)
        
        # Add overview tab
        tabs.addTab(overview_tab, "Overview")
        
        # Quiz Analysis tab
        quiz_tab = QWidget()
        quiz_layout = QVBoxLayout(quiz_tab)
        
        if quiz_data["total_answered"] > 0:
            # Performance metrics
            metrics_widget = QWidget()
            metrics_layout = QGridLayout(metrics_widget)
            
            # Calculate additional metrics
            wrong_count = len(quiz_data["incorrect_answers"])
            correct_count = quiz_data["score"]
            total_attempted = quiz_data["total_answered"]
            
            metrics_layout.addWidget(QLabel("Performance Metrics:"), 0, 0, 1, 2)
            metrics_layout.addWidget(QLabel("Correct Answers:"), 1, 0)
            metrics_layout.addWidget(QLabel(f"{correct_count} ({correct_count/total_attempted*100:.1f}%)"), 1, 1)
            
            metrics_layout.addWidget(QLabel("Incorrect Answers:"), 2, 0)
            metrics_layout.addWidget(QLabel(f"{wrong_count} ({wrong_count/total_attempted*100:.1f}%)"), 2, 1)
            
            metrics_layout.addWidget(QLabel("Accuracy Rate:"), 3, 0)
            metrics_layout.addWidget(QLabel(f"{(correct_count/total_attempted*100):.1f}%"), 3, 1)
            
            quiz_layout.addWidget(metrics_widget)
            
            # Wrong answers review
            if wrong_count > 0:
                wrong_answers_widget = QWidget()
                wrong_answers_layout = QVBoxLayout(wrong_answers_widget)
                
                wrong_answers_layout.addWidget(QLabel("Incorrect Answers Review:"))
                for i, wa in enumerate(quiz_data["incorrect_answers"], 1):
                    wrong_text = f"{i}. Q: {wa['question']}\n   Your Answer: {wa['your_answer']}\n   Correct Answer: {wa['correct_answer']}\n"
                    wrong_answers_layout.addWidget(QLabel(wrong_text))
                
                quiz_layout.addWidget(wrong_answers_widget)
        else:
            quiz_layout.addWidget(QLabel("No quiz data available for this session"))
        
        tabs.addTab(quiz_tab, "Quiz Analysis")
        
        layout.addWidget(tabs)
        
        # Add close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Style the dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                font-size: 12px;
                padding: 5px;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 2px;
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 1px solid #ffffff;
            }
        """) 