# AZURE DEVOPS MODEL CONTEXT PROTOCOL (MCP) SETUP
=================================================

## 🔌 Connection Overview
- **Azure DevOps Organization:** `anthonydimarcello` ([https://dev.azure.com/anthonydimarcello](https://dev.azure.com/anthonydimarcello))
- **Project:** `osintneoai`
- **MCP Server URL:** `https://mcp.dev.azure.com/anthonydimarcello`
- **Protocol:** HTTP REST / Stream-JSON

---

## 🛠️ Configuration in VS Code & Copilot CLI

Located at `.vscode/mcp.json`:
```json
{
  "servers": {
    "azure-devops": {
      "type": "http",
      "url": "https://mcp.dev.azure.com/anthonydimarcello",
      "description": "Azure DevOps org anthonydimarcello — project osintneoai",
      "headers": {}
    }
  },
  "inputs": []
}
```

---

## 🚀 Capabilities Enabled
1. **Work Item Management:** Query, create, update, and track user stories, bugs, and backlog tasks.
2. **Git Repositories & Pipelines:** Trigger Azure Pipelines, inspect build artifacts, and query branch status.
3. **Task Tracking:** Seamless synchronization between `data/tasks.json`, Kanban `/tasks`, and Azure DevOps Boards.
