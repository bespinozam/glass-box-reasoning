"""
Output Parser Module

This module provides functionality to parse reasoning model outputs
for the Tower of Hanoi puzzle. It can robustly extract moves from text
strings even when they contain line breaks and formatting variations.
"""

import re
import json
from typing import List, Optional, Tuple, Any


def parse_hanoi_output(text: str) -> Tuple[Optional[List[List[int]]], Optional[str]]:
    """
    Parse Hanoi Tower puzzle output from a text string.

    This function robustly extracts moves from text output that contains
    the pattern 'moves=[...]', handling line breaks, extra whitespace,
    and various formatting variations.

    Args:
        text: The text string containing the reasoning model output

    Returns:
        Tuple of (moves, error_message):
            - moves: List of moves in format [[disk, from_peg, to_peg], ...] or None if parsing failed
            - error_message: Error message if parsing failed, None otherwise

    Examples:
        >>> text = "The solution is: moves=[[1,0,2],[2,0,1],[1,2,1]]"
        >>> moves, error = parse_hanoi_output(text)
        >>> print(moves)
        [[1, 0, 2], [2, 0, 1], [1, 2, 1]]

        >>> text = '''
        ... Here's my solution:
        ... moves=[
        ...   [1, 0, 2],
        ...   [2, 0, 1],
        ...   [1, 2, 1]
        ... ]
        ... '''
        >>> moves, error = parse_hanoi_output(text)
        >>> print(moves)
        [[1, 0, 2], [2, 0, 1], [1, 2, 1]]
    """
    if not text or not isinstance(text, str):
        return None, "Input text is empty or not a string"

    # Strategy: Find all 'moves=' patterns and use the LAST match
    # This handles cases where the model generates multiple attempts
    # and we want the final answer

    # Find ALL occurrences of the 'moves=' pattern (case-insensitive)
    matches = list(re.finditer(r'moves\s*=\s*(\[)', text, re.IGNORECASE))

    if not matches:
        return None, "Could not find 'moves=' pattern in the text"

    # Take the LAST match
    match = matches[-1]

    # Find the starting position of the list
    start_pos = match.end() - 1  # Position of the opening bracket

    # Extract the complete list by matching brackets
    extracted_list = _extract_bracketed_content(text[start_pos:])

    if extracted_list is None:
        return None, "Could not extract complete list - unmatched brackets"

    # Clean up the extracted content for parsing
    # Remove line breaks and extra whitespace while preserving structure
    cleaned_list = re.sub(r'\s+', ' ', extracted_list)

    # Try to parse as JSON
    try:
        moves = json.loads(cleaned_list)
    except json.JSONDecodeError:
        # JSON parsing failed, try alternative parsing
        moves = _parse_list_alternative(cleaned_list)
        if moves is None:
            return None, f"Could not parse the list: {cleaned_list[:100]}..."

    # Validate the structure
    if not isinstance(moves, list):
        return None, f"Parsed output is not a list: {type(moves)}"

    # Validate each move
    for i, move in enumerate(moves):
        if not isinstance(move, list):
            return None, f"Move {i} is not a list: {move}"

        if len(move) != 3:
            return None, f"Move {i} does not have exactly 3 elements: {move}"

        # Try to convert elements to integers
        try:
            moves[i] = [int(move[0]), int(move[1]), int(move[2])]
        except (ValueError, TypeError) as e:
            return None, f"Move {i} contains non-integer values: {move} - {e}"

    return moves, None


def _extract_bracketed_content(text: str) -> Optional[str]:
    """
    Extract content within matching brackets from text starting with '['.

    Args:
        text: String starting with an opening bracket '['

    Returns:
        The complete bracketed content including the brackets, or None if unmatched
    """
    if not text or text[0] != '[':
        return None

    bracket_count = 0
    for i, char in enumerate(text):
        if char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1

            if bracket_count == 0:
                # Found the matching closing bracket
                return text[:i+1]

    # Unmatched brackets
    return None


def _parse_list_alternative(text: str) -> Optional[List[List[int]]]:
    """
    Alternative parsing method when JSON parsing fails.
    Tries to extract numbers and reconstruct the list structure.

    Args:
        text: String representation of the list

    Returns:
        Parsed list of lists or None if parsing fails
    """
    try:
        # Remove outer brackets
        text = text.strip()
        if text.startswith('[') and text.endswith(']'):
            text = text[1:-1]
        else:
            return None

        # Find all inner lists using regex
        inner_list_pattern = r'\[\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]'
        matches = re.findall(inner_list_pattern, text)

        if not matches:
            return None

        # Convert to list of lists with integers
        result = [[int(m[0]), int(m[1]), int(m[2])] for m in matches]
        return result

    except Exception:
        return None


def parse_hanoi_output_lenient(text: str) -> Tuple[Optional[List[List[int]]], Optional[str]]:
    """
    More lenient version of parse_hanoi_output that tries multiple strategies.

    This function will attempt to find moves in the text even if they're not
    explicitly labeled with 'moves='. It looks for any list-of-lists pattern
    that could represent Hanoi moves.

    Args:
        text: The text string to parse

    Returns:
        Tuple of (moves, error_message)
    """
    # First try the standard parsing
    moves, error = parse_hanoi_output(text)
    if moves is not None:
        return moves, None

    # If that fails, try to find any list of lists in the text
    # Look for patterns like [[1,2,3], [4,5,6], ...]
    # Take the LAST match if multiple patterns are found
    pattern = r'\[\s*\[\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\](?:\s*,\s*\[\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\])*\s*\]'

    matches = list(re.finditer(pattern, text))

    # Process matches in reverse order (last to first)
    for match in reversed(matches):
        potential_moves = match.group(0)
        # Clean up
        cleaned = re.sub(r'\s+', ' ', potential_moves)

        try:
            moves = json.loads(cleaned)

            # Validate structure
            if isinstance(moves, list) and all(
                isinstance(m, list) and len(m) == 3 for m in moves
            ):
                # Convert to integers
                moves = [[int(m[0]), int(m[1]), int(m[2])] for m in moves]
                return moves, None
        except (json.JSONDecodeError, ValueError, TypeError, IndexError):
            continue

    return None, f"Could not find valid moves pattern in text. Original error: {error}"


def validate_and_parse(text: str, n_disks: Optional[int] = None) -> dict:
    """
    Parse the output and optionally validate the move numbers.

    Args:
        text: The text string to parse
        n_disks: Optional number of disks to validate against

    Returns:
        Dictionary with:
            - 'success': bool - Whether parsing succeeded
            - 'moves': List of moves or None
            - 'error': Error message or None
            - 'warnings': List of warning messages
    """
    warnings = []

    # Try lenient parsing first
    moves, error = parse_hanoi_output_lenient(text)

    if moves is None:
        return {
            'success': False,
            'moves': None,
            'error': error,
            'warnings': []
        }

    # Additional validation if n_disks is provided
    if n_disks is not None:
        for i, move in enumerate(moves):
            disk, from_peg, to_peg = move

            # Check if disk number is valid
            if disk < 1 or disk > n_disks:
                warnings.append(
                    f"Move {i}: disk {disk} is out of range (should be 1-{n_disks})"
                )

            # Check if peg numbers are valid
            if from_peg not in [0, 1, 2]:
                warnings.append(
                    f"Move {i}: from_peg {from_peg} is invalid (should be 0, 1, or 2)"
                )

            if to_peg not in [0, 1, 2]:
                warnings.append(
                    f"Move {i}: to_peg {to_peg} is invalid (should be 0, 1, or 2)"
                )

    return {
        'success': True,
        'moves': moves,
        'error': None,
        'warnings': warnings
    }


def main():
    """Demonstration of the parser with various input formats."""
    print("\n" + "="*70)
    print("HANOI OUTPUT PARSER - DEMONSTRATION")
    print("="*70)

    # Test case 1: Simple format
    print("\nTest 1: Simple format")
    print("-" * 70)
    text1 = "moves=[[1,0,2],[2,0,1],[1,2,1]]"
    print(f"Input: {text1}")
    moves, error = parse_hanoi_output(text1)
    if moves:
        print(f"✓ Parsed successfully: {moves}")
    else:
        print(f"✗ Error: {error}")

    # Test case 2: Format with line breaks
    print("\nTest 2: Format with line breaks")
    print("-" * 70)
    text2 = """
    The solution is:
    moves=[
        [1, 0, 2],
        [2, 0, 1],
        [1, 2, 1]
    ]
    That's the answer!
    """
    print(f"Input: {text2}")
    moves, error = parse_hanoi_output(text2)
    if moves:
        print(f"✓ Parsed successfully: {moves}")
    else:
        print(f"✗ Error: {error}")

    # Test case 3: Format with extra whitespace
    print("\nTest 3: Format with extra whitespace")
    print("-" * 70)
    text3 = "moves  =  [ [ 1 , 0 , 2 ] , [ 2 , 0 , 1 ] ]"
    print(f"Input: {text3}")
    moves, error = parse_hanoi_output(text3)
    if moves:
        print(f"✓ Parsed successfully: {moves}")
    else:
        print(f"✗ Error: {error}")

    # Test case 4: Lenient parsing without 'moves=' label
    print("\nTest 4: Lenient parsing without 'moves=' label")
    print("-" * 70)
    text4 = "Here is my answer: [[1,0,2],[2,0,1],[1,2,1]]"
    print(f"Input: {text4}")
    moves, error = parse_hanoi_output_lenient(text4)
    if moves:
        print(f"✓ Parsed successfully: {moves}")
    else:
        print(f"✗ Error: {error}")

    # Test case 5: Invalid format
    print("\nTest 5: Invalid format")
    print("-" * 70)
    text5 = "moves=[1,2,3]"
    print(f"Input: {text5}")
    moves, error = parse_hanoi_output(text5)
    if moves:
        print(f"✓ Parsed successfully: {moves}")
    else:
        print(f"✗ Error: {error}")

    # Test case 6: Validation with n_disks
    print("\nTest 6: Validation with n_disks")
    print("-" * 70)
    text6 = "moves=[[1,0,2],[5,0,1],[1,2,1]]"  # disk 5 in a 3-disk puzzle
    print(f"Input: {text6}")
    result = validate_and_parse(text6, n_disks=3)
    print(f"Success: {result['success']}")
    print(f"Moves: {result['moves']}")
    if result['warnings']:
        print(f"Warnings: {result['warnings']}")

    # Test case 7: Multiple 'moves=' patterns (should take the last one)
    print("\nTest 7: Multiple 'moves=' patterns (takes last match)")
    print("-" * 70)
    text7 = """
    First attempt (wrong):
    moves=[[1,0,1],[2,0,2]]

    Wait, let me reconsider...

    Actually, the correct solution is:
    moves=[[1,0,2],[2,0,1],[1,2,1]]
    """
    print(f"Input: {text7}")
    moves, error = parse_hanoi_output(text7)
    if moves:
        print(f"✓ Parsed successfully (last match): {moves}")
    else:
        print(f"✗ Error: {error}")

    # Test case 8: Multiple list patterns without 'moves=' label
    print("\nTest 8: Multiple list patterns without label (lenient parser)")
    print("-" * 70)
    text8 = """
    Attempt 1: [[1,0,1],[2,0,2]]

    Attempt 2 (final): [[1,0,2],[2,0,1],[1,2,1]]
    """
    print(f"Input: {text8}")
    moves, error = parse_hanoi_output_lenient(text8)
    if moves:
        print(f"✓ Parsed successfully (last match): {moves}")
    else:
        print(f"✗ Error: {error}")

    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    from automated_validator import AutomatedValidator

    validator = AutomatedValidator(n_disks=3)


    bad_sample = "../../output_samples/deepseek-r1-7b-stuck-reasoning.txt"
    good_sample = "../../output_samples/good_sample_n3.txt"
    with open(good_sample, "r") as f:
        text = f.read()
    # print(text)
    moves, error = parse_hanoi_output(text)
    print(moves)
    print(error)
    # main()

    result = validator.validate_solution(moves, verbose=False)
    print(result)