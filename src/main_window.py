import sys
import os
import json
import signal
import atexit
import copy
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QRadioButton, 
                            QCheckBox, QButtonGroup, QProgressBar, QScrollArea, 
                            QMessageBox, QStatusBar, QGraphicsDropShadowEffect, QDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QKeySequence, QAction, QColor

from src.components.review_dialog import ReviewDialog
from src.components.styles import Styles

class MockExamApp(QMainWindow):
    def __init__(self, exam_data, shuffle_enabled=False, session_data=None, exam_file_path=None):
        super().__init__()
        self.exam_data = exam_data
        self.shuffle_enabled = shuffle_enabled
        self.session_data = session_data
        self.exam_file_path = exam_file_path  # Track the exam file path
        self.session_filepath = None  # Track the session file path for overwriting
        self.original_session_date = None  # Track the original session date
        
        # Initialize from session data if resuming
        if session_data:
            # Extract filepath if available (from _filepath added by SessionManager)
            self.session_filepath = session_data.get('_filepath')
            # Preserve original session date
            self.original_session_date = session_data.get('session_date')
            quiz_mode = session_data.get('quiz_mode', {})
            self.score = quiz_mode.get('score', 0)
            self.wrong_answers = quiz_mode.get('wrong_answers', [])
            self.answered_questions = set(range(quiz_mode.get('total_answered', 0)))
            self.current_index = quiz_mode.get('total_answered', 0)
        else:
            self.score = 0
            self.wrong_answers = []
            self.answered_questions = set()
            self.current_index = 0
            
        self.answer_revealed = False
        self.is_paused = False
        self.review_mode = False  # Track if we're in review mode
        self.review_questions = []  # Store full question data for wrong answers
        # Keep original exam data - make a deep copy to avoid mutations
        self.original_exam_data = copy.deepcopy(exam_data)
        
        # Initialize timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.start_time = None
        self.elapsed_time = timedelta(0)
        
        # If resuming a session, restore elapsed time
        if session_data and 'timer_data' in session_data:
            timer_data = session_data['timer_data']
            self.elapsed_time = timedelta(seconds=timer_data.get('elapsed_seconds', 0))
        
        # Shuffle questions if enabled
        if self.shuffle_enabled:
            import random
            random.shuffle(self.exam_data['questions'])
        
        # Initialize styles
        self.styles = Styles()
        self.colors = self.styles.colors
        
        # Set up the main window
        if self.session_data:
            title_suffix = " - Resuming Session"
            if self.shuffle_enabled:
                title_suffix += " (Shuffled)"
        else:
            title_suffix = " - Study Mode (Shuffled)" if self.shuffle_enabled else " - Study Mode"
        self.setWindowTitle(f"{exam_data['title']}{title_suffix}")
        self.setMinimumSize(800, 600)
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.update_status()
        
        # Set application style
        self.setStyleSheet(self.styles.get_application_style())
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)  # Remove spacing between sections
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        # Create header widget (sticky)
        header_widget = QWidget()
        header_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['card']};
                border-bottom: none;
            }}
        """)
        # Add shadow effect to header
        header_shadow = QGraphicsDropShadowEffect()
        header_shadow.setBlurRadius(8)
        header_shadow.setColor(QColor(30, 41, 59, 8))  # rgba(30,41,59,0.03)
        header_shadow.setOffset(0, 2)
        header_widget.setGraphicsEffect(header_shadow)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(32, 28, 32, 20)
        
        # Header top row with title and dark mode toggle
        header_top = QHBoxLayout()
        
        # Dark mode toggle button (left side)
        self.dark_mode_button = QPushButton("🌙")
        self.dark_mode_button.setFixedSize(40, 40)
        self.dark_mode_button.setToolTip("Toggle Dark Mode (Ctrl+D)")
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)
        self.dark_mode_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['background']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['hover']};
            }}
        """)
        header_top.addWidget(self.dark_mode_button)
        
        # Pause button (left side, next to dark mode)
        self.pause_button = QPushButton("⏸")
        self.pause_button.setFixedSize(40, 40)
        self.pause_button.setToolTip("Pause/Resume (Ctrl+P)")
        self.pause_button.clicked.connect(self.toggle_pause)
        self.pause_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['background']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['hover']};
            }}
        """)
        header_top.addWidget(self.pause_button)
        
        # Title (centered)
        header_top.addStretch()
        title_label = QLabel(exam_data['title'])
        title_label.setFont(QFont('Helvetica', 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(self.styles.styles['label_title'])
        header_top.addWidget(title_label)
        header_top.addStretch()
        
        # Spacer to balance the buttons on the left
        spacer = QWidget()
        spacer.setFixedSize(80, 40)  # Increased to balance two buttons
        header_top.addWidget(spacer)
        
        header_layout.addLayout(header_top)
        
        # Add header to main layout
        main_layout.addWidget(header_widget)
        
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Create content widget
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(32, 32, 32, 32)
        self.content_layout.setSpacing(24)
        
        # Question label
        self.question_label = QLabel()
        self.question_label.setFont(QFont('Helvetica', 16))
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text']};
                background-color: {self.colors['card']};
                padding: 20px;
                border-radius: 10px;
                border: 1px solid {self.colors['border']};
            }}
        """)
        self.content_layout.addWidget(self.question_label)
        
        # Options container
        self.options_container = QWidget()
        options_layout = QVBoxLayout(self.options_container)
        options_layout.setSpacing(12)
        
        # Create option buttons container
        self.option_group = QButtonGroup()
        self.option_buttons = []
        self.options_layout = options_layout
        self.current_question_type = "singleChoice"  # Track current question type
        
        self.content_layout.addWidget(self.options_container)
        
        # Selection indicator
        self.selection_indicator = QLabel()
        self.selection_indicator.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text_light']};
                font-size: 14px;
            }}
        """)
        self.selection_indicator.hide()
        self.content_layout.addWidget(self.selection_indicator)
        
        # Answer label
        self.answer_label = QLabel()
        self.answer_label.setFont(QFont('Helvetica', 14))
        self.answer_label.setWordWrap(True)
        self.answer_label.hide()
        self.content_layout.addWidget(self.answer_label)
        
        # Add content to scroll area
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Create footer widget (sticky)
        footer_widget = QWidget()
        footer_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['card']};
                border-top: 1px solid {self.colors['border']};
            }}
        """)
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(32, 20, 32, 20)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(len(exam_data['questions']))
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
        footer_layout.addWidget(self.progress_bar)
        
        # Navigation container
        nav_container = QWidget()
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 10, 0, 0)  # Add top margin
        
        # Previous button
        self.prev_button = QPushButton("← Previous")
        self.prev_button.setStyleSheet(self.styles.styles['button_secondary'])
        self.prev_button.clicked.connect(self.previous_question)
        nav_layout.addWidget(self.prev_button)
        
        # Question counter
        self.nav_label = QLabel()
        self.nav_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self.nav_label)
        
        # Combined Confirm/Next button
        self.action_button = QPushButton("Confirm Answer")
        self.action_button.setFont(QFont('Helvetica', 12))
        self.action_button.setStyleSheet(self.styles.styles['button'])
        self.action_button.clicked.connect(self.handle_action_button)
        self.action_button.setEnabled(False)  # Initially disabled until an option is selected
        nav_layout.addWidget(self.action_button)
        
        footer_layout.addWidget(nav_container)
        
        # Study button (initially hidden, shown in review mode)
        self.study_button = QPushButton("📚 Study These Questions")
        self.study_button.setStyleSheet(self.styles.styles['button'])
        self.study_button.hide()
        self.study_button.clicked.connect(self.study_wrong_questions)
        nav_layout.insertWidget(1, self.study_button)
        
        # Add footer to main layout
        main_layout.addWidget(footer_widget)
        
        # Set up keyboard shortcuts
        self.setup_shortcuts()
        
        # Display first question
        self.display_question()
        
        # Start timer for new sessions or resume timer for existing sessions
        if not session_data:
            self.start_timer()
        elif session_data and 'timer_data' in session_data:
            # Resume timer for existing session
            self.start_timer()
        
        # Set up crash detection and auto-save
        self.setup_crash_protection()
    
    def create_option_buttons(self, num_options, question_type="singleChoice"):
        """Create the required number of option buttons"""
        # Clear existing buttons
        for button in self.option_buttons:
            button.deleteLater()
        self.option_buttons.clear()
        self.option_group = QButtonGroup()
        self.current_question_type = question_type
        
        # Create new buttons based on question type
        for i in range(num_options):
            if question_type == "multiChoice":
                option = QCheckBox()
                option.setFont(QFont('Helvetica', 14))
                option.setStyleSheet(f"""
                    QCheckBox {{
                        color: {self.colors['text']};
                        background-color: {self.colors['card']};
                        padding: 15px;
                        border-radius: 8px;
                        border: 1px solid {self.colors['border']};
                    }}
                    QCheckBox:hover {{
                        background-color: {self.colors['hover']};
                    }}
                    QCheckBox::indicator {{
                        width: 20px;
                        height: 20px;
                    }}
                """)
            else:
                option = QRadioButton()
                option.setFont(QFont('Helvetica', 14))
                option.setStyleSheet(f"""
                    QRadioButton {{
                        color: {self.colors['text']};
                        background-color: {self.colors['card']};
                        padding: 15px;
                        border-radius: 8px;
                        border: 1px solid {self.colors['border']};
                    }}
                    QRadioButton:hover {{
                        background-color: {self.colors['hover']};
                    }}
                    QRadioButton::indicator {{
                        width: 20px;
                        height: 20px;
                    }}
                """)
            
            self.options_layout.addWidget(option)
            self.option_buttons.append(option)
            self.option_group.addButton(option, i)
        
        # Set up keyboard shortcuts for options
        self.setup_option_shortcuts(num_options)
    
    def setup_shortcuts(self):
        # Show answer shortcut (Space)
        show_answer_shortcut = QAction(self)
        show_answer_shortcut.setShortcut(QKeySequence(Qt.Key.Key_Space))
        show_answer_shortcut.triggered.connect(self.show_answer)
        self.addAction(show_answer_shortcut)
        
        # Next question shortcut (Right arrow)
        next_shortcut = QAction(self)
        next_shortcut.setShortcut(QKeySequence(Qt.Key.Key_Right))
        next_shortcut.triggered.connect(self.next_question)
        self.addAction(next_shortcut)
        
        # Previous question shortcut (Left arrow)
        prev_shortcut = QAction(self)
        prev_shortcut.setShortcut(QKeySequence(Qt.Key.Key_Left))
        prev_shortcut.triggered.connect(self.previous_question)
        self.addAction(prev_shortcut)
        
        # Option shortcuts will be set up dynamically in display_question
        
        # Dark mode toggle shortcut (Ctrl+D)
        dark_mode_shortcut = QAction(self)
        dark_mode_shortcut.setShortcut(QKeySequence("Ctrl+D"))
        dark_mode_shortcut.triggered.connect(self.toggle_dark_mode)
        self.addAction(dark_mode_shortcut)
        
        # Pause toggle shortcut (Ctrl+P)
        pause_shortcut = QAction(self)
        pause_shortcut.setShortcut(QKeySequence("Ctrl+P"))
        pause_shortcut.triggered.connect(self.toggle_pause)
        self.addAction(pause_shortcut)
    
    def setup_option_shortcuts(self, num_options):
        """Set up keyboard shortcuts for option selection"""
        # Remove existing option shortcuts
        for action in self.actions():
            if hasattr(action, '_is_option_shortcut'):
                self.removeAction(action)
        
        # Add new shortcuts
        for i in range(num_options):
            shortcut = QAction(self)
            shortcut.setShortcut(QKeySequence(str(i + 1)))
            shortcut.triggered.connect(lambda checked, idx=i: self.select_option(idx))
            shortcut._is_option_shortcut = True  # Mark for removal
            self.addAction(shortcut)
    
    def select_option(self, index):
        if 0 <= index < len(self.option_buttons):
            self.option_buttons[index].setChecked(True)
    
    def display_question(self):
        # If in review mode, show review-specific display
        if self.review_mode:
            self.display_review_question()
            return
        
        question = self.exam_data['questions'][self.current_index]
        
        # Update counter (single source of truth)
        counter_text = f"Question {self.current_index + 1} of {len(self.exam_data['questions'])}"
        self.nav_label.setText(counter_text)  # Only update nav label
        
        # Update navigation
        self.prev_button.setEnabled(self.current_index > 0)
        
        # Update question
        self.question_label.setText(question['question'])
        
        # Create the right number of option buttons
        num_options = len(question['options'])
        question_type = question.get('type', 'singleChoice')
        self.create_option_buttons(num_options, question_type)
        
        # Normal mode display
        if question_type == "singleChoice":
            self.option_group.setExclusive(True)
        else:
            self.option_group.setExclusive(False)
            
        for i, (key, value) in enumerate(question['options'].items()):
            self.option_buttons[i].setText(f"{key}. {value}")
            self.option_buttons[i].setChecked(False)
            self.option_buttons[i].setEnabled(True)  # Re-enable buttons for new question
        
        # Reset answer display and selection indicator
        self.answer_label.hide()
        self.selection_indicator.hide()
        self.answer_revealed = False
        self.action_button.setText("Confirm Answer")
        self.action_button.setStyleSheet(self.styles.styles['button'])
        self.action_button.setEnabled(False)
        
        # Connect option selection handler
        self.option_group.buttonClicked.connect(self.on_option_selected)
        
        # Update progress
        self.progress_bar.setValue(self.current_index + 1)
        
        # Update status
        self.update_status()
        
        # Respect pause state - hide question and answers if paused
        if self.is_paused:
            self.question_label.hide()
            self.options_container.hide()

    def on_option_selected(self, button):
        # Enable action button when an option is selected
        self.action_button.setEnabled(True)
        
        # Get selected options
        if self.current_question_type == "multiChoice":
            selected_options = []
            for i, option_button in enumerate(self.option_buttons):
                if option_button.isChecked():
                    selected_options.append(chr(ord('A') + i))
            
            if selected_options:
                selected_text = ", ".join(selected_options)
                self.selection_indicator.setText(f"Selected: Options {selected_text}")
                self.action_button.setText(f"Confirm {selected_text}")
            else:
                self.selection_indicator.setText("No options selected")
                self.action_button.setText("Confirm Answer")
        else:
            # Single choice
            selected_option = chr(ord('A') + self.option_group.id(button))
            self.selection_indicator.setText(f"Selected: Option {selected_option}")
            self.action_button.setText(f"Confirm {selected_option}")
        
        self.selection_indicator.show()
        self.action_button.setStyleSheet(self.styles.styles['button'])

    def handle_action_button(self):
        if self.review_mode:
            # In review mode, action button just goes to next
            self.next_question()
        elif not self.answer_revealed:
            self.show_answer()
        else:
            self.next_question()

    def show_answer(self):
        if not self.answer_revealed:
            question = self.exam_data['questions'][self.current_index]
            correct = question['answer']
            question_type = question.get('type', 'singleChoice')
            
            # Get selected options
            if question_type == "multiChoice":
                selected_options = []
                for i, option_button in enumerate(self.option_buttons):
                    if option_button.isChecked():
                        selected_options.append(chr(ord('A') + i))
                selected_option = selected_options
            else:
                # Single choice
                selected_button = self.option_group.checkedButton()
                selected_option = chr(ord('A') + self.option_group.id(selected_button)) if selected_button else None
            
            # Check if answer is correct
            if question_type == "multiChoice":
                # For multi-choice, compare sets
                correct_set = set(correct) if isinstance(correct, list) else {correct}
                selected_set = set(selected_option) if selected_option else set()
                is_correct = correct_set == selected_set
            else:
                # Single choice
                is_correct = selected_option == correct
            
            # Update answer display with selection feedback
            if is_correct:
                if question_type == "multiChoice":
                    selected_text = ", ".join(selected_option) if selected_option else "None"
                    self.answer_label.setText(f"✓ Correct! Your answers {selected_text} were right.")
                else:
                    self.answer_label.setText(f"✓ Correct! Your answer {selected_option} was right.")
                
                self.answer_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {self.colors['card']};
                        padding: 20px;
                        border-radius: 10px;
                        border: 1px solid {self.colors['correct']};
                        color: {self.colors['correct']};
                    }}
                """)
            else:
                # Incorrect answer
                if question_type == "multiChoice":
                    selected_text = ", ".join(selected_option) if selected_option else "None"
                    correct_text = ", ".join(correct) if isinstance(correct, list) else correct
                    correct_options_text = "\n".join([f"{opt}. {question['options'][opt]}" for opt in correct])
                    
                    self.answer_label.setText(
                        f"✗ Incorrect. You selected {selected_text}, but the correct answers are {correct_text}.\n\n"
                        f"Correct Answers:\n{correct_options_text}"
                    )
                else:
                    correct_text = question['options'][correct]
                    self.answer_label.setText(
                        f"✗ Incorrect. You selected {selected_option}, but the correct answer is {correct}.\n\n"
                        f"Correct Answer: {correct}. {correct_text}"
                    )
                
                self.answer_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {self.colors['card']};
                        padding: 20px;
                        border-radius: 10px;
                        border: 1px solid {self.colors['warning']};
                        color: {self.colors['warning']};
                    }}
                """)
            
            self.answer_label.show()
            self.answer_revealed = True
            self.action_button.setText("Next →")
            self.action_button.setStyleSheet(self.styles.styles['button_secondary'])
            self.selection_indicator.hide()
            
            # Disable all option buttons to prevent further changes
            for button in self.option_buttons:
                button.setEnabled(False)
            
            # Record answer
            if selected_option:
                if is_correct:
                    self.score += 1
                else:
                    # Store human-readable answers (option text) in wrong_answers
                    if question_type == "multiChoice":
                        your_texts = [question['options'][opt] for opt in (selected_option or [])]
                        correct_list = correct if isinstance(correct, list) else [correct]
                        correct_texts = [question['options'][opt] for opt in correct_list]
                        your_answer_value = "; ".join(your_texts) if your_texts else ""
                        correct_answer_value = "; ".join(correct_texts)
                    else:
                        your_answer_value = question['options'].get(selected_option, "") if selected_option else ""
                        correct_answer_value = question['options'].get(correct, "")

                    # Store wrong answer with question ID for easy filtering
                    wrong_answer = {
                        'question_id': question.get('id'),
                        'question': question['question'],
                        'your_answer': your_answer_value,
                        'correct_answer': correct_answer_value
                    }
                    self.wrong_answers.append(wrong_answer)
                self.answered_questions.add(self.current_index)
                self.update_status()

    def next_question(self):
        if self.review_mode:
            # In review mode, just move to next question
            self.current_index += 1
            if self.current_index >= len(self.review_questions):
                # Reached end of review, go back to start or close
                reply = QMessageBox.question(
                    self, "Review Complete", 
                    "You've reviewed all incorrect answers.\n\nWould you like to study these questions?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.study_wrong_questions()
                else:
                    self.close()
                return
            self.display_question()
            return
        
        if not self.answer_revealed:
            QMessageBox.warning(self, "Warning", "Please show the answer before proceeding.")
            return
        
        # Check if any option is selected
        has_selection = False
        if self.current_question_type == "multiChoice":
            has_selection = any(button.isChecked() for button in self.option_buttons)
        else:
            has_selection = self.option_group.checkedButton() is not None
            
        if not has_selection:
            QMessageBox.warning(self, "Warning", "Please select an answer before proceeding.")
            return
        
        # Move to next question or show results
        self.current_index += 1
        if self.current_index >= len(self.exam_data['questions']):
            self.show_results()
        else:
            self.display_question()
    
    def enter_review_mode(self):
        """Enter review mode for incorrect answers."""
        if not self.wrong_answers:
            return
        
        # Map wrong answers back to full question data using IDs (much simpler!)
        self.review_questions = []
        for wrong_answer in self.wrong_answers:
            question_id = wrong_answer.get('question_id')
            if question_id is not None:
                # Find question by ID in original exam
                for q in self.original_exam_data['questions']:
                    if q.get('id') == question_id:
                        review_q = q.copy()
                        review_q['wrong_answer_info'] = wrong_answer
                        self.review_questions.append(review_q)
                        break
            else:
                # Fallback: find by question text if ID not available (for old results)
                question_text = wrong_answer['question'].strip()
                for q in self.original_exam_data['questions']:
                    if q['question'].strip() == question_text:
                        review_q = q.copy()
                        review_q['wrong_answer_info'] = wrong_answer
                        self.review_questions.append(review_q)
                        break
        
        if not self.review_questions:
            QMessageBox.warning(self, "Error", "Could not map wrong answers to questions.")
            return
        
        # Switch to review mode
        self.review_mode = True
        self.current_index = 0
        self.exam_data = {'title': f"{self.original_exam_data['title']} - Review Mode", 'questions': self.review_questions}
        
        # Update UI for review mode
        self.setWindowTitle(f"{self.original_exam_data['title']} - Review Mode")
        self.study_button.show()
        self.action_button.setText("Next →")
        self.action_button.setStyleSheet(self.styles.styles['button_secondary'])
        self.action_button.setEnabled(True)
        
        # Update progress bar
        self.progress_bar.setMaximum(len(self.review_questions))
        
        # Display first review question
        self.display_question()
    
    def display_review_question(self):
        """Display a question in review mode with wrong/correct answer info."""
        if self.current_index >= len(self.review_questions):
            return
        
        review_q = self.review_questions[self.current_index]
        wrong_info = review_q.get('wrong_answer_info', {})
        
        # Update counter
        counter_text = f"Review {self.current_index + 1} of {len(self.review_questions)}"
        self.nav_label.setText(counter_text)
        
        # Update navigation
        self.prev_button.setEnabled(self.current_index > 0)
        
        # Display question
        self.question_label.setText(review_q['question'])
        
        # Create option buttons (for display only)
        num_options = len(review_q['options'])
        question_type = review_q.get('type', 'singleChoice')
        self.create_option_buttons(num_options, question_type)
        
        if question_type == "singleChoice":
            self.option_group.setExclusive(False)  # Allow multiple selections for highlighting
        else:
            self.option_group.setExclusive(False)
        
        # Display options and highlight correct/incorrect
        for i, (key, value) in enumerate(review_q['options'].items()):
            self.option_buttons[i].setText(f"{key}. {value}")
            self.option_buttons[i].setChecked(False)
            self.option_buttons[i].setEnabled(False)  # Disabled in review mode
            
            # Highlight correct answer
            correct_answer = review_q['answer']
            if question_type == "multiChoice":
                is_correct = key in (correct_answer if isinstance(correct_answer, list) else [correct_answer])
            else:
                is_correct = key == correct_answer
            
            if is_correct:
                self.option_buttons[i].setStyleSheet(f"""
                    QRadioButton, QCheckBox {{
                        color: {self.colors['correct']};
                        background-color: {self.colors['card']};
                        padding: 15px;
                        border-radius: 8px;
                        border: 2px solid {self.colors['correct']};
                        font-weight: bold;
                    }}
                """)
            else:
                # Check if this was the user's wrong answer
                your_answer_text = wrong_info.get('your_answer', '').lower()
                option_key = key.lower()
                option_value = value.lower()
                # Check if this option key or text was in the user's answer
                is_wrong_answer = (option_key in your_answer_text or 
                                 option_value in your_answer_text or
                                 f"{key}." in your_answer_text)
                
                if is_wrong_answer:
                    self.option_buttons[i].setStyleSheet(f"""
                        QRadioButton, QCheckBox {{
                            color: {self.colors['warning']};
                            background-color: {self.colors['card']};
                            padding: 15px;
                            border-radius: 8px;
                            border: 2px solid {self.colors['warning']};
                        }}
                    """)
                else:
                    self.option_buttons[i].setStyleSheet(f"""
                        QRadioButton, QCheckBox {{
                            color: {self.colors['text']};
                            background-color: {self.colors['card']};
                            padding: 15px;
                            border-radius: 8px;
                            border: 1px solid {self.colors['border']};
                        }}
                    """)
        
        # Show answer explanation
        your_answer = wrong_info.get('your_answer', 'N/A')
        correct_answer = wrong_info.get('correct_answer', 'N/A')
        
        answer_text = f"<b>Your Answer:</b> {your_answer}<br><br>"
        answer_text += f"<b>Correct Answer:</b> {correct_answer}"
        
        self.answer_label.setText(answer_text)
        self.answer_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.colors['card']};
                padding: 20px;
                border-radius: 10px;
                border: 1px solid {self.colors['warning']};
                color: {self.colors['text']};
            }}
        """)
        self.answer_label.show()
        
        # Hide selection indicator in review mode
        self.selection_indicator.hide()
        self.answer_revealed = True
        
        # Update progress
        self.progress_bar.setValue(self.current_index + 1)
        self.update_status()
        
        # Respect pause state
        if self.is_paused:
            self.question_label.hide()
            self.options_container.hide()
    
    def study_wrong_questions(self):
        """Filter exam to only include wrong answer questions for study."""
        if not self.review_questions:
            QMessageBox.warning(self, "Error", "No questions to study.")
            return
        
        # Create filtered exam data using question IDs (much simpler!)
        incorrect_ids = {q.get('wrong_answer_info', {}).get('question_id') for q in self.review_questions}
        incorrect_ids = {id for id in incorrect_ids if id is not None}
        
        # Filter questions by ID
        filtered_questions = []
        for q in self.original_exam_data['questions']:
            if q.get('id') in incorrect_ids:
                filtered_questions.append(q.copy())
        
        # If no IDs available, fallback to question text matching
        if not filtered_questions:
            for review_q in self.review_questions:
                question_text = review_q.get('question', '').strip()
                for orig_q in self.original_exam_data['questions']:
                    if orig_q.get('question', '').strip() == question_text:
                        filtered_questions.append(orig_q.copy())
                        break
        
        filtered_exam = {
            'title': f"{self.original_exam_data['title']} - Study Wrong Answers",
            'questions': filtered_questions
        }
        
        # Reset state for new quiz
        self.review_mode = False
        self.exam_data = filtered_exam
        self.original_exam_data = filtered_exam
        self.current_index = 0
        self.score = 0
        self.answered_questions = set()
        self.wrong_answers = []
        self.answer_revealed = False
        
        # Update UI
        self.setWindowTitle(filtered_exam['title'])
        self.study_button.hide()
        self.action_button.setText("Confirm Answer")
        self.action_button.setStyleSheet(self.styles.styles['button'])
        self.action_button.setEnabled(False)
        self.progress_bar.setMaximum(len(filtered_exam['questions']))
        
        # Display first question
        self.display_question()
        self.update_status()
    
    def show_results(self):
        # Stop timer and save session data (mark as completed)
        self.stop_timer()
        self.save_session_data(auto_save=False, emergency=False, completed=True)
        
        # Save detailed results to file
        self.save_results_to_file()
        
        # Create results window with more options
        results = QMessageBox(self)
        results.setWindowTitle("Exam Results")
        results.setIcon(QMessageBox.Icon.Information)
        
        # Format results message with timer info
        total_time = self.get_total_elapsed_time()
        time_str = self.format_time(total_time)
        percentage = (self.score / len(self.answered_questions) * 100) if len(self.answered_questions) > 0 else 0
        message = f"Your Score: {self.score}/{len(self.answered_questions)}\n"
        message += f"Time Taken: {time_str}\n\n"
        if self.wrong_answers:
            message += f"You had {len(self.wrong_answers)} incorrect answers.\n"
            message += "Would you like to review them?\n\n"
        message += f"Grade: {percentage:.1f}%"
        
        results.setText(message)
        
        # Add buttons
        review_button = None
        if self.wrong_answers:
            review_button = results.addButton("Review Incorrect Answers", QMessageBox.ButtonRole.ActionRole)
        results.addButton("Close", QMessageBox.ButtonRole.RejectRole)
        
        results.exec()
        
        if results.clickedButton() == review_button and self.wrong_answers:
            self.enter_review_mode()
        else:
            self.close()

    def update_status(self):
        status_parts = []
        
        if self.review_mode:
            status_parts.append(f"Review Mode: {self.current_index + 1}/{len(self.review_questions)}")
        else:
            # Add score
            if self.answered_questions:
                status_parts.append(f"Score: {self.score}/{len(self.answered_questions)}")
            else:
                status_parts.append("Not started")
            
            # Add timer
            total_time = self.get_total_elapsed_time()
            time_str = self.format_time(total_time)
            status_parts.append(f"Time: {time_str}")
        
        self.statusBar.showMessage(" | ".join(status_parts))

    def previous_question(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_question()
    
    def start_timer(self):
        """Start the exam timer"""
        if not self.start_time:
            self.start_time = datetime.now()
            self.timer.start(1000)  # Update every second
    
    def stop_timer(self):
        """Stop the exam timer"""
        if self.start_time:
            self.timer.stop()
            # Add the current session time to elapsed time
            current_session_time = datetime.now() - self.start_time
            self.elapsed_time += current_session_time
            self.start_time = None
    
    def update_timer(self):
        """Update the timer display"""
        if self.start_time:
            current_session_time = datetime.now() - self.start_time
            total_time = self.elapsed_time + current_session_time
            self.update_status()
    
    def get_total_elapsed_time(self):
        """Get total elapsed time including current session"""
        if self.start_time:
            current_session_time = datetime.now() - self.start_time
            return self.elapsed_time + current_session_time
        return self.elapsed_time
    
    def format_time(self, time_delta):
        """Format time delta as HH:MM:SS"""
        total_seconds = int(time_delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def toggle_pause(self):
        """Toggle pause state - hide/show question and answers, pause/resume timer"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            # Pause: hide question and answers, stop timer
            self.question_label.hide()
            self.options_container.hide()
            self.answer_label.hide()
            self.selection_indicator.hide()
            self.pause_button.setText("▶")
            self.pause_button.setToolTip("Resume (Ctrl+P)")
            self.stop_timer()
        else:
            # Resume: show question and answers, start timer
            self.question_label.show()
            self.options_container.show()
            # Only show answer label if it was previously revealed
            if self.answer_revealed:
                self.answer_label.show()
            # Only show selection indicator if an option was selected
            if any(button.isChecked() for button in self.option_buttons):
                self.selection_indicator.show()
            self.pause_button.setText("⏸")
            self.pause_button.setToolTip("Pause (Ctrl+P)")
            self.start_timer()
    
    def toggle_dark_mode(self):
        """Toggle dark mode and refresh all styles"""
        self.styles.toggle_dark_mode()
        self.colors = self.styles.colors
        
        # Refresh application style
        self.setStyleSheet(self.styles.get_application_style())
        
        # Update header
        header_widget = self.centralWidget().layout().itemAt(0).widget()
        header_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['card']};
                border-bottom: none;
            }}
        """)
        
        # Update dark mode button
        self.dark_mode_button.setText("☀️" if self.styles.dark_mode else "🌙")
        self.dark_mode_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['background']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['hover']};
            }}
        """)
        
        # Update pause button
        self.pause_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['background']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['hover']};
            }}
        """)
        
        # Update question label
        self.question_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text']};
                background-color: {self.colors['card']};
                padding: 20px;
                border-radius: 10px;
                border: 1px solid {self.colors['border']};
            }}
        """)
        
        # Update selection indicator
        self.selection_indicator.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text_light']};
                font-size: 14px;
            }}
        """)
        
        # Update footer
        footer_widget = self.centralWidget().layout().itemAt(2).widget()
        footer_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['card']};
                border-top: 1px solid {self.colors['border']};
            }}
        """)
        
        # Update progress bar
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
        
        # Update buttons
        self.prev_button.setStyleSheet(self.styles.styles['button_secondary'])
        self.action_button.setStyleSheet(
            self.styles.styles['button'] if self.action_button.text() == "Confirm Answer" 
            else self.styles.styles['button_secondary']
        )
        
        # Update option buttons
        for button in self.option_buttons:
            if isinstance(button, QRadioButton):
                button.setStyleSheet(self.styles.styles['radio_button'])
            else:
                button.setStyleSheet(f"""
                    QCheckBox {{
                        color: {self.colors['text']};
                        background-color: {self.colors['card']};
                        padding: 15px;
                        border-radius: 8px;
                        border: 1px solid {self.colors['border']};
                    }}
                    QCheckBox:hover {{
                        background-color: {self.colors['hover']};
                    }}
                    QCheckBox::indicator {{
                        width: 20px;
                        height: 20px;
                    }}
                """)
        
        # Refresh current answer label if visible
        if self.answer_label.isVisible():
            # Re-show answer to update styling
            current_question = self.exam_data['questions'][self.current_index]
            correct = current_question['answer']
            question_type = current_question.get('type', 'singleChoice')
            
            # Get selected options to determine if correct
            if question_type == "multiChoice":
                selected_options = []
                for i, option_button in enumerate(self.option_buttons):
                    if option_button.isChecked():
                        selected_options.append(chr(ord('A') + i))
                correct_set = set(correct) if isinstance(correct, list) else {correct}
                selected_set = set(selected_options) if selected_options else set()
                is_correct = correct_set == selected_set
            else:
                selected_button = self.option_group.checkedButton()
                selected_option = chr(ord('A') + self.option_group.id(selected_button)) if selected_button else None
                is_correct = selected_option == correct
            
            # Update answer label style
            if is_correct:
                self.answer_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {self.colors['card']};
                        padding: 20px;
                        border-radius: 10px;
                        border: 1px solid {self.colors['correct']};
                        color: {self.colors['correct']};
                    }}
                """)
            else:
                self.answer_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {self.colors['card']};
                        padding: 20px;
                        border-radius: 10px;
                        border: 1px solid {self.colors['warning']};
                        color: {self.colors['warning']};
                    }}
                """)
    
    
    def setup_crash_protection(self):
        """Set up crash detection and auto-save mechanisms"""
        # Set up periodic auto-save
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_session)
        self.auto_save_timer.start(30000)  # Auto-save every 30 seconds
        
        # Set up signal handlers for crash detection
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Register cleanup function for normal exit
        atexit.register(self.cleanup_on_exit)
        
        # Override closeEvent to save on window close
        self.closeEvent = self.custom_close_event
    
    def signal_handler(self, signum, frame):
        """Handle system signals (SIGINT, SIGTERM)"""
        print(f"Received signal {signum}, saving session...")
        self.emergency_save()
        sys.exit(0)
    
    def cleanup_on_exit(self):
        """Cleanup function called on normal exit"""
        try:
            self.emergency_save()
        except:
            pass  # Ignore errors during cleanup
    
    def custom_close_event(self, event):
        """Custom close event handler"""
        self.emergency_save()
        event.accept()
    
    def auto_save_session(self):
        """Auto-save session data periodically"""
        try:
            self.save_session_data(auto_save=True)
        except Exception as e:
            print(f"Auto-save error: {e}")
    
    def emergency_save(self):
        """Emergency save when app is closing or crashing"""
        try:
            # Stop timer first
            self.stop_timer()
            
            # Save session data
            self.save_session_data(auto_save=True, emergency=True)
            print("Emergency save completed")
        except Exception as e:
            print(f"Emergency save failed: {e}")
    
    def save_session_data(self, auto_save=False, emergency=False, completed=False):
        """Save current session data including timer"""
        try:
            from src.utils.session_manager import SessionManager
            
            # Prepare session data
            # Preserve original session date if available, otherwise use current time (first save)
            if self.original_session_date:
                session_date = self.original_session_date
            else:
                session_date = datetime.now().isoformat()
                # Store it for future saves
                self.original_session_date = session_date
            
            session_data = {
                'session_date': session_date,
                'exam_title': self.exam_data['title'],
                'total_questions': len(self.exam_data['questions']),
                'quiz_mode': {
                    'score': self.score,
                    'total_answered': len(self.answered_questions),
                    'wrong_answers': self.wrong_answers
                },
                'timer_data': {
                    'elapsed_seconds': int(self.get_total_elapsed_time().total_seconds()),
                    'completed': completed,  # True when quiz is finished
                    'auto_saved': auto_save,
                    'emergency_saved': emergency
                }
            }
            
            # Save session (overwrite existing file if resuming, otherwise create new)
            session_manager = SessionManager()
            saved_filepath = session_manager.save_session(session_data, self.session_filepath)
            
            # Store filepath for future saves (overwrites)
            self.session_filepath = saved_filepath
            
            if auto_save:
                print("Auto-save completed")
            
        except Exception as e:
            print(f"Error saving session: {e}")
    
    def save_results_to_file(self):
        """Save detailed quiz results to a file."""
        try:
            # Create results directory if it doesn't exist (project root is 1 level up from src/)
            results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
            os.makedirs(results_dir, exist_ok=True)
            
            # Generate filename with timestamp (including microseconds for uniqueness)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"quiz_results_{timestamp}.json"
            filepath = os.path.join(results_dir, filename)
            
            # Calculate statistics
            total_time = self.get_total_elapsed_time()
            total_questions = len(self.exam_data['questions'])
            answered_questions = len(self.answered_questions)
            accuracy = (self.score / answered_questions * 100) if answered_questions > 0 else 0
            completion_rate = (answered_questions / total_questions * 100) if total_questions > 0 else 0
            
            # Get incorrect question IDs
            incorrect_question_ids = [wa.get('question_id') for wa in self.wrong_answers if wa.get('question_id') is not None]
            
            # Get exam file path (relative to project root if absolute)
            exam_file_path = self.exam_file_path
            if exam_file_path and os.path.isabs(exam_file_path):
                # Convert to relative path if possible
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                try:
                    exam_file_path = os.path.relpath(exam_file_path, project_root)
                except:
                    pass  # Keep absolute path if relpath fails
            
            # Prepare comprehensive results data
            results_data = {
                "exam_info": {
                    "title": self.exam_data['title'],
                    "total_questions": total_questions,
                    "shuffle_enabled": self.shuffle_enabled,
                    "exam_file_path": exam_file_path  # Store the exam file path
                },
                "session_info": {
                    "completion_date": datetime.now().isoformat(),
                    "time_taken": self.format_time(total_time),
                    "time_taken_seconds": int(total_time.total_seconds())
                },
                "performance": {
                    "score": self.score,
                    "total_answered": answered_questions,
                    "accuracy_percentage": round(accuracy, 2),
                    "completion_percentage": round(completion_rate, 2),
                    "incorrect_count": len(self.wrong_answers)
                },
                "detailed_results": {
                    "correct_answers": self.score,
                    "incorrect_answers": self.wrong_answers,
                    "questions_answered": list(self.answered_questions),
                    "incorrect_question_ids": incorrect_question_ids  # Store IDs for easy filtering
                }
            }
            
            # Save to JSON file
            with open(filepath, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            print(f"Quiz results saved to: {filepath}")
            
            # Also create a human-readable text summary (using same timestamp)
            text_filename = f"quiz_summary_{timestamp}.txt"
            text_filepath = os.path.join(results_dir, text_filename)
            
            with open(text_filepath, 'w') as f:
                f.write("QUIZ RESULTS SUMMARY\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Exam: {self.exam_data['title']}\n")
                f.write(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Time Taken: {self.format_time(total_time)}\n")
                f.write(f"Questions Answered: {answered_questions}/{total_questions}\n")
                f.write(f"Score: {self.score}/{answered_questions}\n")
                f.write(f"Accuracy: {accuracy:.1f}%\n")
                f.write(f"Completion Rate: {completion_rate:.1f}%\n\n")
                
                if self.wrong_answers:
                    f.write("INCORRECT ANSWERS:\n")
                    f.write("-" * 30 + "\n")
                    for i, wrong in enumerate(self.wrong_answers, 1):
                        f.write(f"{i}. Question: {wrong['question']}\n")
                        f.write(f"   Your Answer: {wrong['your_answer']}\n")
                        f.write(f"   Correct Answer: {wrong['correct_answer']}\n\n")
                else:
                    f.write("No incorrect answers!\n")
                
                f.write("\n" + "=" * 50 + "\n")
                f.write(f"FINAL GRADE: {accuracy:.1f}%\n")
                f.write("=" * 50 + "\n")
            
            print(f"Quiz summary saved to: {text_filepath}")
            
        except Exception as e:
            print(f"Error saving results to file: {e}")

def main():
    app = QApplication(sys.argv)
    
    # Show test selection dialog
    from src.components.dialogs.test_select_dialog import TestSelectDialog
    test_dialog = TestSelectDialog()
    
    if test_dialog.exec() == QDialog.DialogCode.Accepted:
        selected_exam = test_dialog.get_selected_exam()
        selected_session = test_dialog.get_selected_session()
        selected_result = test_dialog.get_selected_result()
        shuffle_enabled = test_dialog.is_shuffle_enabled()
        
        if selected_result:
            # Load exam and enter review mode using saved file path and IDs
            incorrect_answers = selected_result.get('detailed_results', {}).get('incorrect_answers', [])
            if not incorrect_answers:
                QMessageBox.information(None, "No Incorrect Answers", "This test session has no incorrect answers to review.")
                sys.exit(0)
            
            # Get exam file path from result
            exam_file_path = selected_result.get('exam_info', {}).get('exam_file_path')
            if not exam_file_path:
                QMessageBox.warning(None, "Error", "Exam file path not found in result data.")
                sys.exit(1)
            
            # Convert relative path to absolute if needed
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            if not os.path.isabs(exam_file_path):
                exam_file_path = os.path.join(project_root, exam_file_path)
            
            # Load exam data
            from src.utils.data_loader import load_exam_data
            try:
                exam_data = load_exam_data(exam_file_path)
            except Exception as e:
                QMessageBox.warning(None, "Error", f"Could not load exam file: {exam_file_path}\n\n{str(e)}")
                sys.exit(1)
            
            # Create window and enter review mode
            window = MockExamApp(exam_data, shuffle_enabled=False, exam_file_path=exam_file_path)
            window.wrong_answers = incorrect_answers
            window.show()
            # Enter review mode after showing window
            QTimer.singleShot(100, window.enter_review_mode)
            sys.exit(app.exec())
        elif selected_exam:
            # Load the selected exam data
            from src.utils.data_loader import load_exam_data
            exam_file_path = selected_exam['filepath']
            exam_data = load_exam_data(exam_file_path)
            
            # Start the exam with file path
            window = MockExamApp(exam_data, shuffle_enabled, exam_file_path=exam_file_path)
            window.show()
            sys.exit(app.exec())
        elif selected_session:
            # Resume a previous session
            from src.utils.data_loader import load_exam_data
            # Find the exam file for this session
            exam_title = selected_session['exam_title']
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            
            # Try to find matching exam file in exams folder
            exam_file = None
            exams_dir = os.path.join(project_root, 'exams')
            if os.path.exists(exams_dir):
                for filename in os.listdir(exams_dir):
                    if filename.endswith('.json'):
                        try:
                            with open(os.path.join(exams_dir, filename), 'r') as f:
                                data = json.load(f)
                                if data.get('title') == exam_title:
                                    exam_file = os.path.join(exams_dir, filename)
                                    break
                        except:
                            continue
            
            if exam_file:
                exam_data = load_exam_data(exam_file)
                # Start the exam with session data and file path
                window = MockExamApp(exam_data, shuffle_enabled, selected_session, exam_file_path=exam_file)
                window.show()
                sys.exit(app.exec())
            else:
                QMessageBox.warning(None, "Error", f"Could not find exam file for session: {exam_title}")
                sys.exit(1)
        else:
            sys.exit(0)
    else:
        sys.exit(0) 