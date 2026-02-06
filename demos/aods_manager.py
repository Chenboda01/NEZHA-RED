"""Always On Display Screensaver (AODS) for NEZHA-RED."""

import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import json
import os
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass, asdict


@dataclass
class AODSSettings:
    """AODS configuration settings."""

    enabled: bool = True
    activation_minutes: int = 15  # Default 15 minutes
    custom_minutes: Optional[int] = None
    image_path: Optional[str] = None
    show_clock: bool = True
    show_stats: bool = True


class AODSManager:
    """Manages the Always On Display Screensaver feature."""

    def __init__(self, user_manager, data_dir: str = "demos/data"):
        """Initialize AODS manager.

        Args:
            user_manager: User manager instance for stats
            data_dir: Directory to store settings
        """
        self.user_manager = user_manager
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.settings_file = self.data_dir / "aods_settings.json"
        self.settings = AODSSettings()
        self._load_settings()

        # Idle tracking
        self.idle_time_ms = 0
        self.last_activity_ms = 0
        self.is_active = False
        self.screensaver_window: Optional[tk.Toplevel] = None
        self.check_interval_ms = 1000  # Check every second

        # Callbacks
        self.on_screensaver_start: Optional[Callable] = None
        self.on_screensaver_end: Optional[Callable] = None

        # Image cache
        self.photo_image: Optional[ImageTk.PhotoImage] = None

    def _load_settings(self) -> None:
        """Load AODS settings from file."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r") as f:
                    data = json.load(f)
                    self.settings = AODSSettings(**data)
            except (json.JSONDecodeError, TypeError):
                self.settings = AODSSettings()

    def save_settings(self) -> None:
        """Save AODS settings to file."""
        with open(self.settings_file, "w") as f:
            json.dump(asdict(self.settings), f, indent=2)

    def get_activation_ms(self) -> int:
        """Get activation time in milliseconds."""
        minutes = self.settings.custom_minutes or self.settings.activation_minutes
        return minutes * 60 * 1000

    def start_monitoring(self, root: tk.Tk) -> None:
        """Start monitoring for idle time.

        Args:
            root: Main tkinter window
        """
        if not self.settings.enabled:
            return

        self.root = root
        self.last_activity_ms = root.winfo_pixels("1i")  # Get current time

        # Bind activity events
        self._bind_activity_events()

        # Start idle check
        self._schedule_idle_check()

    def _bind_activity_events(self) -> None:
        """Bind events that indicate user activity."""
        events = [
            "<Motion>",
            "<Button-1>",
            "<Button-2>",
            "<Button-3>",
            "<Key>",
            "<KeyRelease>",
            "<MouseWheel>",
            "<Enter>",
            "<Leave>",
        ]

        for event in events:
            self.root.bind_all(event, self._on_activity)

    def _on_activity(self, event=None) -> None:
        """Reset idle timer on user activity."""
        self.idle_time_ms = 0
        self.last_activity_ms = self.root.winfo_pixels("1i")

        # If screensaver is active, close it
        if self.is_active and self.screensaver_window:
            self._close_screensaver()

    def _schedule_idle_check(self) -> None:
        """Schedule next idle check."""
        if not self.settings.enabled:
            return

        self.root.after(self.check_interval_ms, self._check_idle)

    def _check_idle(self) -> None:
        """Check if screensaver should activate."""
        if not self.settings.enabled or self.is_active:
            self._schedule_idle_check()
            return

        # Increment idle time
        self.idle_time_ms += self.check_interval_ms

        # Check if it's time to activate
        activation_ms = self.get_activation_ms()
        if self.idle_time_ms >= activation_ms:
            self._activate_screensaver()

        self._schedule_idle_check()

    def _activate_screensaver(self) -> None:
        """Activate the AODS screensaver."""
        if self.is_active:
            return

        self.is_active = True

        # Close any existing screensaver window first
        if self.screensaver_window:
            try:
                self.screensaver_window.destroy()
            except:
                pass
            self.screensaver_window = None

        # Create screensaver window
        self.screensaver_window = tk.Toplevel(self.root)
        self.screensaver_window.attributes("-fullscreen", True)
        self.screensaver_window.attributes("-topmost", True)
        self.screensaver_window.configure(bg="black")

        # Remove window decorations
        self.screensaver_window.overrideredirect(True)

        # Set focus to ensure key events are captured
        self.screensaver_window.focus_set()

        # Create canvas for display
        self._setup_screensaver_display()

        # Call callback
        if self.on_screensaver_start:
            self.on_screensaver_start()

        # Update display
        self._update_screensaver()

    def _setup_screensaver_display(self) -> None:
        """Setup the screensaver display."""
        window = self.screensaver_window

        # Get screen dimensions
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Create canvas
        self.canvas = tk.Canvas(
            window,
            width=screen_width,
            height=screen_height,
            bg="black",
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Load and display image if set
        if self.settings.image_path and os.path.exists(self.settings.image_path):
            self._load_image(screen_width, screen_height)

        # Add text elements
        if self.settings.show_clock:
            self.clock_label = self.canvas.create_text(
                screen_width // 2,
                screen_height - 100,
                text="",
                font=("Courier", 48, "bold"),
                fill="#ff0040",
                anchor="center",
            )

        if self.settings.show_stats and self.user_manager.current_user:
            user = self.user_manager.current_user
            stats_text = f"{user.username} | Games: {user.total_games_played} | Best Score: {user.best_score}"
            self.stats_label = self.canvas.create_text(
                screen_width // 2,
                screen_height - 40,
                text=stats_text,
                font=("Courier", 20),
                fill="#ff99bb",
                anchor="center",
            )

        # Add instruction text
        self.instruction_label = self.canvas.create_text(
            screen_width // 2,
            50,
            text="AODS - Always On Display Screensaver - Press any key or click to exit",
            font=("Courier", 14),
            fill="#660000",
            anchor="center",
        )

        # Bind events to close screensaver - use multiple approaches for better capture
        def on_any_event(event=None):
            self._close_screensaver()

        # Bind click events on canvas
        self.canvas.bind("<Button-1>", on_any_event)
        self.canvas.bind("<Button-2>", on_any_event)
        self.canvas.bind("<Button-3>", on_any_event)
        self.canvas.bind("<Double-Button-1>", on_any_event)

        # Bind motion event on canvas (any mouse movement)
        self.canvas.bind("<Motion>", on_any_event)

        # Bind key press events on window
        window.bind("<Key>", on_any_event)
        window.bind("<Escape>", on_any_event)
        window.bind("<Return>", on_any_event)
        window.bind("<space>", on_any_event)
        window.bind("<Button-1>", on_any_event)
        window.bind("<Button-3>", on_any_event)
        window.bind("<Motion>", on_any_event)

    def _load_image(self, screen_width: int, screen_height: int) -> None:
        """Load and display the custom image.

        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
        """
        try:
            # Open image
            img = Image.open(self.settings.image_path)

            # Calculate resize to fit screen while maintaining aspect ratio
            img_width, img_height = img.size
            scale = min(screen_width / img_width, screen_height / img_height)

            new_width = int(img_width * scale * 0.8)  # 80% of screen
            new_height = int(img_height * scale * 0.8)

            # Resize image
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Convert to PhotoImage
            self.photo_image = ImageTk.PhotoImage(img)

            # Display on canvas
            self.canvas.create_image(
                screen_width // 2,
                screen_height // 2,
                image=self.photo_image,
                anchor="center",
            )
        except Exception as e:
            print(f"Error loading image: {e}")
            # Show error text
            self.canvas.create_text(
                screen_width // 2,
                screen_height // 2,
                text="Unable to load image",
                font=("Courier", 24),
                fill="#ff0040",
                anchor="center",
            )

    def _update_screensaver(self) -> None:
        """Update screensaver display (clock, etc.)."""
        if not self.is_active or not self.screensaver_window:
            return

        # Update clock
        if self.settings.show_clock and hasattr(self, "clock_label"):
            from datetime import datetime

            current_time = datetime.now().strftime("%H:%M:%S")
            self.canvas.itemconfig(self.clock_label, text=current_time)

        # Schedule next update
        self.screensaver_window.after(1000, self._update_screensaver)

    def _close_screensaver(self) -> None:
        """Close the screensaver."""
        if not self.is_active:
            return

        self.is_active = False
        self.idle_time_ms = 0

        # Unbind events from window
        if self.screensaver_window:
            try:
                for event in ["<Key>", "<Escape>", "<Return>", "<space>", "<Button-1>", "<Button-3>", "<Motion>"]:
                    try:
                        self.screensaver_window.unbind(event)
                    except:
                        pass
            except:
                pass

        # Call restore callback if exists (for preview mode)
        if hasattr(self, "_restore_callback") and self._restore_callback:
            try:
                self._restore_callback()
            except Exception as e:
                print(f"Error restoring AODS settings: {e}")
            delattr(self, "_restore_callback")

        if self.screensaver_window:
            self.screensaver_window.destroy()
            self.screensaver_window = None

        # Call callback
        if self.on_screensaver_end:
            self.on_screensaver_end()

    def stop_monitoring(self) -> None:
        """Stop monitoring for idle time."""
        self._close_screensaver()

    def open_settings(self, parent: tk.Tk) -> None:
        """Open AODS settings dialog.

        Args:
            parent: Parent window
        """
        settings_window = tk.Toplevel(parent)
        settings_window.title("AODS Settings")
        settings_window.geometry("500x500")
        settings_window.configure(bg="#1a0000")
        settings_window.transient(parent)
        settings_window.grab_set()

        colors = {
            "bg": "#1a0000",
            "grid": "#ff0040",
            "text": "#ff99bb",
            "button": "#cc0033",
            "button_fg": "#ffffff",
            "input_bg": "#330000",
        }

        # Title
        tk.Label(
            settings_window,
            text="⚡ AODS SETTINGS ⚡",
            font=("Courier", 16, "bold"),
            fg=colors["grid"],
            bg=colors["bg"],
        ).pack(pady=15)

        # Enable/Disable
        enabled_var = tk.BooleanVar(value=self.settings.enabled)
        tk.Checkbutton(
            settings_window,
            text="Enable AODS",
            variable=enabled_var,
            font=("Courier", 11),
            fg=colors["text"],
            bg=colors["bg"],
            selectcolor=colors["input_bg"],
            activebackground=colors["bg"],
            activeforeground=colors["text"],
        ).pack(pady=10)

        # Activation time
        tk.Label(
            settings_window,
            text="Activate after:",
            font=("Courier", 11),
            fg=colors["text"],
            bg=colors["bg"],
        ).pack(pady=5)

        time_frame = tk.Frame(settings_window, bg=colors["bg"])
        time_frame.pack(pady=5)

        time_var = tk.IntVar(value=self.settings.activation_minutes)

        tk.Radiobutton(
            time_frame,
            text="10 minutes",
            variable=time_var,
            value=10,
            font=("Courier", 10),
            fg=colors["text"],
            bg=colors["bg"],
            selectcolor=colors["input_bg"],
        ).pack(anchor="w", padx=20)

        tk.Radiobutton(
            time_frame,
            text="15 minutes",
            variable=time_var,
            value=15,
            font=("Courier", 10),
            fg=colors["text"],
            bg=colors["bg"],
            selectcolor=colors["input_bg"],
        ).pack(anchor="w", padx=20)

        tk.Radiobutton(
            time_frame,
            text="20 minutes",
            variable=time_var,
            value=20,
            font=("Courier", 10),
            fg=colors["text"],
            bg=colors["bg"],
            selectcolor=colors["input_bg"],
        ).pack(anchor="w", padx=20)

        # Custom time
        custom_frame = tk.Frame(time_frame, bg=colors["bg"])
        custom_frame.pack(anchor="w", padx=20, pady=5)

        custom_var = tk.BooleanVar(value=self.settings.custom_minutes is not None)
        tk.Checkbutton(
            custom_frame,
            text="Custom:",
            variable=custom_var,
            font=("Courier", 10),
            fg=colors["text"],
            bg=colors["bg"],
            selectcolor=colors["input_bg"],
        ).pack(side=tk.LEFT)

        custom_minutes_var = tk.IntVar(value=self.settings.custom_minutes or 30)
        custom_spin = tk.Spinbox(
            custom_frame,
            from_=1,
            to=120,
            width=5,
            textvariable=custom_minutes_var,
            font=("Courier", 10),
            bg=colors["input_bg"],
            fg=colors["text"],
        )
        custom_spin.pack(side=tk.LEFT, padx=5)

        tk.Label(
            custom_frame,
            text="minutes",
            font=("Courier", 10),
            fg=colors["text"],
            bg=colors["bg"],
        ).pack(side=tk.LEFT)

        # Image selection
        tk.Label(
            settings_window,
            text="Screensaver Image:",
            font=("Courier", 11),
            fg=colors["text"],
            bg=colors["bg"],
        ).pack(pady=(20, 5))

        img_frame = tk.Frame(settings_window, bg=colors["bg"])
        img_frame.pack(pady=5, fill=tk.X, padx=20)

        img_path_var = tk.StringVar(
            value=self.settings.image_path or "No image selected"
        )
        img_label = tk.Label(
            img_frame,
            textvariable=img_path_var,
            font=("Courier", 9),
            fg=colors["text"],
            bg=colors["bg"],
            wraplength=350,
        )
        img_label.pack(side=tk.LEFT)

        def browse_image():
            file_path = filedialog.askopenfilename(
                title="Select Image",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("All files", "*.*"),
                ],
            )
            if file_path:
                img_path_var.set(file_path)

        tk.Button(
            img_frame,
            text="Browse...",
            font=("Courier", 9),
            bg=colors["button"],
            fg=colors["button_fg"],
            command=browse_image,
        ).pack(side=tk.RIGHT, padx=5)

        # Display options
        tk.Label(
            settings_window,
            text="Display Options:",
            font=("Courier", 11),
            fg=colors["text"],
            bg=colors["bg"],
        ).pack(pady=(20, 5))

        show_clock_var = tk.BooleanVar(value=self.settings.show_clock)
        tk.Checkbutton(
            settings_window,
            text="Show Clock",
            variable=show_clock_var,
            font=("Courier", 10),
            fg=colors["text"],
            bg=colors["bg"],
            selectcolor=colors["input_bg"],
        ).pack(anchor="w", padx=20)

        show_stats_var = tk.BooleanVar(value=self.settings.show_stats)
        tk.Checkbutton(
            settings_window,
            text="Show User Stats",
            variable=show_stats_var,
            font=("Courier", 10),
            fg=colors["text"],
            bg=colors["bg"],
            selectcolor=colors["input_bg"],
        ).pack(anchor="w", padx=20)

        # Preview button
        def preview_aods():
            """Preview AODS screensaver."""
            # Check if already previewing
            if self.is_active:
                messagebox.showinfo(
                    "AODS Preview",
                    "Screensaver is already active. Close it first.",
                    parent=settings_window,
                )
                return

            # Temporarily save settings
            from dataclasses import replace

            old_settings = self.settings
            self.settings = AODSSettings(
                enabled=True,
                activation_minutes=time_var.get(),
                custom_minutes=custom_minutes_var.get() if custom_var.get() else None,
                image_path=(
                    img_path_var.get()
                    if img_path_var.get() != "No image selected"
                    else None
                ),
                show_clock=show_clock_var.get(),
                show_stats=show_stats_var.get(),
            )

            # Activate screensaver
            self._activate_screensaver()

            # Restore old settings after preview ends
            # The _close_screensaver will be called automatically when user clicks
            # So we just need to restore settings when that happens
            def restore_on_close():
                self.settings = old_settings
                # Clear the restore callback
                if hasattr(self, "_restore_callback"):
                    delattr(self, "_restore_callback")

            self._restore_callback = restore_on_close

            # Set up a one-time callback for when preview closes
            # We'll attach this to the close_screensaver call

        tk.Button(
            settings_window,
            text="Preview AODS",
            font=("Courier", 10, "bold"),
            bg=colors["grid"],
            fg=colors["button_fg"],
            width=15,
            command=preview_aods,
        ).pack(pady=15)

        # Save/Cancel buttons
        btn_frame = tk.Frame(settings_window, bg=colors["bg"])
        btn_frame.pack(pady=20)

        def save_settings():
            """Save the settings."""
            self.settings.enabled = enabled_var.get()
            self.settings.activation_minutes = time_var.get()
            self.settings.custom_minutes = (
                custom_minutes_var.get() if custom_var.get() else None
            )

            img_path = img_path_var.get()
            self.settings.image_path = (
                img_path if img_path != "No image selected" else None
            )

            self.settings.show_clock = show_clock_var.get()
            self.settings.show_stats = show_stats_var.get()

            self.save_settings()
            settings_window.destroy()

            messagebox.showinfo(
                "AODS Settings Saved", "Your screensaver settings have been saved!"
            )

        tk.Button(
            btn_frame,
            text="SAVE",
            font=("Courier", 11, "bold"),
            bg=colors["button"],
            fg=colors["button_fg"],
            width=12,
            command=save_settings,
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="CANCEL",
            font=("Courier", 11, "bold"),
            bg="#660000",
            fg=colors["button_fg"],
            width=12,
            command=settings_window.destroy,
        ).pack(side=tk.LEFT, padx=5)
