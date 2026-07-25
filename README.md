# Character Mode for Pokemon Lazarus v2.0

An opt-in game mode where you play as an iconic Pokemon character — a
protagonist, rival, gym leader, Elite Four member, champion, villain, or
anime cast member — and are restricted to catching and keeping only that
character's canon roster (as documented on Bulbapedia, expanded to full
evolution families). 201 characters, Generations 1 through 9.

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

> **Updating from an earlier build of this patch?** Character Mode now records
> "mode is on" in a different save slot, because the old one sat in a block the
> game wipes whenever the in-game day rolls over — which quietly switched the
> mode off at midnight. Your save, party and boxes are untouched, but if you had
> Character Mode active you'll find it reads as off: just re-enter your
> character's code once at the university desk and it stays on for good.

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
| `Agatha` | Agatha | Elite Four | Gastly |
| `Ash` | Ash | anime | Pikachu |
| `Blaine` | Blaine | Gym Leader | Growlithe |
| `Blue` | Blue | champion | Aerodactyl |
| `Brock` | Brock | Gym Leader | Onix |
| `Bruno` | Bruno | Elite Four | Dratini |
| `Erika` | Erika | Gym Leader | Bellsprout |
| `Gary` | Gary | anime | Aerodactyl |
| `Giovanni` | Giovanni | villain | Bellsprout |
| `James` | James | anime | Aron |
| `Jessie` | Jessie | anime | Ekans |
| `Koga` | Koga | Elite Four | Chinchou |
| `Lance` | Lance | champion | Dratini |
| `Leaf` | Leaf | protagonist | Eevee |
| `Lorelei` | Lorelei | Elite Four | Lapras |
| `LtSurge` | Lt. Surge | Gym Leader | Pikachu |
| `Misty` | Misty | Gym Leader | Buizel |
| `Oak` | Oak | Professor | Dratini |
| `Red` | Red | protagonist | Pikachu |
| `Ritchie` | Ritchie | anime | Pikachu |
| `Sabrina` | Sabrina | Gym Leader | Chingling |
| `Tracey` | Tracey | anime | Scyther |

### Generation 2

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Archer` | Archer | villain | Houndour |
| `Ariana` | Ariana | villain | Ekans |
| `Bugsy` | Bugsy | Gym Leader | Scyther |
| `Chuck` | Chuck | Gym Leader | Poliwag |
| `Clair` | Clair | Gym Leader | Aerodactyl |
| `Elm` | Elm | Professor | Bellsprout |
| `Ethan` | Ethan | protagonist | Cyndaquil |
| `Falkner` | Falkner | Gym Leader | Hoothoot |
| `Janine` | Janine | Gym Leader | Spinarak |
| `Jasmine` | Jasmine | Gym Leader | Onix |
| `Karen` | Karen | Elite Four | Eevee |
| `Kris` | Kris | protagonist | Totodile |
| `Lyra` | Lyra | protagonist | Chikorita |
| `Morty` | Morty | Gym Leader | Gastly |
| `Pryce` | Pryce | Gym Leader | Swinub |
| `Silver` | Silver | rival | Totodile |
| `Whitney` | Whitney | Gym Leader | Aipom |
| `Will` | Will | Elite Four | Natu |

### Generation 3

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Anabel` | Anabel | Frontier Brain | Eevee |
| `Archie` | Archie | villain | Dratini |
| `Birch` | Birch | Professor | Aron |
| `Brandon` | Brandon | Frontier Brain | Duskull |
| `Brawly` | Brawly | Gym Leader | Heracross |
| `Brendan` | Brendan | protagonist | Aron |
| `Drake` | Drake | Elite Four | Pichu |
| `Drew` | Drew | anime | Budew |
| `Flannery` | Flannery | Gym Leader | Torkoal |
| `Glacia` | Glacia | Elite Four | Spheal |
| `Greta` | Greta | Frontier Brain | Eevee |
| `Juan` | Juan | Gym Leader | Barboach |
| `Liza` | Liza | Gym Leader | Baltoy |
| `Lucy` | Lucy | Frontier Brain | Magikarp |
| `Maxie` | Maxie | villain | Numel |
| `May` | May | protagonist | Torchic |
| `Noland` | Noland | Frontier Brain | Aron |
| `Norman` | Norman | Gym Leader | Aipom |
| `Phoebe` | Phoebe | Elite Four | Duskull |
| `Roxanne` | Roxanne | Gym Leader | Nosepass |
| `Sidney` | Sidney | Elite Four | Corphish |
| `Spenser` | Spenser | Frontier Brain | Baltoy |
| `Steven` | Steven | champion | Aerodactyl |
| `Tate` | Tate | Gym Leader | Baltoy |
| `Tucker` | Tucker | Frontier Brain | Growlithe |
| `Wallace` | Wallace | champion | Barboach |
| `Wally` | Wally | rival | Ralts |
| `Wattson` | Wattson | Gym Leader | Magnemite |
| `Winona` | Winona | Gym Leader | Swablu |

### Generation 4

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Aaron` | Aaron | Elite Four | Skorupi |
| `Barry` | Barry | rival | Budew |
| `Bertha` | Bertha | Elite Four | Barboach |
| `Byron` | Byron | Gym Leader | Shieldon |
| `Candice` | Candice | Gym Leader | Snorunt |
| `CrasherWak` | Crasher Wake | Gym Leader | Buizel |
| `Cynthia` | Cynthia | champion | Budew |
| `Cyrus` | Cyrus | villain | Sneasel |
| `Dahlia` | Dahlia | Frontier Brain | Duskull |
| `Darach` | Darach | Frontier Brain | Houndour |
| `Dawn` | Dawn | protagonist | Aipom |
| `Fantina` | Fantina | Gym Leader | Bronzor |
| `Flint` | Flint | Elite Four | Buizel |
| `Gardenia` | Gardenia | Gym Leader | Budew |
| `Jupiter` | Jupiter | villain | Stunky |
| `Lucas` | Lucas | protagonist | Cranidos |
| `Lucian` | Lucian | Elite Four | Bronzor |
| `Mars` | Mars | villain | Bronzor |
| `Maylene` | Maylene | Gym Leader | Aipom |
| `Nando` | Nando | anime | Budew |
| `Palmer` | Palmer | Frontier Brain | Dratini |
| `Paul` | Paul | anime | Aron |
| `Roark` | Roark | Gym Leader | Cranidos |
| `Rowan` | Rowan | Professor | Aipom |
| `Saturn` | Saturn | villain | Bronzor |
| `Volkner` | Volkner | Gym Leader | Aipom |
| `Zoey` | Zoey | anime | Aipom |

### Generation 5

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Alder` | Alder | champion | Archen |
| `Bianca` | Bianca | rival | Blitzle |
| `Brycen` | Brycen | Gym Leader | Cubchoo |
| `Burgh` | Burgh | Gym Leader | Dwebble |
| `Caitlin` | Caitlin | Elite Four | Gothita |
| `Cheren` | Cheren | Gym Leader | Lillipup |
| `Chili` | Chili | Gym Leader | Pansear |
| `Cilan` | Cilan | Gym Leader | Pansage |
| `Clay` | Clay | Gym Leader | Baltoy |
| `Colress` | Colress | villain | Cubchoo |
| `Cress` | Cress | Gym Leader | Panpour |
| `Drayden` | Drayden | Gym Leader | Dratini |
| `Elesa` | Elesa | Gym Leader | Blitzle |
| `Ghetsis` | Ghetsis | villain | Munna |
| `Grimsley` | Grimsley | Elite Four | Houndour |
| `Hilda` | Hilda | protagonist | Eevee |
| `Hugh` | Hugh | rival | Grimer |
| `Iris` | Iris | champion | Archen |
| `Juniper` | Juniper | Professor | Archen |
| `Lenora` | Lenora | Gym Leader | Gothita |
| `Marlon` | Marlon | Gym Leader | Shellder |
| `Marshal` | Marshal | Elite Four | Timburr |
| `N` | N | rival | Zorua |
| `Nate` | Nate | protagonist | Growlithe |
| `Rosa` | Rosa | protagonist | Archen |
| `Roxie` | Roxie | Gym Leader | Grimer |
| `Shauntal` | Shauntal | Elite Four | Litwick |
| `Skyla` | Skyla | Gym Leader | Ducklett |
| `Trip` | Trip | anime | Dwebble |

### Generation 6

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Alain` | Alain | anime | Chespin |
| `Calem` | Calem | protagonist | Chespin |
| `Clemont` | Clemont | Gym Leader | Helioptile |
| `Diantha` | Diantha | champion | Ralts |
| `Drasna` | Drasna | Elite Four | Skrelp |
| `Grant` | Grant | Gym Leader | Tyrunt |
| `Korrina` | Korrina | Gym Leader | Chespin |
| `Lysandre` | Lysandre | villain | Magikarp |
| `Malva` | Malva | Elite Four | Fennekin |
| `Ramos` | Ramos | Gym Leader | Skiddo |
| `Sawyer` | Sawyer | anime | Clauncher |
| `Serena` | Serena | protagonist | Fennekin |
| `Shauna` | Shauna | rival | Chespin |
| `Siebold` | Siebold | Elite Four | Clauncher |
| `Sycamore` | Sycamore | Professor | Chespin |
| `Valerie` | Valerie | Gym Leader | Eevee |
| `Viola` | Viola | Gym Leader | Honedge |
| `Wikstrom` | Wikstrom | Elite Four | Honedge |
| `Wulfric` | Wulfric | Gym Leader | Pichu |

### Generation 7

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Acerola` | Acerola | Elite Four | Cubone |
| `Burnet` | Burnet | Professor | Bruxish |
| `Elio` | Elio | protagonist | Popplio |
| `Gladion` | Gladion | rival | Cubone |
| `Guzma` | Guzma | villain | Wimpod |
| `Hala` | Hala | Gym Leader | Crabrawler |
| `Hapu` | Hapu | Gym Leader | Mudbray |
| `Hau` | Hau | champion | Pichu |
| `Kahili` | Kahili | Elite Four | Pikipek |
| `Kiaweanime` | Kiawe (anime) | anime | Corphish |
| `Kukui` | Kukui | champion | Litten |
| `Lanaanime` | Lana (anime) | anime | Popplio |
| `Lillieanim` | Lillie (anime) | anime | Vulpix |
| `Lusamine` | Lusamine | villain | Stufful |
| `Mallowanim` | Mallow (anime) | anime | Bounsweet |
| `Molayne` | Molayne | Elite Four | Grubbin |
| `Nanu` | Nanu | Gym Leader | Meowth |
| `Olivia` | Olivia | Gym Leader | Rockruff |
| `Plumeria` | Plumeria | villain | Salandit |
| `SamsonOak` | Samson Oak | Professor | Bronzor |
| `Selene` | Selene | protagonist | Rowlet |
| `Sophocles` | Sophocles | anime | Togedemaru |

### Generation 8

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Allister` | Allister | Gym Leader | Gastly |
| `Bea` | Bea | Gym Leader | Dracovish |
| `Bede` | Bede | rival | Caterpie |
| `Cerise` | Cerise | Professor | Eevee |
| `Chloe` | Chloe | anime | Eevee |
| `Goh` | Goh | anime | Aerodactyl |
| `Gordie` | Gordie | Gym Leader | Lapras |
| `Kabu` | Kabu | Gym Leader | Sizzlipede |
| `Laventon` | Laventon | Professor | Cyndaquil |
| `Leon` | Leon | champion | Amaura |
| `Magnolia` | Magnolia | Professor | Bronzor |
| `Marnie` | Marnie | rival | Cufant |
| `Melony` | Melony | Gym Leader | Lapras |
| `Milo` | Milo | Gym Leader | Applin |
| `Nessa` | Nessa | Gym Leader | Magikarp |
| `Opal` | Opal | Gym Leader | Dracovish |
| `Piers` | Piers | Gym Leader | Zigzagoon |
| `Raihan` | Raihan | Gym Leader | Dreepy |
| `Rose` | Rose | villain | Cufant |
| `Sonia` | Sonia | Professor | Bounsweet |

### Generation 9

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Arven` | Arven | rival | Eevee |
| `Brassius` | Brassius | Gym Leader | Applin |
| `Geeta` | Geeta | champion | Chespin |
| `Grusha` | Grusha | Gym Leader | Cubchoo |
| `Hassel` | Hassel | Elite Four | Applin |
| `Iono` | Iono | Gym Leader | Charcadet |
| `Katy` | Katy | Gym Leader | Heracross |
| `Kofu` | Kofu | Gym Leader | Crabrawler |
| `Larry` | Larry | Gym Leader | Flamigo |
| `Nemona` | Nemona | champion | Pawmi |
| `Penny` | Penny | rival | Eevee |
| `Poppy` | Poppy | Elite Four | Tinkatink |
| `Rika` | Rika | Elite Four | Wooper |
| `Ryme` | Ryme | Gym Leader | Fuecoco |
| `Tulip` | Tulip | Gym Leader | Florges |

## Credits

- **Pokemon Lazarus** by Nemo622 — this project modifies nothing about
  the hack's own content and requires the official patch.
- Character rosters from **Bulbapedia**.
- Character Mode concept and reference implementation: the Pokemon ROWE
  project; binary-port methodology proven on Pokemon Radical Red.
