"""
Google Gemini Assistant Test Chat Script (REST API Version)
Allows querying the Assistant via HTTP REST to verify grounding and citation behavior.
Saves package requirements and supports Python 3.8 natively.
"""
import os
import sys
import logging
import json
import requests
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] - %(message)s")
logger = logging.getLogger("test_chat")

SYSTEM_PROMPT = """You are OptiBot, the customer-support bot for OptiSigns.com.

• Tone: helpful, factual, concise.
• Only answer using the uploaded docs.
• Max 5 bullet points; else link to the doc.
• Cite up to 3 "Article URL:" lines per reply. Place each URL citation on a new line prefixed with a bullet point."""

def main() -> None:
    load_dotenv()
    
    api_key = os.getenv("AI_API_KEY") or os.getenv("API_KEY")
    
    if not api_key:
        logger.error("AI_API_KEY or API_KEY not found in env.")
        sys.exit(1)
        
    # Load state file to get active Gemini file names
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    state_file_path = os.path.join(project_root, "data", "state", "sync_state.json")
    
    if not os.path.exists(state_file_path):
        logger.error("State file sync_state.json not found. Please run 'py -m src.main' first to upload documents.")
        sys.exit(1)
        
    try:
        with open(state_file_path, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read state file: {e}")
        sys.exit(1)
        
    articles = state.get("articles", {})
    file_parts = []
    
    logger.info("Retrieving file mappings from state database...")
    for art_id, art_meta in articles.items():
        file_id = art_meta.get("file_id")
        if file_id:
            # Reconstruct the file URI deterministically
            file_uri = f"https://generativelanguage.googleapis.com/v1beta/{file_id}"
            file_parts.append({
                "file_data": {
                    "mime_type": "text/markdown",
                    "file_uri": file_uri
                }
            })
            
    # Initialize the generative model
    logger.info("Configuring Gemini Model...")
    model_name = "gemini-flash-latest"
    
    print("\n" + "="*50)
    print("🤖 Welcome to OptiBot Interactive Terminal Chat!")
    print("Type your support question below and press Enter.")
    print("Type 'exit' or 'quit' to close the chat.")
    print("="*50 + "\n")
    
    while True:
        try:
            query = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break
            
        if not query:
            continue
            
        if query.lower() in ["exit", "quit"]:
            print("Exiting. Goodbye!")
            break
            
        print("OptiBot is thinking...")
        
        # Prepare combined parts
        combined_parts = file_parts + [{"text": query}]
        
        # 3. Call generateContent REST API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": combined_parts
                }
            ],
            "systemInstruction": {
                "parts": [
                    {
                        "text": SYSTEM_PROMPT
                    }
                ]
            }
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code != 200:
                logger.error(f"Gemini API generation failed (status {response.status_code}): {response.text}")
                continue
                
            result = response.json()
            
            # Parse output text
            candidates = result.get("candidates", [])
            if candidates:
                text_response = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                print("\n" + "="*50)
                print("OPTIBOT RESPONSE:")
                print("="*50)
                print(text_response)
                print("="*50 + "\n")
            else:
                logger.error(f"No response text in model candidates. Full response: {result}")
                
        except Exception as e:
            logger.error(f"Failed to generate content: {e}")

if __name__ == "__main__":
    main()
