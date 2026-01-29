#!/usr/bin/env python3
"""
Apple Notes MCP Server

A minimal MCP server that allows reading, creating, and updating Apple Notes.
Does NOT support deleting or other destructive operations.
"""

import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("macos-notes-mcp")


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
    Read the HTML content of a note.

    Args:
        name: The exact name of the note
        folder: The folder containing the note (default: "Notes")

    Returns:
        The note content in HTML format
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
def update_note(name: str, html_content: str, folder: str = "Notes") -> str:
    """
    Update an existing note with HTML content.

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


@mcp.tool()
def create_note(body: str, folder: str = "Notes") -> str:
    """
    Create a new note with HTML content.

    The note's title will be derived from the first line of content.
    Use a title div for best results: <div><b>Title</b></div>

    Args:
        body: The note content in HTML format
        folder: The folder to create the note in (default: "Notes")

    Returns:
        Success message with the new note's name
    """
    escaped_html = body.replace('\\', '\\\\').replace('"', '\\"')

    script = f'''
    tell application "Notes"
        set targetFolder to folder "{folder}"
        set newNote to make new note at targetFolder with properties {{body:"{escaped_html}"}}
        return name of newNote
    end tell
    '''
    note_name = run_osascript(script)
    return f"Created note: {note_name}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
