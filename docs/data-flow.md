# Data Flow

[← Back to Documentation Index](index.md)

## Overview

Data flows through the application in a unidirectional pattern: **User Actions → ViewModels → State → Signals → UI Updates**. This section documents detailed data flows for all major operations.

### Application Initialization Flow

**Startup Sequence:**

```
main.py
  └─> QApplication created
      └─> TestSelectDialog shown
          └─> User selects exam/session/result
              └─> MockExamApp created with exam_data
                  ├─> Styles initialized
                  ├─> QuizState created
                  │   ├─> Exam data loaded
                  │   ├─> Questions shuffled (if enabled)
                  │   ├─> Show answers at end mode set (if enabled)
                  │   └─> Session data restored (if resuming)
                  ├─> ViewModels instantiated
                  │   ├─> TimerViewModel
                  │   ├─> QuizViewModel
                  │   ├─> SessionViewModel
                  │   └─> ResultsViewModel
                  ├─> UI widgets created
                  │   ├─> HeaderWidget
                  │   ├─> QuestionDisplayWidget
                  │   ├─> OptionButtonsWidget
                  │   ├─> NavigationFooterWidget
                  │   └─> StatusBarWidget
                  ├─> Signals connected
                  ├─> Shortcuts configured
                  ├─> Crash protection enabled
                  └─> First question displayed
```

**Code Reference:**
```520:615:src/main_window.py
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
            
            window = MockExamApp(exam_data, shuffle_enabled=False, exam_file_path=exam_file_path)
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
            
            window = MockExamApp(exam_data, shuffle_enabled, exam_file_path=exam_file_path)
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
                window = MockExamApp(exam_data, shuffle_enabled, selected_session, exam_file_path=exam_file)
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
```

### User Interaction Data Flow

#### Option Selection Flow

```
User clicks option button
  └─> OptionButtonsWidget.option_clicked signal emitted
      └─> MockExamApp._on_option_clicked() handler
          └─> Updates action button: "Confirm Answer" enabled
              └─> OptionButtonsWidget.option_selected signal emitted
                  └─> MockExamApp._on_option_selected() handler
                      └─> QuizViewModel.select_option(option_index, is_checked)
                          ├─> Updates selected_options list
                          └─> Emits option_selected signal
                              └─> QuestionDisplayWidget.set_selection()
                                  └─> Shows selection indicator
```

**Code Reference:**
```279:286:src/main_window.py
    def _on_option_clicked(self, option_index: int):
        """Handle option click (for single choice)."""
        self.nav_footer.set_action_button_text("Confirm Answer", enabled=True, is_secondary=False)
```

```32:52:src/viewmodels/quiz_viewmodel.py
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
```

#### Answer Validation Flow

```
User confirms answer (button click or Space)
  └─> QuizViewModel.validate_answer() called
      ├─> Retrieves current question from QuizState.get_current_question()
      ├─> Compares selected_options with question['answer']
      ├─> Determines if correct or incorrect
      └─> Updates QuizState:
          ├─> If show_answer_at_end is False:
          │   └─> answer_revealed = True (emits signal)
          ├─> If correct:
          │   └─> score += 1 (emits score_changed signal)
          └─> If incorrect:
              └─> wrong_answers.append(wrong_answer_dict) (emits signal)
          └─> answered_questions.add(current_index) (emits signal)
      └─> If show_answer_at_end is False:
          └─> Emits answer_validated(is_correct, feedback_text, style_class)
              └─> MockExamApp._on_answer_validated() handler
                  ├─> QuestionDisplayWidget.set_answer_feedback()
                  ├─> OptionButtonsWidget.set_enabled(False)
                  └─> NavigationFooterWidget: "Next →" button enabled
      └─> If show_answer_at_end is True:
          └─> answer_revealed = True (for navigation), but no feedback shown
      └─> Auto-save triggered (if 30 seconds elapsed)
```

**Code Reference:**
```54:129:src/viewmodels/quiz_viewmodel.py
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
        
        # Update state
        self.quiz_state.answer_revealed = True
        
        if is_correct:
            self.quiz_state.score += 1
            if question_type == "multiChoice":
                feedback = f"✓ Correct! Your answers {', '.join(self.selected_options)} were right."
            else:
                feedback = f"✓ Correct! Your answer {self.selected_options[0]} was right."
            style_class = "correct"
        else:
            # Store wrong answer
            if question_type == "multiChoice":
                your_texts = [question['options'][opt] for opt in self.selected_options]
                correct_list = correct if isinstance(correct, list) else [correct]
                correct_texts = [question['options'][opt] for opt in correct_list]
                your_answer_value = "; ".join(your_texts)
                correct_answer_value = "; ".join(correct_texts)
            else:
                your_answer_value = question['options'].get(self.selected_options[0], "")
                correct_answer_value = question['options'].get(correct, "")
            
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
        
        self.answer_validated.emit(is_correct, feedback, style_class)
        self.update_status()
        return True
```

#### Navigation Flow (Next/Previous)

```
User clicks Next/Previous button
  └─> NavigationFooterWidget.prev_clicked/next_clicked signal
      └─> QuizViewModel.next_question() or previous_question()
          ├─> Validates answer_revealed state
          ├─> If next and last question:
          │   └─> QuizViewModel._complete_quiz()
          │       └─> Emits quiz_complete signal
          └─> Otherwise:
              ├─> Updates QuizState.current_index (emits signal)
              ├─> Calls _display_current_question()
              │   ├─> Gets question from QuizState.get_current_question()
              │   ├─> Emits question_changed signal
              │   ├─> Emits progress_changed signal
              │   └─> Emits navigation_state_changed signal
              └─> UI widgets update:
                  ├─> QuestionDisplayWidget.set_question()
                  ├─> OptionButtonsWidget.create_options()
                  ├─> NavigationFooterWidget.update_progress()
                  └─> StatusBarWidget.update_status()
```

**Code Reference:**
```131:153:src/viewmodels/quiz_viewmodel.py
    def next_question(self) -> bool:
        """Move to next question. Returns True if moved, False if quiz complete or validation needed."""
        if self.quiz_state.review_mode:
            return self._next_review_question()
        
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
```

### Session Management Data Flow

#### Auto-Save Flow (Every 30 Seconds)

```
QTimer timeout (30 seconds)
  └─> SessionViewModel.auto_save_session()
      └─> SessionViewModel.save_session_data(auto_save=True)
          ├─> Collects data from QuizState:
          │   ├─> score
          │   ├─> answered_questions count
          │   ├─> wrong_answers list
          │   └─> current_index (implied by answered count)
          ├─> Gets elapsed time from TimerViewModel.get_total_elapsed_time()
          ├─> Creates session_data dictionary
          └─> SessionManager.save_session(session_data, filepath)
              ├─> Uses existing filepath (if resuming) or creates new
              ├─> Adds session_date if missing
              └─> Writes JSON to data/sessions/session_TIMESTAMP.json
          └─> Emits session_saved signal
```

**Code Reference:**
```47:52:src/viewmodels/session_viewmodel.py
    def auto_save_session(self):
        """Auto-save session data periodically"""
        try:
            self.save_session_data(auto_save=True)
        except Exception as e:
            print(f"Auto-save error: {e}")
```

```74:134:src/viewmodels/session_viewmodel.py
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
```

#### Emergency Save Flow (On Close/Crash)

```
Window close event or SIGINT/SIGTERM
  └─> _custom_close_event() or signal_handler()
      └─> SessionViewModel.emergency_save()
          ├─> Stops timer (if running)
          ├─> Collects final state from QuizState and TimerViewModel
          └─> Calls save_session_data(emergency=True)
              └─> SessionManager.save_session() writes final state
```

**Code Reference:**
```54:72:src/viewmodels/session_viewmodel.py
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
```

#### Session Resume Flow

```
User selects previous session
  └─> TestSelectDialog loads session file
      └─> SessionManager.load_session(filepath)
          └─> Returns session_data dictionary
              └─> MockExamApp created with session_data
                  └─> QuizState.__init__(exam_data, shuffle, session_data)
                      ├─> Restores score from session_data['quiz_mode']['score']
                      ├─> Restores answered count
                      ├─> Restores wrong_answers list
                      ├─> Sets current_index to total_answered
                      └─> Restores elapsed_time from timer_data
                  └─> UI initializes with restored state
                  └─> Timer resumes from saved elapsed time
```

**Code Reference:**
```48:61:src/models/quiz_state.py
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
```

### Results Saving Data Flow

#### Quiz Completion Flow

```
Last question answered
  └─> QuizViewModel.next_question() detects quiz complete
      └─> QuizViewModel._complete_quiz()
          ├─> If show_answer_at_end is enabled:
          │   └─> QuizViewModel._reveal_all_answers()
          │       ├─> Collects all answered questions
          │       ├─> Builds answer_info for each question
          │       ├─> Enters review mode with all questions
          │       └─> Displays first question with answers visible
          └─> Emits quiz_complete signal with results dict
              └─> MockExamApp._on_quiz_complete() handler
                  ├─> Stops timer
                  ├─> Saves session (completed=True)
                  ├─> ResultsViewModel.save_results_to_file()
                  │   ├─> Calculates results
                  │   ├─> Builds comprehensive results data
                  │   ├─> Writes quiz_results_TIMESTAMP.json
                  │   └─> Writes quiz_summary_TIMESTAMP.txt
                  └─> Shows results dialog
                      ├─> If show_answer_at_end: message indicates all answers visible
                      └─> User can review incorrect answers (or all answers if show_answer_at_end)
```

**Code Reference:**
```212:228:src/viewmodels/quiz_viewmodel.py
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
```

```433:479:src/main_window.py
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
```

#### Results Calculation Flow

```
ResultsViewModel.calculate_results()
  ├─> Gets total_elapsed_time from TimerViewModel
  ├─> Gets total_questions from QuizState
  ├─> Gets answered_questions count from QuizState
  ├─> Calculates accuracy = (score / answered) * 100
  ├─> Calculates completion_rate = (answered / total) * 100
  └─> Returns results dictionary with:
      ├─> score, total_answered, total_questions
      ├─> accuracy, completion_rate
      ├─> time_taken (formatted string)
      └─> wrong_answers_count
```

**Code Reference:**
```20:38:src/viewmodels/results_viewmodel.py
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
```

### Timer Data Flow

#### Timer Start Flow

```
TimerViewModel.start_timer()
  ├─> Sets QuizState.start_time = datetime.now()
  ├─> Starts QTimer with 1000ms interval
  └─> Timer begins ticking
```

**Code Reference:**
```18:23:src/viewmodels/timer_viewmodel.py
    def start_timer(self):
        """Start the exam timer"""
        if not self.quiz_state.start_time:
            self.quiz_state.start_time = datetime.now()
            self.timer.start(1000)  # Update every second
```

#### Timer Update Flow (Every Second)

```
QTimer.timeout (every 1000ms)
  └─> TimerViewModel._update_timer()
      ├─> Calculates current_session_time = now() - start_time
      ├─> Total time = elapsed_time + current_session_time
      ├─> Updates QuizState.elapsed_time (emits timer_elapsed_changed signal)
      ├─> Formats time as "HH:MM:SS"
      └─> Emits time_updated signal
          └─> StatusBarWidget.update_status()
              └─> Updates status bar display
```

**Code Reference:**
```32:39:src/viewmodels/timer_viewmodel.py
    def _update_timer(self):
        """Update the timer display"""
        if self.quiz_state.start_time:
            current_session_time = datetime.now() - self.quiz_state.start_time
            total_time = self.quiz_state.elapsed_time + current_session_time
            self.quiz_state.elapsed_time = total_time  # This will emit signal
            self.time_updated.emit(self.format_time(total_time))
            self.time_changed.emit(total_time)
```

### Review Mode Data Flow

#### Entering Review Mode

```
Quiz complete → User clicks "Review Incorrect Answers"
  └─> QuizViewModel.enter_review_mode()
      ├─> Maps wrong_answers back to full question data using question_id
      ├─> Creates review_questions list with wrong_answer_info attached
      ├─> Updates QuizState:
      │   ├─> review_mode = True (emits signal)
      │   ├─> review_questions = [...]
      │   ├─> current_index = 0
      │   └─> exam_data = filtered to review questions only
      ├─> Emits review_mode_entered signal
      └─> UI updates:
          ├─> Window title changes
          ├─> Navigation shows "Study These Questions" button
          └─> First review question displayed
```

**Code Reference:**
```181:223:src/viewmodels/quiz_viewmodel.py
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
```

### Signal/Slot Architecture

**Signal Propagation Pattern:**

- **Unidirectional**: ViewModel → View (data flows down)
- **User Actions**: View → ViewModel → State (actions flow up)
- **State Changes**: State → ViewModel → View (reactivity flows down)

**Key Signal Chains:**

1. **Question Change Chain:**
   ```
   QuizState.current_index changed
     └─> current_index_changed signal
         └─> QuizViewModel._display_current_question()
             └─> question_changed signal
                 └─> MockExamApp._on_question_changed()
                     └─> UI widgets update
   ```

2. **Answer Validation Chain:**
   ```
   User action
     └─> QuizViewModel.validate_answer()
         └─> QuizState updates (score, wrong_answers, etc.)
             └─> Signals emitted (score_changed, wrong_answers_changed)
                 └─> answer_validated signal
                     └─> UI feedback update
   ```

3. **Timer Update Chain:**
   ```
   QTimer.timeout (every second)
     └─> TimerViewModel._update_timer()
         └─> QuizState.elapsed_time updated
             └─> time_updated signal (formatted string)
                 └─> StatusBarWidget.update_status()
                     └─> Status bar display updated
   ```

### Data Structures Flow

#### Exam Data Structure

Loaded from JSON files in `exams/` directory:

```python
exam_data = {
    "title": str,                    # Exam title
    "questions": [                    # Array of question objects
        {
            "id": int,               # Unique question ID
            "question": str,         # Question text
            "options": {             # Option dictionary
                "A": str,           # Option A text
                "B": str,           # Option B text
                "C": str,           # Option C text (optional)
                "D": str,           # Option D text (optional)
                "E": str            # Option E text (optional)
            },
            "type": str,             # "singleChoice" or "multiChoice"
            "answer": str | [str]    # Single letter or array for multi-choice
        }
    ]
}
```

#### Session Data Structure

Saved to `data/sessions/session_TIMESTAMP.json`:

```python
session_data = {
    "session_date": str,             # ISO timestamp
    "exam_title": str,               # Exam title
    "total_questions": int,          # Total questions in exam
    "quiz_mode": {
        "score": int,               # Current score
        "total_answered": int,      # Number of questions answered
        "wrong_answers": [          # List of wrong answer dicts
            {
                "question_id": int,
                "question": str,
                "your_answer": str,
                "correct_answer": str
            }
        ]
    },
    "timer_data": {
        "elapsed_seconds": int,     # Total elapsed time in seconds
        "completed": bool,          # Whether quiz was completed
        "auto_saved": bool,         # Whether this was an auto-save
        "emergency_saved": bool,    # Whether this was an emergency save
        "quit_by_user": bool        # Whether user manually quit
    }
}
```

#### Results Data Structure

Saved to `results/quiz_results_TIMESTAMP.json`:

```python
results_data = {
    "exam_info": {
        "title": str,               # Exam title
        "total_questions": int,     # Total questions
        "shuffle_enabled": bool,    # Whether shuffle was used
        "exam_file_path": str        # Path to exam file
    },
    "session_info": {
        "completion_date": str,     # ISO timestamp
        "time_taken": str,          # Formatted time string (HH:MM:SS)
        "time_taken_seconds": int   # Time in seconds
    },
    "performance": {
        "score": int,               # Correct answers
        "total_answered": int,      # Questions answered
        "accuracy_percentage": float, # Accuracy percentage
        "completion_percentage": float, # Completion percentage
        "incorrect_count": int      # Number of incorrect answers
    },
    "detailed_results": {
        "correct_answers": int,     # Number of correct answers
        "incorrect_answers": [      # List of wrong answer dicts
            {
                "question_id": int,
                "question": str,
                "your_answer": str,
                "correct_answer": str
            }
        ],
        "questions_answered": [int], # List of answered question indices
        "incorrect_question_ids": [int] # List of incorrect question IDs
    }
}
```

---
