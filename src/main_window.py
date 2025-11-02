import sys
import os
import json
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QScrollArea, QMessageBox, QDialog)
from PyQt6.QtCore import Qt, QTimer, QEventLoop

from src.models.quiz_state import QuizState
from src.viewmodels.quiz_viewmodel import QuizViewModel
from src.viewmodels.timer_viewmodel import TimerViewModel
from src.viewmodels.session_viewmodel import SessionViewModel
from src.viewmodels.results_viewmodel import ResultsViewModel
from src.components.styles import Styles
from src.components.widgets import (HeaderWidget, QuestionDisplayWidget,
                                   OptionButtonsWidget, NavigationFooterWidget,
                                   StatusBarWidget, QuestionTimelineWidget)
from src.utils.shortcuts import ShortcutManager


class MockExamApp(QMainWindow):
    def __init__(self, exam_data, shuffle_enabled=False, session_data=None, exam_file_path=None, practice_mode=False, show_answer_at_end=False):
        super().__init__()
        
        # Initialize styles
        self.styles = Styles()
        self.colors = self.styles.colors
        
        # Create state model
        self.quiz_state = QuizState(exam_data, shuffle_enabled, session_data, practice_mode, show_answer_at_end)
        if exam_file_path:
            self.quiz_state.exam_file_path = exam_file_path
        
        # Create ViewModels
        self.timer_viewmodel = TimerViewModel(self.quiz_state)
        self.quiz_viewmodel = QuizViewModel(self.quiz_state)
        self.session_viewmodel = SessionViewModel(self.quiz_state, self.timer_viewmodel)
        self.results_viewmodel = ResultsViewModel(self.quiz_state, self.timer_viewmodel)
        
        # Set up window
        self._setup_window()
        
        # Create widgets
        self._create_widgets()
        
        # Connect signals
        self._connect_signals()
        
        # Set up shortcuts
        self.shortcut_manager = ShortcutManager(self)
        self._setup_shortcuts()
        
        # Set up crash protection
        self.session_viewmodel.setup_crash_protection()
        self.original_closeEvent = self.closeEvent
        self.closeEvent = self._custom_close_event
        
        # Display first question
        self.quiz_viewmodel._display_current_question()
        
        # Start timer for new sessions or resume for existing sessions (only if not in practice mode)
        if not self.quiz_state.practice_mode and (not session_data or (session_data and 'timer_data' in session_data)):
            self.timer_viewmodel.start_timer()
    
    def _setup_window(self):
        """Set up the main window."""
        if self.quiz_state.practice_mode:
            title_suffix = " - Practice Mode"
            if self.quiz_state.shuffle_enabled:
                title_suffix += " (Shuffled)"
        elif self.quiz_state.session_data:
            title_suffix = " - Resuming Session"
            if self.quiz_state.shuffle_enabled:
                title_suffix += " (Shuffled)"
        else:
            title_suffix = " - Study Mode (Shuffled)" if self.quiz_state.shuffle_enabled else " - Study Mode"
        self.setWindowTitle(f"{self.quiz_state.exam_data['title']}{title_suffix}")
        self.setMinimumSize(800, 600)
        
        # Set application style
        self.setStyleSheet(self.styles.get_application_style())
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create header
        header = HeaderWidget(self.quiz_state.exam_data['title'], self.styles)
        header.set_practice_mode(self.quiz_state.practice_mode)
        main_layout.addWidget(header)
        self.header_widget = header
        
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
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(24)
        
        # Question display
        question_display = QuestionDisplayWidget(self.styles)
        content_layout.addWidget(question_display)
        self.question_display = question_display
        
        # Option buttons
        option_buttons = OptionButtonsWidget(self.styles)
        content_layout.addWidget(option_buttons)
        self.option_buttons = option_buttons
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Create footer
        footer = NavigationFooterWidget(self.styles, len(self.quiz_state.exam_data['questions']), 
                                        practice_mode=self.quiz_state.practice_mode, 
                                        quiz_state=self.quiz_state)
        main_layout.addWidget(footer)
        self.nav_footer = footer
        
        # Create status bar
        status_bar = StatusBarWidget(self.styles, self.quiz_state, self.timer_viewmodel)
        self.setStatusBar(status_bar)
        self.status_bar_widget = status_bar
    
    def _create_widgets(self):
        """Widgets are created in _setup_window, this is a placeholder."""
        pass
    
    def _connect_signals(self):
        """Connect all ViewModel and widget signals."""
        # Header signals
        self.header_widget.dark_mode_toggled.connect(self._toggle_dark_mode)
        self.header_widget.pause_toggled.connect(self._toggle_pause)
        self.header_widget.quit_clicked.connect(self._quit_quiz)
        
        # Option buttons signals
        self.option_buttons.option_selected.connect(self._on_option_selected)
        self.option_buttons.option_clicked.connect(self._on_option_clicked)
        
        # Navigation footer signals
        self.nav_footer.prev_clicked.connect(self.quiz_viewmodel.previous_question)
        self.nav_footer.next_clicked.connect(self.quiz_viewmodel.next_question)
        self.nav_footer.action_clicked.connect(self._handle_action_button)
        self.nav_footer.study_clicked.connect(self.quiz_viewmodel.study_wrong_questions)
        if hasattr(self.nav_footer, 'question_jumped'):
            self.nav_footer.question_jumped.connect(self.quiz_viewmodel.jump_to_question)
        
        # Quiz ViewModel signals
        self.quiz_viewmodel.question_changed.connect(self._on_question_changed)
        self.quiz_viewmodel.review_question_ready.connect(self._on_review_question_ready)
        self.quiz_viewmodel.option_selected.connect(self.question_display.set_selection)
        self.quiz_viewmodel.answer_validated.connect(self._on_answer_validated)
        self.quiz_viewmodel.navigation_state_changed.connect(self.nav_footer.update_navigation_state)
        self.quiz_viewmodel.progress_changed.connect(self._on_progress_changed)
        self.quiz_viewmodel.review_mode_entered.connect(self._on_review_mode_entered)
        self.quiz_viewmodel.study_mode_entered.connect(self._on_study_mode_entered)
        self.quiz_viewmodel.quiz_complete.connect(self._on_quiz_complete)
        
        # Quiz State signals for timeline updates
        self.quiz_state.answered_questions_changed.connect(self._on_answered_questions_changed)
        self.quiz_state.wrong_answers_changed.connect(self._on_wrong_answers_changed)
        
        # Timer ViewModel signals
        self.timer_viewmodel.time_updated.connect(self.status_bar_widget.update_status)
        
        # Quiz State signals
        self.quiz_state.pause_state_changed.connect(self._on_pause_state_changed)
        self.quiz_state.answer_revealed_changed.connect(self._on_answer_revealed_changed)
        self.quiz_state.review_mode_changed.connect(self._on_review_mode_changed)
        
        # Results ViewModel signals
        self.results_viewmodel.results_ready.connect(self._on_results_ready)
    
    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        self.shortcut_manager.setup_global_shortcuts(
            show_answer_callback=self._show_answer,
            next_question_callback=self._shortcut_next_question,
            prev_question_callback=self.quiz_viewmodel.previous_question,
            dark_mode_callback=self._toggle_dark_mode,
            pause_callback=self._toggle_pause
        )
    
    def _on_question_changed(self, question: dict, current: int, total: int):
        """Handle question changed signal."""
        # Set question text
        self.question_display.set_question(question['question'])
        
        # Create options
        question_type = question.get('type', 'singleChoice')
        self.option_buttons.create_options(question['options'], question_type)
        
        # Set up option shortcuts
        self.shortcut_manager.setup_option_shortcuts(
            len(question['options']),
            lambda idx: self.option_buttons.option_buttons[idx].setChecked(True)
        )
        
        # Reset UI state
        self.question_display.hide_answer()
        self.question_display.set_selection("")
        # In practice mode, enable action button immediately for navigation
        if self.quiz_state.practice_mode:
            self.nav_footer.set_action_button_text("Next →", enabled=True, is_secondary=True)
        else:
            self.nav_footer.set_action_button_text("Confirm Answer", enabled=False, is_secondary=False)
        self.option_buttons.set_enabled(True)
        self.option_buttons.clear_selection()
        
        # Update status bar
        self.status_bar_widget.update_status()
        
        # Handle pause state
        if self.quiz_state.is_paused:
            self.question_display.question_label.hide()
            self.option_buttons.hide()
    
    def _on_review_question_ready(self, question: dict, wrong_info: dict):
        """Handle review question ready signal."""
        # Set question text
        self.question_display.set_question(question['question'])
        
        # Create options with highlighting
        question_type = question.get('type', 'singleChoice')
        self.option_buttons.create_options(question['options'], question_type)
        self.option_buttons.set_enabled(False)
        
        # Get answer info - check if we have answer_info (from show_answer_at_end) or wrong_answer_info (from review mode)
        answer_info = question.get('answer_info') or wrong_info
        your_answer = answer_info.get('your_answer', 'N/A')
        correct_answer_text = answer_info.get('correct_answer', 'N/A')
        is_correct = answer_info.get('is_correct', False)
        
        # Highlight correct/incorrect options
        correct_answer = question['answer']
        styles_map = {}
        for i, (key, value) in enumerate(question['options'].items()):
            if question_type == "multiChoice":
                is_correct_option = key in (correct_answer if isinstance(correct_answer, list) else [correct_answer])
            else:
                is_correct_option = key == correct_answer
            
            if is_correct_option:
                styles_map[i] = {
                    'border_color': self.colors['correct'],
                    'text_color': self.colors['correct'],
                    'border_width': 2,
                    'is_bold': True
                }
            else:
                # Check if this was the user's answer (for incorrect answers)
                if not is_correct:
                    # Handle both string and list formats
                    if isinstance(your_answer, list):
                        your_answer_text = ' '.join(str(v).lower() for v in your_answer)
                    else:
                        your_answer_text = str(your_answer).lower()
                    
                    option_key = key.lower()
                    option_value = value.lower()
                    is_user_answer = (option_key in your_answer_text or 
                                     option_value in your_answer_text or
                                     f"{key}." in your_answer_text)
                    
                    if is_user_answer:
                        styles_map[i] = {
                            'border_color': self.colors['warning'],
                            'text_color': self.colors['warning'],
                            'border_width': 2,
                            'is_bold': False
                        }
        
        if styles_map:
            self.option_buttons.set_option_styles(styles_map)
        
        # Show answer info
        self.question_display.set_review_answer(your_answer, correct_answer_text)
        
        # Update navigation (already handled by progress_changed signal, but ensure button text is correct)
        total = len(self.quiz_state.review_questions)
        current = self.quiz_state.current_index + 1
        self.nav_footer.set_action_button_text(f"Next → (Review {current}/{total})", enabled=True, is_secondary=True)
        
        # Update status bar
        self.status_bar_widget.update_status()
    
    def _on_option_selected(self, option_index: int, is_checked: bool):
        """Handle option selection."""
        self.quiz_viewmodel.select_option(option_index, is_checked)
        
        # For multi-choice questions, enable button when at least one option is selected
        question = self.quiz_state.get_current_question()
        question_type = question.get('type', 'singleChoice') if question else 'singleChoice'
        
        if question_type == "multiChoice" and not self.quiz_state.practice_mode:
            # Check if we have any selections after this change
            if self.quiz_viewmodel.selected_options:
                self.nav_footer.set_action_button_text("Confirm Answer", enabled=True, is_secondary=False)
            else:
                self.nav_footer.set_action_button_text("Confirm Answer", enabled=False, is_secondary=False)
    
    def _on_option_clicked(self, option_index: int):
        """Handle option click (for single choice)."""
        if self.quiz_state.practice_mode:
            # In practice mode, show "Show Answer" button
            self.nav_footer.set_action_button_text("Show Answer", enabled=True, is_secondary=False)
        else:
            self.nav_footer.set_action_button_text("Confirm Answer", enabled=True, is_secondary=False)
    
    def _show_answer(self):
        """Show answer and validate."""
        if not self.quiz_state.answer_revealed:
            # Sync selection from UI widgets to ensure we have the current state
            # This fixes the bug where changing answers didn't update the stored selection
            selected_indices = self.option_buttons.get_selected_indices()
            question = self.quiz_state.get_current_question()
            question_type = question.get('type', 'singleChoice') if question else 'singleChoice'
            
            if selected_indices:
                # Convert indices to option keys (A, B, C, D)
                selected_keys = [chr(ord('A') + idx) for idx in selected_indices]
                # Update viewmodel to match UI state
                if question_type == "singleChoice":
                    # Single choice: replace with the selected option
                    self.quiz_viewmodel.selected_options = selected_keys[:1]
                else:
                    # Multi choice: sync all selected options
                    self.quiz_viewmodel.selected_options = selected_keys
            else:
                # No selection made
                self.quiz_viewmodel.selected_options = []
            self.quiz_viewmodel.validate_answer()
    
    def _handle_action_button(self):
        """Handle action button click."""
        if self.quiz_state.review_mode:
            # In review mode, just go to next
            self.quiz_viewmodel.next_question()
        elif self.quiz_state.practice_mode:
            # In practice mode, allow free navigation or show answer if selected
            if self.quiz_viewmodel.selected_options and not self.quiz_state.answer_revealed:
                self._show_answer()
            else:
                self.quiz_viewmodel.next_question()
        elif not self.quiz_state.answer_revealed:
            self._show_answer()
        else:
            self.quiz_viewmodel.next_question()
    
    def _on_answer_validated(self, is_correct: bool, feedback_text: str, style_class: str):
        """Handle answer validation."""
        self.question_display.set_answer_feedback(feedback_text, is_correct, style_class)
        self.question_display.hide_selection()
        self.option_buttons.set_enabled(False)
        self.nav_footer.set_action_button_text("Next →", enabled=True, is_secondary=True)
        
        # Update status bar with new score
        self.status_bar_widget.update_status()
    
    def _shortcut_next_question(self):
        """Handle next question shortcut."""
        if not self.quiz_state.answer_revealed:
            QMessageBox.warning(self, "Warning", "Please show the answer before proceeding.")
            return
        if not self.quiz_viewmodel.selected_options:
            QMessageBox.warning(self, "Warning", "Please select an answer before proceeding.")
            return
        self.quiz_viewmodel.next_question()
    
    def _toggle_pause(self):
        """Toggle pause state."""
        self.quiz_state.is_paused = not self.quiz_state.is_paused
    
    def _on_pause_state_changed(self, is_paused: bool):
        """Handle pause state change."""
        self.header_widget.update_pause_state(is_paused)
        if is_paused:
            self.question_display.question_label.hide()
            self.option_buttons.hide()
            self.question_display.answer_label.hide()
            self.question_display.selection_indicator.hide()
            self.timer_viewmodel.stop_timer()
        else:
            self.question_display.question_label.show()
            self.option_buttons.show()
            if self.quiz_state.answer_revealed:
                self.question_display.answer_label.show()
            if self.quiz_viewmodel.selected_options:
                self.question_display.selection_indicator.show()
            self.timer_viewmodel.start_timer()
    
    def _on_answer_revealed_changed(self, is_revealed: bool):
        """Handle answer revealed state change."""
        if not is_revealed:
            self.question_display.hide_answer()
    
    def _toggle_dark_mode(self):
        """Toggle dark mode."""
        self.styles.toggle_dark_mode()
        self.colors = self.styles.colors
        
        # Update application style
        self.setStyleSheet(self.styles.get_application_style())
        
        # Update all widgets
        self.header_widget.update_colors(self.colors)
        self.header_widget.update_dark_mode(self.styles.dark_mode)
        self.question_display.update_colors(self.colors)
        self.option_buttons.update_colors(self.colors)
        self.nav_footer.update_colors(self.colors)
        self.status_bar_widget.update_colors(self.colors)
        # Update timeline if it exists
        if hasattr(self.nav_footer, 'timeline_widget') and self.nav_footer.timeline_widget:
            self.nav_footer.timeline_widget.update_colors(self.colors)
    
    def _on_progress_changed(self, current: int, total: int):
        """Handle progress update."""
        self.nav_footer.update_progress(current, total)
        # Also update status bar when progress changes
        self.status_bar_widget.update_status()
    
    def _on_answered_questions_changed(self, answered: set):
        """Handle answered questions change - update timeline."""
        if self.quiz_state.practice_mode and hasattr(self.nav_footer, 'timeline_widget') and self.nav_footer.timeline_widget:
            self.nav_footer.update_progress(self.quiz_state.current_index + 1, self.quiz_state.get_total_questions())
    
    def _on_wrong_answers_changed(self, wrong_answers: list):
        """Handle wrong answers change - update timeline."""
        if self.quiz_state.practice_mode and hasattr(self.nav_footer, 'timeline_widget') and self.nav_footer.timeline_widget:
            self.nav_footer.update_progress(self.quiz_state.current_index + 1, self.quiz_state.get_total_questions())
    
    def _on_review_mode_entered(self):
        """Handle review mode entered."""
        self.setWindowTitle(f"{self.quiz_state.original_exam_data['title']} - Review Mode")
        self.nav_footer.show_study_button(True)
        self.nav_footer.update_total_questions(len(self.quiz_state.review_questions))
    
    def _on_review_mode_changed(self, is_review_mode: bool):
        """Handle review mode state change."""
        if not is_review_mode:
            self.nav_footer.show_study_button(False)
    
    def _on_study_mode_entered(self, filtered_exam: dict):
        """Handle study mode entered."""
        self.setWindowTitle(filtered_exam['title'])
        self.nav_footer.show_study_button(False)
        self.nav_footer.update_total_questions(len(filtered_exam['questions']))
        self.nav_footer.set_action_button_text("Confirm Answer", enabled=False, is_secondary=False)
    
    def _on_quiz_complete(self, results: dict):
        """Handle quiz completion."""
        # Stop timer and save session
        self.timer_viewmodel.stop_timer()
        self.session_viewmodel.save_session_data(auto_save=False, emergency=False, completed=True)
        
        # Save results to file
        self.results_viewmodel.save_results_to_file()
        
        # Show results dialog
        total_time = self.timer_viewmodel.get_total_elapsed_time()
        time_str = self.timer_viewmodel.format_time(total_time)
        answered = len(self.quiz_state.answered_questions)
        percentage = (self.quiz_state.score / answered * 100) if answered > 0 else 0
        
        message = f"Your Score: {self.quiz_state.score}/{answered}\n"
        message += f"Time Taken: {time_str}\n\n"
        
        # If show_answer_at_end is enabled, we're already showing all answers
        if self.quiz_state.show_answer_at_end:
            message += "All answers are now visible. Navigate through the questions to review them.\n\n"
        elif self.quiz_state.wrong_answers:
            message += f"You had {len(self.quiz_state.wrong_answers)} incorrect answers.\n"
            message += "Would you like to review them?\n\n"
        
        message += f"Grade: {percentage:.1f}%"
        
        results_msg = QMessageBox(self)
        results_msg.setWindowTitle("Exam Results")
        results_msg.setIcon(QMessageBox.Icon.Information)
        results_msg.setText(message)
        
        review_button = None
        # Only show review button if we're not already in review mode showing all answers
        if self.quiz_state.wrong_answers and not self.quiz_state.show_answer_at_end:
            review_button = results_msg.addButton("Review Incorrect Answers", QMessageBox.ButtonRole.ActionRole)
        results_msg.addButton("Close", QMessageBox.ButtonRole.RejectRole)
        
        results_msg.exec()
        
        if results_msg.clickedButton() == review_button and self.quiz_state.wrong_answers:
            self.quiz_viewmodel.enter_review_mode()
        elif self.quiz_state.show_answer_at_end:
            # Don't close if we're showing all answers - let user navigate
            pass
        else:
            self.close()
    
    def _on_results_ready(self, results_data: dict):
        """Handle results ready signal."""
        pass
    
    def _quit_quiz(self):
        """Handle quit quiz button click."""
        # Save session before quitting with quit flag
        try:
            if self.session_viewmodel is not None:
                # Save with quit_by_user flag
                self.session_viewmodel.save_session_data(auto_save=False, emergency=True, quit_by_user=True)
        except Exception:
            # Fallback: try direct save with quit flag
            try:
                from src.utils.session_manager import SessionManager
                from datetime import datetime
                
                if self.quiz_state.original_session_date:
                    session_date = self.quiz_state.original_session_date
                else:
                    session_date = datetime.now().isoformat()
                
                total_elapsed = self.timer_viewmodel.get_total_elapsed_time() if hasattr(self, 'timer_viewmodel') and self.timer_viewmodel else timedelta(0)
                
                session_data = {
                    'session_date': session_date,
                    'exam_title': self.quiz_state.exam_data['title'],
                    'total_questions': len(self.quiz_state.exam_data['questions']),
                    'quiz_mode': {
                        'score': self.quiz_state.score,
                        'total_answered': len(self.quiz_state.answered_questions),
                        'wrong_answers': self.quiz_state.wrong_answers
                    },
                    'timer_data': {
                        'elapsed_seconds': int(total_elapsed.total_seconds()),
                        'completed': False,
                        'auto_saved': False,
                        'emergency_saved': True,
                        'quit_by_user': True
                    }
                }
                
                session_manager = SessionManager()
                session_manager.save_session(session_data, self.quiz_state.session_filepath)
            except Exception:
                pass
        
        # Close and delete the window to return to home page
        self.close()
        self.deleteLater()
    
    def _custom_close_event(self, event):
        """Custom close event handler."""
        try:
            if self.session_viewmodel is not None:
                self.session_viewmodel.emergency_save()
        except Exception as e:
            # SessionViewModel may have been deleted, try direct save
            try:
                from src.utils.session_manager import SessionManager
                from datetime import datetime
                
                if self.quiz_state.original_session_date:
                    session_date = self.quiz_state.original_session_date
                else:
                    session_date = datetime.now().isoformat()
                
                total_elapsed = self.timer_viewmodel.get_total_elapsed_time() if hasattr(self, 'timer_viewmodel') and self.timer_viewmodel else timedelta(0)
                
                session_data = {
                    'session_date': session_date,
                    'exam_title': self.quiz_state.exam_data['title'],
                    'total_questions': len(self.quiz_state.exam_data['questions']),
                    'quiz_mode': {
                        'score': self.quiz_state.score,
                        'total_answered': len(self.quiz_state.answered_questions),
                        'wrong_answers': self.quiz_state.wrong_answers
                    },
                    'timer_data': {
                        'elapsed_seconds': int(total_elapsed.total_seconds()),
                        'completed': False,
                        'auto_saved': True,
                        'emergency_saved': True
                    }
                }
                
                session_manager = SessionManager()
                session_manager.save_session(session_data, self.quiz_state.session_filepath)
            except Exception as save_error:
                pass  # Silently fail if save isn't possible
        event.accept()
    

def main():
    app = QApplication(sys.argv)
    # Don't quit when last window closes - we want to show dialog again
    app.setQuitOnLastWindowClosed(False)
    
    # Loop to allow returning to home page
    while True:
        # Show test selection dialog
        from src.components.dialogs.test_select_dialog import TestSelectDialog
        test_dialog = TestSelectDialog()
        
        if test_dialog.exec() != QDialog.DialogCode.Accepted:
            app.quit()  # User cancelled, exit app
            break
        selected_exam = test_dialog.get_selected_exam()
        selected_session = test_dialog.get_selected_session()
        selected_result = test_dialog.get_selected_result()
        shuffle_enabled = test_dialog.is_shuffle_enabled()
        practice_mode = test_dialog.is_practice_mode_enabled()
        show_answer_at_end = test_dialog.is_show_answer_at_end_enabled()
        
        if selected_result:
            # Load exam and enter review mode
            incorrect_answers = selected_result.get('detailed_results', {}).get('incorrect_answers', [])
            if not incorrect_answers:
                QMessageBox.information(None, "No Incorrect Answers", "This test session has no incorrect answers to review.")
                sys.exit(0)
            
            exam_file_path = selected_result.get('exam_info', {}).get('exam_file_path')
            if not exam_file_path:
                QMessageBox.warning(None, "Error", "Exam file path not found in result data.")
                sys.exit(1)
            
            project_root = os.path.dirname(os.path.dirname(__file__))
            if not os.path.isabs(exam_file_path):
                exam_file_path = os.path.join(project_root, exam_file_path)
            
            from src.utils.data_loader import load_exam_data
            try:
                exam_data = load_exam_data(exam_file_path)
            except Exception as e:
                QMessageBox.warning(None, "Error", f"Could not load exam file: {exam_file_path}\n\n{str(e)}")
                sys.exit(1)
            
            window = MockExamApp(exam_data, shuffle_enabled=False, exam_file_path=exam_file_path, practice_mode=practice_mode, show_answer_at_end=False)
            window.quiz_state.wrong_answers = incorrect_answers
            window.show()
            QTimer.singleShot(100, window.quiz_viewmodel.enter_review_mode)
            # Wait for window to close, then continue loop
            loop = QEventLoop()
            window.destroyed.connect(loop.quit)
            if window.isVisible():
                loop.exec()
        elif selected_exam:
            from src.utils.data_loader import load_exam_data
            exam_file_path = selected_exam['filepath']
            exam_data = load_exam_data(exam_file_path)
            
            window = MockExamApp(exam_data, shuffle_enabled, exam_file_path=exam_file_path, practice_mode=practice_mode, show_answer_at_end=show_answer_at_end)
            window.show()
            # Wait for window to close, then continue loop
            loop = QEventLoop()
            window.destroyed.connect(loop.quit)
            if window.isVisible():
                loop.exec()
        elif selected_session:
            from src.utils.data_loader import load_exam_data
            exam_title = selected_session['exam_title']
            project_root = os.path.dirname(os.path.dirname(__file__))
            
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
                window = MockExamApp(exam_data, shuffle_enabled, selected_session, exam_file_path=exam_file, practice_mode=practice_mode, show_answer_at_end=False)
                window.show()
                # Wait for window to close, then continue loop
                loop = QEventLoop()
                window.destroyed.connect(loop.quit)
                if window.isVisible():
                    loop.exec()
            else:
                QMessageBox.warning(None, "Error", f"Could not find exam file for session: {exam_title}")
                break  # Exit on error
    
    sys.exit(0) 
