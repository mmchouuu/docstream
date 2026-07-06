"""
Unit tests for HtmlNormalizer class.
"""
import unittest

from src.ingestion.normalizer import HtmlNormalizer

class TestHtmlNormalizer(unittest.TestCase):

    def setUp(self) -> None:
        self.normalizer = HtmlNormalizer(base_page_url="https://support.optisigns.com")

    def test_normalize_basic_elements(self) -> None:
        article = {
            "id": 12345,
            "title": "How to Configure Settings",
            "html_url": "https://support.optisigns.com/hc/en-us/articles/12345-How-to-Configure-Settings",
            "updated_at": "2026-07-06T12:00:00Z",
            "slug": "configure-settings",
            "body": "<h1>Configure Guide</h1><p>Follow these <b>simple</b> steps:</p><ul><li>Step 1</li><li>Step 2</li></ul>"
        }
        
        output = self.normalizer.normalize(article)
        
        # Verify metadata headers (YAML front matter)
        self.assertIn("id: 12345", output)
        self.assertIn("title: How to Configure Settings", output)
        self.assertIn("slug: configure-settings", output)
        
        # Verify body elements conversion
        self.assertIn("# Configure Guide", output)
        self.assertIn("Follow these **simple** steps:", output)
        self.assertIn("- Step 1", output)
        self.assertIn("- Step 2", output)

    def test_link_resolution(self) -> None:
        html = '<p>Check out our <a href="/hc/en-us/articles/111-Other">other article</a> for details.</p>'
        markdown = self.normalizer.html_to_markdown(html)
        self.assertEqual(markdown, "Check out our [other article](https://support.optisigns.com/hc/en-us/articles/111-Other) for details.")

    def test_table_conversion(self) -> None:
        html = """
        <table>
            <tr>
                <th>Feature</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>Dashboard</td>
                <td>Active</td>
            </tr>
        </table>
        """
        markdown = self.normalizer.html_to_markdown(html)
        expected = "| Feature | Status |\n| --- | --- |\n| Dashboard | Active |"
        self.assertEqual(markdown, expected)

    def test_code_block_conversion(self) -> None:
        html = '<pre><code class="language-python">print("Hello World")</code></pre>'
        markdown = self.normalizer.html_to_markdown(html)
        self.assertIn("```python\nprint(\"Hello World\")\n```", markdown)

    def test_boilerplate_cleanup(self) -> None:
        html = """
        <nav>Navigation bar</nav>
        <div class="article-body">
            <p>Real article content.</p>
        </div>
        <footer>Page footer</footer>
        <script>alert('hack');</script>
        """
        markdown = self.normalizer.html_to_markdown(html)
        self.assertNotIn("Navigation bar", markdown)
        self.assertNotIn("Page footer", markdown)
        self.assertNotIn("alert", markdown)
        self.assertIn("Real article content.", markdown)

if __name__ == "__main__":
    unittest.main()
