import os
import sys
import json
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App configuration
st.set_page_config(
    page_title="OptiBot - OptiSigns Support",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
<style>
    /* Custom background & typography styling */
    .stApp {
        background-color: #0e1117;
        color: #e0e6ed;
    }
    .main-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 2.5rem;
        background: linear-gradient(45deg, #7b2ff7, #1187fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #8892b0;
        margin-bottom: 2rem;
    }
    .sidebar-header {
        font-weight: 700;
        color: #7b2ff7;
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }
    .status-connected {
        color: #00e676;
        font-weight: bold;
    }
    .status-disconnected {
        color: #ff1744;
        font-weight: bold;
    }
    .citation-container {
        background-color: #1a1f2c;
        border-radius: 8px;
        padding: 10px;
        border-left: 4px solid #7b2ff7;
        margin-top: 10px;
    }
    .citation-title {
        font-size: 0.85rem;
        font-weight: bold;
        color: #8892b0;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    
</style>
""", unsafe_allow_html=True)

# OptiBot Default System Prompt
DEFAULT_SYSTEM_PROMPT = """You are OptiBot, the customer-support bot for OptiSigns.com.

• Tone: helpful, factual, concise.
• Only answer using the uploaded docs.
• Max 5 bullet points; else link to the doc.
• Cite up to 3 "Article URL:" lines per reply. Place each URL citation on a new line prefixed with a bullet point."""

# Initialize Session States
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header UI
st.markdown('<div class="main-title">🤖 OptiBot Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Customer Support Chatbot for OptiSigns.com</div>', unsafe_allow_html=True)

# Sidebar configurations
with st.sidebar:
    st.markdown('<div class="sidebar-header">Configuration & Status</div>', unsafe_allow_html=True)
    
    # 1. API Status
    api_key = os.getenv("AI_API_KEY") or os.getenv("API_KEY")
    if api_key:
        st.markdown('API Status: <span class="status-connected">● Active (Gemini)</span>', unsafe_allow_html=True)
    else:
        st.markdown('API Status: <span class="status-disconnected">● Key Missing</span>', unsafe_allow_html=True)
        st.error("AI_API_KEY is not defined in your environment/dotenv file.")
        
    # Model Selector
    model_name = st.selectbox(
        "Choose Gemini Model",
        options=["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro", "gemini-flash-latest", "gemini-2.0-flash"],
        index=3,
        help="If the model experiences high demand (503 error), try switching to another model."
    )

        
    # 2. Knowledge Base Details
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    state_file_path = os.path.join(project_root, "data", "state", "sync_state.json")
    
    articles = {}
    if os.path.exists(state_file_path):
        try:
            with open(state_file_path, "r", encoding="utf-8") as f:
                state_data = json.load(f)
                articles = state_data.get("articles", {})
        except Exception as e:
            st.sidebar.error(f"Error loading state: {e}")
            
    st.markdown("---")
    st.markdown(f"**Knowledge Base: {len(articles)} Documents**")
    
    if articles:
        with st.expander("Show synced document sources"):
            for art_id, art_meta in articles.items():
                title = art_meta.get("title", art_id)
                url = art_meta.get("url", "#")
                st.markdown(f"- [{title}]({url})")
    else:
        st.warning("No sync state found. Run document ingestion sync first.")

    st.markdown("---")
    # System Prompt customizer
    system_prompt = st.text_area("System Instruction Prompt", value=DEFAULT_SYSTEM_PROMPT, height=200)

    # Reset Conversation Button
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Pre-construct file parts for Grounding
file_parts = []
for art_id, art_meta in articles.items():
    file_id = art_meta.get("file_id")
    if file_id:
        file_parts.append({
            "file_data": {
                "mime_type": "text/markdown",
                "file_uri": f"https://generativelanguage.googleapis.com/v1beta/{file_id}"
            }
        })

# Render chat history
import datetime
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "time" in message:
            st.markdown(f'<div style="font-size: 0.75rem; color: #8892b0; text-align: left; margin-top: 4px; margin-right: 5px;">{message["time"]}</div>', unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask OptiBot a question about OptiSigns..."):
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
        st.markdown(f'<div style="font-size: 0.75rem; color: #8892b0; text-align: left; margin-top: 4px; margin-right: 5px;">{current_time}</div>', unsafe_allow_html=True)
    
    st.session_state.messages.append({"role": "user", "content": prompt, "time": current_time})
    
    # Generate bot response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        if not api_key:
            message_placeholder.error("Cannot query model. AI_API_KEY is missing.")
        else:
            # Build API contents payload
            # Format history for Gemini API. Gemini REST API multi-turn format:
            # { "role": "user", "parts": [ { "text": ... } ] }
            # For the very first query, or always, we attach file_parts to the very first user message.
            api_contents = []
            
            # Map history into Gemini's format
            for i, msg in enumerate(st.session_state.messages):
                role = "user" if msg["role"] == "user" else "model"
                parts = [{"text": msg["content"]}]
                
                # Prepend the grounding files to the first user message
                if i == 0 and role == "user":
                    parts = file_parts + parts
                    
                api_contents.append({
                    "role": role,
                    "parts": parts
                })
            
            # Make API Call
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            payload = {
                "contents": api_contents,
                "systemInstruction": {
                    "parts": [{"text": system_prompt}]
                }
            }
            headers = {"Content-Type": "application/json"}
            
            try:
                with st.spinner("OptiBot is typing..."):
                    response = requests.post(url, headers=headers, json=payload, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    candidates = result.get("candidates", [])
                    if candidates:
                        text_response = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        
                        # Render text and timestamp
                        bot_time = datetime.datetime.now().strftime("%I:%M %p")
                        message_placeholder.markdown(text_response)
                        st.markdown(f'<div style="font-size: 0.75rem; color: #8892b0; text-align: left; margin-top: 4px; margin-right: 5px;">{bot_time}</div>', unsafe_allow_html=True)
                        
                        # Add to chat history
                        st.session_state.messages.append({"role": "assistant", "content": text_response, "time": bot_time})
                    else:
                        message_placeholder.error("Empty response candidates from Gemini API.")
                else:
                    message_placeholder.error(f"Gemini API Error (status {response.status_code}): {response.text}")
                    
            except Exception as e:
                message_placeholder.error(f"Error connecting to Gemini API: {e}")
