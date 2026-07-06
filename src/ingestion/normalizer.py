"""
HTML to Markdown Content Normalizer
"""
import re
import yaml
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup, NavigableString, Tag

class HtmlNormalizer:
    """Parser to clean HTML bodies and convert them into sanitized Markdown documents."""

    def __init__(self, base_page_url: str = "https://support.optisigns.com") -> None:
        self.base_page_url = base_page_url.rstrip("/")

    def normalize(self, article: Dict[str, Any]) -> str:
        """
        Normalize raw article HTML content into structured Markdown with YAML front-matter.
        """
        article_id = article.get("id")
        title = article.get("title", "Untitled")
        source_url = article.get("html_url") or ""
        updated_at = article.get("updated_at") or ""
        
        # Determine slug
        slug = article.get("slug")
        if not slug:
            # Generate slug from title
            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            
        # Clean and convert the body HTML
        raw_html = article.get("body") or ""
        clean_markdown_body = self.html_to_markdown(raw_html)
        
        # Build YAML front-matter metadata
        metadata = {
            "id": article_id,
            "title": title,
            "source_url": source_url,
            "updated_at": updated_at,
            "slug": slug
        }
        
        # Format the final Markdown document
        yaml_header = yaml.dump(metadata, default_flow_style=False, sort_keys=False).strip()
        markdown_doc = f"---\n{yaml_header}\n---\n\n# {title}\n\n{clean_markdown_body}"
        return markdown_doc

    def html_to_markdown(self, html_content: str) -> str:
        """Converts raw HTML string into clean Markdown."""
        if not html_content.strip():
            return ""
            
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Strip script, style, iframe, nav, footer, sidebar elements
        for element in soup(["script", "style", "iframe", "nav", "footer", "aside"]):
            element.decompose()
            
        # Parse recursively starting from the root
        markdown = self._parse_node(soup)
        
        # Post-processing: clean up excessive line breaks and whitespaces
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)
        return markdown.strip()

    def _parse_node(self, node: Any) -> str:
        """Recursively parses a BeautifulSoup node into Markdown."""
        if isinstance(node, NavigableString):
            return node.string or ""
            
        if not isinstance(node, Tag):
            return ""
            
        content = "".join(self._parse_node(child) for child in node.children)
        
        tag_name = node.name.lower()
        
        if tag_name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            level = int(tag_name[1])
            return f"\n\n{'#' * level} {content.strip()}\n\n"
            
        elif tag_name == "p":
            return f"\n\n{content.strip()}\n\n"
            
        elif tag_name == "br":
            return "\n"
            
        elif tag_name in ["ul", "ol"]:
            return f"\n\n{content}\n\n"
            
        elif tag_name == "li":
            # Determine list prefix
            parent = node.parent
            if parent and parent.name == "ol":
                # Find index
                siblings = [child for child in parent.children if isinstance(child, Tag) and child.name == "li"]
                idx = siblings.index(node) + 1
                return f"{idx}. {content.strip()}\n"
            else:
                return f"- {content.strip()}\n"
                
        elif tag_name == "pre":
            # Check for inner <code> block
            code_tag = node.find("code")
            code_content = code_tag.get_text() if code_tag else node.get_text()
            # Determine language if specified in code tag class (e.g. class="language-python")
            lang = ""
            if code_tag and code_tag.has_attr("class"):
                for cls in code_tag["class"]:
                    if cls.startswith("language-"):
                        lang = cls.replace("language-", "")
                        break
            return f"\n\n```{lang}\n{code_content.strip()}\n```\n\n"
            
        elif tag_name == "code":
            # Inline code block if not wrapped in <pre>
            if node.parent and node.parent.name == "pre":
                return content
            return f"`{content.strip()}`"
            
        elif tag_name == "strong" or tag_name == "b":
            return f"**{content}**"
            
        elif tag_name == "em" or tag_name == "i":
            return f"*{content}*"
            
        elif tag_name == "a":
            href = node.get("href", "")
            # Resolve relative links
            if href.startswith("/"):
                href = self.base_page_url + href
            text = content.strip() or href
            return f"[{text}]({href})"
            
        elif tag_name == "img":
            src = node.get("src", "")
            if src.startswith("/"):
                src = self.base_page_url + src
            alt = node.get("alt", "image")
            return f"![{alt}]({src})"
            
        elif tag_name == "table":
            return f"\n\n{self._parse_table(node)}\n\n"
            
        elif tag_name in ["div", "span"]:
            # Treat div and span as transparent wrappers
            return content
            
        return content

    def _parse_table(self, table_node: Tag) -> str:
        """Converts HTML table into Markdown table."""
        rows = []
        for tr in table_node.find_all("tr"):
            row = []
            for td in tr.find_all(["td", "th"]):
                cell_content = "".join(self._parse_node(c) for c in td.children)
                # Remove line breaks inside table cells to preserve format
                cell_content = cell_content.replace("\n", " ").strip()
                row.append(cell_content)
            if row:
                rows.append(row)
                
        if not rows:
            return ""
            
        # Determine number of columns
        num_cols = max(len(r) for r in rows)
        
        # Build markdown table lines
        lines = []
        
        # Header Row
        header_row = rows[0]
        # Pad row if too short
        header_row += [""] * (num_cols - len(header_row))
        lines.append("| " + " | ".join(header_row) + " |")
        
        # Separator Row
        lines.append("| " + " | ".join(["---"] * num_cols) + " |")
        
        # Data Rows
        for data_row in rows[1:]:
            data_row += [""] * (num_cols - len(data_row))
            lines.append("| " + " | ".join(data_row) + " |")
            
        return "\n".join(lines)
