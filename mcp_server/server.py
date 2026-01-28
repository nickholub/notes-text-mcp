#!/usr/bin/env python3
"""
Apple Notes MCP Server - Edit Only

A minimal MCP server that allows reading and updating Apple Notes.
Does NOT support creating, deleting, or other destructive operations.
"""

import subprocess
import re
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("apple-notes-edit")


def run_osascript(script: str) -> str:
    """Execute AppleScript and return result."""
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"AppleScript error: {result.stderr}")
    return result.stdout.strip()


def html_to_markdown(html: str) -> str:
    """Convert Apple Notes HTML to Markdown."""
    text = html
    # Checked items
    text = re.sub(r'<li><strike>([^<]+)</strike>(<br>)?</li>', r'- [x] \1', text)
    # Unchecked items
    text = re.sub(r'<li>([^<]+)(<br>)?</li>', r'- [ ] \1', text)
    # Title
    text = re.sub(r'<div><b><span style="font-size: 24px">([^<]+)</span></b>(<br>)?</div>', r'# \1\n', text)
    # Bold
    text = re.sub(r'<b>([^<]+)</b>', r'**\1**', text)
    # Italic
    text = re.sub(r'<i>([^<]+)</i>', r'*\1*', text)
    # Strikethrough
    text = re.sub(r'<strike>([^<]+)</strike>', r'~~\1~~', text)
    # Divs to lines
    text = re.sub(r'<div>([^<]*)</div>', r'\1\n', text)
    # Remove remaining tags
    text = re.sub(r'<ul>|</ul>', '', text)
    text = re.sub(r'<br>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


def markdown_to_html(markdown: str) -> str:
    """Convert Markdown to Apple Notes HTML."""
    lines = markdown.split('\n')
    html_lines = []
    in_list = False

    for line in lines:
        # Title
        if line.startswith('# '):
            html_lines.append(f'<div><b><span style="font-size: 24px">{line[2:]}</span></b><br></div>')
        # Checked item
        elif line.startswith('- [x] '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li><strike>{line[6:]}</strike></li>')
        # Unchecked item
        elif line.startswith('- [ ] '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li>{line[6:]}</li>')
        # Regular list item
        elif line.startswith('- '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li>{line[2:]}</li>')
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            # Bold
            line = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', line)
            # Italic
            line = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', line)
            # Strikethrough
            line = re.sub(r'~~([^~]+)~~', r'<strike>\1</strike>', line)
            if line:
                html_lines.append(f'<div>{line}</div>')
            else:
                html_lines.append('<div><br></div>')

    if in_list:
        html_lines.append('</ul>')

    return ''.join(html_lines)


@mcp.tool()
def list_notes(folder: str = "Notes") -> str:
    """
    List all notes in a folder.

    Args:
        folder: The folder name (default: "Notes")

    Returns:
        A list of note names, one per line
    """
    script = f'''
    tell application "Notes"
        set noteNames to {{}}
        set targetFolder to folder "{folder}"
        repeat with aNote in notes of targetFolder
            set end of noteNames to name of aNote
        end repeat
        set AppleScript's text item delimiters to linefeed
        return noteNames as text
    end tell
    '''
    return run_osascript(script)


@mcp.tool()
def read_note(name: str, folder: str = "Notes") -> str:
    """
    Read the content of a note as Markdown.

    Args:
        name: The exact name of the note
        folder: The folder containing the note (default: "Notes")

    Returns:
        The note content in Markdown format
    """
    script = f'''
    tell application "Notes"
        set targetFolder to folder "{folder}"
        set targetNote to first note in targetFolder whose name is "{name}"
        return body of targetNote
    end tell
    '''
    html = run_osascript(script)
    return html_to_markdown(html)


@mcp.tool()
def read_note_html(name: str, folder: str = "Notes") -> str:
    """
    Read the raw HTML content of a note.

    Args:
        name: The exact name of the note
        folder: The folder containing the note (default: "Notes")

    Returns:
        The note content in raw HTML format
    """
    script = f'''
    tell application "Notes"
        set targetFolder to folder "{folder}"
        set targetNote to first note in targetFolder whose name is "{name}"
        return body of targetNote
    end tell
    '''
    return run_osascript(script)


@mcp.tool()
def update_note(name: str, content: str, folder: str = "Notes") -> str:
    """
    Update an existing note with new content (Markdown format).

    Args:
        name: The exact name of the note to update
        content: The new content in Markdown format
        folder: The folder containing the note (default: "Notes")

    Returns:
        Success message
    """
    html = markdown_to_html(content)
    # Escape for AppleScript
    escaped_html = html.replace('\\', '\\\\').replace('"', '\\"')

    script = f'''
    tell application "Notes"
        set targetFolder to folder "{folder}"
        set targetNote to first note in targetFolder whose name is "{name}"
        set body of targetNote to "{escaped_html}"
        return "OK"
    end tell
    '''
    run_osascript(script)
    return f"Updated note: {name}"


@mcp.tool()
def update_note_html(name: str, html_content: str, folder: str = "Notes") -> str:
    """
    Update an existing note with raw HTML content.

    Args:
        name: The exact name of the note to update
        html_content: The new content in HTML format
        folder: The folder containing the note (default: "Notes")

    Returns:
        Success message
    """
    # Escape for AppleScript
    escaped_html = html_content.replace('\\', '\\\\').replace('"', '\\"')

    script = f'''
    tell application "Notes"
        set targetFolder to folder "{folder}"
        set targetNote to first note in targetFolder whose name is "{name}"
        set body of targetNote to "{escaped_html}"
        return "OK"
    end tell
    '''
    run_osascript(script)
    return f"Updated note: {name}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
