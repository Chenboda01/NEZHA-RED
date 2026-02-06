# AGENTS.md - Guidelines for AI Coding Agents

## Project Overview

NEZHA-RED is a robotics + algorithms + art project featuring a robot that navigates puzzles, reads poetry, and generates MIDI music. Tech stack: Python (robotics, algorithms, MIDI generation).

---

## Build / Lint / Test Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run a single test file
pytest tests/test_puzzle.py

# Run a single test function
pytest tests/test_puzzle.py::test_lights_out_solver

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Type checking
mypy src/

# Linting
flake8 src/ tests/

# Code formatting check
black --check src/ tests/

# Auto-format code
black src/ tests/
```

---

## Code Style Guidelines

### General Principles
- Write clean, readable code with clear variable names
- Prefer explicit over implicit
- Add docstrings for all public functions and classes

### Imports
- Group imports: stdlib, third-party, local
- Sort alphabetically within groups
- Use absolute imports for project modules

```python
# Good
import random
from typing import List, Optional

import numpy as np
from midiutil import MIDIFile

from src.puzzle import PuzzleSolver
from src.robot import RobotController
```

### Naming Conventions
- `snake_case` for functions, variables, modules
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Prefix private methods/vars with underscore: `_helper()`

### Type Hints
- Use type hints for function signatures
- Use `Optional[X]` for nullable types
- Use `List[X]`, `Dict[K, V]` from typing module

```python
def solve_puzzle(grid: List[List[int]], max_moves: Optional[int] = None) -> List[str]:
    pass
```

### Error Handling
- Use specific exceptions, not bare `except:`
- Provide meaningful error messages
- Use try/except for expected errors, not control flow

```python
try:
    midi_file = MIDIFile(1)
except ImportError as e:
    raise RuntimeError("midiutil not installed") from e
```

### Documentation
- Docstrings use triple double quotes
- Include Args, Returns, Raises sections for complex functions
- Keep line length to 88 characters (Black default)

---

## Project Structure

```
NEZHA-RED/
├── src/              # Main source code
│   ├── robot/        # Robot controller
│   ├── puzzle/       # Puzzle solvers
│   ├── music/        # MIDI generation
│   └── poetry/       # Poetry generation
├── tests/            # Test files
├── assets/           # Poetry scrolls, etc.
└── demos/            # Demo scripts
```

---

## Working with Agents

When modifying code:
1. Check existing patterns in nearby files
2. Run tests before and after changes
3. Run `black` and `flake8` before finishing
4. Update type hints if changing signatures
5. Never commit secrets or API keys

---

## Notes

- This project generates MIDI files for music output
- Robot uses grid-based navigation with puzzle checkpoints
- Poetry generation should reference Nezha mythology
- Keep the "red neon TRON" aesthetic in visualizations
