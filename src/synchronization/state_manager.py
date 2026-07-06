"""
State Manager handling history checkpoints and checksum lookups.
"""
class StateManager:
    """Manages reading and writing synchronization state metadata."""
    def __init__(self, state_file_path: str) -> None:
        self.state_file_path = state_file_path
