"""
Unit tests for StateManager class.
"""
import unittest
from pathlib import Path
import tempfile
import shutil
import json

from src.synchronization.state_manager import StateManager

class TestStateManager(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.state_file_path = Path(self.temp_dir) / "sync_state.json"
        self.state_manager = StateManager(str(self.state_file_path))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_load_state_non_existent(self) -> None:
        state = self.state_manager.load_state()
        self.assertEqual(state, {"articles": {}})

    def test_save_and_load_state(self) -> None:
        test_state = {
            "articles": {
                "123": {
                    "checksum": "abcde12345",
                    "slug": "test-slug",
                    "last_updated": "2026-07-06T12:00:00Z",
                    "title": "Test Title"
                }
            }
        }
        
        self.state_manager.save_state(test_state)
        self.assertTrue(self.state_file_path.exists())
        
        loaded = self.state_manager.load_state()
        self.assertEqual(loaded, test_state)

    def test_load_state_malformed(self) -> None:
        # Write invalid JSON
        with open(self.state_file_path, "w", encoding="utf-8") as f:
            f.write("invalid json content")
            
        state = self.state_manager.load_state()
        self.assertEqual(state, {"articles": {}})

if __name__ == "__main__":
    unittest.main()
