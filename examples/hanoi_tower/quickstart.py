#!/usr/bin/env python3
"""
Quick Start: Complete Model Evaluation Pipeline

This script demonstrates the complete workflow for evaluating a reasoning model
on the Tower of Hanoi puzzle.
"""

from output_logging.output_logger import OutputLogger
from output_logging.output_parser import parse_hanoi_output
from puzzles.hanoi_tower.automated_validator import AutomatedValidator
from output_logging.results_analyzer import ResultsAnalyzer


def evaluate_model_output(
    run_id: str,
    model_name: str,
    n_disks: int,
    model_output: str,
    input_prompt: str,
    tokens_used: int = None
) -> dict:
    """
    Complete pipeline: Parse, validate, and log a single model output.

    Args:
        run_id: Unique identifier for this experimental run
        model_name: Name of the model being evaluated
        n_disks: Number of disks in the puzzle
        model_output: Raw output from the model
        input_prompt: The prompt that was sent to the model
        tokens_used: Number of tokens used (optional)

    Returns:
        Dictionary with evaluation results
    """
    # Step 1: Parse the output
    parsed_moves, parse_error = parse_hanoi_output(model_output)

    # Step 2: Validate if parsing succeeded
    validation_result = {}
    if parsed_moves is not None:
        validator = AutomatedValidator(n_disks=n_disks)
        validation_result = validator.validate_solution(parsed_moves, verbose=False)

    # Step 3: Log the result
    logger = OutputLogger(
        run_id=run_id,
        model_name=model_name,
        puzzle_name="hanoi"
    )

    logger.log_iteration_with_validation(
        n_disks=n_disks,
        raw_output=model_output,
        input_prompt=input_prompt,
        validation_result=validation_result,
        tokens_used=tokens_used,
        parsed_output=parsed_moves,
        parse_error=parse_error
    )

    # Return summary
    is_correct = validation_result.get('is_valid', False) and validation_result.get('is_solved', False)

    return {
        "parsed": parsed_moves is not None,
        "valid": validation_result.get('is_valid', False),
        "solved": validation_result.get('is_solved', False),
        "is_correct": is_correct,
        "parse_error": parse_error,
        "validation_error": validation_result.get('error_message'),
        "efficiency": validation_result.get('efficiency')
    }


def main():
    """Quick start example."""
    print("\n" + "="*70)
    print("QUICK START: Model Evaluation Pipeline")
    print("="*70)

    # Configuration
    run_id = "quickstart_demo"
    model_name = "my_model"
    n_disks = 3

    # Example 1: Successful solution
    print("\n" + "-"*70)
    print("Example 1: Successful Solution")
    print("-"*70)

    prompt = "Solve the 3-disk Tower of Hanoi puzzle."

    # Simulate model output (replace with actual model call)
    output_1 = """
    I'll solve this step by step:

    moves=[[1,0,2],[2,0,1],[1,2,1],[3,0,2],[1,1,0],[2,1,2],[1,0,2]]

    This moves all disks from peg 0 to peg 2.
    """

    result_1 = evaluate_model_output(
        run_id=run_id,
        model_name=model_name,
        n_disks=n_disks,
        model_output=output_1,
        input_prompt=prompt,
        tokens_used=150
    )

    print(f"Parsed: {result_1['parsed']}")
    print(f"Valid: {result_1['valid']}")
    print(f"Solved: {result_1['solved']}")
    print(f"Correct: {result_1['is_correct']}")
    if result_1['efficiency']:
        print(f"Efficiency: {result_1['efficiency']:.1%}")

    # Example 2: Failed solution
    print("\n" + "-"*70)
    print("Example 2: Failed Solution")
    print("-"*70)

    output_2 = """
    Let me try:
    moves=[[1,0,1],[3,0,2]]
    """

    result_2 = evaluate_model_output(
        run_id=run_id,
        model_name=model_name,
        n_disks=n_disks,
        model_output=output_2,
        input_prompt=prompt,
        tokens_used=50
    )

    print(f"Parsed: {result_2['parsed']}")
    print(f"Valid: {result_2['valid']}")
    print(f"Solved: {result_2['solved']}")
    print(f"Correct: {result_2['is_correct']}")
    if result_2['validation_error']:
        print(f"Error: {result_2['validation_error']}")

    # Example 3: Parse failure
    print("\n" + "-"*70)
    print("Example 3: Parse Failure")
    print("-"*70)

    output_3 = "I don't understand this problem."

    result_3 = evaluate_model_output(
        run_id=run_id,
        model_name=model_name,
        n_disks=n_disks,
        model_output=output_3,
        input_prompt=prompt,
        tokens_used=15
    )

    print(f"Parsed: {result_3['parsed']}")
    print(f"Correct: {result_3['is_correct']}")
    if result_3['parse_error']:
        print(f"Parse Error: {result_3['parse_error']}")

    # Analyze results
    print("\n" + "="*70)
    print("Analysis")
    print("="*70)

    analyzer = ResultsAnalyzer()
    analyzer.print_analysis(run_id, model_name)

    print("\n" + "="*70)
    print("Files saved to:")
    print("="*70)

    logger = OutputLogger(run_id=run_id, model_name=model_name)
    print(f"  {logger.get_output_file(n_disks)}")
    print("\n")


if __name__ == "__main__":
    main()
