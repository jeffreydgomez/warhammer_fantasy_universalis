# Adventurer Province Modifier Design

Design and implementation reference for the selected 18 adventurers in Warhammer Fantasy Universalis, starting in 2502 IC. Updated 21 October 2026. All 360 encounters and 18 arrival notices are now scripted; implementation details, source artwork, and validation are in [Adventurers/README.md](Adventurers/README.md).

This document records the current roster, fixed province modifiers, encounter tables, movement rules, lore reference material, and **360 event concepts: 20 for each of 18 adventurers**. The full catalogue and per-character lore coverage tables are in [section 10](#full-event-catalogue). It supersedes the corresponding proposals in the older 80-entry `Adventurer Province Modifier Event Concepts.txt`; that earlier document is retained as an archive.

## 1. Core system

- Each adventurer, pair, or group has exactly one province modifier marking its location. Pairs count as one travelling entry.
- All 360 encounters remain **triggered-only country events**. `on_bi_yearly_pulse_5` runs the hidden `war_adventurer_pulse.1` coordinator only for the current #1 great power. That event snapshots the visitors' current owners and sends one `war_adventurer_pulse.2` selection event to each distinct host; each eligible host gets one encounter in that global round. The leader's pulse dates determine scheduling, so leadership changes can shift the interval. No round runs without a #1 great power. Visitors are weighted by their eligible story counts, then one eligible story is chosen uniformly, preserving equal odds per story even when extra requirements exclude an incident.
- The host dispatcher checks only visitors recorded for that host in the global snapshot, then caches geography, relationship and eligible story count. Destination existence is checked once for each host with a candidate. The chosen encounter rechecks its own inexpensive conditions without repeating the world destination search. There is no readiness requirement, arrival cooldown or pending-report lock. The ownership snapshot prevents a visitor who moves during the round from being selected again by a later host in that same round. Scheduling/cache flags are cleared after selection.
- The encounter goes to the **current owner** of the province. Ownership, alignment, administration, and location are evaluated when the encounter fires.
- Home/abroad is geographical. Friendly/neutral versus enemy is determined exclusively by the owner's **Alignment and/or Racial Administration**, as specified below.
- Every completed encounter moves the adventurer, regardless of the player's response.
- The presence modifier is identical in friendly, neutral, and enemy countries. It remains in place until the encounter resolves and then transfers to the destination.
- Keep one adventurer per province. A country can host multiple adventurers in different provinces after the initial distribution.

### Encounter categories

| Category | Typical content | Intended event Weighing Value |
|---|---|---:|
| Friendly/neutral, home | Familiar allies, local responsibilities, old grudges, established expertise | +1 or +2 |
| Friendly/neutral, abroad | Expeditions, cultural encounters, discoveries, assistance to strangers | +1 or +2 |
| Enemy, home | Resistance against occupiers, stolen heritage, attacks on familiar enemies | −1 or −2 |
| Enemy, abroad | Sabotage, raids, escaped prisoners, stolen intelligence, destructive confrontations | −1 or −2 |

An enemy occupying a character's homeland gets enemy/home encounters. A friendly state owning distant land gets friendly/abroad encounters. Conquest does not redefine the geographical home range.

## 2. Movement after an encounter

The destination country is selected when the report opens, allowing the effect tooltip to read **“The Adventurer departs for [Country].”** Province selection and the actual transfer wait until the response resolves. Revalidate the announced destination if ownership, borders, or available provinces change while the report is open; if no destination remains, the tooltip simply reads **“The Adventurer remains here.”**

1. Identify the adventurer's current province owner and count its **distinct neighboring countries**, excluding itself. Neighbor means a country connected by a land border or a traversable strait; merely sharing a sea zone does not qualify. Multiple bordering provinces do not increase a country's count. A separate subject country counts as a country.
2. With **two or more neighboring countries**, choose a random eligible neighboring country, then a random eligible province anywhere within that country. The destination province need not itself touch the departure province.
3. With **zero or one neighboring country**, choose a random eligible country **anywhere in the world**, then a random eligible province within it. Exclude the current owner. The sole neighbor may still be selected as part of the worldwide pool; the worldwide choice is not restricted to it.
4. Each eligible country has equal selection weight, followed by equal selection weight among that country's eligible provinces. Large countries do not receive extra country-selection weight simply because they have more provinces.
5. Eligible destinations are existing countries owning at least one settled, owned land province that passes the island restriction and contains no other adventurer. Exclude sea, wasteland, uncolonized land, and the current country.
6. Preserve the agreed exceptions for **the principal landmasses of Nippon and Ulthuan**. Small offshore islands remain excluded. This needs an explicit map eligibility definition rather than assuming a generic island check will match the design.
7. If there are two or more neighbors but none has an eligible destination, use the worldwide fallback as well. This is an additional safeguard against blocked movement, not a change to the zero/one-neighbor rule.
8. Check that a destination can be found before presenting an encounter. Revalidate on resolution if ownership or eligibility has changed. If no other country anywhere has an eligible province, defer the encounter or, for an already-open encounter, retain the unique adventurer for the next eligible pulse. Never delete or duplicate the character.
9. Transfer the identical modifier to the chosen destination and update the saved global location, with no arrival cooldown. Departure remains guaranteed for every normal event resolution with a valid destination, including hostile responses.
10. **Bugman prefers beer:** after choosing the destination country, select among its eligible beer provinces if any exist. Otherwise choose any eligible province there. An island or a province occupied by another adventurer is not eligible, even if it produces beer. This preference never changes which country is selected.
11. After a successful transfer, send the destination province's owner a triggered-only arrival notice: “[Name] has arrived in [Province]” (using “have” for pairs), followed by a brief introduction. These 18 notices use each character's `.21` event, with one effect-free acknowledgement. They are excluded from the random pulse and do not fire on initial placement or failed movement.

Worldwide travel can be explained as an unobserved sea voyage, a caravan journey, clandestine passage, or a supernatural disappearance appropriate to the character. Do not claim that every character teleports. The ruler only knows that the adventurer has escaped or departed; the departure tooltip names the selected country without listing the travel-selection rules.

## 3. Localization and ruler perspective

The player is the ruler **learning about an incident**, not the adventurer performing it. Each description should establish the source of the report, what has already happened, the consequences for the province, and the decision now facing the government.

- Use watch captains, guild petitions, survivors, scouts, intercepted correspondence, temple attendants, and frightened officials as narrators or sources.
- At the first mention in every encounter and arrival description, identify the adventurer by name and an appropriate role, such as a wandering wizard, Dwarf ranger, or High Elf prince. Introduce both members of a pair and briefly identify any other adventurer mentioned; do not assume prior lore knowledge or that the player saw an arrival notice.
- Describe a specific incident with concrete details. Avoid generic openings such as “an adventurer offers to help us.”
- Separate established facts from rumour. An anonymous assassin's responsibility may be suspected even when the player-facing title identifies the character.
- Show the adventurer acting independently: witnesses saw them escape, officials cannot locate them, or they have gone into ruins beyond the authorities' reach.
- Give the ruler 2–4 responses, varying the number across the batch: support a follow-up, compensate victims, exploit findings, investigate, retaliate, contain damage, or ignore the affair.
- An “ignore” option does not erase damage that has already happened. Options determine how the aftermath is handled.
- An order to arrest or pursue the adventurer must not remove them permanently from this system. It can recover goods, disperse followers, or contain damage, but the adventurer ultimately escapes.
- Final encounter descriptions contain **6–10 sentences in 2–3 paragraphs**, each containing 2–4 sentences. The table entries below remain the design seeds; the finished reports are in `localisation/war_adventurers_l_english.yml` and their editable source is `Adventurers/event_data.json`.

### Example: Gotrek and Felix in the catacombs

> Your watch captain reports that a Dwarf calling himself Gotrek and his human companion broke through a cellar wall beneath the merchants' quarter. By dawn, three warehouses had collapsed, several missing townsfolk had returned, and witnesses were insisting that armed rat-men had fled into the drains.
>
> The pair escaped the watch and were last seen entering the old catacombs. Your captain requests instructions: should his men assist their search, seal the entrances, or leave these troublesome strangers to their work?

Possible responses: send support and recover what lies below; seal the entrances and compensate affected households; allow the strangers to continue while the watch protects the streets. Each resolution includes their eventual departure. This is an invented mod incident, not a quotation or a claim about a specific published adventure.

## 4. Starting locations, home territories, and fixed modifiers

Fame is a subjective 1–5 estimate of fan recognition, not personal power. Starts abroad are proposed mod assignments, not documented locations in 2502. Province owners were checked against the current mod history files.

**Unrest sign:** the agreed drawback is **+2 local unrest**. In EU4, −2 local unrest would be a benefit. Each entry has its character benefit, a shared +10% province trade-power bonus for trade-map visibility, and this small disruptive presence penalty; none changes with the host's relationship. Modifier names use “[Name], Adventurer”, with “Gotrek and Felix, Adventurers” for the pair. Each has a personalized description, and all share the same sword icon.

| Adventurer | Fame | Starting region | Starting nation and province | Province modifier: benefits and drawback | Home territory |
|---|:---:|---|---|---|---|
| **Balthasar Gelt** | 5 | Grand Cathay | **Iron Court — I22**, Shang-Yang **2972** | **Balthasar Gelt, Adventurer:** +5% local production efficiency; +10% local trade power; **+2 local unrest** | The Empire, including Westerland |
| **Teclis** | 5 | Ind | **Goa — I64**, Goa **4182** | **Teclis, Adventurer:** +5% local institution spread; +10% local trade power; **+2 local unrest** | Ulthuan |
| **Deathmaster Snikch** | 4 | Nippon | **Hojizu — Z75**, province **4776** | **Deathmaster Snikch, Adventurer:** +5% local defensiveness; +10% local trade power; **+2 local unrest** | Skavenblight/Under-Empire, Cathay and Nippon |
| **Josef Bugman** | 4 | Mountains of Mourn | **Goldtooth — I01**, Mistveil **2795** | **Josef Bugman, Adventurer:** +5% local production efficiency; +10% local trade power; **+2 local unrest** | The Empire and western Dwarf mountain ranges |
| **Bardin Goreksson** | 4 | Darklands | **Darkhold — B23**, Shadowmount **4258** | **Bardin Goreksson, Adventurer:** +5% local defensiveness; +10% local trade power; **+2 local unrest** | Grey Mountains, World's Edge Mountains and the Empire |
| **Harald Hammerstorm** | 3 | Great Eastern Steppes | **Puppets of Misrule — B77**, Shadowrealm **2644** | **Harald Hammerstorm, Adventurer:** +5% local manpower; +10% local trade power; **+2 local unrest** | Norsca, northern Chaos Wastes and Great Eastern Steppes |
| **Abhorash** | 4 | Nehekhara | **Numas — Z09**, province **851** | **Abhorash, Adventurer:** +5% local defensiveness; +10% local trade power; **+2 local unrest** | Nehekhara |
| **Elspeth von Draken** | 4 | Borderlands | **Akendorf — A67**, province **872** | **Elspeth von Draken, Adventurer:** +5% local defensiveness; +10% local trade power; **+2 local unrest** | The Empire |
| **Markus Wulfhart** | 4 | Araby | **Copher — Z16**, province **988** | **Markus Wulfhart, Adventurer:** +5% local manpower; +10% local trade power; **+2 local unrest** | The Empire |
| **Gotrek & Felix** | 5 | The Empire | **Reikland — A01**, East Altdorf **1** | **Gotrek and Felix, Adventurers:** +5% local defensiveness; +10% local trade power; **+2 local unrest** | The Empire and western Dwarf mountain ranges |
| **Repanse de Lyonesse** | 4 | Bretonnia | **Lyonesse — A17**, Merton **284** | **Repanse de Lyonesse, Adventurer:** +5% local manpower; +10% local trade power; **+2 local unrest** | Bretonnia |
| **Sienna Fuegonasus** | 4 | Estalia/Tilea | **Magritta — A41**, province **553** | **Sienna Fuegonasus, Adventurer:** +5% local production efficiency; +10% local trade power; **+2 local unrest** | Estalia and the Empire |
| **Malakai Makaisson** | 4 | Northern Old World | **Kislev — A29**, Erengrad **332** | **Malakai Makaisson, Adventurer:** +5% local defensiveness; +10% local trade power; **+2 local unrest** | Western Dwarf mountain ranges |
| **Tyrion** | 5 | Ulthuan | **Avelorn — H08**, Phoenix Gate **1829** | **Tyrion, Adventurer:** +5% local manpower; +10% local trade power; **+2 local unrest** | Ulthuan |
| **Gor-Rok** | 4 | Lustria | **Itza — V03**, province **2466** | **Gor-Rok, Adventurer:** +5% local defensiveness; +10% local trade power; **+2 local unrest** | Lustria |
| **Nakai the Wanderer** | 4 | Naggaroth | **S'sildra Tor — H20**, Fellwrath **2348** | **Nakai the Wanderer, Adventurer:** +5% local defensiveness; +10% local trade power; **+2 local unrest** | Lustria |
| **Thanquol & Boneripper** | 4 | Skavenblight | **Grey Seer Clan — U25**, Central Skavenblight **4600** | **Thanquol and Boneripper, Adventurer:** +10% local trade power; **+2 local unrest** | Skavenblight and the Under-Empire |
| **Grombrindal** | 4 | World's Edge Mountains | **Clan Angrund — U37**, Kvinn Wyr **4410** | **Grombrindal, Adventurer:** +5% local defensiveness; +10% local trade power; **+2 local unrest** | Western Dwarf mountain ranges, including the World's Edge Mountains |

“Western Dwarf mountain ranges” is implemented as `western_mountains_superregion` (Grey, Black and Vaults), plus `world_edge_mountains_region`, `southern_world_edge_mountains_region`, and `karak_eight_peaks_region`. The named Dragonback Mountains province (699) is impassable and cannot host an adventurer. The Mountains of Mourn, Darklands and Norscan Giant-Home Mountains are excluded. The Under-Empire uses `skavenblight_superregion` plus the explicit Skavenblight and Skavenblight Tunnels areas. Home membership is fixed geography and never changes with the owner's race.

Bardin's home range includes the Grey Mountains to cover Karak Norn, where he served as an Ironbreaker. Snikch's expanded home range is a gameplay definition of familiar operating territory, not a claim that he was born in each of those regions.

The fixed benefits can represent indirect consequences in enemy territory: tighter security after Snikch's arrival, hurried fortification work prompted by Nakai, or recruitment in response to Tyrion. They do not imply that the adventurer willingly serves the owner. The modifier belongs to the province and automatically affects its current owner.

The passive magnitudes are **+10% province trade power, the existing +5% character benefit where different, and +2 local unrest**. Thanquol’s original +5% trade power becomes +10%; it is not duplicated or increased to +15%. Jeff's guide does not directly price these province-only equivalents; no unsupported Weighing Value is assigned to them. The modifier keys and province scopes have been checked. No national army tradition, prestige, or innovativeness modifier is introduced by the presence itself.


## 5. Enemy classification using Alignment and Racial Administration

Use the current owner's existing country modifiers, not its primary culture, state religion, military administration, tag, or diplomatic war status. The identifiers below document existing mod data; they are not new scripted triggers.

| Displayed alignment | Existing country modifier |
|---|---|
| Good | `order_nation` |
| Neutral | `neutral_nation` |
| Evil | `destruction_nation` |
| Chaos | `chaos_nation` |

| Racial Administration used in these rules | Existing country modifier |
|---|---|
| Orcish / Greenskin | `orcish_administration` |
| Skaven | `skaven_administration` |
| Undead | `undead_administration` |
| Elven | `elven_administration` |
| Dwarven | `dwarven_administration` |
| Beastfolk | `beastfolk_administration` |
| Lizardmen | `lizardmen_administration` |
| Ogre | `ogre_administration` |

High, Wood, and Dark Elves share Elven Administration; ordinary and Chaos Dwarfs share Dwarven Administration. Their alignment supplies the distinction where needed. Undead Administration may coexist with another administration and must be checked independently. Beastfolk Administration is broad enough to include eastern Beastfolk: do not automatically equate it with Chaos Beastmen.

### Enemy profiles

| Profile | Enemy if any of these conditions is satisfied | Friendly/neutral otherwise |
|---|---|---|
| **A — Opposed to corrupt or predatory rule** | **Chaos alignment OR Evil alignment OR Orcish Administration OR Skaven Administration OR Undead Administration** | Good/Neutral states outside the listed administration exceptions. In particular, neutral Ogres, neutral Beastfolk and neutral Lizardmen are not automatic enemies. |
| **B — Skaven opportunist** | **Does not have Skaven Administration** | Skaven-administered states. Intraclan scheming remains possible inside the friendly/neutral pool, without a separate war-status check. |
| **C — Harald's enemies** | **Good alignment OR Undead Administration** | Neutral, Evil and Chaos states without Undead Administration. His hatred of the undead overrides shared alignment. |
| **D — Abhorash's martial code** | **Chaos alignment OR Orcish Administration OR Skaven Administration OR (Evil alignment AND no Undead Administration)** | Other states, including ordinary Neutral Tomb Kings and independent undead courts. Undeath is neither a friendship guarantee nor automatic hostility. |

Profile D deliberately cannot distinguish a Nagash loyalist from another undead ruler with the same Alignment and Administration. That earlier religion-specific exception is removed, rather than hidden inside a new religion or tag check. The previous Eshin/Grey Seer war exceptions and High Elf–Dwarf war exception are also removed. Likewise, neutral Dragon Isles Lizardmen receive neutral encounters without being described as loyal servants of the Old Ones.

These are gameplay classifications, not assertions about every individual's canonical relationships. Evil-aligned humans can be enemies of the heroic adventurers; Good/Neutral Elven or Dwarven states are not condemned merely for sharing an administration type with hostile branches of their race. If several alignment markers are present, any satisfied enemy condition wins. Missing alignment does not create hostility by itself; an administration condition can still do so.

## 6. Encounter report summary

Each cell is a specific **proposed mod incident reported to the ruler**. These are not published lore claims. Home and abroad versions should differ in substance, not merely in the place-name. Friendly/neutral versions target +1/+2 Weighing Value; enemy versions target −1/−2.

| Adventurer | Enemy definition | Friendly/neutral reports: home / abroad | Enemy reports: home / abroad |
|---|---|---|---|
| **Gelt** | **A:** Chaos/Evil alignment, or Orcish/Skaven/Undead Administration | **Home:** A guild reports that his demonstration improved its metalworking, but damaged the workshop. **Abroad:** A merchant discovers that Gelt's payment has reverted to lead; the wizard has left valuable research behind. | **Home:** An arsenal reports that its ammunition has become useless metal. **Abroad:** Foundry workers describe a masked intruder and a ruined military commission. |
| **Teclis** | **A:** Chaos/Evil alignment, or Orcish/Skaven/Undead Administration | **Home:** Wardens report a repaired waystone and an apprentice Teclis has taken under his instruction. **Abroad:** Priests complain that a foreign mage has begun teaching a gifted local child. | **Home:** An occupying garrison discovers that its protective wards have failed. **Abroad:** Treasury officials report a missing relic and a written warning against pursuing it. |
| **Snikch** | **B:** No Skaven Administration | **Home:** A rival official is found dead, with evidence of his conspiracy neatly displayed. **Abroad:** An anonymous delivery contains stolen plans and instructions for payment. | **Home:** Tunnel sentries disappear before an important depot is emptied. **Abroad:** A commander is discovered dead inside a locked room; the guards insist nobody entered. |
| **Bugman** | **A:** Chaos/Evil alignment, or Orcish/Skaven/Undead Administration | **Home:** Brewers report that Bugman recovered stolen equipment and commandeered their premises. **Abroad:** A caravan returns with rescued cargo and an enormous bill for the rangers' hospitality. | **Home:** Prison guards report escaped Dwarfs and burning supply stores. **Abroad:** A convoy is found stripped of provisions, its escorts defeated and its ale missing. |
| **Bardin** | **A:** Chaos/Evil alignment, or Orcish/Skaven/Undead Administration | **Home:** Engineers learn that Bardin has reopened a forgotten passage beneath their hold. **Abroad:** An expedition returns with ancient tools, a partial map, and a request for further funding. | **Home:** Officials discover that captives escaped through an unrecorded tunnel. **Abroad:** A mine overseer reports sabotaged machinery and missing slaves. |
| **Harald** | **C:** Good alignment or Undead Administration | **Home:** Warriors return carrying trophies from a barrow Harald has cleared. **Abroad:** Villagers report that a haunted fortress is silent, but its terrifying conqueror remains nearby. | **Home:** An occupying commander reports defeated champions and growing local resistance. **Abroad:** Survivors describe a hammer-wielding warrior destroying their garrison. |
| **Abhorash** | **D:** Chaos alignment, Orcish/Skaven Administration, or Evil without Undead Administration | **Home:** Petitioners report that a mysterious swordsman killed a dangerous creature and refused payment. **Abroad:** A knight returns from a duel with exceptional instruction and refuses to identify his teacher. | **Home:** A fortress commander reports dead guards and released prisoners. **Abroad:** Witnesses confirm that the realm's celebrated champion lost a public duel to a stranger. |
| **Elspeth** | **A:** Chaos/Evil alignment, or Orcish/Skaven/Undead Administration | **Home:** Cemetery officials report that she exposed a corpse-theft ring without consulting them. **Abroad:** A sealed tomb has been opened, its curse broken, and its custodians frightened into silence. | **Home:** A necromancer reports that soldiers under his control collapsed when she passed. **Abroad:** Survivors describe a deathly mist moving through a military workshop. |
| **Wulfhart** | **A:** Chaos/Evil alignment, or Orcish/Skaven/Undead Administration | **Home:** Villagers deliver a monster's head and ask that the hunters' expenses be paid. **Abroad:** Officials receive an unfamiliar beast's carcass and competing claims over its valuable remains. | **Home:** A patrol is found ambushed on a supposedly secure forest road. **Abroad:** Beast-handlers report their prized military creatures slain and their hunter gone. |
| **Gotrek & Felix** | **A:** Chaos/Evil alignment, or Orcish/Skaven/Undead Administration | **Home:** The watch reports collapsed warehouses, rescued townsfolk and the pair's flight into the catacombs. **Abroad:** Survivors arrive from a ruined stronghold carrying treasure and Felix's account of their rescue. | **Home:** A slave convoy is destroyed and its prisoners armed. **Abroad:** The garrison's monstrous champion is dead, while copies of Felix's mocking account circulate in taverns. |
| **Repanse** | **A:** Chaos/Evil alignment, or Orcish/Skaven/Undead Administration | **Home:** Officials report that peasants rallied behind her after she exposed a corrupted household. **Abroad:** Rescued captives arrive bearing her request for sanctuary and provisions. | **Home:** An occupying governor reports villagers sheltering her followers. **Abroad:** A shrine or slave camp has been destroyed, and survivors carry her demand that the abuses cease. |
| **Sienna** | **A:** Chaos/Evil alignment, or Orcish/Skaven/Undead Administration | **Home:** The watch reports rescued captives, a destroyed cult hideout and several neighbouring buildings ablaze. **Abroad:** A foundry reports extraordinary output, while its workers complain about uncontrolled magical heat. | **Home:** Quartermasters discover that plague-tainted supplies have been burned. **Abroad:** An attempted arrest ends with a burning arsenal and contradictory witness accounts. |
| **Malakai** | **A:** Chaos/Evil alignment, or Orcish/Skaven/Undead Administration | **Home:** Engineers report that his weapon worked brilliantly before demolishing its own testing platform. **Abroad:** Harbour officials report an extraordinary airship landing and its inventor requisitioning a workshop. | **Home:** A siege commander reports a battery destroyed by an unfamiliar machine. **Abroad:** Depot survivors describe an attack from the sky and demand new defences. |
| **Tyrion** | **A:** Chaos/Evil alignment, or Orcish/Skaven/Undead Administration | **Home:** Wardens report that he defeated raiders near a sacred grove and praised local volunteers. **Abroad:** Rescued captives arrive alongside soldiers he has personally instructed. | **Home:** An occupying commander is defeated and a confiscated heirloom disappears. **Abroad:** Officials report a breached prison compound and elite guards beaten by an Elven stranger. |
| **Gor-Rok** | **A:** Chaos/Evil alignment, or Orcish/Skaven/Undead Administration | **Home:** Temple attendants report that he held an approach long enough to recover sacred objects. **Abroad:** Local officials report that a white Saurus defended ancient ruins inside their settlement. | **Home:** An occupying garrison reports its strongpoint demolished. **Abroad:** Quarry workers flee after he destroys their equipment around an ancient site. |
| **Nakai** | **A:** Chaos/Evil alignment, or Orcish/Skaven/Undead Administration | **Home:** Messengers report that an enormous Kroxigor held a river crossing until help arrived. **Abroad:** Villagers report a slain monster and a silent giant waiting beside a damaged shrine. | **Home:** Survivors report an invasion column broken before reaching its objective. **Abroad:** A camp is demolished and sacred objects carried away; scouts refuse to follow the tracks. |
| **Thanquol & Boneripper** | **B:** No Skaven Administration | **Home:** Thanquol sends an extravagant account of a rival's exposed plot and demands credit. **Abroad:** Customs officials discover profitable stolen cargo accompanied by dangerously unstable warpstone. | **Home:** A tunnel assault releases a horror that attacks everyone nearby. **Abroad:** Officials report poisoned stores, a rampaging Rat Ogre and a Grey Seer seen fleeing the catastrophe. |
| **Grombrindal** | **A:** Chaos/Evil alignment, or Orcish/Skaven/Undead Administration | **Home:** Exhausted defenders report that a white-bearded stranger rallied them and vanished after victory. **Abroad:** Caravan survivors arrive with news of their rescue and an ancient agreement the stranger demanded be honoured. | **Home:** An occupying force loses captives and ancestral treasures in a sudden counterattack. **Abroad:** Survivors report a destroyed slaving expedition or a slain oathbreaker, accompanied by a formal statement of the grudge. |

Supporting conditions must fit the incident: a corpse-theft report needs an appropriate settlement, a necromantic-garrison report needs an undead host, and a slave-camp story needs a plausible setting. Those conditions select the story within an existing category; they do not replace Alignment/Administration as the enemy test. Use alternate wording or another incident when an asset or institution is absent.

## 7. Event balance reference

Use Jeff's Balance Guide as the source of truth. Each option must remain within ±1 of its intended event Weighing Value, and the eventual script must comment the option's total. Prefer direct effects; use timed country modifiers in roughly half or fewer of the options. The four seeds per adventurer above summarize the categories; section 10 expands each category to five distinct concepts, for 20 per adventurer.

| Direct outcome | Weighing Value |
|---|---:|
| +1 province development in one category | +0.5 |
| +50 of one monarch power | +1 |
| +1 innovativeness | +1 |
| +2 percentage points army professionalism | +1 |
| +25 prestige through the guide's prestige-or-power effect | +1 |
| Half a year's income | +1 |
| +25 province devastation | −1 |
| Size-1 rebel uprising using a suitable rebel type | −2 |

A +1 encounter could grant +1 production development and +25 administrative power. A −1 sabotage encounter could offer accepting 25 devastation or spending half a year's income to prevent that damage; the latter uses the guide's proportional sign reversal. These are example budgets, not implemented effects.

## 8. Actual lore exploits of the chosen adventurers

The bullets below summarize published exploits and established character history. They are separate from the invented encounter table. Online references are linked beside the relevant claims; where those references index books or army books, those underlying works are named where useful. No fan-mod event text is treated as canonical evidence.

Chronology is not perfectly consistent between editions and adaptations. **Later** means a feat must not be described as completed at the 2502 start. **Undated** means the consulted account does not establish a safe pre-2502 date. **Legend** preserves an in-world attribution rather than certifying every detail. Use later exploits as inspiration for new events, not as automatic start-date history.

### 1. Balthasar Gelt

- **Undated:** Paid for passage to Altdorf using gold transmuted from lead, then escaped before it reverted. The cheated captain put a bounty on him. [Gelt: history](https://whfb.lexicanum.com/wiki/Balthasar_Gelt).
- **Undated:** Combined alchemy with black-powder research, winning respect from the College of Engineers. He survived a laboratory explosion and subsequently concealed himself behind his familiar golden mask. [Gelt: research and accident](https://whfb.lexicanum.com/wiki/Balthasar_Gelt).
- **Later, 2516:** Prevented an impending conflict involving Nordland by turning the money intended for Theoderic Gausser's troops into lead, then escaping on his Pegasus. This is an especially close foundation for military-payroll sabotage. [Gelt: Salzenmund incident](https://whfb.lexicanum.com/wiki/Balthasar_Gelt).

Do not assume his later Supreme Patriarch title or End Times accomplishments at game start.

### 2. Teclis

- **Before 2502:** Defeated Malekith in a magical confrontation at the Battle of Finuval Plain. [Teclis: magical achievements](https://whfb.lexicanum.com/mediawiki/index.php?mobileaction=toggle_view_desktop&redirect=no&title=Teclis).
- **Before 2502:** Helped Magnus the Pious against Chaos and established the Imperial Colleges of Magic at Magnus's request, giving human magical practice an enduring institutional foundation. [Magnus and the Colleges](https://warhammerfantasy.fandom.com/wiki/Magnus_the_Pious).
- **Later adventures:** Accompanied Gotrek and Felix on their Albion adventure against Chaos forces and other threats in *Giantslayer*. [Gotrek and Felix chronology](https://whfb.lexicanum.com/wiki/Gotrek_%26_Felix).

### 3. Deathmaster Snikch

- **Undated:** Murdered the Grail Knight Boragild of L'Anguille while the knight prayed. [Snikch: victims](https://whfb.lexicanum.com/mediawiki/index.php?mobileaction=toggle_view_mobile&title=Snikch).
- **Undated:** Terrorized Karaz-a-Karak through a winter of killings and escaped even after the Dwarfs sealed the hold. [Snikch: infiltration](https://whfb.lexicanum.com/mediawiki/index.php?mobileaction=toggle_view_mobile&title=Snikch).
- **Attributed, not certain:** The death of Celestial Wizard Heinrich Frisen in his locked observatory is associated with Snikch. This supports an uncertain official report rather than an omniscient account of the assassin's movements. [Snikch: attributed murders](https://whfb.lexicanum.com/mediawiki/index.php?mobileaction=toggle_view_mobile&title=Snikch).
- **Later, End Times:** Assassinated Thorgrim Grudgebearer and helped enable the final infiltration of Karaz-a-Karak. Do not reproduce this named ruler's death as an ordinary random event. [Snikch: End Times](https://whfb.lexicanum.com/mediawiki/index.php?mobileaction=toggle_view_mobile&title=Snikch).

### 4. Josef Bugman

- **Undated:** Expanded his father's brewery into a prosperous Dwarf settlement and made celebrated ales, including Bugman's XXXXXX and Troll Brew. [Bugman: brewing career](https://whfb.lexicanum.com/wiki/Josef_Bugman).
- **Undated:** Returned from an Imperial delivery to find his brewery destroyed by Goblins. He and the survivors became rangers, pursuing vengeance and hoping to recover missing kin. [Bugman: destruction of the brewery](https://whfb.lexicanum.com/wiki/Josef_Bugman).
- **Undated:** His rangers followed the Goblins beyond the World's Edge Mountains, ambushed their camps, and emerged from the wilderness to help Dwarf armies. [Bugman: ranger exploits](https://whfb.lexicanum.com/wiki/Josef_Bugman).

The selected travelling-ranger version assumes the brewery's destruction has already occurred in the mod's 2502 world-state. The start in the Mountains of Mourn is our placement, not a documented Bugman itinerary.

### 5. Bardin Goreksson

- **Career background:** Served as an Ironbreaker at Karak Norn before becoming a ranger and undertaking his search for lost Karak Zorn. The search is an actual quest, not a successful discovery. [Fatshark: Bardin's background](https://www.vermintide.com/news/2018/12/6/dev-blog-bardin-goreksson).
- **Later, Vermintide era:** Fought through Ubersreik's Skaven disaster with his companions, developing the skills of a veteran ranger and helping defend the Reikland. These exploits are collective, not solo victories. [Fatshark: Bardin and Ubersreik](https://www.vermintide.com/news/2018/12/6/dev-blog-bardin-goreksson).
- **Later, optional career development:** Put his engineering knowledge into practice as an Outcast Engineer, using experimental machinery including his custom Steam-Assisted Crank Gun. This does not mean all his alternative game careers are simultaneous history. [Fatshark: Outcast Engineer](https://www.vermintide.com/news/outcast-engineer-available-now).

### 6. Harald Hammerstorm

- **Undated:** Slew the daemon Mathrag Brainmangler at the Battle of Khorsvold with a blow from his hammer. [Harald: early renown](https://whfb.lexicanum.com/wiki/Harald_Hammerstorm).
- **Undated:** His warriors awakened the dead while exploring Vorshgar. After fighting their way out, Harald turned to face the pursuing undead and fought through a day and night until they were destroyed. [Harald: Vorshgar](https://whfb.lexicanum.com/wiki/Harald_Hammerstorm).
- **Established reputation:** Became a particular terror to the undead, whose supernatural fearlessness fails before him; his hammer can banish their spirits. [Harald: the undead's nemesis](https://whfb.lexicanum.com/wiki/Harald_Hammerstorm).

### 7. Abhorash

- **Ancient history:** Defended Lahmia against the coalition of Priest Kings, killing large numbers of attackers but ultimately failing to save the city. [Abhorash: fall of Lahmia](https://whfb.lexicanum.com/mediawiki/index.php?mobileaction=toggle_view_mobile&title=Abhorash).
- **Ancient history:** Defended Bel Aliad against Neferata's assault, defeated her, and refused to surrender her to W'soran. His relationships with other vampires are more complicated than simple faction loyalty. [Abhorash: Bel Aliad](https://whfb.lexicanum.com/mediawiki/index.php?mobileaction=toggle_view_mobile&title=Abhorash).
- **Before 2502:** Killed a dragon and drank its blood, overcoming his dependence on ordinary blood and providing the model for the Blood Dragons' pursuit of martial perfection. [Blood Dragons: Abhorash's achievement](https://whfb.lexicanum.com/wiki/Blood_Dragons).

### 8. Elspeth von Draken

- **Undated:** Travelled widely collecting and studying arcane artefacts, maintaining towers near Nuln's Gardens of Morr and in the Grey Mountains. [Elspeth: independent investigations](https://whfb.lexicanum.com/wiki/Elspeth_von_Draken).
- **Undated:** Dealt with the Mire Hulk Rawbones and the vampire Vashara of Lahmia; also repelled witch hunters attempting to penetrate her own secrets. [Elspeth: enemies and intruders](https://whfb.lexicanum.com/wiki/Elspeth_von_Draken).
- **Later, Tamurkhan campaign:** Defended Nuln, defeated Orhbal Vipergut and his dragon, and used the talisman she had given Theodore Bruckner to destroy Tamurkhan when he attempted to take Bruckner's body. This was a costly trap, not a straightforward personal duel. [Elspeth: Battle of Nuln](https://whfb.lexicanum.com/wiki/Elspeth_von_Draken).

### 9. Markus Wulfhart

- **Undated:** Hunted the Drakwald Cyclops after it destroyed his home, blinded it with an arrow, and finished it with his sword. [Wulfhart: the Cyclops](https://whfb-de.lexicanum.com/wiki/Markus_Wulfhart).
- **Undated:** His monster-hunting career earned Imperial recognition and command of an elite body of scouts; he continued pursuing creatures preying on the Empire's settlements. [Wulfhart: Huntsmarshal](https://warhammerfantasy.fandom.com/wiki/Markus_Wulfhart).
- **Local mod history, 2501:** The Beasts of Telldros enclave account places Wulfhart hunting its monstrous warband in Norsca without subduing it. This is a Dragon Ogre-led pack, not simply a Beastmen tribe. Treat the hunt as the mod's established prior exploit, not as independently verified tabletop chronology. See the local source note in section 9.

### 10. Gotrek Gurnisson and Felix Jaeger

- **Around the start:** Gotrek saved Felix during the Altdorf Window Tax riots; Felix swore to accompany him and record his doom. [Gotrek and Felix: origin of the partnership](https://whfb.lexicanum.com/wiki/Gotrek_%26_Felix).
- **Chronology varies by source:** They thwarted Thanquol's plans against Nuln in *Skavenslayer*. The accounts consulted disagree on the Imperial year, so do not assume its completion at the start. [Partnership chronology](https://whfb.lexicanum.com/wiki/Gotrek_%26_Felix), [Thanquol chronology](https://whfb.lexicanum.com/wiki/Thanquol).
- **Later adventures:** Travelled aboard the *Spirit of Grungni* to Karak Dum, fought a Bloodthirster, slew a dragon, and survived the siege of Praag. [Gotrek and Felix: major adventures](https://whfb.lexicanum.com/wiki/Gotrek_%26_Felix).

Felix is a participant and chronicler, not merely Gotrek's attendant. Reports should occasionally foreground his testimony, rescue efforts, or diplomatic trouble.

### 11. Repanse de Lyonesse

- **2007 IC:** Following a vision of the Lady, took a fallen knight's armour and a chapel sword and banner, then rallied the defeated knights of Lyonesse. [Repanse: her calling](https://whfb.lexicanum.com/wiki/Repanse_de_Lyonesse).
- **2007 IC:** Led the relief of Couronne, broke the besieging Chaos army, and personally beheaded its commander. [Repanse: relief of Couronne](https://whfb.lexicanum.com/wiki/Repanse_de_Lyonesse).
- **After the victory:** Received knighthood and the Dukedom of Lyonesse from Louis the Young. Her original story therefore does include territorial rulership. [Repanse: reward](https://whfb.lexicanum.com/wiki/Repanse_de_Lyonesse).

**Agreed mod adaptation:** she survives to 2502 through the Lady's grace and now travels without exercising ducal authority. This is an explicit adaptation, not an established conclusion of the original account. Her current placement is Merton on the Bretonnian mainland, within Lyonesse.

### 12. Sienna Fuegonasus

- **Career background:** Studied in the Bright College under Thyrus Gormann, then left rather than accept its discipline. Her struggle to control Aqshy is central to her story. [Fatshark: Sienna's background](https://www.vermintide.com/news/2018/12/6/dev-blog-sienna-fuegonasus).
- **Later, Vermintide era:** Began her association with the other heroes as a prisoner, then helped them survive Ubersreik and fight the Reikland's invaders through her fire magic. [Fatshark: Sienna and Ubersreik](https://www.vermintide.com/news/2018/12/6/dev-blog-sienna-fuegonasus).
- **Later, optional career development:** Her confrontation with her twin Sofia leads into the Necromancer career. That later development is not the version used by this mod proposal: retain wandering Bright Wizard Sienna. [Fatshark: Necromancer release](https://www.vermintide.com/news/patch-5-1-0-necromancer).

### 13. Malakai Makaisson

- **Career background:** Built the ill-fated *Unsinkable* ironclad and *Undestructible* airship (rendered *Indestructible* in the linked Total War introduction). Their disasters led to disgrace and his Slayer oath; failed inventions are genuine foundations for his event themes. [Creative Assembly: Malakai's engineering disasters](https://community.creative-assembly.com/total-war/total-war-warhammer/blogs/15-thrones-of-decay-introducing-malakai-makaisson).
- **Later novel adventure:** Built and piloted the more successful *Spirit of Grungni*, transporting the expedition seeking Karak Dum in *Daemonslayer*. [Spirit of Grungni: history](https://warhammerfantasy.fandom.com/wiki/Spirit_of_Grungni).
- **Undated relative to start:** Created the Goblin-hewer, an axe-hurling war machine. [Creative Assembly: Malakai's inventions](https://community.creative-assembly.com/total-war/total-war-warhammer/blogs/15-thrones-of-decay-introducing-malakai-makaisson).

Use prototypes or other experiments for early encounters rather than assuming every later invention already exists in 2502.

### 14. Tyrion

- **Before 2502:** Banished N'Kari at the Phoenix Shrine, establishing his reputation as a defender of Aenarion's line. [Tyrion: renowned victories](https://warhammerfantasy.fandom.com/wiki/Tyrion).
- **Before 2502:** Slew Urian Poisonblade at the Battle of Finuval Plain, one of his defining feats against the Dark Elves. [Tyrion: Finuval Plain](https://warhammerfantasy.fandom.com/wiki/Tyrion).
- **Undated:** Routed Kritsqueel's Skaven force with only his steed Malhandir accompanying him. [Tyrion: Kritsqueel's defeat](https://warhammerfantasy.fandom.com/wiki/Tyrion).

Do not import his later Sword of Khaine/End Times transformation into ordinary 2502 encounters.

### 15. Gor-Rok

- **Undated relative to start:** Helped recover the Star Stela of Quetli from Dark Elf raiders under Tepec-Inzi's command. He smashed their commander's chariot and killed him despite being impaled, only having the weapon removed after the relic was secured. [Gor-Rok: recovery of the Star Stela](https://whfb.lexicanum.com/mediawiki/index.php?mobileaction=toggle_view_desktop&title=Gor-Rok).
- **Undated:** Slew both a Savage Orc warboss and its Wyvern at the Battle of Bloodpools. [Gor-Rok: Bloodpools](https://whfb.lexicanum.com/mediawiki/index.php?mobileaction=toggle_view_desktop&title=Gor-Rok).
- **Undated:** Survived Ogre charges and blows from Greater Daemons, and campaigned as far as the Chaos Wastes. These feats support extraordinary endurance without inventing a new named victory. [Gor-Rok: campaigns](https://whfb.lexicanum.com/mediawiki/index.php?mobileaction=toggle_view_desktop&title=Gor-Rok).

### 16. Nakai the Wanderer

- **Ancient history:** Held the Bridge of Stars at Itza against daemons during the Great Catastrophe, killing so many that the site retained a terrible reputation among them. [Nakai: defence of Itza](https://whfb.lexicanum.com/wiki/Nakai).
- **Established pattern:** Reappears when Lizardmen face great danger, then resumes his wandering rather than governing a settled realm. This makes his unexplained arrivals and departures intrinsic to his character. [Nakai: the Wanderer](https://warhammerfantasy.fandom.com/wiki/Nakai).
- **Later, Albion campaign:** Accompanied Mazdamundi to Albion and helped establish Konquata. Do not treat that later overseas expedition as already completed in the 2502 opening. [Nakai: Albion and Konquata](https://whfb-de.lexicanum.com/wiki/Nakai).

The Naggaroth shrine investigation in the event table is our invented assignment, not a documented Nakai exploit.

### 17. Thanquol and Boneripper

- **Novel chronology varies:** Thanquol led the failed Skaven attack on Nuln, using plague, engineered vermin and factional intrigue. He reached the palace but failed to kill Countess Emmanuelle and escaped. [Thanquol: Nuln](https://whfb.lexicanum.com/wiki/Thanquol).
- **Later novel sequence:** Attacked the engineering camp at the Lonely Tower to obtain Dwarf technology, then pursued the *Spirit of Grungni* into Kislev and tried to capture it. These were dangerous attempts, not successful conquests. [Thanquol: airship plots](https://whfb.lexicanum.com/wiki/Thanquol).
- **Pair identity:** Boneripper is the name attached to successive Rat Ogre bodyguards, not one unchanging companion surviving every catastrophe. The travelling pair can persist even when a particular bodyguard is replaced. [Thanquol and Boneripper: successive bodyguards](https://whfb.lexicanum.com/wiki/Thanquol_and_Boneripper_%28anthology%29).

His boastful accounts and self-serving explanations should differ sharply from reports by the officials investigating his schemes.

### 18. Grombrindal

- **Dwarf saga:** Appeared when Umthi the Damned and his companions were surrounded by Goblins. His attack inspired the exhausted Dwarfs to fight through to him; after their victory, he had vanished. [Grombrindal: Umthi's rescue](https://whfb.lexicanum.com/wiki/Grombrindal).
- **Reported exploit:** Joined Gotrek and Bugman in turning a desperate battle at Karak Varn in the Dwarfs' favour; the trio pledged to help their kin again in their hour of need. [The three Dwarf heroes](https://whfb.lexicanum.com/wiki/Gotrek_%26_Felix).
- **Legend and identity:** His recurrent rescues of endangered Dwarfs underpin his ancestral-protector reputation. His identification with Snorri Whitebeard is part of the lore surrounding him, not a reason to install him as a ruling king in this system. [Grombrindal: identity and appearances](https://whfb.lexicanum.com/wiki/Grombrindal).

## 9. Local references and implementation notes

- **Balance:** `Dev Stuff/Examples/Balance Guide.txt`. Direct-effect values above follow this guide; the small passive local equivalents are not directly priced there.
- **World-state and voice:** `Dev Stuff/Examples/Lore Reference.txt`. Local mod premises take precedence over outside chronology or faction assumptions.
- **Alignment and Administration:** `common/scripted_effects/war_reset_racial.txt`; alignment changes in `common/scripted_effects/war_scripted_effects.txt`; display names in `localisation/war_misc_l_english.yml`. Use the resulting country modifiers, not the religions that originally assigned them.
- **Starting ownership:** the 18 province history files listed in the roster were checked against `history/provinces`. All 18 starts have different owners. Erengrad belongs to Kislev, not the dormant Erengrad tag; the selected Angrund province is Kvinn Wyr, not an assumed Eight Peaks holding.
- **Map validation:** pixel adjacency identified Lyonesse city (484) and Gaen Vale (1828) as isolated landmasses. Implementation uses Merton (284, A17) and Phoenix Gate (1829, H08) instead. Hojizu (4776) belongs to a principal Nippon landmass; Ulthuan and Nippon mainland eligibility is recorded with the implementation assets.
- **Gelt overlap:** the Altdorf college upgrade in `common/great_projects/01_old_world_monuments.txt` now grants a **Magister of the Gold Order** with the existing general's stats. It no longer duplicates the unique travelling Gelt. Previously recruited generals in an existing save are not retroactively renamed.
- **Wulfhart local exploit:** `localisation/war_enclave_provinces_l_english.yml`, Beasts of Telldros enclave text, supplies the Norscan hunt in 2501.
- **Implementation status:** all 360 events, 1,049 response options, 18 presence modifiers, one-time startup placement, shared movement, pulse registration, BOM localisation, and 18 sourced event pictures are implemented. Exact effects and refined labels are in `Adventurers/event_data.json`; the original conceptual tables below remain a record of the approved design. Static and script-simulation checks are recorded in `Adventurers/validation.json`. An in-game playtest remains necessary to confirm presentation and engine execution.

<a id="full-event-catalogue"></a>

## 10. Full event concept catalogue

**Scope:** 18 adventurers × 4 categories × 5 concepts = **360 concepts**, arranged in **72 five-event pools**. The short IDs below are design references, not reserved EU4 event IDs. FH = friendly/neutral home; FA = friendly/neutral abroad; EH = enemy home; EA = enemy abroad.

**How to read the tables:** each report tells the ruler what has already happened. Each lettered response is a separate option concept; effects following the colon describe the intended gameplay result. The reports below are the approved seeds for the finished 2–3-paragraph localisation. The intended event Weighing Value is shown beside its title. Exact scripted rewards and refined response labels are maintained in `Adventurers/event_data.json`.

**Shared resolution for all 360 concepts:** the adventurer ultimately departs or escapes after every response, including pursuit, arrest, refusal, and inaction. Apply the complete movement rule in section 2: two or more neighboring countries use a random eligible neighbor; zero or one uses a random eligible country worldwide. Then select a permitted province within that country. References to an adventurer already having left mean the ruler receives a delayed report; mechanically the unique location transfers when the option resolves.

**Balance status:** targets are +1/+2 for friendly/neutral encounters and −1/−2 for enemy encounters. Every implemented response is priced within ±1 of its event target, including repair expenses and unavoidable damage, with its total commented in the script. No extra narrative damage is applied outside the selected option. “Ignore,” “accept,” and “leave” responses retain the stated consequences; they do not erase the incident. Broad concept rewards such as tradition or local defence were converted to priced direct effects with matching instruction, reconstruction, or public recognition in the option text.

“Administrative/diplomatic/military knowledge” means a prospective gain of the corresponding monarch power. Income, development, manpower, prestige, innovativeness, professionalism, devastation, and a small rebel rising can use the guide’s direct-effect examples. “Trade gains,” “production,” “authority,” and “provincial recovery” describe purposes rather than new statistics: prefer appropriately budgeted income, power, development, prestige, or recovery effects. A one-off army/naval tradition change, reduced local unrest, a local defence/trade bonus, or a precise recovery effect is **not directly priced by the guide in that form**; convert it to a priced direct effect where suitable, or explicitly resolve its valuation before coding. No unsupported numerical valuation is asserted here. Prefer direct effects and keep timed country modifiers to roughly half or fewer of eventual options.

**Story eligibility:** Alignment/Racial Administration alone determines the relationship category, and the fixed geography determines home versus abroad. A story about the owner’s undead troops, flying machinery, a siege, or a particular institution also needs that asset to make sense. Use suitable local wording or another concept when it does not; do not invent an undead state army for a living host or change the enemy test to accommodate the story. Keep a broadly applicable eligible concept in every pool. A reported foreign expedition may end in the current province, but its rewards and penalties must reach this province or its owner.

**Lore coverage:** each character’s L1/L2/etc. entries below correspond to the sourced exploits and background in section 8. Every one of the **68 lore entries** has at least one linked concept. All 360 new incidents are invented mod adaptations, not additional canonical claims. Earlier feats can inform testimony or remembered obligations; undated and later feats supply clearly identified echoes. No concept automatically kills a named country ruler, forces an End Times outcome, discovers Karak Zorn, turns Sienna into a Necromancer, or duplicates another travelling adventurer. A story inspired by a shared adventure uses local companions, retrospective evidence, or an independent expedition unless an eventual explicit crossover checks the other character’s location.

### Catalogue navigation

| Adventurer | Concepts |
|---|---:|
| [Balthasar Gelt](#catalogue-gel) | 20 |
| [Teclis](#catalogue-tec) | 20 |
| [Deathmaster Snikch](#catalogue-sni) | 20 |
| [Josef Bugman](#catalogue-bug) | 20 |
| [Bardin Goreksson](#catalogue-bar) | 20 |
| [Harald Hammerstorm](#catalogue-har) | 20 |
| [Abhorash](#catalogue-abh) | 20 |
| [Elspeth von Draken](#catalogue-els) | 20 |
| [Markus Wulfhart](#catalogue-wul) | 20 |
| [Gotrek Gurnisson and Felix Jaeger](#catalogue-gof) | 20 |
| [Repanse de Lyonesse](#catalogue-rep) | 20 |
| [Sienna Fuegonasus](#catalogue-sie) | 20 |
| [Malakai Makaisson](#catalogue-mal) | 20 |
| [Tyrion](#catalogue-tyr) | 20 |
| [Gor-Rok](#catalogue-gor) | 20 |
| [Nakai the Wanderer](#catalogue-nak) | 20 |
| [Thanquol and Boneripper](#catalogue-tha) | 20 |
| [Grombrindal](#catalogue-gro) | 20 |

<a id="catalogue-gel"></a>

### 10.1. Balthasar Gelt

**Fame:** 5/5. **Start:** **Iron Court — I22**, Shang-Yang **2972** (Grand Cathay). **Enemy profile:** A, as defined in section 5. **Home:** The Empire, including Westerland.

#### Lore coverage

| Lore reference | Exploit or background and chronology | Concepts representing it |
|---|---|---|
| **L1** | Temporary gold used to pay for passage, followed by the captain's bounty; undated. | [GEL-FH03](#gel-fh03), [GEL-FA01](#gel-fa01), [GEL-EH03](#gel-eh03), [GEL-EA01](#gel-ea01), [GEL-EA05](#gel-ea05) |
| **L2** | Black-powder research and cooperation with the College of Engineers; undated. | [GEL-FH01](#gel-fh01), [GEL-FH05](#gel-fh05), [GEL-FA02](#gel-fa02), [GEL-FA05](#gel-fa05), [GEL-EH02](#gel-eh02), [GEL-EH05](#gel-eh05), [GEL-EA03](#gel-ea03), [GEL-EA05](#gel-ea05) |
| **L3** | Laboratory explosion and the golden mask; undated. Do not establish a definitive explanation for the mask. | [GEL-FH02](#gel-fh02), [GEL-FA03](#gel-fa03), [GEL-EH04](#gel-eh04), [GEL-EA04](#gel-ea04) |
| **L4** | Gausser's payroll transmuted into lead at Salzenmund in 2516; later inspiration, not a compulsory replay against Nordland. | [GEL-FH04](#gel-fh04), [GEL-FA04](#gel-fa04), [GEL-EH01](#gel-eh01), [GEL-EA02](#gel-ea02) |

#### Friendly/neutral — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="gel-fh01"></a>**GEL-FH01 — Powder Without Smoke**<br>Target WV **+1** | Your artillery clerk reports that Gelt's overnight experiments produced a cleaner powder batch, but the guild has impounded his notes after a dispute over credit. | **A.** Recognize the engineers and adopt the method: military knowledge.<br>**B.** Purchase the notes for civilian furnaces: production.<br>**C.** Leave the dispute to the guild: a smaller commercial benefit. | L2 |
| <a id="gel-fh02"></a>**GEL-FH02 — Behind the Golden Door**<br>Target WV **+1** | A magistrate reports an explosion in a rented laboratory. Gelt rescued the apprentices and escaped behind his mask; salvagers have recovered unfamiliar refining instruments from the wreckage. | **A.** Rebuild around the recovered instruments: production with repair costs.<br>**B.** Give them to the college: innovativeness. | L3 |
| <a id="gel-fh03"></a>**GEL-FH03 — The Captain's Old Claim**<br>Target WV **+1** | A river captain petitions your court over gold that became lead after Gelt paid his fare. Examination of the remaining metal reveals a useful assay technique, while the captain demands restitution. | **A.** Compensate the captain and study the sample: administrative knowledge.<br>**B.** Broker a guild settlement: trade.<br>**C.** Dismiss the claim but retain the evidence: a smaller research gain. | L1 |
| <a id="gel-fh04"></a>**GEL-FH04 — A Mutiny Paid in Lead**<br>Target WV **+2** | Your treasurer reports that conspirators preparing to seize a local arsenal have lost their mercenary payroll to Gelt's transmutation. Their abandoned accounts name officials involved in the plot. | **A.** Prosecute the organizers: authority and prestige.<br>**B.** Recover their remaining assets: treasury.<br>**C.** Reward informants: administrative knowledge with expense. | L4 |
| <a id="gel-fh05"></a>**GEL-FH05 — The Engineers' Dinner**<br>Target WV **+1** | Guild officers report that a quarrel at a banquet ended with Gelt demonstrating a safer powder measure on the dining table. He departed before the senior master could forbid its use. | **A.** Authorize a public trial: military knowledge.<br>**B.** Commission controlled workshop copies: production.<br>**C.** Sponsor independent verification: innovativeness.<br>**D.** Archive the demonstration: modest prestige. | L2 |

#### Friendly/neutral — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="gel-fa01"></a>**GEL-FA01 — Lead on Foreign Scales**<br>Target WV **+1** | Your customs officers intercepted counterfeit-looking gold after Gelt left a caravanserai. A local assayer found that the residue exposes adulterated imports more reliably than the existing test. | **A.** Pay affected merchants and adopt the test: trade.<br>**B.** Retain the residue for scholars: innovativeness.<br>**C.** Allow merchants to settle privately: modest commercial gains. | L1 |
| <a id="gel-fa02"></a>**GEL-FA02 — The Furnace Translator**<br>Target WV **+2** | A foreign-language notebook left by Gelt has helped local metalworkers recover ore they previously discarded. Two guilds now claim exclusive rights to the technique. | **A.** Publish a translation: production and knowledge.<br>**B.** Grant a limited charter: income and prestige.<br>**C.** Divide access between guilds: administrative gains. | L2 |
| <a id="gel-fa03"></a>**GEL-FA03 — The Masked Patient**<br>Target WV **+1** | A physician reports treating apprentices after an alchemical flash in Gelt's lodgings. The wizard paid with medical reagents and vanished, leaving both useful supplies and alarming rumours about his face. | **A.** Distribute the reagents through licensed physicians: development.<br>**B.** Reserve them for study: innovativeness. | L3 |
| <a id="gel-fa04"></a>**GEL-FA04 — A Warlord's Worthless Chest**<br>Target WV **+2** | Border traders report that Gelt turned a raider's tribute chest into lead before its owner could hire an army. Captured ledgers expose the foreign brokers supplying the raiders. | **A.** Buy the ledgers and disrupt the network: diplomatic knowledge.<br>**B.** Seize implicated goods: income.<br>**C.** Finance protected caravans: trade and prestige with expense. | L4 |
| <a id="gel-fa05"></a>**GEL-FA05 — The Price of a Golden Statue**<br>Target WV **+1** | Temple stewards report that Gelt used a damaged ceremonial statue to demonstrate metalworking, leaving stronger fittings but a scandal over its altered appearance. | **A.** Pay for restoration while retaining the method: production.<br>**B.** Commission a scholarly explanation: administrative knowledge.<br>**C.** Let the temple claim the discovery: prestige. | L2 |

#### Enemy — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="gel-eh01"></a>**GEL-EH01 — The Salzenmund Trick**<br>Target WV **−2** | Your paymaster reports that the garrison's chest now contains lead coins. Witnesses saw a golden rider leaving the tower; unpaid soldiers are already gathering outside the treasury. | **A.** Replace the payroll: treasury loss.<br>**B.** Delay payment and contain the disorder: administrative loss and devastation.<br>**C.** Expose the sabotage publicly: prestige loss with military reorganization. | L4 |
| <a id="gel-eh02"></a>**GEL-EH02 — The Arsenal's Soft Teeth**<br>Target WV **−1** | An ordnance inspection finds cannon fittings softened beyond use after Gelt entered the occupied foundry in disguise. He has fled through a service passage known to the former workers. | **A.** Purchase replacement fittings: income loss.<br>**B.** Salvage the metal and suspend operations: military power loss. | L2 |
| <a id="gel-eh03"></a>**GEL-EH03 — A Bounty in False Gold**<br>Target WV **−1** | Your governor reports that agents bribed to locate Gelt accepted coins that reverted to lead. Their furious informants have exposed several government safe houses. | **A.** Reimburse the network: treasury loss.<br>**B.** Abandon the compromised contacts: diplomatic power loss.<br>**C.** Prosecute the agents: prestige and administrative losses. | L1 |
| <a id="gel-eh04"></a>**GEL-EH04 — Windows of Brass**<br>Target WV **−2** | The occupation commandant reports that Gelt sealed a requisitioned laboratory in metal while prisoners escaped through its cellar. The frightened garrison has damaged adjoining houses trying to break in. | **A.** Pay specialist smiths: income loss.<br>**B.** Force a breach: devastation.<br>**C.** Abandon the building and restore discipline: military and prestige losses. | L3 |
| <a id="gel-eh05"></a>**GEL-EH05 — A Foundry's Silent Strike**<br>Target WV **−1** | Your inspector discovers that Gelt left apprentices instructions for quietly ruining military castings. The apprentices have disappeared, and the foundry's next delivery must be condemned. | **A.** Recall and replace the shipment: treasury loss.<br>**B.** Suspend casting and audit every mould: administrative power loss.<br>**C.** Blame the foreman: prestige loss and local disorder. | L2 |

#### Enemy — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="gel-ea01"></a>**GEL-EA01 — The Diplomatic Gift**<br>Target WV **−1** | Your chamberlain reports that an impressive gold gift brought by Gelt has reverted during an audience. Foreign guests witnessed the humiliation before the wizard escaped from his lodgings. | **A.** Compensate offended guests: treasury loss.<br>**B.** Admit the deception: prestige loss. | L1 |
| <a id="gel-ea02"></a>**GEL-EA02 — Mercenaries Without Masters**<br>Target WV **−2** | A frontier commander reports that Gelt transmuted the advance payment for imported mercenaries. The company is threatening to loot the district before marching away. | **A.** Pay the company again: major treasury loss.<br>**B.** Let them depart under guard: manpower and prestige losses.<br>**C.** Refuse and contain their looting: devastation. | L4 |
| <a id="gel-ea03"></a>**GEL-EA03 — The Golden Sluice**<br>Target WV **−1** | Mine officers report that Gelt fused a drainage mechanism while helping captives escape. Water is rising through the lower workings, and the fugitive has crossed the outer cordon. | **A.** Hire foreign pumps: treasury loss.<br>**B.** Abandon the flooded galleries: production disruption represented by devastation.<br>**C.** Divert engineers from other duties: administrative power loss. | L2 |
| <a id="gel-ea04"></a>**GEL-EA04 — An Embassy of Ash**<br>Target WV **−2** | An official searching Gelt's abandoned workshop triggered a dangerous residue. The explosion destroyed seized military papers and spread panic through the administrative quarter. | **A.** Fund relief and replace records: treasury and administrative losses.<br>**B.** Isolate the quarter: devastation.<br>**C.** Conceal the failure: diplomatic and prestige losses. | L3 |
| <a id="gel-ea05"></a>**GEL-EA05 — The Merchant's Last Lesson**<br>Target WV **−1** | Your trade commissioner reports that Gelt publicly demonstrated the adulteration of state-issued coinage, then disappeared. Merchants are refusing the next tax payment in that currency. | **A.** Exchange suspect coins at a loss: treasury.<br>**B.** Impose a temporary accounting settlement: administrative loss.<br>**C.** Threaten the guilds: prestige loss and disorder. | L1, L2 |

<a id="catalogue-tec"></a>

### 10.2. Teclis

**Fame:** 5/5. **Start:** **Goa — I64**, Goa **4182** (Ind). **Enemy profile:** A, as defined in section 5. **Home:** Ulthuan.

#### Lore coverage

| Lore reference | Exploit or background and chronology | Concepts representing it |
|---|---|---|
| **L1** | Defeated Malekith in a magical confrontation at Finuval Plain; before 2502. | [TEC-FH01](#tec-fh01), [TEC-FA04](#tec-fa04), [TEC-EH01](#tec-eh01), [TEC-EH05](#tec-eh05), [TEC-EA03](#tec-ea03), [TEC-EA05](#tec-ea05) |
| **L2** | Helped Magnus the Pious against Chaos; before 2502. | [TEC-FH03](#tec-fh03), [TEC-FA02](#tec-fa02), [TEC-EH03](#tec-eh03), [TEC-EA04](#tec-ea04) |
| **L3** | Founded the Imperial Colleges of Magic at Magnus's request; before 2502. | [TEC-FH02](#tec-fh02), [TEC-FH05](#tec-fh05), [TEC-FA01](#tec-fa01), [TEC-FA05](#tec-fa05), [TEC-EH02](#tec-eh02), [TEC-EH05](#tec-eh05), [TEC-EA02](#tec-ea02), [TEC-EA05](#tec-ea05) |
| **L4** | Albion adventure with Gotrek and Felix in Giantslayer; later inspiration. Do not move or duplicate the other adventurers. | [TEC-FH04](#tec-fh04), [TEC-FA03](#tec-fa03), [TEC-EH04](#tec-eh04), [TEC-EA01](#tec-ea01) |

#### Friendly/neutral — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="tec-fh01"></a>**TEC-FH01 — The Scar of Finuval**<br>Target WV **+2** | Your wardens report that Teclis broke a lingering hostile enchantment at an old battlefield. Fragments of its design offer rare lessons, but pilgrims are entering the still-dangerous site. | **A.** Close the site for scholarly study: innovativeness and administrative knowledge.<br>**B.** Consecrate a safe memorial: prestige.<br>**C.** Station trained wardens: military knowledge with expense. | L1 |
| <a id="tec-fh02"></a>**TEC-FH02 — Students from the Human Lands**<br>Target WV **+1** | A harbour officer reports that Teclis admitted visiting human apprentices to a private lesson despite objections from local tutors. Their demonstrations have revealed mistakes in the province's teaching manuals. | **A.** Endorse the exchange: diplomatic knowledge.<br>**B.** Circulate corrected manuals: administrative knowledge.<br>**C.** Restrict attendance but retain the findings: modest innovativeness. | L3 |
| <a id="tec-fh03"></a>**TEC-FH03 — The Old Alliance's Dispatches**<br>Target WV **+1** | An archivist reports that Teclis recovered correspondence from the war fought beside Magnus. A comparison with current border reports exposes a familiar pattern of cult infiltration. | **A.** Train investigators from the evidence: administrative knowledge.<br>**B.** Distribute warnings to captains: military knowledge. | L2 |
| <a id="tec-fh04"></a>**TEC-FH04 — Mud from Albion**<br>Target WV **+2** | Your scholars receive Teclis's analysis of a mud-covered stone associated with an overseas expedition. He has neutralized its influence, leaving a useful map of related geomantic disturbances. | **A.** Finance a survey: innovativeness.<br>**B.** Share findings with allied scholars: diplomatic knowledge and prestige.<br>**C.** Secure the stone in a guarded archive: administrative gains. | L4 |
| <a id="tec-fh05"></a>**TEC-FH05 — A Ward Without a Master**<br>Target WV **+1** | Temple attendants report that Teclis repaired a failing protective inscription and identified a local novice capable of maintaining it. Senior custodians refuse to accept the novice's appointment. | **A.** Appoint the novice with oversight: institutional knowledge.<br>**B.** Reward the custodians for adopting the correction: prestige with expense.<br>**C.** Preserve the repair without changing offices: modest local improvement. | L3 |

#### Friendly/neutral — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="tec-fa01"></a>**TEC-FA01 — The Unlicensed School**<br>Target WV **+2** | Your magistrate reports that Teclis has already taught several gifted children to control dangerous magic. Their families seek protection while established authorities demand the school be closed. | **A.** Charter supervised instruction: innovativeness and development.<br>**B.** Place pupils under existing tutors: administrative knowledge.<br>**C.** Close the school but preserve its methods: a smaller research gain. | L3 |
| <a id="tec-fa02"></a>**TEC-FA02 — A Second Magnus**<br>Target WV **+1** | Scouts report that Teclis helped local defenders repel a daemonic breach, then left a stern account comparing their preparation with Magnus's army. Survivors ask for recognition. | **A.** Reward the defenders: prestige.<br>**B.** Adopt the recommended drills: military knowledge.<br>**C.** Fund treatment and equipment: manpower recovery with expense. | L2 |
| <a id="tec-fa03"></a>**TEC-FA03 — Stones Beneath the Orchard**<br>Target WV **+1** | Farmers report that Teclis uncovered an ancient stone beneath their orchard and silenced the nightmares troubling the district. His notes warn against removing its neighbouring markers. | **A.** Pay for a protected survey: administrative knowledge.<br>**B.** Compensate the farmers and fence the site: local development. | L4 |
| <a id="tec-fa04"></a>**TEC-FA04 — The Foreign Court's Duel**<br>Target WV **+2** | Your envoy reports that Teclis defeated a visiting sorcerer's attempt to dominate the court through a concealed spell. The defeated mage fled, leaving compromising letters behind. | **A.** Expose the plot: prestige and diplomatic knowledge.<br>**B.** Quietly dismantle its network: administrative gains.<br>**C.** Ransom implicated intermediaries: income. | L1 |
| <a id="tec-fa05"></a>**TEC-FA05 — The Translator of Eight Winds**<br>Target WV **+1** | A local scholar has translated instructions Teclis left after correcting a dangerous magical experiment. The manuscript challenges a profitable monopoly on supposedly protective charms. | **A.** Publish the translation: innovativeness.<br>**B.** License reliable practitioners: income.<br>**C.** Ask the guild to reform itself: administrative knowledge.<br>**D.** Retain it privately: modest prestige. | L3 |

#### Enemy — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="tec-eh01"></a>**TEC-EH01 — The Unravelling at Dawn**<br>Target WV **−2** | Your commandant reports that Teclis stripped the wards from an occupied fortress before local insurgents stole its supplies. He has vanished, and the defenders no longer trust their protective charms. | **A.** Replace the wards with mundane works: treasury loss.<br>**B.** Rebuild discipline and supply: military power loss.<br>**C.** Pull back from the damaged perimeter: devastation. | L1 |
| <a id="tec-eh02"></a>**TEC-EH02 — The Missing Novices**<br>Target WV **−1** | Your governor reports that Teclis led conscripted magical pupils out of a guarded school. Instructors found their coercive bindings broken and their records copied. | **A.** Recruit replacements: treasury loss.<br>**B.** Reorganize the institution: administrative power loss. | L3 |
| <a id="tec-eh03"></a>**TEC-EH03 — Letters to the Resistance**<br>Target WV **−1** | Your intelligence office intercepted only the last of Teclis's warnings to local communities. The letters compare your rule with former Chaos incursions and identify weaknesses in your patrol routes. | **A.** Change the routes and codes: military power loss.<br>**B.** Confiscate the correspondence: administrative and prestige losses.<br>**C.** Concede a public failure: prestige loss. | L2 |
| <a id="tec-eh04"></a>**TEC-EH04 — The Stone That Refused Us**<br>Target WV **−2** | Surveyors report that a geomantic stone seized for your project became inert after Teclis visited it. Workers fled when its surrounding ground shifted, and the site is now unusable. | **A.** Relocate the project: treasury loss.<br>**B.** Stabilize the ground: administrative loss and expense.<br>**C.** Abandon the workings: devastation. | L4 |
| <a id="tec-eh05"></a>**TEC-EH05 — A Crown's Forbidden Formula**<br>Target WV **−1** | Your court mage reports that Teclis removed a dangerous formula from the palace archive and left evidence of its earlier disasters. Courtiers are questioning the ruler's judgement. | **A.** Acknowledge the risk: prestige loss.<br>**B.** Purge the compromised archive: administrative power loss.<br>**C.** Pay for an independent inquiry: treasury loss. | L1, L3 |

#### Enemy — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="tec-ea01"></a>**TEC-EA01 — The Empty Reliquary**<br>Target WV **−1** | Your keeper of treasures discovers a relic missing and a note from Teclis warning that it was feeding a hostile power. Witnesses saw the Elf leave before the alarm. | **A.** Admit the relic was unsafe: prestige loss.<br>**B.** Purchase a replacement symbol: treasury loss.<br>**C.** Investigate the keeper's patrons: administrative power loss. | L4 |
| <a id="tec-ea02"></a>**TEC-EA02 — An Enemy's Apprentices**<br>Target WV **−2** | Provincial officials report that Teclis taught a group of persecuted spellcasters enough control to escape a state roundup. Their flight has exposed the recruitment office's abuses. | **A.** Compensate affected households: treasury loss.<br>**B.** Reorganize the office: administrative loss.<br>**C.** Suppress the testimony: prestige loss and disorder. | L3 |
| <a id="tec-ea03"></a>**TEC-EA03 — A Battle Already Lost**<br>Target WV **−2** | A garrison report describes Teclis breaking its commander's sorcerous advantage in a brief duel. The commander survived, but the troops abandoned stores during the retreat. | **A.** Restore equipment and pay: treasury loss.<br>**B.** Conduct emergency drills: military power loss.<br>**C.** Withdraw from the exposed district: devastation. | L1 |
| <a id="tec-ea04"></a>**TEC-EA04 — The Coalition He Left Behind**<br>Target WV **−1** | Your diplomats learn that Teclis has convinced local opponents to exchange information rather than compete. Their coordinated petitions reveal scandals that were previously isolated. | **A.** Buy a negotiated settlement: treasury loss.<br>**B.** Revise the offending administration: administrative power loss.<br>**C.** Endure the public accusations: prestige loss. | L2 |
| <a id="tec-ea05"></a>**TEC-EA05 — A Tower Without Shadows**<br>Target WV **−1** | Watchmen report that Teclis cleansed a tower being used for state-sponsored magical coercion. Its bound watchers are gone, and prisoners escaped during the disturbance. | **A.** Replace magical surveillance with paid agents: treasury loss.<br>**B.** Change the security system: diplomatic power loss.<br>**C.** Conceal the escape: prestige loss. | L1, L3 |

<a id="catalogue-sni"></a>

### 10.3. Deathmaster Snikch

**Fame:** 4/5. **Start:** **Hojizu — Z75**, province **4776** (Nippon). **Enemy profile:** B, as defined in section 5. **Home:** Skavenblight/Under-Empire, Cathay and Nippon.

#### Lore coverage

| Lore reference | Exploit or background and chronology | Concepts representing it |
|---|---|---|
| **L1** | Killed Grail Knight Boragild while he prayed; undated. | [SNI-FH01](#sni-fh01), [SNI-FA01](#sni-fa01), [SNI-EH03](#sni-eh03), [SNI-EA01](#sni-ea01) |
| **L2** | Winter of killings inside sealed Karaz-a-Karak and escape; undated. | [SNI-FH02](#sni-fh02), [SNI-FA02](#sni-fa02), [SNI-EH02](#sni-eh02), [SNI-EA02](#sni-ea02) |
| **L3** | Heinrich Frisen's locked-observatory murder is attributed to Snikch, not proven. | [SNI-FH03](#sni-fh03), [SNI-FA03](#sni-fa03), [SNI-EH01](#sni-eh01), [SNI-EA03](#sni-ea03) |
| **L4** | End Times assassination of Thorgrim and ensuing infiltration; later echo only. No automatic death of a named country ruler. | [SNI-FH04](#sni-fh04), [SNI-FA04](#sni-fa04), [SNI-EH04](#sni-eh04), [SNI-EA04](#sni-ea04) |

#### Friendly/neutral — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="sni-fh01"></a>**SNI-FH01 — The Rival's Prayer**<br>Target WV **+1** | Your clan overseer reports that a rival's foreign champion was found dead at prayer. Snikch's messenger has delivered the champion's correspondence, but insists the service remain unacknowledged. | **A.** Exploit the letters: diplomatic knowledge.<br>**B.** Seize the rival's assets: income.<br>**C.** Quietly reward the messenger: prestige with expense. | L1 |
| <a id="sni-fh02"></a>**SNI-FH02 — One Winter's Ledgers**<br>Target WV **+2** | Tunnel officers recover ledgers from a stronghold Snikch infiltrated over several months. The records reveal safe routes through its patrol system and stocks worth stealing. | **A.** Plan limited raids: income and military knowledge.<br>**B.** Sell selected routes to another clan: income.<br>**C.** Strengthen your own tunnel security: administrative knowledge. | L2 |
| <a id="sni-fh03"></a>**SNI-FH03 — An Observatory's Last Chart**<br>Target WV **+1** | A courier deposits star charts stolen from a murdered surface wizard. Snikch's involvement is suggested by a blood-mark, but your agents cannot authenticate it. | **A.** Study the charts: innovativeness.<br>**B.** Sell them through intermediaries: income. | L3 |
| <a id="sni-fh04"></a>**SNI-FH04 — The Gatekeeper's Successor**<br>Target WV **+2** | Your commander reports that Snikch removed a hostile gatekeeper and obtained the signal used to admit supply wagons. A small infiltration team has already returned with military stores. | **A.** Reward the team and distribute stores: military knowledge and manpower.<br>**B.** Sell captured goods: income.<br>**C.** Exploit the signal once more: larger spoils with preparation costs. | L4 |
| <a id="sni-fh05"></a>**SNI-FH05 — The Assassins' Quarrel**<br>Target WV **+1** | Your steward finds two rival murder-contracts pinned to the same corpse. Snikch has killed their intended victim, leaving both sponsors exposed and your court unexpectedly secure. | **A.** Blackmail both sponsors: income.<br>**B.** Expose one and recruit the other: diplomatic knowledge.<br>**C.** Suppress the affair: administrative gains. | Original character-based incident |

#### Friendly/neutral — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="sni-fa01"></a>**SNI-FA01 — The Chapel's Foreign Patron**<br>Target WV **+1** | An agent reports that Snikch killed a knight protecting an overseas enemy's trade interests. The knight's secret payment book has reached your provincial headquarters. | **A.** Disrupt the payments: trade gains.<br>**B.** Auction the names discreetly: income.<br>**C.** Cultivate the compromised merchants: diplomatic knowledge. | L1 |
| <a id="sni-fa02"></a>**SNI-FA02 — Behind the Mountain's Doors**<br>Target WV **+2** | A caravan courier brings sketches Snikch made inside a supposedly sealed foreign hold. Your agents have already used one route to recover confiscated clan property. | **A.** Recover more property: income.<br>**B.** Copy the fortifications: military knowledge.<br>**C.** Pay local smugglers to maintain access: trade with expense. | L2 |
| <a id="sni-fa03"></a>**SNI-FA03 — The Astrologer's Cipher**<br>Target WV **+1** | Your provincial spymaster receives coded correspondence from a locked observatory whose master has vanished. Snikch's accompanying instructions explain the cipher but nothing about the disappearance. | **A.** Read the diplomatic messages: diplomatic knowledge.<br>**B.** Extract astronomical tables: innovativeness. | L3 |
| <a id="sni-fa04"></a>**SNI-FA04 — An Open Door at the Feast**<br>Target WV **+2** | Your agents report that Snikch removed a banquet's security officer and left a servant's route open. They escaped with plans for a rival's military expedition. | **A.** Prepare countermeasures: military knowledge.<br>**B.** Sell a warning to threatened clients: income and prestige.<br>**C.** Keep the route for future intelligence: diplomatic knowledge. | L4 |
| <a id="sni-fa05"></a>**SNI-FA05 — The Price of Silence**<br>Target WV **+1** | A frightened foreign merchant tells your governor that Snikch spared him after discovering a profitable smuggling route. The assassin left instructions for directing its customs payments to your agents. | **A.** Regularize the route quietly: trade gains.<br>**B.** Take an immediate payment: income.<br>**C.** Protect the merchant as an informant: diplomatic knowledge. | Original character-based incident |

#### Enemy — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="sni-eh01"></a>**SNI-EH01 — No Lock Broken**<br>Target WV **−1** | Your astronomer is found dead inside an observatory with every door locked. Officials whisper Snikch's name, but the only certain losses are the scholar and several sensitive charts. | **A.** Hire a replacement and reconstruct the charts: treasury loss.<br>**B.** Suspend the observatory and review access: administrative power loss.<br>**C.** Conceal the missing charts: diplomatic power loss. | L3 |
| <a id="sni-eh02"></a>**SNI-EH02 — The Sealed Hold**<br>Target WV **−2** | Your commandant reports killings continuing despite a complete closure of the settlement. After weeks of paralysis, scouts find evidence that Snikch escaped through the supposedly sealed perimeter. | **A.** Pay for a security overhaul: treasury loss.<br>**B.** Maintain the closure: devastation and administrative loss.<br>**C.** Reopen and admit defeat: prestige and military losses. | L2 |
| <a id="sni-eh03"></a>**SNI-EH03 — A Champion at Prayer**<br>Target WV **−1** | Attendants discover the provincial champion slain at a private shrine. The assassin has gone, and the garrison interprets the killing as proof that even sacred refuges are unsafe. | **A.** Stage a state funeral: treasury loss.<br>**B.** Reorganize the guard: military power loss. | L1 |
| <a id="sni-eh04"></a>**SNI-EH04 — The Warden's Unwatched Stair**<br>Target WV **−2** | Your fortress warden has been assassinated at a secluded lookout. Infiltrators used his stolen signal to enter the stores before a relief patrol drove them away. | **A.** Replace stores and security: treasury loss.<br>**B.** Abandon the compromised wing: devastation.<br>**C.** Court-martial the surviving officers: military and prestige losses. | L4 |
| <a id="sni-eh05"></a>**SNI-EH05 — The Murder That Named Us**<br>Target WV **−1** | Your governor reports that Snikch arranged a victim's papers to implicate government agents. The true assassin escaped while witnesses spread the accusation through the district. | **A.** Commission a credible inquiry: treasury loss.<br>**B.** Confiscate the papers: administrative loss.<br>**C.** Accept the scandal: prestige loss. | Original character-based incident |

#### Enemy — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="sni-ea01"></a>**SNI-EA01 — The Chapel on Foreign Soil**<br>Target WV **−1** | Your envoy's armed protector is found murdered during prayer in a provincial shrine. Snikch has left the envoy alive but stripped of confidential documents. | **A.** Recall and replace the mission: diplomatic power loss.<br>**B.** Pay to repair relations: treasury loss.<br>**C.** Publicly acknowledge the breach: prestige loss. | L1 |
| <a id="sni-ea02"></a>**SNI-EA02 — Winter Behind the Customs Wall**<br>Target WV **−2** | A border governor reports repeated disappearances inside a closed customs compound. Snikch finally escaped with seizure records that expose the state's hidden revenues. | **A.** Rebuild the customs administration: administrative loss.<br>**B.** Reimburse compromised clients: treasury loss.<br>**C.** Abandon the disputed claims: income and prestige losses. | L2 |
| <a id="sni-ea03"></a>**SNI-EA03 — The Wizard's Missing Seal**<br>Target WV **−1** | A court magician is found dead in a locked study, and letters bearing his stolen seal have already redirected official couriers. Investigators suspect Snikch but cannot prove it. | **A.** Replace seals and recall couriers: diplomatic power loss.<br>**B.** Compensate recipients of false orders: treasury loss. | L3 |
| <a id="sni-ea04"></a>**SNI-EA04 — A Gate Opened from Within**<br>Target WV **−2** | Your commander reports a slain watch officer and a supply gate opened during the night. Raiders escaped with powder and prisoners before the alarm reached headquarters. | **A.** Purchase replacement supplies: treasury loss.<br>**B.** Reduce the garrison's commitments: military loss.<br>**C.** Punish the district collectively: devastation and prestige loss. | L4 |
| <a id="sni-ea05"></a>**SNI-EA05 — The Decoy's Funeral**<br>Target WV **−1** | Your intelligence office admits that the alleged assassin it displayed was a decoy. While officials celebrated, Snikch stole the informant register and disappeared. | **A.** Relocate endangered informants: treasury loss.<br>**B.** Replace the network: diplomatic power loss.<br>**C.** Bury the mistake: prestige loss. | Original character-based incident |

<a id="catalogue-bug"></a>

### 10.4. Josef Bugman

**Fame:** 4/5. **Start:** **Goldtooth — I01**, Mistveil **2795** (Mountains of Mourn). **Enemy profile:** A, as defined in section 5. **Home:** The Empire and western Dwarf mountain ranges.

#### Lore coverage

| Lore reference | Exploit or background and chronology | Concepts representing it |
|---|---|---|
| **L1** | Expanded the family brewery into a prosperous settlement; famed XXXXXX and Troll Brew. | [BUG-FH01](#bug-fh01), [BUG-FH05](#bug-fh05), [BUG-FA02](#bug-fa02), [BUG-EH04](#bug-eh04), [BUG-EA05](#bug-ea05) |
| **L2** | Returned from an Imperial delivery to find the brewery destroyed by Goblins. | [BUG-FH02](#bug-fh02), [BUG-FA03](#bug-fa03), [BUG-FA05](#bug-fa05), [BUG-EH01](#bug-eh01), [BUG-EH05](#bug-eh05), [BUG-EA02](#bug-ea02) |
| **L3** | Survivors became rangers to avenge the brewery and recover missing kin. | [BUG-FH02](#bug-fh02), [BUG-FH03](#bug-fh03), [BUG-FA03](#bug-fa03), [BUG-EH01](#bug-eh01), [BUG-EH02](#bug-eh02), [BUG-EH05](#bug-eh05), [BUG-EA02](#bug-ea02), [BUG-EA04](#bug-ea04) |
| **L4** | Pursuit beyond the World's Edge Mountains, night raids, and assistance to Dwarf armies. | [BUG-FH04](#bug-fh04), [BUG-FA01](#bug-fa01), [BUG-FA04](#bug-fa04), [BUG-EH03](#bug-eh03), [BUG-EA01](#bug-ea01), [BUG-EA03](#bug-ea03), [BUG-EA05](#bug-ea05) |

#### Friendly/neutral — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="bug-fh01"></a>**BUG-FH01 — The Seventh Cask**<br>Target WV **+1** | Your brewer's guild reports that Bugman corrected a spoiled batch and left instructions inspired by his celebrated ales. Rival masters are fighting over who may advertise the association. | **A.** Share the method under inspection: production.<br>**B.** Auction a limited licence: income.<br>**C.** Endorse a public tasting: prestige. | L1 |
| <a id="bug-fh02"></a>**BUG-FH02 — Charcoal Beneath the Brewhouse**<br>Target WV **+2** | Workmen restoring an abandoned brewery uncovered records Bugman recognized from his ruined settlement. His rangers recovered stolen vessels from a nearby camp, and displaced brewing families are asking to settle. | **A.** Grant a rebuilding charter: development with expense.<br>**B.** Employ the families in existing workshops: production and knowledge.<br>**C.** Sell surplus vessels to fund relief: income. | L2, L3 |
| <a id="bug-fh03"></a>**BUG-FH03 — Names on the Missing List**<br>Target WV **+1** | A ranger delivers rescued captives and a list of families taken by raiders. Bugman has continued the pursuit; the survivors require somewhere safe to rebuild their lives. | **A.** Settle the families: local development.<br>**B.** Recruit experienced survivors: manpower.<br>**C.** Finance their return to kin: prestige with expense. | L3 |
| <a id="bug-fh04"></a>**BUG-FH04 — Crossbows Before Dawn**<br>Target WV **+2** | Your field officer reports that Bugman's rangers broke an encircling raider camp during the night. They departed after sharing ale with the exhausted defenders, leaving captured supplies. | **A.** Distribute the stores to soldiers: manpower and military knowledge.<br>**B.** Return stolen property: prestige and development.<br>**C.** Sell unclaimed spoils: income. | L4 |
| <a id="bug-fh05"></a>**BUG-FH05 — Troll Brew at the Muster**<br>Target WV **+1** | A muster captain reports that Bugman's potent beer revived weary volunteers but caused a noisy dispute with the quartermaster. The brewer left enough ordinary ale to provision the next march. | **A.** Adopt controlled rations: manpower.<br>**B.** Pay the quartermaster and retain brewing advice: production.<br>**C.** Stage a veterans' gathering: prestige. | L1 |

#### Friendly/neutral — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="bug-fa01"></a>**BUG-FA01 — A Caravan with Empty Tankards**<br>Target WV **+1** | Merchants report that Bugman's rangers rescued their wagons, then consumed much of the recovered beer. The remaining cargo and an accurate route survey have reached your customs house. | **A.** Reward the rangers through their suppliers: trade with expense.<br>**B.** Use the route survey: diplomatic knowledge. | L4 |
| <a id="bug-fa02"></a>**BUG-FA02 — Grain from a Strange Valley**<br>Target WV **+2** | Local brewers report that Bugman adapted his methods to unfamiliar grain and repaired their failing vats. He has left, but their first successful batch attracted merchants from neighbouring markets. | **A.** Support wider production: development.<br>**B.** Sponsor a merchant fair: trade and prestige.<br>**C.** Sell the recipe rights locally: income. | L1 |
| <a id="bug-fa03"></a>**BUG-FA03 — A Brand on the Barrel**<br>Target WV **+1** | Your market inspector found Bugman's old brewery mark on stolen casks. The ranger followed the sellers, returned with freed workers, and vanished before the smugglers' patrons could retaliate. | **A.** Protect the witnesses: administrative knowledge.<br>**B.** Employ their skills: production.<br>**C.** Confiscate the smugglers' stock: income. | L2, L3 |
| <a id="bug-fa04"></a>**BUG-FA04 — The Pass Beyond the Mountains**<br>Target WV **+2** | A caravan master reports that Bugman tracked raiders across a pass dismissed as impassable. The rangers recovered supplies and left cairns marking a safer crossing. | **A.** Survey and open the route: trade and development.<br>**B.** Buy the recovered provisions: manpower with expense.<br>**C.** Circulate the warning to merchants: diplomatic knowledge. | L4 |
| <a id="bug-fa05"></a>**BUG-FA05 — The Emperor's Delivery**<br>Target WV **+1** | Your governor receives a battered consignment bearing a distant customer's seal. Bugman recovered it from thieves and left the decision to forward it or settle the disputed freight charges to your officials. | **A.** Forward it with an escort: diplomatic prestige.<br>**B.** Arrange a paid local sale: income.<br>**C.** Compensate the carrier and retain brewing samples: production knowledge. | L2 |

#### Enemy — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="bug-eh01"></a>**BUG-EH01 — The Brewery Burns Twice**<br>Target WV **−2** | Your governor reports that Bugman destroyed a requisitioned brewery after finding stolen family equipment inside. The workers escaped with his rangers, leaving the garrison without its contracted supplies. | **A.** Import replacements: treasury loss.<br>**B.** Divert civilian stocks: devastation.<br>**C.** Reduce military allocations: military power loss. | L2, L3 |
| <a id="bug-eh02"></a>**BUG-EH02 — A Grudge in the Granary**<br>Target WV **−1** | Quartermasters discover that Bugman's rangers emptied a grain depot serving the troops who occupied a Dwarf settlement. The raiders posted the names of missing captives on the doors. | **A.** Buy replacement grain: treasury loss.<br>**B.** Redistribute existing supplies: administrative power loss.<br>**C.** Ignore the demand and endure shortages: devastation. | L3 |
| <a id="bug-eh03"></a>**BUG-EH03 — The Night of Broken Crossbows**<br>Target WV **−2** | Your camp commander reports a night attack that freed prisoners and destroyed siege equipment. Tracks suggest Bugman's rangers had watched the camp for days before striking. | **A.** Rebuild the equipment: treasury loss.<br>**B.** Abandon the operation: military and prestige losses.<br>**C.** Requisition local materials: devastation. | L4 |
| <a id="bug-eh04"></a>**BUG-EH04 — The False XXXXXX**<br>Target WV **−1** | Your excise officer reports that Bugman exposed counterfeit ale sold under his name by a state contractor. Merchants now distrust the whole consignment, and the contractor has fled. | **A.** Refund purchasers: treasury loss.<br>**B.** Investigate the licence: administrative power loss. | L1 |
| <a id="bug-eh05"></a>**BUG-EH05 — A Delivery That Never Arrived**<br>Target WV **−1** | A supply barge vanished near the site of a former Dwarf brewery. Survivors say Bugman spared the hired crew but took its cargo and released prisoners hidden below deck. | **A.** Replace the cargo quietly: treasury loss.<br>**B.** Tighten river controls: diplomatic power loss.<br>**C.** Deny the prisoners existed: prestige loss. | L2, L3 |

#### Enemy — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="bug-ea01"></a>**BUG-EA01 — Ale for the Wrong Army**<br>Target WV **−1** | Your commissary reports that Bugman intercepted a purchased ale convoy and redirected it to your local opponents. The merchants demand payment despite the loss. | **A.** Pay the merchants: treasury loss.<br>**B.** Contest the contracts: administrative power loss.<br>**C.** Abandon the purchase: military power loss. | L4 |
| <a id="bug-ea02"></a>**BUG-EA02 — The Brewer's Mark Abroad**<br>Target WV **−2** | A provincial officer found Bugman's rangers inside a warehouse dealing in plundered Dwarf goods. They escaped with captives and set fire to the illegally stored cargo. | **A.** Compensate surrounding businesses: treasury loss.<br>**B.** Let the district absorb the damage: devastation.<br>**C.** Expose and dismantle the trafficking network: administrative loss. | L2, L3 |
| <a id="bug-ea03"></a>**BUG-EA03 — The Caravan's Last Campfire**<br>Target WV **−1** | Scouts find your raiding convoy abandoned around cold fires. Bugman's rangers freed its prisoners and removed the pack animals, leaving a grudgingly precise inventory of what they took. | **A.** Purchase animals and equipment: treasury loss.<br>**B.** Reduce the convoy service: military power loss. | L4 |
| <a id="bug-ea04"></a>**BUG-EA04 — A Tavern Full of Witnesses**<br>Target WV **−1** | Your governor reports that Bugman publicly identified captives from his lost community among a merchant's servants. The ensuing rescue exposed the merchant's official protection and emptied the tavern into the streets. | **A.** Pay restitution: treasury loss.<br>**B.** Prosecute compromised officials: administrative power loss.<br>**C.** Silence the witnesses: prestige loss. | L3 |
| <a id="bug-ea05"></a>**BUG-EA05 — The Mountain King's Barrels**<br>Target WV **−2** | An imported ceremonial ale shipment was destroyed after Bugman discovered that its profits supported raiders. Visiting delegates watched the dispute and now demand guarantees for their own goods. | **A.** Compensate the delegation: treasury loss.<br>**B.** Renegotiate the supply agreement: diplomatic power loss.<br>**C.** Abandon the ceremony: prestige and income losses. | L1, L4 |

<a id="catalogue-bar"></a>

### 10.5. Bardin Goreksson

**Fame:** 4/5. **Start:** **Darkhold — B23**, Shadowmount **4258** (Darklands). **Enemy profile:** A, as defined in section 5. **Home:** Grey Mountains, World's Edge Mountains and the Empire.

#### Lore coverage

| Lore reference | Exploit or background and chronology | Concepts representing it |
|---|---|---|
| **L1** | Ironbreaker service at Karak Norn before his ranger career. | [BAR-FH01](#bar-fh01), [BAR-FH05](#bar-fh05), [BAR-FA02](#bar-fa02), [BAR-EH01](#bar-eh01), [BAR-EA01](#bar-ea01), [BAR-EA05](#bar-ea05) |
| **L2** | Search for Karak Zorn; a continuing quest, never a confirmed discovery in these concepts. | [BAR-FH02](#bar-fh02), [BAR-FA01](#bar-fa01), [BAR-FA05](#bar-fa05), [BAR-EH02](#bar-eh02), [BAR-EA02](#bar-ea02) |
| **L3** | Collective defence of Ubersreik and Reikland in the later Vermintide era. | [BAR-FH03](#bar-fh03), [BAR-FH05](#bar-fh05), [BAR-FA03](#bar-fa03), [BAR-EH03](#bar-eh03), [BAR-EH05](#bar-eh05), [BAR-EA03](#bar-ea03) |
| **L4** | Later Outcast Engineer development and custom Steam-Assisted Crank Gun; optional career inspiration without imposing all careers. | [BAR-FH04](#bar-fh04), [BAR-FA04](#bar-fa04), [BAR-EH04](#bar-eh04), [BAR-EA04](#bar-ea04) |

#### Friendly/neutral — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="bar-fh01"></a>**BAR-FH01 — The Old Ironbreaker's Tunnel**<br>Target WV **+1** | Your engineer reports that Bardin recognized a failing support pattern from his Ironbreaker service and led trapped workers out. He left a sketch of how to brace the passage before moving on. | **A.** Repair to his design: local development.<br>**B.** Train the rescue crews: military knowledge.<br>**C.** Reward the workers' testimony: prestige. | L1 |
| <a id="bar-fh02"></a>**BAR-FH02 — A Map That Ends in Questions**<br>Target WV **+1** | An archivist reports that Bardin compared a supposed Karak Zorn map with old toll records and exposed a forgery. The genuine fragments still identify forgotten trading routes. | **A.** Fund a careful survey: diplomatic knowledge.<br>**B.** Catalogue the fragments: administrative knowledge. | L2 |
| <a id="bar-fh03"></a>**BAR-FH03 — Five Voices in the Cellar**<br>Target WV **+2** | Your watch captain reports that Bardin organized a mixed band of locals against ratmen beneath a storehouse. Survivors disagree over who deserves credit, but several missing households have returned. | **A.** Recognize all participants: prestige and manpower.<br>**B.** Investigate the tunnels: military knowledge.<br>**C.** Compensate the storekeeper and preserve the evidence: administrative gains. | L3 |
| <a id="bar-fh04"></a>**BAR-FH04 — The Crank Gun in the Yard**<br>Target WV **+1** | A workshop master reports that Bardin's improvised gun drove off attackers during a delivery dispute. The machine jammed immediately afterward, leaving useful design sketches and an angry insurance claimant. | **A.** Purchase the prototype: innovativeness.<br>**B.** Pay for repairs and train gunsmiths: military knowledge.<br>**C.** Return the sketches to the guild: production knowledge. | L4 |
| <a id="bar-fh05"></a>**BAR-FH05 — A Ranger's Warning Bells**<br>Target WV **+2** | Village reeves report that Bardin linked their watchposts after recognizing signs of a coordinated underground attack. The first alarm allowed several settlements to evacuate their stores safely. | **A.** Fund the warning network: development and military knowledge.<br>**B.** Reward the reeves: prestige.<br>**C.** Redistribute the saved supplies: manpower and income. | L1, L3 |

#### Friendly/neutral — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="bar-fa01"></a>**BAR-FA01 — The Stone in the Caravan**<br>Target WV **+1** | A merchant reports that Bardin identified a carved stone as a clue in his search for Karak Zorn. He traded practical mining advice for permission to copy it and left without claiming a discovery. | **A.** Use the mining advice: production.<br>**B.** Preserve the inscription for scholars: administrative knowledge.<br>**C.** Sponsor translation: innovativeness with expense. | L2 |
| <a id="bar-fa02"></a>**BAR-FA02 — A Door Made for Shorter Men**<br>Target WV **+2** | Your surveyors report that Bardin opened a forgotten Dwarf refuge beneath a foreign hill. He rescued stranded travellers and sealed a dangerous lower passage, leaving the upper chambers usable. | **A.** Restore the refuge: development.<br>**B.** Catalogue its fittings: innovativeness.<br>**C.** Provision a permanent rescue station: manpower with expense. | L1 |
| <a id="bar-fa03"></a>**BAR-FA03 — The Stranger Who Held the Stairs**<br>Target WV **+1** | A magistrate reports that Bardin held a stairwell while civilians fled a vermin-infested customs house. The rescued clerks recovered records of unpaid duties during their escape. | **A.** Recover the duties fairly: income.<br>**B.** Honour the rescuers: prestige. | L3 |
| <a id="bar-fa04"></a>**BAR-FA04 — A Machine the Guild Never Approved**<br>Target WV **+2** | Artisans report that Bardin adapted a hand-cranked mechanism to clear a collapsed quarry route. Conservative masters object to his methods, but the recovered workforce has returned safely. | **A.** Sponsor controlled trials: innovativeness.<br>**B.** Adopt the hauling mechanism: production and development.<br>**C.** Compensate the guild and publish the drawings: administrative knowledge. | L4 |
| <a id="bar-fa05"></a>**BAR-FA05 — The Lost Hold's False Heir**<br>Target WV **+1** | Your court receives evidence from Bardin that a travelling claimant sold invented rights to Karak Zorn. The claimant fled, leaving deposits and genuine geographical notes behind. | **A.** Return deposits and prosecute accomplices: prestige.<br>**B.** Fund a map archive: diplomatic knowledge.<br>**C.** Retain unclaimed funds: income. | L2 |

#### Enemy — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="bar-eh01"></a>**BAR-EH01 — The Passage Beneath the Barracks**<br>Target WV **−1** | Your commandant reports that Bardin used an old Ironbreaker route to free detainees beneath the barracks. The tunnel map he left is deliberately incomplete. | **A.** Pay engineers to secure the route: treasury loss.<br>**B.** Close the lower barracks: military power loss.<br>**C.** Reorganize detention records: administrative power loss. | L1 |
| <a id="bar-eh02"></a>**BAR-EH02 — A False Map Turned Against Us**<br>Target WV **−1** | Your governor admits that a forged Karak Zorn map intended to lure Bardin into custody instead led your pursuit into an abandoned quarry. He escaped after exposing the scheme. | **A.** Compensate the injured patrol: treasury loss.<br>**B.** Investigate the failed operation: administrative power loss. | L2 |
| <a id="bar-eh03"></a>**BAR-EH03 — The Cellar That Answered Back**<br>Target WV **−2** | Your occupation officer reports that Bardin organized civilians and deserters against a hidden supply post. The attackers recovered captives, scattered the guards, and escaped through the drains. | **A.** Replace the supplies and guards: treasury loss.<br>**B.** Sweep the district: military loss and devastation.<br>**C.** Admit the post was compromised: prestige loss and reorganization. | L3 |
| <a id="bar-eh04"></a>**BAR-EH04 — Cog Teeth in the Gatehouse**<br>Target WV **−2** | Your fortress engineer reports that Bardin used a compact experimental weapon to drive guards from a gatehouse. Escaping prisoners disabled the winch before he withdrew. | **A.** Rebuild the gate mechanism: treasury loss.<br>**B.** Hold a wider perimeter: military power loss.<br>**C.** Abandon nearby houses for a clear field of fire: devastation. | L4 |
| <a id="bar-eh05"></a>**BAR-EH05 — The Ranger's Empty Camp**<br>Target WV **−1** | Patrols raided Bardin's camp after he exposed their abuse of villagers. They found misleading trail signs and a ledger of requisitions already copied for local petitioners. | **A.** Repay disputed requisitions: treasury loss.<br>**B.** Revise the patrol service: administrative power loss.<br>**C.** Dismiss the accusations: prestige loss. | L3 |

#### Enemy — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="bar-ea01"></a>**BAR-EA01 — A Mine Without Its Captives**<br>Target WV **−2** | Your overseer reports that Bardin rescued forced labourers from a failing mine and dismantled the winch to prevent pursuit. Surviving workers refuse to descend until the shaft is inspected. | **A.** Pay for repairs and replacement labour: treasury loss.<br>**B.** Abandon the galleries: devastation.<br>**C.** Divert state engineers: administrative power loss. | L1 |
| <a id="bar-ea02"></a>**BAR-EA02 — The Auction of a False Kingdom**<br>Target WV **−1** | Your collector reports that Bardin exposed a state-backed sale of invented Karak Zorn claims. Foreign buyers demand restitution and threaten to publish the correspondence. | **A.** Refund the buyers: treasury loss.<br>**B.** Negotiate smaller settlements: diplomatic power loss.<br>**C.** Deny responsibility: prestige loss. | L2 |
| <a id="bar-ea03"></a>**BAR-EA03 — The Customs House Survivors**<br>Target WV **−1** | Your governor reports that Bardin led detainees out of a fortified customs house during a vermin attack. Their testimony reveals that officials had ignored warnings for months. | **A.** Compensate the victims: treasury loss.<br>**B.** Replace the customs staff: administrative power loss. | L3 |
| <a id="bar-ea04"></a>**BAR-EA04 — The Missing Mechanism**<br>Target WV **−2** | Your arsenal officer reports that Bardin recovered stolen Dwarf components and used them to disable a pursuit squad. The experimental assembly is gone, and the remaining plans are incomplete. | **A.** Buy substitute parts: treasury loss.<br>**B.** Restart the research: military and administrative losses.<br>**C.** Abandon the project publicly: prestige loss. | L4 |
| <a id="bar-ea05"></a>**BAR-EA05 — An Ironbreaker's Inspection**<br>Target WV **−1** | A foreign engineer invited into your fort proved to be Bardin. Before disappearing, he released a report showing that the contractor had built unsafe escape passages for himself. | **A.** Rebuild the passages: treasury loss.<br>**B.** Prosecute the contractor: administrative power loss.<br>**C.** Suppress the report: prestige loss. | L1 |

<a id="catalogue-har"></a>

### 10.6. Harald Hammerstorm

**Fame:** 3/5. **Start:** **Puppets of Misrule — B77**, Shadowrealm **2644** (Great Eastern Steppes). **Enemy profile:** C, as defined in section 5. **Home:** Norsca, northern Chaos Wastes and Great Eastern Steppes.

#### Lore coverage

| Lore reference | Exploit or background and chronology | Concepts representing it |
|---|---|---|
| **L1** | Killed daemon Mathrag Brainmangler at Khorsvold with his hammer; undated. | [HAR-FH01](#har-fh01), [HAR-FH05](#har-fh05), [HAR-FA02](#har-fa02), [HAR-FA05](#har-fa05), [HAR-EH02](#har-eh02), [HAR-EH05](#har-eh05), [HAR-EA02](#har-ea02), [HAR-EA05](#har-ea05) |
| **L2** | Explored Vorshgar, awakened its dead, then fought them through a day and night; undated. | [HAR-FH02](#har-fh02), [HAR-FH03](#har-fh03), [HAR-FA01](#har-fa01), [HAR-FA04](#har-fa04), [HAR-EH03](#har-eh03), [HAR-EH04](#har-eh04), [HAR-EA03](#har-ea03) |
| **L3** | His hammer banishes spirits and his presence terrifies otherwise fearless undead. | [HAR-FH03](#har-fh03), [HAR-FH04](#har-fh04), [HAR-FA01](#har-fa01), [HAR-FA03](#har-fa03), [HAR-EH01](#har-eh01), [HAR-EA01](#har-ea01), [HAR-EA04](#har-ea04) |

#### Friendly/neutral — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="har-fh01"></a>**HAR-FH01 — The Hammer's Trophy**<br>Target WV **+2** | Your warband's herald reports that Harald destroyed a daemon preying on tributary camps. Its scattered followers left armour and tribute, but rival captains dispute the right to collect them. | **A.** Divide the spoils among the camps: manpower and prestige.<br>**B.** Claim a ruler's share: income.<br>**C.** Reward the scouts who found the threat: military knowledge. | L1 |
| <a id="har-fh02"></a>**HAR-FH02 — Vorshgar's Other Door**<br>Target WV **+1** | Treasure-seekers return from a ruin Harald cleared after they awakened its dead. They carry surviving relics and a bitter warning against following the deeper stair. | **A.** Confiscate dangerous relics for study: innovativeness.<br>**B.** Auction mundane treasure: income.<br>**C.** Reward the warning: prestige. | L2 |
| <a id="har-fh03"></a>**HAR-FH03 — A Night of Broken Bones**<br>Target WV **+2** | Your camp reeve reports that Harald stood against walking dead until sunrise while families escaped. He has departed, leaving the warriors arguing over whether to rebuild or abandon the camp. | **A.** Rebuild with the rescued households: development.<br>**B.** Reward the defenders: manpower and prestige.<br>**C.** Relocate salvaged supplies: income and administrative knowledge. | L2, L3 |
| <a id="har-fh04"></a>**HAR-FH04 — The Dead That Fled**<br>Target WV **+1** | Scouts report a fleeing column of undead after Harald struck its leader. Their abandoned baggage has blocked a road that traders can now reopen. | **A.** Clear and reopen the road: trade gains.<br>**B.** Recover military stores: manpower. | L3 |
| <a id="har-fh05"></a>**HAR-FH05 — A Champion's Unwanted Example**<br>Target WV **+1** | Your captains report that Harald defeated a boasting challenger before the assembled warband. Recruits are imitating his discipline as eagerly as his reckless thirst for combat. | **A.** Organize supervised contests: military knowledge.<br>**B.** Enlist the eager recruits: manpower.<br>**C.** Sponsor a victory feast: prestige. | L1 |

#### Friendly/neutral — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="har-fa01"></a>**HAR-FA01 — The Haunted Caravanserai**<br>Target WV **+1** | Merchants report that Harald demolished the undead guarding an abandoned caravanserai. They want it reopened but fear the warrior's returning followers more than the former ghosts. | **A.** Restore it under your guards: trade.<br>**B.** Salvage its stores: income.<br>**C.** Pay for funerary clearance: development with expense. | L2, L3 |
| <a id="har-fa02"></a>**HAR-FA02 — A Daemon's Broken Idol**<br>Target WV **+2** | Your local governor reports that Harald shattered a daemon's material anchor during a clash outside town. The liberated workshops still contain tribute and useful tools. | **A.** Return tools to their owners: production and prestige.<br>**B.** Inspect the remains under guard: innovativeness.<br>**C.** Claim unowned tribute: income. | L1 |
| <a id="har-fa03"></a>**HAR-FA03 — The Cemetery's Empty Watch**<br>Target WV **+1** | Your magistrate reports that the graveyard's walking sentries collapsed after Harald passed through. Families are asking permission to recover remains previously held for ransom by a rogue keeper. | **A.** Permit supervised burials: prestige.<br>**B.** Seize the keeper's accumulated fees: income. | L3 |
| <a id="har-fa04"></a>**HAR-FA04 — The Foreign Barrow's Warning**<br>Target WV **+2** | Excavators report that Harald fought through a night of awakened skeletons after their survey breached a barrow. The surviving tablets describe safer routes through neighbouring ruins. | **A.** Translate the tablets: administrative knowledge and innovativeness.<br>**B.** Secure the approaches: military knowledge.<br>**C.** Reopen only the outer chambers: income. | L2 |
| <a id="har-fa05"></a>**HAR-FA05 — A Hammer at the Toll Road**<br>Target WV **+1** | A caravan captain reports that Harald killed a monstrous toll-collector and walked away without claiming the toll chest. Several settlements now petition over the recovered payments. | **A.** Return verified payments: trade gains.<br>**B.** Finance road wardens: manpower.<br>**C.** Retain unclaimed funds: income. | L1 |

#### Enemy — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="har-eh01"></a>**HAR-EH01 — Bones at the Northern Gate**<br>Target WV **−2** | Your necromantic commander reports that Harald destroyed the dead guarding a northern gate. The surviving attendants fled when creatures supposedly incapable of fear turned and ran. | **A.** Rebuild the guard: treasury loss.<br>**B.** Redirect other forces: military power loss.<br>**C.** Abandon the exposed district: devastation. | L3 |
| <a id="har-eh02"></a>**HAR-EH02 — The Shrine's Shattered Champion**<br>Target WV **−1** | Your governor reports that Harald killed the champion defending a newly established occupation shrine. Local warriors are circulating the story as proof that your protection is hollow. | **A.** Replace the champion's retinue: treasury loss.<br>**B.** Reorganize the defence: military power loss.<br>**C.** Absorb the humiliation: prestige loss. | L1 |
| <a id="har-eh03"></a>**HAR-EH03 — The Barrow We Reopened**<br>Target WV **−2** | Your excavators awakened an ancient garrison and then watched Harald destroy it along with their equipment. The dig has collapsed and the survivors refuse to return. | **A.** Pay a new survey team: treasury loss.<br>**B.** Seal the site permanently: devastation.<br>**C.** Salvage only the records: administrative power loss. | L2 |
| <a id="har-eh04"></a>**HAR-EH04 — The Night Watch's Last Horn**<br>Target WV **−1** | The last survivors of your patrol report that Harald pursued them through an ancestral ruin after they tried to arrest him. Their equipment remains scattered among freshly smashed tombs. | **A.** Recover and replace equipment: treasury loss.<br>**B.** Discontinue patrols through the ruin: military power loss. | L2 |
| <a id="har-eh05"></a>**HAR-EH05 — A Hammer Against Our Oath**<br>Target WV **−1** | Your occupation captain reports that Harald defeated an officer who claimed the local tribes had submitted willingly. The officer survived, but the public challenge has undermined your agreements. | **A.** Renegotiate the pledges: diplomatic power loss.<br>**B.** Buy renewed loyalty: treasury loss.<br>**C.** Maintain the claim despite ridicule: prestige loss. | L1 |

#### Enemy — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="har-ea01"></a>**HAR-EA01 — A Procession of Empty Armour**<br>Target WV **−2** | Your court receives a report that Harald smashed an undead ceremonial escort in full view of the population. Its attendants fled, leaving the state's sacred insignia trampled in the road. | **A.** Restore the procession at expense: treasury loss.<br>**B.** Suspend ceremonies and reorganize security: administrative loss.<br>**C.** Accept the public humiliation: prestige loss. | L3 |
| <a id="har-ea02"></a>**HAR-EA02 — The Foreign Fort's Broken Hero**<br>Target WV **−1** | Your commander reports that Harald killed the champion stationed at an isolated fort. The remaining soldiers abandoned their outer post rather than accept his next challenge. | **A.** Hire replacements: treasury loss.<br>**B.** Retrain the garrison: military power loss. | L1 |
| <a id="har-ea03"></a>**HAR-EA03 — A Tomb Opened for Tribute**<br>Target WV **−2** | Officials excavating a tomb to collect valuables report that Harald fought its awakened defenders until both treasury chambers and survey camp were ruined. He has already left the district. | **A.** Rehouse the workers and repair the road: treasury loss.<br>**B.** Abandon the site: devastation.<br>**C.** Investigate the failed excavation: administrative power loss. | L2 |
| <a id="har-ea04"></a>**HAR-EA04 — The Spirit That Could Not Return**<br>Target WV **−1** | Your necromancer reports that a bound guardian struck by Harald cannot be summoned again. Its disappearance has exposed a route previously considered secure. | **A.** Purchase mundane guards: treasury loss.<br>**B.** Redesign the defences: military power loss.<br>**C.** Conceal the weakness: administrative power loss. | L3 |
| <a id="har-ea05"></a>**HAR-EA05 — The Tournament's Uninvited Guest**<br>Target WV **−1** | Your herald reports that Harald entered a provincial martial display, defeated its champion, and escaped before the guards closed the field. Foreign observers are asking whether the result will be acknowledged. | **A.** Recognize the result: prestige loss.<br>**B.** Compensate the defeated company: treasury loss.<br>**C.** Discipline the organizers: administrative power loss. | L1 |

<a id="catalogue-abh"></a>

### 10.7. Abhorash

**Fame:** 4/5. **Start:** **Numas — Z09**, province **851** (Nehekhara). **Enemy profile:** D, as defined in section 5. **Home:** Nehekhara.

#### Lore coverage

| Lore reference | Exploit or background and chronology | Concepts representing it |
|---|---|---|
| **L1** | Defended Lahmia against the Priest Kings but could not save it; ancient history. | [ABH-FH01](#abh-fh01), [ABH-FH04](#abh-fh04), [ABH-FA03](#abh-fa03), [ABH-EH01](#abh-eh01), [ABH-EH04](#abh-eh04), [ABH-EA04](#abh-ea04) |
| **L2** | Defeated Neferata at Bel Aliad and refused to surrender her to W'soran; ancient history. | [ABH-FH02](#abh-fh02), [ABH-FA02](#abh-fa02), [ABH-EH02](#abh-eh02), [ABH-EH05](#abh-eh05), [ABH-EA03](#abh-ea03), [ABH-EA05](#abh-ea05) |
| **L3** | Slew a dragon, drank its blood, and overcame ordinary blood dependence; foundation of the Blood Dragons' martial ideal. | [ABH-FH03](#abh-fh03), [ABH-FH05](#abh-fh05), [ABH-FA01](#abh-fa01), [ABH-FA04](#abh-fa04), [ABH-FA05](#abh-fa05), [ABH-EH03](#abh-eh03), [ABH-EH04](#abh-eh04), [ABH-EA01](#abh-ea01), [ABH-EA02](#abh-ea02), [ABH-EA05](#abh-ea05) |

#### Friendly/neutral — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="abh-fh01"></a>**ABH-FH01 — The Palace Steps Remember**<br>Target WV **+2** | Your custodians report that Abhorash defended workers restoring an ancient palace stair against tomb predators. His terse corrections to their inscription contradict the official account of Lahmia's fall. | **A.** Preserve his testimony alongside the old account: administrative knowledge.<br>**B.** Honour the rescued workers: development and prestige.<br>**C.** Quietly retain the corrections: modest scholarly gains. | L1 |
| <a id="abh-fh02"></a>**ABH-FH02 — The Prisoner He Would Not Yield**<br>Target WV **+1** | Your governor reports that Abhorash defeated a dangerous vampire but refused to surrender the captive to a sorcerer claiming authority over her. Their abandoned correspondence exposes a local coercion network. | **A.** Investigate the network: administrative knowledge.<br>**B.** Accept a negotiated departure: diplomatic knowledge.<br>**C.** Confiscate the conspirators' funds: income. | L2 |
| <a id="abh-fh03"></a>**ABH-FH03 — Blood Beyond Hunger**<br>Target WV **+2** | A physician brings observations left by Abhorash after he slew a dangerous scaled beast. He rejected ordinary tribute and warned against mistaking his ancient triumph over hunger for an easily repeated cure. | **A.** Fund cautious study: innovativeness.<br>**B.** Preserve the remains as a trophy: prestige.<br>**C.** Reward the hunters who guided him: manpower and military knowledge. | L3 |
| <a id="abh-fh04"></a>**ABH-FH04 — The Last Gate of Lahmia**<br>Target WV **+1** | Your garrison commander reports that Abhorash held a breach until civilians escaped a collapsing ruin. Survivors compare the rescue with his doomed defence of ancient Lahmia. | **A.** Repair the escape route: development.<br>**B.** Instruct the guard from the account: military knowledge. | L1 |
| <a id="abh-fh05"></a>**ABH-FH05 — A Duel Without Feeding**<br>Target WV **+1** | A local champion returns defeated but alive after challenging Abhorash. The stranger refused the customary payment and left a demanding schedule of exercises for anyone seeking another contest. | **A.** Adopt supervised training: professionalism.<br>**B.** Honour restraint publicly: prestige.<br>**C.** Keep the instructions within the guard: military knowledge. | L3 |

#### Friendly/neutral — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="abh-fa01"></a>**ABH-FA01 — The Dragon's Empty Lair**<br>Target WV **+2** | Your scouts report that Abhorash killed a dangerous drake and departed without taking its hoard. His followers insist the deed recalls his victory over a true dragon, but cannot promise miraculous properties in the remains. | **A.** Secure and distribute the hoard: income.<br>**B.** Fund anatomical study: innovativeness.<br>**C.** Reward nearby settlements for guiding him: development with expense. | L3 |
| <a id="abh-fa02"></a>**ABH-FA02 — A Captive Claimed by Two Courts**<br>Target WV **+1** | Your magistrate reports that Abhorash defeated a visiting vampire and prevented another sorcerer from taking custody. Their dispute spilled confidential letters into your officials' hands. | **A.** Broker a settlement from the letters: diplomatic knowledge.<br>**B.** Expose the coercive bargain: prestige.<br>**C.** Confiscate abandoned valuables: income. | L2 |
| <a id="abh-fa03"></a>**ABH-FA03 — The Foreign City's Stair**<br>Target WV **+2** | Refugees report that Abhorash held a palace stair while a marauding force searched for captives. He left after the evacuation, refusing an invitation to take command. | **A.** Settle the survivors: development.<br>**B.** Train guards in the defence he demonstrated: military knowledge and manpower.<br>**C.** Recover abandoned property: income. | L1 |
| <a id="abh-fa04"></a>**ABH-FA04 — The Swordsman's Unpaid Lesson**<br>Target WV **+1** | Your guard captain admits that a stranger defeated his best officers, then showed them how their formation failed. Witnesses identify Abhorash, who has already continued his journey. | **A.** Pay for the officers to teach others: professionalism with expense.<br>**B.** Preserve the account as a training text: military knowledge. | L3 |
| <a id="abh-fa05"></a>**ABH-FA05 — The Shrine of a False Dragon**<br>Target WV **+1** | Temple officials report that Abhorash exposed a charlatan selling a supposed cure for vampiric hunger. He destroyed the fraudulent draughts but left evidence of the sellers' wider network. | **A.** Prosecute the fraud: administrative knowledge.<br>**B.** Refund victims from seized funds: prestige.<br>**C.** Confiscate unclaimed proceeds: income. | L3 |

#### Enemy — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="abh-eh01"></a>**ABH-EH01 — The Steps We Could Not Hold**<br>Target WV **−2** | Your occupation commander reports that Abhorash cut through the palace guard and led captives out by an ancient stair. The attack has revived stories of Lahmia's defence among the inhabitants. | **A.** Rebuild and reinforce the guard: treasury loss.<br>**B.** Relinquish the exposed palace quarter: devastation.<br>**C.** Suppress the growing legend: administrative and prestige losses. | L1 |
| <a id="abh-eh02"></a>**ABH-EH02 — The Sorcerer's Refused Demand**<br>Target WV **−1** | Your envoy reports that Abhorash defeated your escort after it tried to seize a vampire under his protection. The prisoner escaped, and the papers authorizing the seizure are now public. | **A.** Negotiate an end to the dispute: diplomatic power loss.<br>**B.** Compensate the escort's families: treasury loss. | L2 |
| <a id="abh-eh03"></a>**ABH-EH03 — An Empty Beast Pen**<br>Target WV **−2** | Your beast-master reports that Abhorash killed a prized draconic creature in single combat. He ignored the treasury beside its pen, making the loss look like judgement rather than robbery. | **A.** Import another military beast: treasury loss.<br>**B.** Replace its role with troops: military power loss.<br>**C.** Admit the loss publicly: prestige loss and reorganization. | L3 |
| <a id="abh-eh04"></a>**ABH-EH04 — The Challenge on the Gate**<br>Target WV **−1** | Your governor finds the garrison champion's broken weapon hung above the city gate. Abhorash spared the defeated soldiers but left a demand that prisoners be treated honourably. | **A.** Meet the demand at administrative cost: administrative power loss.<br>**B.** Pay for a new guard establishment: treasury loss.<br>**C.** Reject it despite the scandal: prestige loss. | L1, L3 |
| <a id="abh-eh05"></a>**ABH-EH05 — The Collector of Blood**<br>Target WV **−1** | Your tax officer reports that Abhorash scattered an armed collection party abusing local households. Its ledgers were left with the victims, who now demand repayment. | **A.** Repay the disputed levy: treasury loss.<br>**B.** Investigate the collectors: administrative power loss.<br>**C.** Deny liability: prestige loss. | L2 |

#### Enemy — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="abh-ea01"></a>**ABH-EA01 — The Champion's Last Salute**<br>Target WV **−1** | Your herald reports that Abhorash killed a celebrated officer in an openly witnessed duel. The officer's companions escaped unharmed and insist that their ruler honour the result. | **A.** Acknowledge the duel: prestige loss.<br>**B.** Fund a state funeral: treasury loss.<br>**C.** Challenge the testimony: administrative power loss. | L3 |
| <a id="abh-ea02"></a>**ABH-EA02 — A Dragon Sold Too Soon**<br>Target WV **−2** | Your merchant-agent reports that Abhorash slew the drake bought for your army before delivery. The contract is enforceable, and the creature's remains are worth much less than the promised weapon. | **A.** Pay the contract: treasury loss.<br>**B.** Renegotiate under threat of scandal: diplomatic power loss.<br>**C.** Requisition compensation from the district: devastation. | L3 |
| <a id="abh-ea03"></a>**ABH-EA03 — The Fugitive He Protected**<br>Target WV **−1** | Your prison commander reports that Abhorash took a captive vampire from a sorcerer's escort after defeating its guards. Neither fugitive remains in the province, and the escort's allies demand answers. | **A.** Settle their claims: treasury loss.<br>**B.** Investigate the escort's secret orders: administrative power loss. | L2 |
| <a id="abh-ea04"></a>**ABH-EA04 — The Foreign Palace Breach**<br>Target WV **−2** | Your governor reports that Abhorash opened a route through the palace guard during a mass escape. The surviving soldiers refuse to pursue him into the ruins beyond the city. | **A.** Restore the guard's equipment and pay: treasury loss.<br>**B.** Abandon the outer compound: devastation.<br>**C.** Reorganize the command: military and prestige losses. | L1 |
| <a id="abh-ea05"></a>**ABH-EA05 — The Trophy He Left Behind**<br>Target WV **−1** | A provincial noble presented Abhorash with captives as a reward for killing a monster. Your officials now report the captives freed and the noble publicly defeated before the entire court. | **A.** Compensate those harmed by the noble: treasury loss.<br>**B.** Remove his office: administrative power loss.<br>**C.** Defend him despite the disgrace: prestige loss. | L2, L3 |

<a id="catalogue-els"></a>

### 10.8. Elspeth von Draken

**Fame:** 4/5. **Start:** **Akendorf — A67**, province **872** (Borderlands). **Enemy profile:** A, as defined in section 5. **Home:** The Empire.

#### Lore coverage

| Lore reference | Exploit or background and chronology | Concepts representing it |
|---|---|---|
| **L1** | Travelling collector of arcane artefacts, with towers near Nuln's Gardens of Morr and in the Grey Mountains. | [ELS-FH01](#els-fh01), [ELS-FA01](#els-fa01), [ELS-EH01](#els-eh01), [ELS-EA01](#els-ea01) |
| **L2** | Dealt with the Mire Hulk Rawbones; undated. | [ELS-FH02](#els-fh02), [ELS-FA02](#els-fa02), [ELS-EH02](#els-eh02), [ELS-EA02](#els-ea02) |
| **L3** | Dealt with the vampire Vashara of Lahmia; undated. | [ELS-FH03](#els-fh03), [ELS-FA03](#els-fa03), [ELS-EH03](#els-eh03), [ELS-EA03](#els-ea03) |
| **L4** | Repelled witch hunters seeking to penetrate her towers and secrets. | [ELS-FH04](#els-fh04), [ELS-EH04](#els-eh04) |
| **L5** | Defeated Orhbal Vipergut and his dragon during the later defence of Nuln. | [ELS-FA04](#els-fa04), [ELS-EA04](#els-ea04) |
| **L6** | Talisman given to Bruckner destroyed Tamurkhan when he tried to possess Bruckner; later, costly-trap inspiration. | [ELS-FH05](#els-fh05), [ELS-FA05](#els-fa05), [ELS-EH05](#els-eh05), [ELS-EA05](#els-ea05) |

#### Friendly/neutral — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="els-fh01"></a>**ELS-FH01 — The Tower's Returned Reliquary**<br>Target WV **+1** | Your cemetery keeper reports that Elspeth recovered a stolen funerary relic and identified a dangerous error in its inscription. She returned to her tower before officials could question her methods. | **A.** Correct the burial register and rites: administrative knowledge.<br>**B.** Commission a guarded study: innovativeness.<br>**C.** Honour the keeper's cooperation: prestige. | L1 |
| <a id="els-fh02"></a>**ELS-FH02 — Rawbones in the Reed Beds**<br>Target WV **+2** | Your marsh patrol brings remains of a monstrous corpse-heap destroyed by Elspeth. Witnesses compare it to Rawbones, while nearby villagers demand the blocked waterways be cleared. | **A.** Restore the waterways: development.<br>**B.** Study the creature safely: innovativeness.<br>**C.** Reward the patrol and reclaim supplies: manpower and income. | L2 |
| <a id="els-fh03"></a>**ELS-FH03 — The Lady Behind the Mirror**<br>Target WV **+1** | Your court clerk reports that Elspeth exposed a vampire intermediary using borrowed identities. The intruder escaped her first trap, but abandoned letters reveal a network resembling Vashara's methods. | **A.** Investigate the correspondents: administrative knowledge.<br>**B.** Quietly reverse the bargains: diplomatic knowledge. | L3 |
| <a id="els-fh04"></a>**ELS-FH04 — The Witch Hunters' Silence**<br>Target WV **+1** | Your magistrate reports that hunters who forced their way into Elspeth's refuge returned alive but unable to explain what they saw. They left recovered criminal evidence and a dispute over jurisdiction. | **A.** Review their mandate and use the evidence: administrative knowledge.<br>**B.** Broker limits on future searches: diplomatic knowledge.<br>**C.** Reward the useful discovery without endorsing the intrusion: prestige. | L4 |
| <a id="els-fh05"></a>**ELS-FH05 — The Champion's Black Talisman**<br>Target WV **+2** | Your military council receives a survivor's account of a warded champion who died when an enemy tried to possess his body. Elspeth's talisman destroyed the intruder, leaving the council both a defence to study and a family to compensate. | **A.** Train ward-keepers: military knowledge and innovativeness.<br>**B.** Fund the champion's dependants: prestige with expense.<br>**C.** Preserve the preparation records: administrative knowledge. | L6 |

#### Friendly/neutral — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="els-fa01"></a>**ELS-FA01 — A Tower in Another Language**<br>Target WV **+1** | Local scholars report that Elspeth opened a sealed archive and removed a lethal curse before departing with one disputed object. Her remaining notes explain several previously unreadable inscriptions. | **A.** Translate and publish the notes: innovativeness.<br>**B.** Settle ownership claims and restore the archive: development.<br>**C.** Keep the knowledge within the court: administrative gains. | L1 |
| <a id="els-fa02"></a>**ELS-FA02 — The Marsh's Borrowed Dead**<br>Target WV **+2** | Your governor reports that Elspeth dismantled a shambling mass of stolen corpses outside a foreign burial ground. Families seek their remains while officials argue over who pays for identification. | **A.** Fund identification and burial: prestige and development with expense.<br>**B.** Recover the desecrators' property: income.<br>**C.** Study the binding method under guard: administrative knowledge. | L2 |
| <a id="els-fa03"></a>**ELS-FA03 — A Diplomat with No Reflection**<br>Target WV **+1** | Your chamberlain receives Elspeth's evidence that a charming visitor has been enthralling officials. The visitor fled, leaving gifts that can be reclaimed once their enchantments are removed. | **A.** Disentangle the agreements: diplomatic knowledge.<br>**B.** Purify and sell the gifts: income. | L3 |
| <a id="els-fa04"></a>**ELS-FA04 — The Dragon Above the Caravan**<br>Target WV **+2** | Caravan survivors report Elspeth intercepting a hostile dragon-rider before it reached their camp. Her victory was costly, but recovered baggage includes the raiders' route plans. | **A.** Prepare safer routes: trade and military knowledge.<br>**B.** Reward rescuers and survivors: prestige.<br>**C.** Sell unclaimed military cargo: income. | L5 |
| <a id="els-fa05"></a>**ELS-FA05 — The Possessor's Empty Vessel**<br>Target WV **+2** | Your physician reports that Elspeth laid a trap inside a warded body intended for possession by a hostile spirit. The trap consumed the vessel, saving the ward but leaving an ethical dispute. | **A.** Approve tightly supervised safeguards: innovativeness.<br>**B.** Compensate those affected and close the practice: prestige.<br>**C.** Preserve the warning for magistrates: administrative knowledge. | L6 |

#### Enemy — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="els-eh01"></a>**ELS-EH01 — The Garden Gives Up Its Prisoners**<br>Target WV **−1** | Your custodian reports that Elspeth entered a requisitioned mortuary and released spirits bound to official service. The records she left expose who ordered the bindings. | **A.** Replace the lost services: treasury loss.<br>**B.** Audit the institution: administrative power loss.<br>**C.** Suppress the records: prestige loss. | L1 |
| <a id="els-eh02"></a>**ELS-EH02 — The Hulk That Fell Apart**<br>Target WV **−2** | Your necromantic engineer reports that Elspeth destroyed a corpse-built siege creature in its assembly yard. Contaminated remains now block the workshops and frighten the labour force. | **A.** Fund safe clearance: treasury loss.<br>**B.** Abandon the yard: devastation.<br>**C.** Divert specialists to rebuild the project: military power loss. | L2 |
| <a id="els-eh03"></a>**ELS-EH03 — The Courtier's Broken Hold**<br>Target WV **−1** | Your governor reports that Elspeth broke a vampire agent's influence over provincial officials. Several agreements collapsed with the enchantment, and their beneficiaries are demanding enforcement. | **A.** Renegotiate the agreements: diplomatic power loss.<br>**B.** Buy settlements: treasury loss. | L3 |
| <a id="els-eh04"></a>**ELS-EH04 — The Tower We Could Not Search**<br>Target WV **−1** | Your officers return from an attempted search of Elspeth's refuge unable to describe the interior. Their prisoners escaped during the confusion, and the warrant has become an object of ridicule. | **A.** Review the operation: administrative power loss.<br>**B.** Restore the officers' standing through compensation: treasury loss.<br>**C.** Accept the public embarrassment: prestige loss. | L4 |
| <a id="els-eh05"></a>**ELS-EH05 — The Ward That Burned Its Master**<br>Target WV **−2** | Your court sorcerer tried to occupy a body prepared by Elspeth and triggered a hidden ward. The resulting blast destroyed the ritual chamber and much of its equipment. | **A.** Rebuild elsewhere: treasury loss.<br>**B.** Seal the chamber: devastation.<br>**C.** Suspend the programme and purge its records: administrative power loss. | L6 |

#### Enemy — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="els-ea01"></a>**ELS-EA01 — The Collector's Missing Prize**<br>Target WV **−1** | Your treasury keeper reports that Elspeth removed an artefact from a foreign collection before a planned display. She left proof of its danger, but no explanation of where she took it. | **A.** Cancel the display: prestige loss.<br>**B.** Reimburse its sponsors: treasury loss.<br>**C.** Investigate the acquisition: administrative power loss. | L1 |
| <a id="els-ea02"></a>**ELS-EA02 — The Mire Engine's Ruin**<br>Target WV **−2** | Your frontier commander reports that Elspeth shattered a corpse-powered engine on a marsh road. The wreckage traps supply wagons, and labourers refuse to handle its remains. | **A.** Pay specialist crews: treasury loss.<br>**B.** Abandon the trapped supplies: military power loss.<br>**C.** Force clearance through nearby land: devastation. | L2 |
| <a id="els-ea03"></a>**ELS-EA03 — The Ambassador Unmasked**<br>Target WV **−1** | Your envoy reports that Elspeth exposed a vampire operative travelling under diplomatic protection. The operative escaped her attack, but the host's officials now hold the forged credentials. | **A.** Repair relations: diplomatic power loss.<br>**B.** Compensate the offended authorities: treasury loss.<br>**C.** Repudiate the mission: prestige loss. | L3 |
| <a id="els-ea04"></a>**ELS-EA04 — A Rider Falls from the Clouds**<br>Target WV **−2** | Your scouts report that Elspeth defeated a dragon-mounted officer above an outlying fortress. The fallen mount destroyed storehouses before she vanished from the scene. | **A.** Replenish stores and defences: treasury loss.<br>**B.** Abandon the damaged buildings: devastation.<br>**C.** Reassign troops to replace aerial support: military power loss. | L5 |
| <a id="els-ea05"></a>**ELS-EA05 — The Trap in the Captive**<br>Target WV **−2** | Your interrogator reports that a prisoner selected for a possession ritual carried Elspeth's concealed ward. Its activation destroyed the apparatus and scattered the officers attending the demonstration. | **A.** Pay for recovery and replacements: treasury loss.<br>**B.** Investigate every surviving order: administrative power loss.<br>**C.** Conceal the failure at court: prestige and military losses. | L6 |

<a id="catalogue-wul"></a>

### 10.9. Markus Wulfhart

**Fame:** 4/5. **Start:** **Copher — Z16**, province **988** (Araby). **Enemy profile:** A, as defined in section 5. **Home:** The Empire.

#### Lore coverage

| Lore reference | Exploit or background and chronology | Concepts representing it |
|---|---|---|
| **L1** | Blinded and killed the Drakwald Cyclops after it destroyed his home; undated. | [WUL-FH01](#wul-fh01), [WUL-FH04](#wul-fh04), [WUL-FA02](#wul-fa02), [WUL-EH01](#wul-eh01), [WUL-EH04](#wul-eh04), [WUL-EA01](#wul-ea01), [WUL-EA05](#wul-ea05) |
| **L2** | Imperial recognition, elite scouts, and continued protection of settlements through monster hunting. | [WUL-FH02](#wul-fh02), [WUL-FH04](#wul-fh04), [WUL-FH05](#wul-fh05), [WUL-FA01](#wul-fa01), [WUL-FA04](#wul-fa04), [WUL-FA05](#wul-fa05), [WUL-EH02](#wul-eh02), [WUL-EH05](#wul-eh05), [WUL-EA02](#wul-ea02), [WUL-EA04](#wul-ea04), [WUL-EA05](#wul-ea05) |
| **L3** | Local mod history: hunted the Dragon Ogre-led Beasts of Telldros across Norsca in 2501 without subduing them. | [WUL-FH03](#wul-fh03), [WUL-FA03](#wul-fa03), [WUL-EH03](#wul-eh03), [WUL-EA03](#wul-ea03) |

#### Friendly/neutral — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="wul-fh01"></a>**WUL-FH01 — The Arrow in the Giant's Eye**<br>Target WV **+2** | Your forester reports that Wulfhart blinded a giant threatening woodland villages and finished it on foot. The recovered captives carry stores taken from several missing caravans. | **A.** Return supplies to the villages: development.<br>**B.** Reward the hunters: manpower and prestige.<br>**C.** Sell unclaimed goods: income. | L1 |
| <a id="wul-fh02"></a>**WUL-FH02 — The Emperor's Scoutbook**<br>Target WV **+1** | Your captain receives a field notebook Wulfhart left after correcting a patrol's tracking errors. Several recruits have already used its methods to find missing travellers. | **A.** Train selected scouts: professionalism.<br>**B.** Copy the notebook widely: military knowledge.<br>**C.** Recognize the rescuers: prestige. | L2 |
| <a id="wul-fh03"></a>**WUL-FH03 — Tracks from the Northern Hunt**<br>Target WV **+1** | Your watch receives Wulfhart's warning that creatures resembling those he pursued in Norsca have crossed into the province. His scouts recovered abandoned livestock but did not catch their leaders. | **A.** Organize an informed watch: military knowledge.<br>**B.** Shelter exposed herds: production protection.<br>**C.** Compensate and relocate frontier families: development with expense. | L3 |
| <a id="wul-fh04"></a>**WUL-FH04 — The Village He Would Not Leave**<br>Target WV **+2** | Your governor reports that Wulfhart stayed with an exposed settlement after its paid guard withdrew. He killed the predator attacking its fields, leaving villagers willing to rebuild together. | **A.** Support reconstruction: development.<br>**B.** Enlist experienced volunteers: manpower.<br>**C.** Reward the village's cooperation: prestige and administrative knowledge. | L1, L2 |
| <a id="wul-fh05"></a>**WUL-FH05 — A Trophy with a Tax Receipt**<br>Target WV **+1** | Your excise officer tried to confiscate a beast Wulfhart had slain for villagers. The hunter departed after leaving proof that the officer had collected protection money without providing guards. | **A.** Repay victims from seized funds: prestige.<br>**B.** Reform the patrol levy: administrative knowledge. | L2 |

#### Friendly/neutral — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="wul-fa01"></a>**WUL-FA01 — A Beast No Bestiary Names**<br>Target WV **+2** | Your court receives a strange carcass from Wulfhart's latest hunt. Local guides say it attacked caravans, while scholars disagree over whether its valuable glands are poisonous. | **A.** Fund supervised dissection: innovativeness.<br>**B.** Sell safe parts through licensed merchants: income.<br>**C.** Reward the guides and secure the route: trade and prestige. | L2 |
| <a id="wul-fa02"></a>**WUL-FA02 — The Cyclops Beyond the Desert**<br>Target WV **+1** | A caravan guard reports that Wulfhart used an eye-shot and close pursuit to bring down a giant in unfamiliar terrain. The surviving guide offers a reliable map of the creature's hunting grounds. | **A.** Purchase the map: diplomatic knowledge.<br>**B.** Protect the cleared route: trade.<br>**C.** Honour the survivors: prestige. | L1 |
| <a id="wul-fa03"></a>**WUL-FA03 — The Northern Beasts' Broker**<br>Target WV **+2** | Your customs officers receive Wulfhart's evidence that a merchant has been supplying a monstrous northern warband. The merchant escaped, but ledgers and concealed stores remain. | **A.** Seize the stores: income.<br>**B.** Dismantle the broker network: diplomatic knowledge and prestige.<br>**C.** Fund a cautious follow-up: military knowledge. | L3 |
| <a id="wul-fa04"></a>**WUL-FA04 — The Local Hunters' Dispute**<br>Target WV **+1** | A guild petitions after Wulfhart bypassed its exclusive hunting rights to rescue missing children. He left a practical account of the rescue, and the families refuse to surrender the recovered goods. | **A.** Reform the licence: administrative knowledge.<br>**B.** Compensate the guild and train volunteers: military knowledge with expense. | L2 |
| <a id="wul-fa05"></a>**WUL-FA05 — A Hunt That Ended at the Shrine**<br>Target WV **+1** | Your magistrate reports that Wulfhart wounded a dangerous beast but stopped pursuit when it entered a locally protected refuge. He left a safe containment plan rather than force a religious confrontation. | **A.** Fund the containment: development.<br>**B.** Train shrine wardens: manpower.<br>**C.** Record the compromise as policy: diplomatic knowledge. | L2 |

#### Enemy — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="wul-eh01"></a>**WUL-EH01 — The Beast Pen in the Forest**<br>Target WV **−2** | Your military keeper reports that Wulfhart killed a giant being held for battlefield service. Freed labourers escaped with him, and the damaged pen now threatens adjoining buildings. | **A.** Repair and replace the asset: treasury loss.<br>**B.** Abandon the enclosure: devastation.<br>**C.** Substitute infantry units: military power loss. | L1 |
| <a id="wul-eh02"></a>**WUL-EH02 — The Scouts Who Knew Too Much**<br>Target WV **−1** | Your patrol commander reports that Wulfhart exposed the routes used to seize villagers for forced service. The hunters escaped after guiding detainees through gaps in the cordon. | **A.** Reorganize the patrol system: military power loss.<br>**B.** Compensate exposed households: treasury loss.<br>**C.** Suppress their testimony: prestige loss. | L2 |
| <a id="wul-eh03"></a>**WUL-EH03 — Telldros' Lost Convoy**<br>Target WV **−2** | Your supply officer reports that Wulfhart ambushed goods destined for a monstrous warband. He could not catch its leaders, but destroyed the stores and released their intended captives. | **A.** Replace the shipment: treasury loss.<br>**B.** Cancel the arrangement: military and prestige losses.<br>**C.** Requisition local goods: devastation. | L3 |
| <a id="wul-eh04"></a>**WUL-EH04 — A Head Above the Village Gate**<br>Target WV **−1** | Your governor reports that Wulfhart left the head of your appointed beast-keeper's predator above a village gate. The display has emboldened residents to refuse another levy. | **A.** Negotiate a revised levy: administrative power loss.<br>**B.** Offer compensation: treasury loss. | L1 |
| <a id="wul-eh05"></a>**WUL-EH05 — The Empty Hunting Lodge**<br>Target WV **−1** | Your commissioner found Wulfhart's supposed refuge empty and the lodge's former prisoners already gone. A scout manual left behind exposes the complacency of your officers. | **A.** Retrain the guard: military power loss.<br>**B.** Investigate the lodge staff: administrative power loss.<br>**C.** Conceal the failed arrest: prestige loss. | L2 |

#### Enemy — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="wul-ea01"></a>**WUL-EA01 — The War Beast's Single Wound**<br>Target WV **−2** | Your frontier commander reports that Wulfhart killed an imported giant with a carefully placed arrow and a finishing attack. Its handlers fled with part of the purchase money. | **A.** Buy replacement forces: treasury loss.<br>**B.** Pursue the handlers: military power loss.<br>**C.** Reduce the frontier commitment: prestige and administrative losses. | L1 |
| <a id="wul-ea02"></a>**WUL-EA02 — The Foreign Trophy Market**<br>Target WV **−1** | Your market inspector reports that Wulfhart exposed a trade in live man-eaters protected by officials. He freed the handlers' captives and left incriminating bills of sale. | **A.** Refund illicit buyers quietly: treasury loss.<br>**B.** Prosecute the officials: administrative power loss.<br>**C.** Refuse the accusations: prestige loss. | L2 |
| <a id="wul-ea03"></a>**WUL-EA03 — The Trail Back to Norsca**<br>Target WV **−2** | Your governor learns that Wulfhart traced a foreign monster shipment to brokers serving a northern warband. He burned the cages after an escape, and traders now demand compensation. | **A.** Pay the traders: treasury loss.<br>**B.** Close the route and investigate: diplomatic power loss.<br>**C.** Abandon the damaged holding ground: devastation. | L3 |
| <a id="wul-ea04"></a>**WUL-EA04 — The Guide Who Changed Sides**<br>Target WV **−1** | A local guide led Wulfhart to your scouts instead of the beast they claimed to be hunting. The scouts' prisoners escaped, and the guide has published their orders. | **A.** Disavow and reorganize the patrol: military power loss.<br>**B.** Compensate victims: treasury loss. | L2 |
| <a id="wul-ea05"></a>**WUL-EA05 — The Governor's Private Menagerie**<br>Target WV **−1** | Your governor reports that Wulfhart entered his private menagerie after a creature escaped into town. The hunter killed the threat and departed with witnesses to the governor's negligence. | **A.** Fund relief: treasury loss.<br>**B.** Remove and investigate the governor: administrative power loss.<br>**C.** Defend the collection: prestige loss. | L1, L2 |

<a id="catalogue-gof"></a>

### 10.10. Gotrek Gurnisson and Felix Jaeger

**Fame:** 5/5. **Start:** **Reikland — A01**, East Altdorf **1** (The Empire). **Enemy profile:** A, as defined in section 5. **Home:** The Empire and western Dwarf mountain ranges.

#### Lore coverage

| Lore reference | Exploit or background and chronology | Concepts representing it |
|---|---|---|
| **L1** | Window Tax riot rescue in Altdorf and Felix's oath to record Gotrek's doom; around 2502. | [GOF-FH01](#gof-fh01), [GOF-FH05](#gof-fh05), [GOF-FA05](#gof-fa05), [GOF-EH01](#gof-eh01), [GOF-EH05](#gof-eh05) |
| **L2** | Thwarted Thanquol's attack on Nuln in Skavenslayer; chronology varies. | [GOF-FH02](#gof-fh02), [GOF-EH02](#gof-eh02), [GOF-EA05](#gof-ea05) |
| **L3** | Spirit of Grungni expedition to Karak Dum; later adventure. No duplicate Malakai appearance. | [GOF-FH05](#gof-fh05), [GOF-FA02](#gof-fa02), [GOF-EA02](#gof-ea02) |
| **L4** | Fought and defeated a Bloodthirster during their adventures; later inspiration. | [GOF-FH04](#gof-fh04), [GOF-FA03](#gof-fa03), [GOF-EH04](#gof-eh04), [GOF-EA03](#gof-ea03) |
| **L5** | Slew a dragon in the World's Edge Mountains; later inspiration. | [GOF-FH03](#gof-fh03), [GOF-FA04](#gof-fa04), [GOF-EH03](#gof-eh03), [GOF-EA04](#gof-ea04) |
| **L6** | Survived the siege of Praag and helped defeat its attackers; later inspiration. | [GOF-FA01](#gof-fa01), [GOF-EA01](#gof-ea01) |

#### Friendly/neutral — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="gof-fh01"></a>**GOF-FH01 — The Window Tax Witness**<br>Target WV **+1** | Your magistrate reports that Gotrek pulled a young protester from charging guards while Felix recorded the incident. The pair disappeared into a tavern, leaving witnesses prepared to expose an abusive collector. | **A.** Review and reform the collection: administrative knowledge.<br>**B.** Compensate victims from recovered fees: prestige.<br>**C.** Publish a moderated account: diplomatic knowledge. | L1 |
| <a id="gof-fh02"></a>**GOF-FH02 — Ratmen Beneath the Warehouses**<br>Target WV **+2** | Your watch reports collapsed cellars, rescued townsfolk and evidence of a ratman plot uncovered by Gotrek and Felix. The pair escaped into the catacombs while officials argued over whether to acknowledge the threat. | **A.** Send investigators after the evidence: military knowledge.<br>**B.** Restore the warehouses from recovered goods: development.<br>**C.** Honour the rescue publicly: prestige. | L2 |
| <a id="gof-fh03"></a>**GOF-FH03 — A Dragon's Unclaimed Hoard**<br>Target WV **+2** | Mountain wardens report that Gotrek and Felix killed a dragon threatening a pass. Felix left an inventory of recovered property, but several towns now claim the same treasure. | **A.** Return identifiable goods: development and prestige.<br>**B.** Auction unclaimed treasure: income.<br>**C.** Pay wardens to secure the pass: trade with expense. | L5 |
| <a id="gof-fh04"></a>**GOF-FH04 — The Blood on the Chapel Floor**<br>Target WV **+2** | Your priest reports that Gotrek destroyed a summoned daemon while Felix led worshippers out through the crypt. The chapel is damaged, but the cult's hidden accounts survived. | **A.** Rebuild and investigate: administrative knowledge with expense.<br>**B.** Confiscate the cult's wealth: income.<br>**C.** Reward the rescuers' local helpers: manpower and prestige. | L4 |
| <a id="gof-fh05"></a>**GOF-FH05 — The Chronicle Nobody Commissioned**<br>Target WV **+1** | Your archivist receives Felix's account of a dangerous expedition and a request to identify rescued heirlooms. Gotrek refuses an audience, while merchants argue over the cost of distributing the testimony. | **A.** Sponsor a public archive: prestige.<br>**B.** Return the heirlooms diplomatically: diplomatic knowledge.<br>**C.** Sell a licensed edition: income. | L1, L3 |

#### Friendly/neutral — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="gof-fa01"></a>**GOF-FA01 — The Siege Survivors' Petition**<br>Target WV **+2** | Refugees report that Gotrek and Felix held a street during a foreign siege long enough for families to escape. The pair have moved on, leaving survivors and captured supplies at your border office. | **A.** Settle the survivors: development.<br>**B.** Recruit experienced defenders: manpower and military knowledge.<br>**C.** Fund their onward journey: prestige with expense. | L6 |
| <a id="gof-fa02"></a>**GOF-FA02 — The Airship's Returned Passengers**<br>Target WV **+2** | An expedition crew delivers survivors escorted from a lost hold by Gotrek and Felix. The pair travelled aboard a Dwarf airship; its captain requests a landing ground while officials inventory recovered tools. | **A.** Repair the landing ground and study the tools: development and innovativeness.<br>**B.** Buy the recovered equipment: military knowledge.<br>**C.** Help the survivors return home: prestige. | L3 |
| <a id="gof-fa03"></a>**GOF-FA03 — A Slayer in the Summoning Pit**<br>Target WV **+2** | Your scouts report that Gotrek killed a great daemon inside a ruined sanctuary while Felix rescued captives. The pair departed before your troops arrived, leaving a dangerous site and grateful witnesses. | **A.** Seal and document the sanctuary: administrative knowledge.<br>**B.** Return rescued property: development.<br>**C.** Reward the local guides: prestige and manpower. | L4 |
| <a id="gof-fa04"></a>**GOF-FA04 — The Wrong Dragon's Bones**<br>Target WV **+1** | Your customs office receives bones from a dragon the pair slew in unfamiliar country. Felix disputes a merchant's claim to the remains and has left sworn statements from the endangered villagers. | **A.** Recognize the villagers' rights: prestige.<br>**B.** Buy samples for scholars: innovativeness with expense. | L5 |
| <a id="gof-fa05"></a>**GOF-FA05 — A Riot in an Unfamiliar Tongue**<br>Target WV **+1** | A governor reports that Gotrek rescued Felix and several locals from a violent tax protest. Felix's translated account exposes a collector's fraud but embarrasses the town guard. | **A.** Recover the fraudulent takings: income.<br>**B.** Reform the guard's instructions: administrative knowledge.<br>**C.** Mediate compensation: diplomatic knowledge. | L1 |

#### Enemy — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="gof-eh01"></a>**GOF-EH01 — The Collector's Broken Escort**<br>Target WV **−1** | Your collector reports that Gotrek scattered his escort during a protest and Felix carried away the levy records. Witnesses are gathering around copies of the pair's accusations. | **A.** Refund disputed payments: treasury loss.<br>**B.** Investigate the escort: administrative power loss.<br>**C.** Suppress the account: prestige loss. | L1 |
| <a id="gof-eh02"></a>**GOF-EH02 — The Catacombs' Empty Cells**<br>Target WV **−2** | Your occupation officer reports that the pair broke into a concealed detention site while pursuing ratmen. Captives escaped, supplies burned, and Felix has taken evidence of official involvement. | **A.** Rebuild the damaged district: treasury loss.<br>**B.** Seal the lower passages: devastation.<br>**C.** Reorganize security before the evidence spreads: administrative and prestige losses. | L2 |
| <a id="gof-eh03"></a>**GOF-EH03 — The Beast We Had Purchased**<br>Target WV **−2** | Your commander reports that Gotrek killed a dragon held for military service while Felix released its handlers' prisoners. The pair escaped through the ruined pen. | **A.** Replace its military role: treasury loss.<br>**B.** Divert existing troops: military power loss.<br>**C.** Abandon the damaged compound: devastation. | L5 |
| <a id="gof-eh04"></a>**GOF-EH04 — The Summoner's Last Bargain**<br>Target WV **−2** | Your ritual officer reports that Gotrek destroyed the daemon meant to secure a local garrison. Felix led its intended offerings away, and the apparatus collapsed during the fight. | **A.** Rebuild conventional defences: treasury loss.<br>**B.** Close the ruined chamber: devastation.<br>**C.** Investigate the failed contract: administrative power loss. | L4 |
| <a id="gof-eh05"></a>**GOF-EH05 — The Book with Our Names in It**<br>Target WV **−1** | Your governor reports that Felix's account of a recent clash names officers involved in extortion. Gotrek protected the first public reading, then both vanished before an arrest could be organized. | **A.** Settle the victims' claims: treasury loss.<br>**B.** Remove implicated officials: administrative power loss.<br>**C.** Endure the circulation: prestige loss. | L1 |

#### Enemy — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="gof-ea01"></a>**GOF-EA01 — The Supply Street at the Siege**<br>Target WV **−2** | Your commander reports that Gotrek and Felix opened an escape route through your siege camp. Refugees fled with captured supplies, and the pair disappeared amid the traffic. | **A.** Replace the stores: treasury loss.<br>**B.** Reorganize the encirclement: military power loss.<br>**C.** Requisition nearby settlements: devastation. | L6 |
| <a id="gof-ea02"></a>**GOF-EA02 — The Airship Above the Prison**<br>Target WV **−2** | Your governor reports that the pair evacuated captives and stolen heirlooms aboard a passing expedition airship. Ground crews escaped after disabling the landing machinery used by your pursuers. | **A.** Repair the machinery and guard: treasury loss.<br>**B.** Abandon aerial interception: military power loss.<br>**C.** Conceal the loss of the heirlooms: prestige and administrative losses. | L3 |
| <a id="gof-ea03"></a>**GOF-EA03 — The Daemon's Broken Chain**<br>Target WV **−2** | Your overseer reports that Gotrek attacked a bound daemon while Felix cut its captives free. The surviving ritualists demand compensation for equipment they abandoned during the escape. | **A.** Replace the equipment: treasury loss.<br>**B.** Dismantle the programme: administrative power loss.<br>**C.** Leave the district to recover unaided: devastation. | L4 |
| <a id="gof-ea04"></a>**GOF-EA04 — A Trophy Stolen from the Court**<br>Target WV **−1** | Your governor displayed a dragon's hoard acquired from raiders. Gotrek and Felix identified stolen property among it, defeated the guards, and left with witnesses to the original theft. | **A.** Repay proven claims: treasury loss.<br>**B.** Investigate the purchase: administrative power loss.<br>**C.** Deny the evidence: prestige loss. | L5 |
| <a id="gof-ea05"></a>**GOF-EA05 — The Palace's Rat-Filled Cellar**<br>Target WV **−1** | Your chamberlain reports that the pair exposed a ratman passage beneath the provincial palace and wrecked the cellar while escaping. Their discovery also revealed secret payments made by palace staff. | **A.** Repair the cellar and repay victims: treasury loss.<br>**B.** Purge the compromised staff: administrative power loss.<br>**C.** Hide the scandal: prestige loss. | L2 |

<a id="catalogue-rep"></a>

### 10.11. Repanse de Lyonesse

**Fame:** 4/5. **Start:** **Lyonesse — A17**, Merton **284** (Bretonnia). **Enemy profile:** A, as defined in section 5. **Home:** Bretonnia.

#### Lore coverage

| Lore reference | Exploit or background and chronology | Concepts representing it |
|---|---|---|
| **L1** | In 2007, answered the Lady's vision, took a fallen knight's armour and a chapel sword and banner, and rallied defeated Lyonesse knights. | [REP-FH01](#rep-fh01), [REP-FH02](#rep-fh02), [REP-FH05](#rep-fh05), [REP-FA01](#rep-fa01), [REP-FA02](#rep-fa02), [REP-FA05](#rep-fa05), [REP-EH01](#rep-eh01), [REP-EH04](#rep-eh04), [REP-EA01](#rep-ea01), [REP-EA02](#rep-ea02), [REP-EA05](#rep-ea05) |
| **L2** | Relieved Couronne and beheaded the besieging Chaos commander in 2007; new relief actions echo this victory rather than repeat its named battle. | [REP-FH03](#rep-fh03), [REP-FA02](#rep-fa02), [REP-FA03](#rep-fa03), [REP-EH02](#rep-eh02), [REP-EH04](#rep-eh04), [REP-EA01](#rep-ea01), [REP-EA03](#rep-ea03) |
| **L3** | Received knighthood and the Dukedom of Lyonesse from Louis the Young; encounters draw on that legacy without restoring current ducal rule. | [REP-FH04](#rep-fh04), [REP-FH05](#rep-fh05), [REP-FA04](#rep-fa04), [REP-EH03](#rep-eh03), [REP-EH05](#rep-eh05), [REP-EA04](#rep-ea04) |

#### Friendly/neutral — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="rep-fh01"></a>**REP-FH01 — The Banner from the Chapel**<br>Target WV **+1** | Your bailiff reports that Repanse carried an old chapel banner into a village threatened by raiders, speaking of the Lady's vision that first sent her to war. Frightened retainers rallied behind her, and the chaplain now petitions for repairs to the damaged sanctuary. | **A.** Repair the chapel: prestige with expense.<br>**B.** Enlist the rallied volunteers: manpower.<br>**C.** Have veterans teach the village watch: army professionalism. | L1 |
| <a id="rep-fh02"></a>**REP-FH02 — The Armour in the Hayloft**<br>Target WV **+1** | Your steward reports that Repanse recovered a dead knight's armour from a corrupt collector and gave it to the family he had defended. Her account of her own humble calling has drawn witnesses to other abuses. | **A.** Hear the families' claims: administrative knowledge.<br>**B.** Recognize their service publicly: prestige.<br>**C.** Recover the collector's illicit proceeds: income. | L1 |
| <a id="rep-fh03"></a>**REP-FH03 — The Road to Couronne**<br>Target WV **+2** | Your marshal reports that Repanse broke a raiding force blocking a relief road, cutting down its champion before the convoy arrived. Veterans compare the rescue to Couronne, and several isolated settlements can now be supplied. | **A.** Restore the relief route: provincial recovery.<br>**B.** Reward the convoy's volunteer escort: manpower and prestige.<br>**C.** Study the breakthrough: army tradition. | L2 |
| <a id="rep-fh04"></a>**REP-FH04 — The Duchess Who Would Not Stay**<br>Target WV **+1** | Your seneschal reports that villagers asked Repanse to judge a dispute under the authority of her ancient dukedom. She settled the immediate violence but referred the lasting decision to your court and departed. | **A.** Confirm the mediated settlement: reduced local unrest.<br>**B.** Preserve her testimony in the court record: administrative knowledge.<br>**C.** Recognize both villages' cooperation: prestige. | L3 |
| <a id="rep-fh05"></a>**REP-FH05 — A Knight's Name on the Roll**<br>Target WV **+1** | Your herald reports that Repanse insisted a lowborn rescuer be recorded beside the knights he saved. She invoked her own knighthood under Louis the Young, leaving your officials to resolve the offended nobles' petitions. | **A.** Acknowledge the rescue: prestige.<br>**B.** Fund military instruction for the volunteer: army professionalism with expense.<br>**C.** Record the deed without altering rank: army tradition. | L1, L3 |

#### Friendly/neutral — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="rep-fa01"></a>**REP-FA01 — The Foreign Chapel's Refugees**<br>Target WV **+2** | Your governor reports that Repanse escorted captives out of a raiders' camp and sheltered them in a local sanctuary. Its unfamiliar priesthood has requested your help feeding the rescued families. | **A.** Settle the willing families: development with resettlement expense.<br>**B.** Reunite them with their communities: prestige.<br>**C.** Employ willing adults on public repairs: provincial recovery. | L1 |
| <a id="rep-fa02"></a>**REP-FA02 — The Banner Nobody Recognized**<br>Target WV **+1** | Your border commander reports that soldiers who could not understand Repanse's words followed her banner through a broken enemy line. Survivors have returned with a practical account of her signals and formations. | **A.** Adopt the useful signals: army professionalism.<br>**B.** Reward the returning soldiers: army tradition.<br>**C.** Display the captured standards: prestige. | L1, L2 |
| <a id="rep-fa03"></a>**REP-FA03 — The Champion at the Water Gate**<br>Target WV **+2** | Your governor reports that Repanse slew the champion holding a town's water gate and opened it for a relief convoy. Her companions have gone on, leaving captured supplies and competing petitions for their distribution. | **A.** Distribute the food: provincial recovery.<br>**B.** Provision the garrison: manpower.<br>**C.** Sell surplus stores to finance repairs: income. | L2 |
| <a id="rep-fa04"></a>**REP-FA04 — A Title That Buys No Passage**<br>Target WV **+1** | Your customs judge reports that Repanse refused a merchant's attempt to purchase privileges in her name as Duchess of Lyonesse. She left evidence of his forged letters, but claimed no authority over your officials. | **A.** Prosecute the forgeries: administrative knowledge.<br>**B.** Recover fraudulent fees: income.<br>**C.** Publish her testimony: prestige. | L3 |
| <a id="rep-fa05"></a>**REP-FA05 — The Fallen Knight's Foreign Grave**<br>Target WV **+1** | Your magistrate reports that Repanse recovered a traveller's armour from bandits and arranged his burial according to the family's wishes. The rescued retainers offer to teach your patrols what they learned during the pursuit. | **A.** Accept the patrol instruction: army tradition.<br>**B.** Return the heirlooms with an official escort: prestige.<br>**C.** Keep the reopened road supplied: local economic recovery. | L1 |

#### Enemy — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="rep-eh01"></a>**REP-EH01 — The Chapel We Had Sealed**<br>Target WV **−1** | Your governor reports that Repanse broke the seal on a confiscated chapel, raised its banner, and escorted detained villagers out through the guard cordon. Her followers have dispersed among sympathetic households. | **A.** Rebuild the cordon: treasury loss.<br>**B.** Negotiate the detainees' settlement: prestige loss.<br>**C.** Order a search that finds only abandoned camps: military power loss. | L1 |
| <a id="rep-eh02"></a>**REP-EH02 — The Relief Column We Missed**<br>Target WV **−2** | Your siege commander reports that Repanse killed his champion and forced a supply convoy through the blockade. Occupied villages are now openly repeating the story of Couronne. | **A.** Replace the lost stores and equipment: treasury loss.<br>**B.** Reorganize the blockade: military power loss.<br>**C.** Abandon damaged forward positions: local devastation. | L2 |
| <a id="rep-eh03"></a>**REP-EH03 — The Duke's Old Seal**<br>Target WV **−1** | Your tax officer reports that Repanse exposed forged orders bearing the seal of her former dukedom. Villagers have withheld the disputed payments and circulated copies of her declaration. | **A.** Refund the disputed levy: treasury loss.<br>**B.** Investigate the officials responsible: administrative power loss.<br>**C.** Enforce collection despite the evidence: prestige loss. | L3 |
| <a id="rep-eh04"></a>**REP-EH04 — Peasants Beneath the Banner**<br>Target WV **−2** | Your marshal reports that Repanse armed villagers from a captured depot and led them out of the district. A small band remains behind to resist your collectors, while she has already escaped pursuit. | **A.** Offer an amnesty and buy back the arms: treasury loss.<br>**B.** Contain the holdouts: a small, budgeted rebel rising.<br>**C.** Withdraw exposed collection teams: administrative power loss. | L1, L2 |
| <a id="rep-eh05"></a>**REP-EH05 — A Knighthood Denied**<br>Target WV **−1** | Your herald reports that Repanse publicly defended a prisoner condemned for claiming a knight's honours. She broke the escort, took the prisoner away, and invoked her own elevation by Louis the Young before a large crowd. | **A.** Compensate the defeated escort: treasury loss.<br>**B.** Revise the disputed judgment: administrative power loss.<br>**C.** Uphold the sentence in her absence: prestige loss. | L3 |

#### Enemy — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="rep-ea01"></a>**REP-EA01 — The Camp with Open Gates**<br>Target WV **−2** | Your overseer reports that Repanse broke into a labour camp and led its captives away beneath her banner. The gatehouse and the records of the camp's contracts were destroyed in the fighting. | **A.** Rebuild and audit the camp: treasury loss.<br>**B.** Reconstruct the missing records: administrative power loss.<br>**C.** Leave the ruined site abandoned: devastation. | L1, L2 |
| <a id="rep-ea02"></a>**REP-EA02 — The Shrine's Broken Trophy**<br>Target WV **−1** | Your governor reports that Repanse destroyed a trophy taken from a plundered sanctuary and returned its fragments to local custodians. Your guards were disarmed before they could stop her. | **A.** Compensate the guards and custodians: treasury loss.<br>**B.** Investigate the original plunder: administrative power loss.<br>**C.** Dismiss the incident publicly: prestige loss. | L1 |
| <a id="rep-ea03"></a>**REP-EA03 — A Couronne in Foreign Soil**<br>Target WV **−2** | Your field officer reports that Repanse cut down the champion enforcing your occupation and opened a passage for refugees. Their departure has carried accounts of the garrison's abuses beyond the frontier. | **A.** Replace the damaged occupation force: treasury loss.<br>**B.** Review its command: military power loss.<br>**C.** Try to contain the testimony: prestige and administrative losses. | L2 |
| <a id="rep-ea04"></a>**REP-EA04 — The Knight's Stolen Name**<br>Target WV **−1** | Your customs office reports that Repanse exposed a slave broker using her name and supposed ducal protection. She freed his prisoners before the watch arrived, leaving your officials implicated by their signatures. | **A.** Compensate those harmed by the contracts: treasury loss.<br>**B.** Purge the compromised registry: administrative power loss.<br>**C.** Defend the officials' conduct: prestige loss. | L3 |
| <a id="rep-ea05"></a>**REP-EA05 — The Banner Beyond the Frontier**<br>Target WV **−1** | Your commander reports that Repanse scattered a patrol holding a group of pilgrims and escorted them toward a foreign border. She left the patrol's weapons stacked around its officer's broken standard. | **A.** Replace the weapons before rumours spread: treasury loss.<br>**B.** Discipline the officer: military power loss.<br>**C.** Let the humiliation pass: prestige loss. | L1 |

<a id="catalogue-sie"></a>

### 10.12. Sienna Fuegonasus

**Fame:** 4/5. **Start:** **Magritta — A41**, province **553** (Estalia/Tilea). **Enemy profile:** A, as defined in section 5. **Home:** Estalia and the Empire.

#### Lore coverage

| Lore reference | Exploit or background and chronology | Concepts representing it |
|---|---|---|
| **L1** | Trained under Thyrus Gormann at the Bright College, then left its discipline; the useful and dangerous sides of Aqshy shape these incidents. | [SIE-FH01](#sie-fh01), [SIE-FH03](#sie-fh03), [SIE-FH05](#sie-fh05), [SIE-FA01](#sie-fa01), [SIE-EH01](#sie-eh01), [SIE-EH02](#sie-eh02), [SIE-EH05](#sie-eh05), [SIE-EA01](#sie-ea01), [SIE-EA04](#sie-ea04) |
| **L2** | Later went from prisoner to a member of the Ubersreik heroes and fought Reikland's invaders; these are early echoes, not claims that the later campaign has occurred. | [SIE-FH02](#sie-fh02), [SIE-FH03](#sie-fh03), [SIE-FA02](#sie-fa02), [SIE-FA04](#sie-fa04), [SIE-EH01](#sie-eh01), [SIE-EH02](#sie-eh02), [SIE-EH03](#sie-eh03), [SIE-EA01](#sie-ea01), [SIE-EA02](#sie-ea02), [SIE-EA05](#sie-ea05) |
| **L3** | Later confronted her twin Sofia in the story leading into the optional Necromancer career; represent the necromantic double and its temptation without changing this wandering Bright Wizard into a necromancer. | [SIE-FH04](#sie-fh04), [SIE-FA03](#sie-fa03), [SIE-FA05](#sie-fa05), [SIE-EH04](#sie-eh04), [SIE-EA03](#sie-ea03) |

#### Friendly/neutral — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="sie-fh01"></a>**SIE-FH01 — Thyrus's Marginal Notes**<br>Target WV **+1** | Your guild reports that Sienna corrected a dangerous furnace design using lessons she attributes to Thyrus Gormann. She quarrelled with its masters over supervision and left before the successful test was complete. | **A.** Copy the corrected design: innovativeness.<br>**B.** Fund its use in a workshop: production development with expense.<br>**C.** Recognize the guild's safer practice: prestige. | L1 |
| <a id="sie-fh02"></a>**SIE-FH02 — The Prisoner's Burning Rescue**<br>Target WV **+2** | Your watch captain reports that Sienna, being escorted for questioning, broke her restraints when attackers trapped civilians in a cellar. She burned through the obstruction and helped the escort escape, then disappeared herself. | **A.** Pardon the incident and support the survivors: prestige.<br>**B.** Train the watch from their account: army professionalism.<br>**C.** Use recovered supplies to rebuild the cellar: provincial recovery. | L2 |
| <a id="sie-fh03"></a>**SIE-FH03 — The Fire in the Grain Store**<br>Target WV **+1** | Your magistrate reports that Sienna burned an infested store before its vermin could reach the public granary. Watchmen who tried to arrest her instead helped pull workers clear; the saved grain is now under official seal. | **A.** Release the grain to the district: local recovery.<br>**B.** Retain a reserve for the garrison: manpower.<br>**C.** Investigate how the infestation began: administrative knowledge. | L1, L2 |
| <a id="sie-fh04"></a>**SIE-FH04 — The Sister in the Testimony**<br>Target WV **+1** | Your investigator receives conflicting descriptions of a woman resembling Sienna near disturbed graves. Sienna has burned a necromantic cache and left a warning naming her twin Sofia; this early echo does not assume their later confrontation has happened. | **A.** Examine the surviving evidence: innovativeness.<br>**B.** Correct the mistaken accusation: prestige.<br>**C.** Fund secure burials and patrols: reduced local unrest with expense. | L3 |
| <a id="sie-fh05"></a>**SIE-FH05 — The Workshop's Unwelcome Miracle**<br>Target WV **+1** | Your smiths petition after Sienna used Aqshy to finish a difficult casting, cracked the roof tiles, and walked out during the ensuing argument. The casting survived and the apprentices recorded the process. | **A.** Buy the apprentices' notes: innovativeness with expense.<br>**B.** Install the finished casting in public works: local economic recovery.<br>**C.** Sell it and settle the repair claims: income. | L1 |

#### Friendly/neutral — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="sie-fa01"></a>**SIE-FA01 — A Furnace with No Shared Language**<br>Target WV **+1** | Your provincial engineer reports that Sienna and local smiths overcame a language barrier by drawing furnace diagrams in soot. The trial produced useful metal, although its heat drove officials out of the building. | **A.** Translate and circulate the diagrams: innovativeness.<br>**B.** Support a safer furnace: production development with expense.<br>**C.** Purchase the trial output: military supplies. | L1 |
| <a id="sie-fa02"></a>**SIE-FA02 — The Captive Who Cleared the Road**<br>Target WV **+2** | Your governor reports that Sienna was detained for carrying unfamiliar magical tools, then rescued the same guards when raiders attacked their convoy. Survivors returned with recovered cargo and a request to clear her name. | **A.** Return the cargo and recognize the guards: prestige.<br>**B.** Use unclaimed stores for relief: provincial recovery.<br>**C.** Commission their account of the ambush: army tradition. | L2 |
| <a id="sie-fa03"></a>**SIE-FA03 — The Foreign Pyre**<br>Target WV **+1** | Your harbour magistrate reports that Sienna burned a concealed shipment of corpse-raising reagents. Her warning mentions Sofia, but local witnesses had mistaken the two women for one person. | **A.** Preserve samples from the unburned crates: innovativeness.<br>**B.** Publish corrected witness statements: prestige.<br>**C.** Return the traffickers' stolen goods: reduced local unrest. | L3 |
| <a id="sie-fa04"></a>**SIE-FA04 — The Bridge of Sparks**<br>Target WV **+2** | Your commander reports that Sienna held a narrow bridge with fire while a mixed group of travellers brought civilians to safety. The strangers have separated, leaving your officials to house the rescued families. | **A.** Offer temporary homes: provincial recovery with expense.<br>**B.** Hire willing survivors as scouts: manpower.<br>**C.** Record the defence for officers: army tradition. | L2 |
| <a id="sie-fa05"></a>**SIE-FA05 — The Invitation She Burned**<br>Target WV **+1** | Your customs officer reports that Sienna destroyed a letter offering forbidden instruction in exchange for stolen bodies. She left its seal and a sketch of the courier, warning that the invitation was meant to exploit her family's history. | **A.** Trace the courier: administrative knowledge.<br>**B.** Study the seal safely: innovativeness.<br>**C.** Expose the traffickers to their victims: prestige. | L3 |

#### Enemy — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="sie-eh01"></a>**SIE-EH01 — The Powder Store's Red Dawn**<br>Target WV **−2** | Your quartermaster reports that Sienna set fire to ammunition stored beside captives taken from nearby villages. The captives escaped through a breach she burned in the outer wall. | **A.** Replace the lost ammunition: treasury loss.<br>**B.** Redistribute existing stocks: military power loss.<br>**C.** Abandon the damaged magazine: devastation. | L1, L2 |
| <a id="sie-eh02"></a>**SIE-EH02 — The Escort That Lost Its Prisoner**<br>Target WV **−1** | Your magistrate reports that guards attempted to chain Sienna after recognizing her college training. She burned the restraints, released other detainees, and vanished into the smoke. | **A.** Replace the escort's equipment: treasury loss.<br>**B.** Investigate its orders: administrative power loss.<br>**C.** Conceal the humiliating escape: prestige loss. | L1, L2 |
| <a id="sie-eh03"></a>**SIE-EH03 — The Grain We Could Not Issue**<br>Target WV **−2** | Your supply officer reports that Sienna burned a stockpile prepared with plague-tainted vermin for distribution into a rival district. Workers escaped, but the operation's surviving records now circulate among witnesses. | **A.** Replace the stores conventionally: treasury loss.<br>**B.** Reorganize the exposed operation: administrative power loss.<br>**C.** Abandon the contaminated compound: devastation. | L2 |
| <a id="sie-eh04"></a>**SIE-EH04 — The Wrong Sister's Warrant**<br>Target WV **−1** | Your governor reports that an arrest warrant intended for a necromancer with Sienna's likeness brought her to your mortuary. She destroyed its hidden experiments and left the warrant pinned to a scorched door. | **A.** Rebuild the damaged facilities: treasury loss.<br>**B.** Investigate the false identity trail: administrative power loss.<br>**C.** Deny the experiments existed: prestige loss. | L3 |
| <a id="sie-eh05"></a>**SIE-EH05 — The Lesson the Guild Rejected**<br>Target WV **−1** | Your foundry master reports that Sienna recognized coercive production practices and ruined the machinery driving them. Her chalk diagrams explain exactly which corners the guild had cut. | **A.** Repair the machinery properly: treasury loss.<br>**B.** Reorganize the foundry's supervision: administrative power loss.<br>**C.** Blame an unexplained accident: prestige loss. | L1 |

#### Enemy — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="sie-ea01"></a>**SIE-EA01 — The Arsenal's Failed Arrest**<br>Target WV **−2** | Your commander reports that an attempt to seize Sienna inside a provincial arsenal ended in a spreading fire. Labourers fled with her assistance, and the pursuers returned without their prisoner. | **A.** Replace the damaged stores: treasury loss.<br>**B.** Reassign troops to temporary depots: military power loss.<br>**C.** Leave the burnt compound closed: devastation. | L1, L2 |
| <a id="sie-ea02"></a>**SIE-EA02 — The Ship with the Empty Hold**<br>Target WV **−1** | Your customs officer reports that Sienna burned the locks from a captive transport and destroyed its restraining equipment. The released prisoners reached shore while the crew tried to contain the fire. | **A.** Repair the transport: treasury loss.<br>**B.** Audit the failed watch: administrative power loss.<br>**C.** Abandon the claim to its passengers: prestige loss. | L2 |
| <a id="sie-ea03"></a>**SIE-EA03 — A Necromancer's Rejected Gift**<br>Target WV **−1** | Your collector reports that Sienna destroyed a manuscript offered as the work of her twin. The flames also consumed records of the collector's dealings in forbidden remains, leaving angry suppliers at your door. | **A.** Settle the outstanding claims: treasury loss.<br>**B.** Reconstruct the lost records: administrative power loss.<br>**C.** Repudiate the collector publicly: prestige loss. | L3 |
| <a id="sie-ea04"></a>**SIE-EA04 — The Furnace Turned Outward**<br>Target WV **−2** | Your overseer reports that Sienna reversed a forced-labour foundry's magical draft, blasting open its holding yard. Its skilled workers escaped with tools and account books. | **A.** Hire replacements and repair the works: treasury loss.<br>**B.** Redistribute surviving workshops' capacity: administrative power loss.<br>**C.** Abandon the ruined yard: devastation. | L1 |
| <a id="sie-ea05"></a>**SIE-EA05 — The Witnesses in the Smoke**<br>Target WV **−1** | Your governor reports that Sienna covered a group of fugitives with a wall of flame while they carried evidence out of a seized archive. The provincial guard cannot explain how an apparent prisoner became the organizer of the escape. | **A.** Compensate the archive staff: treasury loss.<br>**B.** Reconstruct the missing intelligence: administrative power loss.<br>**C.** Dismiss the fugitives' allegations: prestige loss. | L2 |

<a id="catalogue-mal"></a>

### 10.13. Malakai Makaisson

**Fame:** 4/5. **Start:** **Kislev — A29**, Erengrad **332** (Northern Old World). **Enemy profile:** A, as defined in section 5. **Home:** Western Dwarf mountain ranges.

#### Lore coverage

| Lore reference | Exploit or background and chronology | Concepts representing it |
|---|---|---|
| **L1** | Built the Unsinkable ironclad, which sank; salvage and safety experiments recall this failed invention. | [MAL-FH01](#mal-fh01), [MAL-FA02](#mal-fa02), [MAL-EH02](#mal-eh02), [MAL-EA02](#mal-ea02) |
| **L2** | Built the Undestructible airship, which exploded; these disasters brought disgrace and the Slayer oath. | [MAL-FH02](#mal-fh02), [MAL-FH04](#mal-fh04), [MAL-FA04](#mal-fa04), [MAL-EH03](#mal-eh03), [MAL-EH04](#mal-eh04), [MAL-EA04](#mal-ea04), [MAL-EA05](#mal-ea05) |
| **L3** | Later built and piloted the Spirit of Grungni on the Karak Dum expedition; early incidents use prototypes, preliminary trials, and rescue motifs rather than assert the expedition has occurred. | [MAL-FH05](#mal-fh05), [MAL-FA01](#mal-fa01), [MAL-FA05](#mal-fa05), [MAL-EH03](#mal-eh03), [MAL-EH05](#mal-eh05), [MAL-EA01](#mal-ea01), [MAL-EA04](#mal-ea04) |
| **L4** | Invented the axe-hurling Goblin-hewer; undated designs can appear as experimental machinery. | [MAL-FH03](#mal-fh03), [MAL-FA03](#mal-fa03), [MAL-EH01](#mal-eh01), [MAL-EA03](#mal-ea03) |

#### Friendly/neutral — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="mal-fh01"></a>**MAL-FH01 — The Unsinkable's Last Rivet**<br>Target WV **+1** | Your engineers report that Malakai used salvaged plans from the Unsinkable to demonstrate a safer compartmented hull. The test barge sank, but the sealed cargo compartment reached shore intact and its measurements survived. | **A.** Fund another controlled trial: innovativeness with expense.<br>**B.** Adapt the compartments for storehouses: local economic recovery.<br>**C.** Publish the failure report: administrative knowledge. | L1 |
| <a id="mal-fh02"></a>**MAL-FH02 — The Hangar with No Roof**<br>Target WV **+1** | Your hold engineer reports that Malakai's lifting-engine trial blew the roof off a disused hangar. He left corrected drawings and a bitter note comparing the failure with the Undestructible before disappearing into the mountains. | **A.** Repair the site and study the drawings: innovativeness with expense.<br>**B.** Salvage the intact machinery: income.<br>**C.** Circulate the safety lessons: military knowledge. | L2 |
| <a id="mal-fh03"></a>**MAL-FH03 — Axes in the Target Wall**<br>Target WV **+2** | Your garrison reports that a trial Goblin-hewer broke a raiding force before its own platform collapsed. The defenders recovered usable axes and a detailed ammunition-loading diagram. | **A.** Rebuild the firing platform: improved local defence with expense.<br>**B.** Train the surviving crew: army professionalism.<br>**C.** Distribute the recovered weapons: manpower support. | L4 |
| <a id="mal-fh04"></a>**MAL-FH04 — A Slayer's Workshop Debt**<br>Target WV **+1** | Your guild court reports that Malakai settled an old workshop debt by repairing machinery, then refused an offer of reinstatement that might soften his disgrace. The repaired works are producing again, but rival masters dispute ownership of his notes. | **A.** Confirm the workshop settlement: administrative knowledge.<br>**B.** Buy copies for apprentices: innovativeness with expense.<br>**C.** Honour the fulfilled debt: prestige. | L2 |
| <a id="mal-fh05"></a>**MAL-FH05 — The Cargo Above the Pass**<br>Target WV **+2** | Your border warden reports that Malakai's experimental flying machine carried stranded prospectors over a blocked pass. They returned with mineral samples and sketches of ruins that recall the ambitions behind his later Karak Dum expedition. | **A.** Survey the samples: innovativeness.<br>**B.** Develop the promising workings: production development with expense.<br>**C.** Preserve the rescue account: prestige and army tradition. | L3 |

#### Friendly/neutral — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="mal-fa01"></a>**MAL-FA01 — The Harbour's Unscheduled Landing**<br>Target WV **+1** | Your harbour master reports that Malakai landed a flying prototype between the warehouses and commandeered a damaged crane to lift it again. He left the crane repaired and its operators trained in a new hoist arrangement. | **A.** Adopt the hoist design: innovativeness.<br>**B.** Extend its use to public cargo handling: local trade recovery.<br>**C.** Auction the spare machinery: income. | L3 |
| <a id="mal-fa02"></a>**MAL-FA02 — The River Refused the Name**<br>Target WV **+1** | Your ferrymen report that Malakai declined to call a test vessel unsinkable, then deliberately flooded it to prove a rescue method. The vessel was lost, but every passenger and the sealed food cargo reached shore. | **A.** Teach the method to river crews: naval tradition.<br>**B.** Fund sealed relief barges: provincial recovery with expense.<br>**C.** Preserve the test results: innovativeness. | L1 |
| <a id="mal-fa03"></a>**MAL-FA03 — The Foreign Range's Axe Rain**<br>Target WV **+2** | Your commander reports that Malakai tested a compact axe-thrower against raiders threatening a frontier post. Local armourers recovered its throwing pattern and have asked how much of the experiment they may copy. | **A.** Authorize supervised trials: army professionalism.<br>**B.** Reinforce the frontier post: local defence.<br>**C.** Display the recovered enemy standards: prestige. | L4 |
| <a id="mal-fa04"></a>**MAL-FA04 — The Burnt Balloon's Survivors**<br>Target WV **+1** | Your magistrate reports that Malakai cut a failing experimental envelope free before its fire reached a crowded market. His own account invokes the Undestructible's disaster, and merchants credit the evacuation drill he shouted from the rigging. | **A.** Make the drill standard practice: administrative knowledge.<br>**B.** Reimburse damage and train rescuers: prestige with expense.<br>**C.** Study the discarded valves: innovativeness. | L2 |
| <a id="mal-fa05"></a>**MAL-FA05 — The Ruin Seen from Above**<br>Target WV **+2** | Your surveyor reports that Malakai carried an expedition over impassable ground and recovered a stranded team with ancient tools. His crew has departed, leaving aerial sketches of roads and ruins unfamiliar to your administration. | **A.** Fund a ground survey: innovativeness with expense.<br>**B.** Restore an identified route: provincial economic recovery.<br>**C.** Purchase the recovered tools: production development with expense. | L3 |

#### Enemy — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="mal-eh01"></a>**MAL-EH01 — The Battery that Fired Axes**<br>Target WV **−2** | Your siege commander reports that Malakai's improvised Goblin-hewer tore through a supply approach and wrecked the nearest gun crew. The machine was dismantled before your counterattack arrived. | **A.** Replace the gun crew and stores: treasury loss.<br>**B.** Redistribute the surviving battery: military power loss.<br>**C.** Abandon the damaged position: devastation. | L4 |
| <a id="mal-eh02"></a>**MAL-EH02 — The Dock's Flooded Prize**<br>Target WV **−1** | Your dockmaster reports that Malakai sabotaged a seized experimental ironclad by exploiting weaknesses he compared to his own Unsinkable. Its prisoners escaped in compartmented floats before the hull settled into the mud. | **A.** Pay to raise the hull: treasury loss.<br>**B.** Write off the naval experiment: prestige loss.<br>**C.** Investigate the stolen design: administrative power loss. | L1 |
| <a id="mal-eh03"></a>**MAL-EH03 — The Hangar's Escape Valve**<br>Target WV **−2** | Your engineer reports that Malakai opened the lift apparatus on a captured flying prototype and used the resulting confusion to free its workers. The empty machine exploded after drifting clear of the hangar. | **A.** Replace the machinery: treasury loss.<br>**B.** Revise the air-defence programme: military power loss.<br>**C.** Abandon the scorched installation: devastation. | L2, L3 |
| <a id="mal-eh04"></a>**MAL-EH04 — The Guild We Had Purchased**<br>Target WV **−1** | Your governor reports that Malakai destroyed a ledger binding a workshop to your military contracts. The masters followed his example of accepting disgrace rather than submission and fled with their finest tools. | **A.** Hire replacement artisans: treasury loss.<br>**B.** Rebuild the missing contract records: administrative power loss.<br>**C.** Let the failed purchase become public: prestige loss. | L2 |
| <a id="mal-eh05"></a>**MAL-EH05 — The Pass Below the Airship**<br>Target WV **−2** | Your warden reports that Malakai carried captives and heirlooms out of a sealed mountain fortress by air. Your costly blockade held every road but never reached the departing craft. | **A.** Expand the watch and repair its equipment: treasury loss.<br>**B.** Retrain the garrison: military power loss.<br>**C.** Deny the value of the lost captives and trophies: prestige loss. | L3 |

#### Enemy — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="mal-ea01"></a>**MAL-EA01 — The Depot Under the Shadow**<br>Target WV **−2** | Your quartermaster reports that an unfamiliar flying machine dropped explosives onto a military depot. Survivors identified a red-haired Dwarf pilot; rescued labourers departed with the craft before your scouts arrived. | **A.** Replace the stores: treasury loss.<br>**B.** Reorganize dispersed depots: military power loss.<br>**C.** Leave the burnt district unrepaired: devastation. | L3 |
| <a id="mal-ea02"></a>**MAL-EA02 — The Trial Ship's Missing Bulkheads**<br>Target WV **−1** | Your shipwright reports that Malakai removed critical fittings from a stolen prototype and left a mocking account of the Unsinkable. The vessel foundered during launch, although its workers escaped. | **A.** Rebuild the vessel safely: treasury loss.<br>**B.** Audit the procurement office: administrative power loss.<br>**C.** Abandon the project publicly: prestige loss. | L1 |
| <a id="mal-ea03"></a>**MAL-EA03 — The Axe Machine in the Alley**<br>Target WV **−2** | Your governor reports that Malakai installed an experimental axe-thrower across the route of a captive convoy. The escort broke, and the freed workers carried away its ammunition while he dismantled the machine. | **A.** Replace the escort's arms: treasury loss.<br>**B.** Reorganize convoy doctrine: military power loss.<br>**C.** Abandon the contested street: devastation. | L4 |
| <a id="mal-ea04"></a>**MAL-EA04 — The Fire Above the Foundry**<br>Target WV **−1** | Your foundry master reports that Malakai used a small lifting engine to pull stolen plans out of the archive, then destroyed it before your guards could study it. Burning fragments damaged the roof and scattered the records. | **A.** Repair the roof and salvage records: treasury loss.<br>**B.** Reconstruct the missing research: administrative power loss.<br>**C.** Acknowledge the security failure: prestige loss. | L2, L3 |
| <a id="mal-ea05"></a>**MAL-EA05 — The Engineer's Refused Commission**<br>Target WV **−1** | Your governor reports that an attempt to compel Malakai into service ended with disabled lathes and apprentices escaping through a maintenance passage. He left a note explaining why neither patronage nor disgrace would make him work for you. | **A.** Replace the workshop's equipment: treasury loss.<br>**B.** Reorganize the surviving workforce: administrative power loss.<br>**C.** Repudiate the governor's coercion: prestige loss. | L2 |

<a id="catalogue-tyr"></a>

### 10.14. Tyrion

**Fame:** 5/5. **Start:** **Avelorn — H08**, Phoenix Gate **1829** (Ulthuan). **Enemy profile:** A, as defined in section 5. **Home:** Ulthuan.

#### Lore coverage

| Lore reference | Exploit or background and chronology | Concepts representing it |
|---|---|---|
| **L1** | Banished N'Kari at the Phoenix Shrine, defending Aenarion's line; new shrine encounters echo that victory without repeatedly resurrecting the named daemon. | [TYR-FH01](#tyr-fh01), [TYR-FH05](#tyr-fh05), [TYR-FA01](#tyr-fa01), [TYR-EH01](#tyr-eh01), [TYR-EH04](#tyr-eh04), [TYR-EA01](#tyr-ea01), [TYR-EA04](#tyr-ea04) |
| **L2** | Slew Urian Poisonblade at Finuval Plain; use accounts, tactical lessons, and new champions rather than kill Urian again. | [TYR-FH02](#tyr-fh02), [TYR-FH04](#tyr-fh04), [TYR-FA02](#tyr-fa02), [TYR-FA05](#tyr-fa05), [TYR-EH02](#tyr-eh02), [TYR-EH05](#tyr-eh05), [TYR-EA02](#tyr-ea02), [TYR-EA05](#tyr-ea05) |
| **L3** | Routed Kritsqueel's Skaven force with only Malhandir accompanying him; lone charges and broken tunnel raids draw on this feat. | [TYR-FH03](#tyr-fh03), [TYR-FA03](#tyr-fa03), [TYR-FA04](#tyr-fa04), [TYR-EH03](#tyr-eh03), [TYR-EA03](#tyr-ea03) |

#### Friendly/neutral — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="tyr-fh01"></a>**TYR-FH01 — The Shrine's Renewed Watch**<br>Target WV **+2** | Your shrine wardens report that Tyrion broke a daemonic incursion at an outer sanctuary and left instructions recalling his stand against N'Kari at the Phoenix Shrine. Pilgrims have returned, but the wardens disagree over the recovered offerings. | **A.** Restore the sanctuary with the offerings: provincial recovery.<br>**B.** Strengthen its watch: army professionalism.<br>**C.** Commemorate the rescue: prestige. | L1 |
| <a id="tyr-fh02"></a>**TYR-FH02 — Urian's Lesson on the Practice Field**<br>Target WV **+1** | Your marshal reports that Tyrion corrected an overconfident officer's sword drill by explaining how he defeated Urian Poisonblade. The demonstration ended with an embarrassed officer and a regiment eager to practise. | **A.** Adopt the revised training: army professionalism.<br>**B.** Circulate the battle commentary: army tradition.<br>**C.** Reward the officer for accepting correction: prestige. | L2 |
| <a id="tyr-fh03"></a>**TYR-FH03 — One Rider at the Culvert**<br>Target WV **+2** | Your patrol reports that Tyrion and Malhandir broke a ratman force emerging beneath a supply road. Survivors compare the charge to Kritsqueel's defeat, and abandoned stores now block the culvert. | **A.** Recover the stores for the garrison: manpower support.<br>**B.** Study and seal the route: military knowledge.<br>**C.** Sell unclaimed cargo to repair the road: income. | L3 |
| <a id="tyr-fh04"></a>**TYR-FH04 — The Poisoned Champion's Purse**<br>Target WV **+1** | Your herald reports that Tyrion exposed a would-be champion's poisoned blade before a ceremonial bout. He left testimony comparing the deception with Urian's methods and asked that the injured attendants be remembered. | **A.** Investigate the accomplices: administrative knowledge.<br>**B.** Establish safer tournament inspections: army professionalism.<br>**C.** Honour the attendants publicly: prestige. | L2 |
| <a id="tyr-fh05"></a>**TYR-FH05 — The Heirloom at the Phoenix Gate**<br>Target WV **+1** | Your keeper reports that Tyrion recovered an ancestral token from thieves operating near a sanctuary. His refusal to let them bargain with a relic associated with Aenarion has renewed interest in the shrine's neglected records. | **A.** Restore the records: administrative knowledge.<br>**B.** Exhibit the recovered token: prestige.<br>**C.** Fund the sanctuary's custodians: reduced local unrest with expense. | L1 |

#### Friendly/neutral — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="tyr-fa01"></a>**TYR-FA01 — The Stranger at the Defiled Shrine**<br>Target WV **+2** | Your governor reports that Tyrion expelled a summoned creature from a local sanctuary, despite understanding little of its rites. Its custodians compare his description of the Phoenix Shrine with their own account of the breach. | **A.** Share the warding records: innovativeness.<br>**B.** Support the displaced custodians: provincial recovery.<br>**C.** Recognize the rescue across religious differences: prestige. | L1 |
| <a id="tyr-fa02"></a>**TYR-FA02 — The Duel Beyond the Interpreter**<br>Target WV **+1** | Your commander reports that Tyrion defeated a marauder champion after negotiations failed through an interpreter. He left a sketch of the feint he used, annotated with a reference to Finuval Plain. | **A.** Teach the feint to officers: army tradition.<br>**B.** Reward the rescued interpreter: prestige.<br>**C.** Purchase and translate the full account: military knowledge with expense. | L2 |
| <a id="tyr-fa03"></a>**TYR-FA03 — Malhandir on the Caravan Road**<br>Target WV **+2** | Your caravan master reports that Tyrion and his horse scattered a tunnelling ambush before the guards could form. The rescued merchants have surrendered captured intelligence to your customs office. | **A.** Map the raiders' routes: military knowledge.<br>**B.** Recover unclaimed merchandise: income.<br>**C.** Train escorts from the survivors' account: army professionalism. | L3 |
| <a id="tyr-fa04"></a>**TYR-FA04 — A Prison Opened by One Rider**<br>Target WV **+2** | Your border officer reports that Tyrion broke a raiders' prison and escorted captives to the frontier. The released soldiers have requested permission to teach your recruits the disciplined counterattack they witnessed. | **A.** Accept their instruction: army professionalism.<br>**B.** Settle civilian survivors: development with expense.<br>**C.** Celebrate the prisoners' return: prestige. | L3 |
| <a id="tyr-fa05"></a>**TYR-FA05 — The Foreign Swordmaster's Testimony**<br>Target WV **+1** | Your governor receives a foreign instructor's account of losing a friendly bout to Tyrion. The visitor identified a dangerous flaw in the local school and explained his duel with Urian as a warning against theatrical swordplay. | **A.** Revise the school's curriculum: army tradition.<br>**B.** Fund translated training notes: military knowledge with expense.<br>**C.** Honour the instructor's candour: prestige. | L2 |

#### Enemy — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="tyr-eh01"></a>**TYR-EH01 — The Occupier's Empty Shrine**<br>Target WV **−2** | Your governor reports that Tyrion destroyed a summoning apparatus installed in a seized sanctuary. The bound creature is gone, the attendants escaped, and the provincial guard refuses to approach the damaged chamber. | **A.** Rebuild conventional security: treasury loss.<br>**B.** Investigate the lost ritual: administrative power loss.<br>**C.** Abandon the chamber: devastation. | L1 |
| <a id="tyr-eh02"></a>**TYR-EH02 — The Champion Before the Gate**<br>Target WV **−1** | Your marshal reports that Tyrion defeated the officer guarding a confiscated estate and returned its heirlooms to their claimants. Witnesses have begun comparing your officer unfavourably with Urian Poisonblade. | **A.** Replace the officer's equipment and escort: treasury loss.<br>**B.** Revise the garrison's command: military power loss.<br>**C.** Endure the public comparisons: prestige loss. | L2 |
| <a id="tyr-eh03"></a>**TYR-EH03 — The Column that Met Malhandir**<br>Target WV **−2** | Your quartermaster reports that Tyrion and Malhandir scattered an isolated supply column before nearby troops could intervene. Its surviving guards insist that no supporting army ever appeared. | **A.** Replace the lost supplies: treasury loss.<br>**B.** Reorganize the march order: military power loss.<br>**C.** Requisition replacements locally: devastation. | L3 |
| <a id="tyr-eh04"></a>**TYR-EH04 — The Ancestor's Confiscated Relic**<br>Target WV **−1** | Your keeper reports that Tyrion recovered a seized ancestral relic and released the attendants held with it. He left a warning invoking the defence of Aenarion's line, then rode through the closing gates. | **A.** Compensate the defeated guards: treasury loss.<br>**B.** Rebuild the sanctuary's security: administrative power loss.<br>**C.** Dismiss the relic's importance: prestige loss. | L1 |
| <a id="tyr-eh05"></a>**TYR-EH05 — The School with No Master**<br>Target WV **−1** | Your military tutor reports that Tyrion defeated the champion enforcing compulsory instruction at an occupied sword school. The pupils dispersed with the school's records and have begun training opposition volunteers. | **A.** Recruit replacement instructors: treasury loss.<br>**B.** Reorganize military education: military power loss.<br>**C.** Tolerate the loss of authority: prestige loss. | L2 |

#### Enemy — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="tyr-ea01"></a>**TYR-EA01 — The Broken Summoning Escort**<br>Target WV **−2** | Your commander reports that Tyrion attacked a convoy carrying a bound daemon and destroyed its controlling vessel. The escort fled while captive labourers escaped along the road. | **A.** Replace the convoy's military role: treasury loss.<br>**B.** Investigate the failed containment: administrative power loss.<br>**C.** Abandon its damaged staging ground: devastation. | L1 |
| <a id="tyr-ea02"></a>**TYR-EA02 — The Governor's Champion Unhorsed**<br>Target WV **−1** | Your governor reports that Tyrion publicly defeated his champion after discovering prisoners held as tournament stakes. He released them and left before the reserve guard assembled. | **A.** Pay compensation to restore order: treasury loss.<br>**B.** Retrain the humiliated guard: military power loss.<br>**C.** Preserve the governor's account despite witnesses: prestige loss. | L2 |
| <a id="tyr-ea03"></a>**TYR-EA03 — The Tunnel Mouth's Lone Rider**<br>Target WV **−2** | Your engineer reports that Tyrion and Malhandir broke a sortie from a concealed military tunnel. Work crews fled, leaving the access mechanism destroyed and the stored provisions in enemy hands. | **A.** Rebuild the mechanism: treasury loss.<br>**B.** Reorganize the tunnel garrison: military power loss.<br>**C.** Abandon the entrance: devastation. | L3 |
| <a id="tyr-ea04"></a>**TYR-EA04 — A Shrine Beyond His Homeland**<br>Target WV **−1** | Your overseer reports that Tyrion removed a captive temple custodian from a guarded excavation and wrecked the apparatus restraining a dangerous relic. His warning concerns the relic's use, regardless of the temple's faith. | **A.** Repair and secure the excavation: treasury loss.<br>**B.** Examine the custodians' claims: administrative power loss.<br>**C.** Deny the public accusation: prestige loss. | L1 |
| <a id="tyr-ea05"></a>**TYR-EA05 — The Lesson Our Officers Received**<br>Target WV **−1** | Your commander reports that Tyrion defeated an officer sent to arrest him and explained the officer's mistakes to the watching soldiers. His account of Finuval Plain has become an embarrassing favourite in the barracks. | **A.** Replace damaged equipment and reassure the troops: treasury loss.<br>**B.** Overhaul officer training: military power loss.<br>**C.** Forbid the story and accept the ridicule: prestige loss. | L2 |

<a id="catalogue-gor"></a>

### 10.15. Gor-Rok

**Fame:** 4/5. **Start:** **Itza — V03**, province **2466** (Lustria). **Enemy profile:** A, as defined in section 5. **Home:** Lustria.

#### Lore coverage

| Lore reference | Exploit or background and chronology | Concepts representing it |
|---|---|---|
| **L1** | Recovered the Star Stela of Quetli under Tepec-Inzi, smashed a Dark Elf commander's chariot, and killed him despite being impaled; retain the endurance and relic-recovery details in new incidents without repeating the named campaign. | [GOR-FH01](#gor-fh01), [GOR-FH02](#gor-fh02), [GOR-FA02](#gor-fa02), [GOR-EH01](#gor-eh01), [GOR-EH05](#gor-eh05), [GOR-EA02](#gor-ea02), [GOR-EA05](#gor-ea05) |
| **L2** | Slew a Savage Orc warboss and its Wyvern at Bloodpools; paired rider-and-beast threats provide the event echo. | [GOR-FH03](#gor-fh03), [GOR-FA03](#gor-fa03), [GOR-EH02](#gor-eh02), [GOR-EA03](#gor-ea03) |
| **L3** | Withstood Ogre charges and blows from Greater Daemons; these are exceptional feats of endurance, not proof of invulnerability. | [GOR-FH04](#gor-fh04), [GOR-FH05](#gor-fh05), [GOR-FA04](#gor-fa04), [GOR-FA05](#gor-fa05), [GOR-EH03](#gor-eh03), [GOR-EH04](#gor-eh04), [GOR-EA02](#gor-ea02), [GOR-EA04](#gor-ea04), [GOR-EA05](#gor-ea05) |
| **L4** | Campaigned as far as the Chaos Wastes; foreign conditions and fighting beyond Lustria are legitimate motifs. | [GOR-FA01](#gor-fa01), [GOR-FA05](#gor-fa05), [GOR-EA01](#gor-ea01), [GOR-EA05](#gor-ea05) |

#### Friendly/neutral — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="gor-fh01"></a>**GOR-FH01 — The Stela Returned with a Spear**<br>Target WV **+2** | Your temple liaison reports that Gor-Rok recovered a stolen inscribed stone from raiders and waited until it was secured before allowing a spear to be drawn from his side. The custodians compare the incident with the Star Stela of Quetli's recovery under Tepec-Inzi. | **A.** Restore the shrine and catalogue the stone: innovativeness.<br>**B.** Fortify its approach: local defence.<br>**C.** Commemorate the recovery: prestige. | L1 |
| <a id="gor-fh02"></a>**GOR-FH02 — The Chariot in the Causeway**<br>Target WV **+1** | Your road warden reports that Gor-Rok smashed a raider commander's chariot while blocking a temple causeway. The defeated band's abandoned cargo includes stolen tools and fragments of sacred inscriptions. | **A.** Return the tools to their workshops: local economic recovery.<br>**B.** Examine the fragments: innovativeness.<br>**C.** Train guards from the surviving witnesses: army tradition. | L1 |
| <a id="gor-fh03"></a>**GOR-FH03 — The Rider and the Wings**<br>Target WV **+2** | Your scouts report that Gor-Rok killed a raider chief and its flying mount beside a settlement's pools. Attendants invoke Bloodpools while petitioning for the dangerous remains to be removed. | **A.** Study the carcass safely: innovativeness.<br>**B.** Reward the scouts who protected civilians: army professionalism.<br>**C.** Use recovered raider supplies for relief: provincial recovery. | L2 |
| <a id="gor-fh04"></a>**GOR-FH04 — The Line That Did Not Move**<br>Target WV **+2** | Your commander reports that Gor-Rok held a narrow approach against repeated charges by hired Ogre raiders. His stand allowed the settlement's defenders to regroup, and their officers have returned with a precise account of the formation. | **A.** Teach the defensive formation: army tradition.<br>**B.** Rebuild the battered approach: local defence with expense.<br>**C.** Recognize the defenders' recovery: prestige. | L3 |
| <a id="gor-fh05"></a>**GOR-FH05 — The Blow Against the White Shield**<br>Target WV **+1** | Your temple watch reports that Gor-Rok survived a summoned horror's blow long enough for attendants to close the breach behind it. The site is secure, but his cracked shield marks have become the subject of competing interpretations. | **A.** Record the witnesses' account: military knowledge.<br>**B.** Reinforce the wardens' watch: army professionalism.<br>**C.** Honour the successful defence: prestige. | L3 |

#### Friendly/neutral — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="gor-fa01"></a>**GOR-FA01 — The Snow on the White Saurus**<br>Target WV **+1** | Your frontier governor reports that Gor-Rok crossed freezing ground to destroy raiders threatening an ancient ruin. His tracks and the survivors' route notes offer a rare account of travel in conditions reminiscent of his Chaos Wastes campaigns. | **A.** Map the winter approaches: military knowledge.<br>**B.** Establish a shelter for patrols: local defence with expense.<br>**C.** Recover abandoned raider stores: income. | L4 |
| <a id="gor-fa02"></a>**GOR-FA02 — The Auction's Broken Chariot**<br>Target WV **+2** | Your magistrate reports that Gor-Rok intercepted a smuggler's chariot carrying a stolen inscribed slab. He held the yard despite an embedded weapon until the frightened custodians recovered the slab, then left them with your officials. | **A.** Study the recovered inscription: innovativeness.<br>**B.** Compensate the yard and return stolen goods: prestige with expense.<br>**C.** Prosecute the smuggling records: administrative knowledge. | L1 |
| <a id="gor-fa03"></a>**GOR-FA03 — The Wyvern Above the Quarry**<br>Target WV **+2** | Your overseer reports that Gor-Rok killed both a flying beast and its marauding rider before they reached a workers' camp. The workers have offered the recovered equipment to your government in gratitude. | **A.** Equip a local watch: manpower support.<br>**B.** Sell surplus equipment for repairs: income.<br>**C.** Catalogue the beast's remains: innovativeness. | L2 |
| <a id="gor-fa04"></a>**GOR-FA04 — The Ruin Beneath the New Street**<br>Target WV **+1** | Your surveyor reports that Gor-Rok stood against a hired raiding band's heavy charge at an exposed ancient foundation. He protected the excavation without acknowledging either the officials or the workers now petitioning for its preservation. | **A.** Preserve and examine the foundation: innovativeness.<br>**B.** Incorporate the strong masonry into public works: local defence.<br>**C.** Recognize the workers' restraint: prestige. | L3 |
| <a id="gor-fa05"></a>**GOR-FA05 — The Horror in the Foreign Gate**<br>Target WV **+2** | Your garrison reports that Gor-Rok absorbed the first assault of a summoned creature at an isolated gate while civilians escaped. Local defenders then closed the breach, but cannot explain why he chose their settlement. | **A.** Reward and train the defenders: army professionalism.<br>**B.** Repair the gate from recovered supplies: local defence.<br>**C.** Investigate the breach's remains: innovativeness. | L3, L4 |

#### Enemy — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="gor-eh01"></a>**GOR-EH01 — The Stela's Empty Wagon**<br>Target WV **−2** | Your occupation officer reports that Gor-Rok destroyed a relic convoy's command chariot and recovered its stone cargo. Even a spear through his body failed to stop him before the surviving temple attendants escaped. | **A.** Replace the convoy and guards: treasury loss.<br>**B.** Reorganize relic transport: administrative power loss.<br>**C.** Abandon the wrecked depot: devastation. | L1 |
| <a id="gor-eh02"></a>**GOR-EH02 — The Wyvern Pen's Two Corpses**<br>Target WV **−2** | Your beast-master reports that Gor-Rok killed a military Wyvern and the champion riding it during a demonstration. The ruined pen has drawn crowds of hostile local witnesses. | **A.** Replace the lost military capacity: treasury loss.<br>**B.** Reorganize beast-handling detachments: military power loss.<br>**C.** Leave the compound ruined: devastation. | L2 |
| <a id="gor-eh03"></a>**GOR-EH03 — The Charge Against the Causeway**<br>Target WV **−1** | Your commander reports that hired heavy troops broke themselves against Gor-Rok at a temple approach. He withdrew with the custodians after the failed charge left your formation in disorder. | **A.** Pay the troops' recovery costs: treasury loss.<br>**B.** Replace their officers: military power loss.<br>**C.** Deny the defeat's significance: prestige loss. | L3 |
| <a id="gor-eh04"></a>**GOR-EH04 — The Greater Horror's Failed Blow**<br>Target WV **−2** | Your ritual officer reports that the summoned creature guarding a confiscated shrine failed to dislodge Gor-Rok. The struggle wrecked its apparatus and allowed captives to escape into the surrounding district. | **A.** Replace the shattered apparatus: treasury loss.<br>**B.** Abandon the ritual programme: administrative power loss.<br>**C.** Close the ruined shrine: devastation. | L3 |
| <a id="gor-eh05"></a>**GOR-EH05 — The Commander's Crushed Trophy**<br>Target WV **−1** | Your governor reports that Gor-Rok smashed the vehicle displaying stolen temple trophies, defeated its commander, and carried away the inscribed pieces. The remaining guards refuse to pursue him into the jungle. | **A.** Replace the escort and display: treasury loss.<br>**B.** Investigate the trophies' provenance: administrative power loss.<br>**C.** Endure the public humiliation: prestige loss. | L1 |

#### Enemy — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="gor-ea01"></a>**GOR-EA01 — The Camp Beyond the Snowline**<br>Target WV **−2** | Your frontier commander reports that Gor-Rok broke a supply camp thought safe behind severe winter terrain. He left its engines wrecked and disappeared toward ancient ruins outside the patrol routes. | **A.** Replace the winter stores: treasury loss.<br>**B.** Reorganize the exposed patrol routes: military power loss.<br>**C.** Abandon the damaged camp: devastation. | L4 |
| <a id="gor-ea02"></a>**GOR-EA02 — The Stone the Quarry Would Not Yield**<br>Target WV **−1** | Your quarry overseer reports that Gor-Rok destroyed the lifting equipment around an inscribed foundation. Heavy guards failed to shift him until labourers fled with several recovered tablets. | **A.** Replace the equipment: treasury loss.<br>**B.** Relocate the work crews: administrative power loss.<br>**C.** Leave the quarry closed: local devastation. | L1, L3 |
| <a id="gor-ea03"></a>**GOR-EA03 — The Foreign Champion's Fallen Mount**<br>Target WV **−2** | Your governor reports that Gor-Rok slew the winged beast used to intimidate a labour district and then killed its rider. The workers have scattered with the district's tools and records. | **A.** Replace the district's security: treasury loss.<br>**B.** Reconstruct the missing labour records: administrative power loss.<br>**C.** Abandon the damaged yard: devastation. | L2 |
| <a id="gor-ea04"></a>**GOR-EA04 — The Demonstration of Heavy Troops**<br>Target WV **−1** | Your marshal reports that a public charge intended to capture Gor-Rok ended with the attackers thrown back. Witnesses saw him hold his ground until a group of detained excavators escaped behind him. | **A.** Pay for the soldiers' recovery: treasury loss.<br>**B.** Revise their tactical training: military power loss.<br>**C.** Dismiss the failed spectacle: prestige loss. | L3 |
| <a id="gor-ea05"></a>**GOR-EA05 — The Relic Behind the Daemon**<br>Target WV **−2** | Your keeper reports that Gor-Rok endured the bound guardian's blows, broke its controlling frame, and carried a confiscated relic out of the vault. The remaining exhibits lie beneath collapsed masonry. | **A.** Repair the vault and its guards: treasury loss.<br>**B.** Investigate the failed guardian: administrative power loss.<br>**C.** Seal the ruined galleries: devastation. | L1, L3, L4 |

<a id="catalogue-nak"></a>

### 10.16. Nakai the Wanderer

**Fame:** 4/5. **Start:** **S'sildra Tor — H20**, Fellwrath **2348** (Naggaroth). **Enemy profile:** A, as defined in section 5. **Home:** Lustria.

#### Lore coverage

| Lore reference | Exploit or background and chronology | Concepts representing it |
|---|---|---|
| **L1** | Held the Bridge of Stars at Itza against daemons during the Great Catastrophe; new crossing defences recall that ancient feat without replaying it. | [NAK-FH01](#nak-fh01), [NAK-FH04](#nak-fh04), [NAK-FA02](#nak-fa02), [NAK-FA04](#nak-fa04), [NAK-EH01](#nak-eh01), [NAK-EH04](#nak-eh04), [NAK-EA02](#nak-ea02) |
| **L2** | Appears when Lizardmen face danger and resumes wandering afterward; timely arrivals, uncertain motives, and unexplained departures drive the reports. | [NAK-FH02](#nak-fh02), [NAK-FH03](#nak-fh03), [NAK-FH05](#nak-fh05), [NAK-FA01](#nak-fa01), [NAK-FA03](#nak-fa03), [NAK-FA04](#nak-fa04), [NAK-EH02](#nak-eh02), [NAK-EH03](#nak-eh03), [NAK-EH05](#nak-eh05), [NAK-EA01](#nak-ea01), [NAK-EA03](#nak-ea03), [NAK-EA04](#nak-ea04) |
| **L3** | Later accompanied Mazdamundi to Albion and helped establish Konquata; foreign sacred-site recovery and settlement protection are explicit early echoes, not a completed 2502 Albion campaign. | [NAK-FH05](#nak-fh05), [NAK-FA01](#nak-fa01), [NAK-FA02](#nak-fa02), [NAK-FA03](#nak-fa03), [NAK-FA05](#nak-fa05), [NAK-EH05](#nak-eh05), [NAK-EA01](#nak-ea01), [NAK-EA03](#nak-ea03), [NAK-EA05](#nak-ea05) |

#### Friendly/neutral — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="nak-fh01"></a>**NAK-FH01 — The Crossing Before the Alarm**<br>Target WV **+2** | Your river warden reports that Nakai held a crossing against a daemonic incursion before the alarm reached the nearest temple. Attendants compare the piled remains with stories of the Bridge of Stars, while the surviving defenders await instructions. | **A.** Rebuild the crossing: local defence with expense.<br>**B.** Train the defenders from the battle account: army tradition.<br>**C.** Restore the interrupted supply route: provincial recovery. | L1 |
| <a id="nak-fh02"></a>**NAK-FH02 — The Temple that Sent No Messenger**<br>Target WV **+1** | Your liaison reports that Nakai arrived at a threatened temple before its trapped custodians could send for help. He broke the attackers and vanished, leaving the custodians disputing which endangered storehouse should receive the recovered supplies. | **A.** Return the stores according to need: reduced local unrest.<br>**B.** Provision the temple watch: manpower support.<br>**C.** Preserve the testimony: prestige. | L2 |
| <a id="nak-fh03"></a>**NAK-FH03 — The Procession Returned at Dawn**<br>Target WV **+1** | Your patrol reports that a missing group of temple attendants returned behind Nakai with their relics intact. He led them around a concealed ambush, then walked away without accepting their offered escort. | **A.** Map the safe route: military knowledge.<br>**B.** Reinforce the procession guard: army professionalism.<br>**C.** Honour the rescued custodians: prestige. | L2 |
| <a id="nak-fh04"></a>**NAK-FH04 — The Bridge Nobody Would Approach**<br>Target WV **+2** | Your scouts report that hostile summoned creatures recoiled from a crossing after Nakai's defence of it. The effect recalls the Bridge of Stars' dread reputation, but engineers caution that the shattered roadway still needs repair. | **A.** Repair and reopen the route: provincial recovery with expense.<br>**B.** Build on the defensive advantage: local defence.<br>**C.** Record the observed reaction: innovativeness. | L1 |
| <a id="nak-fh05"></a>**NAK-FH05 — The Watch Left Behind**<br>Target WV **+1** | Your temple officer reports that Nakai drove raiders from a neglected site and remained until local guardians returned. He has since disappeared, leaving your administration to sustain the recovered position. | **A.** Restore the site's watch: army professionalism.<br>**B.** Catalogue its surviving records: innovativeness.<br>**C.** Help its displaced workers return: local economic recovery. | L2, L3 |

#### Friendly/neutral — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="nak-fa01"></a>**NAK-FA01 — The Shrine Beyond the Black Forest**<br>Target WV **+1** | Your governor reports that Nakai destroyed raiders occupying a forgotten shrine in unfamiliar woodland. Its local custodians believe the site predates their settlement; his interest is unexplained, and he has moved on. | **A.** Survey the shrine: innovativeness.<br>**B.** Recognize the custodians' protection: prestige.<br>**C.** Use recovered supplies for the settlement: provincial recovery. | L2, L3 |
| <a id="nak-fa02"></a>**NAK-FA02 — The Causeway Through the Mist**<br>Target WV **+2** | Your frontier officer reports that Nakai held a mist-covered causeway long enough for an archaeological party to escape with inscribed stones. The incident is an early echo of the foreign campaigning later associated with Albion and Konquata. | **A.** Examine the stones: innovativeness.<br>**B.** Rebuild the causeway: local defence with expense.<br>**C.** Settle rescued workers near the route: development with expense. | L1, L3 |
| <a id="nak-fa03"></a>**NAK-FA03 — The Camp Built Around His Tracks**<br>Target WV **+1** | Your surveyors report that Nakai cleared raiders from a ruined enclosure and lingered until a defensible camp had been established. He departed without claiming it, leaving your officials to decide the camp's purpose. | **A.** Maintain a survey station: innovativeness.<br>**B.** Establish a patrol shelter: local defence.<br>**C.** Reopen the nearby caravan route: local trade recovery. | L2, L3 |
| <a id="nak-fa04"></a>**NAK-FA04 — The Giant in the Floodwater**<br>Target WV **+2** | Your river officer reports that Nakai held a damaged crossing while travellers escaped an attack during a flood. His timely arrival has become a popular tale, although none of the witnesses knows where he went afterward. | **A.** Repair the crossing and nearby homes: provincial recovery with expense.<br>**B.** Recruit willing survivors for rescue patrols: manpower.<br>**C.** Record the defenders' methods: army tradition. | L1, L2 |
| <a id="nak-fa05"></a>**NAK-FA05 — The Tablets on the Governor's Steps**<br>Target WV **+1** | Your governor reports that Nakai left recovered tablets beside the provincial office after breaking a relic trafficker's camp. Several displaced custodians followed him to the town and now seek a protected place to study them. | **A.** Offer a temporary scholarly refuge: innovativeness.<br>**B.** Return the tablets under official protection: prestige.<br>**C.** Prosecute the trafficker's surviving records: administrative knowledge. | L3 |

#### Enemy — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="nak-eh01"></a>**NAK-EH01 — The Invasion Stopped at the Bridge**<br>Target WV **−2** | Your commander reports that Nakai shattered the leading units of an invasion column at a temple crossing. Surviving scouts refuse to follow the same approach, recalling the ancient stories of Itza. | **A.** Replace the column's equipment: treasury loss.<br>**B.** Reorganize its route and command: military power loss.<br>**C.** Abandon the battered approach: devastation. | L1 |
| <a id="nak-eh02"></a>**NAK-EH02 — The Garrison's Unannounced Visitor**<br>Target WV **−1** | Your occupation officer reports that Nakai entered a poorly guarded shrine compound and broke open its holding pens. The captives dispersed while he destroyed the equipment intended to restrain them. | **A.** Replace the damaged equipment: treasury loss.<br>**B.** Review the occupation's security: administrative power loss.<br>**C.** Admit the garrison's failure: prestige loss. | L2 |
| <a id="nak-eh03"></a>**NAK-EH03 — The Relics Gone Before Dawn**<br>Target WV **−1** | Your keeper reports that Nakai recovered confiscated temple objects and escorted their custodians into the jungle. He appeared before the scheduled transfer, although its route had been disclosed only to senior officials. | **A.** Replace the escort and transport: treasury loss.<br>**B.** Investigate the information leak: administrative power loss.<br>**C.** Deny the trophies' importance: prestige loss. | L2 |
| <a id="nak-eh04"></a>**NAK-EH04 — The Daemons at the Water's Edge**<br>Target WV **−2** | Your ritual commander reports that summoned troops faltered at the crossing Nakai defended, allowing its captives to escape. The subsequent fighting wrecked the control apparatus and your supply landing. | **A.** Replace the apparatus and landing: treasury loss.<br>**B.** Abandon the summoned formation: military power loss.<br>**C.** Leave the site sealed: devastation. | L1 |
| <a id="nak-eh05"></a>**NAK-EH05 — The Ruin Reoccupied Without Us**<br>Target WV **−2** | Your surveyor reports that Nakai drove your labour guard from a sacred enclosure and remained until its former custodians returned. Your stored tools and maps have been taken inside the renewed defences. | **A.** Replace the expedition's tools: treasury loss.<br>**B.** Reconstruct its lost surveys: administrative power loss.<br>**C.** Relinquish the position and its prestige: prestige loss. | L2, L3 |

#### Enemy — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="nak-ea01"></a>**NAK-EA01 — The Shrine Beneath the Slave Camp**<br>Target WV **−2** | Your overseer reports that Nakai demolished a camp built over ancient foundations and carried recovered carvings away. The captives followed him beyond the patrol perimeter. | **A.** Replace the compound's equipment: treasury loss.<br>**B.** Reorganize the exposed frontier administration: administrative power loss.<br>**C.** Abandon the damaged site: devastation. | L2, L3 |
| <a id="nak-ea02"></a>**NAK-EA02 — The Foreign Bridge's Broken Column**<br>Target WV **−2** | Your commander reports that Nakai stood across a narrow bridge and broke the convoy attempting to cross it. Captive labourers escaped during the struggle, leaving your stores scattered in the river. | **A.** Replace the lost stores: treasury loss.<br>**B.** Reorganize the escort doctrine: military power loss.<br>**C.** Requisition the river settlements: devastation. | L1 |
| <a id="nak-ea03"></a>**NAK-EA03 — The Settlement He Would Not Leave**<br>Target WV **−1** | Your governor reports that Nakai drove an armed requisition party out of a small settlement beside an ancient ruin. He stayed until its inhabitants had repaired a barricade, then disappeared into unfamiliar country. | **A.** Compensate the requisition party: treasury loss.<br>**B.** Revise the district's collection arrangements: administrative power loss.<br>**C.** Accept the public defiance: prestige loss. | L2, L3 |
| <a id="nak-ea04"></a>**NAK-EA04 — The Monster Hunter's Empty Cage**<br>Target WV **−1** | Your collector reports that an attempt to trap Nakai for a court menagerie ended with broken cages and released prisoners. The tracks lead toward a threatened shrine well beyond your scouts' usual routes. | **A.** Replace the collector's equipment: treasury loss.<br>**B.** Investigate the failed expedition: administrative power loss.<br>**C.** Disown the spectacle: prestige loss. | L2 |
| <a id="nak-ea05"></a>**NAK-EA05 — The Tablets Beyond the Frontier**<br>Target WV **−2** | Your expedition leader reports that Nakai overran a fortified excavation and escorted its coerced interpreters away with the sacred tablets. Their departure leaves your planned outpost without its records, workers, or defensible entrance. | **A.** Replace the expedition and its stores: treasury loss.<br>**B.** Reconstruct the missing research: administrative power loss.<br>**C.** Abandon the shattered outpost: devastation. | L3 |

<a id="catalogue-tha"></a>

### 10.17. Thanquol and Boneripper

**Fame:** 4/5. **Start:** **Grey Seer Clan — U25**, Central Skavenblight **4600** (Skavenblight). **Enemy profile:** B, as defined in section 5. **Home:** Skavenblight and the Under-Empire.

#### Lore coverage

| Lore reference | Exploit or background and chronology | Concepts representing it |
|---|---|---|
| **L1** | Thanquol's failed Nuln attack involved plague, engineered vermin, and factional intrigue; he reached the palace, failed to kill Emmanuelle, and escaped. Chronology varies, so these are parallel schemes rather than a fixed completed opening campaign. | [THA-FH01](#tha-fh01), [THA-FH02](#tha-fh02), [THA-FA01](#tha-fa01), [THA-FA02](#tha-fa02), [THA-FA05](#tha-fa05), [THA-EH01](#tha-eh01), [THA-EH02](#tha-eh02), [THA-EA01](#tha-ea01), [THA-EA02](#tha-ea02) |
| **L2** | Later attacked the Lonely Tower engineering camp to steal Dwarf technology; his attempt supplies the workshop-theft motif, not a claim of successful conquest. | [THA-FH03](#tha-fh03), [THA-FA03](#tha-fa03), [THA-EH03](#tha-eh03), [THA-EA03](#tha-ea03) |
| **L3** | Later pursued the Spirit of Grungni into Kislev and attempted to capture it; use prototype-aircraft schemes without requiring the named expedition to have happened. | [THA-FH04](#tha-fh04), [THA-FA04](#tha-fa04), [THA-EH04](#tha-eh04), [THA-EA04](#tha-ea04) |
| **L4** | Boneripper names successive Rat Ogre bodyguards; a replacement can appear without duplicating Thanquol or ending the travelling pair. | [THA-FH05](#tha-fh05), [THA-FA03](#tha-fa03), [THA-FA05](#tha-fa05), [THA-EH02](#tha-eh02), [THA-EH04](#tha-eh04), [THA-EH05](#tha-eh05), [THA-EA05](#tha-ea05) |

#### Friendly/neutral — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="tha-fh01"></a>**THA-FH01 — The Triumph in the Wrong Sewer**<br>Target WV **+1** | Thanquol's courier claims he destroyed a traitorous rival's plague laboratory. Your own inspectors confirm that his intended attack misfired, but the wreckage exposed stolen treasury goods and a genuine plot against your rule. | **A.** Confiscate the recovered goods: income.<br>**B.** Study the exposed conspiracy: administrative knowledge.<br>**C.** Announce the plot's defeat while omitting his excesses: prestige. | L1 |
| <a id="tha-fh02"></a>**THA-FH02 — The Vermin that Found the Stores**<br>Target WV **+1** | Your granary inspector reports that Thanquol's engineered vermin escaped their handlers and uncovered a hidden cache of embezzled grain. His letter describes this accident as a flawless investigation. | **A.** Recover the grain for the army: manpower support.<br>**B.** Sell surplus stores: income.<br>**C.** Reconstruct the embezzlement network: administrative knowledge.<br>**D.** Let the inspector claim the discovery: prestige. | L1 |
| <a id="tha-fh03"></a>**THA-FH03 — The Lonely Workshop's Stolen Gear**<br>Target WV **+2** | Your engineer reports that Thanquol returned from a raid on a foreign workshop with an unfamiliar rangefinder. Most of the stolen equipment was destroyed during his escape, but the surviving instrument can still be studied. | **A.** Buy the engineer's reconstruction: innovativeness with expense.<br>**B.** Use its measurements to train artillery crews: army tradition.<br>**C.** Sell the valuable spare parts: income. | L2 |
| <a id="tha-fh04"></a>**THA-FH04 — The Airship that Was Almost Captured**<br>Target WV **+1** | Your tunnel commander reports that Thanquol's attempt to seize a passing experimental aircraft failed spectacularly. The retreat nevertheless left your forces with a dropped cargo crate and sketches of its ground crew's procedures. | **A.** Study the sketches: innovativeness.<br>**B.** Recover the cargo for the treasury: income.<br>**C.** Train a specialist interception team: army professionalism. | L3 |
| <a id="tha-fh05"></a>**THA-FH05 — Boneripper's Replacement Invoice**<br>Target WV **+1** | Your beast-handlers petition over a bill for a new Rat Ogre after Thanquol's previous bodyguard was destroyed. Their inspection of the replacement exposed a supplier's fraud, and they have seized usable equipment from his pens. | **A.** Recover the supplier's illicit gains: income.<br>**B.** Retain the handlers' inspection method: administrative knowledge.<br>**C.** Equip the garrison from the seized stores: manpower support. | L4 |

#### Friendly/neutral — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="tha-fa01"></a>**THA-FA01 — The Provincial Palace's Secret Pipe**<br>Target WV **+2** | Your provincial agent reports that Thanquol escaped a failed attempt on a foreign dignitary through an overlooked drain. He failed to kill his target but brought back correspondence revealing a plot against your nearby enclave. | **A.** Exploit the correspondence: administrative knowledge.<br>**B.** Sell expendable secrets: income.<br>**C.** Improve the enclave's counterintelligence: army professionalism. | L1 |
| <a id="tha-fa02"></a>**THA-FA02 — The Plague Shipment's Useful Mistake**<br>Target WV **+1** | Your customs agent reports that a diseased shipment intended for an enemy instead exposed a rival supplier's concealed route. Thanquol blames the error on a subordinate; the route records and untainted goods are now in your custody. | **A.** Seize the safe merchandise: income.<br>**B.** Map the concealed route: military knowledge.<br>**C.** Use the evidence to settle internal disputes: prestige. | L1 |
| <a id="tha-fa03"></a>**THA-FA03 — The Workshop Plans in Three Pieces**<br>Target WV **+2** | Your frontier engineer reports that Thanquol and Boneripper escaped a raid on a Dwarf workshop with fragments of its machinery plans. Boneripper tore the papers during the retreat, but enough remains to identify a useful mechanism. | **A.** Fund a reconstruction: innovativeness with expense.<br>**B.** Adapt the mechanism for local works: production development with expense.<br>**C.** Sell copies to selected buyers: income. | L2, L4 |
| <a id="tha-fa04"></a>**THA-FA04 — The Captured Ground Crew**<br>Target WV **+1** | Your agent reports that Thanquol failed to take an experimental flying machine but returned with its abandoned winch and ground instructions. His demand for a victory celebration arrives before the quieter report of his retreat. | **A.** Study the lifting apparatus: innovativeness.<br>**B.** Train handlers on the captured winch: army professionalism.<br>**C.** Sell the valuable machinery: income. | L3 |
| <a id="tha-fa05"></a>**THA-FA05 — The Ogre That Broke the Smugglers**<br>Target WV **+2** | Your provincial officer reports that Thanquol's newly acquired Boneripper smashed a smuggling depot while pursuing a debtor. The Grey Seer escaped an ensuing fire, leaving seized contraband and enough records to identify corrupt officials. | **A.** Confiscate the contraband: income.<br>**B.** Investigate the officials: administrative knowledge.<br>**C.** Supply the border guard from the stores: manpower support. | L4, L1 |

#### Enemy — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="tha-eh01"></a>**THA-EH01 — The Fever Beneath the Occupation**<br>Target WV **−2** | Your district physician reports that Thanquol contaminated a supply conduit beneath the occupied tunnels. His own followers also suffered, but he escaped while your workers struggled to isolate the affected stores. | **A.** Replace the supplies and fund relief: treasury loss.<br>**B.** Redeploy workers to containment: administrative power loss.<br>**C.** Seal the damaged district: devastation. | L1 |
| <a id="tha-eh02"></a>**THA-EH02 — The Granary Full of Teeth**<br>Target WV **−2** | Your quartermaster reports that engineered vermin burst into an occupied tunnel granary. Boneripper broke the cordon during the confusion and carried Thanquol away, leaving scattered grain and panicked labourers. | **A.** Replace the lost grain: treasury loss.<br>**B.** Reorganize supply security: military power loss.<br>**C.** Requisition nearby districts: devastation. | L1, L4 |
| <a id="tha-eh03"></a>**THA-EH03 — The Engineer's Missing Night Shift**<br>Target WV **−1** | Your engineer reports that Thanquol raided a military workshop beneath the occupied city. He failed to seize its main engine but escaped with technical notes and several frightened specialists. | **A.** Hire replacements and secure the workshop: treasury loss.<br>**B.** Reconstruct the missing research: administrative power loss.<br>**C.** Conceal the failed protection: prestige loss. | L2 |
| <a id="tha-eh04"></a>**THA-EH04 — The Landing Stage's Broken Winch**<br>Target WV **−1** | Your commander reports that Thanquol tried to steal a supply aircraft from an underground staging shaft. The attempt failed, but Boneripper wrecked the winch while opening their escape route. | **A.** Repair the loading equipment: treasury loss.<br>**B.** Reroute the military deliveries: military power loss.<br>**C.** Announce the attempted theft without admitting the damage: prestige loss. | L3, L4 |
| <a id="tha-eh05"></a>**THA-EH05 — The Bodyguard We Already Killed**<br>Target WV **−1** | Your governor reports that a new Rat Ogre calling forth the same terrified cries of Boneripper broke Thanquol out of an inspection cordon. The previous creature's corpse remains in your custody; the guards had mistaken its death for the Grey Seer's defeat. | **A.** Replace the damaged guard equipment: treasury loss.<br>**B.** Revise identification and pursuit orders: administrative power loss.<br>**C.** Admit the premature victory announcement: prestige loss. | L4 |

#### Enemy — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="tha-ea01"></a>**THA-EA01 — The Governor Survived the Sewer Plot**<br>Target WV **−2** | Your chamberlain reports that Thanquol reached the provincial residence through its drains but failed to murder the governor. He escaped with Boneripper after wrecking the treasury office and setting rival agents against one another. | **A.** Repair the residence and records: treasury loss.<br>**B.** Purge compromised access arrangements: administrative power loss.<br>**C.** Acknowledge the security scandal: prestige loss. | L1 |
| <a id="tha-ea02"></a>**THA-EA02 — The Plague that Spoiled His Own Plan**<br>Target WV **−2** | Your physician reports that Thanquol's contaminated stores sickened his own attackers before they reached their objective. Their retreat still left your food reserves unusable and workers tending the affected district. | **A.** Replace the food and support treatment: treasury loss.<br>**B.** Organize emergency distribution: administrative power loss.<br>**C.** Isolate the district and accept disruption: devastation. | L1 |
| <a id="tha-ea03"></a>**THA-EA03 — The Tower's Stolen Rangefinder**<br>Target WV **−1** | Your engineer reports that Thanquol's raid failed to capture a fortified workshop, but the attackers escaped with a rangefinder and fragments of its drawings. Boneripper tore down a gantry to cover their retreat. | **A.** Replace the rangefinder and gantry: treasury loss.<br>**B.** Revise vulnerable weapon settings: military power loss.<br>**C.** Suppress the embarrassing theft: prestige loss. | L2 |
| <a id="tha-ea04"></a>**THA-EA04 — The Airship He Could Not Keep**<br>Target WV **−2** | Your air-transport officer reports that Thanquol briefly seized a grounded experimental craft but lost it when its crew cut the moorings. His escape wrecked the landing equipment and scattered military cargo across the district. | **A.** Replace the landing equipment: treasury loss.<br>**B.** Reorganize military transport: military power loss.<br>**C.** Leave the ruined yard closed: devastation. | L3 |
| <a id="tha-ea05"></a>**THA-EA05 — The Replacement in the Market Square**<br>Target WV **−1** | Your watch reports that Thanquol used a newly acquired Rat Ogre to break an arrest cordon and escape through a busy market. Witnesses disagree over whether Boneripper had mechanical fittings, scars, or both; several stalls lie crushed. | **A.** Compensate the traders: treasury loss.<br>**B.** Revise the pursuit instructions: administrative power loss.<br>**C.** Let the damaged market recover without official aid: devastation. | L4 |

<a id="catalogue-gro"></a>

### 10.18. Grombrindal

**Fame:** 4/5. **Start:** **Clan Angrund — U37**, Kvinn Wyr **4410** (World's Edge Mountains). **Enemy profile:** A, as defined in section 5. **Home:** Western Dwarf mountain ranges, including the World's Edge Mountains.

#### Lore coverage

| Lore reference | Exploit or background and chronology | Concepts representing it |
|---|---|---|
| **L1** | In the saga of Umthi the Damned, rescued Dwarfs surrounded by Goblins, inspired their counterattack, and vanished afterward; new rescues recall that saga. | [GRO-FH01](#gro-fh01), [GRO-FH04](#gro-fh04), [GRO-FA01](#gro-fa01), [GRO-FA04](#gro-fa04), [GRO-EH01](#gro-eh01), [GRO-EH05](#gro-eh05), [GRO-EA01](#gro-ea01), [GRO-EA04](#gro-ea04) |
| **L2** | Reportedly fought beside Gotrek and Bugman at Karak Varn and pledged further aid to endangered kin; use a recovered account or matching promise without spawning duplicate versions of the other adventurers. | [GRO-FH02](#gro-fh02), [GRO-FH05](#gro-fh05), [GRO-FA03](#gro-fa03), [GRO-EH03](#gro-eh03), [GRO-EA03](#gro-ea03) |
| **L3** | Ancestral protector whose legendary identification with Snorri Whitebeard remains uncertain; old agreements, recognition, and disappearance express that reputation without making him a ruling king. | [GRO-FH03](#gro-fh03), [GRO-FH05](#gro-fh05), [GRO-FA02](#gro-fa02), [GRO-FA04](#gro-fa04), [GRO-FA05](#gro-fa05), [GRO-EH02](#gro-eh02), [GRO-EH04](#gro-eh04), [GRO-EH05](#gro-eh05), [GRO-EA01](#gro-ea01), [GRO-EA02](#gro-ea02), [GRO-EA05](#gro-ea05) |

#### Friendly/neutral — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="gro-fh01"></a>**GRO-FH01 — Umthi's Story at the Barricade**<br>Target WV **+2** | Your hold captain reports that a white-bearded stranger rallied defenders surrounded by raiders and led their counterattack. By the time the survivors sought him, he was gone; their testimony closely recalls Umthi the Damned's saga. | **A.** Train the militia from the account: army tradition.<br>**B.** Restore the saved district: provincial recovery.<br>**C.** Honour the surviving defenders: prestige. | L1 |
| <a id="gro-fh02"></a>**GRO-FH02 — The Three Names on the Old Tablet**<br>Target WV **+1** | Your archivist reports that Grombrindal recovered an account of the stand at Karak Varn naming himself, Gotrek, and Bugman. He demanded that its promise of aid to endangered kin be honoured, then departed alone. | **A.** Restore a neglected kin-relief fund: reduced local unrest with expense.<br>**B.** Preserve the recovered account: administrative knowledge.<br>**C.** Commemorate the old pledge: prestige. | L2 |
| <a id="gro-fh03"></a>**GRO-FH03 — The Ancestor at the Muster**<br>Target WV **+1** | Your muster officer reports that Grombrindal recognized an old regiment's forgotten oath and shamed its quarrelling veterans into helping new recruits. Some call him Snorri Whitebeard; the officer records that identification only as rumour. | **A.** Adopt the veterans' instruction: army professionalism.<br>**B.** Restore the regiment's records: military knowledge.<br>**C.** Celebrate the renewed oath: prestige. | L3 |
| <a id="gro-fh04"></a>**GRO-FH04 — The Miners Beyond the Goblin Ring**<br>Target WV **+2** | Your mine steward reports that Grombrindal broke through raiders surrounding a stranded work party. The miners fought their way out to him and returned with their tools, while their rescuer disappeared into another passage. | **A.** Reopen the saved workings: production development with expense.<br>**B.** Train the mine watch: army tradition.<br>**C.** Repay the rescuers from recovered supplies: reduced local unrest. | L1 |
| <a id="gro-fh05"></a>**GRO-FH05 — The Grudge He Would Not Let Us Forget**<br>Target WV **+1** | Your clan judge reports that Grombrindal returned a stolen family heirloom and produced witnesses to an unfulfilled rescue pledge. His warning echoed the obligation remembered from Karak Varn, leaving the court to settle the descendants' claims. | **A.** Honour the claim and reconcile the families: reduced local unrest.<br>**B.** Preserve the testimony: administrative knowledge.<br>**C.** Recognize the rescue pledge publicly: prestige. | L2, L3 |

#### Friendly/neutral — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="gro-fa01"></a>**GRO-FA01 — The Caravan's White-Bearded Guard**<br>Target WV **+2** | Your governor receives a caravan's account of a white-bearded Dwarf who broke a bandit encirclement, rallied its guards, and vanished before payment could be offered. The survivors have brought recovered trade goods to your customs house. | **A.** Restore the caravan route: local trade recovery.<br>**B.** Train escorts from the survivors' testimony: army professionalism.<br>**C.** Recover duties on the rescued goods: income. | L1 |
| <a id="gro-fa02"></a>**GRO-FA02 — The Agreement Older than the Province**<br>Target WV **+1** | Your magistrate reports that Grombrindal recovered an old mutual-aid agreement from a raided archive and insisted that endangered settlers receive its promised shelter. Witnesses offer contradictory legends about the age of its bearer. | **A.** Honour the shelter agreement: provincial recovery with expense.<br>**B.** Authenticate the archive: administrative knowledge.<br>**C.** Recognize the rescued community: prestige. | L3 |
| <a id="gro-fa03"></a>**GRO-FA03 — The Pledge Carried Far from Karak Varn**<br>Target WV **+1** | Your border officer reports that Grombrindal rescued a mining party and left a copy of the pledge associated with his stand beside Gotrek and Bugman. Neither companion was seen; this was his own intervention. | **A.** Fund the miners' return: prestige with expense.<br>**B.** Preserve their survey records: innovativeness.<br>**C.** Employ willing survivors in local works: production development with expense. | L2 |
| <a id="gro-fa04"></a>**GRO-FA04 — The Foreign Fortress's Last Gate**<br>Target WV **+2** | Your commander reports that Grombrindal held a gate while civilians and a trapped Dwarf detachment escaped. His example rallied the remaining garrison, but he was gone before the relief force arrived. | **A.** Rebuild the gate: local defence with expense.<br>**B.** Train the rallied garrison: army tradition.<br>**C.** Honour those who protected the civilians: prestige. | L1, L3 |
| <a id="gro-fa05"></a>**GRO-FA05 — The King's Name He Never Claimed**<br>Target WV **+1** | Your governor reports that a merchant tried to sell privileges supposedly granted by Snorri Whitebeard. Grombrindal exposed the fraud and returned the victims' seals, refusing to answer questions about his own identity. | **A.** Recover the fraudulent fees: income.<br>**B.** Secure the registry against further forgeries: administrative knowledge.<br>**C.** Publish the victims' vindication: prestige. | L3 |

#### Enemy — home

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="gro-eh01"></a>**GRO-EH01 — The Encirclement Broken from Within**<br>Target WV **−2** | Your siege officer reports that Grombrindal appeared among surrounded defenders and led them through your weakest position. The escaping force carried its wounded and stores away before your reserve could arrive. | **A.** Replace the lost siege stores: treasury loss.<br>**B.** Revise the encirclement: military power loss.<br>**C.** Abandon the damaged siege position: devastation. | L1 |
| <a id="gro-eh02"></a>**GRO-EH02 — The Heirlooms Taken from Our Hall**<br>Target WV **−1** | Your governor reports that Grombrindal entered a trophy hall, defeated its guard, and restored seized heirlooms to their surviving families. He left a formal account of the grudge beside the empty cases. | **A.** Compensate the defeated guard: treasury loss.<br>**B.** Investigate the original confiscations: administrative power loss.<br>**C.** Dismiss the written grievance: prestige loss. | L3 |
| <a id="gro-eh03"></a>**GRO-EH03 — The Promise Behind the Prison Break**<br>Target WV **−2** | Your jailer reports that Grombrindal opened the cells holding a captured Dwarf work party. A pledge recalling Karak Varn was carved into the broken gate; no evidence places Gotrek or Bugman at this escape. | **A.** Replace the damaged prison works: treasury loss.<br>**B.** Reorganize detention security: administrative power loss.<br>**C.** Leave the ruined compound closed: devastation. | L2 |
| <a id="gro-eh04"></a>**GRO-EH04 — The Muster that Turned Against Us**<br>Target WV **−1** | Your commander reports that Grombrindal exposed the breaking of an ancestral service agreement before a conscript muster. Several companies refused to assemble, and he escorted their detained spokesmen away. | **A.** Buy new service contracts: treasury loss.<br>**B.** Reorganize the reduced muster: military power loss.<br>**C.** Endure the repudiation of your authority: prestige loss. | L3 |
| <a id="gro-eh05"></a>**GRO-EH05 — The Mine's Unpaid Debt**<br>Target WV **−2** | Your overseer reports that Grombrindal broke the guard around a captive mining crew and rallied them into an escape. The fugitives carried off the tools your administration had seized from their families. | **A.** Replace the equipment and workers: treasury loss.<br>**B.** Redirect production to other mines: administrative power loss.<br>**C.** Close the damaged workings: devastation. | L1, L3 |

#### Enemy — abroad

| Concept and target weight | What the ruler learns | Possible ruler responses and outcome direction | Lore |
|---|---|---|---|
| <a id="gro-ea01"></a>**GRO-EA01 — The Slaving Expedition's Return**<br>Target WV **−2** | Your frontier officer reports that Grombrindal scattered a slaving expedition and freed its captives. Survivors returned with a written grudge and no explanation of how the old Dwarf vanished after the battle. | **A.** Replace the expedition's losses: treasury loss.<br>**B.** Investigate its failed command: military power loss.<br>**C.** Repudiate the expedition publicly: prestige loss. | L1, L3 |
| <a id="gro-ea02"></a>**GRO-EA02 — The Foreign Oathbreaker's Ledger**<br>Target WV **−1** | Your magistrate reports that Grombrindal defeated a contractor who withheld promised protection from a Dwarf settlement. He left the contractor's ledger with witnesses and carried its detained petitioners to safety. | **A.** Settle the broken contract: treasury loss.<br>**B.** Investigate the approving officials: administrative power loss.<br>**C.** Defend the contractor despite the evidence: prestige loss. | L3 |
| <a id="gro-ea03"></a>**GRO-EA03 — The Karak Varn Petition**<br>Target WV **−1** | Your governor reports that Grombrindal recovered a seized relief fund after its custodians invoked the promise associated with Karak Varn. He acted alone, leaving the fund's accounts nailed to the treasury door. | **A.** Replace the missing treasury allocation: treasury loss.<br>**B.** Audit the confiscation: administrative power loss.<br>**C.** Deny the petitioners' claim: prestige loss. | L2 |
| <a id="gro-ea04"></a>**GRO-EA04 — The Caravan We Had Surrounded**<br>Target WV **−2** | Your commander reports that Grombrindal rallied an encircled caravan and broke its captives out through a supply camp. He disappeared after the rescued guards reached a safe route, leaving your camp stripped of provisions. | **A.** Replace the camp's stores: treasury loss.<br>**B.** Reorganize interception tactics: military power loss.<br>**C.** Requisition nearby settlements: devastation. | L1 |
| <a id="gro-ea05"></a>**GRO-EA05 — The Ancestor's Unanswered Grudge**<br>Target WV **−1** | Your court receives a formal grievance after Grombrindal defeated a provincial officer holding stolen clan relics. The officer survived, the relics are gone, and witnesses disagree whether the rescuer was an ancient king or simply an indomitable traveller. | **A.** Compensate the affected households: treasury loss.<br>**B.** Investigate the officer's collection: administrative power loss.<br>**C.** Refuse the grievance and accept the shame: prestige loss. | L3 |

### Catalogue completeness

All 18 adventurers have exactly five friendly/neutral home, five friendly/neutral abroad, five enemy home, and five enemy abroad concepts. Every concept has 2–4 proposed responses and a signed event-weight target. All 68 lore entries are represented, with chronology and adaptation limits retained. Starting assignments, fixed presence modifiers, enemy profiles, and the shared movement rule remain those recorded above.
