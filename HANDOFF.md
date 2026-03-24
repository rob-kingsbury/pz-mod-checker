# PZ Mod Checker — Handoff

**Last Updated:** 2026-03-24

## Current State

Core tool complete and functional. Web GUI v1 deployed. Needs UX polish pass.

## What's Working

- **Scanner** — 51 JSON rules covering B42.0 through B42.15, version-keyed filtering
- **Diagnose** — Parses console.txt, identifies mod errors with MOD attribution, resolves names to IDs
- **Manager** — Read/write default.txt, enable/disable mods, profiles, backups
- **Workshop** — Steam API queries with cache, heuristic classification
- **Bisect** — Binary search with dependency groups, state persistence, diagnose shortcut
- **CLI** — 4 subcommands (scan, diagnose, manage, bisect) + --gui flag
- **Web GUI** — Localhost dashboard at :8642, dark theme, 4 tabs, JSON API
- **Tests** — 52+ tests, all passing
- **Packaging** — pyproject.toml, pip install -e . works, JSON rules (no custom parser)

## Immediate Next: GUI Improvement Pass

Combined feedback from Atlas (architecture), Morgan (UX), Soren (code), and user testing:

### Critical Fixes
1. Remove CORS `Access-Control-Allow-Origin: *` — security risk, not needed for same-origin
2. Switch to `ThreadingHTTPServer` — prevents UI freeze during scan
3. Add try/except to all server handlers — return JSON errors, not crashes
4. Fix JS `api()` to check `res.ok` — handle server errors gracefully
5. Escape single quotes in `esc()` — mod IDs with `'` break onclick handlers

### High Priority UX
6. Version dropdown from rule files — add `/api/versions` endpoint, pre-select detected PZ version
7. "X/Y mods active" in header — show total discovered vs enabled
8. Inline "Disable" buttons on scan/diagnose finding cards — act without switching tabs
9. User-friendly require failure messages — explain what missing modules mean
10. Empty state guidance before first scan — "Press Scan to check your 165 mods..."
11. Replace `alert()` with toast notifications

### Medium Priority
12. Sort scan results by severity (breaking first)
13. Severity filter toggles on scan results
14. "Disable All Breaking" button on scan results
15. Bisect onboarding text (3-step explanation)
16. Content-Length limit on POST bodies
17. Use `get_data_dir()` in server instead of hardcoded path

### User Feedback
- Require failures message needs plain language: "These mods use features removed in B42"
- Use PZ-style colors (green-on-dark)
- Everything should offer fix suggestions, not just report problems

## After GUI Polish

### Priority Order (user-confirmed)
1. ~~Bisect~~ ✅ Done
2. GUI improvements (this pass)
3. Distribution (PyInstaller .exe + pip publish) — see issue #2
4. PZwiki API for rule discovery — deprioritized, user skeptical

### Open Issues
- #1 — Future: Crowdsourced mod compatibility data
- #2 — Enhancement: Localhost Web GUI + PyInstaller .exe distribution
- #3 — Documentation: User Guide (README exists, needs ongoing updates)

## Recent Commits
```
2add07c Migrate rules to JSON, add web GUI, update README
d573eb7 Add comprehensive README / user guide
fde3ab7 Fix YAML parser double-escaping regex patterns
d70a3c1 Audit fixes: false positives, input validation, shared paths, performance
5665746 Add bisect: binary search for the mod crashing PZ
d2a9118 Add version-keyed rules for B42.8 through B42.15
1e6b265 Add diagnose, manager, and workshop modules with CLI subcommands
478ef74 Audit fixes: security, correctness, performance, packaging
ac543bd Fix Workshop mod discovery: handle mods/ subdirectory
9a94744 Initial project: PZ Mod Checker v0.1.0
```
