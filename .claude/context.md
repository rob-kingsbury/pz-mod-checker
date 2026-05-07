# PZ Mod Checker Context

```yaml
version: 0.2.0
status: Feature complete, ready for distribution
created: 2026-03-23
session: 9
last_updated: 2026-05-06

arch:
  stack: Python 3.10+, CLI (argparse), JSON rules
  purpose: External pre-launch scanner for PZ mod compatibility
  target: Project Zomboid Build 42.x
  coauthor: Claude Sonnet 4.6 <noreply@anthropic.com>

identity:
  product: PZ Mod Checker
  what: External compatibility scanner, NOT an in-game mod
  approach: Rule-based (version-keyed PZ changes, not mod blacklists)
```

## Session Notes

### Session 9 (2026-05-06): Live Triage + B42 Structure Discovery
Live triage on user's 180-mod B42.17 install. DAMN library updated upstream — 30+ KI5 vehicle mods now working. Diagnose attribution improved: regex captures `pcall(require, "X")` patterns in addition to standard forms. Identified previously-unattributed broken mods (AutotsarMotorClub, TowTruckMod, WaterPipes, SmokeLikeIts93). Disabled 4 broken mods via API.

**Critical empirical finding on PZ B42 mod structure:** PZ B42 requires mod.info in BOTH the root AND `42/` subfolder. Mods missing `42/mod.info` are silently rejected — not even logged to console.txt. Bumped 3 existing structure rules from info to warning, added new `b42-modinfo-in-versioned-folder` rule (breaking severity, certain confidence).

Filed 3 GitHub issues on rob-kingsbury/unbreaker repo for mod-author bug tracking. Created 5 issue labels.

### Session 8 (2026-05-02): Field Cases, Shims & Rule Derivation
Triaged three broken workshop mods (KATTAJ1 Clothes Core, SimpleSilencers, NepUniversalSS) against 42.17. Found and shimmed 9 distinct root causes. Created data/cases/field-cases.md with full triage notes, shim file references, and generalisation notes. Created data/rules/42.0.0-field-cases.json with 9 new rules derived from observed breakage patterns: b42-removed-bagsandcontainers, b42-require-npcs-bodylocations, b42-require-npcs-prefix, b42-removed-istooltipinv, b42-lua-outside-lua-folder, b42-weaponpart-canon-renamed, b42-java-field-access-projectilecount, b42-java-field-access-twohandweapon, b42-class-conflict-isupgradeweapon. Updated no-comp.txt with commented reference entries for all three mods. Also built and validated a lupa/Lua5.4 logic checker (lua_checker.py, ss_checker.py) for runtime assertion testing of shim files without PZ.

### Session 7 (2026-04-15): Translation Shim + Rule False Positive Fixes
New translate.py module + Translate GUI tab: scans mods for missing EN keys, generates single stub shim mod, on/off toggle, title-case key conversion. Removed false positive rule b42-removed-transferall (ISInventoryTransferAction still exists in B42). Narrowed b42-13-itemtag-string to only flag string literals in hasTag/containsTag calls.

### Session 6 (2026-04-09): Issue Blitz + Rule Audit
Closed 9 issues. Scan UX: warning/breaking groups auto-expand, enabled/disabled status in scan results (dimmed + badge). Accessibility: keyboard toggles, loading states. DRY refactor: _cached_mod_status(). Workshop outbound links on Mods and Scan pages. Rule audit: 1912 to 1716 findings, tightened patterns, filesystem-security upgraded to breaking.

### Session 5 (2026-04-08): 42.16 Rules + False Positive Audit
Added 42.16.0.json (6 rules: occupation/trait renames, sandbox type change, procLists fix, Lua security). False positive audit on 258-mod install. 2432 to 1912 findings. 73 tests passing.
