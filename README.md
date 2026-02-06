Project NEZHA-RED: The Techno-Poet Robot Lab

A red-neon TRON arena where Nezha-inspired robot learns, explores, solves math/logic/science puzzels, reads ancient poetry, and converts its experiences into piano music.


This is not a toy.
This becomes a robotics + algorithms + art + storytelling playground.

The Gameplay / System Loop
1. Robot spawns in a red grid world.
2. To move forward, it must solve:

    a logic puzzle
    a math/science calibration task

3. Solving improves its controller / planner.
4. It discovers a poetry scroll.
5. It prints a poem about what just happened. 
6. The solution path is converted into a piano melody.
7. Visual red trails draws the "Wind Fire Wheels" of Nezha.
8. Repeat, with harder challenges.

Music Engine (MIDI)

Every solution becomes music.


Mapping examples:
    Path length -> tempo
    Turns -> note changes
    Puzzle states -> chords
    Energy used -> dynamics 

This is a MIDI file for every mission.

Installation:

Create Makefile:
install:
	pip install -r requirements.txt
run:
	python demos/main_demo.py
test:
	pytest
.PHONY: install run test
Then: make install && make run

Running the First Demo

Run on startup:

1. python demos/main_demo.py

You will see: 

1. Robot navigate to a puzzle node
2. Solve a Lights Out puzzle
3. Unlock the next sector
4. Print a poem
5. Generate a MIDI performance

This will be using a github repository. It will be visible in [github repository](https://github.com/Chenboda01/NEZHA-RED)
Github repository:

Main, root branch.

AODS - Always On Display Screensaver

AODS (Always On Display Screensaver) is a built-in screensaver feature for NEZHA-RED that activates when the system is idle.

Features:
- Automatic activation after configurable idle time (default: 15 minutes)
- Real-time clock display
- User statistics display
- Custom image support
- One-click preview mode
- Fully configurable settings

Usage:
1. Click the "⚡ AODS" button in the main interface to open settings
2. Configure activation time, custom images, and display options
3. Use the "Preview AODS" button to test your settings
4. Press any key or move your mouse to exit the screensaver

Configuration:
- Activation time: 10, 15, 20 minutes or custom (1-120 minutes)
- Display options: Show/Hide clock and user stats
- Custom image: Supports PNG, JPG, JPEG, GIF, BMP formats 



