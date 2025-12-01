# Tower of Hanoi - Model Evaluation Utilities

This directory contains utilities for evaluating reasoning models on the Tower of Hanoi puzzle.

## Overview

The evaluation pipeline consists of four main components:

1. **Output Parser** - Robustly parses model outputs to extract moves
2. **Validator** - Validates moves and checks puzzle solutions
3. **Output Logger** - Saves results to JSONL files
4. **Results Analyzer** - Analyzes and compares results across runs

## Quick Start

```python
from output_logger import OutputLogger
from output_parser import parse_hanoi_output
from automated_validator import AutomatedValidator

# Your model's output
model_output = """
Solution:
moves=[[1,0,2],[2,0,1],[1,2,1],[3,0,2],[1,1,0],[2,1,2],[1,0,2]]
"""

# Parse
moves, error = parse_hanoi_output(model_output)

# Validate
validator = AutomatedValidator(n_disks=3)
result = validator.validate_solution(moves, verbose=False)

# Log
logger = OutputLogger(run_id="my_run", model_name="my_model")
logger.log_iteration_with_validation(
    n_disks=3,
    raw_output=model_output,
    input_prompt="Solve the 3-disk Tower of Hanoi",
    validation_result=result,
    tokens_used=150,
    parsed_output=moves,
    parse_error=error
)

print(f"Valid: {result['is_valid']}, Solved: {result['is_solved']}")
```

See `quickstart.py` for a complete example.

## File Structure

```
outputs/
└── {run_id}/
    └── {model_name}/
        ├── output_hanoi_n3.jsonl
        ├── output_hanoi_n4.jsonl
        └── output_hanoi_n5.jsonl
```

## JSONL Format

Each line in the JSONL file contains:

```json
{
  "raw_output": "The model's raw output text",
  "input_prompt": "The prompt sent to the model",
  "tokens_used": 150,
  "parsed_output": [[1,0,2], [2,0,1], [1,2,1]],
  "is_correct": true,
  "failure_reason": null,
  "timestamp": "2024-11-27T12:00:00.000000",
  "n_disks": 3,
  "metadata": {
    "validation": {
      "is_valid": true,
      "is_solved": true,
      "total_moves": 7,
      "optimal_moves": 7,
      "efficiency": 1.0,
      "failed_at": null
    }
  }
}
```

## Core Modules

### 1. output_parser.py

Parses model outputs to extract moves. Handles:
- Line breaks and whitespace variations
- Multiple `moves=` patterns (takes the last one)
- Missing labels (lenient mode)

**Functions:**
- `parse_hanoi_output(text)` - Standard parser (requires `moves=` label)
- `parse_hanoi_output_lenient(text)` - Lenient parser (no label required)
- `validate_and_parse(text, n_disks)` - Parse with basic validation

**Example:**
```python
from output_parser import parse_hanoi_output

text = "moves=[[1,0,2],[2,0,1]]"
moves, error = parse_hanoi_output(text)
```

### 2. automated_validator.py

Validates move sequences for correctness.

**Functions:**
- `AutomatedValidator(n_disks)` - Create validator
- `validate_solution(moves, verbose)` - Validate a sequence

**Example:**
```python
from automated_validator import AutomatedValidator

validator = AutomatedValidator(n_disks=3)
result = validator.validate_solution(moves, verbose=True)

print(f"Valid: {result['is_valid']}")
print(f"Solved: {result['is_solved']}")
print(f"Efficiency: {result['efficiency']:.1%}")
```

### 3. output_logger.py

Logs evaluation results to JSONL files.

**Functions:**
- `OutputLogger(run_id, model_name)` - Create logger
- `log_iteration(...)` - Log a single iteration
- `log_iteration_with_validation(...)` - Log with automatic validation processing
- `read_iterations(n_disks)` - Read all logged iterations
- `get_summary_stats(n_disks)` - Get summary statistics

**Example:**
```python
from output_logger import OutputLogger

logger = OutputLogger(run_id="exp_001", model_name="gpt4")

logger.log_iteration_with_validation(
    n_disks=3,
    raw_output=model_output,
    input_prompt=prompt,
    validation_result=result,
    tokens_used=150,
    parsed_output=moves,
    parse_error=None
)

# Get statistics
stats = logger.get_summary_stats(n_disks=3)
print(f"Success rate: {stats['success_rate']:.1%}")
```

### 4. results_analyzer.py

Analyzes and compares results across runs and models.

**Functions:**
- `ResultsAnalyzer()` - Create analyzer
- `list_runs()` - List all experimental runs
- `analyze_run(run_id, model_name)` - Analyze specific run
- `compare_models(run_id)` - Compare all models in a run
- `print_analysis(run_id, model_name)` - Print formatted report
- `print_comparison(run_id)` - Print model comparison

**Example:**
```python
from results_analyzer import ResultsAnalyzer

analyzer = ResultsAnalyzer()

# List available runs
runs = analyzer.list_runs()

# Analyze a specific run
analyzer.print_analysis("exp_001", "gpt4")

# Compare all models in a run
analyzer.print_comparison("exp_001")
```

## Example Scripts

### quickstart.py
Complete end-to-end example showing:
- Parsing model output
- Validating solutions
- Logging results
- Analyzing results

Run: `python3 quickstart.py`

### example_model_evaluation.py
Full evaluation pipeline with:
- Multiple iterations
- Multiple puzzle sizes
- Summary statistics

Run: `python3 example_model_evaluation.py`

### parse_and_validate_example.py
Examples of parsing and validation integration.

Run: `python3 parse_and_validate_example.py`

### test_multiple_attempts.py
Tests for handling multiple `moves=` patterns in model output.

Run: `python3 test_multiple_attempts.py`

## Parsing Features

The parser handles various output formats:

**Simple format:**
```
moves=[[1,0,2],[2,0,1],[1,2,1]]
```

**With line breaks:**
```
moves=[
    [1, 0, 2],
    [2, 0, 1],
    [1, 2, 1]
]
```

**Multiple attempts (takes last):**
```
First try:
moves=[[1,0,1],[2,0,2]]

Correct answer:
moves=[[1,0,2],[2,0,1],[1,2,1]]
```

**No label (lenient mode):**
```
Here's my answer: [[1,0,2],[2,0,1],[1,2,1]]
```

## Validation

The validator checks:
- Move format correctness
- Tower of Hanoi rules compliance
- Solution completeness
- Efficiency (compared to optimal)

**Optimal moves:** 2^n - 1 (where n is the number of disks)

## Analysis Metrics

The analyzer provides:
- **Success rate** - Percentage of correct solutions
- **Average tokens** - Mean tokens used per iteration
- **Average efficiency** - Mean efficiency for successful solutions
- **Failure breakdown** - Categorized failure reasons:
  - Parse errors
  - Invalid moves
  - Incomplete solutions
  - Other

## Usage in Experiments

Typical workflow:

1. **Setup:**
   ```python
   logger = OutputLogger(run_id="exp_001", model_name="my_model")
   ```

2. **For each test iteration:**
   ```python
   # Get model output
   output = call_your_model(prompt)

   # Parse and validate
   moves, error = parse_hanoi_output(output)
   validator = AutomatedValidator(n_disks=3)
   result = validator.validate_solution(moves) if moves else {}

   # Log
   logger.log_iteration_with_validation(...)
   ```

3. **Analyze:**
   ```python
   analyzer = ResultsAnalyzer()
   analyzer.print_analysis("exp_001", "my_model")
   ```

## Best Practices

1. **Use unique run IDs** - Include timestamp or version info
2. **Log all attempts** - Even failures provide useful data
3. **Track tokens** - Important for cost/efficiency analysis
4. **Use metadata** - Add custom info like temperature, prompting strategy
5. **Regular analysis** - Check results frequently during experiments

## Integration Example

```python
def run_experiment(model, n_disks_list, iterations=10):
    """Run a complete experiment."""
    run_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = OutputLogger(run_id=run_id, model_name=model.name)

    for n_disks in n_disks_list:
        prompt = create_prompt(n_disks)

        for i in range(iterations):
            # Call model
            output, tokens = model.generate(prompt)

            # Parse and validate
            moves, error = parse_hanoi_output(output)
            validator = AutomatedValidator(n_disks)
            result = validator.validate_solution(moves) if moves else {}

            # Log
            logger.log_iteration_with_validation(
                n_disks=n_disks,
                raw_output=output,
                input_prompt=prompt,
                validation_result=result,
                tokens_used=tokens,
                parsed_output=moves,
                parse_error=error,
                metadata={"iteration": i}
            )

    # Analyze
    analyzer = ResultsAnalyzer()
    analyzer.print_analysis(run_id, model.name)

    return logger.output_dir
```

## Files

- `output_parser.py` - Output parsing utilities
- `automated_validator.py` - Solution validation
- `output_logger.py` - JSONL logging
- `results_analyzer.py` - Results analysis
- `quickstart.py` - Quick start example
- `example_model_evaluation.py` - Full pipeline example
- `parse_and_validate_example.py` - Parse/validate examples
- `test_multiple_attempts.py` - Multiple attempts tests
- `hanoi_state.py` - Core puzzle state management
- `hanoi_simulator.py` - Interactive simulator
