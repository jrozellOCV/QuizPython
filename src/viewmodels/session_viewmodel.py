import sys
import signal
import atexit
from datetime import datetime
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from src.models.quiz_state import QuizState


class SessionViewModel(QObject):
    """ViewModel for session management and auto-save."""
    
    session_saved = pyqtSignal(bool)  # Emits True if saved successfully
    emergency_save_completed = pyqtSignal()
    
    def __init__(self, quiz_state: QuizState, timer_viewmodel):
        super().__init__()
        self.quiz_state = quiz_state
        self.timer_viewmodel = timer_viewmodel
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_session)
        
    def setup_crash_protection(self):
        """Set up crash detection and auto-save mechanisms"""
        # Set up periodic auto-save
        self.auto_save_timer.start(30000)  # Auto-save every 30 seconds
        
        # Set up signal handlers for crash detection
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Register cleanup function for normal exit
        atexit.register(self.cleanup_on_exit)
    
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
    
    def auto_save_session(self):
        """Auto-save session data periodically"""
        try:
            self.save_session_data(auto_save=True)
        except Exception as e:
            print(f"Auto-save error: {e}")
    
    def emergency_save(self):
        """Emergency save when app is closing or crashing"""
        try:
            # Stop timer first if available
            if self.timer_viewmodel is not None:
                try:
                    self.timer_viewmodel.stop_timer()
                except:
                    pass  # Timer may already be stopped or deleted
            
            # Save session data
            self.save_session_data(auto_save=True, emergency=True)
            print("Emergency save completed")
            try:
                self.emergency_save_completed.emit()
            except:
                pass  # Signal may not be available if object is being deleted
        except Exception as e:
            print(f"Emergency save failed: {e}")
    
    def save_session_data(self, auto_save=False, emergency=False, completed=False, quit_by_user=False):
        """Save current session data including timer"""
        try:
            from src.utils.session_manager import SessionManager
            from datetime import timedelta
            
            # Preserve original session date if available, otherwise use current time
            if self.quiz_state.original_session_date:
                session_date = self.quiz_state.original_session_date
            else:
                session_date = datetime.now().isoformat()
                self.quiz_state.original_session_date = session_date
            
            # Get elapsed time safely
            try:
                if self.timer_viewmodel is not None:
                    total_elapsed = self.timer_viewmodel.get_total_elapsed_time()
                else:
                    total_elapsed = timedelta(0)
            except:
                total_elapsed = timedelta(0)
            
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
                    'completed': completed,
                    'auto_saved': auto_save,
                    'emergency_saved': emergency,
                    'quit_by_user': quit_by_user
                }
            }
            
            # Save session
            session_manager = SessionManager()
            saved_filepath = session_manager.save_session(session_data, self.quiz_state.session_filepath)
            
            # Store filepath for future saves
            self.quiz_state.session_filepath = saved_filepath
            
            if auto_save:
                print("Auto-save completed")
            
            try:
                self.session_saved.emit(True)
            except:
                pass  # Signal may not be available if object is being deleted
            
        except Exception as e:
            print(f"Error saving session: {e}")
            try:
                self.session_saved.emit(False)
            except:
                pass  # Ignore if object is being deleted

