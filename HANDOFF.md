# PZ Mod Checker -- Handoff

**Last Updated:** 2026-03-24 (Session 3)

## Current State

Core tool complete. Web GUI v2 polished with full audit fixes. Ready for testing pass.

## What's Working

- **Scanner** -- 51 JSON rules covering B42.0 through B42.15, version-keyed filtering
- **Diagnose** -- Parses console.txt, identifies mod errors with MOD attribution, resolves names to IDs
- **Manager** -- Read/write default.txt, enable/disable mods, profiles, backups
- **Workshop** -- Steam API queries with cache, heuristic classification
- **Bisect** -- Binary search with dependency groups, state persistence, diagnose shortcut
- **CLI** -- 4 subcommands (scan, diagnose, manage, bisect) + --gui flag
- **Web GUI v2** -- Full dashboard at :8642, see below
- **Tests** -- 43+ tests, all passing
- **Packaging** -- pyproject.toml, pip install -e . works, JSON rules
- **GitHub** -- Repo at robotsmeller/pz-mod-checker, 15 issues tracked (#4-#18)

## GUI v2 Features (Session 3)

### Layout
- Global scope bar: Active Mods / All Installed / Profile (persistent, affects all tabs)
- Tab descriptions explaining each tool's use case
- Footer: credits (@robotsmeller), GitHub link, inline User Guide, Dev Mode toggle
- Paginated scan results (25/page) with search filter

### Scan Tab
- Version dropdown from rule files, auto-detects PZ version, labels like "42.15+ (latest)"
- Severity filter toggles (keyboard-accessible, aria-pressed)
- Results sorted by severity (breaking first)
- Inline Disable buttons per mod (via event delegation, XSS-safe)
- "Disable All Breaking" bulk action
- Findings grouped by severity within each mod (breaking expanded, others collapsed)
- Animated +/- indicators (CSS bar collapse)

### Dev Mode (footer toggle, persists in localStorage)
- Rule IDs on each finding
- Per-mod export: Copy TXT / Copy MD / Copy JSON
- Export All: full scan report to clipboard
- Aimed at mod developers debugging their own mods

### Diagnose Tab
- User-friendly require() failure explanations with fix suggestions
- Inline Disable per mod

### Mods Tab
- Sort: A-Z, Z-A, Enabled first, Disabled first
- Scope-aware filtering
- Toggle switches with role="switch", aria-checked, keyboard-accessible

### Bisect Tab
- 3-step onboarding guide (single source, rendered dynamically)

### Infrastructure
- ThreadingHTTPServer prevents UI freezes
- No CORS headers (same-origin only)
- try/except on all handlers returns JSON errors
- 400 on bad JSON, 413 on oversized body
- console.txt parsing cached with mtime
- discover_mods() cached with mtime
- Toast notifications replace all alert()/confirm()
- Themed confirm modal
- Content-Length limit (1MB)

### Accessibility
- Tab bar: role="tablist", role="tab", aria-selected, aria-controls, role="tabpanel"
- Toggle switches: role="switch", aria-checked, tabindex
- Severity pills: role="button", aria-pressed, keyboard handler
- Docs panel: role="dialog", aria-modal, focus trap
- Scope profile select: aria-label
- Severity badges include text labels (brk/wrn/inf)

### Docs
- docs/user-guide.md -- full usage documentation
- README.md -- project landing page (features, roadmap, API, architecture)
- Inline User Guide fetches from GitHub (versioned tag first, main fallback, local fallback)
- Version check: header badge when newer release available

## Open Issues

### Medium (logged, not yet fixed)
- None remaining -- all #14-#18 fixed in session 3

### Future
- #1 -- Crowdsourced mod compatibility data
- #2 -- PyInstaller .exe + pip publish
- #3 -- Documentation updates (ongoing)

## After This Session

### Priority Order
1. ~~GUI improvements~~ Done (session 3)
2. Distribution (PyInstaller .exe + pip publish) -- see issue #2
3. Workshop staleness detection (compare local mod timestamps vs Workshop time_updated)
4. PZwiki API for rule discovery -- deprioritized

## Recent Commits
```
3da57dd Fix 10 audit findings: XSS, accessibility, UX, performance
9acb87d Global scope bar: Active/All/Profile scoping across all tabs
d9e0c47 Tab descriptions, versioned docs, update checker, sort fix
4e00812 Update GitHub URLs to robotsmeller org
2cb7f30 Add inline user guide, split README into project page + docs
a19efca GUI: dev mode, pagination, animated +/-, footer, mod sorting
1aa04f4 Fix GUI init: split fetches so dropdown/header load independently
05b8a89 GUI polish: 17 improvements from audit feedback
```
