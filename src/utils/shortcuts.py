from PyQt6.QtGui import QKeySequence, QAction
from PyQt6.QtCore import Qt
from typing import Callable


class ShortcutManager:
    """Manager for keyboard shortcuts."""
    
    def __init__(self, parent):
        self.parent = parent
        self.option_shortcuts = []
    
    def setup_global_shortcuts(self, 
                               show_answer_callback: Callable,
                               next_question_callback: Callable,
                               prev_question_callback: Callable,
                               dark_mode_callback: Callable,
                               pause_callback: Callable):
        """Set up global keyboard shortcuts."""
        # Show answer shortcut (Space)
        show_answer_shortcut = QAction(self.parent)
        show_answer_shortcut.setShortcut(QKeySequence(Qt.Key.Key_Space))
        show_answer_shortcut.triggered.connect(show_answer_callback)
        self.parent.addAction(show_answer_shortcut)
        
        # Next question shortcut (Right arrow)
        next_shortcut = QAction(self.parent)
        next_shortcut.setShortcut(QKeySequence(Qt.Key.Key_Right))
        next_shortcut.triggered.connect(next_question_callback)
        self.parent.addAction(next_shortcut)
        
        # Previous question shortcut (Left arrow)
        prev_shortcut = QAction(self.parent)
        prev_shortcut.setShortcut(QKeySequence(Qt.Key.Key_Left))
        prev_shortcut.triggered.connect(prev_question_callback)
        self.parent.addAction(prev_shortcut)
        
        # Dark mode toggle shortcut (Ctrl+D)
        dark_mode_shortcut = QAction(self.parent)
        dark_mode_shortcut.setShortcut(QKeySequence("Ctrl+D"))
        dark_mode_shortcut.triggered.connect(dark_mode_callback)
        self.parent.addAction(dark_mode_shortcut)
        
        # Pause toggle shortcut (Ctrl+P)
        pause_shortcut = QAction(self.parent)
        pause_shortcut.setShortcut(QKeySequence("Ctrl+P"))
        pause_shortcut.triggered.connect(pause_callback)
        self.parent.addAction(pause_shortcut)
    
    def setup_option_shortcuts(self, num_options: int, select_callback: Callable):
        """Set up keyboard shortcuts for option selection (1-9 keys)."""
        # Remove existing option shortcuts
        self.clear_option_shortcuts()
        
        # Add new shortcuts
        for i in range(num_options):
            shortcut = QAction(self.parent)
            shortcut.setShortcut(QKeySequence(str(i + 1)))
            shortcut.triggered.connect(lambda checked, idx=i: select_callback(idx))
            shortcut._is_option_shortcut = True  # Mark for removal
            self.parent.addAction(shortcut)
            self.option_shortcuts.append(shortcut)
    
    def clear_option_shortcuts(self):
        """Remove all option shortcuts."""
        for action in self.option_shortcuts:
            if action in self.parent.actions():
                self.parent.removeAction(action)
        self.option_shortcuts.clear()
        
        # Also remove any orphaned shortcuts
        for action in list(self.parent.actions()):
            if hasattr(action, '_is_option_shortcut') and action._is_option_shortcut:
                self.parent.removeAction(action)

