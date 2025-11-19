# MIND-Model Rules (mind-model-rules.md)

## Overview
MIND-Model (Mesh Integration Networked Development Model) is a **non-linear, AI-ready SDLC** that treats every phase as an interconnected node. Use this file as a reference or load it into Cursor/Windsurf to enforce the mesh workflow.

---

## Core Nodes
| ID | Name | Description | Typical Connections |
|----|------|-------------|---------------------|
| `requirements` | **Requirements (R)** | Gather user, system & business needs | `design`, `testing`, `maintenance` |
| `design` | **Design (D)** | Architecture, DB schema, UI/UX, APIs | `requirements`, `coding`, `security` |
| `coding` | **Coding / Development (C)** | Implementation | `design`, `testing`, `documentation` |
| `testing` | **Testing / QA (T)** | Validation & verification | `coding`, `requirements`, `deployment` |
| `deployment` | **Deployment (DP)** | Release to production | `testing`, `maintenance`, `documentation` |
| `maintenance` | **Maintenance (M)** | Updates, bug-fixes, monitoring | `requirements`, `coding`, `testing` |

---

## Extended (Optional) Nodes
| ID | Name | Description |
|----|------|-------------|
| `security` | **Security (S)** | Threat modeling, compliance | `design`, `testing`, `deployment` |
| `documentation` | **Documentation (DOC)** | Guides, API docs | `coding`, `deployment`, `maintenance` |
| `operations` | **DevOps / Ops (OPS)** | CI/CD, infra | `deployment`, `testing`, `maintenance` |
| `ux` | **User Experience (UX)** | Usability testing | `design`, `testing`, `feedback_analytics` |
| `feedback_analytics` | **Feedback & Analytics (FA)** | Metrics, user behavior | `requirements`, `maintenance`, `testing` |

---

## Connection Rules
- **Bidirectional**: **Yes** – every link works both ways.  
- **Min connections per node**: **2**  
- **Max connections per node**: **4**  
- **Flow types**: forward, backward, lateral.

---

## Flow & Execution
- **Multidirectional**: Enabled  
- **Parallel execution**: Enabled  
- **Dynamic entry points**  
  - New project → `requirements`  
  - Legacy → `maintenance`  
  - AI-driven → `feedback_analytics`

---

## AI Integration (toggle in IDE)
- **Enabled**: `false` (default)  
- **Mode**: `central` (or `distributed`)  
- **Central AI node** (`ai_assist`) connects to **all** active nodes.  
- **Human approval** required for every AI suggestion.

---

## Governance
1. **Node Activation** – Needs valid input from ≥1 connected node.  
2. **Feedback** – Every node must publish output (logs, reports).  
3. **Path Logging** – Record every transition as a *Mesh Path*.  
4. **Exit Condition** – Success metrics (coverage, reviews) must pass.  
5. **Scalability** – Turn extended nodes on/off via project config.

---

## Scalability Tiers
| Tier | Nodes | AI |
|------|-------|----|
| **Light** | 6 core only | Off |
| **Standard** | Core + `security`, `ops`, `doc` | Off |
| **Enterprise** | All nodes | On |

---

## Logging
- **Enabled**: Yes  
- **Level**: `detailed`  
- **Features**: node state, feedback loops, mesh-graph visualisation.

---

## Mitigations
- Use **pathway templates** for common flows.  
- Assign a **Navigator** role for decision making.  
- Enable **graph view** in the IDE.  
- Define **per-node success metrics** upfront.

---

*Load this file in Cursor/Windsurf → “Enable MIND-Model” to get auto-node suggestions, path visualisation, and AI assistance.*