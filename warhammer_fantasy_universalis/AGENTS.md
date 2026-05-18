# Agent Instructions

- We are only working on Warhammer_fantasy_universalis. Ignore the other folders.


## EU4 Balance Guide

- When adding or changing modifiers or effects, always reference Jeff's EU4 balance guide at `Dev Stuff/Examples/Balance Guide.txt`.
- Use the guide's `Weighing Value` as the source of truth for judging effect and modifier strength.
- Each individual idea in an idea group should total a `Weighing Value` of 10.
- Random events should choose an intended event `Weighing Value` from -3 to +3 inclusive, depending on whether the event is bad, neutral, or good.
- Each random event option should total within +1/0/-1 of the event's intended `Weighing Value`, and each option's total `Weighing Value` should be commented in the event script.
- Random event options should not both add and remove the same resource to cancel themselves out. If a balancing adjustment would zero out an effect, remove the self-canceling pair and keep the net `Weighing Value` unchanged.
- It is acceptable to mix and match effects and modifiers to hit the target value. Increase or decrease effect magnitudes together with their `Weighing Value` so the balance target remains intentional.
- Use `add_country_modifier` sparingly in random events. Prefer direct effects from the balance guide when they fit, and keep timed country modifiers to roughly half or less of the options in a new event batch unless the design specifically needs them.
- If the guide is unavailable or does not cover a modifier/effect being used, call that out before making a balance-sensitive change.

## Country Creation

- When creating or wiring a country, work only inside `Warhammer_fantasy_universalis` and follow the local country structure there. The core checklist is: unique tag, tag registration, country definition file, country history file, localisation, flag, a unique national idea group, a unique intro event, and either starting province history or a scripted formation/spawn path.
- Before choosing a tag, check `common/country_tags/war_countries.txt`, `common/country_tags/00_countries.txt`, `history/countries`, `gfx/flags`, and localisation for existing use. Tags must be unique. Prefer the mod's existing tag style for the relevant region or faction, and avoid reserved/problematic tags from the EU4 wiki such as `ADD`, `ADM`, `AND`, `ART`, `AUX`, `CAR`, `CAT`, `CAV`, `CON`, `DIP`, `HAS`, `HRE`, `INF`, `MIL`, `MIN`, `NOT`, `NUL`, `PRN`, `RGB`, `SUM`, `VAL`, and `VAN`.
- Register the tag in `common/country_tags/war_countries.txt` unless an existing local file is clearly more specific. Use the exact form `TAG = "countries/Country File.txt"` and make sure the referenced file exists under `common/countries`.
- Create `common/countries/Country File.txt` by copying a close local analogue, then revise it deliberately. Check `graphical_culture`, `color = { R G B }`, `historical_idea_groups`, `historical_units`, `monarch_names`, `leader_names`, `ship_names`, `army_names`, and `fleet_names`. Use Warhammer-appropriate names and unit lists from the same culture/race where possible.
- Create `history/countries/TAG - Country Name.txt`. Include the starting government setup (`government` and any `add_government_reform`), `primary_culture`, optional accepted cultures, `religion`, `technology_group`, `capital` or `fixed_capital`, `government_rank`, vision setup if the local analogue uses it, and a start-date ruler/heir setup when the country should exist from game start.
- If the country exists on the map at start, edit each starting province history so it has `add_core = TAG`, `owner = TAG`, and `controller = TAG`. For newly split-off start-present countries, remove the previous owner's core from the transferred starting provinces unless the user explicitly asks for old claims to remain. Also check province culture, religion, trade good, estate setup, forts, buildings, and discovery/visibility against nearby local examples. Do not leave a previous owner/controller/core assignment that contradicts the new setup.
- If the country is formed, released, or spawned instead of present at start, wire it through the appropriate decision/event effect path, typically `change_tag = TAG` for formation or `cede_province = TAG` / province ownership effects for spawned countries. Add starting cores/claims and cleanup effects intentionally.
- Add country localisation in an existing appropriate `localisation/*_l_english.yml` file or a new focused country localisation file. Include at least `TAG:0 "Country Name"` and `TAG_ADJ:0 "Adjective"`; add `TAG_ADJ2` only when the surrounding localisation style needs it. Preserve the localisation rules in this AGENTS file, especially UTF-8 with BOM for edited `.yml` files.
- Add `gfx/flags/TAG.tga`. The EU4 country-creation guide expects a 128x128 TGA flag; in this mod, ordinary country flags are named by tag. The flag's predominant field color should match the country's `color = { R G B }`, and the design should be visually distinct from nearby countries and other newly created countries rather than reusing the same layout with small color swaps. Add alternate flags only when the local system already expects them.
- Create a country-specific national idea group for every new playable country unless the user explicitly asks to reuse a generic/shared idea group. Add the idea script, trigger it on the new tag, add idea localisation, and follow the EU4 Balance Guide in this file: each individual idea should total `Weighing Value` 10, and any modifier strength should be justified from `Dev Stuff/Examples/Balance Guide.txt`.
- Add a unique intro event for every new playable country. Use `events/War_Unique_Intro_Events.txt` with the `war_unique_intro_events` namespace and the next unused numeric id, trigger it on `tag = TAG` plus `NOT = { has_country_flag = did_intro_event }`, and set `did_intro_event` in `immediate`. Use an event picture defined in `interface/war_eventpictures.gfx`, include the required concept and option comments, and reference the Lore Reference plus the Balance Guide for flavor and rewards. Add `war_unique_intro_events.ID.t`, `.d`, and `.a` localisation in `localisation/war_unique_intro_events_l_english.yml`, preserving UTF-8 with BOM. For start-present countries, wire the event into `common/on_actions/war_startup_on_actions.txt`; for formed, released, or spawned countries, fire it from the formation/spawn path instead and call out the choice if startup wiring is not appropriate.
- Check downstream hooks after the base country exists: diplomacy history, subjects/overlords, cores and releasability, decisions, missions, events, disasters, estate privileges, scripted triggers, AI setup, bookmarks, trade companies, rebel types, and any region/faction priority systems that should include or exclude the new tag.
- Add every new start-present country to `Dev Stuff/Examples/Country Reference.txt` with the same pipe-delimited schema as the surrounding rows. Include tag, display name, ruler, culture and culture group, religion, tech group, government and reforms, rank, capital with area/region/continent, and a short note describing the country's premise.
- Before considering the country done, verify the tag with targeted searches: the tag registration resolves to the country file, the history file name begins with the tag, the flag exists, localisation has name and adjective, the unique idea group has a tag trigger and localisation, province history grants ownership/core/controller if start-present, the unique intro event has event/localisation/startup-or-spawn wiring, and no duplicate tag, duplicate event id, or broken path exists. If the game or logs are available, check `error.log` for missing country, missing flag, localisation, event, or history parse errors.

## Mission Trees

- When making or editing mission trees, reference Jeff's EU4 balance guide at `Dev Stuff/Examples/Balance Guide.txt` and use its `Weighing Value` to budget rewards.
- When designing mission objectives/triggers, reference `Dev Stuff/Examples/Mission Trigger Catalogue.txt` for existing trigger families, acceptable numerical ranges, difficulty bands, anti-start-completion guidance, and flavor implications.
- Before scripting a mission tree, first draft a conceptual mission table in chat and get approval. The table should show the 5 mission slots/columns, rows, blank spaces, mission concepts, and prerequisite indicators.
- In conceptual mission tables, use prerequisite indicators like `↑` for the nearest mission above in the same column, `↖` for the previous row one column left, and `↗` for the previous row one column right. Use multiple indicators for multiple prerequisites.
- A mission tree should provide roughly 130-180 total `Weighing Value` (not including the 'ultimate mission')
- Most missions should reward about 5 `Weighing Value`. Mission rewards often use permanent country modifiers; for a typical 5-value reward, halve the strength of a modifier that would be worth 10.
- Mission reward modifiers should use clean player-facing increments: prefer values like `0.05`, `0.10`, `0.5`, `1`, `5`, and `10`. Avoid awkward values such as `0.04`, `0.08`, `0.075`, `0.0125`, or `0.8` unless there is a specific balance reason and you call it out.
- Each mission tree should have one ultimate mission as the last entry of slot 3. This should be extremely difficult and reward about 35 total `Weighing Value`.
- Rewards should include some blend of economic, military, diplomatic, and administrative benefits, though individual trees can lean strongly toward one theme.
- About half of a mission tree should be completable with effort within roughly 50 years. The rest should generally be completable by the End Times, roughly 150 years in.
- Mission objectives should only rarely happen by accident. Avoid objectives a tag starts the game with already completed, and do not let any tag begin with a completable mission.
- Choose objective triggers from the catalogue where possible, and prefer active-effort gates such as growth, buildings, estate agendas, war-history proof, institutions, tech, ideas, developed provinces, upgraded centers of trade, diplomacy, or later prerequisites.
- Focus less on conquest than vanilla mission trees; players will naturally conquer. Prefer objectives that represent deliberate state-building, preparation, diplomacy, institutions, faith, economy, military reform, culture, or faction story beats.
- Mission trees should tell a story and feel like a series of historical events that took place as the nation progressed.
- Mission icons should be drawn from images defined in `interface/war_missions.gfx`. Use the image name as the best guess for what the art depicts.
- Mission trees use 5 columns and usually 15-20 rows. Each mission has a `slot` column from the tree block and a `position` row in the mission entry. Mission positions are 1-indexed in-game, so the first visible row should use `position = 1`, not `position = 2`. No two visible missions in the same tree should occupy the same column and row.
- Mission tree blocks should use `generic = yes`, even when the tree is unique to a specific tag. Do not use `generic = no`, because it can prevent the country from also receiving compatible generic mission groups.
- Keep mission tables visually readable: about one third of cells should be blank, every row should have at least one blank cell, and no column should usually have more than three consecutive missions without a blank break.
- Keep prerequisite lines simple. A mission should require another mission only if the required mission is directly above it in the same column with no intervening missions, or if the required mission is on the previous row and one column to the left or right.
- Prefer mission concepts whose prerequisites make narrative and mechanical sense. Avoid arbitrary prerequisite links made only for table shape.
- When using faction or generic mission trees, follow the mod's local priority system in `common/scripted_triggers/war_scripted_triggers_missions.txt` so broader trees exclude more-specific trees with `war_mission_priority_N = no`.
- 2-4 of the most important missions should trigger events with decisions that give different rewards.
- Use comments to indicate conceptually what each mission and modifier is.
- Mission trees should assume the nation has formed its main formable by about the midpoint. Later missions should build from that unity toward outside ambition.
- Descriptions should usually frame the beat as "the situation is Y, so we must X."
- Objectives should use varied trigger families. Most missions should use only 2-3 trigger checks, and building requirements should avoid repeating the same building type unless the repetition is narratively important. Generally, avoid repeating the same trigger across multiple missions.

## Dragon Isles Mission Trees

- Dragon Isles mission trees should emphasize semi-feral, uncivilized Lizardmen trapped between brutal living dragons, blood-clan politics, obsidian rites, and Mesoamerican-inspired step-altars, skull racks, gem tribute, and heart-blood sacrifice. Their story should move from fractured island clans and altar rivalries toward a unified blood-gong realm that survives dragon hunger, bargains with dragons from strength, and turns fear, sacrifice, and clan discipline into harsh state power.
- Dragon Isles trees should assume the Dragon Isles are unified by about the midpoint. Later missions should build from that unity toward outside ambition, especially influence along the River Ruin and inroads into Ind.
- Dragon Isles mission descriptions should usually frame the beat as "the situation is Y, so we must X."
- Dragon Isles mission objectives should use varied trigger families. Most missions should use only 2-3 trigger checks, and building requirements should avoid repeating the same building type unless the repetition is narratively important.
- Prefer the Dragon Isles-specific mission icons in `interface/war_missions.gfx` for dragon pacts, volcanic rites, blood-altars, obsidian gates, and gem tribute when those beats appear.

## Events

- Each new event should have a brief concept comment immediately before the `country_event` or `province_event` block.
- Each event option should have a very short comment describing the option's intent.
- Random events should have between 2 and 4 options. When adding a batch of random events, vary the number of options across the batch.
- Use `goto` only when an event effect actually affects an individual province.
- Event pictures must be selected from images defined in `interface/war_eventpictures.gfx`.
- Usually use the event file's template picture. Choose a different defined picture only when there is a clear flavor or readability reason.

## Lore Reference

- When making or editing events, missions, ideas, localization, or other flavor text, reference `Dev Stuff/Examples/Lore Reference.txt` for the mod's established world-state, faction premises, regional lore, voice, hooks, and mechanics.
- Also reference established Warhammer Fantasy lore when making or editing content. Use official/canonical Warhammer Fantasy names, institutions, rivalries, geography, and tone where they apply.
- If established Warhammer Fantasy lore conflicts with the mod's local premise, preserve the local mod canon and use the outside lore only to improve flavor consistency. Call out meaningful conflicts when they affect design or writing choices.


## Localizations

- New or edited EU4 localisation `.yml` files should be saved as UTF-8 with BOM, matching the existing mod files. If a localization file appears valid but does not load in-game, check for the BOM first.
- Use "\n\n" for line breaks.
- Mission localization should include both `mission_id_title:0 "Mission Name"` and `mission_id_desc:0 "Mission description"`. It is also fine to include the bare `mission_id:0 "Mission Name"` key for compatibility, but do not rely on it alone.
- Event descriptions should be 2-3 paragraphs of 2-4 sentences each. Vary paragraph counts and paragraph sentence counts across event batches.
