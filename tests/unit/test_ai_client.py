"""
Unit tests for AIClient and AIAssistantManager (Gemini REST API Wrapper).
"""
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile
import shutil

from src.ai_integration.client import AIClient
from src.ai_integration.assistant import AIAssistantManager

class TestAIClientAndAssistant(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.api_key = "fake-key"
        self.ai_client = AIClient(api_key=self.api_key)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    @patch("requests.post")
    def test_upload_file(self, mock_post) -> None:
        # Mock successful Gemini File API upload response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "file": {
                "name": "files/test-file-id",
                "displayName": "test_doc.md",
                "uri": "https://generativelanguage.googleapis.com/v1beta/files/test-file-id"
            }
        }
        mock_post.return_value = mock_response
        
        temp_file = Path(self.temp_dir) / "test_doc.md"
        temp_file.write_text("Markdown Content")
        
        file_id = self.ai_client.upload_file(temp_file)
        self.assertEqual(file_id, "files/test-file-id")
        mock_post.assert_called_once()

    @patch("requests.delete")
    def test_delete_file(self, mock_delete) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        
        self.ai_client.delete_file("files/test-file-id")
        mock_delete.assert_called_once()

    def test_assistant_manager_configuration(self) -> None:
        manager = AIAssistantManager(client=self.ai_client, assistant_id=None)
        asst_id = manager.get_or_create_assistant(vector_store_id="gemini_files_store")
        self.assertEqual(asst_id, "gemini-1.5-flash")

if __name__ == "__main__":
    unittest.main()
