"""
Output Logger Module

This module provides functionality to save reasoning model outputs to JSONL files
for the Tower of Hanoi puzzle experiments.
"""

import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class OutputLogger:
    """
    Logger for saving model outputs to JSONL files.

    File structure: outputs/{run_id}/{model_name}/output_{puzzle_name}_n{N}.jsonl
    """

    def __init__(self, run_id: str, model_name: str, puzzle_name: str = "hanoi",
                 base_dir: str = "outputs"):
        """
        Initialize the output logger.

        Args:
            run_id: Unique identifier for this experimental run
            model_name: Name of the model being evaluated
            puzzle_name: Name of the puzzle (default: "hanoi")
            base_dir: Base directory for outputs (default: "outputs")
        """
        self.run_id = run_id
        self.model_name = model_name
        self.puzzle_name = puzzle_name
        self.base_dir = base_dir

        # Create the directory structure
        self.output_dir = Path(base_dir) / run_id / model_name
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_output_file(self, n_disks: int) -> Path:
        """
        Get the path to the output file for a specific puzzle size.

        Args:
            n_disks: Number of disks in the puzzle

        Returns:
            Path to the JSONL output file
        """
        filename = f"output_{self.puzzle_name}_n{n_disks}.jsonl"
        return self.output_dir / filename

    def log_iteration(
        self,
        n_disks: int,
        raw_output: str,
        input_prompt: str,
        tokens_used: Optional[int] = None,
        parsed_output: Optional[List[List[int]]] = None,
        is_correct: Optional[bool] = None,
        failure_reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a single iteration to the JSONL file.

        Args:
            n_disks: Number of disks in the puzzle
            raw_output: Raw output from the model
            input_prompt: Input prompt sent to the model
            tokens_used: Number of tokens used (optional)
            parsed_output: Parsed moves (optional)
            is_correct: Whether the solution is correct (optional)
            failure_reason: Reason for failure if is_correct is False (optional)
            metadata: Additional metadata to include (optional)
        """
        entry = {
            "raw_output": raw_output,
            "input_prompt": input_prompt,
            "tokens_used": tokens_used,
            "parsed_output": parsed_output,
            "is_correct": is_correct,
            "failure_reason": failure_reason,
            "timestamp": datetime.utcnow().isoformat(),
            "n_disks": n_disks
        }

        # Add any additional metadata
        if metadata:
            entry["metadata"] = metadata

        # Append to JSONL file
        output_file = self.get_output_file(n_disks)
        with open(output_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def log_iteration_with_validation(
        self,
        n_disks: int,
        raw_output: str,
        input_prompt: str,
        validation_result: Dict[str, Any],
        tokens_used: Optional[int] = None,
        parsed_output: Optional[List[List[int]]] = None,
        parse_error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an iteration with automatic validation result processing.

        Args:
            n_disks: Number of disks in the puzzle
            raw_output: Raw output from the model
            input_prompt: Input prompt sent to the model
            validation_result: Result from AutomatedValidator.validate_solution()
            tokens_used: Number of tokens used (optional)
            parsed_output: Parsed moves (optional)
            parse_error: Error from parsing if parsing failed (optional)
            metadata: Additional metadata to include (optional)
        """
        # Determine correctness and failure reason from validation result
        if parse_error:
            is_correct = False
            failure_reason = f"Parse error: {parse_error}"
        elif validation_result.get('is_valid') and validation_result.get('is_solved'):
            is_correct = True
            failure_reason = None
        else:
            is_correct = False
            if not validation_result.get('is_valid'):
                failure_reason = f"Invalid solution: {validation_result.get('error_message', 'Unknown error')}"
            else:
                failure_reason = "Valid moves but puzzle not solved"

        # Add validation details to metadata
        if metadata is None:
            metadata = {}

        metadata["validation"] = {
            "is_valid": validation_result.get('is_valid'),
            "is_solved": validation_result.get('is_solved'),
            "total_moves": validation_result.get('total_moves'),
            "optimal_moves": validation_result.get('optimal_moves'),
            "efficiency": validation_result.get('efficiency'),
            "failed_at": validation_result.get('failed_at')
        }

        self.log_iteration(
            n_disks=n_disks,
            raw_output=raw_output,
            input_prompt=input_prompt,
            tokens_used=tokens_used,
            parsed_output=parsed_output,
            is_correct=is_correct,
            failure_reason=failure_reason,
            metadata=metadata
        )

    def read_iterations(self, n_disks: int) -> List[Dict[str, Any]]:
        """
        Read all iterations for a specific puzzle size.

        Args:
            n_disks: Number of disks in the puzzle

        Returns:
            List of iteration entries
        """
        output_file = self.get_output_file(n_disks)

        if not output_file.exists():
            return []

        iterations = []
        with open(output_file, 'r') as f:
            for line in f:
                if line.strip():
                    iterations.append(json.loads(line))

        return iterations

    def get_summary_stats(self, n_disks: int) -> Dict[str, Any]:
        """
        Get summary statistics for a specific puzzle size.

        Args:
            n_disks: Number of disks in the puzzle

        Returns:
            Dictionary with summary statistics
        """
        iterations = self.read_iterations(n_disks)

        if not iterations:
            return {
                "total_iterations": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0
            }

        total = len(iterations)
        successful = sum(1 for it in iterations if it.get('is_correct'))
        failed = total - successful

        # Calculate average tokens if available
        tokens_list = [it.get('tokens_used') for it in iterations if it.get('tokens_used') is not None]
        avg_tokens = sum(tokens_list) / len(tokens_list) if tokens_list else None

        # Calculate average efficiency for successful attempts
        efficiencies = []
        for it in iterations:
            if it.get('is_correct') and it.get('metadata', {}).get('validation', {}).get('efficiency'):
                efficiencies.append(it['metadata']['validation']['efficiency'])
        avg_efficiency = sum(efficiencies) / len(efficiencies) if efficiencies else None

        return {
            "total_iterations": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0.0,
            "avg_tokens_used": avg_tokens,
            "avg_efficiency": avg_efficiency
        }

    def clear_output(self, n_disks: int) -> None:
        """
        Clear the output file for a specific puzzle size.

        Args:
            n_disks: Number of disks in the puzzle
        """
        output_file = self.get_output_file(n_disks)
        if output_file.exists():
            output_file.unlink()


def main():
    """Demonstration of the output logger."""
    print("\n" + "="*70)
    print("OUTPUT LOGGER - DEMONSTRATION")
    print("="*70)

    # Initialize logger
    print("\nInitializing logger...")
    logger = OutputLogger(
        run_id="test_run_2024",
        model_name="test_model",
        puzzle_name="hanoi"
    )
    print(f"Output directory: {logger.output_dir}")

    # Clear any existing data
    logger.clear_output(n_disks=3)

    # Example 1: Log a successful iteration
    print("\n" + "-"*70)
    print("Example 1: Logging a successful iteration")
    print("-"*70)

    from output_parser import parse_hanoi_output
    from automated_validator import AutomatedValidator

    raw_output_1 = """
    Solution:
    moves=[[1,0,2],[2,0,1],[1,2,1],[3,0,2],[1,1,0],[2,1,2],[1,0,2]]
    """

    prompt_1 = "Solve the 3-disk Tower of Hanoi puzzle."

    # Parse and validate
    moves, parse_error = parse_hanoi_output(raw_output_1)
    validator = AutomatedValidator(n_disks=3)
    result = validator.validate_solution(moves, verbose=False) if moves else {}

    # Log with validation
    logger.log_iteration_with_validation(
        n_disks=3,
        raw_output=raw_output_1,
        input_prompt=prompt_1,
        validation_result=result,
        tokens_used=150,
        parsed_output=moves,
        parse_error=parse_error
    )
    print("✓ Logged successful iteration")

    # Example 2: Log a failed iteration (invalid solution)
    print("\n" + "-"*70)
    print("Example 2: Logging a failed iteration")
    print("-"*70)

    raw_output_2 = """
    Solution:
    moves=[[1,0,1],[3,0,2]]
    """

    prompt_2 = "Solve the 3-disk Tower of Hanoi puzzle."

    moves2, parse_error2 = parse_hanoi_output(raw_output_2)
    validator2 = AutomatedValidator(n_disks=3)
    result2 = validator2.validate_solution(moves2, verbose=False) if moves2 else {}

    logger.log_iteration_with_validation(
        n_disks=3,
        raw_output=raw_output_2,
        input_prompt=prompt_2,
        validation_result=result2,
        tokens_used=75,
        parsed_output=moves2,
        parse_error=parse_error2
    )
    print("✓ Logged failed iteration")

    # Example 3: Log a parsing failure
    print("\n" + "-"*70)
    print("Example 3: Logging a parsing failure")
    print("-"*70)

    raw_output_3 = "I don't know how to solve this."

    moves3, parse_error3 = parse_hanoi_output(raw_output_3)
    result3 = {}

    logger.log_iteration_with_validation(
        n_disks=3,
        raw_output=raw_output_3,
        input_prompt=prompt_2,
        validation_result=result3,
        tokens_used=20,
        parsed_output=moves3,
        parse_error=parse_error3
    )
    print("✓ Logged parsing failure")

    # Read back and display
    print("\n" + "-"*70)
    print("Reading back logged iterations")
    print("-"*70)

    iterations = logger.read_iterations(n_disks=3)
    print(f"\nTotal iterations logged: {len(iterations)}")

    for i, iteration in enumerate(iterations, 1):
        print(f"\nIteration {i}:")
        print(f"  Correct: {iteration['is_correct']}")
        print(f"  Tokens: {iteration['tokens_used']}")
        if iteration['failure_reason']:
            print(f"  Failure: {iteration['failure_reason']}")
        if iteration.get('metadata', {}).get('validation'):
            val = iteration['metadata']['validation']
            print(f"  Moves: {val.get('total_moves')}/{val.get('optimal_moves')}")

    # Display summary
    print("\n" + "-"*70)
    print("Summary Statistics")
    print("-"*70)

    summary = logger.get_summary_stats(n_disks=3)
    print(f"\nTotal iterations: {summary['total_iterations']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success rate: {summary['success_rate']:.1%}")
    print(f"Avg tokens: {summary['avg_tokens_used']:.1f}")
    if summary['avg_efficiency']:
        print(f"Avg efficiency: {summary['avg_efficiency']:.1%}")

    # Show file location
    print("\n" + "-"*70)
    print(f"Output saved to: {logger.get_output_file(n_disks=3)}")
    print("-"*70)

    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
