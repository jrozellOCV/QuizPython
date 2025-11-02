import os
import json
from datetime import datetime
from typing import Dict, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from src.models.quiz_state import QuizState
from src.viewmodels.timer_viewmodel import TimerViewModel


class ResultsViewModel(QObject):
    """ViewModel for quiz results and file saving."""
    
    results_ready = pyqtSignal(dict)  # Emits results data dict
    
    def __init__(self, quiz_state: QuizState, timer_viewmodel: TimerViewModel):
        super().__init__()
        self.quiz_state = quiz_state
        self.timer_viewmodel = timer_viewmodel
    
    def calculate_results(self) -> Dict:
        """Calculate and return results data."""
        total_time = self.timer_viewmodel.get_total_elapsed_time()
        total_questions = len(self.quiz_state.exam_data['questions'])
        answered_questions = len(self.quiz_state.answered_questions)
        accuracy = (self.quiz_state.score / answered_questions * 100) if answered_questions > 0 else 0
        completion_rate = (answered_questions / total_questions * 100) if total_questions > 0 else 0
        
        return {
            'score': self.quiz_state.score,
            'total_answered': answered_questions,
            'total_questions': total_questions,
            'accuracy': accuracy,
            'completion_rate': completion_rate,
            'time_taken': self.timer_viewmodel.format_time(total_time),
            'time_taken_seconds': int(total_time.total_seconds()),
            'wrong_answers_count': len(self.quiz_state.wrong_answers),
            'wrong_answers': self.quiz_state.wrong_answers
        }
    
    def save_results_to_file(self):
        """Save detailed quiz results to a file."""
        try:
            # Create results directory if it doesn't exist
            results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'results')
            os.makedirs(results_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"quiz_results_{timestamp}.json"
            filepath = os.path.join(results_dir, filename)
            
            # Calculate statistics
            results = self.calculate_results()
            
            # Get incorrect question IDs
            incorrect_question_ids = [wa.get('question_id') for wa in self.quiz_state.wrong_answers 
                                    if wa.get('question_id') is not None]
            
            # Get exam file path (relative to project root if absolute)
            exam_file_path = self.quiz_state.exam_file_path
            if exam_file_path and os.path.isabs(exam_file_path):
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                try:
                    exam_file_path = os.path.relpath(exam_file_path, project_root)
                except:
                    pass
            
            # Prepare comprehensive results data
            results_data = {
                "exam_info": {
                    "title": self.quiz_state.exam_data['title'],
                    "total_questions": results['total_questions'],
                    "shuffle_enabled": self.quiz_state.shuffle_enabled,
                    "exam_file_path": exam_file_path
                },
                "session_info": {
                    "completion_date": datetime.now().isoformat(),
                    "time_taken": results['time_taken'],
                    "time_taken_seconds": results['time_taken_seconds']
                },
                "performance": {
                    "score": results['score'],
                    "total_answered": results['total_answered'],
                    "accuracy_percentage": round(results['accuracy'], 2),
                    "completion_percentage": round(results['completion_rate'], 2),
                    "incorrect_count": results['wrong_answers_count']
                },
                "detailed_results": {
                    "correct_answers": results['score'],
                    "incorrect_answers": results['wrong_answers'],
                    "questions_answered": list(self.quiz_state.answered_questions),
                    "incorrect_question_ids": incorrect_question_ids
                }
            }
            
            # Save to JSON file
            with open(filepath, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            print(f"Quiz results saved to: {filepath}")
            
            # Also create a human-readable text summary
            text_filename = f"quiz_summary_{timestamp}.txt"
            text_filepath = os.path.join(results_dir, text_filename)
            
            with open(text_filepath, 'w') as f:
                f.write("QUIZ RESULTS SUMMARY\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Exam: {self.quiz_state.exam_data['title']}\n")
                f.write(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Time Taken: {results['time_taken']}\n")
                f.write(f"Questions Answered: {results['total_answered']}/{results['total_questions']}\n")
                f.write(f"Score: {results['score']}/{results['total_answered']}\n")
                f.write(f"Accuracy: {results['accuracy']:.1f}%\n")
                f.write(f"Completion Rate: {results['completion_rate']:.1f}%\n\n")
                
                if self.quiz_state.wrong_answers:
                    f.write("INCORRECT ANSWERS:\n")
                    f.write("-" * 30 + "\n")
                    for i, wrong in enumerate(self.quiz_state.wrong_answers, 1):
                        f.write(f"{i}. Question: {wrong['question']}\n")
                        f.write(f"   Your Answer: {wrong['your_answer']}\n")
                        f.write(f"   Correct Answer: {wrong['correct_answer']}\n\n")
                else:
                    f.write("No incorrect answers!\n")
                
                f.write("\n" + "=" * 50 + "\n")
                f.write(f"FINAL GRADE: {results['accuracy']:.1f}%\n")
                f.write("=" * 50 + "\n")
            
            print(f"Quiz summary saved to: {text_filepath}")
            
            self.results_ready.emit(results_data)
            
        except Exception as e:
            print(f"Error saving results to file: {e}")

