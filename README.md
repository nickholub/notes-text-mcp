# NotesEdit

Command-line tools to programmatically edit Apple Notes using AppleScript and Apple Intelligence via Shortcuts.

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

The MCP server acts as a bridge between Claude and Apple Notes:
- **FastMCP Framework**: Handles MCP protocol communication via stdio transport
- **AppleScript Execution**: All Notes operations go through `osascript` subprocess
- **HTML/Markdown Conversion**: Bidirectional conversion between Apple Notes HTML and Markdown

## MCP Server

The `mcp_server/` directory contains an MCP server for direct Claude integration. **Edit-only** - intentionally omits create/delete to prevent accidental data loss.

### Tools

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `list_notes` | List notes in a folder | folder name | Note names (newline-separated) |
| `read_note` | Read note as Markdown | note name, folder | Markdown content |
| `read_note_html` | Read note as raw HTML | note name, folder | HTML content |
| `update_note` | Update note from Markdown | note name, content, folder | Success message |
| `update_note_html` | Update note from HTML | note name, html_content, folder | Success message |

### Installation

```bash
cd mcp_server
pip install mcp
```

### Configuration

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

### Usage Examples

Once configured, ask Claude:
- "List my Apple Notes"
- "Read my Shopping List note"
- "Update my Shopping List to add eggs"

## Shell Scripts

### AI-Powered Editing (ai_edit.sh)

Edit notes with Apple Intelligence via Shortcuts:

```bash
./ai_edit.sh "My Note" grammar      # Fix grammar and spelling
./ai_edit.sh "My Note" rewrite      # Rewrite for clarity
./ai_edit.sh "My Note" summarize    # Summarize content
./ai_edit.sh "My Note" custom "cross off items related to groceries"

DRY_RUN=1 ./ai_edit.sh "My Note" grammar  # Preview without modifying
```

**Prerequisites:** Create these Shortcuts in Shortcuts.app:
- `Notes-Grammar`: Receive Text -> Proofread -> Stop and Output
- `Notes-Rewrite`: Receive Text -> Rewrite -> Stop and Output
- `Notes-Summarize`: Receive Text -> Summarize -> Stop and Output
- `Notes-Custom`: Receive Text -> Use Model -> Stop and Output

See [exploration.md](exploration.md) for detailed setup instructions.

### Other Scripts

| Script | Purpose |
|--------|---------|
| `note_source.sh` | Print HTML body of a note |
| `note_check_item.sh` | Toggle checklist item checked/unchecked |
| `note_edit.sh` | Basic note body modification |
| `note_md_convert.sh` | HTML to Markdown conversion |

## Apple Notes HTML Format

Apple Notes stores content as HTML internally. The MCP server handles conversion automatically.

### HTML/Markdown Conversion

| HTML | Markdown |
|------|----------|
| `<li><strike>text</strike></li>` | `- [x] text` |
| `<li>text</li>` | `- [ ] text` |
| `<b>text</b>` | `**text**` |
| `<i>text</i>` | `*text*` |
| `<strike>text</strike>` | `~~text~~` |
| `<div>text</div>` | `text\n` |

### Supported HTML Tags

| Tag | Purpose | Example |
|-----|---------|---------|
| `<div>` | Paragraph/line container | `<div>Text here</div>` |
| `<br>` | Line break | `<br>` |
| `<b>` | Bold text | `<b>bold</b>` |
| `<i>` | Italic text | `<i>italic</i>` |
| `<u>` | Underlined text | `<u>underline</u>` |
| `<strike>` | Strikethrough text | `<strike>crossed out</strike>` |
| `<span>` | Inline styling container | `<span style="font-size: 24px">Title</span>` |
| `<ul>` | Unordered list (checklist) | `<ul><li>Item</li></ul>` |
| `<ol>` | Ordered list | `<ol><li>Item</li></ol>` |
| `<li>` | List item | `<li>Item text</li>` |
| `<a>` | Hyperlink | `<a href="url">link text</a>` |
| `<table>` | Table | `<table><tr><td>cell</td></tr></table>` |

### Example Note Structure

```html
<div><b><span style="font-size: 24px">Note Title</span></b><br></div>
<div><br></div>
<div>Regular paragraph text.</div>
<div><br></div>
<ul>
<li>Checklist item 1</li>
<li><strike>Completed item</strike></li>
</ul>
```

## Environment Variables

- `FOLDER` - Notes folder to use (default: "Notes")
- `DRY_RUN=1` - Preview changes without modifying

## Requirements

- macOS with Notes.app
- Python 3.10+ (for MCP server)
- `mcp>=1.2.0` package
- macOS 26+ for Apple Intelligence features
- Automation permissions for osascript

## Limitations

- Advanced CSS styling is not supported
- Cannot access checkbox state directly (stored separately from HTML)
- Cannot detect currently selected note
- The Notes app uses its own internal formatting that may differ from standard HTML

## References

- [Apple Notes User Guide](https://support.apple.com/guide/notes/write-and-format-notes-not9474646a9/mac)
- [Automators Forum - HTML in Notes](https://talk.automators.fm/t/pasting-html-rich-text-in-notes/4522)
