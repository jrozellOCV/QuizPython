# Results System

[← Back to Documentation Index](index.md)

## Overview

The Results System saves comprehensive quiz completion data, enabling review of incorrect answers and performance tracking over time.

### When Results Are Saved

Results are automatically saved when:
1. Quiz completion is detected (last question answered)
2. User navigates to the final question and clicks "Next"
3. All required questions are answered

**Code Reference:**
```389:426:src/main_window.py
    def _on_quiz_complete(self, results: dict):
        """Handle quiz completion."""
        # Stop timer and save session
        self.timer_viewmodel.stop_timer()
        self.session_viewmodel.save_session_data(auto_save=False, emergency=False, completed=True)
        
        # Save results to file
        self.results_viewmodel.save_results_to_file()
```

### Results File Format

Two files are created for each completed quiz:

1. **JSON File** (`quiz_results_YYYYMMDD_HHMMSS.json`): Machine-readable structured data
2. **TXT File** (`quiz_summary_YYYYMMDD_HHMMSS.txt`): Human-readable summary

**File Naming Convention:**
- Format: `quiz_results_YYYYMMDD_HHMMSS_microseconds.json`
- Example: `quiz_results_20241101_184132_123456.json`
- Timestamp ensures unique filenames

### Results Data Structure

See the [Data Structures Flow](data-flow.md#data-structures-flow) section for complete structure documentation.

### Results Directory

Results are stored in the `results/` directory. See [Project Structure](project-structure.md) for directory layout.

### Review Mode Integration

Results enable review functionality. See [Review Mode Data Flow](data-flow.md#review-mode-data-flow) section for details.

### Results Aggregation

The `SessionManager.find_completed_results()` method aggregates all completed quiz results. See [Session Management](session-management.md) section for API documentation.

---
