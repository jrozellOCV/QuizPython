# Creating New Quizzes

[← Back to Documentation Index](index.md)

## Overview

QuizPython uses JSON-formatted exam files stored in the `exams/` directory. Each exam file contains a title and an array of questions following a specific schema.

### Step-by-Step Process

#### 1. Create JSON File

Create a new file in the `exams/` directory with a `.json` extension. For example: `exams/my_custom_exam.json`

#### 2. Basic File Structure

Each exam file must have this minimum structure:

```json
{
    "title": "Your Exam Title",
    "questions": []
}
```

#### 3. Add Questions

Each question follows this structure:

```json
{
    "id": 1,
    "question": "Your question text here?",
    "options": {
        "A": "Option A text",
        "B": "Option B text",
        "C": "Option C text",
        "D": "Option D text"
    },
    "type": "singleChoice",
    "answer": "A"
}
```

**Required Fields:**
- `id`: Unique integer identifier for the question
- `question`: String containing the question text
- `options`: Object with keys A-E and string values
- `answer`: String (single choice) or array of strings (multi-choice)

**Optional Fields:**
- `type`: "singleChoice" (default) or "multiChoice"

#### 4. Complete Example

```json
{
    "title": "AWS Cloud Practitioner Practice Exam",
    "questions": [
        {
            "id": 1,
            "question": "What is AWS's pay-as-you-go pricing model?",
            "options": {
                "A": "Fixed monthly cost",
                "B": "Pay only for what you use",
                "C": "Annual subscription required",
                "D": "Free tier only"
            },
            "type": "singleChoice",
            "answer": "B"
        },
        {
            "id": 2,
            "question": "Which AWS services are compute services? (Choose TWO)",
            "options": {
                "A": "Amazon EC2",
                "B": "Amazon S3",
                "C": "AWS Lambda",
                "D": "Amazon RDS",
                "E": "Amazon VPC"
            },
            "type": "multiChoice",
            "answer": ["A", "C"]
        }
    ]
}
```

#### 5. File Placement

Place your exam file in the `exams/` directory. The application automatically discovers all `.json` files in this directory on startup.

#### 6. Validation

The exam file must conform to the schema defined in `question_schema.json`. Key validation rules:

- Minimum 2 options per question, maximum 5 options
- Option keys must be single letters: A, B, C, D, or E
- Answer must match option keys
- Multi-choice answers must be arrays with at least 1 and at most 5 items
- Each question ID must be unique within the exam

### AI-Assisted Question Generation

You can use AI tools to generate questions following this format:

**Prompt Template:**
```
Generate a multiple-choice question about [TOPIC] with:
- Format: Multiple choice with 4-5 options (A, B, C, D, E)
- Include a clear, concise question
- Provide plausible options
- Mark the correct answer
- Follow this JSON format:
{
    "id": [NEXT_ID],
    "question": "Question text?",
    "options": {
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
    },
    "type": "singleChoice",
    "answer": "CORRECT_LETTER"
}
```

### Quick Reference

- **File Location**: `exams/your_exam.json`
- **File Format**: JSON
- **Minimum Questions**: 1 (though practical exams have many more)
- **Maximum Options**: 5 (A-E)
- **Question Types**: `singleChoice` or `multiChoice`
- **ID Format**: Integer (must be unique)

See the [Question Schema](question-schema.md) section for complete schema documentation.

---
