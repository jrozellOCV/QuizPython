# Quiz Python Application

A modern, interactive quiz application built with Python and PyQt6, designed to help users study and prepare for exams through both quiz and flashcard modes.

## System Requirements

- Python 3.8 or higher
- PyQt6 and its dependencies
- Operating System: Windows, macOS, or Linux

## Features

### Quiz Mode
- Interactive multiple-choice questions with immediate feedback
- Progress tracking with a visual progress bar
- Score tracking and performance statistics
- Review of incorrect answers
- Keyboard shortcuts for navigation and answering
- Modern, clean user interface with smooth animations

### Flashcard Mode
- Flip cards to reveal answers
- Mark cards as known or needing more review
- Track progress of learned cards
- Smooth card flip animations
- Easy navigation between cards

### User Interface
- Modern, responsive design
- Dark/light mode support
- Intuitive navigation
- Clear visual feedback for correct/incorrect answers
- Progress indicators
- Status bar with current mode and progress

## Question Format

The application uses a JSON format for exam questions. Here's the schema:

```json
{
    "title": "Exam Title",
    "questions": [
        {
            "id": 1,
            "question": "Question text here?",
            "options": {
                "A": "Option A text",
                "B": "Option B text",
                "C": "Option C text",
                "D": "Option D text"
            },
            "answer": "A"  // The correct option letter
        }
    ]
}
```

## Using AI to Generate Exam Questions

You can use AI to generate new exam questions following these steps:

1. **Prepare a Topic Outline**
   - Create a list of key topics and concepts to cover
   - Define the difficulty level for each topic
   - Specify the number of questions needed per topic

2. **AI Prompt Template**
   Use this template to generate questions with AI:

   ```
   Generate a multiple-choice question about [TOPIC] with the following requirements:
   - Difficulty: [BEGINNER/INTERMEDIATE/ADVANCED]
   - Format: Multiple choice with 4 options (A, B, C, D)
   - Include a clear, concise question
   - Provide 4 plausible options
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
       "answer": "CORRECT_LETTER"
   }
   ```

3. **Quality Control**
   - Review generated questions for accuracy
   - Ensure questions are clear and unambiguous
   - Verify that all options are plausible
   - Check that the correct answer is properly marked
   - Validate the JSON format

4. **Adding to the Application**
   - Add new questions to your exam JSON file
   - Maintain unique IDs for each question
   - Keep the JSON structure consistent
   - Test the questions in the application

## Example AI-Generated Question

Here's an example of how to use AI to generate a question about AWS services:

```
Generate a multiple-choice question about AWS Lambda with the following requirements:
- Difficulty: INTERMEDIATE
- Format: Multiple choice with 4 options
- Topic: Serverless computing and AWS Lambda
```

Expected AI response:
```json
{
    "id": 71,
    "question": "Which of the following is a key characteristic of AWS Lambda?",
    "options": {
        "A": "Requires manual server provisioning",
        "B": "Charges only for compute time used",
        "C": "Supports only Java and Python",
        "D": "Requires a minimum runtime of 1 hour"
    },
    "answer": "B"
}
```

## Getting Started

### Prerequisites

1. Ensure you have Python 3.8 or higher installed:
   ```bash
   python --version
   ```

2. (Optional) Create a virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/quiz-python.git
   cd quiz-python
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Note: If you encounter any issues installing PyQt6, you may need to install additional system dependencies:
   - On Ubuntu/Debian:
     ```bash
     sudo apt-get install python3-pyqt6
     ```
   - On macOS (using Homebrew):
     ```bash
     brew install pyqt@6
     ```
   - On Windows:
     The PyQt6 wheel should install automatically via pip.

3. Run the application:
   ```bash
   python src/main.py
   ```

### Troubleshooting

If you encounter any issues:

1. **PyQt6 Installation Fails**
   - Try installing the system package first (see above)
   - Ensure you have the latest pip: `pip install --upgrade pip`
   - Try installing with: `pip install PyQt6 --no-cache-dir`

2. **Application Won't Start**
   - Verify Python version: `python --version`
   - Check PyQt6 installation: `python -c "import PyQt6; print(PyQt6.__version__)"`
   - Ensure you're in the correct directory
   - Check the exam data file exists: `aws_mock_exam.json`

3. **Display Issues**
   - Update your graphics drivers
   - Try running with a different Qt backend:
     ```bash
     export QT_QPA_PLATFORM=xcb  # For Linux
     # or
     export QT_QPA_PLATFORM=windows  # For Windows
     ```

## Contributing

Feel free to contribute to this project by:
- Adding new features
- Improving the UI/UX
- Creating new exam question sets
- Reporting bugs
- Suggesting improvements

## License

This project is licensed under the MIT License - see the LICENSE file for details. 