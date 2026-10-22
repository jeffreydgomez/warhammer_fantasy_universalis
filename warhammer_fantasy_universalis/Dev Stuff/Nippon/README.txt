NIPPON: THE SECOND DAWN

48 missions, five slots, rows 1-15. The approved layout has 27 blank cells.
All 47 other missions lead into the final slot-3 mission.

Eligibility
- Priority 4, based solely on capital location in nippon_region.
- Existing priority 1, 2, and 3 trees take precedence under the mod's system.
- No culture or religion restriction is added to regional eligibility.
- The Borderlands and overseas Norscan trees defer to Nippon when capitals
  overlap its region. Compatible racial challenges follow from row 16.
- Grand Nippon (Z89 or formed_grand_nippon_flag) is required from row 9 onward.

Content
- First half: surveys, compromised households, samurai reform, restored court,
  Grand Nippon, island cleansing, and victories against Cathay and Khuresh.
- Second half: domestic growth, underground garrisons and government, exploration,
  New World settlements, foreign recognition, and restoration of the palaces.
- 176 Weighing Value before the ultimate: 30 x 5, 16 x 1, and a colonist worth 10.
- The Second Dawn: +2 diplomatic reputation, +1.5 annual prestige, +10% infantry
  combat ability, +10% governing capacity. Total Weighing Value 40.
- Four mission events, each offering two alternative rewards worth 5 each.
- Local lore and balance sources are Dev Stuff/Examples/Lore Reference.txt,
  Balance Guide.txt, and Mission Trigger Catalogue.txt.

Implementation notes
- Ocean Charters requires quest_for_the_new_world. It grants a colonist without
  introducing an unpriced permanent may_explore modifier.
- Cathayan, Khureshi, and underground victory checks accept a war won within
  50 years against a surviving regional state of at least 50 development, or
  control of eight cities in that geography through direct/non-sovereign rule.
  This keeps the branches usable when the original rival has been annexed.
- Colony completion marks new settlements owned by a Nippon-capital country or
  its colonial nation. Marks survive transfer to colonial subjects. The first
  colony, five-settlement, and ten-settlement checks cannot be met solely by
  conquering unmarked native cities. Existing saves must finish new settlements
  after installing this content; old colonies are not retrospectively marked.
- Cleansing permits faiths other than vampirism and Chaos. Loyal non-tributary
  subject rule counts for the homeland and later imperial domains.
- The palace mission restores province 4780 and requires it to be the capital.
- New localisation is UTF-8 with BOM. Event paragraphs use literal \n\n escapes.

Artwork
- Every mission has a different sprite, texture path, and texture hash.
- 18 new images were created with the built-in image_gen tool and converted to
  59 x 63 uncompressed RGBA8 DDS. Original PNG sources are retained in Mission
  Art/sources. The other 30 missions reuse distinct existing mod artwork.
- Mission Art/manifest.json records assignments, prompts, sources, dimensions,
  hashes, and the existing battle-standard fallback for the commander image
  rejected by the image tool. No shared texture is overwritten.
- Sprites are defined in interface/war_missions.gfx.
- mission_tree_preview.png shows the complete layout and prerequisite arrows;
  Mission Art/icon_review.png shows all 48 icons at enlarged inspection size.

Editing and verification
- The editable game files are missions/02_Nippon_missions.txt, the matching
  war_nippon_mission_modifiers and war_nippon_mission_triggers files, events/
  War_Nippon_Mission_Events.txt, and localisation/war_nippon_missions_l_english.yml.
- build_missions.py regenerates the mission, reward, event, localisation and
  design files. Update it too if future changes should survive regeneration.
- prepare_art.py packages sources, registers the new sprites, and redraws previews.
- validate_missions.py checks syntax, references, geometry, all reward arithmetic
  against the balance guide, starting history, scope scenarios and icon uniqueness.
  It needs Pillow; use the bundled workspace Python when system Python lacks it.
- validation.json records the latest results. Validation is static and synthetic;
  the new tree still needs a fresh EU4 load and an in-game playtest.
