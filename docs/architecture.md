# Architecture & Components

[← Back to Documentation Index](index.md)

## MVVM Architecture Overview

QuizPython follows the **Model-View-ViewModel (MVVM)** pattern, providing separation of concerns and data binding through PyQt6 signals.

```
┌─────────────────────────────────────────┐
│              View Layer                 │
│  (UI Widgets, Main Window, Dialogs)    │
└───────────────┬─────────────────────────┘
                │ Signals/Events
                ▼
┌─────────────────────────────────────────┐
│          ViewModel Layer                │
│  (QuizViewModel, TimerViewModel, etc.)  │
└───────────────┬─────────────────────────┘
                │ State Updates
                ▼
┌─────────────────────────────────────────┐
│           Model Layer                   │
│  (QuizState - Central State Management) │
└─────────────────────────────────────────┘
```

**Data Flow Pattern:**
- **User Actions**: View → ViewModel → Model (actions flow up)
- **State Changes**: Model → ViewModel → View (reactivity flows down via signals)
- **Business Logic**: Lives in ViewModels (not in Views or Models)

### Component Hierarchy

```
MockExamApp (QMainWindow)
├── HeaderWidget
│   ├── Dark Mode Toggle
│   ├── Pause Button
│   └── Quit Button
├── ScrollArea
│   └── Content Widget
│       ├── QuestionDisplayWidget
│       └── OptionButtonsWidget
├── NavigationFooterWidget
│   ├── Progress Bar
│   ├── Navigation Buttons
│   └── Action Button
└── StatusBarWidget
    └── Timer & Stats Display
```

### Key Classes

#### QuizState (`src/models/quiz_state.py`)

The central state model that holds all quiz-related data.

**Key Properties:**
- `exam_data`: Current exam questions
- `original_exam_data`: Original exam (before filtering)
- `shuffle_enabled`: Whether questions are shuffled
- `show_answer_at_end`: Whether answers are hidden until quiz completion
- `practice_mode`: Whether in practice mode (no timer, free navigation)
- `current_index`: Current question index
- `score`: Current score
- `wrong_answers`: List of incorrectly answered questions
- `answered_questions`: Set of answered question indices
- `answer_revealed`: Boolean for answer visibility
- `is_paused`: Pause state
- `review_mode`: Whether in review mode
- `elapsed_time`: Total elapsed time

**Signals:**
All properties emit signals on change for reactive UI updates:
- `current_index_changed(int)`
- `score_changed(int)`
- `wrong_answers_changed(list)`
- `answered_questions_changed(set)`
- `answer_revealed_changed(bool)`
- `pause_state_changed(bool)`
- `review_mode_changed(bool)`
- `timer_elapsed_changed(timedelta)`

**Key Methods:**
```python
get_current_question() -> Optional[Dict]
get_total_questions() -> int
reset()
```

#### QuizViewModel (`src/viewmodels/quiz_viewmodel.py`)

Handles quiz logic, question navigation, and answer validation.

**Key Methods:**
- `select_option(option_index, is_checked)`: Handle option selection
- `validate_answer()`: Validate selected answer and update state
- `next_question()`: Navigate to next question
- `previous_question()`: Navigate to previous question
- `enter_review_mode()`: Enter review mode for wrong answers
- `study_wrong_questions()`: Start new quiz with only wrong questions

**Signals:**
- `question_changed(dict, int, int)`: Emitted when question changes
- `answer_validated(bool, str, str)`: Emitted after validation
- `review_question_ready(dict, dict)`: Emitted in review mode
- `progress_changed(int, int)`: Progress update
- `quiz_complete(dict)`: Quiz finished

**Code Reference:**
```7:27:src/viewmodels/quiz_viewmodel.py
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
```

#### SessionViewModel (`src/viewmodels/session_viewmodel.py`)

Manages session persistence, auto-save, and crash protection.

**Key Features:**
- Auto-save every 30 seconds
- Emergency save on application close/crash
- Signal handlers for SIGINT/SIGTERM
- Session data serialization

**Key Methods:**
- `setup_crash_protection()`: Configure auto-save and signal handlers
- `save_session_data(auto_save, emergency, completed, quit_by_user)`: Save session
- `emergency_save()`: Emergency save on crash/close
- `auto_save_session()`: Periodic auto-save

**Code Reference:**
```22:32:src/viewmodels/session_viewmodel.py
    def setup_crash_protection(self):
        """Set up crash detection and auto-save mechanisms"""
        # Set up periodic auto-save
        self.auto_save_timer.start(30000)  # Auto-save every 30 seconds
        
        # Set up signal handlers for crash detection
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Register cleanup function for normal exit
        atexit.register(self.cleanup_on_exit)
```

#### TimerViewModel (`src/viewmodels/timer_viewmodel.py`)

Manages quiz timer functionality.

**Key Methods:**
- `start_timer()`: Start/resume timer
- `stop_timer()`: Pause timer
- `get_total_elapsed_time()`: Get cumulative elapsed time
- `format_time(timedelta)`: Format time as HH:MM:SS

**Code Reference:**
```18:23:src/viewmodels/timer_viewmodel.py
    def start_timer(self):
        """Start the exam timer"""
        if not self.quiz_state.start_time:
            self.quiz_state.start_time = datetime.now()
            self.timer.start(1000)  # Update every second
```

#### ResultsViewModel (`src/viewmodels/results_viewmodel.py`)

Calculates and saves quiz results.

**Key Methods:**
- `calculate_results()`: Calculate performance metrics
- `save_results_to_file()`: Save results to JSON and TXT files

**Calculated Metrics:**
- Score and accuracy percentage
- Completion rate
- Time taken
- Incorrect answer details

#### SessionManager (`src/utils/session_manager.py`)

Utility class for session file operations.

**Key Methods:**
- `save_session(session_data, filepath)`: Save session to file
- `load_session(filepath)`: Load session from file
- `find_study_sessions()`: Find all available sessions
- `find_completed_results()`: Find all completed quiz results
- `clear_all_sessions()`: Delete all session files

**Code Reference:**
```13:43:src/utils/session_manager.py
    def save_session(self, session_data: Dict, filepath: Optional[str] = None) -> str:
        """Save a study session to disk.
        
        Args:
            session_data: Dictionary containing session data
            filepath: Optional filepath to save to (will overwrite if exists).
                     If None, generates a new timestamp-based filename.
            
        Returns:
            str: Path to the saved session file
        """
        # Use provided filepath or generate new one
        if filepath is None:
            # Generate filename from timestamp for new sessions
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_{timestamp}.json"
            filepath = os.path.join(self.data_dir, filename)
        else:
            # Ensure filepath is in the data directory
            if not os.path.dirname(filepath):
                filepath = os.path.join(self.data_dir, filepath)
        
        # Add session date if not present
        if "session_date" not in session_data:
            session_data["session_date"] = datetime.now().isoformat()
        
        # Save to file (will overwrite if exists)
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return filepath
```

### UI Components

#### MockExamApp (`src/main_window.py`)

Main application window that orchestrates all components.

**Initialization Sequence:**
1. Create `QuizState` with exam data
2. Instantiate ViewModels (Timer, Quiz, Session, Results)
3. Create UI widgets
4. Connect signals and slots
5. Setup keyboard shortcuts
6. Setup crash protection
7. Display first question

**Code Reference:**
```22:30:src/main_window.py
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
        
        # Start timer for new sessions or resume for existing sessions
        if not session_data or (session_data and 'timer_data' in session_data):
            self.timer_viewmodel.start_timer()
```

#### Widgets

**HeaderWidget** (`src/components/widgets/header_widget.py`): Title, dark mode toggle, pause, quit

**QuestionDisplayWidget** (`src/components/widgets/question_display.py`): Question text and answer feedback display

**OptionButtonsWidget** (`src/components/widgets/option_buttons.py`): Radio buttons or checkboxes for options

**NavigationFooterWidget** (`src/components/widgets/navigation_footer.py`): Progress bar, navigation buttons, action button

**StatusBarWidget** (`src/components/widgets/status_bar_widget.py`): Timer, score, accuracy, question counter

### Signal/Slot System

PyQt6 signals provide reactive data binding between components.

**Key Signal Chains:**
1. User clicks option → `OptionButtonsWidget.option_clicked` → `MockExamApp._on_option_clicked()` → `QuizViewModel.select_option()`
2. Answer validated → `QuizViewModel.answer_validated` → `MockExamApp._on_answer_validated()` → UI feedback update
3. Question changes → `QuizViewModel.question_changed` → UI widgets update
4. Timer updates → `TimerViewModel.time_updated` → `StatusBarWidget` display update
5. State changes → `QuizState.*_changed` signals → ViewModels react → UI updates

**Code Reference - Signal Connections:**
```135:172:src/main_window.py
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
        
        # Timer ViewModel signals
        self.timer_viewmodel.time_updated.connect(self.status_bar_widget.update_status)
        
        # Quiz State signals
        self.quiz_state.pause_state_changed.connect(self._on_pause_state_changed)
        self.quiz_state.answer_revealed_changed.connect(self._on_answer_revealed_changed)
        self.quiz_state.review_mode_changed.connect(self._on_review_mode_changed)
        
        # Results ViewModel signals
        self.results_viewmodel.results_ready.connect(self._on_results_ready)
```

---
