# Antigravity CLI (`agy`) Reference

The Antigravity CLI (`agy`) is a lightweight, terminal-based interface for fast
agent interaction.

## 1. Getting Started & TUI Navigation

-   Run the command: `agy`
-   **Authentication**: On first run, press `Enter` to open the browser OAuth
    flow, authenticate, and paste the code back in the terminal.
-   **Keyboard Shortcuts**:
    -   `ESC`: Close active menus (like `/skills` or `/settings`).
    -   `Ctrl+D Ctrl+D` (or /exit or /quit) to exit the CLI.
    -   `Up/Down Arrows`: Navigate command history.

--------------------------------------------------------------------------------

## 2. Interactive Session & TUI Commands (CLI-Only)

These commands are used to manage the terminal interface, workspace directories,
and local conversation context. They are only available in the CLI.

| Command                  | Description                                       |
| :----------------------- | :------------------------------------------------ |
| `/add-dir`               | Adds a new directory path to the active project   |
:                          : workspace.                                        :
| `/agents`                | Lists all active subagents and custom agents.     |
| `/artifact`              | Opens the TUI artifact viewer.                    |
| `/btw`                   | Asks a quick side-question without starting a     |
:                          : full agent run.                                   :
| `/changelog`             | Displays the product changelog and release notes. |
| `/clear` or `/new`       | Clears the terminal screen and scrollback buffer. |
| `/config` or `/settings` | Opens the TUI configuration panel to customize    |
:                          : settings.                                         :
| `/context`               | Lists all files and symbols currently in the      |
:                          : agent's context.                                  :
| `/copy`                  | Copies the last agent response to the system      |
:                          : clipboard.                                        :
| `/credits`               | Displays third-party software licenses and        |
:                          : attributions (external builds only).              :
| `/diff`                  | Displays the current codebase diff of changes     |
:                          : made by the agent.                                :
| `/exit` or `/quit`       | Exits the active Antigravity CLI session.         |
| `/fast`                  | Toggles Fast Mode for typing delays and thought   |
:                          : visualization (external builds only).             :
| `/feedback`              | Opens the product feedback and bug reporting      |
:                          : form.                                             :
| `/fork` or `/branch`     | Forks the current conversation into a new thread, |
:                          : preserving history.                               :
| `/help`                  | Displays the help menu with commands and keyboard |
:                          : shortcuts.                                        :
| `/hooks`                 | Lists all registered lifecycle hooks.             |
| `/keybindings`           | Configures a list of all active CLI keyboard      |
:                          : shortcuts.                                        :
| `/logout`                | Logs out of the active Google account session.    |
| `/mcp`                   | Lists active MCP servers and their exposed tools. |
| `/model`                 | Changes the active Gemini model for the session.  |
| `/open`                  | Opens a file in your preferred local editor.      |
| `/permissions`           | Manages tool execution permissions (allow/deny    |
:                          : lists).                                           :
| `/planning`              | Opens the interactive graphical planning and task |
:                          : list editor (external builds only).               :
| `/rename`                | Renames the active conversation thread.           |
| `/resume`, `/switch` or  | Resumes a past conversation thread by ID or name. |
: `/conversation`          :                                                   :
| `/rewind` or `/undo`     | Rewinds the conversation history to a previous    |
:                          : checkpoint.                                       :
| `/skills`                | Lists all active agent skills.                    |
| `/statusline`            | Toggles the terminal status line.                 |
| `/tasks`                 | Displays the active task list and progress.       |
| `/title`                 | Toggles or configures the terminal title.         |
| `/usage` or `/quota`     | Displays token usage and session cost statistics. |

--------------------------------------------------------------------------------

## 3. Configuration Settings (`settings.json`)

The CLI is configured via **`~/.gemini/antigravity-cli/settings.json`**. Below
are all active exported keys:

JSON Key                  | Type   | Description                                                                                              | Default
:------------------------ | :----- | :------------------------------------------------------------------------------------------------------- | :------
`allowNonWorkspaceAccess` | bool   | Permits the agent to read or write files outside the workspace root.                                     | `false`
`altScreenMode`           | string | Controls alternate screen buffer usage (`default`, `always`, `never`).                                   | `default`
`artifactReviewPolicy`    | string | Controls when the agent asks for artifact review (`always-proceed`, `agent-decides`, `asks-for-review`). | `asks-for-review`
`colorScheme`             | string | The CLI color scheme (`terminal`, `dark`, `light`).                                                      | `terminal`
`editor`                  | string | Preferred editor command for file opening (e.g., `vim`, `nano`, `auto`).                                 | `auto`
`enableTelemetry`         | bool   | Toggles anonymous usage and crash reporting.                                                             | `true`
`enableTerminalSandbox`   | bool   | Runs terminal commands inside a restricted sandbox environment.                                          | `false`
`gcp`                     | object | GCP project and location configurations for cloud-based tools.                                           | `nil`
`historySize`             | int    | Maximum number of history entries persisted to disk (`-1` for unlimited).                                | `2000`
`model`                   | string | The active model identifier used by the main agent.                                                      | `gemini-3.5-flash`
`notifications`           | bool   | Enables system notifications on task completion.                                                         | `false`
`permissions`             | object | Global allow/deny/ask rules for files, commands, and URLs.                                               | `nil`
`runningLightSpeed`       | string | Artificial typing delays to control thought visualization (`off`, `fast`, `medium`, `slow`).             | `medium`
`showFeedbackSurvey`      | bool   | Displays periodic product feedback surveys.                                                              | `true`
`showTips`                | bool   | Displays helpful tips and shortcuts in the CLI.                                                          | `true`
`statusLine`              | object | Configuration for the TUI status line.                                                                   | `nil`
`title`                   | object | Configuration for the TUI title.                                                                         | `nil`
`toolPermission`          | string | Confirmation mode for tools (`always-proceed`, `request-review`, `strict`, `proceed-in-sandbox`).        | `request-review`
`trustedWorkspaces`       | array  | List of directory paths trusted by the user for execution.                                               | `[]`
`useG1Credits`            | bool   | Toggles usage of Google One AI premium quotas.                                                           | `false`
`verbosity`               | string | Detail level of agent trace rendering (`high`, `low`).                                                   | `high`
