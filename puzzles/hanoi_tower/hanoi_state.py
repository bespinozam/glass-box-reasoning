"""
Tower of Hanoi State Representation Module

This module provides the HanoiState class for representing and managing
the state of a Tower of Hanoi puzzle.
"""

from typing import List, Tuple, Optional
from copy import deepcopy


class HanoiState:
    """
    Represents the state of a Tower of Hanoi puzzle.

    Attributes:
        n_disks (int): Total number of disks in the puzzle
        pegs (List[List[int]]): Current state of pegs (disks in bottom-to-top order)
        history (List[Tuple[int, int, int]]): History of moves applied (disk, from, to)
        num_moves (int): Total number of moves applied
        is_solved (bool): Flag indicating if puzzle is solved
    """

    def __init__(self, n_disks: int):
        """
        Initialize a Tower of Hanoi puzzle with n disks.

        Args:
            n_disks: Number of disks in the puzzle
        """
        if n_disks < 1:
            raise ValueError("Number of disks must be at least 1")

        self.n_disks = n_disks
        # Initialize all disks on peg 0 (largest to smallest: N, N-1, ..., 1)
        self.pegs: List[List[int]] = [
            list(range(n_disks, 0, -1)),  # Peg 0: [N, N-1, ..., 2, 1]
            [],                            # Peg 1: empty
            []                             # Peg 2: empty
        ]
        self.history: List[Tuple[int, int, int]] = []
        self.num_moves: int = 0
        self.is_solved: bool = False

    def get_state(self) -> List[List[int]]:
        """
        Get the current state of the pegs.

        Returns:
            Deep copy of the current peg configuration
        """
        return deepcopy(self.pegs)

    def get_top_disk(self, peg: int) -> Optional[int]:
        """
        Get the topmost disk on a peg.

        Args:
            peg: Peg number (0, 1, or 2)

        Returns:
            Disk number if peg is not empty, None otherwise
        """
        if 0 <= peg <= 2 and self.pegs[peg]:
            return self.pegs[peg][-1]
        return None

    def check_solved(self) -> bool:
        """
        Check if the puzzle is in a solved state.

        Returns:
            True if all disks are on peg 2 in correct order
        """
        # Solved when all disks are on peg 2
        if len(self.pegs[2]) == self.n_disks:
            # Verify correct ordering (largest to smallest: N, N-1, ..., 1)
            expected = list(range(self.n_disks, 0, -1))
            return self.pegs[2] == expected
        return False

    def apply_move(self, disk: int, from_peg: int, to_peg: int) -> Tuple[bool, str]:
        """
        Apply a move to the current state after validation.

        Args:
            disk: Disk number to move
            from_peg: Source peg (0, 1, or 2)
            to_peg: Destination peg (0, 1, or 2)

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Validate the move
        is_valid, error_msg = self._validate_move(disk, from_peg, to_peg)

        if not is_valid:
            return False, error_msg

        # Apply the move
        self.pegs[from_peg].pop()
        self.pegs[to_peg].append(disk)

        # Update history and counter
        self.history.append((disk, from_peg, to_peg))
        self.num_moves += 1

        # Check if puzzle is solved
        self.is_solved = self.check_solved()

        return True, "Move applied successfully"

    def _validate_move(self, disk: int, from_peg: int, to_peg: int) -> Tuple[bool, str]:
        """
        Validate a move according to Tower of Hanoi rules.

        Args:
            disk: Disk number to move
            from_peg: Source peg (0, 1, or 2)
            to_peg: Destination peg (0, 1, or 2)

        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        # Check if pegs are valid
        if from_peg not in [0, 1, 2]:
            return False, f"Invalid source peg: {from_peg}. Must be 0, 1, or 2."

        if to_peg not in [0, 1, 2]:
            return False, f"Invalid destination peg: {to_peg}. Must be 0, 1, or 2."

        if from_peg == to_peg:
            return False, "Source and destination pegs must be different."

        # Check if source peg is not empty
        if not self.pegs[from_peg]:
            return False, f"Source peg {from_peg} is empty."

        # Check if the disk is the topmost on the source peg
        top_disk = self.pegs[from_peg][-1]
        if top_disk != disk:
            return False, f"Disk {disk} is not on top of peg {from_peg}. Top disk is {top_disk}."

        # Check if the disk exists in the puzzle
        if disk < 1 or disk > self.n_disks:
            return False, f"Invalid disk number: {disk}. Must be between 1 and {self.n_disks}."

        # Check size ordering constraint (can't place larger disk on smaller disk)
        if self.pegs[to_peg]:
            target_top = self.pegs[to_peg][-1]
            if disk > target_top:
                return False, f"Cannot place disk {disk} on top of smaller disk {target_top}."

        return True, ""

    def reset(self):
        """Reset the puzzle to initial state."""
        self.pegs = [
            list(range(self.n_disks, 0, -1)),
            [],
            []
        ]
        self.history = []
        self.num_moves = 0
        self.is_solved = False

    def __str__(self) -> str:
        """String representation of the current state."""
        return (
            f"Tower of Hanoi State (N={self.n_disks}):\n"
            f"Pegs: {self.pegs}\n"
            f"Moves: {self.num_moves}\n"
            f"Solved: {self.is_solved}"
        )

    def display(self):
        """Display a visual representation of the current state."""
        print("\n" + "="*50)
        print(f"Tower of Hanoi - {self.n_disks} disks")
        print("="*50)
        print(f"Pegs (bottom → top):")
        for i, peg in enumerate(self.pegs):
            peg_display = str(peg) if peg else "[]"
            print(f"  Peg {i}: {peg_display}")
        print(f"\nTotal moves: {self.num_moves}")
        print(f"Solved: {'Yes' if self.is_solved else 'No'}")
        print("="*50 + "\n")
