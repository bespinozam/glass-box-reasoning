# Installation Guide

## Installing the Package

To install this package from a Kaggle notebook or any other environment, follow these steps:

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/glass-box-reasoning.git
cd glass-box-reasoning
```

### 2. Install the package

```bash
pip install -e .
```

The `-e` flag installs the package in editable mode, which is useful for development.

### 3. Verify installation

Run the test script to verify that all imports work correctly:

```bash
python3 test_imports.py
```

You should see output like:

```
======================================================================
PACKAGE STRUCTURE TEST
======================================================================
Testing folder structure...
✓ puzzles/hanoi_tower/ exists
✓ output_logging/ exists
✓ examples/hanoi_tower/ exists
✓ tests/ exists
✓ eval/ exists
✓ models/ exists
Testing core puzzle imports...
✓ Successfully imported from puzzles.hanoi_tower
✓ Successfully created HanoiState instance
✓ Successfully created AutomatedValidator instance
✓ Successfully created InteractiveSolver instance

Testing output_logging module imports...
✓ Successfully imported output_logging modules
✓ Successfully created OutputLogger instance

Testing direct module imports...
✓ Successfully imported puzzle modules directly

Testing simple validation...
✓ Validation successful! Solved in 7 moves

======================================================================
✓ ALL TESTS PASSED!
The package structure is correct and all imports work.
======================================================================
```

## Using the Package

### Quick Start with Core Puzzle

```python
from puzzles.hanoi_tower import HanoiState, AutomatedValidator, InteractiveSolver

# Create and validate a 3-disk puzzle solution
validator = AutomatedValidator(3)

moves = [
    [1, 0, 2], [2, 0, 1], [1, 2, 1],
    [3, 0, 2], [1, 1, 0], [2, 1, 2],
    [1, 0, 2]
]

result = validator.validate_solution(moves, verbose=False)
print(f"Solution valid: {result['is_solved']}")
```

### Using Output Logging

```python
from output_logging import OutputLogger, parse_hanoi_output
from puzzles.hanoi_tower import AutomatedValidator

# Log model outputs
logger = OutputLogger("my_run", "my_model", puzzle_name="hanoi")

# Parse model output
model_output = """
The solution is:
moves = [[1, 0, 2], [2, 0, 1], [1, 2, 1], [3, 0, 2], [1, 1, 0], [2, 1, 2], [1, 0, 2]]
"""

moves, error = parse_hanoi_output(model_output)
if moves:
    validator = AutomatedValidator(3)
    result = validator.validate_solution(moves)
    logger.log_iteration_with_validation(
        n_disks=3,
        raw_output=model_output,
        input_prompt="...",
        validation_result=result,
        tokens_used=100,
        parsed_output=moves
    )
```

### Using the CLI Simulator

```bash
# Interactive mode
python3 -m puzzles.hanoi_tower.hanoi_simulator --interactive

# Quick validator
python3 -m puzzles.hanoi_tower.hanoi_simulator --validate

# Show rules
python3 -m puzzles.hanoi_tower.hanoi_simulator --rules
```

### More Examples

For more advanced usage examples, see the `examples/hanoi_tower/` directory:

- `minimal_example.py` - Minimal usage example
- `example_usage.py` - Comprehensive usage examples
- `quickstart.py` - Complete model evaluation pipeline
- `example_model_evaluation.py` - Model evaluation with logging
- `parse_and_validate_example.py` - Parsing and validation examples

## Project Structure

```
glass-box-reasoning/
├── puzzles/hanoi_tower/      # Core puzzle logic
├── output_logging/           # Output logging & parsing
├── examples/hanoi_tower/     # Usage examples
├── tests/                    # Test suite
├── eval/                     # Evaluation utilities
└── models/                   # Model utilities
```

For a detailed explanation of the project structure, see [RESTRUCTURING.md](RESTRUCTURING.md).

## Changes from Previous Version

The project has been restructured for better organization:

1. **Core puzzle**: Only 4 essential files in `puzzles/hanoi_tower/`
2. **Logging utilities**: Moved to `output_logging/` folder
3. **Examples**: Moved to `examples/hanoi_tower/` folder
4. **Tests**: Moved to `tests/` folder
5. **All imports**: Use absolute imports for compatibility

### Import Changes

If you have existing code, update your imports:

```python
# Old (broken after restructuring)
from puzzles.hanoi_tower.output_logger import OutputLogger

# New (works correctly)
from output_logging.output_logger import OutputLogger
```

Core puzzle imports remain the same:
```python
from puzzles.hanoi_tower import HanoiState, AutomatedValidator, InteractiveSolver
```

## Troubleshooting

### Import Errors

If you see import errors, make sure you:
1. Installed the package with `pip install -e .`
2. Are running from the project root directory
3. Updated imports to use the new structure (see RESTRUCTURING.md)

### Testing

Run the test script to diagnose issues:
```bash
python3 test_imports.py
```

This will show exactly which imports are failing and help you identify the problem.
