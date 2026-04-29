# Agent Instructions

## EU4 Balance Guide

- When adding or changing modifiers or effects, always reference Jeff's EU4 balance guide at `Dev Stuff/Examples/Balance Guide.txt`.
- Use the guide's `Weighing Value` as the source of truth for judging effect and modifier strength.
- Each individual idea in an idea group should total a `Weighing Value` of 10.
- Random events should choose an intended event `Weighing Value` from -3 to +3 inclusive, depending on whether the event is bad, neutral, or good.
- Each random event option should total within +1/0/-1 of the event's intended `Weighing Value`, and each option's total `Weighing Value` should be commented in the event script.
- It is acceptable to mix and match effects and modifiers to hit the target value. Increase or decrease effect magnitudes together with their `Weighing Value` so the balance target remains intentional.
- Use `add_country_modifier` sparingly in random events. Prefer direct effects from the balance guide when they fit, and keep timed country modifiers to roughly half or less of the options in a new event batch unless the design specifically needs them.
- If the guide is unavailable or does not cover a modifier/effect being used, call that out before making a balance-sensitive change.

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

- Use "\n\n" for line breaks.
- Event descriptions should be 2-3 paragraphs of 2-4 sentences each. Vary paragraph counts and paragraph sentence counts across event batches.
