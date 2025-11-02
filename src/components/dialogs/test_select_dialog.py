import sys
import json
import os
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QListWidget, QListWidgetItem, QMessageBox,
                            QCheckBox, QWidget, QTabWidget, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush

from src.components.styles import Styles

class TestSelectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_exam = None
        self.selected_session = None
        self.selected_result = None
        self.shuffle_enabled = False
        self.styles = Styles()
        self.colors = self.styles.colors
        
        self.setWindowTitle("Select Practice Test")
        self.setModal(True)
        self.setMinimumSize(600, 600)
        self.setStyleSheet(self.styles.get_application_style())
        
        self.setup_ui()
        self.load_available_tests()
        self.load_previous_sessions()
        self.load_incorrect_answers()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Title
        title_label = QLabel("Choose a Practice Test")
        title_label.setFont(QFont('Helvetica', 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text']};
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(title_label)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                background-color: {self.colors['card']};
            }}
            QTabBar::tab {{
                background-color: {self.colors['background']};
                color: {self.colors['text']};
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: 1px solid {self.colors['border']};
            }}
            QTabBar::tab:selected {{
                background-color: {self.colors['card']};
                border-bottom: none;
            }}
            QTabBar::tab:hover {{
                background-color: {self.colors['hover']};
            }}
        """)
        
        # New Test tab
        self.new_test_tab = self.create_new_test_tab()
        self.tab_widget.addTab(self.new_test_tab, "New Test")
        
        # Previous Sessions tab
        self.sessions_tab = self.create_sessions_tab()
        self.tab_widget.addTab(self.sessions_tab, "Previous Sessions")
        
        # Review Incorrect Answers tab
        self.review_tab = self.create_review_tab()
        self.tab_widget.addTab(self.review_tab, "Review Incorrect Answers")
        
        layout.addWidget(self.tab_widget)
        
        # Button container
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet(self.styles.styles['button_secondary'])
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        
        # Start/Review button
        self.start_button = QPushButton("Start Test")
        self.start_button.setStyleSheet(self.styles.styles['button'])
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.accept)
        button_layout.addWidget(self.start_button)
        
        layout.addLayout(button_layout)
    
    def create_new_test_tab(self):
        """Create the new test tab content"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Description
        desc_label = QLabel("Select from the available practice tests below:")
        desc_label.setFont(QFont('Helvetica', 12))
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text_light']};
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(desc_label)
        
        # Test list
        self.test_list = QListWidget()
        self.test_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.colors['background']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                padding: 8px;
            }}
            QListWidget::item {{
                background-color: {self.colors['card']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 12px;
                margin: 4px;
            }}
            QListWidget::item:hover {{
                background-color: {self.colors['hover']};
            }}
            QListWidget::item:selected {{
                background-color: {self.colors['primary']};
                color: white;
            }}
        """)
        self.test_list.itemClicked.connect(self.on_test_selected)
        layout.addWidget(self.test_list)
        
        # Shuffle option
        shuffle_container = QWidget()
        shuffle_layout = QHBoxLayout(shuffle_container)
        shuffle_layout.setContentsMargins(0, 0, 0, 0)
        
        self.shuffle_checkbox = QCheckBox("Shuffle questions")
        self.shuffle_checkbox.setFont(QFont('Helvetica', 12))
        self.shuffle_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {self.colors['text']};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {self.colors['border']};
                border-radius: 4px;
                background-color: {self.colors['card']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.colors['primary']};
                border-color: {self.colors['primary']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {self.colors['primary']};
            }}
        """)
        self.shuffle_checkbox.stateChanged.connect(self.on_shuffle_toggled)
        shuffle_layout.addWidget(self.shuffle_checkbox)
        shuffle_layout.addStretch()
        
        layout.addWidget(shuffle_container)
        layout.addStretch()
        
        return tab
    
    def create_sessions_tab(self):
        """Create the previous sessions tab content"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Description
        desc_label = QLabel("Resume a previous study session:")
        desc_label.setFont(QFont('Helvetica', 12))
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text_light']};
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(desc_label)
        
        # Sessions list
        self.sessions_list = QListWidget()
        self.sessions_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.sessions_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.colors['background']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                padding: 8px;
            }}
            QListWidget::item {{
                background-color: {self.colors['card']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 12px;
                margin: 4px;
            }}
            QListWidget::item:hover {{
                background-color: {self.colors['hover']};
            }}
            QListWidget::item:selected {{
                background-color: {self.colors['primary']};
                color: white;
            }}
        """)
        self.sessions_list.itemClicked.connect(self.on_session_selected)
        layout.addWidget(self.sessions_list, stretch=1)
        
        # Clear sessions button
        clear_button = QPushButton("Clear Previous Sessions")
        clear_button.setStyleSheet(self.styles.styles['button_warning'])
        clear_button.clicked.connect(self.clear_all_sessions)
        layout.addWidget(clear_button)
        
        return tab
    
    def create_review_tab(self):
        """Create the review incorrect answers tab content"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Description
        desc_label = QLabel("Review incorrect answers from all completed tests:")
        desc_label.setFont(QFont('Helvetica', 12))
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text_light']};
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(desc_label)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.results_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.colors['background']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                padding: 8px;
            }}
            QListWidget::item {{
                background-color: {self.colors['card']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 12px;
                margin: 4px;
            }}
            QListWidget::item:hover {{
                background-color: {self.colors['hover']};
            }}
            QListWidget::item:selected {{
                background-color: {self.colors['primary']};
                color: white;
            }}
        """)
        self.results_list.itemClicked.connect(self.on_result_selected)
        layout.addWidget(self.results_list, stretch=1)
        
        return tab
    
    def load_available_tests(self):
        """Load all available exam files from the exams directory"""
        exam_files = []
        
        # Look for JSON files in the exams directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        exams_dir = os.path.join(project_root, 'exams')
        
        # Check if exams directory exists
        if not os.path.exists(exams_dir):
            item = QListWidgetItem("Exams folder not found")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.test_list.addItem(item)
            return
        
        try:
            for filename in os.listdir(exams_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(exams_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                            if 'title' in data and 'questions' in data:
                                exam_files.append({
                                    'filename': filename,
                                    'filepath': filepath,
                                    'title': data['title'],
                                    'question_count': len(data['questions'])
                                })
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
        except Exception as e:
            print(f"Error reading exams directory: {e}")
            item = QListWidgetItem("Error reading exams folder")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.test_list.addItem(item)
            return
        
        # Add tests to list widget
        for exam in exam_files:
            item = QListWidgetItem()
            item.setText(f"{exam['title']}\n{exam['question_count']} questions")
            item.setData(Qt.ItemDataRole.UserRole, exam)
            self.test_list.addItem(item)
        
        if not exam_files:
            # Show message if no tests found
            item = QListWidgetItem("No practice tests found in exams folder")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.test_list.addItem(item)
    
    def load_previous_sessions(self):
        """Load previous study sessions"""
        try:
            from src.utils.session_manager import SessionManager
            session_manager = SessionManager()
            sessions = session_manager.find_study_sessions()
            
            if not sessions:
                # Show message if no sessions found
                item = QListWidgetItem("No previous sessions found")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                self.sessions_list.addItem(item)
                return
            
            # Check for crashed sessions (incomplete sessions)
            crashed_sessions = []
            completed_sessions = []
            
            for session in sessions:
                timer_data = session.get('timer_data', {})
                if timer_data.get('completed', True) == False:
                    crashed_sessions.append(session)
                else:
                    completed_sessions.append(session)
            
            # Add crashed sessions first (most recent)
            if crashed_sessions:
                crashed_item = QListWidgetItem("⚠️ INCOMPLETE SESSIONS (May have crashed)")
                crashed_item.setFlags(Qt.ItemFlag.NoItemFlags)
                bold_font = QFont()
                bold_font.setBold(True)
                crashed_item.setFont(bold_font)
                crashed_item.setForeground(QBrush(QColor("#dc2626")))
                self.sessions_list.addItem(crashed_item)
                
                for session in crashed_sessions:
                    self.add_session_item(session, is_crashed=True)
            
            # Add completed sessions
            if completed_sessions:
                if crashed_sessions:
                    completed_item = QListWidgetItem("✅ COMPLETED SESSIONS")
                    completed_item.setFlags(Qt.ItemFlag.NoItemFlags)
                    bold_font = QFont()
                    bold_font.setBold(True)
                    completed_item.setFont(bold_font)
                    completed_item.setForeground(QBrush(QColor("#059669")))
                    self.sessions_list.addItem(completed_item)
                
                for session in completed_sessions:
                    self.add_session_item(session, is_crashed=False)
                
        except Exception as e:
            print(f"Error loading sessions: {e}")
            item = QListWidgetItem("Error loading sessions")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.sessions_list.addItem(item)
    
    def load_incorrect_answers(self):
        """Load incorrect answers from all result files"""
        try:
            from src.utils.session_manager import SessionManager
            session_manager = SessionManager()
            results = session_manager.find_completed_results()
            
            if not results:
                item = QListWidgetItem("No completed tests with incorrect answers found")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                self.results_list.addItem(item)
                return
            
            # Group by exam title
            exams_dict = {}
            for result in results:
                exam_title = result.get('exam_info', {}).get('title', 'Unknown Exam')
                if exam_title not in exams_dict:
                    exams_dict[exam_title] = []
                exams_dict[exam_title].append(result)
            
            # Add results grouped by exam
            for exam_title, exam_results in exams_dict.items():
                # Add header for exam
                header_item = QListWidgetItem(f"📚 {exam_title}")
                header_item.setFlags(Qt.ItemFlag.NoItemFlags)
                bold_font = QFont()
                bold_font.setBold(True)
                header_item.setFont(bold_font)
                header_item.setForeground(QBrush(QColor(self.colors.get('primary', '#3b82f6'))))
                self.results_list.addItem(header_item)
                
                # Add each result session
                for result in exam_results:
                    self.add_result_item(result)
                
        except Exception as e:
            print(f"Error loading incorrect answers: {e}")
            item = QListWidgetItem("Error loading results")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.results_list.addItem(item)
    
    def add_result_item(self, result):
        """Add a result item to the list"""
        item = QListWidgetItem()
        
        # Format completion date
        completion_date = result.get('session_info', {}).get('completion_date', '')
        if completion_date:
            try:
                date_obj = datetime.fromisoformat(completion_date.replace('Z', '+00:00'))
                date_str = date_obj.strftime("%B %d, %Y at %I:%M %p")
            except:
                date_str = completion_date
        else:
            date_str = "Unknown date"
        
        # Get performance metrics
        performance = result.get('performance', {})
        score = performance.get('score', 0)
        total_answered = performance.get('total_answered', 0)
        incorrect_count = performance.get('incorrect_count', 0)
        accuracy = performance.get('accuracy_percentage', 0)
        
        # Create display text
        display_text = f"{date_str}\n"
        display_text += f"Score: {score}/{total_answered} ({accuracy:.1f}%)\n"
        display_text += f"Incorrect Answers: {incorrect_count}"
        
        item.setText(display_text)
        item.setData(Qt.ItemDataRole.UserRole, result)
        
        self.results_list.addItem(item)
    
    def on_result_selected(self, item):
        """Handle result selection"""
        if item.data(Qt.ItemDataRole.UserRole):
            self.selected_result = item.data(Qt.ItemDataRole.UserRole)
            self.selected_exam = None  # Clear exam selection
            self.selected_session = None  # Clear session selection
            self.start_button.setEnabled(True)
            self.start_button.setText("Review Answers")
    
    def add_session_item(self, session, is_crashed=False):
        """Add a session item to the list"""
        item = QListWidgetItem()
        
        # Format session date
        session_date = datetime.fromisoformat(session['session_date'].replace('Z', '+00:00'))
        date_str = session_date.strftime("%B %d, %Y at %I:%M %p")
        
        # Create display text
        score = session.get('quiz_mode', {}).get('score', 0)
        total_answered = session.get('quiz_mode', {}).get('total_answered', 0)
        progress_text = f"Score: {score}/{total_answered}" if total_answered > 0 else "Not started"
        
        # Add timer info if available
        timer_info = ""
        if 'timer_data' in session:
            elapsed_seconds = session['timer_data'].get('elapsed_seconds', 0)
            hours = elapsed_seconds // 3600
            minutes = (elapsed_seconds % 3600) // 60
            seconds = elapsed_seconds % 60
            timer_info = f"Time: {hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            timer_info = "Time: Not tracked"
        
        # Add crash indicator
        crash_indicator = "🔄 CRASHED - Resume?" if is_crashed else ""
        
        display_text = f"{session['exam_title']}\n{date_str}\n{progress_text}\n{timer_info}"
        if crash_indicator:
            display_text = f"{crash_indicator}\n{display_text}"
        
        item.setText(display_text)
        item.setData(Qt.ItemDataRole.UserRole, session)
        
        # Style crashed sessions differently
        if is_crashed:
            # Note: QListWidgetItem doesn't have setStyleSheet, styling is handled by QListWidget
            pass
        
        self.sessions_list.addItem(item)
    
    def on_test_selected(self, item):
        """Handle test selection"""
        if item.data(Qt.ItemDataRole.UserRole):
            self.selected_exam = item.data(Qt.ItemDataRole.UserRole)
            self.selected_session = None  # Clear session selection
            self.selected_result = None  # Clear result selection
            self.start_button.setEnabled(True)
            self.start_button.setText("Start Test")
    
    def on_session_selected(self, item):
        """Handle session selection"""
        if item.data(Qt.ItemDataRole.UserRole):
            self.selected_session = item.data(Qt.ItemDataRole.UserRole)
            self.selected_exam = None  # Clear exam selection
            self.selected_result = None  # Clear result selection
            self.start_button.setEnabled(True)
            self.start_button.setText("Resume Session")
    
    def on_shuffle_toggled(self, state):
        """Handle shuffle checkbox toggle"""
        self.shuffle_enabled = state == Qt.CheckState.Checked.value
    
    def clear_all_sessions(self):
        """Clear all previous sessions after confirmation"""
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Clear All Sessions",
            "Are you sure you want to delete all previous sessions?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from src.utils.session_manager import SessionManager
                session_manager = SessionManager()
                deleted_count = session_manager.clear_all_sessions()
                
                # Clear the list widget
                self.sessions_list.clear()
                
                # Show success message
                QMessageBox.information(
                    self,
                    "Sessions Cleared",
                    f"Successfully deleted {deleted_count} session file(s)."
                )
                
                # Reload sessions (will show empty message)
                self.load_previous_sessions()
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to clear sessions: {str(e)}"
                )
    
    def get_selected_exam(self):
        """Return the selected exam data"""
        return self.selected_exam
    
    def get_selected_session(self):
        """Return the selected session data"""
        return self.selected_session
    
    def get_selected_result(self):
        """Return the selected result data"""
        return self.selected_result
    
    def is_shuffle_enabled(self):
        """Return whether shuffle is enabled"""
        return self.shuffle_enabled
