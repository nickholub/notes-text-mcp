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
- "Update my Shopping List to add eggs"

## Tools

Edit-only by design - intentionally omits create/delete to prevent accidental data loss.

| Tool | Purpose |
|------|---------|
| `list_notes` | List notes in a folder |
| `read_note` | Read note as Markdown |
| `read_note_html` | Read note as raw HTML |
| `update_note` | Update note with Markdown |
| `update_note_html` | Update note with HTML |

## Limitations

- Cannot access checkbox state directly (stored separately from HTML)
- Cannot detect currently selected note
- Advanced CSS styling not supported

## Architecture

```
┌─────────────┐     MCP/stdio     ┌─────────────┐    subprocess    ┌───────────┐
│   Claude    │ ◄──────────────► │  server.py  │ ◄──────────────► │ osascript │
│   (Client)  │                   │  (FastMCP)  │                  │           │
└─────────────┘                   └─────────────┘                  └─────┬─────┘
                                        │                                │
                                        │ HTML ◄─► Markdown              │ AppleScript
                                        │ conversion                     ▼
                                                                   ┌───────────┐
                                                                   │   Apple   │
                                                                   │   Notes   │
                                                                   └───────────┘
```

- **FastMCP Framework**: Handles MCP protocol communication via stdio
- **AppleScript Execution**: All Notes operations go through `osascript`
- **HTML/Markdown Conversion**: Bidirectional conversion for natural editing

## HTML Format Reference

Apple Notes stores content as HTML. The server converts to/from Markdown automatically.

| HTML | Markdown |
|------|----------|
| `<li><strike>text</strike></li>` | `- [x] text` |
| `<li>text</li>` | `- [ ] text` |
| `<b>text</b>` | `**text**` |
| `<i>text</i>` | `*text*` |
| `<strike>text</strike>` | `~~text~~` |
| `<div>text</div>` | `text\n` |
