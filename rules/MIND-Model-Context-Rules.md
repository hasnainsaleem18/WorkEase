# MIND-Model Context Rules (mind-model-context-rules.md)

## Overview
Preserves **project context** (open files, cursor, breakpoints, types, functions) when switching IDEs or sessions. Works with MIND-Model core rules.

---

## Principles
- **Continuity** – State never disappears.  
- **Comprehension** – IDE instantly knows datatypes, signatures, dependencies.  
- **Seamlessness** – New code merges without conflicts.  
- **Sync** – All metadata stays in lock-step.

---

## Preservation Rules
1. **Session State** – Auto-save on exit, auto-load on open.  
2. **IDE Switch** – Export/Import via `.mind-context.json`.  
3. **VCS Integration** – Auto-commit on switch, pull latest on open.

---

## Synchronization
1. **Cloud / Repo Sync** – GitHub, Dropbox, etc.  
2. **Metadata Sync** – `.env`, lockfiles, build configs.

---

## Project Understanding
### Static Analysis
- Run linters & type-checkers on load.  
- Build AST / code map.  

### Inference
- Infer types & signatures.  
- Suggest completions, validate on edit.  
- Pre-save error prediction.

---

## Development Flow
### Vibe Coding
- Context-aware autocomplete.  
- Safe refactor + post-refactor tests.  
- Breakpoint & watch sync across sessions.

### Additions
- Validate new code vs. existing structure.  
- Incremental builds + hot-reload.  
- Auto-doc generation (JSDoc, Sphinx).

---

## Governance
1. **Context Activation** – Load only if project ID matches.  
2. **Full Scan on Open** – Confirm comprehension.  
3. **Real-time Alerts** – Unresolved refs, type mismatches.  
4. **Auto-Backup** – Before big changes or IDE switch.  
5. **IDE Compatibility Check**.

---

## Integration
- **IDE-agnostic**: VS Code, Cursor, IntelliJ, etc.  
- **Files**: `.mind-context.yaml`, `.mind-project.yaml`  
- **Recommended extensions**: MIND-Context Plugin.

---

## Logging
- **Enabled**, **detailed**  
- Tracks switches, scans, conflicts.

---

## Mitigations
- AI-assisted conflict merge.  
- Scan only changed files for large repos.  
- Allow manual type overrides.  
- Encrypt context files for sensitive projects.

---

*Drop this file into your IDE’s rule folder to keep your FYP context alive across tools.*