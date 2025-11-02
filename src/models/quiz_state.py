import copy
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional
from PyQt6.QtCore import QObject, pyqtSignal


class QuizState(QObject):
    """Complete application state with PyQt signals for MVVM data binding."""
    
    # Signals for state changes
    current_index_changed = pyqtSignal(int)
    score_changed = pyqtSignal(int)
    wrong_answers_changed = pyqtSignal(list)
    answered_questions_changed = pyqtSignal(set)
    answer_revealed_changed = pyqtSignal(bool)
    pause_state_changed = pyqtSignal(bool)
    review_mode_changed = pyqtSignal(bool)
    timer_elapsed_changed = pyqtSignal(timedelta)
    practice_mode_changed = pyqtSignal(bool)
    
    def __init__(self, exam_data: Dict, shuffle_enabled: bool = False, session_data: Optional[Dict] = None, practice_mode: bool = False, show_answer_at_end: bool = False):
        super().__init__()
        self.exam_data = exam_data
        self.original_exam_data = copy.deepcopy(exam_data)
        self.shuffle_enabled = shuffle_enabled
        self.session_data = session_data
        self._practice_mode = practice_mode
        self.show_answer_at_end = show_answer_at_end
        
        # Exam data
        self.exam_file_path: Optional[str] = None
        self.session_filepath: Optional[str] = None
        self.original_session_date: Optional[str] = None
        
        # Quiz state
        self._current_index = 0
        self._score = 0
        self._wrong_answers: List[Dict] = []
        self._answered_questions: Set[int] = set()
        self._answer_revealed = False
        
        # Pause and review state
        self._is_paused = False
        self._review_mode = False
        self.review_questions: List[Dict] = []
        
        # Timer state
        self.start_time: Optional[datetime] = None
        self._elapsed_time = timedelta(0)
        
        # Initialize from session data if resuming
        if session_data:
            self.session_filepath = session_data.get('_filepath')
            self.original_session_date = session_data.get('session_date')
            quiz_mode = session_data.get('quiz_mode', {})
            self._score = quiz_mode.get('score', 0)
            self._wrong_answers = quiz_mode.get('wrong_answers', [])
            self._answered_questions = set(range(quiz_mode.get('total_answered', 0)))
            self._current_index = quiz_mode.get('total_answered', 0)
            
            if 'timer_data' in session_data:
                timer_data = session_data['timer_data']
                self._elapsed_time = timedelta(seconds=timer_data.get('elapsed_seconds', 0))
        
        # Shuffle questions if enabled
        if shuffle_enabled:
            import random
            random.shuffle(self.exam_data['questions'])
    
    @property
    def current_index(self) -> int:
        return self._current_index
    
    @current_index.setter
    def current_index(self, value: int):
        if self._current_index != value:
            self._current_index = value
            self.current_index_changed.emit(value)
    
    @property
    def score(self) -> int:
        return self._score
    
    @score.setter
    def score(self, value: int):
        if self._score != value:
            self._score = value
            self.score_changed.emit(value)
    
    @property
    def wrong_answers(self) -> List[Dict]:
        return self._wrong_answers
    
    @wrong_answers.setter
    def wrong_answers(self, value: List[Dict]):
        self._wrong_answers = value
        self.wrong_answers_changed.emit(value)
    
    @property
    def answered_questions(self) -> Set[int]:
        return self._answered_questions
    
    @answered_questions.setter
    def answered_questions(self, value: Set[int]):
        self._answered_questions = value
        self.answered_questions_changed.emit(value)
    
    @property
    def answer_revealed(self) -> bool:
        return self._answer_revealed
    
    @answer_revealed.setter
    def answer_revealed(self, value: bool):
        if self._answer_revealed != value:
            self._answer_revealed = value
            self.answer_revealed_changed.emit(value)
    
    @property
    def is_paused(self) -> bool:
        return self._is_paused
    
    @is_paused.setter
    def is_paused(self, value: bool):
        if self._is_paused != value:
            self._is_paused = value
            self.pause_state_changed.emit(value)
    
    @property
    def review_mode(self) -> bool:
        return self._review_mode
    
    @review_mode.setter
    def review_mode(self, value: bool):
        if self._review_mode != value:
            self._review_mode = value
            self.review_mode_changed.emit(value)
    
    @property
    def elapsed_time(self) -> timedelta:
        return self._elapsed_time
    
    @elapsed_time.setter
    def elapsed_time(self, value: timedelta):
        self._elapsed_time = value
        self.timer_elapsed_changed.emit(value)
    
    @property
    def practice_mode(self) -> bool:
        return self._practice_mode
    
    @practice_mode.setter
    def practice_mode(self, value: bool):
        if self._practice_mode != value:
            self._practice_mode = value
            self.practice_mode_changed.emit(value)
    
    def get_current_question(self) -> Optional[Dict]:
        """Get the current question based on review mode or normal mode."""
        if self.review_mode and self.review_questions:
            if 0 <= self.current_index < len(self.review_questions):
                return self.review_questions[self.current_index]
        elif 0 <= self.current_index < len(self.exam_data['questions']):
            return self.exam_data['questions'][self.current_index]
        return None
    
    def get_total_questions(self) -> int:
        """Get total number of questions in current mode."""
        if self.review_mode:
            return len(self.review_questions)
        return len(self.exam_data['questions'])
    
    def reset(self):
        """Reset the quiz state to initial values."""
        self._current_index = 0
        self._score = 0
        self._wrong_answers = []
        self._answered_questions = set()
        self._answer_revealed = False
        self._is_paused = False
        self._review_mode = False
        self.review_questions = []
        self._elapsed_time = timedelta(0)
        self.start_time = None 