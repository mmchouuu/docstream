"""
State Manager handling history checkpoints and checksum lookups.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class StateManager:
    """Manages reading and writing synchronization state metadata."""

    def __init__(self, state_file_path: str) -> None:
        self.state_file_path = Path(state_file_path)

    def load_state(self) -> Dict[str, Any]:
        """Loads synchronization state from the local JSON file."""
        if not self.state_file_path.exists():
            logger.info(f"State file '{self.state_file_path}' not found. Initializing empty state.")
            return {"articles": {}}

        try:
            with open(self.state_file_path, "r", encoding="utf-8") as f:
                state = json.load(f)
                if not isinstance(state, dict) or "articles" not in state:
                    logger.warning("Malformed state file. Resetting state.")
                    return {"articles": {}}
                return state
        except Exception as e:
            logger.error(f"Error loading state file: {e}. Resetting state.")
            return {"articles": {}}

    def save_state(self, state: Dict[str, Any]) -> None:
        """Saves synchronization state to the local JSON file."""
        try:
            self.state_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved synchronization state to '{self.state_file_path}'")
        except Exception as e:
            logger.error(f"Failed to save state file: {e}")
