# Session Management

[← Back to Documentation Index](index.md)

## Overview

The Session Manager provides automatic session persistence, allowing users to resume their quiz progress at any time. Sessions are automatically saved every 30 seconds and on application close.

### Session Lifecycle

1. **Session Creation**: When a quiz starts, a new session file is created with a timestamp-based filename
2. **Auto-Save**: Every 30 seconds, session state is automatically saved
3. **Emergency Save**: On application close or crash, final state is saved
4. **Session Resume**: Users can resume any previous session from the "Previous Sessions" tab

### Auto-Save Mechanism

**Frequency**: Every 30 seconds  
**Trigger**: `QTimer` in `SessionViewModel`  
**Data Saved**:
- Current score
- Number of questions answered
- List of wrong answers
- Elapsed time
- Current progress (implied by answered count)

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

### Crash Protection

The application implements multiple layers of crash protection:

1. **Periodic Auto-Save**: Saves every 30 seconds
2. **Emergency Save on Close**: Window close event triggers save
3. **Signal Handlers**: SIGINT and SIGTERM signals trigger emergency save
4. **Exit Handler**: `atexit` module ensures save on normal exit

**Code Reference:**
```34:45:src/viewmodels/session_viewmodel.py
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
```

### Session File Format

Sessions are saved as JSON files in the `data/sessions/` directory with the naming convention: `session_YYYYMMDD_HHMMSS.json`

**Example Session File:**
```json
{
  "session_date": "2024-11-01T20:05:08.123456",
  "exam_title": "AWS Cloud Practitioner Practice Exam",
  "total_questions": 50,
  "quiz_mode": {
    "score": 35,
    "total_answered": 42,
    "wrong_answers": [
      {
        "question_id": 5,
        "question": "What is AWS Lambda?",
        "your_answer": "A virtual machine service",
        "correct_answer": "A serverless compute service"
      }
    ]
  },
  "timer_data": {
    "elapsed_seconds": 1845,
    "completed": false,
    "auto_saved": true,
    "emergency_saved": false,
    "quit_by_user": false
  }
}
```

### Session Data Structure Fields

**Top Level:**
- `session_date`: ISO format timestamp when session was created
- `exam_title`: Title of the exam being taken
- `total_questions`: Total number of questions in the exam

**quiz_mode Object:**
- `score`: Current score (number of correct answers)
- `total_answered`: Number of questions answered so far
- `wrong_answers`: Array of wrong answer objects

**timer_data Object:**
- `elapsed_seconds`: Total elapsed time in seconds
- `completed`: Boolean indicating if quiz was completed
- `auto_saved`: Boolean indicating if this was an auto-save
- `emergency_saved`: Boolean indicating if this was an emergency save
- `quit_by_user`: Boolean indicating if user manually quit

### Resume Functionality

When resuming a session:

1. `SessionManager.load_session()` reads the JSON file
2. `QuizState.__init__()` receives `session_data` parameter
3. State is restored:
   - Score from `quiz_mode.score`
   - Answered questions reconstructed from `total_answered`
   - Wrong answers list restored
   - Current index set to `total_answered` (next unanswered question)
   - Elapsed time restored
4. UI initializes with restored state
5. Timer resumes from saved elapsed time

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

### Session Directory

Sessions are stored in `data/sessions/` directory. The directory structure:
```
data/
└── sessions/
    ├── session_20241101_200329.json
    ├── session_20241101_200508.json
    └── session_20241101_200854.json
```

### SessionManager API

**Key Methods:**

- `save_session(session_data, filepath)`: Save session to file
  - If `filepath` is `None`, generates new timestamp-based filename
  - If `filepath` provided, overwrites existing file (for resuming)
  - Returns path to saved file

- `load_session(filepath)`: Load session from file
  - Reads JSON and returns dictionary
  - Throws exception if file not found or invalid JSON

- `find_study_sessions()`: Find all available sessions
  - Scans `data/sessions/` directory
  - Returns list of session dictionaries with `_filepath` added

- `find_completed_results()`: Find all completed quiz results
  - Scans `results/` directory
  - Returns only results with incorrect answers

- `clear_all_sessions()`: Delete all session files
  - Useful for cleaning up old sessions
  - Returns count of deleted files

---
