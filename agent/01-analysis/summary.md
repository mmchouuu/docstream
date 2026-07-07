# Project Summary

## Overview

This project is a take-home assignment for the AlphaSphere "The Next Alpha" recruitment process.

The objective is to build a simplified AI-powered customer support assistant similar to OptiSigns' OptiBot.

The application retrieves support articles from the OptiSigns Help Center, converts them into clean Markdown documents while preserving headings, code blocks, and relative links, removes unnecessary navigation elements, uploads the documents into an AI Vector Store or Knowledge Base, and provides an AI Assistant capable of answering user questions using only the uploaded documentation.

Additionally, the application must support automated daily synchronization by detecting newly added or updated articles and uploading only the changed content (delta update).

---

# Project Objectives

- Scrape at least 30 support articles from the OptiSigns Help Center.
- Convert each article into clean Markdown format.
- Preserve headings, code blocks, and relative links while removing navigation and advertisements.
- Upload Markdown documents programmatically to an AI Vector Store or Knowledge Base using the selected AI platform's API.
- Configure an AI Assistant that answers questions based only on the uploaded documentation and provides article citations.
- Deploy the scraper as an automated daily synchronization job.
- Detect new or updated articles and upload only the delta.

---

# Proposed Technologies

- Python
- Zendesk Help Center API
- OpenAI API or Google Gemini API
- OpenAI Vector Store 
- Docker
- GitHub
- Cloud Platform (Railway, Render, DigitalOcean, AWS, or GCP)

---

# Expected Deliverables

- GitHub repository with clean commit history
- Dockerized application
- AI Assistant configured with uploaded knowledge documents
- Automated daily synchronization job
- Incremental (delta) update mechanism
- Job execution logs or latest run artifact
- Screenshot showing the AI Assistant answering a sample question with cited article URLs
- README containing setup instructions, local execution guide, chunking strategy, deployment information, and links to job logs