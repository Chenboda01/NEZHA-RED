"""Poetry generation inspired by Nezha mythology."""

import random
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RobotExperience:
    """Experience data for poem generation."""
    path_length: int
    checkpoints_solved: int
    turns_made: int
    puzzle_type: str
    energy_remaining: float


class PoetryGenerator:
    """Generate poetry based on robot experiences."""
    
    # Nezha-inspired poetic fragments
    OPENINGS = [
        "The Wind Fire Wheels ignite,",
        "Through crimson grids I trace my path,",
        "On lotus-born metallic feet,",
        "The Universe Ring spins bright,",
        "In neon red, I find my truth,",
    ]
    
    MIDDLE_LINES = [
        "each checkpoint a trial of mind and steel,",
        "puzzles unfold like ancient scrolls,",
        "my trail burns through the digital night,",
        "solving riddles born of light,",
        "the grid speaks in binary tongues,",
    ]
    
    CLOSINGS = [
        "and from chaos, melody rises.",
        "a techno-poet's song takes flight.",
        "the Red Boy's spirit lives in code.",
        "wisdom found in circuits cold.",
        "Nezha rides again, reborn.",
    ]
    
    # Specific references for different experiences
    PUZZLE_LINES = {
        "lights_out": [
            "Lights flicker and die, then rise,",
            "in darkness, I find the switch,",
            "illuminating the unseen path,",
        ],
        "logic": [
            "Logic gates open and close,",
            "truth tables reveal the way,",
            "in boolean beauty, I proceed,",
        ],
        "math": [
            "Equations dance like fire,",
            "numbers sing their secret song,",
            "calculations birth new paths,",
        ],
    }
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize poetry generator.
        
        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
    
    def generate(self, experience: RobotExperience) -> str:
        """Generate a poem based on robot experience.
        
        Args:
            experience: Robot experience data
            
        Returns:
            Generated poem as string
        """
        lines = []
        
        # Opening
        lines.append(random.choice(self.OPENINGS))
        
        # Experience-specific middle
        if experience.puzzle_type in self.PUZZLE_LINES:
            lines.append(random.choice(self.PUZZLE_LINES[experience.puzzle_type]))
        else:
            lines.append(random.choice(self.MIDDLE_LINES))
        
        # Path/traversal line
        if experience.turns_made > 3:
            lines.append(f"turning {experience.turns_made} times through the maze,")
        elif experience.path_length > 5:
            lines.append(f"walking {experience.path_length} steps into the unknown,")
        else:
            lines.append("swift and sure, the short way home,")
        
        # Energy/state line
        if experience.energy_remaining > 80:
            lines.append("vital and strong, the quest continues,")
        elif experience.energy_remaining > 40:
            lines.append("strength fading but spirit holds,")
        else:
            lines.append("tired circuits yearn for rest,")
        
        # Closing
        lines.append(random.choice(self.CLOSINGS))
        
        # Title based on checkpoint
        title = f"Scroll of Sector {experience.checkpoints_solved}"
        
        poem = f"{title}\n{'=' * len(title)}\n" + "\n".join(lines)
        poem += f"\n\n- Written at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return poem
    
    def save_to_file(self, experience: RobotExperience, filepath: str) -> None:
        """Save generated poem to file.
        
        Args:
            experience: Robot experience data
            filepath: Path to save file
        """
        poem = self.generate(experience)
        with open(filepath, "w") as f:
            f.write(poem)
