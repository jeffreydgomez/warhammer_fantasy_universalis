#!/usr/bin/env python3
"""Validate the adventurer UI, live location cache, and collection switching."""
import argparse
from copy import deepcopy
import importlib.util
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load("adventurer_builder", "build_adventurer_browser.py")
checks = load("artifact_checks", "validate_artifact_browser.py")
parse, get, walk = checks.parse, checks.get, checks.walk
ROOT = builder.ROOT


condition = checks.evaluate
effects = checks.effects


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-dir", type=Path, required=True)
    args = parser.parse_args()
    outputs = builder.build(args.game_dir)
    for name, data in outputs.items():
        assert (ROOT / name).read_bytes() == data, f"Generated file drift: {name}"
    parsed = {name: parse(data.decode()) for name, data in outputs.items() if name.endswith((".txt", ".gui", ".gfx"))}
    custom = parsed["common/custom_gui/war_adventurer_browser.txt"]
    bindings = {get(v, "name"): (k, v) for k, v in custom}
    assert len(bindings) == len(custom) == 22
    host = parsed["interface/countrydecisionsview.gui"]
    scripted = {get(v, "name"): (k, v) for k, v in walk(host)
                if isinstance(v, list) and get(v, "scripted") == "yes"
                and get(v, "name", "").startswith("war_adventurer_browser_")}
    assert set(bindings) == set(scripted)
    kinds = {"custom_window": "windowType", "custom_button": "guiButtonType", "custom_icon": "iconType"}
    for name, (kind, _) in bindings.items():
        assert kinds[kind] == scripted[name][0], name
    opener = scripted["war_adventurer_browser_open"][1]
    pos = dict(get(opener, "position"))
    assert int(pos["x"]) > 371 and int(pos["x"]) + 105 < 535 and int(pos["y"]) + 31 < 436

    assets = {}
    for base in (args.game_dir, ROOT):
        for path in (base / "interface").glob("*.gfx"):
            for kind, name in re.findall(r'(spriteType|textSpriteType|corneredTileSpriteType|bitmapfont)\s*=\s*\{\s*name\s*=\s*"?([\w_]+)', path.read_text(errors="replace"), re.I):
                assets[name] = kind
    window = scripted["war_adventurer_browser_window"][1]
    for key, value in walk(window + opener):
        if key in {"spriteType", "quadTextureSprite", "font", "buttonFont"}:
            assert value in assets, (key, value)
    gfx = parsed["interface/war_adventurer_browser.gfx"]
    for key, value in walk(gfx):
        if key == "texturefile":
            assert any((base / value).is_file() for base in (ROOT, args.game_dir)), value
        if key == "effectFile":
            assert value == "gfx/FX/buttonstate.lua", "Portraits must remain colored"
            assert (args.game_dir / value.replace(".lua", ".shader")).is_file()

    loc_bytes = outputs["localisation/war_adventurer_browser_l_english.yml"]
    assert loc_bytes.startswith(b"\xef\xbb\xbf")
    loc = loc_bytes.decode("utf-8-sig")
    pairs = re.findall(r'^\s*(\w+):0\s+"(.*)"', loc, re.M)
    values = dict(pairs)
    assert len(values) == len(pairs) and "$" not in loc
    assert "local trade power" not in loc.lower()
    assert not re.search(r"(?<!\\n)\\n(?!\\n)", loc)
    assert values[get(opener, "buttonText")] == "Adventurers"
    dynamics = parsed["customizable_localization/war_adventurer_browser.txt"]
    functions = {get(body, "name"): body for _, body in dynamics}
    for key, value in walk(custom + dynamics):
        if key in {"tooltip", "localisation_key"}:
            assert value in values, value
    data = builder.read_data()
    for index, slug in enumerate(builder.ROSTER, 1):
        key = f"war_adventurer_browser_{slug}"
        target = f"war_adventurer_location_{slug}"
        mod = f"war_adventurer_{slug}"
        title, bonuses, lore, current = values[key + "_tt"].split(r"\n\n")
        assert title == f"§Y{data[slug]['name']}§!" and lore == data[slug]["lore"]
        assert bonuses == builder.shared.benefits(data[slug]["values"], builder.LABELS, builder.HIDDEN_BENEFITS)
        assert values[key + "_located"] == f"§Y[{target}.GetName]§!, §Y[{target}.Owner.GetName]§!, §Y[{target}.GetSuperRegionName]§!"
        assert values[key + "_unowned_location"] == f"§Y[{target}.GetName]§!, §YUnowned§!, §Y[{target}.GetSuperRegionName]§!"
        assert current == f"[Root.GetWarAdventurerBrowserLocation{index}]"
        kind, body = bindings[key]
        assert kind == "custom_button" and get(body, "potential") == [("always", "yes")]
        assert get(body, "effect") and get(body, "trigger") == []
        assert get(scripted[key][1], "scale") == "0.4375"
        branches = [v for k, v in functions[f"GetWarAdventurerBrowserLocation{index}"] if k == "text"]
        for province, expected in [
            ({"owner": "ME", "modifiers": {mod}}, key + "_located"),
            ({"owner": "FOREIGN", "modifiers": {mod}}, key + "_located"),
            ({"owner": "SUBJECT", "modifiers": {mod}}, key + "_located"),
            ({"owner": "FOREIGN", "controller": "ME", "modifiers": {mod}}, key + "_located"),
            ({"owner": "FOREIGN", "discovered": False, "modifiers": {mod}}, key + "_located"),
            ({"owner": None, "modifiers": {mod}}, key + "_unowned_location"),
            ({"owner": "ME", "modifiers": set()}, "war_adventurer_browser_missing_location"),
            (None, "war_adventurer_browser_missing_location"),
        ]:
            world = {"targets": {target: province}, "player": "ME", "flags": set()}
            actual = next(get(v, "localisation_key") for v in branches if checks.evaluate(get(v, "trigger", []), {}, world))
            assert actual == expected, (slug, actual, expected)
            assert condition(get(body, "potential"), {}, world), "Foreign/missing portraits must remain visible"

    definitions = dict(parsed["common/scripted_effects/war_adventurer_browser_effects.txt"])
    definitions.update(dict(parse((ROOT / "common/scripted_effects/war_artifact_effects.txt").read_text())))
    report_entries = [(i, f"war_adventurer_browser_{slug}", f"war_adventurer_location_{slug}", f"war_adventurer_{slug}",
                       [f"war_adventurer_browser_{slug}"]) for i, slug in enumerate(builder.ROSTER, 1)]
    checks.check_reports("war_adventurer_browser", report_entries, bindings, parsed["events/War_Adventurer_Browser.txt"], values, definitions,
                         {f"war_adventurer_browser_{slug}": data[slug]["picture"] for slug in builder.ROSTER})
    provinces = [{"id": i, "owner": "FOREIGN", "modifiers": {f"war_adventurer_{slug}"}} for i, slug in enumerate(builder.ROSTER)]
    world = {"targets": {}, "player": "ME", "flags": set(), "country_flags": {"war_artifact_browser_open"},
             "provinces": provinces, "scans": 0}
    original = deepcopy(provinces)
    for province in original:
        province["permanent"] = set(province["modifiers"])
    open_effect = get(bindings["war_adventurer_browser_open"][1], "effect")
    effects(open_effect, {}, world, definitions)
    assert world["country_flags"] == {"war_adventurer_browser_open"} and world["scans"] == 1
    assert condition(get(bindings["war_adventurer_browser_window"][1], "potential"), {}, world)
    for i, slug in enumerate(builder.ROSTER):
        assert world["targets"][f"war_adventurer_location_{slug}"] is provinces[i]
    assert provinces == original, "Migration must only mark existing presence as permanent"
    effects(open_effect, {}, world, definitions)
    assert world["scans"] == 1, "Already-open collection should not rescan"
    # Move one traveller, remove another, and refresh with deliberately stale targets.
    first, second = builder.ROSTER[:2]
    provinces[0]["modifiers"].clear()
    provinces[0]["permanent"].clear()
    provinces[1]["modifiers"] = {f"war_adventurer_{first}"}
    provinces[1]["permanent"].clear()
    before_refresh = deepcopy(provinces)
    before_refresh[1]["permanent"] = {f"war_adventurer_{first}"}
    effects(get(bindings["war_adventurer_browser_refresh"][1], "effect"), {}, world, definitions)
    assert world["targets"][f"war_adventurer_location_{first}"] is provinces[1]
    assert f"war_adventurer_location_{second}" not in world["targets"]
    assert provinces == before_refresh
    artifact_custom = parse((ROOT / "common/custom_gui/war_artifact_browser.txt").read_text())
    artifact_open = next(v for _, v in artifact_custom if get(v, "name") == "war_artifact_browser_open")
    effects(get(artifact_open, "effect"), {}, world, definitions)
    assert world["country_flags"] == {"war_artifact_browser_open"}
    assert not condition(get(bindings["war_adventurer_browser_window"][1], "potential"), {}, world)
    effects(open_effect, {}, world, definitions)
    effects(get(bindings["war_adventurer_browser_close"][1], "effect"), {}, world, definitions)
    assert not world["country_flags"]
    for name in ("common/custom_gui/war_adventurer_browser.txt", "customizable_localization/war_adventurer_browser.txt"):
        assert b"every_province" not in outputs[name] and b"every_country" not in outputs[name]
    # Existing unlimited-duration modifiers must survive conquest after migration.
    for province in provinces:
        province["owner"] = "CONQUEROR"
        province["modifiers"] &= province.get("permanent", set())
    assert sum(bool(p["modifiers"]) for p in provinces) == 17
    setup = parse((ROOT / "events/War_Adventurer_Setup.txt").read_text())
    event_defs = {get(v, "id"): v for k, v in setup if k in {"country_event", "province_event"}}
    migration = event_defs["war_adventurer_setup.2"]
    assert get(migration, "fire_only_once") == "yes" and get(migration, "hidden") == "yes"
    assert get(migration, "immediate") == [("war_adventurer_browser_rebuild_locations", "yes")]
    assert "war_adventurer_setup.2" in (ROOT / "common/on_actions/war_startup_on_actions.txt").read_text()
    placements = [v for k, v in walk(setup) if k == "add_permanent_province_modifier"]
    assert len(placements) == 37  # two initial paths per traveller, plus manual Thanquol recovery
    assert not any(k == "add_province_modifier" for k, _ in walk(setup))
    movement = parse((ROOT / "common/scripted_effects/war_adventurer_effects.txt").read_text())
    assert not any(k == "add_province_modifier" for k, _ in walk(movement))
    assert any(k == "add_permanent_province_modifier" for k, _ in walk(movement))
    assert any(k == "remove_province_modifier" for k, _ in walk(movement)), "Travellers must still leave their old province"
    # Manual recovery is safe when repeated, and never duplicates a traveller elsewhere.
    repair = get(event_defs["war_adventurer_setup.3"], "immediate")
    for case in ("lost", "elsewhere", "occupied", "not_city"):
        here = {"id": 4623, "owner": "ME", "is_city": case != "not_city", "modifiers": {"war_adventurer_gelt"} if case == "occupied" else set()}
        elsewhere = {"id": 4600, "owner": "FOREIGN", "modifiers": {"war_adventurer_thanquol"} if case == "elsewhere" else set()}
        repair_world = {"targets": {}, "provinces": [here, elsewhere], "scans": 0}
        effects(repair, here, repair_world, definitions)
        effects(repair, here, repair_world, definitions)
        assert ("war_adventurer_thanquol" in here["modifiers"]) == (case == "lost")
        if case == "lost":
            assert repair_world["targets"]["war_adventurer_location_thanquol"] is here
            assert "war_adventurer_thanquol" in here["permanent"]
    print("PASS: 18 adventurers, 144 location scenarios, 36 lore events, 126 navigation cases, ownership-transfer migration, guarded recovery, 22 GUI bindings, always-colored portraits, panel switching, assets, BOM and deterministic generation.")


if __name__ == "__main__":
    main()
