from eval.utils import create_hanoi_prompt
from models.deepseek import load_tokenizer, Model
from output_logging.output_parser import parse_hanoi_output
from puzzles.hanoi_tower.automated_validator import AutomatedValidator
from output_logging.output_logger import OutputLogger
import wandb
from datetime import datetime
import json
from pathlib import Path

class ValidationPipe:
    def __init__(self, model_name):
        self.model_name = model_name

        self.tokenizer = load_tokenizer(model_name)
        self.model = Model(model_name, self.tokenizer)


    def run_evaluation(self, level_limit=5, num_samples=5, verbose=False, wandb_key=None):
        print(f"Running evaluation for model {self.model_name}")
        logger = OutputLogger(
            run_id="test_run_2025",
            model_name=self.model_name,
            puzzle_name="hanoi"
        )
        print(f"Output directory: {logger.output_dir}")
        run_results = {}

        # Initialize wandb logging
        use_wandb = wandb_key is not None
        if use_wandb:
            print("Logging in on wandb")
            wandb.login(key=wandb_key)
            wandb.init(
                project="the-illusion-of-thinking",
                name="experiment_1",
                config={
                    "model_name": self.model_name,
                    "level_limit": level_limit,
                    "num_samples": num_samples,
                    "verbose": verbose,
                    "puzzle": "hanoi"
                }
            )

            # Create wandb Table for summary viewing (with previews)
            summary_columns = [
                "timestamp", "n_disks", "sample_idx", "is_correct",
                "failure_reason", "tokens_used", "total_moves", "optimal_moves",
                "efficiency", "is_valid", "is_solved"
            ]
            summary_table = wandb.Table(columns=summary_columns)

            # Store full iteration data for JSON export
            all_iterations_data = []
        else:
            print("Skipping wandb setup")
            summary_table = None
            all_iterations_data = None


        for current_level in range(1, level_limit + 1):
            print(f"Running evaluation for level {current_level}")
            run_results[str(current_level)] = {"passed": 0, "parse_failed": 0, "validation_failed": 0}
            for sample_iter in range(num_samples):
                print(f"\tSample {sample_iter}")
                prompt = create_hanoi_prompt(self.tokenizer, current_level)

                if verbose:
                    print(f"prompt:\n{prompt}")

                prompt_tokens = self.tokenizer(prompt, return_tensors="pt")
                prompt_length = prompt_tokens['input_ids'].shape[1]

                response = []
                for token in self.model.generate_streaming(
                    prompt = prompt,
                    max_new_tokens = 65000,
                    temperature = 1.0,
                    top_p = 1.0,
                    do_sample = True
                ):
                    response.append(token)
                    if verbose:
                        print(token, end="", flush=True)

                # Parsing output to check for solution
                response_length = len(response)
                response_as_text = "".join(response)
                moves, error = parse_hanoi_output(response_as_text)

                # Prepare common data for logging
                timestamp = datetime.utcnow().isoformat()
                tokens_used = prompt_length + response_length

                if moves:
                    validator = AutomatedValidator(n_disks=current_level)
                    result = validator.validate_solution(moves, verbose=False)

                    # Log to JSONL
                    logger.log_iteration_with_validation(
                        n_disks=current_level,
                        raw_output=response_as_text,
                        input_prompt=prompt,
                        validation_result=result,
                        tokens_used=tokens_used,
                        parsed_output=moves,
                        parse_error=result["error_message"]
                    )

                    # Prepare wandb data
                    if use_wandb:
                        is_correct = result["is_valid"] and result["is_solved"]
                        failure_reason = None if is_correct else (
                            f"Invalid: {result.get('error_message', 'Unknown')}" if not result.get("is_valid")
                            else "Valid but not solved"
                        )

                        # Store FULL iteration data (no truncation)
                        full_iteration_data = {
                            "timestamp": timestamp,
                            "n_disks": current_level,
                            "sample_idx": sample_iter,
                            "is_correct": is_correct,
                            "failure_reason": failure_reason,
                            "tokens_used": tokens_used,
                            "prompt_tokens": prompt_length,
                            "response_tokens": response_length,
                            "raw_output": response_as_text,  # FULL OUTPUT
                            "input_prompt": prompt,  # FULL PROMPT
                            "parsed_output": moves,  # FULL MOVES
                            "validation_result": {
                                "is_valid": result.get("is_valid"),
                                "is_solved": result.get("is_solved"),
                                "total_moves": result.get("total_moves"),
                                "optimal_moves": result.get("optimal_moves"),
                                "efficiency": result.get("efficiency"),
                                "failed_at": result.get("failed_at"),
                                "error_message": result.get("error_message")
                            }
                        }
                        all_iterations_data.append(full_iteration_data)

                        # Add summary row to table (for dashboard visualization)
                        summary_table.add_data(
                            timestamp,
                            current_level,
                            sample_iter,
                            is_correct,
                            failure_reason,
                            tokens_used,
                            result.get("total_moves"),
                            result.get("optimal_moves"),
                            result.get("efficiency"),
                            result.get("is_valid"),
                            result.get("is_solved")
                        )

                        # Log per-sample metrics
                        wandb.log({
                            f"level_{current_level}/sample_{sample_iter}/is_correct": is_correct,
                            f"level_{current_level}/sample_{sample_iter}/tokens_used": tokens_used,
                            f"level_{current_level}/sample_{sample_iter}/total_moves": result.get("total_moves", 0),
                            f"level_{current_level}/sample_{sample_iter}/efficiency": result.get("efficiency", 0),
                        })

                    if result["is_solved"]:
                        run_results[str(current_level)]["passed"] += 1
                    else:
                        run_results[str(current_level)]["validation_failed"] += 1

                else:
                    # Log to JSONL
                    logger.log_iteration_with_validation(
                        n_disks=current_level,
                        raw_output=response_as_text,
                        input_prompt=prompt,
                        validation_result={},
                        tokens_used=tokens_used,
                        parsed_output=moves,
                        parse_error=error
                    )

                    # Prepare wandb data
                    if use_wandb:
                        # Store FULL iteration data (no truncation)
                        full_iteration_data = {
                            "timestamp": timestamp,
                            "n_disks": current_level,
                            "sample_idx": sample_iter,
                            "is_correct": False,
                            "failure_reason": f"Parse error: {error}",
                            "tokens_used": tokens_used,
                            "prompt_tokens": prompt_length,
                            "response_tokens": response_length,
                            "raw_output": response_as_text,  # FULL OUTPUT
                            "input_prompt": prompt,  # FULL PROMPT
                            "parsed_output": None,
                            "parse_error": error,
                            "validation_result": None
                        }
                        all_iterations_data.append(full_iteration_data)

                        # Add summary row to table
                        summary_table.add_data(
                            timestamp,
                            current_level,
                            sample_iter,
                            False,  # is_correct
                            f"Parse error: {error}",
                            tokens_used,
                            None,  # total_moves
                            None,  # optimal_moves
                            None,  # efficiency
                            False,  # is_valid
                            False   # is_solved
                        )

                        wandb.log({
                            f"level_{current_level}/sample_{sample_iter}/is_correct": False,
                            f"level_{current_level}/sample_{sample_iter}/tokens_used": tokens_used,
                            f"level_{current_level}/sample_{sample_iter}/parse_error": error,
                        })

                    run_results[str(current_level)]["parse_failed"] += 1

            # Log aggregate metrics per level
            if use_wandb:
                total_samples = num_samples
                wandb.log({
                    f"level_{current_level}/accuracy": run_results[str(current_level)]["passed"] / total_samples,
                    f"level_{current_level}/passed": run_results[str(current_level)]["passed"],
                    f"level_{current_level}/parse_failed": run_results[str(current_level)]["parse_failed"],
                    f"level_{current_level}/validation_failed": run_results[str(current_level)]["validation_failed"],
                })

        # Print final results
        print("\n" + "="*60)
        print("EVALUATION RESULTS")
        print("="*60)
        for level, results in run_results.items():
            print(f"\nLevel {level}:")
            print(f"  Passed: {results['passed']}/{num_samples}")
            print(f"  Parse Failed: {results['parse_failed']}/{num_samples}")
            print(f"  Validation Failed: {results['validation_failed']}/{num_samples}")
        print("="*60)

        # Log final wandb data
        if use_wandb:
            # Log the summary table (for quick dashboard viewing)
            wandb.log({"iterations_summary": summary_table})

            # Calculate and log overall statistics
            total_passed = sum(r["passed"] for r in run_results.values())
            total_samples_run = num_samples * level_limit
            overall_accuracy = total_passed / total_samples_run

            wandb.log({
                "overall/accuracy": overall_accuracy,
                "overall/total_passed": total_passed,
                "overall/total_samples": total_samples_run,
            })

            # Log level summary table
            level_summary_table = wandb.Table(
                columns=["level", "passed", "parse_failed", "validation_failed", "accuracy"],
                data=[
                    [
                        int(level),
                        results["passed"],
                        results["parse_failed"],
                        results["validation_failed"],
                        results["passed"] / num_samples
                    ]
                    for level, results in run_results.items()
                ]
            )
            wandb.log({"level_summary": level_summary_table})

            # Save FULL iteration data to JSON files and upload as artifacts
            print("\nSaving full iteration data to wandb...")

            # Create temporary directory for wandb JSON files
            wandb_json_dir = logger.output_dir / "wandb_json"
            wandb_json_dir.mkdir(exist_ok=True)

            # Save all iterations to a single comprehensive JSON file
            full_data_file = wandb_json_dir / "all_iterations_full_data.json"
            with open(full_data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "model_name": self.model_name,
                        "run_id": "test_run_2025",
                        "level_limit": level_limit,
                        "num_samples": num_samples,
                        "total_iterations": len(all_iterations_data),
                        "generated_at": datetime.utcnow().isoformat()
                    },
                    "iterations": all_iterations_data,
                    "summary": run_results
                }, f, indent=2, ensure_ascii=False)

            print(f"  ✓ Saved {len(all_iterations_data)} iterations to {full_data_file.name}")

            # Also save per-level JSON files for easier access
            for level in range(1, level_limit + 1):
                level_data = [
                    iteration for iteration in all_iterations_data
                    if iteration["n_disks"] == level
                ]
                if level_data:
                    level_file = wandb_json_dir / f"level_{level}_iterations.json"
                    with open(level_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            "metadata": {
                                "model_name": self.model_name,
                                "level": level,
                                "num_samples": len(level_data),
                                "generated_at": datetime.utcnow().isoformat()
                            },
                            "iterations": level_data,
                            "summary": run_results[str(level)]
                        }, f, indent=2, ensure_ascii=False)
                    print(f"  ✓ Saved level {level} data to {level_file.name}")

            # Upload JSON files as wandb artifact
            json_artifact = wandb.Artifact(
                name=f"full-iteration-data-{self.model_name}",
                type="detailed-results",
                description=f"Complete iteration data with full outputs for {self.model_name}"
            )

            # Add all JSON files
            for json_file in wandb_json_dir.glob("*.json"):
                json_artifact.add_file(str(json_file))

            wandb.log_artifact(json_artifact)
            print(f"  ✓ Uploaded full data artifact: full-iteration-data-{self.model_name}")

            # Also upload original JSONL files as a separate artifact
            jsonl_artifact = wandb.Artifact(
                name=f"jsonl-outputs-{self.model_name}",
                type="model-outputs",
                description=f"Original JSONL output files for {self.model_name}"
            )

            # Add all JSONL files from the output directory
            for jsonl_file in logger.output_dir.glob("*.jsonl"):
                jsonl_artifact.add_file(str(jsonl_file))

            wandb.log_artifact(jsonl_artifact)
            print(f"  ✓ Uploaded JSONL artifact: jsonl-outputs-{self.model_name}")

            # Finish wandb run
            wandb.finish()
            print("\n✓ All data logged to wandb successfully!")
            print(f"  - Summary table: iterations_summary")
            print(f"  - Full data JSON: full-iteration-data-{self.model_name}")
            print(f"  - Original JSONL: jsonl-outputs-{self.model_name}")

        return run_results