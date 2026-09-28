# Sylvania mission artwork

Four original illustrations made with the built-in image generation tool:

| Mission | Sprite |
| --- | --- |
| Guns for the Counts | `mission_sylvania_guns_for_counts` |
| Muster the Mortal Levies | `mission_sylvania_mortal_levies` |
| Discipline Beyond Death | `mission_sylvania_discipline_beyond_death` |
| Underground Workshops | `mission_sylvania_underground_workshops` |

The consumed DDS textures are in `gfx/interface/missions/` and registered in `interface/war_missions.gfx`. The mission references are in `missions/02_Sylvania_missions.txt`. The workshop's internal mission ID remains `sylvania_production_powerhouse`.

- [Preview](sylvania_mission_art_preview.png): native 59×63 and tripled size, decoded from the final DDS files.
- [Manifest](manifest.json): exact prompts, original source paths, and final asset paths.
- `sources/`: full-resolution PNG originals.

The originals were center-cropped to the mission aspect ratio, downsampled with Pillow LANCZOS to 59×63, and exported as uncompressed RGBA8 DDS. Static checks cover sprite references, DDS decoding, localisation encoding, and preservation of mission gameplay data. In-game presentation has not been tested.
