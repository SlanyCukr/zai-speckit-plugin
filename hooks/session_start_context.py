#!/usr/bin/env python3
"""SessionStart hook: inject subagent philosophy for main session only."""
import json

SUBAGENT_PHILOSOPHY = """
## Subagent Usage Philosophy

**Subagent usage is PIVOTAL for preserving main session context.** The main session should orchestrate, not execute heavy work.

### Why Subagents
- Main session context is precious - every token counts
- Subagents run in isolation - their token usage doesn't pollute main context
- Parallelization - multiple subagents can work simultaneously
- Specialization - each agent has focused expertise

### Small Chunks Only
**Give each subagent ONE small, focused task.** When subagents receive large chunks of work:
- They become "lazy" and implement only part of the work
- They lose focus and quality degrades
- They may silently skip steps

**Good:** "Implement T1: Create User model in models/user.py"
**Bad:** "Implement all 5 tasks from the plan"

**This is GOOD behavior** - it prevents wasted work and poor quality output.

### Specialized Build Agents
Use language-specific build agents for better code quality:

- **python-build-agent**: Python code with type hints, PEP 8, error handling, Ruff/mypy awareness
- **react-nextjs-agent**: React/Next.js with TanStack Query, TypeScript, feature-based organization

These agents discover repo tooling config before implementing (pyproject.toml, tsconfig.json, package.json).
""".strip()

output = {
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": SUBAGENT_PHILOSOPHY
    }
}
print(json.dumps(output))
