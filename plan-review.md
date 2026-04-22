# Pre-Flight Plan Review
**Plan**: Build a require shim generator for PZ Mod Checker: scans diagnose results, categorizes missing require() modules into vanilla-global-redirects vs empty stubs, generates a pzmc_require_shim mod with stub Lua files.
**Date**: 2026-04-22
**Reviewers**: Soren (implementation) + Atlas (architecture & synthesis) + Morgan (UX/design)
**Method**: Multi-round collaborative pre-flight review

## Plan Description
Build a require shim generator for PZ Mod Checker: scans diagnose results, categorizes missing require() modules into vanilla-global-redirects vs empty stubs, generates a pzmc_require_shim mod with stub Lua files. Integrates with existing translate shim pattern. Key risks: global load ordering, subdirectory paths (ISUI/ISInventoryPaneContextMenu), empty stubs silently breaking dependent mods.

## Readiness Assessment
- **Implementation (Soren)**: ⚠️ CAUTION -- Pattern is proven and code path is clear, but VANILLA_GLOBALS map and load-order verification must exist before writing `generate_shim()`.
- **Architecture (Atlas)**: ⚠️ CAUTION -- Parallel module approach is sound, but two unverified assumptions (Kahlua search path timing, shim load ordering) carry silent-failure risk.
- **UX/Design (Morgan)**: ⚠️ CAUTION -- Existing UI patterns transfer cleanly, but the risk communication for empty stubs and rollback visibility are unsolved design problems.
- **Overall**: ⚠️ CAUTION -- Architecture and patterns are ready. A hard data gate blocks implementation: Rob's actual require_failures must be collected and categorized before writing code. Without that data, we don't know if Phase 1 produces useful output or nothing.

## Morgan's Design Brief

### Style and Character
Mirror the Translate tab's established pattern. Dark surface cards, toggle+generate lifecycle, same visual language. The require shim is a second instance of "PZMC generates a compatibility mod for you," not a new concept. Users who learned Translate already have the mental model.

The critical difference from Translate: require stubs carry real risk. Translation stubs are cosmetic and cannot break anything. Require stubs can convert loud crashes into silent malfunctions. The UI must make this difference visible without making the feature feel dangerous to use.

### Color Palette
All existing values, no new colors needed:
- Surfaces: `#0f172a` (base), `#1e293b` (surface-1), `#334155` (surface-2)
- Accent: `#4ade80` (PZ green, primary actions)
- Safe stubs: `#4ade80` (green, same as existing success states)
- Risky stubs (Phase 2 only): `severity-warning` amber (`#f59e0b`)
- Errors/breaking: `severity-breaking` red (`#ef4444`)
- Interactive: `sky-700` (`#0369a1`) for secondary actions (matches Workshop/generate buttons)

### Typography
Unchanged from existing app: system-ui stack, `0.875rem` body, `0.75rem` labels, `1rem` headings within cards. No new font choices.

### Component Kit
- **Status card**: Identical to Translate's status card. Shows: shim enabled/disabled toggle, stub count, last generated timestamp. Always visible (no console.txt required).
- **CTA injection**: "Generate Require Shim" button injected into the Diagnose tab's require failures card when `reqFails.length > 0`. Green button, same style as existing action buttons. Text: "Generate stubs for X known modules."
- **Results list**: Grouped by category. Phase 1 shows only "Redirected modules" (vanilla globals that moved). Phase 2 adds "Unresolvable modules" (listed but not stubbed) and "Risky stubs" (empty, behind opt-in).
- **Remove button**: Prominent. Not below the fold. In the status card itself, not after the results list. Reason: if the shim makes PZ behave strangely, the user needs Remove immediately, not after scrolling through stub details.
- **Rollback affordance**: Remove button styled with `severity-warning` amber border when the shim is active, signaling "this is reversible, here's how." Translate's Remove doesn't need this because it can't break anything.

### Top 3 Design Recommendations (unanimous)

1. **Two entry points, one feature.** Standalone status/toggle section always visible (accessible without console.txt for regenerate/remove/status). CTA button injected into Diagnose require failures card when session data exists (discovery path). The user who just crashed finds it where the pain is. The user managing an existing shim finds it where the tool is.

2. **Risk tiers, not implementation categories.** The UI says "Safe fixes" and "Risky fixes," not "redirects" and "stubs." Phase 1 only generates safe fixes. Phase 2's empty stubs get an explicit opt-in confirmation that says, in plain language: "This makes PZ launch without crashing, but the mod's features may silently stop working. Inventory menus, context actions, or other behavior could break without an error message." Not developer terminology. Outcome language.

3. **Remove button is first-class, not buried.** Unlike the translate shim, the require shim can make things worse. The Remove action lives in the status card header, not at the bottom of a results list. If a user generates stubs, relaunches PZ, and things get weirder, "Remove Shim" must be findable in under 2 seconds.

## Soren's Implementation Blueprint

### Approach: File-per-module stubs (Approach A), redirect-only for Phase 1

New `pz_mod_checker/require_shim.py` (~200 lines), parallel to `translate.py`. For each module in VANILLA_GLOBALS that appears in `SessionDiagnosis.require_failures`, generate a Lua file at the correct path inside `~/Zomboid/mods/pzmc_require_shim/media/lua/shared/`.

### Module Organization
```
pz_mod_checker/
  require_shim.py          # New. scan_require_gaps(), generate_shim(), 
                           #   remove_shim(), get_shim_status()
  diagnose.py              # Unchanged except path sanitization filter
  gui/server.py            # +3 endpoint handlers (~80 lines)
  gui/static/index.html    # +require shim UI section (~100 lines)
```

### Key Code Patterns

**VANILLA_GLOBALS map** (dict in require_shim.py):
```python
VANILLA_GLOBALS: dict[str, str] = {
    "ISUI/ISInventoryPaneContextMenu": "ISInventoryPaneContextMenu",
    "Reloading/ISReloadWeaponAction": "ISReloadWeaponAction",
    # ... seeded from Rob's actual failure data
}
```

**Stub content** (redirect only, Phase 1):
```lua
-- pzmc_require_shim: redirect to B42 global
-- Module "ISUI/ISInventoryPaneContextMenu" moved to global namespace in B42
return ISInventoryPaneContextMenu
```

**Path sanitization** (added to diagnose.py, at parse time):
```python
_SAFE_MODULE_PATH = re.compile(r'^[A-Za-z0-9_/]+$')
# In _collect_require_failures(), after regex capture:
if '..' in module_path or not _SAFE_MODULE_PATH.match(module_path):
    continue  # reject traversal and special characters
```

**Generate lifecycle** (mirrors translate.py):
- `generate_shim()`: `shutil.rmtree()` existing shim dir first (solves orphan stubs), then create directory tree + stub files + mod.info
- `remove_shim()`: delete shim dir, call `disable_mods()`
- `get_shim_status()`: check dir exists + check default.txt
- Toggle: reuse `enable_mods()`/`disable_mods()` from manager.py

**Deduplication**: `set()` on `module_path` before generating. `attribute_require_failures()` expands to per-caller entries; the generator collapses back to unique modules.

### Server Endpoints
- `GET /api/require-shim/status` -- shim exists, enabled, stub count
- `POST /api/require-shim/generate` -- run scan + generate redirect stubs
- `POST /api/require-shim/toggle` -- enable/disable in default.txt
- `DELETE /api/require-shim/remove` -- delete shim dir + disable

### Test Strategy

| Test | Type | Approach |
|------|------|----------|
| Path sanitization (reject `..`, special chars) | Unit | Parametrized, malicious inputs |
| Module path to file path conversion | Unit | Slash, nested, edge cases |
| Deduplication of require failures | Unit | Duplicate module_paths in input |
| VANILLA_GLOBALS lookup | Unit | Hit, miss, case sensitivity |
| Stub file content correctness | Unit | Verify Lua syntax, correct global name |
| Full shim generation (dir tree) | Integration | `tmp_path` fixture, verify structure |
| Delete-and-recreate on regenerate | Integration | Generate, modify, regenerate, verify no orphans |
| Round-trip: generate, status, remove | Integration | Follow translate.py's pattern |

Gap: `translate.py` has zero tests. Adding `test_require_shim.py` without `test_translate.py` builds on an untested foundation. Recommend adding basic translate shim tests alongside.

### Complexity Estimate
~2 days implementation if VANILLA_GLOBALS map and Rob's data are ready. The pattern exists, it's replication with new content logic. Add 1 day for tests (both shim modules). Add half a day for the UI section.

## Atlas's Architecture Blueprint

### System Design Overview

```
diagnose.py                    require_shim.py
┌─────────────────────┐       ┌──────────────────────────┐
│ parse console.txt   │       │ VANILLA_GLOBALS map       │
│ _collect_require    │──────>│ scan_require_gaps()       │
│   _failures()       │  list │ categorize: redirect/skip │
│ [path sanitization] │  of   │ generate_shim()           │
│ RequireFailure      │  RF   │   rmtree + mkdir + write  │
└─────────────────────┘       │ remove_shim()             │
                              │ get_shim_status()         │
                              └──────────┬───────────────┘
                                         │ calls
                              ┌──────────▼───────────────┐
                              │ manager.py                │
                              │ enable_mods/disable_mods  │
                              └──────────────────────────┘
```

Data flows one direction: diagnose produces `RequireFailure` objects, `require_shim.py` consumes them and writes to disk. Manager handles enable/disable. No circular dependencies.

### Integration Points

| Component | Change | Scope |
|-----------|--------|-------|
| `diagnose.py` | Add path sanitization filter after `_REQUIRE_FAIL_RE` capture | ~5 lines |
| `require_shim.py` | New file, full module | ~200 lines |
| `server.py` | 3-4 new endpoint handlers | ~80 lines |
| `index.html` | Require shim UI section + Diagnose CTA injection | ~100 lines |
| `manager.py` | No changes. Existing `enable_mods`/`disable_mods` consumed as-is | 0 lines |

### Build Sequence

**Step 0 (data gate, before any code):**
Run diagnose on Rob's 258-mod install. Collect `require_failures`. Categorize each `module_path`: is it a vanilla module that became a B42 global, or a genuinely missing dependency? This determines the VANILLA_GLOBALS starter map and whether Phase 1 produces useful output.

**Step 1:** Path sanitization in `diagnose.py`. Tighten `_collect_require_failures()` to reject traversal paths. Test immediately.

**Step 2:** `require_shim.py` core: VANILLA_GLOBALS map, `scan_require_gaps()`, `generate_shim()`, `remove_shim()`, `get_shim_status()`. Tests for all.

**Step 3:** Server endpoints. Wire into `server.py`.

**Step 4:** UI. Standalone section (status card + toggle + generate/remove). CTA injection into Diagnose require failures card.

**Step 5:** Load order investigation. Test with a real PZ session. If shim loads too late, implement `enable_mods_first()` or default.txt insert-at-0.

### Load Order: The Unresolved Bet

PZ loads mods in default.txt order. `enable_mods()` appends to the end (`manager.py:229`). The shim loads last. If PZ registers all mod directories to Lua's search path at startup (before any mod code runs), stubs are available regardless of load order. If PZ registers directories incrementally as mods initialize, the shim dir isn't registered until after mods that need it have already failed.

We cannot verify this without a running PZ instance. The implementation must treat this as an explicit open assumption and test it empirically in Step 5. If the bet is wrong, the fix is either:
- Insert shim at position 0 of default.txt (new `enable_mods_first()` in manager.py)
- Add all other mod IDs to the shim's `require` field in mod.info (forces PZ to load them after the shim)

Neither is complex. But neither should be built until we know which is needed.

## Risks & Concerns

### Code Risks

| Risk | Raised by | Consensus | Detail |
|------|-----------|-----------|--------|
| Empty stubs convert loud crashes to silent nil propagation | Soren (R1), Atlas (R1), Morgan (R1) | **Unanimous** | Mitigated: empty stubs deferred to Phase 2 behind explicit opt-in. Phase 1 is redirect-only. |
| Stale stubs persist after regeneration | Atlas (R1) | **Unanimous** | `generate_shim()` must `shutil.rmtree()` before recreating. Delete-and-recreate, not incremental. |
| Path traversal in module_path from log data | Soren (R1), Atlas (R1) | **Unanimous** | Sanitize at parse time in `diagnose.py`, not at generation time. Reject `..`, absolute paths, non-`[A-Za-z0-9_/]` characters. |
| Deduplication needed before stub generation | Soren (R1) | **Unanimous** | `attribute_require_failures()` expands per-caller. Generator must deduplicate by `module_path`. |
| translate.py has zero tests | Soren (R1) | **Unanimous** | Adding a second shim module on an untested foundation. Recommend adding basic translate tests alongside. |

### Architecture Risks

| Risk | Raised by | Consensus | Detail |
|------|-----------|-----------|--------|
| Load order: shim may load after mods that need it | Atlas (R1), Morgan (R2) | **Unanimous** | Unresolved. `enable_mods()` appends to end. PZ's Kahlua search path registration timing is unknown. Must test empirically. |
| VANILLA_GLOBALS map maintenance burden | Soren (R1) | **Unanimous** | Every PZ update could change globals. Acceptable for now: the map is small, PZ updates are infrequent, and the data is version-keyed. |
| Unattributed require failures (source_file=None) | Soren (R1) | **Unanimous** | Policy: generate redirect stub if module is in VANILLA_GLOBALS (provenance doesn't matter, the module moved regardless). Skip unattributed unknowns entirely. |

### UX Risks

| Risk | Raised by | Consensus | Detail |
|------|-----------|-----------|--------|
| Silent damage from empty stubs looks like success to user | Morgan (R1, R2) | **Unanimous** | Phase 2 opt-in must use outcome language: "PZ may launch without crashing, but mod features may silently stop working." |
| Rollback UX: Remove button buried below fold | Morgan (R1, R2) | **Unanimous** | Remove button in status card header, not after results list. Unlike translate shim, this feature can make things worse. |
| No feedback loop after shim generation | Morgan (R1) | **Unanimous** | User generates shim, relaunches PZ, runs Diagnose again. Require failure count should change. UI should note: "X failures resolved by shim" if detectable. Low priority for Phase 1. |
| Pre-launch access requires standalone section | Morgan (R2), Soren (R2) | **Unanimous** | Diagnose CTA only appears after a crash. Standalone section must exist for users managing an existing shim without a new console.txt. |

## Gaps in the Plan

| Gap | Resolution |
|-----|------------|
| No VANILLA_GLOBALS data source identified | Seed from Rob's actual require_failures. Cross-reference with B42 patch notes for API moves. Start small, expand on evidence. |
| Load order verification method unspecified | Step 5 in build sequence: empirical test with real PZ session. If shim loads too late, implement insert-at-position-0 in manager.py. |
| translate.py has no test coverage | Add `test_translate.py` with basic lifecycle tests (generate/status/remove) alongside `test_require_shim.py`. |
| Unattributed failure count unknown | Determined by Step 0 data collection. If significant, UI needs "X stubs generated, Y failures couldn't be attributed to a specific mod." |
| No `enable_mods_first()` in manager.py | Design this API before Step 5. Even if not needed immediately, the shim use case (must load early) is distinct from normal mod enabling (append to end). |

## Open Questions

| # | Question | Owner | Urgency | Gate? |
|---|----------|-------|---------|-------|
| 1 | What are the actual require_failures from Rob's 258-mod install? | Rob | **Before any code** | Yes |
| 2 | How many failures map to known B42 globals vs. genuinely missing deps? | Atlas (categorize after Rob provides data) | **Before any code** | Yes |
| 3 | How many failures are unattributed (mod_name=None)? | Diagnostic from Q1 data | Before UI design finalized | No |
| 4 | Does PZ register all mod directories to Lua search path at startup, or incrementally? | Empirical test (Step 5) | Before shipping | No (build first, test before release) |
| 5 | Should `enable_mods_first()` insert at position 0 or use mod.info dependency manipulation? | Atlas + Soren | Only if Q4 reveals a problem | No |

## Recommended First Phase

**Phase 1: Redirect stubs only, gated on Rob's data.**

**Pre-implementation (hard gate):**
1. Rob runs diagnose on his 258-mod install
2. Collect the `require_failures` list
3. Categorize each `module_path`: vanilla global that moved in B42, or genuinely missing dependency
4. Build starter VANILLA_GLOBALS map from the results
5. If zero failures map to vanilla globals, Phase 1 produces nothing useful. Reassess the feature.

**Build scope (after data gate clears):**
- Path sanitization in `diagnose.py` (~5 lines + tests)
- `require_shim.py` with VANILLA_GLOBALS map, scan/generate/remove/status (~200 lines + tests)
- Server endpoints (3-4 handlers, ~80 lines)
- UI: standalone status card + Diagnose CTA injection (~100 lines)
- Basic `test_translate.py` alongside `test_require_shim.py`

**What Phase 1 does NOT include:**
- Empty stubs (Phase 2, behind explicit opt-in with outcome-language confirmation)
- Categorization UI beyond "X modules redirected, Y unresolvable"
- Auto-generation without user action
- Load order manipulation (tested in Step 5, fixed if needed)

**Phase 1 exit criteria:**
- Rob generates a shim from his actual failures
- At least one redirect stub is produced
- PZ launches with the shim enabled and require failures for redirected modules are gone
- Remove button works and PZ behavior reverts cleanly

---

The first move is Rob's. Run diagnose, pull the require_failures, paste them here. Everything above is architecture on top of an assumption about what that data looks like. The data determines whether this feature is a Tuesday afternoon or a different tool entirely.

---
*Generated by Collab Plan (Soren + Atlas + Morgan), collaborative pre-flight review with extended thinking*