import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class SessionManager:
    """Manages study session data persistence and retrieval."""
    
    def __init__(self, data_dir: str = "data/sessions"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def save_session(self, session_data: Dict, filepath: Optional[str] = None) -> str:
        """Save a study session to disk.
        
        Args:
            session_data: Dictionary containing session data
            filepath: Optional filepath to save to (will overwrite if exists).
                     If None, generates a new timestamp-based filename.
            
        Returns:
            str: Path to the saved session file
        """
        # Use provided filepath or generate new one
        if filepath is None:
            # Generate filename from timestamp for new sessions
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_{timestamp}.json"
            filepath = os.path.join(self.data_dir, filename)
        else:
            # Ensure filepath is in the data directory
            if not os.path.dirname(filepath):
                filepath = os.path.join(self.data_dir, filepath)
        
        # Add session date if not present
        if "session_date" not in session_data:
            session_data["session_date"] = datetime.now().isoformat()
        
        # Save to file (will overwrite if exists)
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return filepath
    
    def load_session(self, filepath: str) -> Dict:
        """Load a study session from disk.
        
        Args:
            filepath: Path to the session file
            
        Returns:
            Dict: Session data
        """
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def find_study_sessions(self) -> List[Dict]:
        """Find all available study sessions.
        
        Returns:
            List[Dict]: List of session data dictionaries with '_filepath' added
        """
        sessions = []
        
        # Get all session files
        session_files = [f for f in os.listdir(self.data_dir) 
                        if f.startswith("session_") and f.endswith(".json")]
        
        # Load each session
        for filename in sorted(session_files, reverse=True):
            filepath = os.path.join(self.data_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    session_data = json.load(f)
                    # Add filepath to session data for tracking
                    session_data['_filepath'] = filepath
                    sessions.append(session_data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading session {filename}: {e}")
                continue
        
        return sessions
    
    def clear_all_sessions(self) -> int:
        """Clear all session files.
        
        Returns:
            int: Number of files deleted
        """
        deleted_count = 0
        
        # Get all session files
        session_files = [f for f in os.listdir(self.data_dir) 
                        if f.startswith("session_") and f.endswith(".json")]
        
        # Delete each session file
        for filename in session_files:
            filepath = os.path.join(self.data_dir, filename)
            try:
                os.remove(filepath)
                deleted_count += 1
            except OSError as e:
                print(f"Error deleting session {filename}: {e}")
                continue
        
        return deleted_count
    
    def find_completed_results(self, results_dir: str = "results") -> List[Dict]:
        """Find all completed quiz results from the results directory.
        
        Args:
            results_dir: Path to the results directory
            
        Returns:
            List[Dict]: List of result data dictionaries with incorrect answers
        """
        results = []
        # Get project root (2 levels up from src/utils/ directory, 3 from file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        results_path = os.path.join(project_root, results_dir)
        
        if not os.path.exists(results_path):
            return results
        
        # Get all result JSON files
        result_files = [f for f in os.listdir(results_path) 
                        if f.startswith("quiz_results_") and f.endswith(".json")]
        
        # Load each result file
        for filename in sorted(result_files, reverse=True):
            filepath = os.path.join(results_path, filename)
            try:
                with open(filepath, 'r') as f:
                    result_data = json.load(f)
                    # Only include results with incorrect answers
                    incorrect_answers = result_data.get('detailed_results', {}).get('incorrect_answers', [])
                    if incorrect_answers:
                        results.append(result_data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading result {filename}: {e}")
                continue
        
        return results
    
    def aggregate_all_incorrect_answers(self, results_dir: str = "results") -> List[Dict]:
        """Aggregate all incorrect answers from all completed results.
        
        Args:
            results_dir: Path to the results directory
            
        Returns:
            List[Dict]: Aggregated list of incorrect answers with metadata
        """
        all_incorrect = []
        results = self.find_completed_results(results_dir)
        
        for result in results:
            exam_title = result.get('exam_info', {}).get('title', 'Unknown Exam')
            completion_date = result.get('session_info', {}).get('completion_date', '')
            incorrect_answers = result.get('detailed_results', {}).get('incorrect_answers', [])
            
            for incorrect in incorrect_answers:
                # Add metadata about which exam and when
                incorrect_with_meta = incorrect.copy()
                incorrect_with_meta['exam_title'] = exam_title
                incorrect_with_meta['completion_date'] = completion_date
                all_incorrect.append(incorrect_with_meta)
        
        return all_incorrect 