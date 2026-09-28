# Moot mission artwork

This artwork pass replaces pictures in 41 of the Moot's 48 missions. It adds 12 original halfling and ingredient illustrations generated with the built-in image generation tool, imports 9 suitable EU4 pictures, and registers 2 existing mod pictures under Moot-specific sprite names. Seven existing assignments remain appropriate: Dwarf friendships, Witch Hunters, hired heroes, Ogre guests, beer, wine, and coffee.

- [Artwork preview](moot_mission_art_preview.png): each added or newly registered picture at native 59×63 and doubled size.
- [Mission tree preview](moot_mission_tree_preview.png): all 48 assignments in the approved layout, with prerequisites. This is a generated reference diagram, not an in-game screenshot.
- [Manifest](manifest.json): exact generation prompts, source provenance, texture paths, and all mission assignments.
- `sources/`: full-resolution originals for the 12 generated illustrations.

The consumed textures are `gfx/interface/missions/mission_moot_*.dds`, registered in `interface/war_missions.gfx`. The boundary and undead sprites reference existing mod textures directly. Original spellings of existing texture filenames are preserved.

Generated originals are center-cropped to the mission aspect ratio and downsampled with Pillow LANCZOS to 59×63, then exported as uncompressed RGBA8 DDS. Imported EU4 textures are copied without alteration. Mission objectives, rewards, positions, and prerequisites are unchanged.

Validation passed for unique sprite registration, DDS decoding and dimensions, source-copy integrity, and the existing Moot mission validator. The artwork was reviewed at native and doubled size. An EU4 launch is still needed to check presentation in the game engine.
