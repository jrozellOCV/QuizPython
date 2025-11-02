from PyQt6.QtWidgets import QWidget, QVBoxLayout, QRadioButton, QCheckBox, QButtonGroup
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QMouseEvent
from typing import Dict, List
from src.components.styles import Styles


class ClickableRadioButton(QRadioButton):
    """Radio button with full area clickable."""
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press anywhere on the widget - ensures entire area is clickable."""
        # PyQt radio buttons already handle clicks across their entire area
        # This override ensures the behavior is explicit and consistent
        super().mousePressEvent(event)


class ClickableCheckBox(QCheckBox):
    """Checkbox with full area clickable."""
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press anywhere on the widget - ensures entire area is clickable."""
        # Call parent to handle the click properly, which will toggle the state
        super().mousePressEvent(event)


class OptionButtonsWidget(QWidget):
    """Widget for displaying option buttons (radio or checkbox)."""
    
    option_selected = pyqtSignal(int, bool)  # option_index, is_checked
    option_clicked = pyqtSignal(int)  # option_index
    
    def __init__(self, styles: Styles):
        super().__init__()
        self.styles = styles
        self.colors = styles.colors
        self.option_buttons: List[QRadioButton | QCheckBox] = []
        self.option_group = QButtonGroup()
        self.current_question_type = "singleChoice"
        self.current_styles_map: Dict[int, Dict[str, str]] = {}  # Store current review styles
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the option buttons container."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        self.option_layout = layout
    
    def create_options(self, options: Dict[str, str], question_type: str = "singleChoice"):
        """Create option buttons for the given options and question type."""
        # Clear existing buttons
        for button in self.option_buttons:
            button.deleteLater()
        self.option_buttons.clear()
        self.option_group = QButtonGroup()
        self.current_question_type = question_type
        self.current_styles_map = {}  # Clear styles when creating new options
        
        # Create buttons based on question type
        for i, (key, value) in enumerate(options.items()):
            if question_type == "multiChoice":
                option = ClickableCheckBox()
            else:
                option = ClickableRadioButton()
            
            option.setFont(QFont('Helvetica', 14))
            option.setText(f"{key}. {value}")
            option.setStyleSheet(self._get_button_style())
            
            # Make entire button clickable by enabling auto-click
            # This makes the whole widget area respond to clicks
            option.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Connect signals - use toggled for both to properly handle selection changes
            if question_type == "multiChoice":
                option.toggled.connect(lambda checked, idx=i: self._on_option_toggled(idx, checked))
            else:
                # Use toggled for radio buttons too, so we get notified when selection changes
                option.toggled.connect(lambda checked, idx=i: self._on_radio_toggled(idx, checked))
            
            self.option_layout.addWidget(option)
            self.option_buttons.append(option)
            self.option_group.addButton(option, i)
        
        # Set exclusivity
        self.option_group.setExclusive(question_type == "singleChoice")
    
    def _on_option_toggled(self, index: int, checked: bool):
        """Handle checkbox toggle."""
        self.option_selected.emit(index, checked)
    
    def _on_radio_toggled(self, index: int, checked: bool):
        """Handle radio button toggle - fires when selection changes."""
        if checked:
            self.option_clicked.emit(index)
            self.option_selected.emit(index, True)
    
    def set_option_styles(self, styles_map: Dict[int, Dict[str, str]]):
        """Set custom styles for specific options (e.g., correct/incorrect highlighting)."""
        # Store the styles map with type markers for color updates
        self.current_styles_map = {}
        for index, style_dict in styles_map.items():
            stored_style = style_dict.copy()
            # Add type marker based on color (for theme updates)
            border_color = style_dict.get('border_color', '')
            if border_color == self.colors.get('correct') or border_color == self.colors.get('success'):
                stored_style['_style_type'] = 'correct'
            elif border_color == self.colors.get('warning'):
                stored_style['_style_type'] = 'warning'
            self.current_styles_map[index] = stored_style
        
        # Apply styles
        for index, style_dict in styles_map.items():
            if 0 <= index < len(self.option_buttons):
                style_str = self._get_button_style(
                    border_color=style_dict.get('border_color'),
                    text_color=style_dict.get('text_color'),
                    border_width=style_dict.get('border_width', 1),
                    is_bold=style_dict.get('is_bold', False)
                )
                self.option_buttons[index].setStyleSheet(style_str)
    
    def _get_button_style(self, border_color: str = None, text_color: str = None, 
                         border_width: int = 1, is_bold: bool = False):
        """Get button style string."""
        border = border_color or self.colors['border']
        text = text_color or self.colors['text']
        weight = "bold" if is_bold else "normal"
        
        if self.current_question_type == "multiChoice":
            return f"""
                QCheckBox {{
                    color: {text};
                    background-color: {self.colors['card']};
                    padding: 15px;
                    border-radius: 8px;
                    border: {border_width}px solid {border};
                    font-weight: {weight};
                    min-height: 50px;
                }}
                QCheckBox:hover {{
                    background-color: {self.colors['hover']};
                }}
                QCheckBox::indicator {{
                    width: 20px;
                    height: 20px;
                    margin-right: 10px;
                }}
            """
        else:
            return f"""
                QRadioButton {{
                    color: {text};
                    background-color: {self.colors['card']};
                    padding: 15px;
                    border-radius: 8px;
                    border: {border_width}px solid {border};
                    font-weight: {weight};
                    min-height: 50px;
                }}
                QRadioButton:hover {{
                    background-color: {self.colors['hover']};
                }}
                QRadioButton::indicator {{
                    width: 20px;
                    height: 20px;
                    margin-right: 10px;
                }}
            """
    
    def reset_styles(self):
        """Reset all option buttons to default style."""
        self.current_styles_map = {}  # Clear stored styles
        for button in self.option_buttons:
            button.setStyleSheet(self._get_button_style())
    
    def set_enabled(self, enabled: bool):
        """Enable or disable all option buttons."""
        for button in self.option_buttons:
            button.setEnabled(enabled)
    
    def clear_selection(self):
        """Clear all selections."""
        for button in self.option_buttons:
            button.setChecked(False)
    
    def get_selected_indices(self) -> List[int]:
        """Get currently selected option indices from UI state."""
        selected = []
        for i, button in enumerate(self.option_buttons):
            if button.isChecked():
                selected.append(i)
        return selected
    
    def hide(self):
        """Hide the widget (override for pause functionality)."""
        super().hide()
        for button in self.option_buttons:
            button.hide()
    
    def show(self):
        """Show the widget."""
        super().show()
        for button in self.option_buttons:
            button.show()
    
    def update_colors(self, colors: dict):
        """Update colors when theme changes."""
        self.colors = colors
        
        # If we have review styles, update the color values and re-apply
        if self.current_styles_map:
            # Rebuild styles with new colors based on stored style types
            updated_styles_map = {}
            for index, style_dict in self.current_styles_map.items():
                style_type = style_dict.get('_style_type', '')
                border_width = style_dict.get('border_width', 2)
                is_bold = style_dict.get('is_bold', False)
                
                if style_type == 'correct':
                    updated_styles_map[index] = {
                        'border_color': colors['correct'],
                        'text_color': colors['correct'],
                        'border_width': border_width,
                        'is_bold': is_bold,
                        '_style_type': 'correct'  # Preserve style type
                    }
                elif style_type == 'warning':
                    updated_styles_map[index] = {
                        'border_color': colors['warning'],
                        'text_color': colors['warning'],
                        'border_width': border_width,
                        'is_bold': is_bold,
                        '_style_type': 'warning'  # Preserve style type
                    }
            
            # Apply updated styles
            for index, style_dict in updated_styles_map.items():
                if 0 <= index < len(self.option_buttons):
                    style_str = self._get_button_style(
                        border_color=style_dict.get('border_color'),
                        text_color=style_dict.get('text_color'),
                        border_width=style_dict.get('border_width', 1),
                        is_bold=style_dict.get('is_bold', False)
                    )
                    self.option_buttons[index].setStyleSheet(style_str)
            
            # Update stored map with new colors (preserving _style_type)
            self.current_styles_map = updated_styles_map
        else:
            # Otherwise, update all buttons with default colors
            for button in self.option_buttons:
                button.setStyleSheet(self._get_button_style())

