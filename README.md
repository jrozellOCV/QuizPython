# Quiz Python Application

A modern, interactive quiz application built with Python and PyQt6, designed to help users study and prepare for exams with session management, progress tracking, and comprehensive review capabilities.

## System Requirements

- Python 3.8 or higher
- PyQt6 and its dependencies
- Operating System: Windows, macOS, or Linux

## Features

### Quiz Modes & Options
- Interactive multiple-choice questions with immediate feedback
- Configurable quiz options for different study approaches
- Progress tracking with a visual progress bar
- Score tracking and performance statistics
- Session save/resume functionality - pause and resume study sessions at any time
- **Pause functionality** - Temporarily hide questions and answers while pausing the timer
- Timer functionality to track study time
- Multiple quiz modes: Shuffle questions, Practice mode, and Hide answers during quiz
- Review of incorrect answers from completed sessions
- Test selection dialog with tabs for easy navigation
- Results saving system with detailed performance metrics
- Keyboard shortcuts for navigation and answering
- Modern, clean user interface with smooth animations

### User Interface
- Modern, responsive design
- **Dark mode toggle** - Switch between light and dark themes for comfortable studying
- Intuitive navigation with tabbed test selection
- Clear visual feedback for correct/incorrect answers
- Progress indicators
- Status bar with current progress and session info

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
   - Place exam JSON files in the `exams/` folder
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
   python main.py
   ```

   Note: The application will automatically:
   - Load exam files from the `exams/` folder
   - Save study sessions to `data/sessions/` for resuming later
   - Save completed quiz results to `results/` folder

## Keyboard Shortcuts

The application supports the following keyboard shortcuts for quick navigation:

- **Space**: Show answer for current question
- **Right Arrow** (→): Move to next question
- **Left Arrow** (←): Move to previous question
- **1-9**: Select option by number (1 for first option, 2 for second, etc.)
- **Ctrl+P**: Toggle pause mode (hides questions/answers and pauses timer)
- **Ctrl+D**: Toggle dark mode

## Features in Detail

### Pause Mode

The pause feature allows you to temporarily hide questions and answers while keeping your session active. When paused:
- The question and all answer options are hidden
- The timer is paused
- Your session data remains saved
- Click the pause button (⏸) again or press **Ctrl+P** to resume

This is useful for:
- Taking a break without losing your place
- Temporarily hiding content from view
- Pausing time tracking during interruptions

### Dark Mode

Toggle between light and dark themes for comfortable studying in any lighting condition:
- Click the dark mode button (🌙/☀️) in the header
- Or use the keyboard shortcut **Ctrl+D**
- Your preference persists throughout the session

## Quiz Options

When starting a new test from the "New Test" tab, you can configure several options to customize your quiz experience:

### Shuffle Questions

**Location**: Checkbox in the "New Test" tab

**Description**: Randomizes the order of questions in the exam, providing a different question sequence each time you take the quiz.

**Use Cases**:
- Prevent memorizing question order through repetition
- Simulate varied exam conditions
- Focus on content knowledge rather than question sequence

**How It Works**:
- Questions are shuffled before the quiz starts
- Each new quiz session will have a different random order
- Resuming a session maintains the original shuffled order

### Practice Mode

**Location**: Checkbox labeled "Practice mode (no timer, free navigation)"

**Description**: A relaxed study mode without timer restrictions and with flexible navigation between questions.

**Features**:
- **No Timer**: Timer is disabled, allowing you to study at your own pace
- **Free Navigation**: Move between questions freely without requiring answer confirmation
- **Show Answer Button**: Instead of "Confirm Answer", shows "Show Answer" button for immediate feedback
- **Unlimited Navigation**: Jump between questions without restrictions
- **Question Timeline**: Visual timeline shows all questions and allows jumping to specific questions (number keys 1-9)

**Best For**:
- Initial learning and exploration
- Studying without time pressure
- Reviewing material at your own pace
- Practicing specific questions repeatedly

**Note**: Practice mode sessions can be saved and resumed like regular sessions, but scores and timers are not tracked for progress comparison.

### Hide Answers During Quiz

**Location**: Checkbox labeled "Hide answers during quiz"

**Description**: Keeps all answers hidden during the quiz and reveals them all at once after completing the entire exam.

**Features**:
- Answers are not shown immediately after selecting an option
- No immediate feedback during the quiz
- All answers are automatically revealed when you complete the quiz
- Navigate through all questions with answers visible for review

**How It Works**:
1. Select answers normally throughout the quiz
2. Answers remain hidden - no immediate feedback
3. When you complete all questions, all answers are revealed automatically
4. Navigate through questions to review your selections alongside correct answers
5. Your score is calculated based on your selections

**Best For**:
- Simulating real exam conditions where you don't get immediate feedback
- Testing your knowledge without hints
- Practicing under exam-like conditions
- Building confidence with full question sets

**Combining Options**:
- **Shuffle + Hide Answers**: Great for exam simulation - randomized questions with no feedback
- **Practice Mode + Shuffle**: Learn material in different orders without time pressure
- **Practice Mode + Hide Answers**: Study without timer but still test yourself without hints

### Option Availability

- **Shuffle Questions**: Available when starting a new test
- **Practice Mode**: Available when starting a new test
- **Hide Answers During Quiz**: Available when starting a new test
- **Note**: These options are not available when resuming a session - the original settings from when the session was created are preserved

### Troubleshooting

If you encounter any issues:

1. **PyQt6 Installation Fails**
   - Try installing the system package first (see above)
   - Ensure you have the latest pip: `pip install --upgrade pip`
   - Try installing with: `pip install PyQt6 --no-cache-dir`

2. **Application Won't Start**
   - Verify Python version: `python --version`
   - Check PyQt6 installation: `python -c "import PyQt6; print(PyQt6.__version__)"`
   - Ensure you're in the correct directory (project root)
   - Verify exam files exist in the `exams/` folder

3. **Display Issues**
   - Update your graphics drivers
   - Try running with a different Qt backend:
     ```bash
     export QT_QPA_PLATFORM=xcb  # For Linux
     # or
     export QT_QPA_PLATFORM=windows  # For Windows
     ```

## Future Improvements

Here are some small but impactful improvements that could enhance the application:

- **Keyboard Shortcut Help Menu**: A help dialog displaying all available keyboard shortcuts
- **Session Statistics Visualization**: Charts and graphs showing performance trends over time
- **Question Difficulty Tagging**: Tag questions by difficulty level to enable filtered practice
- **Cross-Session Progress Tracking**: Track improvement across multiple study sessions
- **Export Results**: Export quiz results to CSV or PDF format for external analysis
- **Question Search/Filter**: Search and filter questions by topic or keywords
- **Question Bookmarks**: Bookmark difficult questions for focused review
- **Performance Analytics Dashboard**: Visual dashboard showing overall study statistics and weak areas

## Contributing

Feel free to contribute to this project by:
- Adding new features
- Improving the UI/UX
- Creating new exam question sets
- Reporting bugs
- Suggesting improvements

## License

This project is licensed under the MIT License - see the LICENSE file for details. 