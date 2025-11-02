# Exams Folder

This folder contains all practice exam files for the QuizPython application.

## Adding New Exams

To add a new practice exam:

1. Create a JSON file with the exam data
2. Place it in this `exams/` folder
3. The application will automatically detect and display it

## Exam File Format

Each exam file should be a JSON file with the following structure:

```json
{
    "title": "Your Exam Title",
    "questions": [
        {
            "id": 1,
            "question": "Your question text here?",
            "options": {
                "A": "Option A",
                "B": "Option B", 
                "C": "Option C",
                "D": "Option D"
            },
            "answer": "A"
        }
    ]
}
```

## Current Exams

### Practice Exams
- `exam_1.json` - Practice Exam 1 (50 questions)
- `exam_2.json` - Practice Exam 2 (50 questions)
- `exam_3.json` - Practice Exam 3 (50 questions)
- `exam_4.json` - Practice Exam 4 (50 questions)

### Tutorials Dojo Exams
- `tDojo_exam_1.json` - Tutorials Dojo Exam 1 (65 questions)
- `tDojo_exam_2.json` - Tutorials Dojo Exam 2 (65 questions)
- `tDojo_exam_3.json` - Tutorials Dojo Exam 3 (65 questions)
- `tDojo_exam_1_missed.json` - Tutorials Dojo Exam 1 Missed Questions (21 questions)

## Notes

- The application automatically detects the number of options
- Exam files are automatically loaded when the application starts
- Session data is saved separately in the `data/sessions/` folder
