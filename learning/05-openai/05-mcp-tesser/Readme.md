# MCP Server: Context7

- `MCPServerStreamableHttp` se Context7 MCP server connect hota hai.
- Connected MCP tools agent ko technical references aur library docs dhoondne dete hain.
- User apna sawal deta hai; agent zaroorat par MCP tools use karke jawab deta hai.
- `async with` server connection ko manage karta hai, aur `Runner.run()` agent chalata hai.

**Flow:** Sawal → Agent → Context7 MCP tools (zaroorat par) → Jawab.
