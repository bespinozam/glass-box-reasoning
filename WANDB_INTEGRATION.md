# Wandb Integration - Full Data Logging

## Overview

The `ValidationPipeline.py` logs **complete, untruncated data** to Weights & Biases (wandb) in addition to the existing JSONL logging. This provides both detailed data preservation AND powerful visualization capabilities.

## What's Logged to Wandb

### 1. **Run Configuration**
Automatically logged when wandb is initialized:
- `model_name`: Name of the model being evaluated
- `level_limit`: Maximum difficulty level tested
- `num_samples`: Number of samples per level
- `verbose`: Whether verbose logging is enabled
- `puzzle`: Puzzle type (hanoi)

### 2. **Full Iteration Data (JSON Artifacts)** ⭐ NEW
Complete, untruncated data for every iteration saved as JSON files:

**`all_iterations_full_data.json`** - Single comprehensive file with:
```json
{
  "metadata": {
    "model_name": "...",
    "run_id": "test_run_2025",
    "level_limit": 5,
    "num_samples": 10,
    "total_iterations": 50,
    "generated_at": "2025-12-01T..."
  },
  "iterations": [
    {
      "timestamp": "2025-12-01T12:34:56.789",
      "n_disks": 3,
      "sample_idx": 0,
      "is_correct": true,
      "failure_reason": null,
      "tokens_used": 1234,
      "prompt_tokens": 234,
      "response_tokens": 1000,
      "raw_output": "COMPLETE FULL OUTPUT TEXT...",  // NOT TRUNCATED
      "input_prompt": "COMPLETE FULL PROMPT...",      // NOT TRUNCATED
      "parsed_output": [[1,0,2], [2,0,1], ...],       // FULL MOVES LIST
      "validation_result": {
        "is_valid": true,
        "is_solved": true,
        "total_moves": 7,
        "optimal_moves": 7,
        "efficiency": 1.0,
        "failed_at": null,
        "error_message": null
      }
    },
    // ... all other iterations
  ],
  "summary": {
    "1": {"passed": 10, "parse_failed": 0, "validation_failed": 0},
    "2": {"passed": 9, "parse_failed": 1, "validation_failed": 0},
    // ... other levels
  }
}
```

**`level_{N}_iterations.json`** - Per-level files for easier access:
- One file per difficulty level
- Contains only iterations for that level
- Same full data structure as above

### 3. **Summary Tables** (for Dashboard Visualization)
Two tables for quick viewing in wandb UI:

**`iterations_summary`** - Summary of each iteration:
- `timestamp`, `n_disks`, `sample_idx`
- `is_correct`, `failure_reason`
- `tokens_used`, `total_moves`, `optimal_moves`
- `efficiency`, `is_valid`, `is_solved`

**`level_summary`** - Aggregate results per level:
- `level`, `passed`, `parse_failed`, `validation_failed`, `accuracy`

### 4. **Per-Sample Metrics**
Real-time metrics logged for each sample:
```
level_{N}/sample_{M}/is_correct
level_{N}/sample_{M}/tokens_used
level_{N}/sample_{M}/total_moves
level_{N}/sample_{M}/efficiency
level_{N}/sample_{M}/parse_error  (if parsing failed)
```

### 5. **Per-Level Aggregate Metrics**
Summary statistics for each difficulty level:
```
level_{N}/accuracy
level_{N}/passed
level_{N}/parse_failed
level_{N}/validation_failed
```

### 6. **Overall Statistics**
Final aggregate metrics across all levels:
```
overall/accuracy
overall/total_passed
overall/total_samples
```

### 7. **Artifacts**
Two types of artifacts are uploaded:

**`full-iteration-data-{model_name}`** (type: `detailed-results`)
- Contains all JSON files with COMPLETE data
- `all_iterations_full_data.json` - Everything in one file
- `level_{N}_iterations.json` - Per-level files
- **NO TRUNCATION** - Full outputs, prompts, and moves

**`jsonl-outputs-{model_name}`** (type: `model-outputs`)
- Original JSONL files from local logging
- Same format as local files
- For backwards compatibility

## Data Completeness

### What's FULLY Preserved:
✅ **Complete raw outputs** - Every character of model output
✅ **Complete input prompts** - Full prompts with all details
✅ **Complete parsed moves** - Full move sequences
✅ **Full validation results** - All validation metadata
✅ **Exact timestamps** - ISO format timestamps
✅ **Token counts** - Separated into prompt and response tokens

### Summary Table (for visualization):
- Contains all metrics but NO full text
- Just for quick dashboard viewing
- Full data is in the JSON artifacts

## Usage

### Basic Usage
```python
from eval.ValidationPipeline import ValidationPipe

# Initialize pipeline
pipeline = ValidationPipe(model_name="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")

# Run evaluation with wandb logging
results = pipeline.run_evaluation(
    level_limit=5,
    num_samples=10,
    verbose=False,
    wandb_key="your_wandb_api_key_here"
)
```

After running, you'll see:
```
Saving full iteration data to wandb...
  ✓ Saved 50 iterations to all_iterations_full_data.json
  ✓ Saved level 1 data to level_1_iterations.json
  ✓ Saved level 2 data to level_2_iterations.json
  ...
  ✓ Uploaded full data artifact: full-iteration-data-{model_name}
  ✓ Uploaded JSONL artifact: jsonl-outputs-{model_name}

✓ All data logged to wandb successfully!
  - Summary table: iterations_summary
  - Full data JSON: full-iteration-data-{model_name}
  - Original JSONL: jsonl-outputs-{model_name}
```

### Accessing the Data

#### 1. Download Full Data from Wandb UI:
1. Go to your run in wandb
2. Click "Artifacts" tab
3. Find `full-iteration-data-{model_name}`
4. Download `all_iterations_full_data.json` or individual level files

#### 2. Download via Wandb API:
```python
import wandb

# Initialize API
api = wandb.Api()

# Get artifact
artifact = api.artifact(
    'your-username/the-illusion-of-thinking/full-iteration-data-model_name:latest',
    type='detailed-results'
)

# Download to local directory
artifact_dir = artifact.download()

# Load the full data
import json
with open(f"{artifact_dir}/all_iterations_full_data.json", 'r') as f:
    full_data = json.load(f)

# Access any iteration
for iteration in full_data["iterations"]:
    print(f"Level {iteration['n_disks']}, Sample {iteration['sample_idx']}")
    print(f"Full output: {iteration['raw_output']}")
    print(f"Full prompt: {iteration['input_prompt']}")
    print(f"Parsed moves: {iteration['parsed_output']}")
    print("---")
```

#### 3. Process Locally:
The JSON files are also saved locally in:
```
outputs/test_run_2025/{model_name}/wandb_json/
├── all_iterations_full_data.json
├── level_1_iterations.json
├── level_2_iterations.json
└── ...
```

### Analysis Examples

#### Load and Filter Data:
```python
import json

# Load full data
with open('all_iterations_full_data.json', 'r') as f:
    data = json.load(f)

# Get all failed iterations
failed = [
    it for it in data["iterations"]
    if not it["is_correct"]
]

# Analyze failure reasons
from collections import Counter
reasons = Counter(it["failure_reason"] for it in failed)
print(reasons)

# Get all level 5 iterations with full outputs
level_5 = [
    it for it in data["iterations"]
    if it["n_disks"] == 5
]

for it in level_5:
    print("Full model response:")
    print(it["raw_output"])
    print("\n" + "="*80 + "\n")
```

#### Compare Outputs Across Levels:
```python
# Average output length by difficulty
from collections import defaultdict

output_lengths = defaultdict(list)
for it in data["iterations"]:
    output_lengths[it["n_disks"]].append(len(it["raw_output"]))

for level in sorted(output_lengths.keys()):
    avg_length = sum(output_lengths[level]) / len(output_lengths[level])
    print(f"Level {level}: Average output length = {avg_length:.0f} chars")
```

## Wandb Dashboard

### Panels
1. **Overview Tab**
   - Overall accuracy metrics
   - Success/failure counts
   - Model configuration

2. **Charts Tab**
   - Accuracy trends by level
   - Token usage distribution
   - Efficiency metrics
   - Parse failure rates

3. **Tables Tab**
   - `iterations_summary`: Clickable summary table
   - `level_summary`: Aggregate stats per level

4. **Artifacts Tab** ⭐
   - **`full-iteration-data-{model_name}`**: Download full JSON files
   - **`jsonl-outputs-{model_name}`**: Original JSONL files
   - Both contain 100% complete data

## Data Consistency

All three storage methods contain **identical data**:

| Storage | Full Outputs | Full Prompts | Full Moves | Metadata |
|---------|--------------|--------------|------------|----------|
| **Local JSONL** | ✅ | ✅ | ✅ | ✅ |
| **Wandb JSON Artifact** | ✅ | ✅ | ✅ | ✅ |
| **Wandb JSONL Artifact** | ✅ | ✅ | ✅ | ✅ |
| Wandb Summary Table | ❌ (for UI) | ❌ (for UI) | ❌ (for UI) | ✅ |

The summary table is intentionally limited for quick dashboard viewing.
**All complete data is preserved in the JSON and JSONL artifacts.**

## Benefits

### Complete Data Preservation:
1. ✅ **No truncation** - Every character preserved
2. ✅ **Full reproducibility** - Can re-analyze any detail
3. ✅ **Cloud backup** - Data safe in wandb
4. ✅ **Easy sharing** - Share artifact links with team
5. ✅ **Version control** - Wandb tracks artifact versions

### Flexible Access:
1. 📊 **Quick view** - Summary tables in dashboard
2. 📥 **Download** - Get full JSON files anytime
3. 🔍 **Query** - Filter and analyze programmatically
4. 📈 **Visualize** - Create custom charts in wandb
5. 💾 **Local backup** - Also saved locally

## Best Practices

### 1. Accessing Full Data
For analysis that needs complete outputs, always download the JSON artifact:
```python
# Good - Gets full data
artifact = api.artifact('full-iteration-data-model:latest')
artifact.download()

# Not ideal - Summary table doesn't have full text
table = run.summary_table("iterations_summary")
```

### 2. Organizing Runs
```python
wandb.init(
    project="the-illusion-of-thinking",
    name=f"{model_name}_level{level_limit}_{timestamp}",
    tags=["full-run", f"levels-{level_limit}", model_name],
    notes="Detailed notes about this experiment"
)
```

### 3. Efficient Loading
For large runs, use level-specific files:
```python
# Instead of loading all 1000 iterations
with open('all_iterations_full_data.json') as f:
    all_data = json.load(f)

# Load just level 5
with open('level_5_iterations.json') as f:
    level_5_data = json.load(f)  # Much faster!
```

## File Sizes

Typical sizes for reference:
- Level 1-3: ~1-5 KB per iteration
- Level 4-7: ~5-20 KB per iteration (longer outputs)
- Level 8-10: ~20-100 KB per iteration (much longer reasoning)

For 50 iterations across 5 levels (~250 total):
- `all_iterations_full_data.json`: ~5-20 MB
- Per-level files: ~1-5 MB each
- Summary tables: <1 MB

All data is compressed when uploaded to wandb.

## Troubleshooting

**Q: Where is the full output text?**
A: In the JSON artifacts! Download `full-iteration-data-{model_name}` from the Artifacts tab.

**Q: The summary table only shows metrics, not text?**
A: Correct! That's for quick viewing. Full text is in the JSON artifacts.

**Q: How do I download just one level's data?**
A: Download the artifact and look for `level_{N}_iterations.json` files.

**Q: Can I access the data without wandb?**
A: Yes! The JSON files are also saved locally in `outputs/.../wandb_json/`

**Q: How much does this cost in wandb storage?**
A: Wandb has generous free tier. Typical runs are <100 MB compressed.
