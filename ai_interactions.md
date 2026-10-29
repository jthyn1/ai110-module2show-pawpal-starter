# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**Tool:** Claude Code (Claude Opus 5.5), running in the terminal.

**What task did you give the agent?**

I pasted the full PawPal+ assignment and had the agent build it end to end: clone the starter repo, design the UML, write `pawpal_system.py`, `main.py`, the tests, and the Streamlit UI, add the third algorithm (next available slot) plus the priority, persistence, and formatting extensions, and fill in the docs.

**What did the agent do?**

| Step | Files | Commands / checks |
|------|-------|-------------------|
| Set up a project-local virtualenv (the system Python had no `pip`/`venv`, so it bootstrapped pip into `.venv`) | — | `pip install -r requirements.txt` |
| Phase 1: draft UML and dataclass skeletons; wrote reflection 1a/1b | `diagrams/uml_draft.mmd`, `pawpal_system.py`, `reflection.md` | commit `chore: add class skeletons from UML` |
| Phase 2: implemented Owner/Pet/Task/Scheduler, CLI demo, 2 starter tests | `pawpal_system.py`, `main.py`, `tests/test_pawpal.py`, `pytest.ini`, `README.md` | `python main.py`, `python -m pytest` |
| Phase 4: sorting, priority sorting, filtering, recurrence (`timedelta`), conflict detection, **next available slot** (third algorithm), greedy daily plan, JSON save/load, `tabulate` output | `pawpal_system.py`, `main.py`, `requirements.txt`, `README.md`, `reflection.md` | re-ran demo after each change |
| Phase 5: grew the suite to 34 tests (happy paths + edge cases) | `tests/test_pawpal.py`, `README.md`, `reflection.md` | all 34 passed on the first run |
| Phase 3: Streamlit UI connected to the backend with `data.json` persistence | `app.py`, `.gitignore` | drove the UI with `streamlit.testing.v1.AppTest`; smoke-tested `streamlit run` |
| Phase 6: final UML, README, reflection, this log | `diagrams/uml.mmd`, `README.md`, `reflection.md`, `ai_interactions.md` | — |

**What did you have to verify or fix manually?**

<!-- TODO: Add what you personally reviewed or changed after the agent finished. -->

Things that were caught by checking output instead of trusting the first version:

- Emoji like ✂️ and 🍽️ broke `tabulate` column alignment (hidden variation-selector characters). Replaced them with single-character emoji and added `wcwidth`.
- The free-slot demo returned a trivial answer (07:00) for a 40-minute task; changed it to 75 minutes so it demonstrates skipping past busy time.
- Added a guard so marking an already-completed recurring task doesn't create a second "next" copy (important for double-clicks in the UI), with a test.
- The starter repo had a committed `__pycache__/*.pyc` file; it was removed from git since `.gitignore` already excludes it.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
