"""
Low-level client wrapper for the Google Gemini API using direct REST HTTP requests.
Allows native Python 3.8 support without third-party generative AI packages.
"""
import json
import logging
from pathlib import Path
import requests

logger = logging.getLogger(__name__)

class AIClient:
    """Wrapper class around Google Gemini REST API endpoints."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def create_vector_store(self, name: str) -> str:
        """Not required for Gemini Files API. Returns a placeholder."""
        logger.debug("create_vector_store called: skipped for Gemini Files API.")
        return "gemini_files_store"

    def upload_file(self, file_path: Path) -> str:
        """
        Uploads a file to Gemini File storage using multipart HTTP upload.
        Returns the Gemini File resource name (e.g., 'files/xxxx-xxxxx').
        """
        url = f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={self.api_key}"
        
        metadata = {
            "file": {
                "displayName": file_path.name
            }
        }
        
        try:
            with open(file_path, "rb") as f:
                files = {
                    "metadata": (None, json.dumps(metadata), "application/json"),
                    "file": (file_path.name, f, "text/markdown")
                }
                headers = {
                    "X-Goog-Upload-Protocol": "multipart"
                }
                
                response = requests.post(url, headers=headers, files=files, timeout=15)
                
            if response.status_code != 200:
                logger.error(f"Gemini upload failed with status {response.status_code}: {response.text}")
                raise Exception(f"Gemini upload failed: {response.text}")
                
            response_data = response.json()
            file_name = response_data["file"]["name"]
            logger.info(f"Uploaded file '{file_path.name}' to Gemini. File Name: {file_name}")
            return file_name
            
        except Exception as e:
            logger.error(f"Failed to upload file '{file_path.name}' to Gemini: {e}")
            raise

    def attach_to_vector_store(self, vector_store_id: str, file_id: str) -> None:
        """Not required for Gemini Files API. Placeholder to preserve interface."""
        logger.debug(f"attach_to_vector_store skipped for file {file_id}")

    def detach_from_vector_store(self, vector_store_id: str, file_id: str) -> None:
        """Not required for Gemini Files API. Placeholder to preserve interface."""
        logger.debug(f"detach_from_vector_store skipped for file {file_id}")

    def delete_file(self, file_id: str) -> None:
        """Deletes a file permanently from Gemini storage."""
        url = f"https://generativelanguage.googleapis.com/v1beta/{file_id}?key={self.api_key}"
        try:
            response = requests.delete(url, timeout=10)
            if response.status_code == 200:
                logger.info(f"Deleted file '{file_id}' from Gemini storage.")
            else:
                logger.warning(f"Failed to delete file '{file_id}' from Gemini: status {response.status_code}")
        except Exception as e:
            logger.warning(f"Failed to delete file '{file_id}' from Gemini storage: {e}")
network_wrapper = AIClient
