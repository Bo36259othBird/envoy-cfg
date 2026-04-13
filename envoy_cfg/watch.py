"""File watcher for detecting .env file changes and triggering sync."""

import hashlib
import os
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional


def _file_hash(path: str) -> Optional[str]:
    """Return MD5 hash of file contents, or None if file is unreadable."""
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except (OSError, IOError):
        return None


@dataclass
class WatchEntry:
    path: str
    last_hash: Optional[str] = None
    last_checked: float = field(default_factory=time.time)

    def has_changed(self) -> bool:
        """Return True if the file hash differs from the last known hash."""
        current = _file_hash(self.path)
        if current != self.last_hash:
            self.last_hash = current
            self.last_checked = time.time()
            return True
        self.last_checked = time.time()
        return False


class EnvWatcher:
    """Watches one or more .env files for changes."""

    def __init__(self, poll_interval: float = 1.0):
        self.poll_interval = poll_interval
        self._entries: Dict[str, WatchEntry] = {}
        self._callbacks: Dict[str, Callable[[str], None]] = {}

    def watch(self, path: str, callback: Callable[[str], None]) -> None:
        """Register a file path to watch with a callback on change."""
        abs_path = os.path.abspath(path)
        self._entries[abs_path] = WatchEntry(
            path=abs_path, last_hash=_file_hash(abs_path)
        )
        self._callbacks[abs_path] = callback

    def unwatch(self, path: str) -> bool:
        """Remove a watched path. Returns True if it was being watched."""
        abs_path = os.path.abspath(path)
        removed = abs_path in self._entries
        self._entries.pop(abs_path, None)
        self._callbacks.pop(abs_path, None)
        return removed

    def check_once(self) -> Dict[str, bool]:
        """Check all watched files once. Returns dict of path -> changed."""
        results = {}
        for path, entry in self._entries.items():
            changed = entry.has_changed()
            results[path] = changed
            if changed and path in self._callbacks:
                self._callbacks[path](path)
        return results

    def run(self, max_cycles: Optional[int] = None) -> None:
        """Poll watched files in a loop. Stops after max_cycles if given."""
        cycles = 0
        while max_cycles is None or cycles < max_cycles:
            self.check_once()
            time.sleep(self.poll_interval)
            cycles += 1

    @property
    def watched_paths(self):
        return list(self._entries.keys())
