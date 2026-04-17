---
name: skill-audit-and-recovery
description: Audit a local skills directory for which skills still work, which need fixes, and which should be archived. Use when inheriting an external/custom skill library or cleaning up stale agent skills.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [skills, audit, maintenance, migration, cleanup]
---

# Skill Audit and Recovery

Use this skill when the user asks things like:
- “Check whether these skills still work.”
- “Help me recycle / clean up skills.”
- “Audit this external `skills/` directory.”
- “Make a keep / fix / archive list for these skills.”

This is especially useful for skills copied from another agent system (old Claw/ClawHub/OpenClaw/custom registries) where docs may no longer match the current runtime.

## Goal

Produce a practical classification for each skill:
- keep
- keep but fix
- archive/remove

Also generate a concrete todo list in the todo tool.

## Workflow

1. Load planning context if needed
- If the user explicitly wants a plan only, use plan mode.
- Otherwise do the audit directly.

2. Verify the target directory exists
- Translate Windows paths into WSL paths when needed, e.g. `C:\root\clawd\skills` -> `/mnt/c/root/clawd/skills`.
- Use read-only inspection first.
- Prefer:
  - `search_files(target='files')` to inventory files
  - lightweight existence checks via `terminal` only if needed

3. Inventory each skill folder
For each top-level skill, look for:
- `SKILL.md`
- metadata files such as `skill.json`, `package.json`, `.clawhub/origin.json`
- setup scripts
- runtime scripts under `scripts/`

4. Validate the skill structurally
Check:
- Does `SKILL.md` exist?
- Do referenced scripts/files actually exist?
- Do documented commands match the shipped files?
- Is it tied to an old tool API or agent runtime?

Typical stale patterns:
- Docs mention scripts that do not exist (`setup.ps1`, `transcribe.cmd`, etc.)
- Script paths reference renamed folders
- Skill text assumes obsolete tool calls (`browser(action="start")`, legacy `message(...)`, old relay/MCP-specific APIs)
- Metadata name does not match folder/skill naming
- Wrapper tasks/scripts still call a missing extractor entrypoint (for example `scripts/x-hotlist.mjs`) while only helper files like scoring/summarization remain; in that case, treat the acquisition path as broken even if some post-processing logic is salvageable

5. Validate environment assumptions
Check only the minimum required binaries actually referenced by the skill.
Examples:
- `python3`
- `ffmpeg`
- `whisper`
- `powershell.exe` / `pwsh`

Do not assume dependencies are present; verify with command lookup.

6. Classify each skill
Use these buckets:
- Keep: structure and assumptions look consistent
- Keep but fix: useful skill, but docs/scripts mismatch or minor path/tooling issues
- Archive/remove: built for an obsolete runtime, duplicated by a better skill, or too broken/stale to trust

7. Create a todo list
Record actionable cleanup items in the todo tool, for example:
- archive obsolete skill
- decide between overlapping skills
- fix wrong script path
- update docs to match actual files
- confirm whether an API-backed skill is still used

8. Summarize briefly for the user
For each skill provide:
- status
- why
- recommended action

## Heuristics from experience

- Documentation-only/API skills can still be worth keeping even without local scripts, if their API/service is still relevant.
- Old browser relay / legacy tool-call syntax is a strong signal the skill is stale unless the user still runs that exact system.
- If two skills overlap and one is actively script-backed while the other depends on a missing CLI, prefer the script-backed one.
- A single wrong script path is usually a “fix”, not an “archive”.
- Missing Windows helper scripts in docs is a common drift issue when only Linux/WSL files were checked in.

## Output format

Keep the final report concise:
- discovered skills
- keep / fix / archive decisions
- top reasons
- todo list created

## Example findings

- `x-hotlist-chrome`: archive/remove if it depends on obsolete browser relay commands no longer supported in the current agent.
- `windows-nircmd-tg`: keep but fix if PowerShell references the wrong skill folder name.
- `faster-whisper`: keep but fix if Linux files exist but docs claim missing Windows scripts exist.
- `openai-whisper`: archive/remove if it duplicates a better local transcription skill and required CLI is absent.
- `deepread-ocr`: keep if it is mostly API documentation and still plausibly useful.
