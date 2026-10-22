"""Crop downloaded character artwork and register EU4 event sprites.

Usage: python3 build_portraits.py /path/to/downloaded/images
The directory must contain CODE.img for each character in art_sources.json.
Requires Pillow. Only framing, resizing and format conversion are performed.
"""
from pathlib import Path
import json
import re
import sys
from PIL import Image, ImageOps, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCES = json.loads((HERE / 'art_sources.json').read_text())
# Match the existing event banners; taller textures draw across the event description.
EVENT_SIZE = (512, 132)
PREVIEW_ROW = EVENT_SIZE[1] + 30
# Normalized crop rectangles, chosen to retain faces and remove poster titles.
CROPS = {
    'GEL': (0, .02, 1, .47),
    'TEC': (0, 0, .49, .64),
    'SNI': (0, 0, 1, 1),
    'BUG': (.02, .05, .99, .74),
    'BAR': (0, 0, 1, .65),
    'HAR': (.08, .03, .98, .98),
    'ABH': (.08, .12, .94, .60),
    'ELS': (.20, .02, .84, .85),
    'WUL': (0, .02, 1, .78),
    'GOF': (0, .02, 1, .68),
    'REP': (.05, .04, .70, .92),
    'SIE': (.13, .27, .98, .70),
    'MAL': (.56, 0, 1, 1),
    'TYR': (0, .02, 1, .67),
    'GOR': (.03, .08, .98, .65),
    'NAK': (.01, .28, 1, 1),
    'THA': (0, 0, 1, 1),
    'GRO': (0, .02, 1, .65),
}
# Face placement within the narrow event banner, checked against the original artwork.
CENTERING = {'BAR': (.5, 0), 'ELS': (.5, .10), 'GOF': (.5, .10),
             'REP': (.5, 0), 'SIE': (.5, .15), 'NAK': (.5, 0)}

def main():
    source_dir = Path(sys.argv[1])
    preview = Image.new('RGB', (1536, 6 * PREVIEW_ROW), '#171b20')
    draw = ImageDraw.Draw(preview)
    sprites = ['\t# BEGIN WAR_ADVENTURER_PORTRAITS']
    for i, (code, source) in enumerate(SOURCES.items()):
        raw = Image.open(source_dir / (code + '.img')).convert('RGBA')
        canvas = Image.new('RGBA', raw.size, '#171b20')
        canvas.alpha_composite(raw)
        box = tuple(round(v * raw.size[n % 2]) for n, v in enumerate(CROPS[code]))
        art = ImageOps.fit(canvas.convert('RGB').crop(box), EVENT_SIZE,
                           method=Image.Resampling.LANCZOS, centering=CENTERING.get(code, (.5, .25)))
        name = f'WAR_ADVENTURER_{code}_eventPicture'
        relative = f'gfx/event_pictures/{name}.dds'
        art.save(ROOT / relative, format='DDS', pixel_format='DXT1')
        assert Image.open(ROOT / relative).size == EVENT_SIZE
        preview.paste(art, ((i % 3) * 512, (i // 3) * PREVIEW_ROW))
        draw.text(((i % 3) * 512 + 8, (i // 3) * PREVIEW_ROW + EVENT_SIZE[1] + 6),
                  source['character'], fill='white')
        sprites += ['\tspriteType = {', f'\t\tname = "{name}"',
                    f'\t\ttexturefile = "{relative}"', '\t}']
        source['crop_normalized'] = list(CROPS[code])
        source['asset'] = relative
        source['dimensions'] = list(EVENT_SIZE)
        source['crop_centering'] = list(CENTERING.get(code, (.5, .25)))
    sprites.append('\t# END WAR_ADVENTURER_PORTRAITS')
    registry = ROOT / 'interface/war_eventpictures.gfx'
    text = registry.read_text()
    block = '\n'.join(sprites)
    if '# BEGIN WAR_ADVENTURER_PORTRAITS' in text:
        text = re.sub(r'\t*# BEGIN WAR_ADVENTURER_PORTRAITS.*?# END WAR_ADVENTURER_PORTRAITS',
                      lambda _: block, text, flags=re.S)
    else:
        at = text.rfind('}')
        text = text[:at] + block + '\n' + text[at:]
    registry.write_text(text)
    (HERE / 'art_sources.json').write_text(json.dumps(SOURCES, ensure_ascii=False, indent=2) + '\n')
    preview.save(HERE / 'portrait_preview.jpg', quality=90)
    print('Built and registered 18 character portraits (512x132, DXT1 DDS).')

if __name__ == '__main__':
    main()
