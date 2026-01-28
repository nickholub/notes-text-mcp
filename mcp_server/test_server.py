"""Unit tests for Apple Notes MCP Server."""

import pytest
from unittest.mock import patch, MagicMock
import server


class TestHtmlToMarkdown:
    """Tests for HTML to Markdown conversion."""

    def test_unchecked_item(self):
        html = "<li>buy milk</li>"
        assert server.html_to_markdown(html) == "- [ ] buy milk"

    def test_checked_item(self):
        html = "<li><strike>buy milk</strike></li>"
        assert server.html_to_markdown(html) == "- [x] buy milk"

    def test_checked_item_with_br(self):
        html = "<li><strike>buy milk</strike><br></li>"
        assert server.html_to_markdown(html) == "- [x] buy milk"

    def test_bold(self):
        html = "<div><b>important</b></div>"
        assert server.html_to_markdown(html) == "**important**"

    def test_italic(self):
        html = "<div><i>emphasis</i></div>"
        assert server.html_to_markdown(html) == "*emphasis*"

    def test_strikethrough(self):
        html = "<div><strike>deleted</strike></div>"
        assert server.html_to_markdown(html) == "~~deleted~~"

    def test_title(self):
        html = '<div><b><span style="font-size: 24px">My Title</span></b><br></div>'
        assert server.html_to_markdown(html) == "# My Title"

    def test_mixed_list(self):
        html = "<ul><li>first</li><li><strike>second</strike></li></ul>"
        result = server.html_to_markdown(html)
        assert "- [ ] first" in result
        assert "- [x] second" in result

    def test_plain_div(self):
        html = "<div>plain text</div>"
        assert server.html_to_markdown(html) == "plain text"

    def test_br_becomes_newline(self):
        html = "<div>line1<br>line2</div>"
        result = server.html_to_markdown(html)
        assert "line1" in result
        assert "line2" in result


class TestMarkdownToHtml:
    """Tests for Markdown to HTML conversion."""

    def test_unchecked_item(self):
        md = "- [ ] buy milk"
        assert "<li>buy milk</li>" in server.markdown_to_html(md)

    def test_checked_item(self):
        md = "- [x] buy milk"
        assert "<li><strike>buy milk</strike></li>" in server.markdown_to_html(md)

    def test_regular_list_item(self):
        md = "- item"
        assert "<li>item</li>" in server.markdown_to_html(md)

    def test_bold(self):
        md = "**important**"
        assert "<b>important</b>" in server.markdown_to_html(md)

    def test_italic(self):
        md = "*emphasis*"
        assert "<i>emphasis</i>" in server.markdown_to_html(md)

    def test_strikethrough(self):
        md = "~~deleted~~"
        assert "<strike>deleted</strike>" in server.markdown_to_html(md)

    def test_title(self):
        md = "# My Title"
        result = server.markdown_to_html(md)
        assert '<span style="font-size: 24px">My Title</span>' in result
        assert "<b>" in result

    def test_plain_text(self):
        md = "plain text"
        assert "<div>plain text</div>" in server.markdown_to_html(md)

    def test_empty_line(self):
        md = "line1\n\nline2"
        result = server.markdown_to_html(md)
        assert "<div><br></div>" in result

    def test_list_wrapping(self):
        md = "- [ ] item1\n- [ ] item2"
        result = server.markdown_to_html(md)
        assert result.startswith("<ul>")
        assert result.endswith("</ul>")

    def test_list_closes_before_text(self):
        md = "- [ ] item\nplain text"
        result = server.markdown_to_html(md)
        assert "</ul>" in result
        assert "<div>plain text</div>" in result


class TestRoundTrip:
    """Tests for HTML -> Markdown -> HTML conversion consistency."""

    def test_checklist_roundtrip(self):
        original_md = "- [ ] unchecked\n- [x] checked"
        html = server.markdown_to_html(original_md)
        back_to_md = server.html_to_markdown(html)
        assert "- [ ] unchecked" in back_to_md
        assert "- [x] checked" in back_to_md

    def test_formatting_roundtrip(self):
        original_md = "**bold** and *italic*"
        html = server.markdown_to_html(original_md)
        back_to_md = server.html_to_markdown(html)
        assert "**bold**" in back_to_md
        assert "*italic*" in back_to_md


class TestRunOsascript:
    """Tests for AppleScript execution."""

    @patch("server.subprocess.run")
    def test_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="result\n",
            stderr=""
        )
        result = server.run_osascript("tell application \"Notes\" to return 1")
        assert result == "result"
        mock_run.assert_called_once()

    @patch("server.subprocess.run")
    def test_error(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Script error"
        )
        with pytest.raises(Exception) as exc_info:
            server.run_osascript("invalid script")
        assert "AppleScript error" in str(exc_info.value)


class TestListNotes:
    """Tests for list_notes tool."""

    @patch("server.run_osascript")
    def test_list_notes(self, mock_osascript):
        mock_osascript.return_value = "Note 1\nNote 2\nNote 3"
        result = server.list_notes("Notes")
        assert result == "Note 1\nNote 2\nNote 3"
        assert 'folder "Notes"' in mock_osascript.call_args[0][0]

    @patch("server.run_osascript")
    def test_list_notes_custom_folder(self, mock_osascript):
        mock_osascript.return_value = "Work Note"
        result = server.list_notes("Work")
        assert 'folder "Work"' in mock_osascript.call_args[0][0]


class TestReadNote:
    """Tests for read_note tool."""

    @patch("server.run_osascript")
    def test_read_note_converts_to_markdown(self, mock_osascript):
        mock_osascript.return_value = "<div>Test</div><ul><li>item</li></ul>"
        result = server.read_note("TestNote", "Notes")
        assert "- [ ] item" in result
        assert 'whose name is "TestNote"' in mock_osascript.call_args[0][0]

    @patch("server.run_osascript")
    def test_read_note_custom_folder(self, mock_osascript):
        mock_osascript.return_value = "<div>Content</div>"
        server.read_note("MyNote", "Work")
        assert 'folder "Work"' in mock_osascript.call_args[0][0]


class TestReadNoteHtml:
    """Tests for read_note_html tool."""

    @patch("server.run_osascript")
    def test_read_note_html_returns_raw(self, mock_osascript):
        html = "<div>Test</div><ul><li>item</li></ul>"
        mock_osascript.return_value = html
        result = server.read_note_html("TestNote", "Notes")
        assert result == html


class TestUpdateNote:
    """Tests for update_note tool."""

    @patch("server.run_osascript")
    def test_update_note_converts_markdown(self, mock_osascript):
        mock_osascript.return_value = "OK"
        result = server.update_note("TestNote", "- [ ] item", "Notes")
        assert "Updated note: TestNote" in result
        call_script = mock_osascript.call_args[0][0]
        assert "<li>item</li>" in call_script

    @patch("server.run_osascript")
    def test_update_note_escapes_quotes(self, mock_osascript):
        mock_osascript.return_value = "OK"
        server.update_note("TestNote", 'text with "quotes"', "Notes")
        call_script = mock_osascript.call_args[0][0]
        assert '\\"' in call_script


class TestUpdateNoteHtml:
    """Tests for update_note_html tool."""

    @patch("server.run_osascript")
    def test_update_note_html_raw(self, mock_osascript):
        mock_osascript.return_value = "OK"
        html = "<div>Raw HTML</div>"
        result = server.update_note_html("TestNote", html, "Notes")
        assert "Updated note: TestNote" in result
        call_script = mock_osascript.call_args[0][0]
        assert "Raw HTML" in call_script

    @patch("server.run_osascript")
    def test_update_note_html_escapes_backslash(self, mock_osascript):
        mock_osascript.return_value = "OK"
        server.update_note_html("TestNote", "path\\to\\file", "Notes")
        call_script = mock_osascript.call_args[0][0]
        assert "\\\\" in call_script
