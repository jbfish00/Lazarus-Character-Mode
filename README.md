# Character Mode for Pokemon Lazarus v2.0

An opt-in game mode where you play as an iconic Pokemon character — a
protagonist, rival, gym leader, Elite Four member, champion, villain, or
anime cast member — and are restricted to catching and keeping only that
character's canon roster (as documented on Bulbapedia, expanded to full
evolution families). 179 characters, Generations 1 through 9.

Ported from the original Character Mode built for Pokemon ROWE, following
the Radical Red port.

## What you need

- A **clean Pokemon Emerald (U)** ROM you obtained legally
  (the usual "TrashMan" dump, CRC32 `1F1C08FB`).
- The **official Pokemon Lazarus v2.0 patch** by Nemo622
  (`Lazarus v2 Patch.bps`).
- This project's `lazarus_cm.bps`.
- [Flips](https://github.com/Alcaro/Flips) or any BPS patcher.

This project distributes a patch only, never a ROM.

## Applying the patch (two steps)

Our patch applies **on top of the official Lazarus patch**, never to clean
Emerald directly:

```
flips --apply "Lazarus v2 Patch.bps" emerald.gba lazarus-v2.gba
flips --apply lazarus_cm.bps lazarus-v2.gba lazarus_cm.gba
```

(The intermediate `lazarus-v2.gba` must have SHA-1
`7dcdc7e280bc4631487e13dd37e6e0cea04adea6` — see `rom.sha1`.)

## Activating Character Mode

Lazarus's cheat codes are entered at the **desk in Acrisia University**
(the professor's building where you start). Interact with the desk and it
asks for a cheat code — Character Mode rides that same system:

1. At the text-entry screen, **type your character's code** from the
   tables below (codes are the character's name with spaces and
   punctuation removed, e.g. `LtSurge` for Lt. Surge — case doesn't
   matter).
2. You'll get a confirmation message and your character's starter
   Pokemon at Lv. 5.
3. From then on, catching or receiving any Pokemon **not on your
   character's roster sends it straight to the PC** instead of your
   party. Everything on-roster (including every evolution of a roster
   Pokemon) joins your party normally.

Notes:
- Eggs are always exempt (they join the party; enforcement applies to
  hatched/caught/gifted Pokemon).
- Your first party slot is never blocked (soft-lock protection).
- **DexNav catches are enforced** like any other catch.
- **In-game trades are enforced**: all four trade NPCs politely refuse a
  trade whose incoming Pokemon is off your roster.
- **Wild encounters occasionally give you a roster Pokemon.** Grass/cave,
  surfing, rock smash, and every fishing rod tier all have a 1-in-10 chance
  to swap the wild Pokemon for a random member of your character's roster
  (never a legendary/mythical one), at whichever evolution stage best fits
  the level you would have encountered. The other 9 times out of 10 it's a
  completely normal wild encounter. This never affects gift Pokemon or
  scripted story encounters.
- All of Lazarus's own cheat codes (`ILOVEALOLA`, the `MONO...` codes,
  etc.) still work unchanged.

### Debug / utility codes

| Code | Effect |
|---|---|
| `CMDbgOff` | Turn Character Mode off (clears the flag and character selection) |
| `CMDbgGive1` | Test code: gives your character's own starter (on-roster -> joins party) |
| `CMDbgGive2` | Test code: gives a Lv. 5 Ekans (off-roster for most -> goes to PC) |

## Known limitations

- Characters keep the normal player sprite (no custom character sprites
  yet).
- Some characters' canon rosters include Pokemon that are not obtainable
  in Lazarus's curated dex; their rosters were validated against the
  official Encounters guide so every character has obtainable Pokemon,
  but roster species missing from Lazarus simply never appear.

## Character codes


### Generation 1

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Red` | Red | protagonist | Pikachu |
| `Leaf` | Leaf | protagonist | Eevee |
| `Blue` | Blue | champion | Aerodactyl |
| `Lance` | Lance | champion | Dratini |
| `Lorelei` | Lorelei | Elite Four | Lapras |
| `Bruno` | Bruno | Elite Four | Dratini |
| `Agatha` | Agatha | Elite Four | Gastly |
| `Koga` | Koga | Elite Four | Chinchou |
| `Brock` | Brock | gym leader | Onix |
| `Misty` | Misty | gym leader | Buizel |
| `LtSurge` | Lt. Surge | gym leader | Pikachu |
| `Erika` | Erika | gym leader | Bellsprout |
| `Sabrina` | Sabrina | gym leader | Chingling |
| `Blaine` | Blaine | gym leader | Growlithe |
| `Giovanni` | Giovanni | villain | Bellsprout |
| `Ash` | Ash | anime | Pikachu |
| `Gary` | Gary | anime | Aerodactyl |
| `Ritchie` | Ritchie | anime | Pikachu |
| `Tracey` | Tracey | anime | Scyther |
| `Jessie` | Jessie | anime | Ekans |
| `James` | James | anime | Bellsprout |

### Generation 2

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Ethan` | Ethan | protagonist | Cyndaquil |
| `Kris` | Kris | protagonist | Totodile |
| `Lyra` | Lyra | protagonist | Chikorita |
| `Will` | Will | Elite Four | Natu |
| `Karen` | Karen | Elite Four | Eevee |
| `Janine` | Janine | gym leader | Spinarak |
| `Falkner` | Falkner | gym leader | Hoothoot |
| `Bugsy` | Bugsy | gym leader | Scyther |
| `Whitney` | Whitney | gym leader | Aipom |
| `Morty` | Morty | gym leader | Gastly |
| `Chuck` | Chuck | gym leader | Poliwag |
| `Jasmine` | Jasmine | gym leader | Onix |
| `Pryce` | Pryce | gym leader | Swinub |
| `Clair` | Clair | gym leader | Aerodactyl |
| `Silver` | Silver | rival | Totodile |
| `Archer` | Archer | villain | Houndour |
| `Ariana` | Ariana | villain | Ekans |

### Generation 3

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Brendan` | Brendan | protagonist | Aron |
| `May` | May | protagonist | Torchic |
| `Steven` | Steven | champion | Aerodactyl |
| `Wallace` | Wallace | champion | Barboach |
| `Sidney` | Sidney | Elite Four | Corphish |
| `Phoebe` | Phoebe | Elite Four | Duskull |
| `Glacia` | Glacia | Elite Four | Spheal |
| `Drake` | Drake | Elite Four | Pichu |
| `Roxanne` | Roxanne | gym leader | Nosepass |
| `Brawly` | Brawly | gym leader | Heracross |
| `Wattson` | Wattson | gym leader | Magnemite |
| `Flannery` | Flannery | gym leader | Torkoal |
| `Norman` | Norman | gym leader | Aipom |
| `Winona` | Winona | gym leader | Swablu |
| `Tate` | Tate | gym leader | Baltoy |
| `Liza` | Liza | gym leader | Baltoy |
| `Juan` | Juan | gym leader | Barboach |
| `Wally` | Wally | rival | Ralts |
| `Maxie` | Maxie | villain | Numel |
| `Archie` | Archie | villain | Dratini |
| `Drew` | Drew | anime | Budew |

### Generation 4

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Lucas` | Lucas | protagonist | Cranidos |
| `Dawn` | Dawn | protagonist | Aipom |
| `Cynthia` | Cynthia | champion | Budew |
| `Aaron` | Aaron | Elite Four | Skorupi |
| `Bertha` | Bertha | Elite Four | Barboach |
| `Flint` | Flint | Elite Four | Buizel |
| `Lucian` | Lucian | Elite Four | Bronzor |
| `Roark` | Roark | gym leader | Cranidos |
| `Gardenia` | Gardenia | gym leader | Budew |
| `Maylene` | Maylene | gym leader | Aipom |
| `CrasherWak` | Crasher Wake | gym leader | Buizel |
| `Fantina` | Fantina | gym leader | Bronzor |
| `Byron` | Byron | gym leader | Shieldon |
| `Candice` | Candice | gym leader | Snorunt |
| `Volkner` | Volkner | gym leader | Aipom |
| `Barry` | Barry | rival | Budew |
| `Cyrus` | Cyrus | villain | Sneasel |
| `Mars` | Mars | villain | Bronzor |
| `Jupiter` | Jupiter | villain | Stunky |
| `Saturn` | Saturn | villain | Bronzor |
| `Paul` | Paul | anime | Aron |
| `Zoey` | Zoey | anime | Aipom |
| `Nando` | Nando | anime | Budew |

### Generation 5

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Hilda` | Hilda | protagonist | Eevee |
| `Nate` | Nate | protagonist | Growlithe |
| `Rosa` | Rosa | protagonist | Lillipup |
| `Alder` | Alder | champion | Archen |
| `Iris` | Iris | champion | Archen |
| `Shauntal` | Shauntal | Elite Four | Litwick |
| `Marshal` | Marshal | Elite Four | Timburr |
| `Grimsley` | Grimsley | Elite Four | Houndour |
| `Caitlin` | Caitlin | Elite Four | Gothita |
| `Cilan` | Cilan | gym leader | Pansage |
| `Chili` | Chili | gym leader | Pansear |
| `Cress` | Cress | gym leader | Panpour |
| `Lenora` | Lenora | gym leader | Gothita |
| `Burgh` | Burgh | gym leader | Dwebble |
| `Elesa` | Elesa | gym leader | Blitzle |
| `Clay` | Clay | gym leader | Baltoy |
| `Skyla` | Skyla | gym leader | Ducklett |
| `Brycen` | Brycen | gym leader | Cubchoo |
| `Drayden` | Drayden | gym leader | Dratini |
| `Cheren` | Cheren | gym leader | Lillipup |
| `Roxie` | Roxie | gym leader | Grimer |
| `Marlon` | Marlon | gym leader | Shellder |
| `Bianca` | Bianca | rival | Blitzle |
| `Hugh` | Hugh | rival | Grimer |
| `N` | N | rival | Zorua |
| `Ghetsis` | Ghetsis | villain | Munna |
| `Colress` | Colress | villain | Cubchoo |
| `Trip` | Trip | anime | Dwebble |

### Generation 6

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Calem` | Calem | protagonist | Chespin |
| `Serena` | Serena | protagonist | Fennekin |
| `Diantha` | Diantha | champion | Ralts |
| `Malva` | Malva | Elite Four | Fennekin |
| `Siebold` | Siebold | Elite Four | Clauncher |
| `Wikstrom` | Wikstrom | Elite Four | Honedge |
| `Drasna` | Drasna | Elite Four | Skrelp |
| `Viola` | Viola | gym leader | Honedge |
| `Grant` | Grant | gym leader | Tyrunt |
| `Korrina` | Korrina | gym leader | Chespin |
| `Ramos` | Ramos | gym leader | Skiddo |
| `Clemont` | Clemont | gym leader | Helioptile |
| `Valerie` | Valerie | gym leader | Eevee |
| `Wulfric` | Wulfric | gym leader | Pichu |
| `Shauna` | Shauna | rival | Chespin |
| `Lysandre` | Lysandre | villain | Magikarp |
| `Alain` | Alain | anime | Chespin |
| `Sawyer` | Sawyer | anime | Clauncher |

### Generation 7

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Elio` | Elio | protagonist | Popplio |
| `Selene` | Selene | protagonist | Rowlet |
| `Kukui` | Kukui | champion | Litten |
| `Hau` | Hau | champion | Pichu |
| `Molayne` | Molayne | Elite Four | Grubbin |
| `Kahili` | Kahili | Elite Four | Pikipek |
| `Acerola` | Acerola | Elite Four | Cubone |
| `Hala` | Hala | gym leader | Crabrawler |
| `Olivia` | Olivia | gym leader | Rockruff |
| `Nanu` | Nanu | gym leader | Meowth |
| `Hapu` | Hapu | gym leader | Mudbray |
| `Gladion` | Gladion | rival | Cubone |
| `Guzma` | Guzma | villain | Wimpod |
| `Plumeria` | Plumeria | villain | Salandit |
| `Lusamine` | Lusamine | villain | Stufful |
| `Lillieanim` | Lillie (anime) | anime | Vulpix |
| `Kiaweanime` | Kiawe (anime) | anime | Corphish |
| `Lanaanime` | Lana (anime) | anime | Popplio |
| `Mallowanim` | Mallow (anime) | anime | Bounsweet |
| `Sophocles` | Sophocles | anime | Togedemaru |

### Generation 8

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Leon` | Leon | champion | Amaura |
| `Milo` | Milo | gym leader | Applin |
| `Nessa` | Nessa | gym leader | Magikarp |
| `Kabu` | Kabu | gym leader | Sizzlipede |
| `Bea` | Bea | gym leader | Dracovish |
| `Allister` | Allister | gym leader | Gastly |
| `Opal` | Opal | gym leader | Dracovish |
| `Gordie` | Gordie | gym leader | Lapras |
| `Melony` | Melony | gym leader | Lapras |
| `Piers` | Piers | gym leader | Zigzagoon |
| `Raihan` | Raihan | gym leader | Dreepy |
| `Bede` | Bede | rival | Caterpie |
| `Marnie` | Marnie | rival | Cufant |
| `Rose` | Rose | villain | Cufant |
| `Goh` | Goh | anime | Cubone |
| `Chloe` | Chloe | anime | Eevee |

### Generation 9

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Geeta` | Geeta | champion | Chespin |
| `Nemona` | Nemona | champion | Pawmi |
| `Rika` | Rika | Elite Four | Wooper |
| `Poppy` | Poppy | Elite Four | Tinkatink |
| `Hassel` | Hassel | Elite Four | Applin |
| `Katy` | Katy | gym leader | Heracross |
| `Brassius` | Brassius | gym leader | Applin |
| `Iono` | Iono | gym leader | Charcadet |
| `Kofu` | Kofu | gym leader | Crabrawler |
| `Larry` | Larry | gym leader | Flamigo |
| `Ryme` | Ryme | gym leader | Fuecoco |
| `Tulip` | Tulip | gym leader | Florges |
| `Grusha` | Grusha | gym leader | Cubchoo |
| `Arven` | Arven | rival | Eevee |
| `Penny` | Penny | rival | Eevee |

## Credits

- **Pokemon Lazarus** by Nemo622 — this project modifies nothing about
  the hack's own content and requires the official patch.
- Character rosters from **Bulbapedia**.
- Character Mode concept and reference implementation: the Pokemon ROWE
  project; binary-port methodology proven on Pokemon Radical Red.
