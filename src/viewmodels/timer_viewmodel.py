from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from src.models.quiz_state import QuizState


class TimerViewModel(QObject):
    """ViewModel for timer management."""
    
    time_updated = pyqtSignal(str)  # Emits formatted time string
    time_changed = pyqtSignal(timedelta)  # Emits time delta
    
    def __init__(self, quiz_state: QuizState):
        super().__init__()
        self.quiz_state = quiz_state
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_timer)
        
    def start_timer(self):
        """Start the exam timer"""
        if not self.quiz_state.start_time:
            self.quiz_state.start_time = datetime.now()
            self.timer.start(1000)  # Update every second
    
    def stop_timer(self):
        """Stop the exam timer"""
        if self.quiz_state.start_time:
            self.timer.stop()
            current_session_time = datetime.now() - self.quiz_state.start_time
            self.quiz_state.elapsed_time += current_session_time
            self.quiz_state.start_time = None
    
    def _update_timer(self):
        """Update the timer display"""
        if self.quiz_state.start_time:
            current_session_time = datetime.now() - self.quiz_state.start_time
            total_time = self.quiz_state.elapsed_time + current_session_time
            # Don't update elapsed_time here - it should only be updated when pausing
            # This ensures pause/resume works correctly without double-counting time
            self.time_updated.emit(self.format_time(total_time))
            self.time_changed.emit(total_time)
    
    def get_total_elapsed_time(self) -> timedelta:
        """Get total elapsed time including current session"""
        if self.quiz_state.start_time:
            current_session_time = datetime.now() - self.quiz_state.start_time
            return self.quiz_state.elapsed_time + current_session_time
        return self.quiz_state.elapsed_time
    
    def format_time(self, time_delta: timedelta) -> str:
        """Format time delta as HH:MM:SS"""
        total_seconds = int(time_delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

