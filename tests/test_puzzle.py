"""Tests for Lights Out puzzle solver."""

import pytest
from src.puzzle.lights_out import LightsOutSolver


def test_solve_simple_puzzle():
    """Test solving a simple puzzle."""
    solver = LightsOutSolver(size=3)
    # Simple puzzle: single light on in center
    grid = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]

    solution = solver.solve(grid)
    assert solution is not None
    assert len(solution) > 0


def test_solve_generated_puzzle():
    """Test solving a randomly generated puzzle."""
    solver = LightsOutSolver(size=3)
    puzzle = solver.generate_random_puzzle(seed=123)

    solution = solver.solve(puzzle)
    assert solution is not None

    # Verify solution works
    current = puzzle
    for move in solution:
        current = solver.apply_move(current, move[0], move[1])

    assert solver.is_solved(current)


def test_is_solved():
    """Test puzzle completion detection."""
    solver = LightsOutSolver(size=3)

    solved = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    unsolved = [[1, 0, 0], [0, 0, 0], [0, 0, 0]]

    assert solver.is_solved(solved)
    assert not solver.is_solved(unsolved)


def test_apply_move():
    """Test move application."""
    solver = LightsOutSolver(size=3)
    grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    # Press center
    result = solver.apply_move(grid, 1, 1)

    # Center and 4 neighbors should be on
    assert result[1][1] == 1
    assert result[0][1] == 1
    assert result[2][1] == 1
    assert result[1][0] == 1
    assert result[1][2] == 1
    # Corners should be off
    assert result[0][0] == 0


def test_print_grid():
    """Test grid visualization."""
    solver = LightsOutSolver(size=3)
    grid = [[1, 0, 1], [0, 1, 0], [1, 0, 1]]

    output = solver.print_grid(grid)
    assert "█" in output
    assert "░" in output
    assert len(output.split("\n")) == 3
