# notes-text-mcp

Claude Apple Notes integration. An MCP server that lets Claude read, create, and edit your Apple Notes.

## Requirements

- macOS with Notes.app
- Python 3.10+
- `mcp>=1.2.0` package
- Automation permissions for osascript

## Setup

1. Clone and install:
   ```bash
   git clone https://github.com/nickholub/notes-text-mcp.git
   cd notes-text-mcp
   pip install -e .
   ```

2. Configure your Claude client:

   **Option A:** From the project directory, ask Claude Code:
   > Add the notes-text MCP server from this project to Claude Code and Claude Desktop configs

   **Option B:** Manual configuration:

   **Claude Code** - add to `~/.claude/.mcp.json`:
   ```json
   {
     "mcpServers": {
       "notes-text": {
         "command": "python3",
         "args": ["/path/to/notes-text-mcp/mcp_server/server.py"]
       }
     }
   }
   ```

   **Claude Desktop** - add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "notes-text": {
         "command": "python3",
         "args": ["/path/to/notes-text-mcp/mcp_server/server.py"]
       }
     }
   }
   ```

## Usage

Once configured, ask Claude:
- "List my Apple Notes"
- "Create a new note called Meeting Notes"
- "Analyze ideas in my Ideas note and add pros and cons for them"
- "Assign priority to items in my Project Backlog note"
- "Correct grammar in my Project Backlog note"
- "Tell me which exercises I did this Mon and Tue in my Journal note"
- "Add eggs to my Shopping List note"

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
