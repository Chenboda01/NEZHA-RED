"""Robot controller for grid navigation."""

from typing import List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class Direction(Enum):
    """Cardinal directions for robot movement."""

    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)


@dataclass
class Position:
    """Grid position with x, y coordinates."""

    x: int
    y: int

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def move(self, direction: Direction) -> "Position":
        """Return new position after moving in direction."""
        dx, dy = direction.value
        return Position(self.x + dx, self.y + dy)

    def manhattan_distance(self, other: "Position") -> int:
        """Calculate Manhattan distance to another position."""
        return abs(self.x - other.x) + abs(self.y - other.y)


@dataclass
class RobotState:
    """Current state of the robot."""

    position: Position
    direction: Direction = Direction.NORTH
    energy: float = 100.0
    trail: List[Position] = field(default_factory=list)
    checkpoints_solved: Set[Position] = field(default_factory=set)

    def __post_init__(self):
        if not self.trail:
            self.trail = [self.position]


class RobotController:
    """Controller for robot navigation in grid world."""

    def __init__(self, grid_size: Tuple[int, int], checkpoints: List[Position]):
        """Initialize robot controller.

        Args:
            grid_size: (width, height) of the grid world
            checkpoints: List of positions requiring puzzle solving
        """
        self.grid_width, self.grid_height = grid_size
        self.checkpoints = set(checkpoints)
        self.state: Optional[RobotState] = None

    def spawn(
        self, start_pos: Position, direction: Direction = Direction.NORTH
    ) -> RobotState:
        """Spawn robot at starting position.

        Args:
            start_pos: Initial position
            direction: Initial facing direction

        Returns:
            RobotState at spawn
        """
        self.state = RobotState(position=start_pos, direction=direction)
        return self.state

    def is_valid_position(self, pos: Position) -> bool:
        """Check if position is within grid bounds."""
        return 0 <= pos.x < self.grid_width and 0 <= pos.y < self.grid_height

    def get_path_to(self, target: Position) -> List[Direction]:
        """Calculate path to target using BFS.

        Args:
            target: Destination position

        Returns:
            List of directions to reach target
        """
        if not self.state:
            raise RuntimeError("Robot not spawned")

        from collections import deque

        start = self.state.position
        if start == target:
            return []

        queue = deque([(start, [])])
        visited = {start}

        while queue:
            current, path = queue.popleft()

            for direction in Direction:
                next_pos = current.move(direction)

                if next_pos in visited or not self.is_valid_position(next_pos):
                    continue

                new_path = path + [direction]

                if next_pos == target:
                    return new_path

                visited.add(next_pos)
                queue.append((next_pos, new_path))

        return []

    def move(self, direction: Direction) -> RobotState:
        """Move robot in given direction.

        Args:
            direction: Direction to move

        Returns:
            Updated robot state
        """
        if not self.state:
            raise RuntimeError("Robot not spawned")

        self.state.direction = direction
        new_pos = self.state.position.move(direction)

        if not self.is_valid_position(new_pos):
            raise ValueError(f"Invalid move: {new_pos} is out of bounds")

        self.state.position = new_pos
        self.state.trail.append(new_pos)
        self.state.energy -= 1.0

        return self.state

    def check_checkpoint(self) -> bool:
        """Check if current position is an unsolved checkpoint.

        Returns:
            True if at unsolved checkpoint
        """
        if not self.state:
            return False

        pos = self.state.position
        return pos in self.checkpoints and pos not in self.state.checkpoints_solved

    def solve_checkpoint(self) -> None:
        """Mark current checkpoint as solved."""
        if not self.state:
            raise RuntimeError("Robot not spawned")

        self.state.checkpoints_solved.add(self.state.position)

    def get_trail_visualization(self) -> str:
        """Get ASCII visualization of robot trail.

        Returns:
            String representation of grid with trail
        """
        grid = [["." for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        # Draw checkpoints
        for cp in self.checkpoints:
            if self.is_valid_position(cp):
                grid[cp.y][cp.x] = "C"

        # Draw trail with red neon aesthetic
        if self.state:
            for i, pos in enumerate(self.state.trail):
                if self.is_valid_position(pos):
                    symbol = "N" if i == len(self.state.trail) - 1 else "+"
                    grid[pos.y][pos.x] = symbol

        return "\n".join(" ".join(row) for row in grid)
