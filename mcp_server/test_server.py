"""Unit tests for Apple Notes MCP Server."""

import pytest
from unittest.mock import patch, MagicMock
from mcp_server import server


class TestRunOsascript:
    """Tests for AppleScript execution."""

    @patch("mcp_server.server.subprocess.run")
    def test_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="result\n",
            stderr=""
        )
        result = server.run_osascript("tell application \"Notes\" to return 1")
        assert result == "result"
        mock_run.assert_called_once()

    @patch("mcp_server.server.subprocess.run")
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

    @patch("mcp_server.server.run_osascript")
    def test_list_notes(self, mock_osascript):
        mock_osascript.return_value = "Note 1\nNote 2\nNote 3"
        result = server.list_notes("Notes")
        assert result == "Note 1\nNote 2\nNote 3"
        assert 'folder "Notes"' in mock_osascript.call_args[0][0]

    @patch("mcp_server.server.run_osascript")
    def test_list_notes_custom_folder(self, mock_osascript):
        mock_osascript.return_value = "Work Note"
        server.list_notes("Work")
        assert 'folder "Work"' in mock_osascript.call_args[0][0]


class TestReadNote:
    """Tests for read_note tool."""

    @patch("mcp_server.server.run_osascript")
    def test_read_note_returns_html(self, mock_osascript):
        html = "<div>Test</div><ul><li>item</li></ul>"
        mock_osascript.return_value = html
        result = server.read_note("TestNote", "Notes")
        assert result == html
        assert 'whose name is "TestNote"' in mock_osascript.call_args[0][0]

    @patch("mcp_server.server.run_osascript")
    def test_read_note_custom_folder(self, mock_osascript):
        mock_osascript.return_value = "<div>Content</div>"
        server.read_note("MyNote", "Work")
        assert 'folder "Work"' in mock_osascript.call_args[0][0]


class TestUpdateNote:
    """Tests for update_note tool."""

    @patch("mcp_server.server.run_osascript")
    def test_update_note(self, mock_osascript):
        mock_osascript.return_value = "OK"
        result = server.update_note("TestNote", "<div>content</div>", "Notes")
        assert "Updated note: TestNote" in result
        call_script = mock_osascript.call_args[0][0]
        assert "<div>content</div>" in call_script

    @patch("mcp_server.server.run_osascript")
    def test_update_note_escapes_quotes(self, mock_osascript):
        mock_osascript.return_value = "OK"
        server.update_note("TestNote", '<div>text with "quotes"</div>', "Notes")
        call_script = mock_osascript.call_args[0][0]
        assert '\\"' in call_script

    @patch("mcp_server.server.run_osascript")
    def test_update_note_escapes_backslash(self, mock_osascript):
        mock_osascript.return_value = "OK"
        server.update_note("TestNote", "<div>path\\to\\file</div>", "Notes")
        call_script = mock_osascript.call_args[0][0]
        assert "\\\\" in call_script


class TestCreateNote:
    """Tests for create_note tool."""

    @patch("mcp_server.server.run_osascript")
    def test_create_note(self, mock_osascript):
        mock_osascript.return_value = "New Note"
        result = server.create_note("<div><b>New Note</b></div>", "Notes")
        assert "Created note: New Note" in result
        call_script = mock_osascript.call_args[0][0]
        assert "make new note" in call_script
        assert "<div><b>New Note</b></div>" in call_script

    @patch("mcp_server.server.run_osascript")
    def test_create_note_custom_folder(self, mock_osascript):
        mock_osascript.return_value = "Work Note"
        server.create_note("<div>Content</div>", "Work")
        call_script = mock_osascript.call_args[0][0]
        assert 'folder "Work"' in call_script

    @patch("mcp_server.server.run_osascript")
    def test_create_note_escapes_quotes(self, mock_osascript):
        mock_osascript.return_value = "Test"
        server.create_note('<div>text with "quotes"</div>', "Notes")
        call_script = mock_osascript.call_args[0][0]
        assert '\\"' in call_script

    @patch("mcp_server.server.run_osascript")
    def test_create_note_escapes_backslash(self, mock_osascript):
        mock_osascript.return_value = "Test"
        server.create_note("<div>path\\to\\file</div>", "Notes")
        call_script = mock_osascript.call_args[0][0]
        assert "\\\\" in call_script
