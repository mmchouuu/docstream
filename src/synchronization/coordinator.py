"""
Sync Coordinator orchestrating the full ingestion and upload cycle.
"""
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from src.ingestion.normalizer import HtmlNormalizer
from src.synchronization.state_manager import StateManager
from src.ai_integration.client import AIClient

logger = logging.getLogger(__name__)

class SyncCoordinator:
    """Orchestrator class for synchronization operations."""

    def __init__(
        self,
        state_manager: StateManager,
        normalizer: HtmlNormalizer,
        markdown_dir: str,
        ai_client: Optional[AIClient] = None,
        vector_store_id: Optional[str] = None
    ) -> None:
        self.state_manager = state_manager
        self.normalizer = normalizer
        self.markdown_dir = Path(markdown_dir)
        self.ai_client = ai_client
        self.vector_store_id = vector_store_id

    def calculate_checksum(self, content: str) -> str:
        """Calculate the SHA-256 fingerprint for a normalized content string."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def sync(self, current_articles: List[Dict[str, Any]]) -> Tuple[bool, Dict[str, int]]:
        """
        Execute the delta synchronization cycle:
        1. Compare scraped articles against local state.
        2. Detect changes (added, updated, skipped, deleted).
        3. Write new/updated markdown files, upload them to OpenAI, and remove orphaned files.
        4. Save the updated state.
        """
        self.markdown_dir.mkdir(parents=True, exist_ok=True)
        state_data = self.state_manager.load_state()
        history = state_data.get("articles", {})
        
        new_history = {}
        stats = {"added": 0, "updated": 0, "skipped": 0, "deleted": 0}
        success = True
        
        current_article_ids = set()
        
        # 1. Process current articles
        for article in current_articles:
            article_id = str(article.get("id"))
            current_article_ids.add(article_id)
            
            title = article.get("title", "Untitled")
            raw_html = article.get("body") or ""
            
            # Step 1: Normalize HTML and calculate checksum
            clean_body = self.normalizer.html_to_markdown(raw_html)
            checksum = self.calculate_checksum(clean_body)
            
            # Formulate slug
            slug = article.get("slug")
            if not slug:
                import re
                slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            
            # Step 2: Compare with historical state
            prev_article = history.get(article_id)
            action = "skipped"
            
            if not prev_article:
                action = "added"
            elif prev_article.get("checksum") != checksum:
                action = "updated"
                
            # Step 3: Perform synchronization actions
            if action in ["added", "updated"]:
                try:
                    # Write markdown file
                    markdown_content = self.normalizer.normalize(article)
                    file_path = self.markdown_dir / f"{slug}.md"
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(markdown_content)
                        
                    file_id = prev_article.get("file_id") if prev_article else None
                    
                    # Remote OpenAI Vector Store upload
                    if self.ai_client and self.vector_store_id:
                        # If updated, detach and delete the old file
                        if action == "updated" and file_id:
                            try:
                                self.ai_client.detach_from_vector_store(self.vector_store_id, file_id)
                                self.ai_client.delete_file(file_id)
                            except Exception as ex:
                                logger.warning(f"Failed to detach/delete old file {file_id} for article {article_id}: {ex}")
                                
                        # Upload new file
                        file_id = self.ai_client.upload_file(file_path)
                        self.ai_client.attach_to_vector_store(self.vector_store_id, file_id)
                        
                    stats[action] += 1
                    logger.info(f"Article {article_id} ('{title}') was {action}.")
                except Exception as e:
                    logger.error(f"Failed to synchronize article {article_id}: {e}")
                    success = False
                    # Keep previous state if writing failed
                    if prev_article:
                        new_history[article_id] = prev_article
                    continue
            else:
                stats["skipped"] += 1
                logger.debug(f"Article {article_id} ('{title}') was skipped (unchanged).")
                # Keep the existing file_id if skipped
                file_id = prev_article.get("file_id") if prev_article else None
                
            # Save into new history state
            new_history[article_id] = {
                "checksum": checksum,
                "slug": slug,
                "last_updated": article.get("updated_at") or "",
                "title": title,
                "file_id": file_id
            }

        # 2. Process deletions (orphaned files present in history but missing from current run)
        for old_id, old_meta in history.items():
            if old_id not in current_article_ids:
                old_slug = old_meta.get("slug", f"article-{old_id}")
                file_path = self.markdown_dir / f"{old_slug}.md"
                old_file_id = old_meta.get("file_id")
                
                try:
                    # Detach and delete from OpenAI
                    if self.ai_client and self.vector_store_id and old_file_id:
                        try:
                            self.ai_client.detach_from_vector_store(self.vector_store_id, old_file_id)
                            self.ai_client.delete_file(old_file_id)
                        except Exception as ex:
                            logger.warning(f"Failed to detach/delete remote file {old_file_id} from OpenAI: {ex}")

                    if file_path.exists():
                        file_path.unlink()
                        logger.info(f"Deleted local orphaned Markdown file: {file_path.name}")
                    stats["deleted"] += 1
                except Exception as e:
                    logger.error(f"Failed to delete orphaned file {file_path}: {e}")
                    success = False
                    # Retain in history if deletion failed
                    new_history[old_id] = old_meta

        # 3. Save new state
        state_data["articles"] = new_history
        self.state_manager.save_state(state_data)
        
        # 4. Print structured summary
        status_str = "Success" if success else "Failure"
        print("=== Synchronization Summary ===")
        print(f"Status: {status_str}")
        print(f"Added: {stats['added']}")
        print(f"Updated: {stats['updated']}")
        print(f"Skipped: {stats['skipped']}")
        print(f"Deleted: {stats['deleted']}")
        print("==============================")
        
        return success, stats
