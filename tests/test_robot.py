"""Tests for robot controller."""

import pytest
from src.robot.controller import RobotController, Position, Direction


def test_robot_spawn():
    """Test robot spawning."""
    controller = RobotController((5, 5), [Position(2, 2)])
    state = controller.spawn(Position(0, 0), Direction.NORTH)
    
    assert state.position.x == 0
    assert state.position.y == 0
    assert state.direction == Direction.NORTH
    assert len(state.trail) == 1


def test_robot_move():
    """Test robot movement."""
    controller = RobotController((5, 5), [Position(2, 2)])
    controller.spawn(Position(0, 0), Direction.NORTH)
    
    state = controller.move(Direction.EAST)
    assert state.position.x == 1
    assert state.position.y == 0
    assert state.energy == 99.0


def test_invalid_move():
    """Test invalid movement detection."""
    controller = RobotController((3, 3), [Position(1, 1)])
    controller.spawn(Position(0, 0), Direction.NORTH)
    
    with pytest.raises(ValueError):
        controller.move(Direction.WEST)  # Out of bounds


def test_pathfinding():
    """Test pathfinding to target."""
    controller = RobotController((5, 5), [Position(4, 4)])
    controller.spawn(Position(0, 0), Direction.NORTH)
    
    target = Position(3, 3)
    path = controller.get_path_to(target)
    
    assert len(path) == 6  # 3 east + 3 south
    
    # Follow path
    for direction in path:
        controller.move(direction)
    
    assert controller.state.position == target


def test_checkpoint_detection():
    """Test checkpoint detection."""
    checkpoint = Position(2, 2)
    controller = RobotController((5, 5), [checkpoint])
    controller.spawn(Position(2, 2), Direction.NORTH)
    
    assert controller.check_checkpoint()
    
    controller.solve_checkpoint()
    assert not controller.check_checkpoint()


def test_trail_visualization():
    """Test trail visualization."""
    controller = RobotController((5, 5), [Position(4, 4)])
    controller.spawn(Position(0, 0), Direction.NORTH)
    
    controller.move(Direction.EAST)
    controller.move(Direction.EAST)
    
    viz = controller.get_trail_visualization()
    assert "N" in viz  # Current position
    assert "+" in viz  # Trail
    assert "C" in viz  # Checkpoint
