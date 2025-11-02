from PyQt6.QtWidgets import QStatusBar
from src.components.styles import Styles
from src.models.quiz_state import QuizState
from src.viewmodels.timer_viewmodel import TimerViewModel


class StatusBarWidget(QStatusBar):
    """Status bar widget displaying quiz statistics and timer."""
    
    def __init__(self, styles: Styles, quiz_state: QuizState, timer_viewmodel: TimerViewModel):
        super().__init__()
        self.styles = styles
        self.colors = styles.colors
        self.quiz_state = quiz_state
        self.timer_viewmodel = timer_viewmodel
        
        # Initialize status
        self.current_time_str = "00:00:00"
        self.current_status_text = "Not started"
        
        # Set initial status
        self._update_status()
    
    def update_status(self, status_text: str = None):
        """Update status bar with timer and stats."""
        if status_text is not None:
            self.current_status_text = status_text
        self._update_status()
    
    def _update_status(self):
        """Internal method to update status bar display."""
        # Check if in practice mode
        if self.quiz_state.practice_mode:
            # Practice mode: show status without timer
            if self.quiz_state.review_mode:
                total_review = len(self.quiz_state.review_questions)
                current_review = self.quiz_state.current_index + 1
                status = f"Review: {current_review}/{total_review} | Practice Mode"
            else:
                total = self.quiz_state.get_total_questions()
                current = self.quiz_state.current_index + 1
                answered = len(self.quiz_state.answered_questions)
                score = self.quiz_state.score
                wrong = len(self.quiz_state.wrong_answers)
                
                if answered > 0:
                    accuracy = (score / answered * 100) if answered > 0 else 0
                    status = f"Question {current}/{total} | Score: {score}/{answered} | Accuracy: {accuracy:.1f}% | Incorrect: {wrong} | Practice Mode"
                else:
                    status = f"Question {current}/{total} | Not started | Practice Mode"
        else:
            # Normal mode: show timer
            # Get current time
            try:
                time_str = self.timer_viewmodel.format_time(self.timer_viewmodel.get_total_elapsed_time())
                self.current_time_str = time_str
            except:
                time_str = self.current_time_str
            
            # Combine timer and status
            if self.quiz_state.review_mode:
                total_review = len(self.quiz_state.review_questions)
                current_review = self.quiz_state.current_index + 1
                status = f"Review: {current_review}/{total_review} | Time: {time_str}"
            else:
                # Build comprehensive status
                total = self.quiz_state.get_total_questions()
                current = self.quiz_state.current_index + 1
                answered = len(self.quiz_state.answered_questions)
                score = self.quiz_state.score
                wrong = len(self.quiz_state.wrong_answers)
                
                if answered > 0:
                    accuracy = (score / answered * 100) if answered > 0 else 0
                    status = f"Question {current}/{total} | Score: {score}/{answered} | Accuracy: {accuracy:.1f}% | Incorrect: {wrong} | Time: {time_str}"
                else:
                    status = f"Question {current}/{total} | Not started | Time: {time_str}"
        
        self.showMessage(status)
    
    def update_colors(self, colors: dict):
        """Update colors when theme changes."""
        self.colors = colors
        # Status bar colors are handled by application style, but we can update if needed
        self._update_status()

