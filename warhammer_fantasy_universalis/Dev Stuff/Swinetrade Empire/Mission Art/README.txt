Pigbarter / Swinetrade Empire mission artwork

The 50-mission tree uses 25 new custom illustrations and 25 distinct existing
icons. Each mission has a unique sprite, texture path and decoded image.

The new illustrations were made with built-in image_gen. manifest.json records
the exact submitted prompts, flag references, original generated paths, local
source copies, texture paths, export dimensions and file hashes. The full-size
originals are preserved in sources/. The generation originals were left intact.

Game textures live in gfx/interface/missions/mission_swine_*.dds and are
registered in interface/war_missions.gfx. Exports use a centred crop and Lanczos
resize to 59 x 63 pixels, saved as uncompressed RGBA8 DDS. previews/ contains
matching PNGs. No gameplay requirements or rewards changed during this art pass.

custom_icons_preview.png shows all 25 new textures at native and doubled size.
mission_tree_icons_preview.png shows all 50 assignments in their mission layout;
gold outlines identify new art. These are review images, not game screenshots.

validation.json records the decoded-image uniqueness check, DDS dimensions,
source-copy integrity, native-size visual review and unchanged gameplay checks.
The parent validate_missions.py also guards against repeated sprite names,
shared texture paths and duplicate texture files. Static checks passed; this
art pass has not been playtested in EU4.
