import sys
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QRadioButton, QButtonGroup, 
                            QProgressBar, QScrollArea, QMessageBox, QStatusBar, QGridLayout,
                            QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QKeySequence, QAction

from src.components.dialogs.review_dialog import ReviewDialog
from src.components.dialogs.session_stats_dialog import SessionStatsDialog
from src.components.dialogs.session_select_dialog import SessionSelectDialog
from src.components.styles import (QUESTION, OPTION, BUTTON_PRIMARY, BUTTON_SECONDARY, 
                                 BUTTON_SUCCESS, BUTTON_WARNING, colors)
from src.models.quiz_state import QuizModeState
from src.utils.session_manager import SessionManager

class OptionCard(QFrame):
    def __init__(self, option_key, option_text, parent=None):
        super().__init__(parent)
        self.setObjectName("option_card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.is_enabled = True
        
        # Create horizontal layout for the card
        self.card_layout = QHBoxLayout(self)
        self.card_layout.setContentsMargins(16, 12, 16, 12)
        self.card_layout.setSpacing(12)
        
        # Create radio button
        self.radio = QRadioButton()
        self.radio.setFixedSize(20, 20)
        self.card_layout.addWidget(self.radio)
        
        # Create option label with key and text
        self.option_label = QLabel(f"{option_key}. {option_text}")
        self.option_label.setWordWrap(True)
        self.option_label.setStyleSheet(f"""
            font-size: 14px;
            color: {colors['text']};
        """)
        self.card_layout.addWidget(self.option_label, 1)  # 1 is the stretch factor
    
    def mousePressEvent(self, event):
        """Handle mouse press on the card."""
        if self.is_enabled:
            self.radio.setChecked(True)
        super().mousePressEvent(event)
    
    def setEnabled(self, enabled):
        """Enable or disable the option card."""
        self.is_enabled = enabled
        self.radio.setEnabled(enabled)
        if enabled:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

class MockExamApp(QMainWindow):
    def __init__(self, exam_data, study_data=None):
        super().__init__()
        self.exam_data = exam_data
        self.session_manager = SessionManager()
        
        # Set window title from exam data
        self.setWindowTitle(exam_data["title"])
        
        # Initialize state
        self.quiz_state = QuizModeState()
        
        # Load study data if provided
        if study_data:
            self.load_study_data(study_data)
        
        self.setup_ui()
        self.setup_shortcuts()
        self.display_question()
    
    def setup_ui(self):
        """Set up the main window UI."""
        self.setMinimumSize(800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sticky header
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(80)  # Reduced height since we removed mode selection
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        header_layout.setSpacing(8)
        
        # Title in header
        title_label = QLabel(self.exam_data["title"])
        title_label.setObjectName("header_title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Progress bar in header
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        header_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(header)
        
        # Question display area (scrollable)
        self.question_area = QScrollArea()
        self.question_area.setWidgetResizable(True)
        self.question_area.setFrameShape(QFrame.Shape.NoFrame)
        self.question_widget = QWidget()
        self.question_layout = QVBoxLayout(self.question_widget)
        self.question_layout.setContentsMargins(20, 20, 20, 20)
        self.question_area.setWidget(self.question_widget)
        main_layout.addWidget(self.question_area)
        
        # Options area
        self.options_widget = QWidget()
        self.options_layout = QVBoxLayout(self.options_widget)
        self.options_layout.setContentsMargins(20, 0, 20, 20)
        main_layout.addWidget(self.options_widget)
        
        # Answer display area (fixed position)
        self.answer_widget = QWidget()
        self.answer_layout = QVBoxLayout(self.answer_widget)
        self.answer_layout.setContentsMargins(20, 0, 20, 20)
        
        self.answer_label = QLabel()
        self.answer_label.setWordWrap(True)
        self.answer_label.setStyleSheet("""
            QLabel {
                background-color: #f8fafc;
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
                font-size: 16px;
                line-height: 1.5;
            }
        """)
        self.answer_label.hide()
        self.answer_layout.addWidget(self.answer_label)
        main_layout.addWidget(self.answer_widget)
        
        # Create sticky footer
        footer = QFrame()
        footer.setObjectName("footer")
        footer.setFixedHeight(80)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 10, 20, 10)
        footer_layout.setSpacing(16)
        
        # Navigation and action buttons in footer
        self.prev_button = QPushButton("← Previous")
        self.prev_button.setProperty("class", "nav_button")
        self.prev_button.setMinimumWidth(120)
        self.prev_button.clicked.connect(self.previous_question)
        footer_layout.addWidget(self.prev_button)
        
        # Add stretch to push action button to center
        footer_layout.addStretch()
        
        # Action button (Check Answer/Next)
        self.action_button = QPushButton("Check Answer")
        self.action_button.setProperty("class", "action_button")
        self.action_button.setMinimumWidth(200)
        self.action_button.clicked.connect(self.handle_action_button)
        footer_layout.addWidget(self.action_button)
        
        # Add stretch to balance the layout
        footer_layout.addStretch()
        
        main_layout.addWidget(footer)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
    
    def setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # Show answer shortcut (Space)
        show_answer_action = QAction(self)
        show_answer_action.setShortcut(QKeySequence(Qt.Key.Key_Space))
        show_answer_action.triggered.connect(self.show_answer)
        self.addAction(show_answer_action)
        
        # Next question shortcut (Right arrow)
        next_action = QAction(self)
        next_action.setShortcut(QKeySequence(Qt.Key.Key_Right))
        next_action.triggered.connect(self.next_question)
        self.addAction(next_action)
        
        # Previous question shortcut (Left arrow)
        prev_action = QAction(self)
        prev_action.setShortcut(QKeySequence(Qt.Key.Key_Left))
        prev_action.triggered.connect(self.previous_question)
        self.addAction(prev_action)
    
    def display_question(self):
        """Display the current question."""
        # Clear previous content
        while self.question_layout.count():
            item = self.question_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Hide answer label when displaying new question
        self.answer_label.hide()
        self.quiz_state.is_answer_shown = False
        self.action_button.setText("Check Answer")
        
        question = self.exam_data["questions"][self.quiz_state.current_index]
        
        # Display question
        question_label = QLabel(question["question"])
        question_label.setWordWrap(True)
        question_label.setStyleSheet(QUESTION)
        self.question_layout.addWidget(question_label)
        
        # Quiz mode - use vertical layout for option cards
        options_group = QButtonGroup(self)
        options_layout = QVBoxLayout()
        options_layout.setSpacing(12)
        
        # Store option cards for later disabling
        self.option_cards = []
        
        # Convert options dictionary to list of tuples for ordered display
        options_list = [(key, value) for key, value in question["options"].items()]
        
        for i, (option_key, option_text) in enumerate(options_list):
            # Create option card
            option_card = OptionCard(option_key, option_text)
            self.option_cards.append(option_card)
            
            # Add radio to button group
            options_group.addButton(option_card.radio, i)
            option_card.radio.clicked.connect(lambda checked, idx=i: self.on_option_selected(idx))
            
            # Add card to options layout
            options_layout.addWidget(option_card)
        
        self.options_layout.addLayout(options_layout)
        
        # Update progress
        total = len(self.exam_data["questions"])
        progress = (self.quiz_state.current_index + 1) / total * 100
        self.progress_bar.setValue(int(progress))
        
        # Update status
        self.update_status()
    
    def on_option_selected(self, index):
        """Handle option selection in quiz mode."""
        self.action_button.setEnabled(True)
        self.selected_option = index
    
    def handle_action_button(self):
        """Handle the action button (Check Answer/Next)."""
        if not self.quiz_state.is_answer_shown:
            self.check_answer()
            self.action_button.setText("Next →")
        else:
            self.next_question()
            self.action_button.setText("Check Answer")
    
    def show_answer(self):
        """Show the answer for the current question."""
        current_index = self.quiz_state.current_index
        question = self.exam_data["questions"][current_index]
        
        # Create and show review dialog
        dialog = ReviewDialog(question, self)
        dialog.exec()
    
    def check_answer(self):
        """Check the selected answer in quiz mode."""
        if not hasattr(self, 'selected_option'):
            return
        
        current_index = self.quiz_state.current_index
        question = self.exam_data["questions"][current_index]
        
        # Get the selected option key (A, B, C, D) from the index
        selected_option_key = list(question["options"].keys())[self.selected_option]
        
        # Check if answer is correct
        is_correct = selected_option_key == question["answer"]
        
        # Update score
        if is_correct:
            self.quiz_state.score += 1
            self.answer_label.setText(f"✓ Correct! Your answer {selected_option_key} was right.")
            self.answer_label.setStyleSheet("""
                QLabel {
                    background-color: #f0fdf4;
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid #86efac;
                    color: #166534;
                    font-size: 16px;
                    line-height: 1.5;
                }
            """)
        else:
            self.quiz_state.incorrect_answers.append({
                "question": question["question"],
                "your_answer": question["options"][selected_option_key],
                "correct_answer": question["options"][question["answer"]]
            })
            self.answer_label.setText(
                f"✗ Incorrect. You selected {selected_option_key}, but the correct answer is {question['answer']}.\n\n"
                f"Correct Answer: {question['options'][question['answer']]}"
            )
            self.answer_label.setStyleSheet("""
                QLabel {
                    background-color: #fef2f2;
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid #fecaca;
                    color: #991b1b;
                    font-size: 16px;
                    line-height: 1.5;
                }
            """)
        
        self.quiz_state.total_answered += 1
        self.answer_label.show()
        self.quiz_state.is_answer_shown = True
        
        # Disable all option cards to prevent further changes
        if hasattr(self, 'option_cards'):
            for card in self.option_cards:
                card.setEnabled(False)
        
        # Update status
        self.update_status()
    
    def next_question(self):
        """Move to the next question."""
        if self.quiz_state.current_index < len(self.exam_data["questions"]) - 1:
            self.quiz_state.current_index += 1
            self.quiz_state.is_answer_shown = False
            self.display_question()
            self.update_status()
            self.action_button.setText("Check Answer")
    
    def previous_question(self):
        """Move to the previous question."""
        if self.quiz_state.current_index > 0:
            self.quiz_state.current_index -= 1
            self.display_question()
            self.update_status()
            self.action_button.setText("Check Answer")
    
    def update_status(self):
        """Update the status bar with current progress."""
        total_questions = len(self.exam_data['questions'])
        current_question = self.quiz_state.current_index + 1
        
        # Calculate statistics
        accuracy = (self.quiz_state.score / self.quiz_state.total_answered * 100) if self.quiz_state.total_answered > 0 else 0
        completion_rate = (self.quiz_state.total_answered / total_questions * 100) if total_questions > 0 else 0
        incorrect_count = len(self.quiz_state.incorrect_answers)
        
        # Format status message with all statistics
        status = [
            f"Quiz: {current_question}/{total_questions}",
            f"Score: {self.quiz_state.score}/{self.quiz_state.total_answered}",
            f"Accuracy: {accuracy:.1f}%",
            f"Incorrect: {incorrect_count}",
            f"Completion: {completion_rate:.1f}%"
        ]
        
        # Use a bullet point (•) as a more subtle separator
        self.status_bar.showMessage(" • ".join(status))
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.save_study_data()
        event.accept()
    
    def save_study_data(self):
        """Save the current study session data."""
        session_data = {
            "session_date": datetime.now().isoformat(),
            "exam_title": self.exam_data["title"],
            "total_questions": len(self.exam_data["questions"]),
            "quiz_mode": {
                "score": self.quiz_state.score,
                "total_answered": self.quiz_state.total_answered,
                "wrong_answers": self.quiz_state.incorrect_answers
            }
        }
        
        self.session_manager.save_session(session_data)
    
    def load_study_data(self, study_data):
        """Load study data from a previous session."""
        # Load quiz mode data
        quiz_data = study_data.get("quiz_mode", {})
        self.quiz_state.score = quiz_data.get("score", 0)
        self.quiz_state.total_answered = quiz_data.get("total_answered", 0)
        self.quiz_state.incorrect_answers = quiz_data.get("wrong_answers", []) 