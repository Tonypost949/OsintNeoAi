---
name: mcp-reference-servers
description: >-
  Reference patterns, setup procedures, and tool options for official Model Context Protocol (MCP) servers
  from modelcontextprotocol/servers (Filesystem, Fetch, Git, Memory, Sequential Thinking, Time, Everything).
---

# Official MCP Reference Servers Guide (`modelcontextprotocol/servers`)

The `modelcontextprotocol/servers` repository provides official reference implementations demonstrating core MCP features, tools, resources, and SDK usage.

---

## Standard Reference Servers Overview

| Server | Primary Purpose | Capabilities | Example Command / Config |
| :--- | :--- | :--- | :--- |
| **Filesystem** | Secure file system operations with directory scoping | File read/write, list directory, search | `npx -y @modelcontextprotocol/server-filesystem /path/to/dir` |
| **Fetch** | Web content retrieval & conversion for LLMs | HTTP fetch, HTML-to-markdown conversion | `uvx mcp-server-fetch` |
| **Git** | Repository search, diff inspection, and history reading | Read commits, search diffs, inspect status | `uvx mcp-server-git` |
| **Memory** | Knowledge graph persistent memory store | Entity & relation creation, graph search | `npx -y @modelcontextprotocol/server-memory` |
| **Sequential Thinking** | Step-by-step problem-solving & thought tracking | Dynamic thought logging & revision | `npx -y @modelcontextprotocol/server-sequential-thinking` |
| **Time** | Timezone parsing and time conversions | Current time, timezone math | `uvx mcp-server-time` |
| **Everything** | Comprehensive test server for MCP capabilities | Prompts, tools, resources, sampling | `npx -y @modelcontextprotocol/server-everything` |

---

## Standard MCP Client Configuration Pattern (`mcp.json` / `settings.json`)

To add any official reference server to an agent workspace:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\OsintNeoAi"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

---

## Usage & Best Practices

1. **Security & Directory Scoping**: When configuring `@modelcontextprotocol/server-filesystem`, explicitly pass authorized root directories to enforce security bounds.
2. **Execution Runtimes**: NPM packages use `npx -y @modelcontextprotocol/server-<name>`. Python-based reference tools utilize `uvx mcp-server-<name>`.
3. **Reference vs Production**: Reference servers demonstrate protocol capabilities; verify production readiness or custom transport options when deploying for enterprise environments.
