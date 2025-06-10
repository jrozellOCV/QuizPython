import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QRadioButton, 
                            QButtonGroup, QProgressBar, QScrollArea, QMessageBox,
                            QStatusBar, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QKeySequence, QAction, QColor

from src.components.flashcard import FlashCard
from src.components.review_dialog import ReviewDialog
from src.components.styles import Styles
from src.utils.data_loader import load_exam_data

class MockExamApp(QMainWindow):
    def __init__(self, exam_data):
        super().__init__()
        self.exam_data = exam_data
        self.current_index = 0
        self.score = 0
        self.wrong_answers = []
        self.answer_revealed = False
        self.flashcard_mode = False
        self.known_cards = set()
        self.answered_questions = set()
        
        # Initialize styles
        self.styles = Styles()
        self.colors = self.styles.colors
        
        # Set up the main window
        self.setWindowTitle(f"{exam_data['title']} - Study Mode")
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
        
        # Title
        title_label = QLabel(exam_data['title'])
        title_label.setFont(QFont('Helvetica', 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(self.styles.styles['label_title'])
        header_layout.addWidget(title_label)
        
        # Mode toggle container
        mode_container = QWidget()
        mode_layout = QHBoxLayout(mode_container)
        mode_layout.setContentsMargins(0, 12, 0, 0)  # Add top margin
        
        # Mode toggle button
        self.mode_toggle = QPushButton("Switch to Flash Card Mode")
        self.mode_toggle.setFont(QFont('Helvetica', 14, QFont.Weight.Bold))
        self.mode_toggle.setMinimumHeight(44)
        self.mode_toggle.setStyleSheet(self.styles.styles['button'])
        self.mode_toggle.setCheckable(True)
        self.mode_toggle.clicked.connect(self.toggle_flashcard_mode)
        mode_layout.addWidget(self.mode_toggle)
        header_layout.addWidget(mode_container)
        
        # Add header to main layout
        main_layout.addWidget(header_widget)
        
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {self.colors['background']};
            }}
            QScrollBar:vertical {{
                border: none;
                background: {self.colors['background']};
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.colors['border']};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        # Create content widget for scroll area
        content_widget = QWidget()
        scroll.setWidget(content_widget)
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(20)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Question text
        self.question_label = QLabel()
        self.question_label.setFont(QFont('Helvetica', 14))
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet(f"""
            {self.styles.styles['card']}
            QLabel {{
                font-size: 16px;
                line-height: 1.5;
            }}
        """)
        self.content_layout.addWidget(self.question_label)
        
        # Options
        self.option_group = QButtonGroup()
        self.option_buttons = []
        for i in range(4):
            option = QRadioButton()
            option.setFont(QFont('Helvetica', 12))
            option.setStyleSheet(self.styles.styles['radio_button'])
            self.option_group.addButton(option, i)
            self.content_layout.addWidget(option)
            self.option_buttons.append(option)
        
        # Add selection indicator label
        self.selection_indicator = QLabel()
        self.selection_indicator.setFont(QFont('Helvetica', 12))
        self.selection_indicator.setStyleSheet(f"""
            {self.styles.styles['label_text']}
            color: {self.colors['primary']};
            font-style: italic;
        """)
        self.selection_indicator.hide()
        self.content_layout.addWidget(self.selection_indicator)
        
        # Answer display
        self.answer_label = QLabel()
        self.answer_label.setFont(QFont('Helvetica', 12, QFont.Weight.Bold))
        self.answer_label.setWordWrap(True)
        self.answer_label.setStyleSheet(f"""
            {self.styles.styles['card']}
            QLabel {{
                font-size: 16px;
                line-height: 1.5;
            }}
        """)
        self.answer_label.hide()
        self.content_layout.addWidget(self.answer_label)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll)
        
        # Create footer widget (sticky)
        footer_widget = QWidget()
        footer_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['card']};
                border-top: none;
            }}
        """)
        # Add shadow effect to footer
        footer_shadow = QGraphicsDropShadowEffect()
        footer_shadow.setBlurRadius(8)
        footer_shadow.setColor(QColor(30, 41, 59, 8))  # rgba(30,41,59,0.03)
        footer_shadow.setOffset(0, -2)
        footer_widget.setGraphicsEffect(footer_shadow)
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(32, 20, 32, 28)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(len(exam_data['questions']))
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
        
        # Flashcard review buttons (footer)
        self.known_button = QPushButton("✓ I Know This")
        self.known_button.setStyleSheet(self.styles.styles['button_success'])
        self.known_button.clicked.connect(lambda: self.mark_card(True))
        self.known_button.hide()
        nav_layout.addWidget(self.known_button)

        self.unknown_button = QPushButton("✗ Need More Review")
        self.unknown_button.setStyleSheet(self.styles.styles['button_warning'])
        self.unknown_button.clicked.connect(lambda: self.mark_card(False))
        self.unknown_button.hide()
        nav_layout.addWidget(self.unknown_button)
        
        footer_layout.addWidget(nav_container)
        
        # Add footer to main layout
        main_layout.addWidget(footer_widget)
        
        # Create flashcard widget
        self.flashcard = FlashCard(self)
        self.flashcard.hide()
        self.content_layout.addWidget(self.flashcard)
        
        # Set up keyboard shortcuts
        self.setup_shortcuts()
        
        # Display first question
        self.display_question()
    
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
        
        # Option shortcuts (1-4)
        for i in range(4):
            shortcut = QAction(self)
            shortcut.setShortcut(QKeySequence(str(i + 1)))
            shortcut.triggered.connect(lambda checked, idx=i: self.select_option(idx))
            self.addAction(shortcut)
    
    def select_option(self, index):
        if 0 <= index < len(self.option_buttons):
            self.option_buttons[index].setChecked(True)
    
    def toggle_flashcard_mode(self, checked):
        self.flashcard_mode = checked
        # Update mode toggle button
        self.mode_toggle.setText("Switch to Quiz Mode" if checked else "Switch to Flash Card Mode")
        self.mode_toggle.setStyleSheet(self.styles.styles['button_success'] if checked else self.styles.styles['button'])
        if checked:
            # Initialize flashcard mode
            self.content_layout.parentWidget().setStyleSheet(f"""
                QWidget {{
                    background-color: {self.colors['flashcard']};
                }}
            """)
            # Hide quiz elements
            self.question_label.hide()
            self.answer_label.hide()
            self.option_group.setExclusive(False)
            for button in self.option_buttons:
                button.hide()
            self.action_button.hide()
            self.prev_button.hide()
            # Show flashcard
            self.flashcard.show()
            # Show flashcard review buttons
            self.known_button.show()
            self.unknown_button.show()
        else:
            # Reset to normal mode
            self.current_index = 0
            self.content_layout.parentWidget().setStyleSheet("")
            # Show quiz elements
            self.question_label.show()
            self.answer_label.hide()
            self.option_group.setExclusive(True)
            for button in self.option_buttons:
                button.show()
            self.action_button.show()
            self.prev_button.show()
            # Hide flashcard
            self.flashcard.hide()
            # Hide flashcard review buttons
            self.known_button.hide()
            self.unknown_button.hide()
        self.display_question()
        self.update_status()

    def mark_card(self, known):
        if self.flashcard_mode:
            if known:
                self.known_cards.add(self.current_index)
            else:
                self.known_cards.discard(self.current_index)
            
            # Reset card to front side
            self.flashcard.is_flipped = False
            self.flashcard.stack.setCurrentIndex(0)
            
            # Move to next card
            self.current_index = (self.current_index + 1) % len(self.exam_data['questions'])
            self.display_question()
            self.update_status()

    def display_question(self):
        question = self.exam_data['questions'][self.current_index]
        
        # Update counter (single source of truth)
        counter_text = f"Question {self.current_index + 1} of {len(self.exam_data['questions'])}"
        self.nav_label.setText(counter_text)  # Only update nav label
        
        # Update navigation
        self.prev_button.setEnabled(self.current_index > 0)
        
        # Update question
        self.question_label.setText(question['question'])
        
        if not self.flashcard_mode:
            # Normal mode display
            self.option_group.setExclusive(False)
            for i, (key, value) in enumerate(question['options'].items()):
                self.option_buttons[i].setText(f"{key}. {value}")
                self.option_buttons[i].setChecked(False)
            self.option_group.setExclusive(True)
            
            # Reset answer display and selection indicator
            self.answer_label.hide()
            self.selection_indicator.hide()
            self.answer_revealed = False
            self.action_button.setText("Confirm Answer")
            self.action_button.setStyleSheet(self.styles.styles['button'])
            self.action_button.setEnabled(False)
            
            # Connect option selection handler
            self.option_group.buttonClicked.connect(self.on_option_selected)
        else:
            # Flashcard mode display
            self.flashcard.setContent(
                question['question'],
                question['answer'],
                question['options']
            )
        
        # Update progress
        self.progress_bar.setValue(self.current_index + 1)
        
        # Update status
        self.update_status()

    def on_option_selected(self, button):
        # Enable action button when an option is selected
        self.action_button.setEnabled(True)
        
        # Show selection indicator
        selected_option = chr(ord('A') + self.option_group.id(button))
        self.selection_indicator.setText(f"Selected: Option {selected_option}")
        self.selection_indicator.show()
        
        # Update button text based on selection
        self.action_button.setText(f"Confirm {selected_option}")
        self.action_button.setStyleSheet(self.styles.styles['button'])

    def handle_action_button(self):
        if not self.answer_revealed:
            self.show_answer()
        else:
            self.next_question()

    def show_answer(self):
        if not self.answer_revealed:
            question = self.exam_data['questions'][self.current_index]
            correct = question['answer']
            correct_text = question['options'][correct]
            
            # Get selected option
            selected_button = self.option_group.checkedButton()
            selected_option = chr(ord('A') + self.option_group.id(selected_button)) if selected_button else None
            
            # Update answer display with selection feedback
            if selected_option == correct:
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
            
            # Record answer if not in flashcard mode
            if not self.flashcard_mode and selected_button:
                if selected_option == correct:
                    self.score += 1
                else:
                    self.wrong_answers.append({
                        'question': question['question'],
                        'your_answer': selected_option,
                        'correct_answer': correct
                    })
                self.answered_questions.add(self.current_index)
                self.update_status()

    def next_question(self):
        if self.flashcard_mode:
            self.current_index = (self.current_index + 1) % len(self.exam_data['questions'])
            self.display_question()
            return
        
        if not self.answer_revealed:
            QMessageBox.warning(self, "Warning", "Please show the answer before proceeding.")
            return
        
        selected_button = self.option_group.checkedButton()
        if not selected_button:
            QMessageBox.warning(self, "Warning", "Please select an answer before proceeding.")
            return
        
        # Move to next question or show results
        self.current_index += 1
        if self.current_index >= len(self.exam_data['questions']):
            if self.flashcard_mode:
                self.current_index = 0  # Loop back to start in flashcard mode
            else:
                self.show_results()
        self.display_question()
    
    def show_results(self):
        # Create results window with more options
        results = QMessageBox(self)
        results.setWindowTitle("Exam Results")
        results.setIcon(QMessageBox.Icon.Information)
        
        # Format results message
        message = f"Your Score: {self.score}/{len(self.answered_questions)}\n\n"
        if self.wrong_answers:
            message += f"You had {len(self.wrong_answers)} incorrect answers.\n"
            message += "Would you like to review them in flashcard mode?"
        
        results.setText(message)
        
        # Add buttons
        review_button = results.addButton("Review in Flashcard Mode", QMessageBox.ButtonRole.ActionRole)
        results.addButton("Close", QMessageBox.ButtonRole.RejectRole)
        
        results.exec()
        
        if results.clickedButton() == review_button:
            self.flashcard_mode = True
            self.mode_toggle.setChecked(True)
            self.current_index = 0
            self.display_question()
            # Show review dialog
            review_dialog = ReviewDialog(self.wrong_answers, self)
            review_dialog.exec()
        else:
            self.close()

    def update_status(self):
        status = []
        if self.flashcard_mode:
            status.append("Flash Card Mode")
            known_count = len(self.known_cards)
            total_cards = len(self.exam_data['questions'])
            status.append(f"Known: {known_count}/{total_cards} cards")
        else:
            status.append(f"Score: {self.score}/{len(self.answered_questions)}" if self.answered_questions else "Not started")
        self.statusBar.showMessage(" | ".join(status))

    def previous_question(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_question()

def main():
    app = QApplication(sys.argv)
    exam_data = load_exam_data()
    window = MockExamApp(exam_data)
    window.show()
    sys.exit(app.exec()) 