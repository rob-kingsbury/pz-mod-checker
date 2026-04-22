# PZ Mod Checker -- Handoff

**Last Updated:** 2026-04-22 (end of Session 8)

```yaml
session: 9
continue_with: Distribution (#2) — pip publish and/or PyInstaller .exe
blockers: none
```

## Current State

62 rules covering B42.0 through B42.17.0. 76 tests passing. 2 open issues (both deferred). Diagnose require() attribution now working. Unbreaker project spun out as separate repo.

## Session 8 Summary

Added 42.17.0 rules (MapRemotePlayerVisibility, VHS skill tapes). Removed 3 false positive inventory UI rules (ISInventoryPane/ISInventoryPaneContextMenu/ISInventoryPage confirmed present in B42.17). Added enable button to scan page mod cards. Diagnose require() failures: now attributed to calling mods by scanning Lua files. Fixed require scan regex to handle `require "module"` shorthand (no parens). Export buttons (TXT/MD/JSON) added to diagnose require failures section. Spun out Unbreaker as standalone Workshop mod project (c:\xampp\htdocs\unbreaker, github.com/rob-kingsbury/unbreaker).

## What's Working

- **Scanner** -- 60 JSON rules, version-keyed filtering, confidence/group fields
- **Rule Engine** -- Conditional rules (8 condition types, AND logic), _make_finding helper
- **Diagnose** -- Parses console.txt, identifies mod errors, inline disable/delete buttons
- **Manager** -- Enable/disable/delete mods, profiles, backups
- **Workshop** -- Steam API queries with 24h cache, outbound links on Mods + Scan pages
- **Bisect** -- Binary search with dependency groups, state persistence
- **Translate** -- Scans mods for missing EN keys, generates stub shim mod, on/off toggle in GUI
- **CLI** -- 4 subcommands + --gui flag, grouped output with confidence
- **Web GUI v2** -- Dashboard at :8642, all UX issues resolved
- **Tests** -- 73 tests, all passing
- **GitHub** -- 2 open issues (#1, #2)

## Open Issues

| # | Title | Priority |
|---|-------|----------|
| 2 | PyInstaller .exe + pip publish | medium |
| 1 | Future: Crowdsourced mod compatibility data | backlog |

## Session 7 Summary

Added Translation Shim feature: new translate.py module, Translate tab in GUI, 3 API endpoints. Scans mods for missing EN translation keys, generates single stub mod (~/Zomboid/mods/pzmc_translation_shim/) with readable title-cased strings. On/off toggle, options for partial/no-translation inclusion and key format. Fixed 2 false positive rules: removed b42-removed-transferall (ISInventoryTransferAction still exists in B42), narrowed b42-13-itemtag-string to only flag string literals in hasTag/containsTag calls.

## Session 6 Summary

Closed 9 issues. Scan UX: warning/breaking groups auto-expand, mod enabled/disabled status shown in scan results (dimmed card + badge), finding layout improved. Accessibility: keyboard handler for toggle switches, loading states on toggle/bulk. DRY refactor: _cached_mod_status(). Workshop outbound link icon added to Mods and Scan pages. Rule audit: 1912 to 1716 findings, tightened patterns, filesystem-security upgraded to breaking.

## Next Session

### Priority 1: Distribution (#2)
- User discussed but deferred. Options: pip publish (easy, needs Python), PyInstaller .exe (AV flag risk without code signing), hosted site (not viable -- tool needs local filesystem access). Likely path: pip first, documented .exe second.
