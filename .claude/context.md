# PZ Mod Checker Context

```yaml
version: 0.2.0
status: Feature complete. Rules now cover B42.0 through B42.20.0.
created: 2026-03-23
session: 10
last_updated: 2026-07-30

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

### Session 10 (2026-07-30): B42.20 Stable rules, backfilled from a file diff
Done from the Unbreaker side of the fence, during that project's 42.20 pass. PZ went B42.20 Stable on 2026-07-29.

Added `data/rules/42.20.0.json` (3 rules) and `data/rules/42.19.0.json` (2 rules, backfilled). Rules previously stopped at 42.18.0.

**The method that produced them is the point.** Instead of reading changelogs, diff the vanilla Lua tree between builds. The community mirror `Project-Zomboid-Community-Modding/ProjectZomboid-Vanilla-Lua` names its commits by version (`29df4fe` = 42.19), so `git clone --depth 1` gives a full `client/server/shared` tree to diff against an installed build. That diff caught two removals no changelog mentions, including two globals that had been dead since 42.18 or 42.19 while both projects' changelog-only reviews called those builds clean.

42.20 rules: `gamepadBinding` moved shared to client (the only file in the whole build that changed root); `ISFarmingCursor` deleted, deliberately WITHOUT a `replacement` field because `ISFarmingCursorMouse` shares only 6 of its 10 methods and advising a swap would break callers; the `LastStand/Challenge2` family removed with the challenge revamp.

42.19 rules: `CharacterCustomisationPanel` and `CommonTemplates`, both gone. `confidence: speculative` refers to the BUILD attribution only, not to the removal, which is certain. They were live in 42.17 and absent in 42.19, so they died in 42.18 or 42.19. Checking the mirror's 42.18 commit (`dda81da`) would pin it.

**NOT verified by execution.** Bash was blocked by the permission classifier for the second half of that session, so the loader never ran against these two files. Watch stderr on the next run for `unknown fields` or `Invalid regex` warnings from `rules/loader.py`. The `ISFarmingCursor(?!Mouse)` negative lookahead is the one worth confirming; `_check_pattern` compiles with plain `re.compile`, so it should hold.

Unbreaker coverage (`unbreaker.py`) needs no change here, it fetches `main` live with a 24h cache. Force a refresh by deleting `%LOCALAPPDATA%\pz-mod-checker\unbreaker_coverage.json`.

**Fixed a rule that had never once fired.** Rob's scan printed `Unknown check type 'no_lua_in_media_root' for rule 'b42-lua-outside-lua-folder'`. That rule was written in session 8 (2026-05-02) and its check type was never implemented in `_check_structure`, so it fell to `case _`, printed a warning, and returned no findings for roughly three months. Implemented it as a real case plus `_find_stray_lua()`.

The trap worth remembering: `_check_structure` computes `target = mod.path / rule.path`, and the rule's path is `media/`. B42 mods do not have `mod.path/media`, they have `42/media` or `common/media`, and some use a point release such as `42.15/media` (see KATTAJ1 in field-cases.md). Implementing the check against `target` would have compiled, run, produced nothing, and looked fixed. `_find_stray_lua` globs `media` and `*/media` instead, so it covers every layout.

Still stale: `README.md` claims "63 rules covering B42.0 through B42.17.0". Both halves are now wrong. The count was left alone rather than guessed at.

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
