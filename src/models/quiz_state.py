from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class QuizModeState:
    """Represents the state of the quiz mode."""
    current_index: int = 0
    score: int = 0
    total_answered: int = 0
    incorrect_answers: List[Dict] = field(default_factory=list)
    is_answer_shown: bool = False
    
    def reset(self):
        """Reset the quiz state to initial values."""
        self.current_index = 0
        self.score = 0
        self.total_answered = 0
        self.incorrect_answers = []
        self.is_answer_shown = False 