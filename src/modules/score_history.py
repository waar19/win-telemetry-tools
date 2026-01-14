"""
Score History Module
Tracks privacy score over time.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

from .profile_manager import ProfileManager


@dataclass
class ScoreEntry:
    """A single score history entry."""
    date: str
    score: int
    telemetry_score: int
    permissions_score: int
    firewall_blocked: int
    firewall_total: int


class ScoreHistory:
    """Manages privacy score history."""
    
    MAX_ENTRIES = 30  # Keep last 30 entries
    HISTORY_FILE = "score_history.json"
    
    def __init__(self):
        self._profile_mgr = ProfileManager()
        self._history_file = self._profile_mgr.get_app_data_path() / self.HISTORY_FILE
        self._history: List[ScoreEntry] = []
        self._load_history()
    
    def _load_history(self):
        """Load history from file."""
        if self._history_file.exists():
            try:
                with open(self._history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._history = [
                        ScoreEntry(**entry) for entry in data.get("entries", [])
                    ]
            except Exception as e:
                print(f"Error loading score history: {e}")
                self._history = []
    
    def _save_history(self):
        """Save history to file."""
        try:
            data = {
                "version": "1.0",
                "entries": [asdict(entry) for entry in self._history]
            }
            with open(self._history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving score history: {e}")
    
    def add_entry(self, score: int, telemetry: int, permissions: int, 
                  firewall_blocked: int, firewall_total: int):
        """Add a new score entry."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Check if we already have an entry for today
        for i, entry in enumerate(self._history):
            if entry.date == today:
                # Update today's entry
                self._history[i] = ScoreEntry(
                    date=today,
                    score=score,
                    telemetry_score=telemetry,
                    permissions_score=permissions,
                    firewall_blocked=firewall_blocked,
                    firewall_total=firewall_total
                )
                self._save_history()
                return
        
        # Add new entry
        entry = ScoreEntry(
            date=today,
            score=score,
            telemetry_score=telemetry,
            permissions_score=permissions,
            firewall_blocked=firewall_blocked,
            firewall_total=firewall_total
        )
        self._history.append(entry)
        
        # Trim to max entries
        if len(self._history) > self.MAX_ENTRIES:
            self._history = self._history[-self.MAX_ENTRIES:]
        
        self._save_history()
    
    def get_history(self, days: int = 7) -> List[ScoreEntry]:
        """Get score history for the last N days."""
        if not self._history:
            return []
        
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.strftime("%Y-%m-%d")
        
        return [e for e in self._history if e.date >= cutoff_str]
    
    def get_all_history(self) -> List[ScoreEntry]:
        """Get all history entries."""
        return self._history.copy()
    
    def get_latest_score(self) -> Optional[ScoreEntry]:
        """Get the most recent score entry."""
        if self._history:
            return self._history[-1]
        return None
    
    def get_score_trend(self) -> str:
        """Get trend direction (up, down, stable)."""
        if len(self._history) < 2:
            return "stable"
        
        recent = self._history[-1].score
        previous = self._history[-2].score
        
        if recent > previous:
            return "up"
        elif recent < previous:
            return "down"
        return "stable"
    
    def clear_history(self):
        """Clear all history."""
        self._history = []
        self._save_history()
