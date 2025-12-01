#!/usr/bin/env python3
"""
Example: Model Evaluation Pipeline

This demonstrates how to use the OutputLogger with a model evaluation pipeline.
"""

from output_logging.output_logger import OutputLogger
from output_logging.output_parser import parse_hanoi_output
from puzzles.hanoi_tower.automated_validator import AutomatedValidator
from datetime import datetime


def simulate_model_call(prompt: str, n_disks: int) -> tuple[str, int]:
    """
    Simulate calling a reasoning model.
    In practice, this would call your actual model API.

    Args:
        prompt: The prompt to send to the model
        n_disks: Number of disks in the puzzle

    Returns:
        Tuple of (model_output, tokens_used)
    """
    # This is a placeholder - replace with actual model call
    if n_disks == 3:
        output = """
        Let me solve this step by step.
        moves=[[1,0,2],[2,0,1],[1,2,1],[3,0,2],[1,1,0],[2,1,2],[1,0,2]]
        """
        tokens = 150
    else:
        output = "I cannot solve this puzzle."
        tokens = 20

    return output, tokens


def evaluate_single_iteration(
    logger: OutputLogger,
    n_disks: int,
    prompt: str,
    iteration_num: int = 1
) -> dict:
    """
    Evaluate a single model iteration.

    Args:
        logger: OutputLogger instance
        n_disks: Number of disks in the puzzle
        prompt: Prompt to send to the model
        iteration_num: Iteration number (for display)

    Returns:
        Dictionary with evaluation results
    """
    print(f"\n{'='*70}")
    print(f"Iteration {iteration_num} - {n_disks} disks")
    print('='*70)

    # Step 1: Call the model
    print("1. Calling model...")
    raw_output, tokens_used = simulate_model_call(prompt, n_disks)
    print(f"   ✓ Received output ({tokens_used} tokens)")

    # Step 2: Parse the output
    print("2. Parsing output...")
    parsed_moves, parse_error = parse_hanoi_output(raw_output)

    if parse_error:
        print(f"   ✗ Parse error: {parse_error}")
        # Log the failure
        logger.log_iteration_with_validation(
            n_disks=n_disks,
            raw_output=raw_output,
            input_prompt=prompt,
            validation_result={},
            tokens_used=tokens_used,
            parsed_output=None,
            parse_error=parse_error,
            metadata={"iteration": iteration_num}
        )
        return {"success": False, "reason": "parse_error"}

    print(f"   ✓ Parsed {len(parsed_moves)} moves")

    # Step 3: Validate the solution
    print("3. Validating solution...")
    validator = AutomatedValidator(n_disks=n_disks)
    validation_result = validator.validate_solution(parsed_moves, verbose=False)

    if validation_result['is_valid'] and validation_result['is_solved']:
        print(f"   ✓ Valid and solved! Efficiency: {validation_result['efficiency']:.1%}")
        success = True
    else:
        print(f"   ✗ Failed: {validation_result.get('error_message', 'Not solved')}")
        success = False

    # Step 4: Log the result
    print("4. Logging result...")
    logger.log_iteration_with_validation(
        n_disks=n_disks,
        raw_output=raw_output,
        input_prompt=prompt,
        validation_result=validation_result,
        tokens_used=tokens_used,
        parsed_output=parsed_moves,
        parse_error=None,
        metadata={"iteration": iteration_num}
    )
    print("   ✓ Logged to JSONL")

    return {
        "success": success,
        "validation": validation_result
    }


def run_experiment(
    run_id: str,
    model_name: str,
    n_disks_list: list[int],
    iterations_per_size: int = 5
):
    """
    Run a full experiment evaluating a model on multiple puzzle sizes.

    Args:
        run_id: Unique identifier for this run
        model_name: Name of the model being evaluated
        n_disks_list: List of puzzle sizes to test
        iterations_per_size: Number of iterations per puzzle size
    """
    print("\n" + "="*70)
    print(f"STARTING EXPERIMENT: {run_id}")
    print("="*70)
    print(f"Model: {model_name}")
    print(f"Puzzle sizes: {n_disks_list}")
    print(f"Iterations per size: {iterations_per_size}")

    # Initialize logger
    logger = OutputLogger(
        run_id=run_id,
        model_name=model_name,
        puzzle_name="hanoi"
    )

    print(f"\nOutput directory: {logger.output_dir}")

    # Run experiments for each puzzle size
    for n_disks in n_disks_list:
        print(f"\n{'#'*70}")
        print(f"# Testing with {n_disks} disks")
        print(f"{'#'*70}")

        # Clear previous results for this size
        logger.clear_output(n_disks)

        # Create prompt
        prompt = f"""Solve the Tower of Hanoi puzzle with {n_disks} disks.

Initial state: All disks are on peg 0
Goal: Move all disks to peg 2
Rules:
- Only move one disk at a time
- Cannot place larger disk on smaller disk

Provide your solution in the format:
moves=[[disk, from_peg, to_peg], ...]
"""

        # Run multiple iterations
        for i in range(1, iterations_per_size + 1):
            evaluate_single_iteration(
                logger=logger,
                n_disks=n_disks,
                prompt=prompt,
                iteration_num=i
            )

        # Display summary for this size
        print(f"\n{'-'*70}")
        print(f"Summary for {n_disks} disks")
        print('-'*70)

        summary = logger.get_summary_stats(n_disks)
        print(f"Total iterations: {summary['total_iterations']}")
        print(f"Successful: {summary['successful']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success rate: {summary['success_rate']:.1%}")
        if summary['avg_tokens_used']:
            print(f"Avg tokens: {summary['avg_tokens_used']:.1f}")
        if summary['avg_efficiency']:
            print(f"Avg efficiency: {summary['avg_efficiency']:.1%}")

        print(f"\nOutput file: {logger.get_output_file(n_disks)}")

    # Final summary
    print("\n" + "="*70)
    print("EXPERIMENT COMPLETE")
    print("="*70)
    print(f"\nAll results saved to: {logger.output_dir}")

    # Display overall statistics
    print("\nOverall Statistics:")
    print("-"*70)
    for n_disks in n_disks_list:
        summary = logger.get_summary_stats(n_disks)
        print(f"n={n_disks}: {summary['successful']}/{summary['total_iterations']} "
              f"({summary['success_rate']:.1%})")


def main():
    """Run example experiment."""
    # Generate a unique run ID
    run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Run experiment
    run_experiment(
        run_id=run_id,
        model_name="test_model",
        n_disks_list=[3],  # You can extend to [3, 4, 5, etc.]
        iterations_per_size=3
    )


if __name__ == "__main__":
    main()
