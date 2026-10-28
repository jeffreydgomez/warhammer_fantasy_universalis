#!/usr/bin/env python3
"""Static checks and state-transition checks for the artifact browser.

This does not replace an in-game GUI/event-navigation smoke test.
"""
import argparse
import importlib.util
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True

SPEC = importlib.util.spec_from_file_location("builder", Path(__file__).with_name("build_artifact_browser.py"))
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)
ROOT = builder.ROOT


def parse(source):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|#[^\n]*|[{}=]|[^\s{}=#]+', source)
    tokens = [t for t in tokens if not t.startswith("#")]
    pos = 0

    def block(nested=False):
        nonlocal pos
        entries = []
        while pos < len(tokens):
            key = tokens[pos]
            pos += 1
            if key == "}":
                assert nested, "Unexpected closing brace"
                return entries
            assert pos < len(tokens) and tokens[pos] == "=", (key, tokens[pos:pos + 5])
            pos += 1
            value = tokens[pos]
            pos += 1
            entries.append((key, block(True) if value == "{" else value.strip('"')))
        assert not nested, "Unclosed block"
        return entries
    return block()


def get(block, key, default=None):
    return next((v for k, v in block if k == key), default)


def walk(block):
    for k, v in block:
        yield k, v
        if isinstance(v, list):
            yield from walk(v)


def evaluate(block, scope, world):
    """Evaluate the actual generated predicate subset against small game states."""
    result = []
    for key, value in block:
        if key == "NOT":
            # EU4 NOT is NOR over its children, not an inverted implicit AND.
            result.append(not any(evaluate([child], scope, world) for child in value))
        elif key == "AND":
            result.append(evaluate(value, scope, world))
        elif key == "OR":
            result.append(any(evaluate([child], scope, world) for child in value))
        elif key == "always":
            result.append(value == "yes")
        elif key == "exists":
            assert value.startswith("event_target:")
            result.append(world["targets"].get(value.removeprefix("event_target:")) is not None)
        elif key == "has_country_flag":
            result.append(value in world["country_flags"])
        elif key == "ai":
            result.append((value == "yes") == world.get("ai", False))
        elif key.startswith("event_target:"):
            target = world["targets"].get(key.removeprefix("event_target:"))
            result.append(target is not None and evaluate(value, target, world))
        elif key == "has_province_modifier":
            result.append(value in scope.get("modifiers", set()))
        elif key == "has_country_modifier":
            result.append(value in scope.get("modifiers", set()))
        elif key == "any_province":
            result.append(any(evaluate(value, p, world) for p in world["provinces"]))
        elif key == "is_city":
            result.append(scope.get("is_city", True) == (value == "yes"))
        elif key == "war_adventurer_present":
            result.append(any(m.startswith("war_adventurer_") for m in scope.get("modifiers", set())) == (value == "yes"))
        elif key == "owned_by":
            assert value in {"ROOT", "FROM"}
            result.append(scope.get("owner") == world["player"])
        elif key == "owner":
            result.append(bool(scope.get("owner")) and evaluate(value, {}, world))
        elif key == "has_global_flag":
            result.append(value in world["flags"])
        else:
            raise AssertionError(f"Unhandled predicate {key}")
        if not result[-1]:
            return False
    return all(result)


def effects(block, scope, world, definitions):
    """Execute browser scripts against small worlds, including queued event snapshots."""
    matched = False
    for key, value in block:
        if key == "hidden_effect":
            effects(value, scope, world, definitions)
        elif key == "if":
            matched = evaluate(get(value, "limit"), scope, world)
            if matched:
                effects([(k, v) for k, v in value if k != "limit"], scope, world, definitions)
        elif key == "else":
            if not matched:
                effects(value, scope, world, definitions)
        elif key in {"every_province", "every_country"}:
            world["scans"] += 1
            for item in world.get("provinces" if key == "every_province" else "countries", []):
                if evaluate(get(value, "limit", []), item, world):
                    effects([(k, v) for k, v in value if k != "limit"], item, world, definitions)
        elif key == "clear_global_event_target":
            world["targets"].pop(value, None)
        elif key in {"save_global_event_target_as", "save_event_target_as"}:
            world["targets"][value] = scope
        elif key.startswith("event_target:"):
            target = world["targets"].get(key.removeprefix("event_target:"))
            if target is not None:
                effects(value, target, world, definitions)
        elif key == "country_event":
            world.setdefault("events", []).append((get(value, "id"), dict(world["targets"])))
        elif key == "set_country_flag":
            world["country_flags"].add(value)
        elif key == "clr_country_flag":
            world["country_flags"].discard(value)
        elif key == "remove_province_modifier":
            scope["modifiers"].discard(value)
            scope.setdefault("permanent", set()).discard(value)
        elif key == "add_permanent_province_modifier":
            assert get(value, "duration") == "-1"
            scope["modifiers"].add(get(value, "name"))
            scope.setdefault("permanent", set()).add(get(value, "name"))
        elif key in definitions:
            assert value == "yes"
            effects(definitions[key], scope, world, definitions)
        else:
            raise AssertionError(f"Unexpected browser effect: {key}")


def check_reports(prefix, entries, bindings, event_script, values, definitions, expected_pictures):
    """Check the actual click paths and event arrows for current, moved and absent entries."""
    events = {get(v, "id"): v for k, v in event_script if k == "country_event"}
    assert len(events) == 2 * len(entries)
    pictures = {get(body, "name"): body for kind, body in walk(parse(
        (ROOT / "interface/war_eventpictures.gfx").read_text())) if kind == "spriteType"}
    for number, key, target, modifier, controls in entries:
        for suffix in (number, 100 + number):
            report = events[f"{prefix}.{suffix}"]
            picture = get(report, "picture")
            assert picture == expected_pictures[key], (key, picture)
            assert picture in pictures
            assert (ROOT / get(pictures[picture], "texturefile")).is_file(), picture
            assert get(report, "is_triggered_only") == "yes"
            assert get(report, "title") in values and get(report, "desc") in values
            assert get(report, "option") == [("name", prefix + "_report_close")]
            assert get(report, "immediate") is None and get(report, "after") is None
            assert get(report, "goto") == (prefix + "_province" if suffix == number else None)
        for control_name in controls:
            assert bindings[control_name][0] == "custom_button"
            control = bindings[control_name][1]
            assert get(control, "trigger") == []
            assert [k for k, _ in get(control, "effect")] == ["hidden_effect"]
            for case in ("own", "foreign", "unowned", "undiscovered", "uncached", "moved", "absent"):
                old = {"id": 1, "owner": "ME", "modifiers": set()}
                province = {"id": 2, "owner": None if case == "unowned" else "ME" if case == "own" else "FOREIGN",
                            "modifiers": set() if case == "absent" else {modifier}, "discovered": case != "undiscovered"}
                targets = {} if case == "uncached" else {target: old if case == "moved" else province}
                world = {"targets": targets, "provinces": [old, province], "flags": set(), "player": "ME",
                         "country_flags": {prefix + "_open"}, "scans": 0}
                effects(get(control, "effect"), {}, world, definitions)
                assert prefix + "_open" not in world["country_flags"]
                expected = f"{prefix}.{100 + number if case == 'absent' else number}"
                assert len(world["events"]) == 1 and world["events"][0][0] == expected, (key, case)
                if case != "absent":
                    snapshot = world["events"][0][1]
                    assert snapshot[prefix + "_province"] is province, (key, case)
                    world["targets"][target] = old
                    world["targets"][prefix + "_province"] = old
                    assert snapshot[prefix + "_province"] is province, "Later clicks must not retarget an open report"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-dir", type=Path, required=True)
    args = parser.parse_args()
    # Keep the evaluator honest: the old NAND interpretation hid the regression.
    for a in (False, True):
        for b in (False, True):
            children = [("always", "yes" if v else "no") for v in (a, b)]
            assert evaluate([("NOT", children)], {}, {}) == (not a and not b)
            assert evaluate([("NOT", [("AND", children)])], {}, {}) == (not (a and b))
    outputs = builder.build(args.game_dir)
    for name, data in outputs.items():
        assert (ROOT / name).read_bytes() == data, f"Generated file drift: {name}"
    script_files = [name for name in outputs if name.endswith((".txt", ".gui", ".gfx"))]
    parsed = {name: parse(outputs[name].decode()) for name in script_files}
    custom = parsed["common/custom_gui/war_artifact_browser.txt"]
    gui = parsed["interface/countrydecisionsview.gui"]
    bindings = {get(v, "name"): (k, v) for k, v in custom}
    assert len(bindings) == len(custom), "Duplicate custom GUI binding"
    scripted = {get(v, "name"): (k, v) for k, v in walk(gui)
                if isinstance(v, list) and get(v, "scripted") == "yes"
                and get(v, "name", "").startswith("war_artifact_browser_")}
    assert set(bindings) == set(scripted), "Unbound GUI control"
    types = {"custom_window": "windowType", "custom_button": "guiButtonType", "custom_icon": "iconType"}
    for name, (kind, _) in bindings.items():
        assert types[kind] == scripted[name][0], name

    # Resolve sprites/fonts using mod overrides before the installed game.
    definitions = {}
    for base in (args.game_dir, ROOT):
        for path in (base / "interface").glob("*.gfx"):
            # Other existing gfx files can contain legacy syntax; isolate named
            # definitions instead of treating them as browser validation failures.
            for kind, name in re.findall(r'(spriteType|textSpriteType|corneredTileSpriteType|bitmapfont)\s*=\s*\{\s*name\s*=\s*"?([\w_]+)', path.read_text(errors="replace"), re.I):
                definitions[name] = kind
    window = scripted["war_artifact_browser_window"][1]
    for key, value in walk(window + scripted["war_artifact_browser_open"][1]):
        if key in {"quadTextureSprite", "spriteType", "font", "buttonFont"}:
            assert value in definitions, f"Missing {key}: {value}"
    for key, value in walk(parsed["interface/war_artifact_browser.gfx"]):
        if key == "texturefile":
            assert any((base / value).is_file() for base in (ROOT, args.game_dir)), value
        if key == "effectFile":
            assert any((base / value.replace(".lua", ".shader")).is_file() for base in (ROOT, args.game_dir)), value

    # Static tooltip content must be inline: nested $key$ references were blank
    # in-game. Only province/owner/superregion needs runtime localization.
    loc_bytes = outputs["localisation/war_artifact_browser_l_english.yml"]
    assert loc_bytes.startswith(b"\xef\xbb\xbf")
    loc = loc_bytes.decode("utf-8-sig")
    keys = re.findall(r"^\s*(\w+):0", loc, re.M)
    assert len(keys) == len(set(keys))
    all_keys = set(keys)
    loc_values = dict(re.findall(r'^\s*(\w+):0\s+"(.*)"', loc, re.M))
    source_loc = dict(re.findall(r'^\s*(\w+):0\s+"(.*)"', (ROOT / "localisation/war_artifacts_l_english.yml").read_text(encoding="utf-8-sig"), re.M))
    assert not re.search(r"(?<!\\n)\\n(?!\\n)", loc), "Use double line breaks"
    assert "$" not in loc, "Nested static localization is unreliable in custom GUI tooltips"
    assert "local goods produced" not in loc.lower()
    for removed in ("Not held by us", "Benefits while held", "Hover and press", "Hover an artifact", "pin the", "pin its", "_selected", "GetWarArtifactState"):
        assert removed.lower() not in loc.lower(), removed
    assert loc_values["war_artifact_browser_unfound"] == "The Grail has not yet been found."
    assert loc_values["war_artifact_browser_unforged"] == "The Gromril Crown has not yet been forged."
    assert "has been destroyed" in loc_values["war_artifact_browser_consumed"]
    dynamics = parsed["customizable_localization/war_artifact_browser.txt"]
    functions = {get(v, "name"): v for k, v in dynamics}
    for func in re.findall(r"\[Root\.(GetWarArtifact\w+)\]", loc):
        assert func in functions, func
    for key, value in walk(dynamics + custom):
        if key in {"localisation_key", "tooltip"}:
            assert value in all_keys, value

    def location(n, world):
        branches = [v for k, v in functions[f"GetWarArtifactLocation{n}"] if k == "text"]
        return next(get(v, "localisation_key") for v in branches if evaluate(get(v, "trigger", []), {}, world))

    # Meaningful state regressions: actual generated predicates must partition
    # owned/unowned and reject stale/consumed targets, without gating on discovery
    # or treating occupation and subject possession as direct ownership.
    artifacts = [a for _, _, group in builder.GROUPS for a in group]
    modifiers = builder.read_modifiers()
    for n, (artifact, _, _) in enumerate(artifacts, 1):
        name = f"war_artifact_browser_{artifact}"
        target = f"war_artifact_location_{artifact}"
        mod = builder.modifier_id(artifact)
        title, benefits, lore, current_location = loc_values[name + "_tt"].split(r"\n\n")
        assert title == f"§Y{source_loc[mod]}§!", artifact
        assert benefits == builder.benefits(modifiers[mod], hidden=builder.HIDDEN_BENEFITS), artifact
        assert loc_values[name + "_located"] == f"§Y[{target}.GetName]§!, §Y[{target}.Owner.GetName]§!, §Y[{target}.GetSuperRegionName]§!"
        assert loc_values[name + "_unowned_location"] == f"§Y[{target}.GetName]§!, §YUnowned§!, §Y[{target}.GetSuperRegionName]§!"
        assert len(re.split(r"(?<=[.!?])\s+", lore)) == 2, artifact
        assert current_location == f"[Root.GetWarArtifactLocation{n}]", artifact
        for state in ("owned", "unowned"):
            kind, control = bindings[name + "_" + state]
            assert kind == "custom_button" and get(control, "effect") and get(control, "trigger") == []
            assert get(control, "tooltip") == name + "_tt"
        missing = {"grail": "unfound", "gromril_crown": "unforged"}.get(artifact, "missing_location")
        cases = [
            ("owned", {"owner": "ME", "modifiers": {mod}}, True, name + "_located"),
            ("foreign", {"owner": "THEM", "modifiers": {mod}}, False, name + "_located"),
            ("occupied", {"owner": "THEM", "controller": "ME", "modifiers": {mod}}, False, name + "_located"),
            ("subject", {"owner": "SUBJECT", "modifiers": {mod}}, False, name + "_located"),
            ("undiscovered", {"owner": "THEM", "discovered": False, "modifiers": {mod}}, False, name + "_located"),
            ("unowned", {"owner": None, "modifiers": {mod}}, False, name + "_unowned_location"),
            ("stale", {"owner": "ME", "modifiers": set()}, False, "war_artifact_browser_" + missing),
            ("absent", None, False, "war_artifact_browser_" + missing),
        ]
        for case, province, expected_owned, expected_location in cases:
            world = {"targets": {target: province} if province else {}, "player": "ME", "flags": set()}
            owned = evaluate(get(bindings[name + "_owned"][1], "potential"), {}, world)
            unowned = evaluate(get(bindings[name + "_unowned"][1], "potential"), {}, world)
            assert owned == expected_owned and owned != unowned, (artifact, case)
            assert location(n, world) == expected_location, (artifact, case, location(n, world))
        # Gifts/theft follow a replacement cached target rather than the start province.
        world["targets"][target] = {"owner": "ME", "modifiers": {mod}}
        assert evaluate(get(bindings[name + "_owned"][1], "potential"), {}, world)
        assert location(n, world) == name + "_located"
        if artifact in {"carstein_ring", "staff_of_nagash", "nagashs_tome", "jade_blooded_vial", "bleeding_idol"}:
            world = {"targets": {target: {"owner": "ME", "modifiers": set()}}, "player": "ME", "flags": {"nagash_resurrected"}}
            assert location(n, world) == "war_artifact_browser_consumed", artifact
            # The unconsumed fifth relic must retain its real location after the ritual.
            world["targets"][target] = {"owner": "THEM", "modifiers": {mod}}
            assert location(n, world) == name + "_located", artifact
        if artifact in {"grail", "gromril_crown"}:
            flag = "grail_has_been_found" if artifact == "grail" else "gromril_crown_forged"
            world = {"targets": {}, "player": "ME", "flags": {flag}}
            assert location(n, world) == "war_artifact_browser_missing_location", artifact

    # The opener is outside the gated collection and
    # lies left of National Decisions, above the first decision row.
    assert not (ROOT / "decisions/War_Artifact_Browser.txt").exists()
    assert "war_artifact_browser_open" not in {get(v, "name") for _, v in walk(window) if isinstance(v, list)}
    opener = scripted["war_artifact_browser_open"][1]
    pos = dict(get(opener, "position"))
    assert int(pos["x"]) + 105 < 171 and int(pos["y"]) + 31 < 436
    assert loc_values[get(opener, "buttonText")] == "Artifacts"
    assert all(get(body, "trigger") == [] for kind, body in custom if kind == "custom_button")
    assert builder.NECROMANCY == {"carstein_ring", "staff_of_nagash", "nagashs_tome", "jade_blooded_vial", "bleeding_idol"}
    assert builder.LAYOUT["necromancy"][1] >= max(y + 110 for group, (_, y, _) in builder.LAYOUT.items() if group != "necromancy")
    report_entries = [(n, f"war_artifact_browser_{a}", f"war_artifact_location_{a}", builder.modifier_id(a),
                       [f"war_artifact_browser_{a}_{s}" for s in ("owned", "unowned")])
                      for n, (a, _, _) in enumerate(artifacts, 1)]
    check_reports("war_artifact_browser", report_entries, bindings, parsed["events/War_Artifact_Browser.txt"],
                  loc_values, dict(parse((ROOT / "common/scripted_effects/war_artifact_effects.txt").read_text())),
                  {f"war_artifact_browser_{a}": picture for a, picture in builder.EVENT_PICTURES.items()})

    # Removing our insertion must recover the installed view byte-for-text.
    content = outputs["interface/countrydecisionsview.gui"].decode()
    for kind in ("ARTIFACT", "ADVENTURER"):
        begin, end_marker = (f"\t\t# {edge} GENERATED WAR {kind} BROWSER" for edge in ("BEGIN", "END"))
        if begin in content:
            start, rest = content.split(begin)
            _, end = rest.split(end_marker)
            content = start + end.lstrip("\n")
    assert content == (args.game_dir / "interface/countrydecisionsview.gui").read_text()
    print(f"PASS: 24 artifacts, 192 ownership/location cases, 48 lore events, 336 navigation cases, transfer/consumption/creation cases, {len(bindings)} GUI bindings, assets/fonts/shaders, localization closure/BOM, preserved vanilla view and deterministic regeneration.")


if __name__ == "__main__":
    main()
