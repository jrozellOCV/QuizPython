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

- `aws_mock_exam.json` - AWS Cloud Practitioner Mock Exam (70 questions)
- `new_mockExam.json` - AWS Cloud Practitioner Practice Exam 2 (50 questions)

## Notes

- Questions can have 4 or 5 options (A, B, C, D, E)
- The application automatically detects the number of options
- Exam files are automatically loaded when the application starts
- Session data is saved separately in the `data/sessions/` folder
