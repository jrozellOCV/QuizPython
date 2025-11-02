# Quiz Results Directory

This directory contains the results of completed quiz sessions.

## File Types

- **quiz_results_YYYYMMDD_HHMMSS.json**: Detailed results in JSON format containing:
  - Exam information (title, total questions, shuffle status)
  - Session information (completion date, time taken)
  - Performance metrics (score, accuracy, completion rate)
  - Detailed results (correct/incorrect answers, questions answered)

- **quiz_summary_YYYYMMDD_HHMMSS.txt**: Human-readable summary containing:
  - Basic exam information
  - Performance statistics
  - List of incorrect answers (if any)

## File Naming Convention

Files are automatically named with timestamps to ensure uniqueness:
- Format: `quiz_results_YYYYMMDD_HHMMSS.json` and `quiz_summary_YYYYMMDD_HHMMSS.txt`
- Example: `quiz_results_20241201_143022.json`

## Usage

Results are automatically saved when you complete a quiz. No manual action required.
