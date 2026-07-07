"""
DocStream Main Entry Point
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

from src.ingestion.scraper import ZendeskScraper
from src.ingestion.normalizer import HtmlNormalizer
from src.synchronization.state_manager import StateManager
from src.synchronization.coordinator import SyncCoordinator
from src.ai_integration.client import AIClient
from src.ai_integration.assistant import AIAssistantManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("docstream")

def main() -> None:
    # Load environment configuration
    load_dotenv()
    
    api_url = os.getenv("HELP_CENTER_API_URL", "https://support.optisigns.com/api/v2/help_center")
    page_url = os.getenv("HELP_CENTER_PAGE_URL", "https://support.optisigns.com")
    token = os.getenv("HELP_CENTER_TOKEN")
    
    throttle_ms = int(os.getenv("SYNC_THROTTLE_MS", "500"))
    max_retries = int(os.getenv("MAX_CONNECTION_RETRIES", "3"))
    
    # OpenAI/Gemini Credentials
    ai_api_key = os.getenv("AI_API_KEY") or os.getenv("API_KEY")
    vector_store_id = os.getenv("VECTOR_STORE_ID")
    assistant_id = os.getenv("ASSISTANT_ID")
    
    logger.info("Initializing DocStream sync execution.")
    
    # Initialize workspace paths relative to project root
    project_root = Path(__file__).resolve().parent.parent
    raw_cache_dir = project_root / "data" / "raw"
    markdown_dir = project_root / "data" / "markdown"
    state_file = project_root / "data" / "state" / "sync_state.json"
    
    # Setup OpenAI integration if credentials are provided
    ai_client = None
    if ai_api_key:
        logger.info("AI_API_KEY found. Activating remote OpenAI Vector Store synchronization.")
        try:
            ai_client = AIClient(api_key=ai_api_key)
            
            # Programmatically create a new Vector Store if ID is not specified
            if not vector_store_id:
                logger.info("VECTOR_STORE_ID not configured. Creating a new OpenAI Vector Store...")
                vector_store_id = ai_client.create_vector_store(name="DocStream Support Vector Store")
                logger.info(f"IMPORTANT: Please save this ID to your '.env' file: VECTOR_STORE_ID={vector_store_id}")
                
            # Programmatically create or retrieve the Assistant
            assistant_manager = AIAssistantManager(client=ai_client, assistant_id=assistant_id)
            new_assistant_id = assistant_manager.get_or_create_assistant(vector_store_id=vector_store_id)
            
            if new_assistant_id != assistant_id:
                logger.info(f"IMPORTANT: Please save this Assistant ID to your '.env' file: ASSISTANT_ID={new_assistant_id}")
                assistant_id = new_assistant_id
                
        except Exception as e:
            logger.error(f"Error configuring OpenAI integration resources: {e}. Exiting execution.")
            sys.exit(1)
    else:
        logger.warning("AI_API_KEY not found. Running in local-only synchronization mode.")
        
    # Step 1: Initialize ingestion and sync coordinator
    scraper = ZendeskScraper(
        api_url=api_url,
        page_url=page_url,
        token=token,
        throttle_ms=throttle_ms,
        max_retries=max_retries
    )
    
    normalizer = HtmlNormalizer(base_page_url=page_url)
    state_manager = StateManager(state_file_path=str(state_file))
    
    coordinator = SyncCoordinator(
        state_manager=state_manager,
        normalizer=normalizer,
        markdown_dir=str(markdown_dir),
        ai_client=ai_client,
        vector_store_id=vector_store_id
    )
    
    # Step 2: Fetch articles (API first, then fallback crawler)
    articles = []
    try:
        articles = scraper.fetch_articles_api(limit=35)
    except Exception as e:
        logger.warning(f"Zendesk API fetching encountered an error: {e}")
        
    if not articles:
        logger.info("No articles retrieved via API. Attempting HTML crawl fallback...")
        try:
            articles = scraper.crawl_articles_html(limit=35)
        except Exception as e:
            logger.error(f"HTML crawler fallback failed: {e}")
            
    if not articles:
        logger.error("No articles were successfully retrieved. Exiting execution with error.")
        sys.exit(1)
        
    logger.info(f"Successfully retrieved {len(articles)} articles. Processing cache...")
    
    # Step 3: Cache raw payloads
    scraper.cache_raw_articles(articles, raw_cache_dir)
    
    # Step 4: Run Delta Synchronization (locally and remotely if AI client is active)
    success, stats = coordinator.sync(articles)
    
    if not success:
        logger.error("Synchronization cycle completed with one or more errors.")
        sys.exit(1)
        
    logger.info("Synchronization execution completed successfully.")

if __name__ == "__main__":
    main()
