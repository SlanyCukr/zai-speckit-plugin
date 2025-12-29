# zai-speckit-plugin

A Claude Code plugin for delegating work to **Z.AI GLM-4.7** powered subagents, with **speckit** integration.

## Overview

This plugin implements a delegation-first workflow where Claude orchestrates while subagents (routed to Z.AI's GLM-4.7 via a proxy) execute the actual work. The agents are specifically prompted to work well with GLM-4.7's capabilities.

### How It Works

1. **Claude as Orchestrator**: The main Claude session plans and coordinates
2. **Proxy Routing**: A separate proxy intercepts subagent requests and routes them to Z.AI
3. **GLM-4.7 Execution**: Subagents run on GLM-4.7 for cost-effective, high-quality execution
4. **Speckit Integration**: Hooks automatically inject subagent recommendations for speckit commands

## Installation

### Add to settings.json
```json
{
  "enabledPlugins": {
    "zai-speckit-plugin@zai-speckit": true
  },
  "extraKnownMarketplaces": {
    "zai-speckit": {
      "source": {
        "source": "github",
        "repo": "SlanyCukr/zai-speckit-plugin"
      }
    }
  }
}
```

## Components

### Agents (GLM-4.7 Optimized)

| Agent | Description | Model Hint |
|-------|-------------|------------|
| `build-agent` | Implements code changes with focused task execution | opus |
| `code-reviewer` | Reviews code for bugs/quality (>=80% confidence threshold) | opus |
| `root-cause-agent` | Diagnoses failures with systematic evidence gathering | opus |
| `codebase-explorer` | Fast codebase search and exploration | sonnet |
| `context7-docs` | Library documentation lookup via Context7 | sonnet |
| `web-research` | Web search for docs and best practices | sonnet |
| `chrome-devtools` | Browser automation via Chrome DevTools | sonnet |

### Commands

| Command | Description |
|---------|-------------|
| `/zai-speckit-plugin:analyze-session <session-id>` | Analyze session transcripts to suggest improvements |
| `/zai-speckit-plugin:feature-dev <description>` | Context-efficient feature development workflow |

### Skills

| Skill | Description |
|-------|-------------|
| `jira` | Interact with Jira issues using jira-cli |

### Hooks

| Hook | Event | Description |
|------|-------|-------------|
| **Speckit Subagent Context** | UserPromptSubmit | Detects speckit commands and injects appropriate subagent recommendations |
| **Bash Output Monitor** | PostToolUse | Token efficiency reminder when output exceeds 30 lines |
| **Honesty Validator** | SubagentStop | Validates subagent work follows "Honesty Over Completion" principle |
| **Session Context** | SessionStart | Injects subagent usage reminders |

## Speckit Integration

When you use speckit commands, the plugin automatically injects guidance:

- `speckit.specify` → Recommends `Explore` subagent for pattern discovery
- `speckit.clarify` → Recommends `web-research` and `context7-docs`
- `speckit.plan` → Recommends parallel exploration with multiple subagents
- `speckit.implement` → Recommends delegating tasks to `build-agent` subagents
- `speckit.tasks` → Recommends `Explore` for file structure understanding

## Philosophy

### Delegation First
- **Main session context is precious** - every token counts
- **Subagents run in isolation** - their token usage doesn't pollute main context
- **Parallelization** - run 2-3 subagents simultaneously for efficiency

### Small Chunks Only
Give each subagent ONE focused task. Large chunks lead to:
- Lazy implementations
- Quality degradation
- Silently skipped steps

### Honesty Over Completion
- Not completing work is NOT an error
- The only error is claiming "done" when steps were skipped
- Partial work with clear reporting is SUCCESS

### Early Bail Pattern
Subagents should return early (without doing work) if:
- Task is unclear → ask for clarification
- Task is too broad → suggest how to split
- Confidence is low → explain concerns

## Related Projects

- **Proxy**: Separate repository that intercepts Claude Code requests and routes subagent calls to Z.AI
- **Speckit**: GitHub-based specification workflow that pairs with this plugin

## License

MIT
