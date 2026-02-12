#!/usr/bin/env python3
"""
Apple Notes MCP Server

A minimal MCP server that allows reading, creating, and updating Apple Notes.
Does NOT support deleting or other destructive operations.
"""

import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("notes-text-mcp")


def _escape_applescript(value: str) -> str:
    """Escape a string for safe interpolation into an AppleScript string literal."""
    return value.replace('\\', '\\\\').replace('"', '\\"')


def run_osascript(script: str) -> str:
    """Execute AppleScript via stdin and return result."""
    result = subprocess.run(
        ["osascript"],
        input=script,
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
    safe_folder = _escape_applescript(folder)
    script = f'''
    tell application "Notes"
        set noteNames to {{}}
        set targetFolder to folder "{safe_folder}"
        repeat with aNote in notes of targetFolder
            set end of noteNames to name of aNote
        end repeat
        set AppleScript's text item delimiters to linefeed
        return noteNames as text
    end tell
    '''
    return run_osascript(script)


@mcp.tool()
def read_note(name: str) -> str:
    """
    Read the HTML content of a note. Searches all folders except Recently Deleted.

    Args:
        name: The exact name of the note

    Returns:
        The note content in HTML format
    """
    safe_name = _escape_applescript(name)
    script = f'''
    tell application "Notes"
        repeat with f in every folder
            if name of f is not "Recently Deleted" then
                try
                    set targetNote to first note of f whose name is "{safe_name}"
                    return body of targetNote
                end try
            end if
        end repeat
        error "Note not found: {safe_name}"
    end tell
    '''
    return run_osascript(script)


@mcp.tool()
def update_note(name: str, html_content: str) -> str:
    """
    Update an existing note with HTML content. Searches all folders except Recently Deleted.

    Args:
        name: The exact name of the note to update
        html_content: The new content in HTML format

    Returns:
        Success message
    """
    safe_name = _escape_applescript(name)
    safe_html = _escape_applescript(html_content)

    script = f'''
    tell application "Notes"
        repeat with f in every folder
            if name of f is not "Recently Deleted" then
                try
                    set targetNote to first note of f whose name is "{safe_name}"
                    set body of targetNote to "{safe_html}"
                    return "OK"
                end try
            end if
        end repeat
        error "Note not found: {safe_name}"
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
    safe_folder = _escape_applescript(folder)
    safe_body = _escape_applescript(body)

    script = f'''
    tell application "Notes"
        set targetFolder to folder "{safe_folder}"
        set newNote to make new note at targetFolder with properties {{body:"{safe_body}"}}
        return name of newNote
    end tell
    '''
    note_name = run_osascript(script)
    return f"Created note: {note_name}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
