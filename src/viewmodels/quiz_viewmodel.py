from typing import Optional, List, Dict, Set
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal
from src.models.quiz_state import QuizState


class QuizViewModel(QObject):
    """Main ViewModel for quiz logic, question navigation, and answer validation."""
    
    # Signals for UI updates
    question_changed = pyqtSignal(dict, int, int)  # question, current_index, total
    option_selected = pyqtSignal(str, bool)  # selected_text, is_multi_choice
    answer_validated = pyqtSignal(bool, str, str)  # is_correct, feedback_text, style_class
    review_question_ready = pyqtSignal(dict, dict)  # question, wrong_answer_info
    navigation_state_changed = pyqtSignal(bool, bool)  # can_go_prev, can_go_next
    progress_changed = pyqtSignal(int, int)  # current, total
    status_text_changed = pyqtSignal(str)
    review_mode_entered = pyqtSignal()
    study_mode_entered = pyqtSignal(dict)  # filtered_exam_data
    quiz_complete = pyqtSignal(dict)  # results dict
    
    def __init__(self, quiz_state: QuizState):
        super().__init__()
        self.quiz_state = quiz_state
        self.current_question_type = "singleChoice"
        self.selected_options: List[str] = []
        
    def get_current_question(self) -> Optional[Dict]:
        """Get current question data."""
        return self.quiz_state.get_current_question()
    
    def select_option(self, option_index: int, is_checked: bool):
        """Handle option selection."""
        option_key = chr(ord('A') + option_index)
        
        if self.current_question_type == "multiChoice":
            if is_checked:
                if option_key not in self.selected_options:
                    self.selected_options.append(option_key)
            else:
                if option_key in self.selected_options:
                    self.selected_options.remove(option_key)
            
            if self.selected_options:
                selected_text = ", ".join(sorted(self.selected_options))
                self.option_selected.emit(f"Selected: Options {selected_text}", True)
            else:
                self.option_selected.emit("No options selected", True)
        else:
            self.selected_options = [option_key] if is_checked else []
            if is_checked:
                self.option_selected.emit(f"Selected: Option {option_key}", False)
    
    def validate_answer(self) -> bool:
        """Validate the selected answer and update state. Returns True if answer was validated."""
        if not self.selected_options:
            return False
        
        question = self.get_current_question()
        if not question:
            return False
        
        correct = question['answer']
        question_type = question.get('type', 'singleChoice')
        
        # Check if answer is correct
        if question_type == "multiChoice":
            correct_set = set(correct) if isinstance(correct, list) else {correct}
            selected_set = set(self.selected_options)
            is_correct = correct_set == selected_set
        else:
            is_correct = self.selected_options[0] == correct if self.selected_options else False
        
        # Update state - don't reveal answer if show_answer_at_end is enabled
        if not self.quiz_state.show_answer_at_end:
            self.quiz_state.answer_revealed = True
        
        # Prepare answer text for storage
        if question_type == "multiChoice":
            your_texts = [question['options'][opt] for opt in self.selected_options]
            correct_list = correct if isinstance(correct, list) else [correct]
            correct_texts = [question['options'][opt] for opt in correct_list]
            your_answer_value = "; ".join(your_texts)
            correct_answer_value = "; ".join(correct_texts)
        else:
            your_answer_value = question['options'].get(self.selected_options[0], "")
            correct_answer_value = question['options'].get(correct, "")
        
        if is_correct:
            self.quiz_state.score += 1
            if question_type == "multiChoice":
                feedback = f"✓ Correct! Your answers {', '.join(self.selected_options)} were right."
            else:
                feedback = f"✓ Correct! Your answer {self.selected_options[0]} was right."
            style_class = "correct"
        else:
            # Store wrong answer
            wrong_answer = {
                'question_id': question.get('id'),
                'question': question['question'],
                'your_answer': your_answer_value,
                'correct_answer': correct_answer_value
            }
            
            # Update wrong_answers list
            wrong_answers = list(self.quiz_state.wrong_answers)
            wrong_answers.append(wrong_answer)
            self.quiz_state.wrong_answers = wrong_answers
            
            # Create feedback text
            if question_type == "multiChoice":
                selected_text = ", ".join(self.selected_options)
                correct_text = ", ".join(correct) if isinstance(correct, list) else correct
                correct_options_text = "\n".join([f"{opt}. {question['options'][opt]}" for opt in correct])
                feedback = (f"✗ Incorrect. You selected {selected_text}, but the correct answers are {correct_text}.\n\n"
                           f"Correct Answers:\n{correct_options_text}")
            else:
                correct_text = question['options'][correct]
                feedback = (f"✗ Incorrect. You selected {self.selected_options[0]}, but the correct answer is {correct}.\n\n"
                           f"Correct Answer: {correct}. {correct_text}")
            
            style_class = "incorrect"
        
        # Mark question as answered
        answered = set(self.quiz_state.answered_questions)
        answered.add(self.quiz_state.current_index)
        self.quiz_state.answered_questions = answered
        
        # Only emit answer validation if we're revealing the answer
        if not self.quiz_state.show_answer_at_end:
            self.answer_validated.emit(is_correct, feedback, style_class)
        else:
            # In show_answer_at_end mode, mark as "answered" to allow navigation
            # but don't show feedback
            self.quiz_state.answer_revealed = True
        
        self.update_status()
        return True
    
    def next_question(self) -> bool:
        """Move to next question. Returns True if moved, False if quiz complete or validation needed."""
        if self.quiz_state.review_mode:
            return self._next_review_question()
        
        # In practice mode, allow free navigation without validation
        if self.quiz_state.practice_mode:
            if self.quiz_state.current_index + 1 >= self.quiz_state.get_total_questions():
                # Reached end - don't complete quiz in practice mode
                return False
            
            self.quiz_state.current_index += 1
            self._reset_question_state()
            self._display_current_question()
            return True
        
        # Normal mode: require validation
        # Check if answer needs to be revealed first
        if not self.quiz_state.answer_revealed:
            return False
        
        # Check if answer was selected
        if not self.selected_options:
            return False
        
        # Move to next question
        if self.quiz_state.current_index + 1 >= self.quiz_state.get_total_questions():
            # Quiz complete
            self._complete_quiz()
            return True
        
        self.quiz_state.current_index += 1
        self._reset_question_state()
        self._display_current_question()
        return True
    
    def previous_question(self):
        """Move to previous question."""
        if self.quiz_state.practice_mode:
            # In practice mode, allow navigation without validation
            if self.quiz_state.current_index > 0:
                self.quiz_state.current_index -= 1
                self._reset_question_state()
                self._display_current_question()
        else:
            # Normal mode: require validation
            if self.quiz_state.current_index > 0:
                self.quiz_state.current_index -= 1
                self._reset_question_state()
                self._display_current_question()
    
    def jump_to_question(self, index: int):
        """Jump to a specific question (practice mode only)."""
        if not self.quiz_state.practice_mode:
            return False
        
        if 0 <= index < self.quiz_state.get_total_questions():
            self.quiz_state.current_index = index
            self._reset_question_state()
            self._display_current_question()
            return True
        return False
    
    def _next_review_question(self) -> bool:
        """Handle next question in review mode."""
        if self.quiz_state.current_index + 1 >= len(self.quiz_state.review_questions):
            # Reached end of review
            return False
        
        self.quiz_state.current_index += 1
        self._display_current_question()
        return True
    
    def _complete_quiz(self):
        """Handle quiz completion."""
        # Don't complete quiz in practice mode
        if self.quiz_state.practice_mode:
            return
        
        # If show_answer_at_end is enabled, reveal all answers before completing
        if self.quiz_state.show_answer_at_end:
            self._reveal_all_answers()
        
        results = {
            'score': self.quiz_state.score,
            'total_answered': len(self.quiz_state.answered_questions),
            'wrong_answers': self.quiz_state.wrong_answers
        }
        self.quiz_complete.emit(results)
    
    def _reveal_all_answers(self):
        """Reveal all answers for all questions in the quiz."""
        # This will be called to show all answers at the end
        # We'll enter a review mode showing all questions with answers
        all_questions = []
        
        for i, question in enumerate(self.quiz_state.exam_data['questions']):
            question_copy = question.copy()
            
            # Find user's answer and whether it was correct
            question_id = question.get('id')
            correct = question['answer']
            question_type = question.get('type', 'singleChoice')
            
            # Check if this question was answered
            if i not in self.quiz_state.answered_questions:
                continue
            
            # Try to find user's selected answer from wrong_answers
            your_answer = None
            correct_answer_text = None
            is_correct = False
            
            # Check if this question was answered incorrectly
            wrong_answer_info = None
            for wrong in self.quiz_state.wrong_answers:
                if wrong.get('question_id') == question_id or wrong.get('question') == question['question']:
                    wrong_answer_info = wrong
                    your_answer = wrong.get('your_answer', 'Not answered')
                    correct_answer_text = wrong.get('correct_answer', '')
                    is_correct = False
                    break
            
            # If not in wrong answers, it was correct - user selected the correct answer
            if wrong_answer_info is None:
                # Find correct answer text
                if question_type == "multiChoice":
                    correct_list = correct if isinstance(correct, list) else [correct]
                    correct_answer_text = "; ".join([question['options'].get(opt, opt) for opt in correct_list])
                    your_answer = correct_answer_text
                else:
                    correct_answer_text = question['options'].get(correct, correct)
                    your_answer = correct_answer_text
                is_correct = True
            
            # Store answer info for review
            question_copy['answer_info'] = {
                'your_answer': your_answer,
                'correct_answer': correct_answer_text,
                'is_correct': is_correct
            }
            all_questions.append(question_copy)
        
        # Enter review mode with all questions
        self.quiz_state.review_questions = all_questions
        self.quiz_state.review_mode = True
        self.quiz_state.current_index = 0
        self.quiz_state.exam_data = {
            'title': f"{self.quiz_state.original_exam_data['title']} - All Answers",
            'questions': all_questions
        }
        
        # Display the first question
        self._display_current_question()
    
    def enter_review_mode(self) -> bool:
        """Enter review mode for incorrect answers. Returns True if entered successfully."""
        if not self.quiz_state.wrong_answers:
            return False
        
        # Map wrong answers back to full question data
        review_questions = []
        for wrong_answer in self.quiz_state.wrong_answers:
            question_id = wrong_answer.get('question_id')
            if question_id is not None:
                for q in self.quiz_state.original_exam_data['questions']:
                    if q.get('id') == question_id:
                        review_q = q.copy()
                        review_q['wrong_answer_info'] = wrong_answer
                        review_questions.append(review_q)
                        break
            else:
                # Fallback: find by question text
                question_text = wrong_answer['question'].strip()
                for q in self.quiz_state.original_exam_data['questions']:
                    if q['question'].strip() == question_text:
                        review_q = q.copy()
                        review_q['wrong_answer_info'] = wrong_answer
                        review_questions.append(review_q)
                        break
        
        if not review_questions:
            return False
        
        # Switch to review mode
        self.quiz_state.review_questions = review_questions
        self.quiz_state.review_mode = True
        self.quiz_state.current_index = 0
        
        # Update exam data for review mode
        self.quiz_state.exam_data = {
            'title': f"{self.quiz_state.original_exam_data['title']} - Review Mode",
            'questions': review_questions
        }
        
        self.review_mode_entered.emit()
        self._display_current_question()
        return True
    
    def study_wrong_questions(self) -> bool:
        """Filter exam to only include wrong answer questions for study. Returns True if successful."""
        if not self.quiz_state.review_questions:
            return False
        
        # Get incorrect IDs
        incorrect_ids = {q.get('wrong_answer_info', {}).get('question_id') 
                        for q in self.quiz_state.review_questions}
        incorrect_ids = {id for id in incorrect_ids if id is not None}
        
        # Filter questions by ID
        filtered_questions = []
        for q in self.quiz_state.original_exam_data['questions']:
            if q.get('id') in incorrect_ids:
                filtered_questions.append(q.copy())
        
        # Fallback if no IDs
        if not filtered_questions:
            for review_q in self.quiz_state.review_questions:
                question_text = review_q.get('question', '').strip()
                for orig_q in self.quiz_state.original_exam_data['questions']:
                    if orig_q.get('question', '').strip() == question_text:
                        filtered_questions.append(orig_q.copy())
                        break
        
        filtered_exam = {
            'title': f"{self.quiz_state.original_exam_data['title']} - Study Wrong Answers",
            'questions': filtered_questions
        }
        
        # Reset state for new quiz
        self.quiz_state.exam_data = filtered_exam
        self.quiz_state.review_mode = False
        self.quiz_state.current_index = 0
        self.quiz_state.score = 0
        self.quiz_state.answered_questions = set()
        self.quiz_state.wrong_answers = []
        self.quiz_state.answer_revealed = False
        self._reset_question_state()
        
        self.study_mode_entered.emit(filtered_exam)
        self._display_current_question()
        return True
    
    def _display_current_question(self):
        """Display the current question."""
        question = self.get_current_question()
        if not question:
            return
        
        total = self.quiz_state.get_total_questions()
        current = self.quiz_state.current_index
        
        # Update question type
        self.current_question_type = question.get('type', 'singleChoice')
        
        # Update navigation state
        can_prev = current > 0
        can_next = current < total - 1
        self.navigation_state_changed.emit(can_prev, can_next)
        
        # Update progress
        self.progress_changed.emit(current + 1, total)
        
        # Update status
        self.update_status()
        
        if self.quiz_state.review_mode:
            # Review mode display
            # Check for answer_info (from show_answer_at_end) or wrong_answer_info (from regular review)
            answer_info = question.get('answer_info') or question.get('wrong_answer_info', {})
            self.review_question_ready.emit(question, answer_info)
        else:
            # Normal mode display
            self.question_changed.emit(question, current, total)
            self._reset_selection()
    
    def _reset_question_state(self):
        """Reset state for a new question."""
        self.selected_options = []
        self.quiz_state.answer_revealed = False
    
    def _reset_selection(self):
        """Reset selection indicator."""
        self.selected_options = []
        self.option_selected.emit("", False)
    
    def update_status(self):
        """Update status bar text."""
        if self.quiz_state.review_mode:
            status = f"Review Mode: {self.quiz_state.current_index + 1}/{len(self.quiz_state.review_questions)}"
        else:
            if self.quiz_state.answered_questions:
                status = f"Score: {self.quiz_state.score}/{len(self.quiz_state.answered_questions)}"
            else:
                status = "Not started"
        self.status_text_changed.emit(status)

