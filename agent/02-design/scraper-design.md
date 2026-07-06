# Scraper & Ingestion Pipeline Design

This document details the architecture, processing workflow, normalization rules, and validation criteria for the documentation scraper.

---

## 1. Purpose
The purpose of the scraper is to automatically harvest documentation articles from the external Help Center, clean them of web boilerplate, convert them to standardized Markdown, and output them as structured knowledge files ready for AI consumption.

---

## 2. Data Source
- **Official Help Center:** The raw documentation repository located at `support.optisigns.com`.
- **Primary Interface (Zendesk API):** The Zendesk Help Center Rest API (e.g., `/api/v2/help_center/en-us/articles.json`) serves as the primary endpoint.
- **Fallback Interface (HTML Crawling):** If the official API is unavailable or insufficient for the required content, HTML parsing may be used as a fallback.

### Why the API Interface is Preferred
- **Data Integrity:** The API returns clean, isolated body text without wrapper templates, navigation menus, footers, or script injections.
- **Performance:** JSON payloads are lightweight, reducing bandwidth and parsing overhead.
- **Consistency:** Structured REST response objects avoid parsing fragility associated with changes in webpage layout or CSS selectors.
- **Native Metadata:** The API directly exposes system fields (e.g., timestamps, unique IDs, category groupings) necessary for sync management.

---

## 3. Scraping Workflow

```text
[ Article Discovery ]
          │ (Get list of active articles & URLs)
          ▼
[ Article Retrieval ]
          │ (Fetch raw content payload/HTML)
          ▼
[ Content Extraction ]
          │ (Isolate article body from markup)
          ▼
[   HTML Cleaning   ]
          │ (Discard layout wrappers, ads, nav panels)
          ▼
[Markdown Conversion]
          │ (Format headers, lists, code, relative links)
          ▼
[Metadata Generation]
          │ (Compute checksums, compile tracking fields)
          ▼
[   Local Storage   ] ──➔ Output Files (data/markdown/)
```

1. **Article Discovery:** Request the article index to identify active document links, IDs, and modifications.
2. **Article Retrieval:** Fetch raw HTML or JSON payloads for each discovered article.
3. **Content Extraction:** Pinpoint and isolate the core article content container from the payload.
4. **HTML Cleaning:** Discard formatting clutter, tracking scripts, navigation blocks, and advertisements.
5. **Markdown Conversion:** Translate elements to standard Markdown syntax while preserving heading hierarchies, code sections, tables, lists, and relative hyperlinks.
6. **Metadata Generation:** Calculate the document signature (checksum) and append routing parameters (e.g., source URL, slug, identifiers).
7. **Local Storage:** Save the output as a Markdown file in the designated runtime folder.

---

## 4. Article Metadata
Each generated Markdown document should contain metadata associated with the article, including:
- **Article ID:** Unique identifier from the source system. Used to match local files with remote documents and trace vector store versions.
- **Title:** The original article title. Helps indexers search and represent article topics.
- **Source URL:** The direct absolute web address. Used for citation output by the AI Assistant.
- **Last Updated Time:** System timestamp of the last revision. Assists in tracking modification states.
- **Signature (Hash Checksum):** Content signature of the normalized Markdown. Used to detect content changes (deltas) between synchronization runs.
- **Filename Slug:** A sanitized, URL-friendly string representing the title. Ensures clean and cross-platform compatible filenames.
The metadata may be stored as YAML front matter or another structured format depending on implementation.
---

## 5. HTML Normalization

### Elements to Preserve
- **Headings (`<h1>` to `<h6>`):** Vital for structural hierarchy and chunking algorithms.
- **Paragraphs (`<p>`) & Line Breaks (`<br>`):** Maintain semantic flow.
- **Lists (`<ul>`, `<ol>`, `<li>`):** Retain sequential and step-by-step instructions.
- **Code Blocks (`<pre>`, `<code>`):** Essential for developer syntax and code configurations.
- **Tables (`<table>`, `<tr>`, `<td>`):** Retain structured tabular statistics or features.
- **Relative Hyperlinks (`<a>`):** Preserved and rebased into absolute URLs referencing the live help portal.
- **Images (`<img>`):** Preserve image references when useful for understanding the documentation.
Downloading or processing image assets is outside the current project scope.

### Elements to Remove
- **Navigation Elements (`<nav>`, menus, sidebars):** Irrelevant to article substance.
- **Footers & Breadcrumbs:** Repetitive layout metadata that degrades RAG relevance.
- **Advertisements & Trackers (`<script>`, `<iframe`>):** Intrusive markup that introduces security concerns and bloats token size.
- **Custom Styling Blocks (`<style>`, `class`/`id` inline tags):** Non-standard presentation layouts.

---

## 6. Markdown Output
The generated Markdown file must conform to a standardized layout:
1. **Front-Matter Block:** Contains the defined metadata keys.
2. **Title Header:** The article title formatted as a top-level heading.
3. **Article Body:** The clean, normalized Markdown representation of the support article content.

---

## 7. Error Handling
- **Request Timeout:** The scraper must implement connection and read timeout thresholds. On timeout, it must retry the request up to a defined limit before logging a failure and continuing to the next article.
- **API Failure:** If the API returns server errors (e.g., status 500), the scraper must log the article ID as failed and gracefully skip it, preserving the execution flow for remaining documents.
- **Malformed HTML:** If the content normalizer encounters corrupt markup, it must fall back to basic text extraction rules, log a warning, and avoid outputting raw HTML characters into the Markdown file.
- **Missing Article (404):** If a previously known article is missing from the source, it must be flagged for deletion in the local synchronization index.
- **Rate Limiting (429):** The application must intercept rate limit signals, inspect recovery parameters (e.g., retry-after headers), pause execution, and resume once the window clears.
- **Authentication Failure:** If authentication or API credentials are invalid, the synchronization job should terminate gracefully with a clear error message.

---

## 8. Performance Considerations
- **Pagination:** The discovery engine must follow paging keys to retrieve the full article list without missing documents.
- **Retry Policy:** Employ an exponential backoff retry strategy for transient connection errors.
- **Request Throttling:** Introduce structured pauses between network operations to avoid excessive request rates..
- **Duplicate Detection:** Compare checksum signatures before writing outputs to disk to minimize unnecessary disk operations and file modifications.

---

## 9. Assumptions
- The Help Center portal allows automated client requests without requiring CAPTCHA verification.
- Article structures contain a identifiable body block separating documentation text from site navigation templates.
- Article URLs map cleanly to titles and slug schemes.
- The Help Center API exposes sufficient metadata (such as article IDs and update timestamps) to support incremental synchronization.

---

## 10. Success Criteria
The scraping pipeline is successful when:
- At least 30 valid support articles are retrieved and processed.
- The output Markdown files are free of HTML scripts, wrappers, and styling.
- All files contain the required metadata block populated with valid values.
- Unchanged documents are recognized and skipped during processing.
- The generated Markdown documents are ready for upload to the AI knowledge base.

## 11. Design Decisions
- Prefer Zendesk API over HTML parsing.
- Normalize content before storage.
- Preserve document structure.
- Keep scraping independent from AI upload.
- Generate deterministic filenames.