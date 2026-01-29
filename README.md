# macos-notes-mcp

MCP server for reading and editing Apple Notes via Claude.

## Requirements

- macOS with Notes.app
- Python 3.10+
- `mcp>=1.2.0` package
- Automation permissions for osascript

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/macos-notes-mcp.git
   cd macos-notes-mcp
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Get the full path to the server (you'll need this for configuration):
   ```bash
   echo "$(pwd)/mcp_server/server.py"
   ```

## Configuration

Use the path from step 3 above in your configuration.

**Claude Code** - add to `~/.claude/mcp.json` (global) or `.mcp.json` (project):
```json
{
  "mcpServers": {
    "apple-notes": {
      "command": "python3",
      "args": ["/Users/yourname/macos-notes-mcp/mcp_server/server.py"]
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
      "args": ["/Users/yourname/macos-notes-mcp/mcp_server/server.py"]
    }
  }
}
```

**Note:** Replace `/Users/yourname/macos-notes-mcp` with the actual path where you cloned the repository.

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
