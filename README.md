# macos-notes-mcp

Claude Apple Notes integration. An MCP server that lets Claude read, create, and edit your Apple Notes.

## Requirements

- macOS with Notes.app
- Python 3.10+
- `mcp>=1.2.0` package
- Automation permissions for osascript

## Setup

1. Clone and install:
   ```bash
   git clone https://github.com/nickholub/macos-notes-mcp.git
   cd macos-notes-mcp
   pip install -e .
   ```

2. Configure your Claude client:

   **Claude Code** - add to `~/.claude/mcp.json`:
   ```json
   {
     "mcpServers": {
       "apple-notes": {
         "command": "python3",
         "args": ["/path/to/macos-notes-mcp/mcp_server/server.py"]
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
         "args": ["/path/to/macos-notes-mcp/mcp_server/server.py"]
       }
     }
   }
   ```

   To get the full path: `echo "$(pwd)/mcp_server/server.py"`

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

## Testing

```bash
pip install -e ".[dev]"
pytest
```

## Limitations

- Updating a note may change its formatting (especially notes with checklists)
- Checkbox state is stored separately from HTML and cannot be preserved on update

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
