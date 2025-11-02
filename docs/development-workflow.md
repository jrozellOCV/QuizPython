# Development Workflow

[← Back to Documentation Index](index.md)

## Running the Application

```bash
source venv/bin/activate
python main.py
```

### Code Organization

Follows MVVM:
- **Models** (`src/models/`): State management
- **ViewModels** (`src/viewmodels/`): Business logic  
- **Views** (`src/main_window.py`, `src/components/`): UI

### Adding Features

1. Identify layer (Model/ViewModel/View)
2. Add to appropriate file
3. Connect signals
4. Test thoroughly

### Extending Application

**New Widget Example:**
1. Create in `src/components/widgets/`
2. Inherit from `QWidget`
3. Add signals for interactions
4. Integrate in `MockExamApp._setup_window()`
5. Connect signals in `_connect_signals()`

---
