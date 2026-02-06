"""MIDI music generation from robot paths and puzzle states."""

from typing import List, Optional
from dataclasses import dataclass
from midiutil import MIDIFile


@dataclass
class MusicParameters:
    """Parameters for music generation."""
    tempo: int = 120
    base_pitch: int = 60  # Middle C
    velocity: int = 80
    track: int = 0
    channel: int = 0


class MIDIGenerator:
    """Generate MIDI files from robot experiences."""
    
    # Scale mappings for different moods
    SCALES = {
        "major": [0, 2, 4, 5, 7, 9, 11],  # C major
        "minor": [0, 2, 3, 5, 7, 8, 10],  # C minor
        "pentatonic": [0, 2, 4, 7, 9],    # C pentatonic
        "tragic": [0, 1, 4, 5, 7, 8, 11], # Phrygian dominant
    }
    
    def __init__(self, params: Optional[MusicParameters] = None):
        """Initialize MIDI generator.
        
        Args:
            params: Music parameters (uses defaults if None)
        """
        self.params = params or MusicParameters()
        self.midi = MIDIFile(1)
        self.midi.addTempo(
            self.params.track,
            0,
            self.params.tempo
        )
    
    def generate_from_path(
        self,
        path_length: int,
        num_turns: int,
        energy_used: float,
        scale: str = "pentatonic",
        filename: Optional[str] = None
    ) -> bytes:
        """Generate MIDI from robot path characteristics.
        
        Args:
            path_length: Number of steps taken
            num_turns: Number of direction changes
            energy_used: Energy consumed
            scale: Scale to use for melody
            filename: Optional filename to save
            
        Returns:
            MIDI file as bytes
        """
        # Map characteristics to musical parameters
        tempo = max(60, min(200, self.params.tempo + path_length))
        velocity = max(40, min(127, int(self.params.velocity - energy_used)))
        
        # Generate melody based on path
        scale_intervals = self.SCALES.get(scale, self.SCALES["pentatonic"])
        
        time = 0
        duration = max(0.5, 2.0 - (num_turns * 0.1))
        
        for i in range(min(path_length, 32)):  # Max 32 notes
            # Map step to pitch in scale
            scale_idx = i % len(scale_intervals)
            octave = i // len(scale_intervals)
            pitch = self.params.base_pitch + (octave * 12) + scale_intervals[scale_idx]
            
            # Add variation based on turns
            if i < num_turns:
                pitch += 7  # Jump on turns
            
            pitch = max(0, min(127, pitch))
            
            self.midi.addNote(
                self.params.track,
                self.params.channel,
                pitch,
                time,
                duration,
                velocity
            )
            
            time += duration
        
        if filename:
            with open(filename, "wb") as f:
                self.midi.writeFile(f)
        
        return self._to_bytes()
    
    def generate_from_puzzle(
        self,
        grid_states: List[List[List[int]]],
        moves: List[tuple],
        filename: Optional[str] = None
    ) -> bytes:
        """Generate MIDI from puzzle solving process.
        
        Args:
            grid_states: Sequence of grid states during solving
            moves: List of moves made
            filename: Optional filename to save
            
        Returns:
            MIDI file as bytes
        """
        time = 0
        
        for i, (state, move) in enumerate(zip(grid_states, moves)):
            # Count lights on
            lights_on = sum(sum(row) for row in state)
            
            # Map to musical parameters
            pitch = self.params.base_pitch + lights_on
            velocity = 60 + (lights_on * 10)
            duration = 1.0
            
            self.midi.addNote(
                self.params.track,
                self.params.channel,
                min(127, pitch),
                time,
                duration,
                min(127, velocity)
            )
            
            # Add chord for move position
            row, col = move
            chord_root = self.params.base_pitch + (row * 3) + col
            self._add_chord(chord_root, time, duration * 0.5, velocity - 20)
            
            time += duration
        
        if filename:
            with open(filename, "wb") as f:
                self.midi.writeFile(f)
        
        return self._to_bytes()
    
    def _add_chord(
        self,
        root: int,
        time: float,
        duration: float,
        velocity: int
    ) -> None:
        """Add a triad chord.
        
        Args:
            root: Root note pitch
            time: Start time
            duration: Note duration
            velocity: Note velocity
        """
        # Major triad: root, major third, perfect fifth
        chord = [root, root + 4, root + 7]
        
        for pitch in chord:
            if 0 <= pitch <= 127:
                self.midi.addNote(
                    self.params.track,
                    self.params.channel,
                    pitch,
                    time,
                    duration,
                    max(0, velocity)
                )
    
    def _to_bytes(self) -> bytes:
        """Convert MIDI file to bytes.
        
        Returns:
            MIDI data as bytes
        """
        import io
        buffer = io.BytesIO()
        self.midi.writeFile(buffer)
        return buffer.getvalue()
