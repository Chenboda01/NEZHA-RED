"""Interactive GUI demo for NEZHA-RED robot game with user authentication."""

import sys
import os
import tkinter as tk
from tkinter import messagebox, font
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.robot.controller import RobotController, Position, Direction
from src.puzzle.lights_out import LightsOutSolver
from src.music.midi_generator import MIDIGenerator, MusicParameters
from src.poetry.generator import PoetryGenerator, RobotExperience
from demos.user_manager import UserManager, UserProfile
from demos.aods_manager import AODSManager


class LoginScreen:
    """Login and account creation screen."""
    
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.user_manager = UserManager()
        
        # Colors (Red Neon TRON aesthetic)
        self.colors = {
            'bg': '#1a0000',
            'grid': '#ff0040',
            'robot': '#ff1a66',
            'text': '#ff99bb',
            'button': '#cc0033',
            'button_fg': '#ffffff',
            'input_bg': '#330000',
            'success': '#00ff66',
            'error': '#ff0040'
        }
        
        self.setup_ui()
        
        # Try auto-login
        if self.user_manager.try_auto_login():
            username = self.user_manager.get_current_username()
            messagebox.showinfo(
                "Welcome Back!",
                f"Auto-logged in as: {username}"
            )
            self.on_login_success(self.user_manager)
    
    def setup_ui(self):
        """Setup the login UI."""
        self.root.title("NEZHA-RED - Login")
        self.root.configure(bg=self.colors['bg'])
        self.root.geometry("500x600")
        
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(padx=30, pady=30, fill=tk.BOTH, expand=True)
        
        # Title
        title_font = font.Font(family='Courier', size=24, weight='bold')
        title = tk.Label(
            main_frame,
            text="NEZHA-RED",
            font=title_font,
            fg=self.colors['grid'],
            bg=self.colors['bg']
        )
        title.pack(pady=10)
        
        subtitle = tk.Label(
            main_frame,
            text="The Techno-Poet Robot Lab",
            font=('Courier', 12),
            fg=self.colors['text'],
            bg=self.colors['bg']
        )
        subtitle.pack(pady=5)
        
        # Separator
        separator = tk.Frame(main_frame, height=2, bg=self.colors['grid'])
        separator.pack(fill=tk.X, pady=20)
        
        # Username
        user_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        user_frame.pack(pady=10, fill=tk.X)
        
        user_label = tk.Label(
            user_frame,
            text="Username:",
            font=('Courier', 12),
            fg=self.colors['text'],
            bg=self.colors['bg'],
            width=12,
            anchor='w'
        )
        user_label.pack(side=tk.LEFT)
        
        self.username_entry = tk.Entry(
            user_frame,
            font=('Courier', 12),
            bg=self.colors['input_bg'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief=tk.FLAT,
            width=25
        )
        self.username_entry.pack(side=tk.LEFT, padx=10)
        self.username_entry.focus()
        
        # Password
        pass_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        pass_frame.pack(pady=10, fill=tk.X)
        
        pass_label = tk.Label(
            pass_frame,
            text="Password:",
            font=('Courier', 12),
            fg=self.colors['text'],
            bg=self.colors['bg'],
            width=12,
            anchor='w'
        )
        pass_label.pack(side=tk.LEFT)
        
        self.password_entry = tk.Entry(
            pass_frame,
            font=('Courier', 12),
            bg=self.colors['input_bg'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief=tk.FLAT,
            width=25,
            show="*"
        )
        self.password_entry.pack(side=tk.LEFT, padx=10)
        
        # Show password checkbox
        self.show_pass_var = tk.BooleanVar()
        show_pass_cb = tk.Checkbutton(
            main_frame,
            text="Show Password",
            variable=self.show_pass_var,
            command=self.toggle_password_visibility,
            font=('Courier', 9),
            fg=self.colors['text'],
            bg=self.colors['bg'],
            selectcolor=self.colors['input_bg'],
            activebackground=self.colors['bg'],
            activeforeground=self.colors['text']
        )
        show_pass_cb.pack(pady=5)
        
        # Message label
        self.message_label = tk.Label(
            main_frame,
            text="",
            font=('Courier', 10),
            fg=self.colors['text'],
            bg=self.colors['bg'],
            wraplength=400
        )
        self.message_label.pack(pady=10)
        
        # Buttons frame
        btn_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        
        btn_font = ('Courier', 12, 'bold')
        
        # Login button
        login_btn = tk.Button(
            btn_frame,
            text="LOGIN",
            font=btn_font,
            bg=self.colors['button'],
            fg=self.colors['button_fg'],
            width=15,
            command=self.login
        )
        login_btn.pack(pady=5)
        
        # Create Account button
        create_btn = tk.Button(
            btn_frame,
            text="CREATE ACCOUNT",
            font=btn_font,
            bg=self.colors['grid'],
            fg=self.colors['button_fg'],
            width=15,
            command=self.create_account
        )
        create_btn.pack(pady=5)
        
        # Exit button
        exit_btn = tk.Button(
            btn_frame,
            text="EXIT",
            font=btn_font,
            bg='#660000',
            fg=self.colors['button_fg'],
            width=15,
            command=self.root.quit
        )
        exit_btn.pack(pady=5)
        
        # Status
        self.status_label = tk.Label(
            main_frame,
            text=f"Users registered: {len(self.user_manager.users)}",
            font=('Courier', 9),
            fg=self.colors['text'],
            bg=self.colors['bg']
        )
        self.status_label.pack(pady=10)
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.login())
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.login())
    
    def toggle_password_visibility(self):
        """Toggle password visibility."""
        if self.show_pass_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
    
    def login(self):
        """Attempt login."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.show_message("Please enter both username and password", error=True)
            return
        
        success, message = self.user_manager.login(username, password)
        
        if success:
            self.show_message(message, error=False)
            self.root.after(1000, lambda: self.on_login_success(self.user_manager))
        else:
            self.show_message(message, error=True)
    
    def create_account(self):
        """Show create account dialog."""
        # Create account window
        account_window = tk.Toplevel(self.root)
        account_window.title("Create Account")
        account_window.configure(bg=self.colors['bg'])
        account_window.geometry("400x300")
        account_window.transient(self.root)
        account_window.grab_set()
        
        # Title
        title = tk.Label(
            account_window,
            text="CREATE NEW ACCOUNT",
            font=('Courier', 14, 'bold'),
            fg=self.colors['grid'],
            bg=self.colors['bg']
        )
        title.pack(pady=15)
        
        # Username
        user_frame = tk.Frame(account_window, bg=self.colors['bg'])
        user_frame.pack(pady=10, fill=tk.X, padx=20)
        
        tk.Label(
            user_frame,
            text="Username:",
            font=('Courier', 11),
            fg=self.colors['text'],
            bg=self.colors['bg'],
            width=12,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        new_user_entry = tk.Entry(
            user_frame,
            font=('Courier', 11),
            bg=self.colors['input_bg'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief=tk.FLAT,
            width=20
        )
        new_user_entry.pack(side=tk.LEFT, padx=10)
        new_user_entry.focus()
        
        # Password
        pass_frame = tk.Frame(account_window, bg=self.colors['bg'])
        pass_frame.pack(pady=10, fill=tk.X, padx=20)
        
        tk.Label(
            pass_frame,
            text="Password:",
            font=('Courier', 11),
            fg=self.colors['text'],
            bg=self.colors['bg'],
            width=12,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        new_pass_entry = tk.Entry(
            pass_frame,
            font=('Courier', 11),
            bg=self.colors['input_bg'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief=tk.FLAT,
            width=20,
            show="*"
        )
        new_pass_entry.pack(side=tk.LEFT, padx=10)
        
        # Confirm Password
        confirm_frame = tk.Frame(account_window, bg=self.colors['bg'])
        confirm_frame.pack(pady=10, fill=tk.X, padx=20)
        
        tk.Label(
            confirm_frame,
            text="Confirm:",
            font=('Courier', 11),
            fg=self.colors['text'],
            bg=self.colors['bg'],
            width=12,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        confirm_entry = tk.Entry(
            confirm_frame,
            font=('Courier', 11),
            bg=self.colors['input_bg'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief=tk.FLAT,
            width=20,
            show="*"
        )
        confirm_entry.pack(side=tk.LEFT, padx=10)
        
        # Message
        msg_label = tk.Label(
            account_window,
            text="",
            font=('Courier', 10),
            fg=self.colors['text'],
            bg=self.colors['bg'],
            wraplength=350
        )
        msg_label.pack(pady=10)
        
        def do_create():
            username = new_user_entry.get().strip()
            password = new_pass_entry.get()
            confirm = confirm_entry.get()
            
            if not username or not password:
                msg_label.config(text="Please fill in all fields", fg=self.colors['error'])
                return
            
            if password != confirm:
                msg_label.config(text="Passwords do not match!", fg=self.colors['error'])
                return
            
            success, message = self.user_manager.create_account(username, password)
            
            if success:
                msg_label.config(text=message, fg=self.colors['success'])
                account_window.after(1500, account_window.destroy)
                self.status_label.config(text=f"Users registered: {len(self.user_manager.users)}")
            else:
                msg_label.config(text=message, fg=self.colors['error'])
        
        # Buttons
        btn_frame = tk.Frame(account_window, bg=self.colors['bg'])
        btn_frame.pack(pady=15)
        
        tk.Button(
            btn_frame,
            text="CREATE",
            font=('Courier', 11, 'bold'),
            bg=self.colors['grid'],
            fg=self.colors['button_fg'],
            width=12,
            command=do_create
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="CANCEL",
            font=('Courier', 11, 'bold'),
            bg='#660000',
            fg=self.colors['button_fg'],
            width=12,
            command=account_window.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter
        new_user_entry.bind('<Return>', lambda e: new_pass_entry.focus())
        new_pass_entry.bind('<Return>', lambda e: confirm_entry.focus())
        confirm_entry.bind('<Return>', lambda e: do_create())
    
    def show_message(self, text, error=False):
        """Show message on login screen."""
        color = self.colors['error'] if error else self.colors['success']
        self.message_label.config(text=text, fg=color)


class NezhaGameGUI:
    """Interactive GUI for NEZHA-RED game."""
    
    def __init__(self, root, user_manager):
        self.root = root
        self.user_manager = user_manager
        self.root.title(f"NEZHA-RED - {self.user_manager.get_current_username()}")
        self.root.configure(bg='#1a0000')
        self.root.geometry("700x850")
        
        # Game state
        self.grid_size = (8, 8)
        self.cell_size = 60
        self.checkpoints = [Position(3, 3), Position(6, 6)]
        self.controller = RobotController(self.grid_size, self.checkpoints)
        self.current_puzzle = None
        self.puzzle_solver = None
        self.at_checkpoint = False
        self.puzzle_solved_flag = False
        
        # Spawn robot
        self.controller.spawn(Position(0, 0), Direction.NORTH)
        
        # Initialize AODS (Always On Display Screensaver)
        self.aods_manager = AODSManager(self.user_manager)
        
        # Colors
        self.colors = {
            'bg': '#1a0000',
            'grid': '#ff0040',
            'robot': '#ff1a66',
            'trail': '#ff3366',
            'checkpoint': '#ff0066',
            'checkpoint_solved': '#00ff66',
            'text': '#ff99bb',
            'button': '#cc0033',
            'button_fg': '#ffffff'
        }
        
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        # User info bar
        user_bar = tk.Frame(main_frame, bg='#330000', relief=tk.RIDGE, bd=1)
        user_bar.pack(fill=tk.X, pady=(0, 10))
        
        username = self.user_manager.get_current_username()
        self.user_label = tk.Label(
            user_bar,
            text=f"👤 {username}",
            font=('Courier', 10, 'bold'),
            fg=self.colors['text'],
            bg='#330000'
        )
        self.user_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Logout button
        logout_btn = tk.Button(
            user_bar,
            text="Logout",
            font=('Courier', 9),
            bg='#660000',
            fg=self.colors['button_fg'],
            command=self.logout
        )
        logout_btn.pack(side=tk.RIGHT, padx=10, pady=3)
        
        # Title
        title_font = font.Font(family='Courier', size=18, weight='bold')
        title = tk.Label(
            main_frame,
            text="NEZHA-RED: The Techno-Poet Robot Lab",
            font=title_font,
            fg=self.colors['grid'],
            bg=self.colors['bg']
        )
        title.pack(pady=5)
        
        # Grid canvas
        canvas_width = self.grid_size[0] * self.cell_size
        canvas_height = self.grid_size[1] * self.cell_size
        self.canvas = tk.Canvas(
            main_frame,
            width=canvas_width,
            height=canvas_height,
            bg=self.colors['bg'],
            highlightthickness=2,
            highlightbackground=self.colors['grid']
        )
        self.canvas.pack(pady=10)
        
        # Status frame
        status_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        status_frame.pack(pady=5, fill=tk.X)
        
        # Status labels
        self.status_labels = {}
        status_items = ['Position', 'Energy', 'Checkpoints', 'Status']
        for i, item in enumerate(status_items):
            label = tk.Label(
                status_frame,
                text=f"{item}: -",
                font=('Courier', 11),
                fg=self.colors['text'],
                bg=self.colors['bg']
            )
            label.grid(row=0, column=i, padx=15)
            self.status_labels[item] = label
        
        # Control buttons frame
        control_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        control_frame.pack(pady=5)
        
        # Direction buttons
        btn_frame = tk.Frame(control_frame, bg=self.colors['bg'])
        btn_frame.pack()
        
        btn_font = font.Font(family='Courier', size=12, weight='bold')
        
        # North button
        self.btn_north = tk.Button(
            btn_frame, text="↑ N",
            font=btn_font,
            bg=self.colors['button'],
            fg=self.colors['button_fg'],
            width=5,
            command=lambda: self.move_robot(Direction.NORTH)
        )
        self.btn_north.grid(row=0, column=1, pady=3)
        
        # West button
        self.btn_west = tk.Button(
            btn_frame, text="← W",
            font=btn_font,
            bg=self.colors['button'],
            fg=self.colors['button_fg'],
            width=5,
            command=lambda: self.move_robot(Direction.WEST)
        )
        self.btn_west.grid(row=1, column=0, padx=3)
        
        # Action button
        self.btn_action = tk.Button(
            btn_frame, text="SOLVE",
            font=btn_font,
            bg=self.colors['checkpoint'],
            fg=self.colors['button_fg'],
            width=7,
            command=self.solve_checkpoint,
            state=tk.DISABLED
        )
        self.btn_action.grid(row=1, column=1, padx=3)
        
        # East button
        self.btn_east = tk.Button(
            btn_frame, text="E →",
            font=btn_font,
            bg=self.colors['button'],
            fg=self.colors['button_fg'],
            width=5,
            command=lambda: self.move_robot(Direction.EAST)
        )
        self.btn_east.grid(row=1, column=2, padx=3)
        
        # South button
        self.btn_south = tk.Button(
            btn_frame, text="↓ S",
            font=btn_font,
            bg=self.colors['button'],
            fg=self.colors['button_fg'],
            width=5,
            command=lambda: self.move_robot(Direction.SOUTH)
        )
        self.btn_south.grid(row=2, column=1, pady=3)
        
        # Message display
        self.message_label = tk.Label(
            main_frame,
            text=f"Welcome {self.user_manager.get_current_username()}! Use arrows to move.",
            font=('Courier', 10),
            fg=self.colors['text'],
            bg=self.colors['bg'],
            wraplength=500
        )
        self.message_label.pack(pady=5)
        
        # Poetry display
        self.poetry_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        self.poetry_frame.pack(pady=5, fill=tk.X)
        
        self.poetry_label = tk.Label(
            self.poetry_frame,
            text="Poetry scrolls will appear here...",
            font=('Courier', 9, 'italic'),
            fg=self.colors['grid'],
            bg=self.colors['bg'],
            wraplength=500,
            justify=tk.LEFT
        )
        self.poetry_label.pack()
        
        # AODS Settings button
        aods_btn = tk.Button(
            main_frame,
            text="⚡ AODS",
            font=('Courier', 9),
            bg='#6600cc',
            fg=self.colors['button_fg'],
            width=10,
            command=self.open_aods_settings
        )
        aods_btn.pack(pady=3)
        
        # Help button
        help_btn = tk.Button(
            main_frame,
            text="? Help",
            font=('Courier', 9),
            bg=self.colors['button'],
            fg=self.colors['button_fg'],
            width=8,
            command=self.show_help
        )
        help_btn.pack(pady=5)
        
        # Bind keyboard
        self.root.bind('<Up>', lambda e: self.move_robot(Direction.NORTH))
        self.root.bind('<Down>', lambda e: self.move_robot(Direction.SOUTH))
        self.root.bind('<Left>', lambda e: self.move_robot(Direction.WEST))
        self.root.bind('<Right>', lambda e: self.move_robot(Direction.EAST))
        self.root.bind('<Return>', lambda e: self.solve_checkpoint() if self.at_checkpoint else None)
        
        # Start AODS monitoring
        self.aods_manager.start_monitoring(self.root)
    
    def draw_grid(self):
        """Draw the game grid."""
        self.canvas.delete("all")
        
        # Draw grid lines
        for i in range(self.grid_size[0] + 1):
            x = i * self.cell_size
            self.canvas.create_line(
                x, 0, x, self.grid_size[1] * self.cell_size,
                fill=self.colors['grid'], width=1
            )
        
        for i in range(self.grid_size[1] + 1):
            y = i * self.cell_size
            self.canvas.create_line(
                0, y, self.grid_size[0] * self.cell_size, y,
                fill=self.colors['grid'], width=1
            )
        
        # Draw checkpoints
        for i, cp in enumerate(self.checkpoints):
            x1 = cp.x * self.cell_size + 5
            y1 = cp.y * self.cell_size + 5
            x2 = (cp.x + 1) * self.cell_size - 5
            y2 = (cp.y + 1) * self.cell_size - 5
            
            color = self.colors['checkpoint_solved'] if self.controller.state and cp in self.controller.state.checkpoints_solved else self.colors['checkpoint']
            
            self.canvas.create_oval(
                x1, y1, x2, y2,
                fill=color,
                outline=self.colors['grid'],
                width=2
            )
            self.canvas.create_text(
                (x1 + x2) / 2, (y1 + y2) / 2,
                text=f"C{i+1}",
                fill=self.colors['button_fg'],
                font=('Courier', 9, 'bold')
            )
        
        # Draw trail
        if self.controller.state and self.controller.state.trail:
            for i in range(len(self.controller.state.trail) - 1):
                pos1 = self.controller.state.trail[i]
                pos2 = self.controller.state.trail[i + 1]
                
                x1 = (pos1.x + 0.5) * self.cell_size
                y1 = (pos1.y + 0.5) * self.cell_size
                x2 = (pos2.x + 0.5) * self.cell_size
                y2 = (pos2.y + 0.5) * self.cell_size
                
                intensity = max(0.3, 1.0 - (len(self.controller.state.trail) - i) * 0.05)
                trail_color = f'#{int(255*intensity):02x}{int(51*intensity):02x}{int(102*intensity):02x}'
                
                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill=trail_color,
                    width=4
                )
        
        # Draw robot
        if self.controller.state:
            pos = self.controller.state.position
            x1 = pos.x * self.cell_size + 10
            y1 = pos.y * self.cell_size + 10
            x2 = (pos.x + 1) * self.cell_size - 10
            y2 = (pos.y + 1) * self.cell_size - 10
            
            self.canvas.create_oval(
                x1, y1, x2, y2,
                fill=self.colors['robot'],
                outline='#ffffff',
                width=3
            )
            
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            arrow_map = {
                Direction.NORTH: (center_x, y1 + 5),
                Direction.SOUTH: (center_x, y2 - 5),
                Direction.EAST: (x2 - 5, center_y),
                Direction.WEST: (x1 + 5, center_y)
            }
            
            arrow_end = arrow_map.get(self.controller.state.direction, (center_x, y1 + 5))
            self.canvas.create_line(
                center_x, center_y,
                arrow_end[0], arrow_end[1],
                fill='#ffffff',
                width=3,
                arrow=tk.LAST
            )
    
    def update_display(self):
        """Update all display elements."""
        self.draw_grid()
        
        if self.controller.state:
            pos = self.controller.state.position
            self.status_labels['Position'].config(
                text=f"Position: ({pos.x}, {pos.y})"
            )
            self.status_labels['Energy'].config(
                text=f"Energy: {self.controller.state.energy:.0f}"
            )
            solved = len(self.controller.state.checkpoints_solved)
            total = len(self.checkpoints)
            self.status_labels['Checkpoints'].config(
                text=f"Checkpoints: {solved}/{total}"
            )
            
            self.at_checkpoint = self.controller.check_checkpoint()
            if self.at_checkpoint:
                self.status_labels['Status'].config(
                    text="Status: CHECKPOINT!",
                    fg=self.colors['checkpoint']
                )
                self.btn_action.config(state=tk.NORMAL)
                self.message_label.config(
                    text="Press SOLVE or Enter to unlock this checkpoint!",
                    fg=self.colors['checkpoint']
                )
            else:
                self.status_labels['Status'].config(
                    text="Status: Moving",
                    fg=self.colors['text']
                )
                self.btn_action.config(state=tk.DISABLED)
    
    def move_robot(self, direction):
        """Move robot in given direction."""
        try:
            self.controller.move(direction)
            self.update_display()
            
            if not self.at_checkpoint:
                assert self.controller.state is not None
                self.message_label.config(
                    text=f"Moved {direction.name}. Energy: {self.controller.state.energy:.0f}",
                    fg=self.colors['text']
                )
        except ValueError as e:
            self.message_label.config(
                text=f"Cannot move there! {str(e)}",
                fg=self.colors['checkpoint']
            )
    
    def solve_checkpoint(self):
        """Solve the current checkpoint puzzle."""
        if not self.at_checkpoint:
            return
        
        puzzle_window = tk.Toplevel(self.root)
        puzzle_window.title("Lights Out Puzzle")
        puzzle_window.configure(bg=self.colors['bg'])
        puzzle_window.transient(self.root)
        puzzle_window.grab_set()
        
        self.puzzle_solved_flag = False
        
        self.puzzle_solver = LightsOutSolver(size=3)
        self.current_puzzle = self.puzzle_solver.generate_random_puzzle(seed=random.randint(1, 1000))
        self.current_solution = self.puzzle_solver.solve(self.current_puzzle)
        
        # Info frame
        info_frame = tk.Frame(puzzle_window, bg=self.colors['bg'])
        info_frame.pack(pady=10)
        
        tk.Label(
            info_frame,
            text="LIGHTS OUT PUZZLE",
            font=('Courier', 13, 'bold'),
            fg=self.colors['grid'],
            bg=self.colors['bg']
        ).pack()
        
        tk.Label(
            info_frame,
            text="Click cells to toggle. Turn OFF all lights!",
            font=('Courier', 9),
            fg=self.colors['text'],
            bg=self.colors['bg']
        ).pack(pady=3)
        
        # Puzzle grid
        puzzle_frame = tk.Frame(puzzle_window, bg=self.colors['bg'])
        puzzle_frame.pack(pady=10)
        
        self.puzzle_buttons = []
        for row in range(3):
            btn_row = []
            for col in range(3):
                btn = tk.Button(
                    puzzle_frame,
                    width=3,
                    height=2,
                    font=('Courier', 12, 'bold'),
                    command=lambda r=row, c=col: self.toggle_puzzle_cell(r, c, puzzle_window)
                )
                btn.grid(row=row, column=col, padx=2, pady=2)
                btn_row.append(btn)
            self.puzzle_buttons.append(btn_row)
        
        self.update_puzzle_display()
        
        # Buttons
        tk.Button(
            puzzle_window,
            text="Auto-Solve",
            font=('Courier', 10),
            bg=self.colors['button'],
            fg=self.colors['button_fg'],
            command=lambda: self.auto_solve_puzzle(puzzle_window)
        ).pack(pady=5)
        
        self.puzzle_status = tk.Label(
            puzzle_window,
            text="Lights on: 5",
            font=('Courier', 10),
            fg=self.colors['text'],
            bg=self.colors['bg']
        )
        self.puzzle_status.pack(pady=5)
    
    def update_puzzle_display(self):
        """Update puzzle button colors."""
        if not self.current_puzzle:
            return
        
        for row in range(3):
            for col in range(3):
                btn = self.puzzle_buttons[row][col]
                if self.current_puzzle[row][col] == 1:
                    btn.config(bg=self.colors['checkpoint'], text="ON")
                else:
                    btn.config(bg=self.colors['bg'], text="OFF")
        
        lights_on = sum(sum(row) for row in self.current_puzzle)
        if hasattr(self, 'puzzle_status'):
            self.puzzle_status.config(text=f"Lights on: {lights_on}")
    
    def toggle_puzzle_cell(self, row, col, window):
        """Toggle a puzzle cell."""
        if self.puzzle_solved_flag:
            return
        
        assert self.current_puzzle is not None and self.puzzle_solver is not None
        
        self.current_puzzle = self.puzzle_solver.apply_move(
            self.current_puzzle, row, col
        )
        
        self.update_puzzle_display()
        self.root.update()
        
        if self.puzzle_solver.is_solved(self.current_puzzle):
            self.puzzle_solved_flag = True
            for btn_row in self.puzzle_buttons:
                for btn in btn_row:
                    btn.config(state=tk.DISABLED, bg=self.colors['checkpoint_solved'], text="✓")
            self.root.update()
            window.after(500, lambda: self.complete_puzzle(window))
    
    def auto_solve_puzzle(self, window):
        """Auto-solve the puzzle."""
        if self.current_solution and self.current_puzzle and self.puzzle_solver:
            for move in self.current_solution:
                self.current_puzzle = self.puzzle_solver.apply_move(
                    self.current_puzzle, move[0], move[1]
                )
                self.update_puzzle_display()
                self.root.update()
                self.root.after(300)
            
            self.complete_puzzle(window)
    
    def complete_puzzle(self, window):
        """Complete the puzzle and generate outputs."""
        window.destroy()
        
        self.controller.solve_checkpoint()
        
        assert self.controller.state is not None
        trail = self.controller.state.trail
        path_length = len(trail)
        
        turns = 0
        if len(trail) > 1:
            for i in range(1, len(trail)):
                prev, curr = trail[i-1], trail[i]
                if prev.x != curr.x and prev.y != curr.y:
                    turns += 1
        
        experience = RobotExperience(
            path_length=path_length,
            checkpoints_solved=len(self.controller.state.checkpoints_solved),
            turns_made=turns,
            puzzle_type="lights_out",
            energy_remaining=self.controller.state.energy
        )
        
        poet = PoetryGenerator(seed=random.randint(1, 1000))
        poem = poet.generate(experience)
        
        self.poetry_label.config(text=poem)
        
        try:
            os.makedirs("demos/output", exist_ok=True)
            music = MIDIGenerator(MusicParameters(tempo=140))
            checkpoint_num = len(self.controller.state.checkpoints_solved)
            midi_data = music.generate_from_path(
                path_length=path_length,
                num_turns=turns,
                energy_used=100 - experience.energy_remaining,
                scale="pentatonic",
                filename=f"demos/output/mission_{checkpoint_num}.mid"
            )
            
            poet.save_to_file(experience, f"demos/output/poem_{checkpoint_num}.txt")
            
            self.message_label.config(
                text=f"Checkpoint solved! Mission {checkpoint_num} complete!",
                fg=self.colors['checkpoint_solved']
            )
        except Exception as e:
            self.message_label.config(
                text=f"Checkpoint solved! (MIDI error: {e})",
                fg=self.colors['checkpoint_solved']
            )
        
        self.update_display()
        
        if len(self.controller.state.checkpoints_solved) == len(self.checkpoints):
            self.show_victory_screen()
    
    def show_victory_screen(self):
        """Show victory screen."""
        assert self.controller.state is not None
        
        # Update user stats
        trail = self.controller.state.trail
        total_distance = len(trail) - 1
        checkpoints_solved = len(self.controller.state.checkpoints_solved)
        
        # Calculate score (based on distance and energy)
        energy_remaining = self.controller.state.energy
        score = int((checkpoints_solved * 100) + (energy_remaining * 2) - (total_distance * 0.5))
        score = max(0, score)
        
        # Save stats
        self.user_manager.update_stats(
            checkpoints_solved=checkpoints_solved,
            distance=total_distance,
            score=score
        )
        
        trail = self.controller.state.trail
        total_distance = len(trail) - 1
        energy_used = 100 - self.controller.state.energy
        checkpoints = len(self.controller.state.checkpoints_solved)
        
        victory_window = tk.Toplevel(self.root)
        victory_window.title("🏆 VICTORY!")
        victory_window.configure(bg=self.colors['bg'])
        victory_window.transient(self.root)
        victory_window.grab_set()
        
        tk.Label(
            victory_window,
            text="⚡ MISSION COMPLETE ⚡",
            font=('Courier', 16, 'bold'),
            fg=self.colors['checkpoint_solved'],
            bg=self.colors['bg']
        ).pack(pady=15)
        
        # Stats
        stats_frame = tk.Frame(victory_window, bg=self.colors['bg'], relief=tk.RIDGE, bd=2)
        stats_frame.pack(padx=20, pady=10, fill=tk.X)
        
        stats_text = f"""FINAL STATISTICS:

Total Distance: {total_distance} steps
Energy Used: {energy_used:.0f} units
Checkpoints: {checkpoints}/{checkpoints}
Trail Length: {len(trail)} positions
Score: {score} points

Your stats have been saved!
"""
        
        tk.Label(
            stats_frame,
            text=stats_text,
            font=('Courier', 10),
            fg=self.colors['text'],
            bg=self.colors['bg'],
            justify=tk.LEFT
        ).pack(padx=15, pady=10)
        
        tk.Label(
            victory_window,
            text="What would you like to do?",
            font=('Courier', 11, 'bold'),
            fg=self.colors['grid'],
            bg=self.colors['bg']
        ).pack(pady=10)
        
        # Buttons
        btn_frame = tk.Frame(victory_window, bg=self.colors['bg'])
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="🎮 NEW GAME",
            font=('Courier', 10, 'bold'),
            bg=self.colors['button'],
            fg=self.colors['button_fg'],
            width=14,
            command=lambda: self.restart_game(victory_window)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🔥 HARD MODE",
            font=('Courier', 10, 'bold'),
            bg=self.colors['checkpoint'],
            fg=self.colors['button_fg'],
            width=14,
            command=lambda: self.start_hard_mode(victory_window)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="👋 EXIT",
            font=('Courier', 10, 'bold'),
            bg='#660000',
            fg=self.colors['button_fg'],
            width=14,
            command=self.root.quit
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            victory_window,
            text="🎵 Check demos/output/ for your music and poetry! 🎵",
            font=('Courier', 9),
            fg=self.colors['checkpoint_solved'],
            bg=self.colors['bg']
        ).pack(pady=10)
    
    def restart_game(self, window=None):
        """Restart with same settings."""
        if window:
            window.destroy()
        
        self.checkpoints = [Position(3, 3), Position(6, 6)]
        self.controller = RobotController(self.grid_size, self.checkpoints)
        self.controller.spawn(Position(0, 0), Direction.NORTH)
        
        self.poetry_label.config(text="Poetry scrolls will appear here...")
        self.message_label.config(
            text="New game started! Navigate to checkpoints!",
            fg=self.colors['text']
        )
        
        self.update_display()
    
    def start_hard_mode(self, window=None):
        """Start harder mode."""
        if window:
            window.destroy()
        
        self.checkpoints = [
            Position(3, 3),
            Position(6, 6),
            Position(1, 6),
            Position(6, 1),
        ]
        
        self.controller = RobotController(self.grid_size, self.checkpoints)
        self.controller.spawn(Position(0, 0), Direction.NORTH)
        
        self.poetry_label.config(text="Poetry scrolls will appear here...")
        self.message_label.config(
            text="🔥 HARD MODE: 4 checkpoints! Can you solve them all?",
            fg=self.colors['checkpoint']
        )
        
        self.update_display()
    
    def logout(self):
        """Logout and return to login screen."""
        # Stop AODS monitoring
        self.aods_manager.stop_monitoring()
        self.user_manager.logout()
        self.root.destroy()
        
        # Restart with login screen
        root = tk.Tk()
        LoginScreen(root, lambda um: self.start_game(root, um))
        root.mainloop()
    
    def start_game(self, root, user_manager):
        """Start the game with logged in user."""
        for widget in root.winfo_children():
            widget.destroy()
        
        root.geometry("700x850")
        NezhaGameGUI(root, user_manager)
    
    def open_aods_settings(self):
        """Open AODS (Always On Display Screensaver) settings."""
        self.aods_manager.open_settings(self.root)
    
    def show_help(self):
        """Show help dialog."""
        help_text = """NEZHA-RED Controls:

ARROW KEYS or BUTTONS:
  Move the robot in that direction

SOLVE BUTTON or ENTER:
  When at a checkpoint, solves the puzzle

OBJECTIVE:
  Navigate to red checkpoints (C1, C2)
  Solve Lights Out puzzles
  Collect poetry scrolls and MIDI music

LEGEND:
  Red circle = Robot
  Red dot = Checkpoint
  Green dot = Solved checkpoint
  Pink lines = Wind Fire Wheels trail

TIP: Plan your path to conserve energy!
        """
        messagebox.showinfo("Help", help_text)


def main():
    """Main entry point."""
    root = tk.Tk()
    
    def on_login_success(user_manager):
        """Callback when login is successful."""
        for widget in root.winfo_children():
            widget.destroy()
        root.geometry("700x850")
        NezhaGameGUI(root, user_manager)
    
    LoginScreen(root, on_login_success)
    root.mainloop()


if __name__ == "__main__":
    main()
