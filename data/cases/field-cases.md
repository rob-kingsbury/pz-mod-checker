# PZ Mod Checker — Field Cases

Real-world triage sessions. Each case records: what broke, why, what the shim fix was,
and what rule or no-comp entry was created or should be created to catch it automatically.

---

## Case 001 — KATTAJ1 Clothes Core (Workshop ID: 3470422050)

**Mod ID:** `KATTAJ1_ClothesCore`
**Highest versioned folder:** `42.15`
**Symptom:** Mod appears in mod list but clothing items cannot be equipped. No "Wear" option.
**Session date:** 2026-05-02

### Root Causes

#### RC-001-A: `registries.lua` at wrong path (never executed)
- **File:** `42.15/media/registries.lua`
- **Issue:** PZ only auto-executes Lua inside `media/lua/shared/` or `media/lua/client/`.
  A file at `media/registries.lua` (root of media) is silently ignored.
- **Effect:** `KATTAJ1_BodyLocation` global table is never populated. All 24 custom body
  location registrations in `KATTAJ1_ExtraBodyLocations.lua` fail silently because the
  table they iterate over is nil.
- **Shim fix:** Re-run the full `ItemBodyLocation.register()` block in the shim's
  `media/lua/shared/` file.
- **Generalisable rule:** Detect Lua files in `media/` root (outside `media/lua/`).
  Rule ID proposed: `b42-lua-outside-lua-folder`

#### RC-001-B: `require "NPCs/BodyLocations"` — B41 path
- **File:** `42.15/media/lua/shared/NPCs/KATTAJ1_ExtraBodyLocations.lua`
- **Issue:** B41 path for the body locations module. In B42, the module is `"BodyLocations"`.
  The require fails, the whole file errors, and no custom body locations or exclusives are
  registered against the Human group.
- **Shim fix:** Pre-require `"BodyLocations"` via B42 path, inject into `package.loaded`
  under the old `"NPCs/BodyLocations"` key, then re-run the full body location + exclusive
  registration block directly.
- **Generalisable rule:** Flag `require "NPCs/BodyLocations"` in any Lua file.
  Rule ID proposed: `b42-require-npcs-bodylocations`

#### RC-001-C: `ISToolTipInv` removed/changed
- **File:** `42.15/media/lua/client/KATTAJ1_TooltipFixer.lua`
- **Issue:** `require "ISUI/ISToolTipInv"` followed by monkey-patching `ISToolTipInv.render`.
  `ISToolTipInv` changed significantly in B42, causing a crash on load.
- **Shim fix:** Pre-stub `ISToolTipInv = { render = function(self) end }` before the
  original file runs, so its require and override land on the stub harmlessly.
- **Generalisable rule:** Flag `ISToolTipInv` usage. Rule ID proposed: `b42-removed-istooltipinv`

### Shim
Located at: `C:\Users\roban\Zomboid\mods\kattaj1_42_17_shim\`
Files: `42/media/lua/shared/KATTAJ1_shim_BodyLocations.lua`,
       `42/media/lua/client/KATTAJ1_TooltipFixer_shim.lua`
Logic check result: **19/19 assertions passed**

### no-comp.txt entry
Not added — shim resolves it. Add if author updates and shim becomes stale:
```
KATTAJ1_ClothesCore|42.15.x|Body location registry at wrong path; NPCs/BodyLocations require; ISToolTipInv crash
```

---

## Case 002 — SimpleSilencers (Workshop ID: 3309896124)

**Mod ID:** `SimpleSilencers`
**Highest versioned folder:** `42.15`
**Symptom:** Silencers cannot be attached. Sound suppression doesn't fire when silencer is equipped.
Silencers also don't spawn in loot.
**Session date:** 2026-05-02

### Root Causes

#### RC-002-A: `getWeaponPart("Canon")` — slot renamed to `"Muzzle"` in B42
- **File:** `42.15/media/lua/client/SimpleSilencers_SilencerEquip.lua`
- **Issue:** The equip handler checks `inventoryItem:getWeaponPart("Canon")` to detect a
  mounted silencer. B42 renamed the muzzle weapon part slot from `"Canon"` to `"Muzzle"`.
  `getWeaponPart("Canon")` always returns nil — the sound suppression block never executes.
- **Note:** The context menu file (`SilencerContextMenu.lua`) already had a shim for this
  via `getMuzzle()` / `getCanon()` fallback, but the equip handler did not.
- **Shim fix:** Register a corrected `OnEquipPrimary` handler that uses `getMuzzle()` then
  `getWeaponPart("Muzzle")` instead.
- **Generalisable rule:** Flag `getWeaponPart("Canon")` string in any Lua file.
  Rule ID proposed: `b42-weaponpart-canon-renamed`

#### RC-002-B: `BagsAndContainers` removed in B42
- **File:** `42.15/media/lua/server/SimpleSilencers_Distribution.lua`
- **Issue:** File opens with `table.insert(BagsAndContainers.Bag_Police.items, ...)`.
  `BagsAndContainers` does not exist in B42 — it was merged into `ProceduralDistributions`.
  This nil-index error on load kills the entire distribution file. No silencers spawn
  anywhere in the world.
- **Shim fix:** `OnPostDistributionMerge` handler that recovers the missed inserts into
  equivalent B42 `ProceduralDistributions.list` entries.
- **Generalisable rule:** Flag `BagsAndContainers` usage. Already exists? If not:
  Rule ID proposed: `b42-removed-bagsandcontainers`

#### RC-002-C: `ISUpgradeWeapon` class name conflict
- **File:** `42.15/media/lua/shared/SimpleSilencers_ISUpgradeWeapon.lua`
- **Issue:** `ISUpgradeWeapon = ISBaseTimedAction:derive("ISUpgradeWeapon")` clobbers the
  vanilla B42 `ISUpgradeWeapon` class, breaking vanilla weapon upgrade timed actions.
- **Shim fix:** File named `AAA_SS_shim_ISUpgradeWeapon.lua` (sorts first alphabetically)
  saves the vanilla reference before the mod file loads. `OnGameBoot` handler detects the
  clobber, restores vanilla, aliases the mod version as `SimpleSilencers_ISUpgradeWeapon`.
- **Generalisable rule:** Flag mods that declare `ISUpgradeWeapon =` at global scope
  as a potential class conflict. Rule ID proposed: `b42-class-conflict-isupgradeweapon`

### Shim
Located at: `C:\Users\roban\Zomboid\mods\simplesilencers_42_17_shim\`
Files: `42/media/lua/client/SS_shim_SilencerEquip.lua`,
       `42/media/lua/server/SS_shim_Distribution.lua`,
       `42/media/lua/shared/AAA_SS_shim_ISUpgradeWeapon.lua`,
       `42/media/lua/shared/SS_shim_ISUpgradeWeapon.lua` (empty placeholder),
       `42/media/lua/shared/SS_shim_NepUniversalSS.lua`
Logic check result: Sound suppression, distribution, ISUpgradeWeapon conflict all verified.

### no-comp.txt entry
Not added — shim resolves it.

---

## Case 003 — Nepenthe's Universal Simple Silencers (Workshop ID: 3634876505)

**Mod ID:** `NepUniversalSS`
**Highest versioned folder:** `42/` (flat, no versioned subfolders)
**Symptom:** All guns classified as "pistol" type regardless of actual type. Shotguns and
rifles get wrong silencer model. Non-ranged weapons may be incorrectly modified.
**Session date:** 2026-05-02

### Root Causes

#### RC-003-A: `item:getItemType() ~= ItemType.WEAPON` — broken comparison
- **File:** `42/media/lua/shared/simplesilencerextra.lua`
- **Issue:** `ItemType.WEAPON` is not a reliable comparison target in B42. Should use
  `instanceof(item, "HandWeapon")` combined with `item:isRanged()`.
- **Shim fix:** Replace `findGunType` with corrected version using `instanceof`.

#### RC-003-B: `item.projectileCount` — Lua field access on Java object
- **File:** `42/media/lua/shared/simplesilencerextra.lua`
- **Issue:** `item.projectileCount` accessed as a plain Lua table field. On B42 Java-backed
  objects this always returns nil. Correct accessor is `item:getProjectileCount()`.
  Effect: shotgun detection always fails, all guns default to pistol type (0).
- **Shim fix:** `findGunType` replacement uses `item:getProjectileCount()`.
- **Generalisable rule:** Flag `.projectileCount` (no colon, no parentheses) on items.
  Rule ID proposed: `b42-java-field-access-projectilecount`

#### RC-003-C: `item.twoHandWeapon` — same Java field access issue
- **File:** `42/media/lua/shared/simplesilencerextra.lua`
- **Issue:** Same pattern as above. `item.twoHandWeapon` is always nil.
  Correct accessor is `item:isTwoHandWeapon()`. Effect: rifles/longarms always
  classified as pistols.
- **Shim fix:** `findGunType` replacement uses `item:isTwoHandWeapon()`.
- **Generalisable rule:** Flag `.twoHandWeapon` (no colon, no parens).
  Rule ID proposed: `b42-java-field-access-twohandweapon`

#### RC-003-D: `Events.OnGameBoot.Add(UniversalSS.AddSS)` — function reference timing
- **File:** `42/media/lua/shared/simplesilencerextra.lua`
- **Issue:** The function reference is captured at registration time. Replacing
  `UniversalSS.AddSS` later (in a shim) does not affect the already-queued handler.
  The patched function must be explicitly re-registered to `OnGameBoot`.
- **Shim fix:** Shim replaces both `findGunType` and `AddSS` at load time (not in an
  event handler), then re-registers the corrected `AddSS` to `OnGameBoot` so it fires
  after the original broken version and overwrites entries with correct gun types.

#### RC-003-E: `mod.info` missing `versionMin`
- **File:** `42/mod.info`
- **Issue:** No `versionMin` declared. Mod activates on any B42 build regardless of
  compatibility.
- **Shim fix:** Not shimmed — noted for author.
- **Generalisable rule:** Already exists: `b42-modinfo-versionmin`

### Shim
Included in `simplesilencers_42_17_shim` (same mod folder as Case 002).
File: `42/media/lua/shared/SS_shim_NepUniversalSS.lua`
Logic check result: findGunType pistol/shotgun/longarm/non-ranged all verified.

### no-comp.txt entry
Not added — shim resolves it.

---

## Patterns & Cross-Case Observations

### Java method vs field access
Cases 003-B and 003-C are both instances of the same class of bug: treating Java-backed
PZ item objects as plain Lua tables and accessing properties without `()`. This is very
common in B41 mods ported to B42. Other known instances of this pattern:
- `item.weight` → `item:getWeight()`
- `item.count` → `item:getCount()`
- `item.maxAmmo` → `item:getMaxAmmo()`

Candidate rule: `b42-java-dot-field-access` — regex scan for common B41 field patterns.

### B41 require paths
`"NPCs/BodyLocations"`, `"NPCs/BodyLocations"`, `"ISUI/ISToolTipInv"` are all B41 paths.
B42 reorganised a number of these. The `NPCs/` prefix in particular is a strong signal of
a B41-era shared file.

Candidate rule: `b42-require-npcs-prefix` — flag any `require "NPCs/` in shared Lua.

### Alphabetical load order dependency
Case 002-C (ISUpgradeWeapon) required the shim file to be named `AAA_*` to guarantee it
loads before the mod file it needs to intercept. This is a general pattern for "save before
clobber" shims. Worth documenting as a shim authoring convention, not a rule.

### Flat `media/` Lua files
Case 001-A (registries.lua) is a pattern where mod authors put Lua in `media/` root
thinking it will be picked up. It won't. This is easy to scan for.

### BagsAndContainers
Case 002-B. Removal of `BagsAndContainers` is a well-known B41→B42 break. A rule scanning
for `BagsAndContainers` would catch a large number of distribution mods.

---

## Proposed New Rules Summary

| Proposed ID | Type | Severity | Pattern | From Case |
|---|---|---|---|---|
| `b42-lua-outside-lua-folder` | structure | warning | Lua files in `media/` root | 001-A |
| `b42-require-npcs-bodylocations` | api_removal | breaking | `require "NPCs/BodyLocations"` | 001-B |
| `b42-removed-istooltipinv` | api_removal | breaking | `ISToolTipInv` | 001-C |
| `b42-weaponpart-canon-renamed` | api_rename | breaking | `getWeaponPart("Canon")` or `getWeaponPart('Canon')` | 002-A |
| `b42-removed-bagsandcontainers` | api_removal | breaking | `BagsAndContainers` | 002-B |
| `b42-class-conflict-isupgradeweapon` | api_signature | warning | `ISUpgradeWeapon\s*=` at global scope | 002-C |
| `b42-java-field-access-projectilecount` | api_rename | warning | `\.projectileCount[^(]` | 003-B |
| `b42-java-field-access-twohandweapon` | api_rename | warning | `\.twoHandWeapon[^(]` | 003-C |
| `b42-require-npcs-prefix` | api_removal | warning | `require "NPCs/` | 001-B, cross-case |
| `b42-removed-bagsandcontainers` | api_removal | breaking | `BagsAndContainers` | 002-B |
