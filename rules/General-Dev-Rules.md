# General Vibe-Tool Development Rules (general-dev-rules-vibe-tools.md)

## Overview
Ensures **AI-assisted IDEs** (Cursor, Windsurf, etc.) stay stable, fast, and helpful on complex projects.

---

## Core Principles
- **Stability** – No crashes under load.  
- **Efficiency** – Instant feedback.  
- **Scalability** – Handles 10k+ files.  
- **User-Centric** – Flow-state first.  
- **Resilience** – Graceful recovery.

---

## Context Management
### Preservation
1. **Persistent State** – Save open tabs, variables, config.  
2. **Tool Switch** – Export/Import `.dev-context.json`.  
3. **VCS Auto-Commit** on milestones.

### Sync
- Real-time across devices.  
- Dependency lockfile sync.

---

## Project Understanding
### Analysis
- Full AST on load, incremental updates.  
- Dependency graph + cycle detection.  
- Auto-lint/format on save.

### Inference
- Smart completions (relevance ≥ 0.8).  
- Type & signature enforcement.  
- Cyclomatic complexity alerts (>10).

---

## Development Flow
### Vibe Coding
- Distraction-free mode, hotkeys.  
- Live preview + hot-reload.  
- Time-travel debugging + AI bug hints.

### Complex Projects
- Enforce modular imports.  
- Lazy-load heavy modules.  
- Auto-save before risky ops (undo depth 100).

### Additions
- Test-on-change, compatibility check.  
- Refactor preview + post-test.  
- Auto-doc sync.

---

## Collaboration
- Live co-editing with conflict UI.  
- Built-in PR/review threads.

---

## Governance
1. **Activation Threshold** – Only for projects >50 files.  
2. **User Overrides** – Configurable per rule.  
3. **Performance Monitoring** – Alerts on lag.  
4. **Auto-Update** – New language support.  
5. **Security Scans** on build.

---

## Integration
- **Tool-agnostic**  
- Files: `.dev-context.yaml`, `.dev-rules.yaml`  
- Extensions: AI-Assist, VCS.

---

## Logging
- **Balanced** level  
- Tracks changes, errors, perf, suggestions.

---

## Mitigations
- Throttle suggestions in huge repos.  
- Manual fallback mode.  
- Learn from project history.  
- CPU/memory caps.

---

*Load into Cursor/Windsurf → “Vibe Mode” for a buttery dev experience.*