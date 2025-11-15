# Agent Task Logs

This directory contains logs of AI agent tasks performed on the ChirpNeighbors project.

## Purpose

Agent logs provide:
- **Transparency**: What agents did and why
- **History**: Chronological record of automated tasks
- **Context**: Future agents can learn from past work
- **Debugging**: Track down when/how changes were made

## Naming Convention

```
YYYYMMDD_HHMMSS_task-description.md
```

**Examples**:
- `20251115_184034_documentation-setup.md`
- `20251116_093022_dx-optimizer-backend-setup.md`
- `20251117_141500_refactor-audio-pipeline.md`

### Format Breakdown

- `YYYYMMDD`: Date (ISO 8601 format)
- `HHMMSS`: Time in 24-hour format (HH:MM:SS without colons)
- `task-description`: Kebab-case description of the task goal

## File Structure

Each agent log should include:

```markdown
# Agent Log: [Task Name]

**Timestamp**: YYYY-MM-DD HH:MM:SS
**Agent Type**: [Agent name/role]
**Goal**: [Brief goal description]

## Task Summary
[What was accomplished]

## Project Analysis
[Context gathered]

## Actions Completed
[Detailed steps taken]

## Files Modified
[List of files created/modified]

## Next Steps (Recommendations)
[Future work suggestions]

## Metrics
[Quantifiable outcomes]

---

**Agent Status**: ✅ Completed | ⏳ In Progress | ❌ Failed
```

## Best Practices

1. **Create logs immediately** when agent tasks start
2. **Be descriptive** in task descriptions (not just "refactor" but "refactor-audio-pipeline")
3. **Include context** for future agents
4. **List all modified files** for traceability
5. **Suggest next steps** to guide future work
6. **Keep concise** but comprehensive

## Searching Logs

```bash
# Find all logs from a specific date
ls docs/agents/20251115_*

# Search for logs about a topic
grep -r "backend" docs/agents/

# List logs chronologically (most recent last)
ls -1 docs/agents/*.md

# View most recent log
cat $(ls -t docs/agents/*.md | head -1)
```

## Agent Types

Common agent types that may create logs:
- `dx-optimizer`: Developer experience improvements
- `documentation-engineer`: Documentation creation/updates
- `backend-developer`: Backend code changes
- `firmware-developer`: ESP32 firmware work
- `refactoring-specialist`: Code refactoring tasks
- `test-engineer`: Testing infrastructure
- `devops-engineer`: CI/CD and deployment

## Retention

- Keep all logs indefinitely (they're small text files)
- Archive old logs to `docs/agents/archive/` after major milestones if needed
- Reference logs in commit messages when relevant
