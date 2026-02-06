"""Lights Out puzzle solver."""

from typing import List, Tuple, Optional
import numpy as np


class LightsOutSolver:
    """Solver for Lights Out puzzle using linear algebra over GF(2)."""
    
    def __init__(self, size: int = 3):
        """Initialize solver with grid size.
        
        Args:
            size: Grid size (default 3x3)
        """
        self.size = size
        self.n = size * size
        
    def _pos_to_idx(self, row: int, col: int) -> int:
        """Convert 2D position to 1D index."""
        return row * self.size + col
    
    def _idx_to_pos(self, idx: int) -> Tuple[int, int]:
        """Convert 1D index to 2D position."""
        return idx // self.size, idx % self.size
    
    def _build_transition_matrix(self) -> np.ndarray:
        """Build transition matrix for the puzzle.
        
        Returns:
            n x n matrix where pressing cell i toggles cell j
        """
        A = np.zeros((self.n, self.n), dtype=int)
        
        for i in range(self.n):
            row, col = self._idx_to_pos(i)
            # Pressing cell toggles itself and neighbors
            toggles = [(row, col)]
            if row > 0:
                toggles.append((row - 1, col))
            if row < self.size - 1:
                toggles.append((row + 1, col))
            if col > 0:
                toggles.append((row, col - 1))
            if col < self.size - 1:
                toggles.append((row, col + 1))
            
            for r, c in toggles:
                j = self._pos_to_idx(r, c)
                A[i, j] = 1
        
        return A
    
    def solve(self, grid: List[List[int]]) -> Optional[List[Tuple[int, int]]]:
        """Solve Lights Out puzzle.
        
        Args:
            grid: Initial grid state (0=off, 1=on)
            
        Returns:
            List of (row, col) positions to press, or None if unsolvable
        """
        # Convert grid to vector
        b = np.array(grid, dtype=int).flatten()
        A = self._build_transition_matrix()
        
        # Solve Ax = b over GF(2) using Gaussian elimination
        solution = self._solve_gf2(A, b)
        
        if solution is None:
            return None
        
        # Convert solution to list of positions
        moves = []
        for i, press in enumerate(solution):
            if press == 1:
                moves.append(self._idx_to_pos(i))
        
        return moves
    
    def _solve_gf2(self, A: np.ndarray, b: np.ndarray) -> Optional[np.ndarray]:
        """Solve linear system over GF(2) using Gaussian elimination.
        
        Args:
            A: Coefficient matrix
            b: Right-hand side vector
            
        Returns:
            Solution vector or None if no solution
        """
        n = len(b)
        # Augmented matrix
        M = np.hstack([A, b.reshape(-1, 1)]).astype(int)
        
        # Forward elimination
        row = 0
        for col in range(n):
            # Find pivot
            pivot = None
            for r in range(row, n):
                if M[r, col] == 1:
                    pivot = r
                    break
            
            if pivot is None:
                continue
            
            # Swap rows
            M[[row, pivot]] = M[[pivot, row]]
            
            # Eliminate
            for r in range(n):
                if r != row and M[r, col] == 1:
                    M[r] = (M[r] + M[row]) % 2
            
            row += 1
        
        # Check for inconsistency
        for r in range(row, n):
            if M[r, -1] == 1 and np.all(M[r, :-1] == 0):
                return None
        
        # Back substitution
        x = np.zeros(n, dtype=int)
        for i in range(n):
            if i < row:
                # Find the pivot column
                pivot_col = np.where(M[i, :-1] == 1)[0]
                if len(pivot_col) > 0:
                    x[pivot_col[0]] = M[i, -1]
        
        return x
    
    def apply_move(self, grid: List[List[int]], row: int, col: int) -> List[List[int]]:
        """Apply a move to the grid (toggle cell and neighbors).
        
        Args:
            grid: Current grid state
            row: Row of cell to press
            col: Column of cell to press
            
        Returns:
            New grid state
        """
        new_grid = [row[:] for row in grid]  # Deep copy
        
        # Toggle cell and neighbors
        toggles = [(row, col)]
        if row > 0:
            toggles.append((row - 1, col))
        if row < self.size - 1:
            toggles.append((row + 1, col))
        if col > 0:
            toggles.append((row, col - 1))
        if col < self.size - 1:
            toggles.append((row, col + 1))
        
        for r, c in toggles:
            new_grid[r][c] = 1 - new_grid[r][c]
        
        return new_grid
    
    def is_solved(self, grid: List[List[int]]) -> bool:
        """Check if puzzle is solved (all lights off).
        
        Args:
            grid: Grid state to check
            
        Returns:
            True if all lights are off
        """
        return all(cell == 0 for row in grid for cell in row)
    
    def generate_random_puzzle(self, seed: Optional[int] = None) -> List[List[int]]:
        """Generate a random solvable puzzle.
        
        Args:
            seed: Random seed for reproducibility
            
        Returns:
            Random grid state
        """
        if seed is not None:
            np.random.seed(seed)
        
        # Start from solved state and apply random moves
        grid = [[0] * self.size for _ in range(self.size)]
        
        num_moves = np.random.randint(1, self.n + 1)
        for _ in range(num_moves):
            row = np.random.randint(0, self.size)
            col = np.random.randint(0, self.size)
            grid = self.apply_move(grid, row, col)
        
        return grid
    
    def print_grid(self, grid: List[List[int]]) -> str:
        """Pretty print grid for debugging.
        
        Args:
            grid: Grid state
            
        Returns:
            String representation
        """
        lines = []
        for row in grid:
            lines.append(" ".join("█" if cell else "░" for cell in row))
        return "\n".join(lines)
