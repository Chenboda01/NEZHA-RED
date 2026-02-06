"""User authentication and profile management for NEZHA-RED."""

import json
import hashlib
import os
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List
from pathlib import Path


@dataclass
class UserProfile:
    """User profile with game statistics."""
    username: str
    password_hash: str
    total_games_played: int = 0
    total_checkpoints_solved: int = 0
    total_distance_traveled: int = 0
    best_score: int = 0
    last_login: Optional[str] = None
    created_at: Optional[str] = None


class UserManager:
    """Manages user accounts and authentication."""
    
    def __init__(self, data_dir: str = "demos/data"):
        """Initialize user manager.
        
        Args:
            data_dir: Directory to store user data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.users_file = self.data_dir / "users.json"
        self.session_file = self.data_dir / "session.json"
        
        self.users: Dict[str, UserProfile] = {}
        self.current_user: Optional[UserProfile] = None
        
        self._load_users()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_users(self) -> None:
        """Load users from JSON file."""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r') as f:
                    data = json.load(f)
                    for username, user_data in data.items():
                        self.users[username] = UserProfile(**user_data)
            except (json.JSONDecodeError, KeyError):
                self.users = {}
    
    def _save_users(self) -> None:
        """Save users to JSON file."""
        data = {}
        for username, profile in self.users.items():
            data[username] = asdict(profile)
        
        with open(self.users_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save_session(self, username: str) -> None:
        """Save current session."""
        from datetime import datetime
        session_data = {
            'username': username,
            'login_time': datetime.now().isoformat()
        }
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
    
    def _clear_session(self) -> None:
        """Clear current session."""
        if self.session_file.exists():
            self.session_file.unlink()
    
    def create_account(self, username: str, password: str) -> tuple[bool, str]:
        """Create a new user account.
        
        Args:
            username: Desired username
            password: User's password
            
        Returns:
            Tuple of (success, message)
        """
        # Validate username
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if not username.isalnum():
            return False, "Username can only contain letters and numbers"
        
        if username in self.users:
            return False, "Username already exists"
        
        # Validate password
        if not password or len(password) < 4:
            return False, "Password must be at least 4 characters long"
        
        # Create user profile
        from datetime import datetime
        password_hash = self._hash_password(password)
        profile = UserProfile(
            username=username,
            password_hash=password_hash,
            created_at=datetime.now().isoformat()
        )
        
        self.users[username] = profile
        self._save_users()
        
        return True, f"Account '{username}' created successfully!"
    
    def login(self, username: str, password: str) -> tuple[bool, str]:
        """Login with username and password.
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            Tuple of (success, message)
        """
        if username not in self.users:
            return False, "Username not found"
        
        user = self.users[username]
        password_hash = self._hash_password(password)
        
        if user.password_hash != password_hash:
            return False, "Incorrect password"
        
        # Successful login
        self.current_user = user
        from datetime import datetime
        user.last_login = datetime.now().isoformat()
        self._save_users()
        self._save_session(username)
        
        return True, f"Welcome back, {username}!"
    
    def try_auto_login(self) -> bool:
        """Try to auto-login from saved session.
        
        Returns:
            True if auto-login successful
        """
        if not self.session_file.exists():
            return False
        
        try:
            with open(self.session_file, 'r') as f:
                session = json.load(f)
                username = session.get('username')
                
                if username and username in self.users:
                    self.current_user = self.users[username]
                    from datetime import datetime
                    self.current_user.last_login = datetime.now().isoformat()
                    self._save_users()
                    return True
        except (json.JSONDecodeError, KeyError):
            pass
        
        return False
    
    def logout(self) -> None:
        """Logout current user."""
        self.current_user = None
        self._clear_session()
    
    def update_stats(self, checkpoints_solved: int = 0, distance: int = 0, score: int = 0) -> None:
        """Update current user's game statistics.
        
        Args:
            checkpoints_solved: Number of checkpoints solved in this game
            distance: Total distance traveled
            score: Game score
        """
        if not self.current_user:
            return
        
        user = self.current_user
        user.total_games_played += 1
        user.total_checkpoints_solved += checkpoints_solved
        user.total_distance_traveled += distance
        
        if score > user.best_score:
            user.best_score = score
        
        self._save_users()
    
    def get_current_username(self) -> Optional[str]:
        """Get current logged-in username."""
        return self.current_user.username if self.current_user else None
    
    def has_users(self) -> bool:
        """Check if any users exist."""
        return len(self.users) > 0
