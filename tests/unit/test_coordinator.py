"""
Unit tests for SyncCoordinator class.
"""
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile
import shutil

from src.synchronization.coordinator import SyncCoordinator
from src.ingestion.normalizer import HtmlNormalizer
from src.synchronization.state_manager import StateManager

class TestSyncCoordinator(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.markdown_dir = Path(self.temp_dir) / "markdown"
        
        self.mock_state_manager = MagicMock(spec=StateManager)
        self.normalizer = HtmlNormalizer(base_page_url="https://support.optisigns.com")
        
        self.coordinator = SyncCoordinator(
            state_manager=self.mock_state_manager,
            normalizer=self.normalizer,
            markdown_dir=str(self.markdown_dir)
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_calculate_checksum(self) -> None:
        content = "Hello World"
        # SHA-256 of "Hello World" is a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e
        checksum = self.coordinator.calculate_checksum(content)
        self.assertEqual(checksum, "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e")

    @patch("src.synchronization.coordinator.print")
    def test_sync_added_and_skipped(self, mock_print) -> None:
        # Mock initial empty state
        self.mock_state_manager.load_state.return_value = {"articles": {}}
        
        current_articles = [
            {
                "id": 1,
                "title": "Welcome",
                "body": "<p>Welcome to our app!</p>",
                "slug": "welcome",
                "updated_at": "2026-07-06T12:00:00Z"
            }
        ]
        
        success, stats = self.coordinator.sync(current_articles)
        
        self.assertTrue(success)
        self.assertEqual(stats["added"], 1)
        self.assertEqual(stats["skipped"], 0)
        
        # Verify file was written
        markdown_file = self.markdown_dir / "welcome.md"
        self.assertTrue(markdown_file.exists())
        
        # Verify state saving was triggered
        self.mock_state_manager.save_state.assert_called_once()
        saved_state = self.mock_state_manager.save_state.call_args[0][0]
        self.assertIn("1", saved_state["articles"])
        checksum = saved_state["articles"]["1"]["checksum"]
        
        # Now run a second sync with identical article to verify "skipped"
        self.mock_state_manager.reset_mock()
        self.mock_state_manager.load_state.return_value = saved_state
        
        success2, stats2 = self.coordinator.sync(current_articles)
        self.assertTrue(success2)
        self.assertEqual(stats2["added"], 0)
        self.assertEqual(stats2["skipped"], 1)

    @patch("src.synchronization.coordinator.print")
    def test_sync_updated_and_deleted(self, mock_print) -> None:
        # Prepopulate state with two articles
        pre_state = {
            "articles": {
                "1": {
                    "checksum": "oldchecksum1111",
                    "slug": "welcome",
                    "last_updated": "2026-07-06T12:00:00Z",
                    "title": "Welcome"
                },
                "2": {
                    "checksum": "somechecksum2222",
                    "slug": "stale-article",
                    "last_updated": "2026-07-06T12:00:00Z",
                    "title": "Stale Article"
                }
            }
        }
        
        self.mock_state_manager.load_state.return_value = pre_state
        
        # Write local Markdown file for article 2 to simulate it being there
        self.markdown_dir.mkdir(parents=True, exist_ok=True)
        stale_file = self.markdown_dir / "stale-article.md"
        stale_file.write_text("Stale content")
        
        # Current articles: article 1 is updated, article 2 is missing (deleted)
        current_articles = [
            {
                "id": 1,
                "title": "Welcome",
                "body": "<p>Welcome to our app! (UPDATED)</p>",
                "slug": "welcome",
                "updated_at": "2026-07-06T13:00:00Z"
            }
        ]
        
        success, stats = self.coordinator.sync(current_articles)
        
        self.assertTrue(success)
        self.assertEqual(stats["updated"], 1)
        self.assertEqual(stats["deleted"], 1)
        
        # Stale file should be deleted
        self.assertFalse(stale_file.exists())
        
        # Welcome file should exist
        welcome_file = self.markdown_dir / "welcome.md"
        self.assertTrue(welcome_file.exists())
        
        # State should be updated
        self.mock_state_manager.save_state.assert_called_once()
        saved_state = self.mock_state_manager.save_state.call_args[0][0]
        self.assertIn("1", saved_state["articles"])
        self.assertNotIn("2", saved_state["articles"])

if __name__ == "__main__":
    unittest.main()
