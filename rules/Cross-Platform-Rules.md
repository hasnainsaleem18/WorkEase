# Cross-Platform Development Rules (cross-platform-dev-rules.md)

## Overview
Rules for **Python frameworks** that run everywhere — Linux (your FYP), Windows, macOS, Android, iOS.

---

## Core Principles
- **Scalability** – Grow without rewrite.  
- **Uniqueness** – Agent orchestration, local AI.  
- **Cross-Platform** – Zero OS-specific code.  
- **Issue Coverage** – Security, perf, accessibility.  
- **Modularity** – Plug-and-play components.

---

## Framework Components
| Component | Role | Must-Have |
|-----------|------|-----------|
| `orchestrator` | Central hub | async, thread-safe |
| `integration_layer` | APIs (Slack, Gmail) | OAuth, offline fallback |
| `ai_layer` | Local LLMs | privacy, fast inference |
| `ui_layer` | Desktop/mobile UI | Kivy/PyQt adapters |
| `security_layer` | Auth, encryption | token store, audit |
| `monitoring_layer` | Logs, metrics | real-time, crash reports |

---

## Development Rules
### Scalability
1. **Modular Design** – ABC interfaces + DI.  
2. **Async First** – `asyncio` for I/O.  
3. **Resource Caps** – Profiling hooks.

### Uniqueness
1. **Agent Architecture** – Message protocols.  
2. **Adaptive Learning** – Preference feedback loop.  
3. **Hybrid Mode** – Local ↔ cloud seamless.

### Cross-Platform
1. **Abstraction** – `platformdirs`, `shutil`.  
2. **Packaging** – PyInstaller/BeeWare scripts.  
3. **UI Kits** – Kivy for mobile, Tkinter fallback.

### Issue Coverage
| Area | Rule |
|------|------|
| Errors | Global handler + retry |
| Security | Encrypt secrets, input validation |
| Perf | Cache, lazy load, benchmarks |
| Accessibility | ARIA, keyboard, themes |
| Testing | ≥80 % coverage, CI |
| Docs | Sphinx/MkDocs auto-gen |

---

## Governance
1. **SemVer + Changelogs**  
2. **Pinned Deps + Vulnerability Scan**  
3. **CI/CD** (GitHub Actions)  
4. **Telemetry Opt-in**  
5. **Linux-First** (then extend)

---

## Integration
- **Libs**: `asyncio`, `aiohttp`, `transformers`, `kivy`, `cryptography`  
- **Files**: `framework_rules.yaml`, `project.yaml`

---

## Logging
- **Detailed**, covers events, issues, perf, security.

---

## Mitigations
- Design patterns (MVC, Agent).  
- Docker/VM testing.  
- Sharding for extreme scale.  
- Focus on core innovation.

---

*Use with Forge or any Python framework to ship anywhere.*