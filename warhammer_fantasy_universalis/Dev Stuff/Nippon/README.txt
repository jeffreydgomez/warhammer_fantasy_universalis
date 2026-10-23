NIPPON: THE SECOND DAWN

Approved revision: 23 October 2026
48 missions, five slots, rows 1-15, with 27 blank cells.
Proof of Superiority requires only A Hundred Banners. The military and
foreign-power capstones remain independent optional branches.

Eligibility and progression
- Priority 4, based on a capital in nippon_region. Existing priority 1-3
  exclusions, regional collision guards, and row-16 racial challenges remain.
- No culture, religion, Grand Nippon tag, or formation-flag gate is imposed.
- Restore Grand Nippon requires peace and ownership of every usable Nippon
  province, directly or through non-sovereign subjects. Unowned land counts as
  unfinished; seas and wastelands do not. The formation decision is separate.
- Blood Debts retains low corruption and three non-vampiric courthouse/town-hall
  provinces, or permits a vampiric country with three courts and all directly
  owned Nippon provinces following its vampiric faith.
- Cleanse the Shrines requires every directly owned Nippon province to follow
  the state religion, plus four temple/cathedral provinces. End the Century of
  Night requires every settled Nippon province to follow the state religion
  and belong to the country or a loyal non-sovereign subject.
- Beneath the Old Shrines requires three directly owned Nippon shrine provinces
  with temple/cathedral and 20 development, plus a level-2 ADM advisor.
  Reusing temples deliberately represents investment in the expedition's bases.
- Overseas progression counts 1, 5, 10, and 20 completed cities in the mod's
  Lustria/Naggaroth continents (north_america/south_america), owned directly or
  by non-sovereign subjects. Conquered cities count; incomplete colonies do not.
  No colonial-origin flag, extra port/building quota, or loyalty check is needed.
- The legacy colony-completion marker hook remains compatible with old saves
  but is no longer consulted by these mission objectives.

Rewards and balance
- Ten former immediate rewards are permanent modifiers; six immediate rewards
  remain. The four event missions still offer two permanent rewards each.
- Priced regular rewards total 177.5 WV: 30 x 5, 15 x 1, 1 x 2.5, 1 x 10.
- Ocean Voyages grants a permanent colonist and may_explore. The colonist is
  worth 10 WV; explorer recruitment is an explicit user-requested unlock not
  covered by the Balance Guide, so no invented WV is assigned to it.
- The ultimate remains 40 WV across diplomatic reputation, annual prestige,
  infantry combat ability, and governing capacity.
- Sources: Examples/Balance Guide.txt, Mission Trigger Catalogue.txt, and
  Lore Reference.txt. This revision preserves the mod's Nippon premise.

Artifacts and compatibility
- Proof of Superiority requires 14 distinct artifact types in directly owned
  provinces. Multiple different artifacts in one province count separately;
  duplicate copies of one artifact type, subject relics and foreign relics do not.
- Each artifact check is explicitly grouped under AND inside calc_true_if and
  reads the actual province modifier. It does not count expanded if/else helper
  branches or rely on cached artifact event targets.
- Internal mission and reward IDs are preserved for saves. Missions already
  completed do not re-award converted permanent rewards automatically.
- Arts of Peace counts 14 unlocked ideas from selectable groups using native
  has_idea checks inside calc_true_if. Both total_ideas and num_of_total_ideas
  were rejected as conditions by EU4; a name appearing in the binary does not
  establish that it is a usable trigger. Warhammer and tall-play groups count;
  free national ideas, traditions and completion bonuses do not.
- build_missions.py generates war_nippon_idea_triggers.txt from common/ideas.
  Rerun it after adding/removing selectable ideas; validation checks coverage.

Highlights and artwork
- 37 missions highlight unfinished geographic requirements; 11 national-only
  objectives document why they have no province highlight.
- Quotas stop highlighting when satisfied. Ordinary targets must be discovered;
  Across the Serpent Sea deliberately highlights undiscovered coastal destinations.
- Witnesses uses mission_unique_vamp_coast_spy_in_capital, showing a sealed
  message at a throne; its highlights identify neighboring capitals only.
- All 48 missions retain distinct registered sprites, texture paths and hashes.
- mission_tree_preview.png is generated from current design data and installed
  DDS files. Optional original art source files are not present in this checkout.

Editing and verification
- mission_design.json is the canonical editable design, including trigger and
  highlight source, rewards, flavor, icons, layout, events and tooltips.
- build_missions.py renders the game mission, modifier, event and BOM-localisation
  files from that design. Edit the design before regenerating.
- The shared helpers in common/scripted_triggers/war_nippon_mission_triggers.txt
  are maintained separately and validated with the mission files.
- validate_missions.py checks geometry, references, guide-derived balance,
  starting history, numerical boundaries, religion/ownership/discovery scenarios,
  artifact counts, localisation and icon uniqueness. Requires Pillow.
- render_preview.py rebuilds the tree preview without modifying shared artwork.
- validation.json records static and synthetic results. An in-game load/playtest
  is still required; this validation does not emulate the full EU4 engine.
