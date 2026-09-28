# Landless enclave countries: E00–E99

All 100 entries from the approved [regional catalogue](../Minor%20Faction%20Research.md) are implemented as dormant countries at **2502.11.11**. Each has one core on its listed province. Existing ownership, control, culture, religion, development, buildings, and other province history are unchanged; unowned sites remain unowned. No enclave is automatically released or spawned.

Each country has a registered tag, country definition, history, culturally appropriate name pools and units, English name and adjective, a unique national idea group, and a 128×128 TGA flag. The 100 unique intro events have been removed at the user's request. Country-history capitals are preferred future seats and do not transfer their provinces.

The **700 individual national ideas each total Weighing Value 10** using `Dev Stuff/Examples/Balance Guide.txt`. Traditions total 20 and ambitions 10, following the mod's country-idea convention.

## Enclave provinces and rooting out factions

Every listed province starts with a unique **[Faction Name] Enclave** permanent modifier. Each applies exactly `local_unrest = 4`, `min_local_autonomy = 33`, and `local_autonomy = 0.05`. It has `duration = -1` and uses `add_permanent_province_modifier`, so conquest does not remove it. The Balance Guide does not directly price these local modifiers; their values follow the explicit user instruction.

Ownership of that province while its modifier remains exposes **Root Out [Faction Name]**. Taking the decision requires peace, control of the enclave province, and no existing rebel armies (`NOT = { num_of_rebel_armies = 1 }`). These requirements apply to players and AI; a temporarily blocked decision remains visible. It has no resource cost. It removes that faction's modifier, restores its original core if it has expired, and spawns one `size = 3` stack of `nationalist_rebels` (EU4's separatist type). Actual regiment counts scale with province development and military technology; size 3 is a multiplier, not three regiments.

The rebels have the faction's primary culture and religion, `friend` and `separatists_target` set to its E## tag, and a named leader and dynasty/byname. `win = yes` makes them immediately occupy the province. Legal ownership, the province population's culture and religion, and other modifiers are unchanged. Removing the enclave modifier makes its decision disappear, so it cannot be repeated there. The faction's core remains after the confrontation.

AI owners check yearly and additionally require at least +1 stability, 90% of maximum manpower, an army at least 90% of land force limit, and a positive monthly balance. Profit uses `current_income_balance = 0.01` (at least 0.01 ducats per month), excluding both deficits and exact break-even. These extra readiness and profit requirements do not restrict the player.

Each decision's `provinces_to_highlight` selects only its faction's assigned enclave province, including while that faction is landless. The [EU4 decision schema](https://github.com/cwtools/cwtools-eu4-config/blob/master/decisions/decisions.cwt) supports province highlighting but does not expose the event-style `goto` field or a country diplomacy target. [Trigger definitions](https://github.com/cwtools/cwtools-eu4-config/blob/master/triggers.cwt) and the installed game's scripts were checked for the readiness and income conditions.

The [leader reference](Leaders.md) distinguishes documented lore characters, Total War leaders, a canonical unnamed office, and original leaders. Historical surnames or established epithets use the engine's `leader_dynasty` field; mononymous characters have an explicit empty dynasty. Original names are not presented as historical lore.

All 100 modifier descriptions give the enclave's leader, local refuge, and present threat. The decisions add a faction-specific confrontation paragraph. The [description source notes](Description%20Sources.md) record checked historical details and distinguish them from the approved local and chronological adaptations.

## Silent emergence setup

Creation, release, and province-owner-change hooks apply the enclave's country identity silently once it owns a city, guarded by `war_enclave_identity_initialized`. A yearly fallback catches scripted tag changes. No enclave-specific intro or replacement event is fired. The country's listed cultures, religion, government, reforms, technology, ideas, racial modifiers, alignment, and vision are restored without changing province population or legal ownership.

Ordinary vassal-release eligibility can still depend on province culture, which intentionally differs from several enclave cultures. The new decisions explicitly select the faction's separatist tag and rebel culture. Game testing is still required to verify the full engine path from rebellion through independence; this has not been inferred from static checks alone.

## Supporting definitions

- All enclaves use existing religions. Cluster Eye Tribe (E02) and Root-Eye Brood (E39) use **Gork n' Mork**. Sog'Kog (E20), Rime-Eaters (E23), Badwater (E27), White Hunger (E47), Last Hearth (E48), First Hunger (E70), Rimejaw (E77), and the Golden Magus (E30) use **Animist**, representing local customs and spirit traditions. The existing religion modifiers are unchanged.
- Corrected the missing equals sign in the existing Southern Trade Republic eligibility block, which Nuevo Luccini uses.
- **Monster Clans:** a generic tribal reform for the monster enclaves that should not be governed by specifically Fimir institutions. Net WV 10: +15% manpower, +15% land force limit, +7.5% development cost.

## Flags

The [flag source ledger](Flag%20Sources/sources.md) distinguishes described lore heraldry from original artwork. All 100 final files were individually illustrated with the built-in imagegen tool; two adapt explicit lore heraldry descriptions and 98 are original interpretations after the online search. No downloaded flag image was incorporated. Exact prompts and generation provenance are retained alongside 512×512 PNG masters. Aucassin's final white-field correction is documented in `Flag Sources/E10-revision.json`.

- [E00–E19](flags_00_19.png)
- [E20–E39](flags_20_39.png)
- [E40–E59](flags_40_59.png)
- [E60–E79](flags_60_79.png)
- [E80–E99](flags_80_99.png)

## Validation

Run `python3 "Dev Stuff/Enclave Countries/validate.py"` from the mod root. The [latest report](validation.json) checks registration, local references, one starting core per tag, zero enclave ownership, preservation of the original province content, non-capital placement, idea budgets, all 100 modifier values, decision visibility, province highlighting, shared requirements, AI readiness, effect order, all rebel fields including size 3, removal of the 100 intro events, silent identity hooks, BOM encoding, and flag files. Static scenarios evaluate the decision predicates at the AI thresholds and just below them, in war, under occupation, with existing rebel armies, at break-even, and in deficit. They also verify that non-owners cannot use the decisions and that removal makes them unavailable. These scenarios do not replace an in-game UI and engine check.

The game has not been launched for this batch. In a new campaign, inspect the modifiers, take representative Root Out decisions, and verify leader names, culture/religion, immediate rebel occupation, and independence into the correct tag. Also check conquest persistence and silent country identity setup. History-file modifiers and cores require a new campaign; existing saves are not automatically migrated.

## Country register

The [resolved JSON manifest](countries.json) records every country, culture, religion, reform, province, idea budget, enclave modifier, decision, and rebel setup. This table is the quick implementation index.

| Tag | Country | Core province | Country faith | Government / reform | Rebel leader |
|---|---|---|---|---|---|
| E00 | Zacharias' Domain | 139 — Forest of Shadows | Vampiric | theocracy: Necromancer's Domain | Zacharias the Everliving |
| E01 | Dieter Helsnicht's Domain | 141 — Ferlangen | Nagashi | theocracy: Necromancer's Domain | Dieter Helsnicht |
| E02 | Cluster Eye Tribe | 96 — Deinste | Gork n' Mork | tribal: Greenskin Tribe | Vish Venombarb |
| E03 | Brass Keep | 393 — Dripping Peak | Nurglite | chaos_gov: Mandate of Chaos, Chaos Warband | Egil Rusthand |
| E04 | House von Wittgenstein | 19 — Wittgendorf | Chaos Undivided | monarchy: Chaos Undivided Monarchy | Margritte von Wittgenstein |
| E05 | Cult of the Red Crown | 105 — Delberz | Tzeentchian | theocracy: Tzeentchian Theocracy | Master of Change |
| E06 | Slugtongue's Warherd | 63 — Nattern Forest | Chaos Undivided | tribal: Call of the Beastmen | Slugtongue |
| E07 | Drycha's Wargrove | 182 — Borkum | The Asrai Pantheon | tribal: The Asrai Pantheon Tribe | Drycha |
| E08 | Morghur's Warherd | 321 — Beaussons | Chaos Undivided | tribal: Call of the Beastmen | Morghur the Shadowgave |
| E09 | Red Duke's Exiles | 241 — Derrevin Libre | Vampiric | monarchy: Midnight Aristocracy | The Red Duke |
| E10 | Aucassin's Household | 317 — Yremy | Vampiric | monarchy: Midnight Aristocracy | Aucassin |
| E11 | Brachnar's Laboratory | 262 — Montlac | Vampiric | theocracy: Necromancer's Domain | Brachnar |
| E12 | Bowmen of Bergerac | 239 — Vignoble | Grail | republic: Grail Republic | Bertrand the Brigand |
| E13 | Coeddil's Wildwood | 776 — Cythral Forest | The Asrai Pantheon | tribal: The Asrai Pantheon Tribe | Coeddil |
| E14 | Knights of Irrana | 538 — Llaqueno | Vampiric | monarchy: Midnight Aristocracy | Armand de Sangrivage |
| E15 | Long Drong's Anchorage | 627 — Caprio | Ancestor Gods | republic: pirate_republic_reform | Long Drong Slayer |
| E16 | Shadewraith Haven | 561 — Grotta | Nagashi | republic: The Vampire Coast | Vangheist |
| E17 | Golgfag's Winter Camp | 413 — Heldegrad | The Great Maw | republic: Mercenary Company | Golgfag Maneater |
| E18 | Wintertooth | 1146 — Lair of the Troll King | Chaos Undivided | tribal: Monster Clans | Throgg the Troll King |
| E19 | Beasts of Telldros | 344 — Skraevold | Chaos Undivided | tribal: Call of the Beastmen | Kharzulg Stormscar |
| E20 | Sog'Kog's Feeding Ground | 338 — Fort Straghov | Animist | tribal: Monster Clans | Sog'Kog |
| E21 | Black Ogham Circle | 1173 — Dunnok | Chaos Undivided | theocracy: Chaos Undivided Theocracy | Maelor Blackreed |
| E22 | Brothers' Giant Moot | 1182 — Everpeak | Druidism | tribal: Druidic Clan Moot | Bologs |
| E23 | Rime-Eater Clans | 449 — Mount Hellspire | Animist | tribal: Call of the Beastmen | Hrogg Rimehide |
| E24 | Rabidscar Remnant | 4484 — Snag | Horned Rat | monarchy: Rule of the Fittest-Strongest | Furblak |
| E25 | Drachenfels Restorationists | 6 — Castle Drachenfels | Nagashi | theocracy: Necromancer's Domain | Albrecht Gravenhorst |
| E26 | Ember-Script Heretics | 4509 — Vogg | Hashut | monarchy: Hashut Monarchy | Durgan Emberbrand |
| E27 | Badwater Hagdom | 190 — Felwing Cave | Animist | tribal: Monster Clans | Grulma Bogbelly |
| E28 | Boglar-Fimir Compact | 154 — Stinkwater Fen | Chaos Undivided | tribal: Greenskin Tribe | Skibbit Mireclaw |
| E29 | Black Lantern Prospectors | 4596 — Redstone Underpass | Nagashi | theocracy: Necromancer's Domain | Borri Graveshaft |
| E30 | Golden Magus' Refuge | 987 — Al-Qayid | Animist | republic: pirate_republic_reform | Golden Magus |
| E31 | Alhazred's Observatory | 1033 — Sharikah | Nagashi | theocracy: Necromancer's Domain | Abdul Alhazred |
| E32 | Moon-Well Keepers | 961 — Zafira Oasis | Nehekharan | theocracy: Golden Hieorocracy | Nadir al-Qamar |
| E33 | Free Spears of the Copper Dunes | 1772 — Dhiban | The One Faith | republic: Mercenary Company | Hamid al-Nahas |
| E34 | Court of the Cursed Scarab | 832 — Khepesh | Nehekharan | monarchy: Nehekharan Monarchy | Apophas |
| E35 | Rikek Ash-Warrens | 4388 — Cripple Peak | Horned Rat | monarchy: Rule of the Fittest-Strongest | Skreev Ashsnout |
| E36 | Black Oasis Riders | 848 — Phaktra | The One Faith | tribal: Tribe of the Sacred Charge | Salim al-Rimal |
| E37 | Clan Festerlingus | 4887 — Cuexotl Wilds | Horned Rat | theocracy: Horned Rat Theocracy | Pustik Rotthroat |
| E38 | Hellbeard's Cinder Anchorage | 4331 — Scaleback Coast | Hashut | republic: pirate_republic_reform | Abnagg Hellbeard |
| E39 | Root-Eye Brood | 4287 — Nahuontl Peaks | Gork n' Mork | tribal: Greenskin Tribe | Zikrit Rootfang |
| E40 | River of Teeth Covenant | 4904 — Flooded Jungle | Vampiric | monarchy: Midnight Aristocracy | Zafira Nightwater |
| E41 | Braugh's Corpse-Train | 2210 — Brimstone Pass | The Great Maw | republic: Mercenary Company | Braugh Slavelord |
| E42 | Sneaky Gits of Gash Kadrak | 815 — Zharr Outskirts | Hobgoblin Shamanism | tribal: Hobgoblin Shamanism Tribe | Nagrit Shivtail |
| E43 | Black Tally Rebellion | 1983 — Blackfire | Gork n' Mork | tribal: Greenskin Tribe | Grakk Chainbreaker |
| E44 | Unchained Furnace | 2162 — Black Smoke Peaks | Ancestor Gods | monarchy: Dwarfen Kingdom | Dorin Shacklecleaver |
| E45 | Ghuth's Spawnchompers | 2752 — Bloodpeak | Chaos Undivided | tribal: Rule of the Largest | Ghuth Spawnchomper |
| E46 | Bezer's Small Empire | 2784 — Gutbuster's Gate | Gork n' Mork | tribal: Greenskin Tribe | Bezer |
| E47 | White Hunger | 2792 — Choketooth Vale | Animist | tribal: Rule of the Largest | Urrgh Whiteclaw |
| E48 | Last Hearth of the Tall Ones | 2764 — Giant's Ridge | Animist | tribal: Monster Clans | Hrol Hearthkeeper |
| E49 | Oglah Khan's Exiles | 4036 — Heicheng | Hobgoblin Shamanism | republic: Mercenary Company | Oglah Khan |
| E50 | Ash-Hoof Herd | 4038 — Tuoba | Khornate | tribal: Call of the Beastmen | Khorgh Ashhoof |
| E51 | Broken Harness Freehold | 2669 — Icescar | Harmony | republic: Harmony Republic | Shun Liu |
| E52 | Cult of the Painted Skin | 2998 — Xienxen | Tzeentchian | theocracy: Tzeentchian Theocracy | Xiu Shen |
| E53 | Vermilion Tax Revolt | 2923 — Radiant Plains | Harmony | republic: Harmony Republic | Bao Zhang |
| E54 | Jade Coffin Society | 2843 — Minghua | Vampiric | monarchy: Midnight Aristocracy | Mei Jiang |
| E55 | Copper Tail Refuge | 2864 — Sapphire Grove | The Thousand Gods | republic: The Thousand Gods Republic | Kavi Copper-Tail |
| E56 | Bengals of the Tiger's Eye | 4071 — Kushan | The Thousand Gods | republic: The Thousand Gods Republic | Rajar Stripeclaw |
| E57 | Red Banquet Court | 4073 — Panchala | Vampiric | monarchy: Midnight Aristocracy | Gorakka Redgullet |
| E58 | Ash Lotus Ascetics | 4252 — Kushari Plains | Nagashi | theocracy: Necromancer's Domain | Harendra Ashlotus |
| E59 | Emerald Throat Brood | 4109 — Ceylon | Ouroboros | theocracy: Ouroboros Theocracy | Ssaritha Emerald-Throat |
| E60 | Moltless Sepulchre | 2967 — Dragonfall | Nagashi | theocracy: Necromancer's Domain | Ssilak Moltless |
| E61 | Unbitten League | 2949 — Silvermist Hills | The Thousand Gods | republic: The Thousand Gods Republic | Devendra Nagesh |
| E62 | Hollow Gong Warren | 2932 — Silent Lotus | Horned Rat | monarchy: Rule of the Fittest-Strongest | Chikkit Gonggnaw |
| E63 | Mangrove Eye Court | 4256 — Zhanggan Wetlands | Chaos Undivided | tribal: Fimir Tribe | Morrga Mangrove-Eye |
| E64 | Empty Sheath League | 4778 — Spirit of the Crane | Harmony | republic: Mercenary Company | Akihiro Kuroda |
| E65 | Cinder-Eye Burrow | 4791 — Iseki | Gork n' Mork | tribal: Greenskin Tribe | Skarrik Cinder-Eye |
| E66 | Antlered Hunger | 2425 — Ixtoc | Chaos Undivided | tribal: Call of the Beastmen | Ghorak Thornhorn |
| E67 | Unmoored Spears | 4753 — Elithis Outpost | The Cytharai | republic: pirate_republic_reform | Aelar Wavebreaker |
| E68 | Itz-Itza | 4840 — Pyooshupya | Old Ones | tribal: Old Ones Tribe | Itz-Huax |
| E69 | River-Ruin Chainport | 4842 — Noigo | Hashut | theocracy: Sorcerer's Conclave | Zarkhul Ironwake |
| E70 | Cave of the First Hunger | 4852 — Xcha | Animist | tribal: Monster Clans | Gor-Ulk |
| E71 | Scourge of Khaine | 1936 — Darkspire | The Cytharai | theocracy: The Cytharai Theocracy | Nocrusith |
| E72 | Cult of Excess | 1800 — Circle of Night | Slaaneshi | theocracy: Slaaneshi Theocracy | Arathar |
| E73 | Blackfang's Worshippers | 1842 — Arithor | Chaos Undivided | tribal: Call of the Beastmen | Gharr Blackfang |
| E74 | Blackpine Autarii | 2046 — Skarnshade | The Cytharai | tribal: The Cytharai Tribe | Draleth Blackpine |
| E75 | Hotek's Lost Apprentices | 2594 — Shadowfrost | The Cadai | republic: The Cadai Republic | Vaelir Ashforge |
| E76 | Deadwood Unbound | 1989 — Deadwood | Imperial Pantheon | republic: Imperial Pantheon Republic | Hakon Freedhand |
| E77 | Rimejaw Families | 2582 — Nightair | Animist | tribal: Monster Clans | Rulgh Rimejaw |
| E78 | Vashnaar's Foothold | 2105 — Gorepeak | Chaos Undivided | chaos_gov: Mandate of Chaos, Chaos Warband | Vashnaar the Tormentor |
| E79 | Cylostra's Drowned | 2104 — Blightward | Nagashi | republic: The Vampire Coast | Cylostra Direfin |
| E80 | Azure Fang Brood | 2351 — Tlacox | Old Ones | tribal: Old Ones Tribe | Tzak-Huax |
| E81 | Port Reaver | 2318 — Port Reaver | Myrmidian | republic: pirate_republic_reform | Lorenzo Saltavento |
| E82 | Swamp Town | 2319 — Swamp Town | Imperial Pantheon | republic: Southern Old World Cults Republic | Konrad Reedhaven |
| E83 | Sven's River Company | 2387 — Xotlzax | Ancestor Gods | republic: Mercenary Company | Sven Hasselfriesian |
| E84 | Bregonne | 2384 — Axmin | Grail | monarchy: Grail Monarchy | Marcel de Parravon |
| E85 | Nuevo Luccini | 2328 — Tzul'cata | Myrmidian | republic: Southern Trade Republic | Marco Venturi |
| E86 | Amber Maw Expedition | 2514 — Xolt | The Great Maw | republic: Mercenary Company | Borgut Ambermaw |
| E87 | Ashen Plaque Covenant | 2487 — Xaltlan | Dragon Cults | tribal: Clutch-Bound Clan | Xol-Tzek |
| E88 | Culchan Feather Exiles | 4371 — Southern Plains | Old Ones | tribal: Amazon Tribe | Itzara Culchanfeather |
| E89 | Deep Drum Hold | 2520 — Izaltl | Ancestor Gods | monarchy: Dwarfen Kingdom | Grundi Deepdrum |
| E90 | Clan Skaar | 589 — Falco | Horned Rat | monarchy: Rule of the Fittest-Strongest | Krizzik Oreclaw |
| E91 | Clan Skaul | 29 — Weissbuck | Horned Rat | monarchy: Rule of the Fittest-Strongest | Skaalrik Dreamfang |
| E92 | Clan Sleekit | 7 — Fielbach | Horned Rat | monarchy: Rule of the Fittest-Strongest | Shipgnawer Nikkitt |
| E93 | Clan Septik | 33 — Dotternbach | Horned Rat | theocracy: Horned Rat Theocracy | Blightskab |
| E94 | Clan Kreepus | 2961 — Eaglecrest | Horned Rat | monarchy: Rule of the Fittest-Strongest | Garrott of Mordheim |
| E95 | Clan Feesik | 4875 — Mangrove Delta | Horned Rat | theocracy: Horned Rat Theocracy | Rikzik Seepage |
| E96 | Clan Gratzz | 2490 — Xotec | Horned Rat | theocracy: Horned Rat Theocracy | Gratzik Rotwhisker |
| E97 | Clan Rikket | 2344 — Ratscar | Horned Rat | monarchy: Rule of the Fittest-Strongest | Rikkaz Warpwake |
| E98 | Clan Skuttle | 623 — Dusklair | Horned Rat | monarchy: Rule of the Fittest-Strongest | Skuttik Bilgetail |
| E99 | Clan Gristlecrack | 4400 — Snikt | Horned Rat | monarchy: Rule of the Fittest-Strongest | Grissk Fleshsuture |
