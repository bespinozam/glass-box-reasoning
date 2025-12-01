# Glass Box Reasoning

A framework for evaluating reasoning models on structured puzzles like the Tower of Hanoi.

## Features

- Automated evaluation pipeline for reasoning models
- Built-in puzzle validators (Tower of Hanoi)
- Output logging and analysis tools
- Support for streaming token generation

## Installation

### Local Installation

```bash
git clone https://github.com/yourusername/glass-box-reasoning.git
cd glass-box-reasoning
pip install -e .
```

### Kaggle/Google Colab Installation

In your notebook:

```python
# Clone the repository
!git clone https://github.com/yourusername/glass-box-reasoning.git

# Install as a package
!pip install -e glass-box-reasoning/

# Now you can import anywhere in your notebook
from eval.ValidationPipeline import ValidationPipe
```

## Quick Start

### Basic Usage

```python
from eval.ValidationPipeline import ValidationPipe

# Create a validation pipeline
pipeline = ValidationPipe(model_name="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B")

# Run evaluation
pipeline.run_evaluation(
    level_limit=5,      # Test up to 5 disks
    num_samples=3,      # 3 samples per level
    verbose=True        # Print output as it generates
)
```

### Using Individual Components

```python
from models.deepseek import load_model, load_tokenizer
from eval.utils import create_hanoi_prompt
from puzzles.hanoi_tower.output_parser import parse_hanoi_output
from puzzles.hanoi_tower.automated_validator import AutomatedValidator

# Load model
model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
tokenizer = load_tokenizer(model_name)
model = load_model(model_name)

# Create prompt
prompt = create_hanoi_prompt(tokenizer, n=3)

# Parse and validate output
moves, error = parse_hanoi_output(response_text)
if moves:
    validator = AutomatedValidator(n_disks=3)
    result = validator.validate_solution(moves)
    print(f"Solved: {result['is_solved']}")
```

## Project Structure

```
glass-box-reasoning/
├── eval/
│   ├── __init__.py
│   ├── ValidationPipeline.py    # Main evaluation pipeline
│   └── utils.py                 # Prompt creation utilities
├── models/
│   ├── __init__.py
│   └── deepseek.py             # Model loading utilities
├── puzzles/
│   ├── __init__.py
│   └── hanoi_tower/            # Tower of Hanoi puzzle
│       ├── __init__.py
│       ├── automated_validator.py
│       ├── output_parser.py
│       ├── output_logger.py
│       └── results_analyzer.py
├── setup.py
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.8+
- PyTorch 2.0+
- Transformers 4.30+
- See `requirements.txt` for full list

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License
