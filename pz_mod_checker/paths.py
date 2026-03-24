"""Shared path utilities for PZ Mod Checker."""

from __future__ import annotations

import platform
from pathlib import Path


def get_zomboid_dir() -> Path:
    """Return the Zomboid user directory for the current platform."""
    system = platform.system()
    home = Path.home()
    if system == "Linux":
        return home / "Zomboid"
    elif system == "Darwin":
        return home / "Zomboid"
    else:  # Windows
        return home / "Zomboid"
