# Project Structure

[← Back to Documentation Index](index.md)

```
QuizPython/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── question_schema.json      # Question schema definition
├── docs/                     # Documentation directory
├── README.md                 # Quick start guide
│
├── exams/                    # Exam files directory
│   ├── exam_1.json
│   ├── exam_2.json
│   └── NonProcessedExams/   # Markdown files (before conversion)
│
├── data/                     # Runtime data
│   └── sessions/             # Session save files
│       └── session_*.json
│
├── results/                   # Quiz results
│   ├── quiz_results_*.json
│   └── quiz_summary_*.txt
│
└── src/                      # Source code
    ├── main_window.py        # Main application window
    │
    ├── models/               # MVVM Model layer
    │   └── quiz_state.py     # Central state management
    │
    ├── viewmodels/           # MVVM ViewModel layer
    │   ├── quiz_viewmodel.py
    │   ├── timer_viewmodel.py
    │   ├── session_viewmodel.py
    │   └── results_viewmodel.py
    │
    ├── components/           # UI components
    │   ├── styles.py         # Theme and styling
    │   ├── widgets/         # Reusable widgets
    │   │   ├── header_widget.py
    │   │   ├── question_display.py
    │   │   ├── option_buttons.py
    │   │   ├── navigation_footer.py
    │   │   └── status_bar_widget.py
    │   └── dialogs/         # Dialog windows
    │       ├── test_select_dialog.py
    │       └── session_select_dialog.py
    │
    └── utils/               # Utility classes
        ├── data_loader.py    # Exam file loading
        ├── session_manager.py # Session persistence
        └── shortcuts.py      # Keyboard shortcuts
```

### Directory Explanations

- **`exams/`**: Quiz JSON files - automatically discovered
- **`data/sessions/`**: Session save files - auto-generated
- **`results/`**: Quiz results - JSON (structured) and TXT (readable)
- **`src/models/`**: MVVM Model - state management
- **`src/viewmodels/`**: MVVM ViewModel - business logic
- **`src/components/`**: UI components - widgets and dialogs
- **`src/utils/`**: Utilities - data loading, session management

---
