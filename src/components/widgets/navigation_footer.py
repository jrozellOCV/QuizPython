from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from src.components.styles import Styles
from src.components.widgets.question_timeline import QuestionTimelineWidget


class NavigationFooterWidget(QWidget):
    """Footer widget with progress bar and navigation buttons."""
    
    prev_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    action_clicked = pyqtSignal()
    study_clicked = pyqtSignal()
    question_jumped = pyqtSignal(int)  # question_index for practice mode
    
    def __init__(self, styles: Styles, total_questions: int, practice_mode: bool = False, quiz_state=None):
        super().__init__()
        self.styles = styles
        self.colors = styles.colors
        self.total_questions = total_questions
        self.practice_mode = practice_mode
        self.quiz_state = quiz_state
        
        self.timeline_widget = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the navigation footer UI."""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['card']};
                border-top: 1px solid {self.colors['border']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 20, 32, 20)
        
        # Progress bar (hidden in practice mode)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.total_questions)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                text-align: center;
                height: 12px;
                background-color: {self.colors['card']};
            }}
            QProgressBar::chunk {{
                background-color: {self.colors['primary']};
                border-radius: 8px;
            }}
        """)
        layout.addWidget(self.progress_bar)
        
        # Timeline widget (shown only in practice mode)
        if self.practice_mode:
            self.timeline_widget = QuestionTimelineWidget(self.styles, self.total_questions)
            self.timeline_widget.question_selected.connect(self.on_timeline_question_selected)
            layout.insertWidget(0, self.timeline_widget)
            self.progress_bar.hide()
        else:
            self.progress_bar.show()
        
        # Navigation container
        nav_container = QWidget()
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 10, 0, 0)
        
        # Previous button
        self.prev_button = QPushButton("← Previous")
        self.prev_button.setStyleSheet(self.styles.styles['button_secondary'])
        self.prev_button.clicked.connect(self.prev_clicked.emit)
        nav_layout.addWidget(self.prev_button)
        
        # Question counter
        self.nav_label = QLabel()
        self.nav_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self.nav_label)
        
        # Combined Confirm/Next button
        self.action_button = QPushButton("Confirm Answer")
        self.action_button.setFont(QFont('Helvetica', 12))
        self.action_button.setStyleSheet(self.styles.styles['button'])
        self.action_button.clicked.connect(self.action_clicked.emit)
        self.action_button.setEnabled(False)
        nav_layout.addWidget(self.action_button)
        
        # Study button (initially hidden, shown in review mode)
        self.study_button = QPushButton("📚 Study These Questions")
        self.study_button.setStyleSheet(self.styles.styles['button'])
        self.study_button.hide()
        self.study_button.clicked.connect(self.study_clicked.emit)
        nav_layout.insertWidget(1, self.study_button)
        
        layout.addWidget(nav_container)
    
    def update_progress(self, current: int, total: int):
        """Update progress bar and question counter."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        
        counter_text = f"Question {current} of {total}"
        self.nav_label.setText(counter_text)
        
        # Update timeline if in practice mode
        if self.timeline_widget:
            self.timeline_widget.update_current_index(current - 1)  # Convert to 0-based index
            if self.quiz_state:
                self.timeline_widget.update_answered_questions(self.quiz_state.answered_questions)
                # Update wrong questions based on wrong_answers
                wrong_indices = set()
                if self.quiz_state.wrong_answers:
                    for wrong_answer in self.quiz_state.wrong_answers:
                        # Try to find question index
                        question_text = wrong_answer.get('question', '').strip()
                        for i, q in enumerate(self.quiz_state.exam_data.get('questions', [])):
                            if q.get('question', '').strip() == question_text:
                                wrong_indices.add(i)
                                break
                self.timeline_widget.update_wrong_questions(wrong_indices)
    
    def update_navigation_state(self, can_go_prev: bool, can_go_next: bool):
        """Update navigation button states."""
        self.prev_button.setEnabled(can_go_prev)
    
    def set_action_button_text(self, text: str, enabled: bool = True, is_secondary: bool = False):
        """Set action button text and style."""
        self.action_button.setText(text)
        self.action_button.setEnabled(enabled)
        if is_secondary:
            self.action_button.setStyleSheet(self.styles.styles['button_secondary'])
        else:
            self.action_button.setStyleSheet(self.styles.styles['button'])
    
    def show_study_button(self, show: bool = True):
        """Show or hide the study button."""
        self.study_button.setVisible(show)
    
    def update_total_questions(self, total: int):
        """Update total number of questions."""
        self.total_questions = total
        self.progress_bar.setMaximum(total)
    
    def on_timeline_question_selected(self, index: int):
        """Handle timeline question selection."""
        self.question_jumped.emit(index)
    
    def set_practice_mode(self, enabled: bool):
        """Show/hide timeline and progress bar based on practice mode."""
        if enabled and not self.timeline_widget:
            # Create timeline if it doesn't exist
            self.timeline_widget = QuestionTimelineWidget(self.styles, self.total_questions)
            self.timeline_widget.question_selected.connect(self.on_timeline_question_selected)
            layout = self.layout()
            layout.insertWidget(0, self.timeline_widget)
            self.progress_bar.hide()
            self.practice_mode = True
        elif not enabled and self.timeline_widget:
            # Remove timeline
            self.timeline_widget.deleteLater()
            self.timeline_widget = None
            self.progress_bar.show()
            self.practice_mode = False
    
    def update_colors(self, colors: dict):
        """Update colors when theme changes."""
        self.colors = colors
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['card']};
                border-top: 1px solid {self.colors['border']};
            }}
        """)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                text-align: center;
                height: 12px;
                background-color: {self.colors['card']};
            }}
            QProgressBar::chunk {{
                background-color: {self.colors['primary']};
                border-radius: 8px;
            }}
        """)
        # Update timeline colors if it exists
        if self.timeline_widget:
            self.timeline_widget.update_colors(colors)

