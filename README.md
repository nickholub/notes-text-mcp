# macos-notes-mcp

MCP server for reading and editing Apple Notes via Claude.

## Requirements

- macOS with Notes.app
- Python 3.10+
- `mcp>=1.2.0` package
- Automation permissions for osascript

## Installation

```bash
cd mcp_server
pip install mcp
```

## Configuration

**Claude Code** - add to `.mcp.json`:
```json
{
  "mcpServers": {
    "apple-notes": {
      "command": "python3",
      "args": ["/path/to/mcp_server/server.py"]
    }
  }
}
```

**Claude Desktop** - add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "apple-notes": {
      "command": "python3",
      "args": ["/path/to/mcp_server/server.py"]
    }
  }
}
```

## Usage

Once configured, ask Claude:
- "List my Apple Notes"
- "Read my Shopping List note"
- "Add eggs to my Shopping List note"
- "Create a new note called Meeting Notes"

## Tools

Supports reading, creating, and updating notes. Intentionally omits delete to prevent accidental data loss.

| Tool | Purpose |
|------|---------|
| `list_notes` | List notes in a folder |
| `read_note` | Read note HTML content |
| `create_note` | Create a new note with HTML content |
| `update_note` | Update note with HTML |

## Limitations

- Cannot access checkbox state directly (stored separately from HTML)
- Cannot detect currently selected note

## Architecture

```
┌─────────────┐     MCP/stdio     ┌─────────────┐    subprocess    ┌───────────┐
│   Claude    │ ◄──────────────► │  server.py  │ ◄──────────────► │ osascript │
│   (Client)  │                   │  (FastMCP)  │                  │           │
└─────────────┘                   └─────────────┘                  └─────┬─────┘
                                                                         │
                                                                         │ AppleScript
                                                                         ▼
                                                                   ┌───────────┐
                                                                   │   Apple   │
                                                                   │   Notes   │
                                                                   └───────────┘
```
