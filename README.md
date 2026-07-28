# Character Mode for Pokemon Lazarus v2.0

An opt-in game mode where you play as an iconic Pokemon character — a
protagonist, rival, gym leader, Elite Four member, champion, villain, or
anime cast member — and are restricted to catching and keeping only that
character's canon roster (as documented on Bulbapedia, expanded to full
evolution families). 123 characters, Generations 1 through 9.

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
| `CMDbgGive2` | Test code: gives a Lv. 5 Pokemon that is **off the first character's roster** -> goes to the PC. The species is derived from that character's own allow-bitmap at build time, so do not expect a specific one (it was documented as Ekans long after the build started deriving it). |

## Known limitations

- Characters keep the normal player sprite in the overworld. A character
  portrait is shown when you select one, for the 164 characters art is
  staged for.
- Some characters' canon rosters include Pokemon that are not obtainable
  in Lazarus's curated dex; their rosters were validated against the
  official Encounters guide so every character has obtainable Pokemon,
  but roster species missing from Lazarus simply never appear.
- **Not every Pokemon character is offered here.** Lazarus ships a curated
  dex, and for many characters it simply cannot field six fully-evolved
  Pokemon from their canon roster — playing as one would mean a whole run
  with almost nothing catchable. Those codes are refused, and only the
  characters listed below are selectable. If you have a save from an
  earlier build on a character that is no longer offered, it keeps working
  exactly as it did.

## Character codes

### Generation 1

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Ash` | Ash | Anime | Pikachu |
| `Blaine` | Blaine | Gym Leader | Growlithe |
| `Blue` | Blue | Champion | Aerodactyl |
| `Brock` | Brock | Gym Leader | Onix |
| `Bruno` | Bruno | Elite Four | Grimer |
| `Erika` | Erika | Gym Leader | Bellsprout |
| `Gary` | Gary | Anime | Doduo |
| `Giovanni` | Giovanni | Villain | Cubone |
| `James` | James | Anime | Aron |
| `Jessie` | Jessie | Anime | Ekans |
| `Koga` | Koga | Elite Four | Chinchou |
| `Lance` | Lance | Champion | Dratini |
| `Leaf` | Leaf | Protagonist | Eevee |
| `Lorelei` | Lorelei | Elite Four | Lapras |
| `LtSurge` | Lt. Surge | Gym Leader | Pikachu |
| `Misty` | Misty | Gym Leader | Buizel |
| `Oak` | Oak | Professor | Bellsprout |
| `Red` | Red | Protagonist | Pikachu |
| `Ritchie` | Ritchie | Anime | Pikachu |
| `Sabrina` | Sabrina | Gym Leader | Chingling |

### Generation 2

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Archer` | Archer | Villain | Houndour |
| `Ariana` | Ariana | Villain | Ekans |
| `Bugsy` | Bugsy | Gym Leader | Scyther |
| `Chuck` | Chuck | Gym Leader | Poliwag |
| `Clair` | Clair | Gym Leader | Aerodactyl |
| `Elm` | Elm | Professor | Chikorita |
| `Ethan` | Ethan | Protagonist | Cyndaquil |
| `Falkner` | Falkner | Gym Leader | Hoothoot |
| `Janine` | Janine | Gym Leader | Spinarak |
| `Jasmine` | Jasmine | Gym Leader | Onix |
| `Karen` | Karen | Elite Four | Eevee |
| `Kris` | Kris | Protagonist | Totodile |
| `Lyra` | Lyra | Protagonist | Chikorita |
| `Morty` | Morty | Gym Leader | Gastly |
| `Pryce` | Pryce | Gym Leader | Swinub |
| `Silver` | Silver | Rival | Totodile |
| `Whitney` | Whitney | Gym Leader | Aipom |
| `Will` | Will | Elite Four | Natu |

### Generation 3

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Anabel` | Anabel | Frontier Brain | Eevee |
| `Archie` | Archie | Villain | Grimer |
| `Birch` | Birch | Professor | Aron |
| `Brendan` | Brendan | Protagonist | Aron |
| `Flannery` | Flannery | Gym Leader | Torkoal |
| `Greta` | Greta | Frontier Brain | Eevee |
| `Juan` | Juan | Gym Leader | Barboach |
| `Liza` | Liza | Gym Leader | Baltoy |
| `Maxie` | Maxie | Villain | Numel |
| `May` | May | Protagonist | Torchic |
| `Noland` | Noland | Frontier Brain | Aron |
| `Roxanne` | Roxanne | Gym Leader | Nosepass |
| `Spenser` | Spenser | Frontier Brain | Baltoy |
| `Steven` | Steven | Champion | Aerodactyl |
| `Tate` | Tate | Gym Leader | Baltoy |
| `Wallace` | Wallace | Champion | Barboach |
| `Winona` | Winona | Gym Leader | Swablu |

### Generation 4

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Aaron` | Aaron | Elite Four | Skorupi |
| `Bertha` | Bertha | Elite Four | Barboach |
| `Byron` | Byron | Gym Leader | Shieldon |
| `Candice` | Candice | Gym Leader | Snorunt |
| `CrasherWak` | Crasher Wake | Gym Leader | Buizel |
| `Cynthia` | Cynthia | Champion | Budew |
| `Cyrus` | Cyrus | Villain | Sneasel |
| `Darach` | Darach | Frontier Brain | Houndour |
| `Dawn` | Dawn | Protagonist | Aipom |
| `Fantina` | Fantina | Gym Leader | Corphish |
| `Flint` | Flint | Elite Four | Eevee |
| `Gardenia` | Gardenia | Gym Leader | Budew |
| `Lucas` | Lucas | Protagonist | Cranidos |
| `Lucian` | Lucian | Elite Four | Bronzor |
| `Mars` | Mars | Villain | Bronzor |
| `Maylene` | Maylene | Gym Leader | Dratini |
| `Paul` | Paul | Anime | Aron |
| `Roark` | Roark | Gym Leader | Cranidos |
| `Saturn` | Saturn | Villain | Bronzor |
| `Volkner` | Volkner | Gym Leader | Aipom |
| `Zoey` | Zoey | Anime | Eevee |

### Generation 5

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Bianca` | Bianca | Rival | Lillipup |
| `Caitlin` | Caitlin | Elite Four | Gothita |
| `Cheren` | Cheren | Gym Leader | Lillipup |
| `Clay` | Clay | Gym Leader | Baltoy |
| `Cress` | Cress | Gym Leader | Panpour |
| `Grimsley` | Grimsley | Elite Four | Houndour |
| `Hilbert` | Hilbert | Protagonist | Archen |
| `Hilda` | Hilda | Protagonist | Archen |
| `Ingo` | Ingo | Frontier Brain | Dwebble |
| `N` | N | Rival | Zorua |
| `Nate` | Nate | Protagonist | Archen |
| `Rosa` | Rosa | Protagonist | Archen |
| `Skyla` | Skyla | Gym Leader | Ducklett |

### Generation 6

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Calem` | Calem | Protagonist | Chespin |
| `Clemont` | Clemont | Gym Leader | Helioptile |
| `Diantha` | Diantha | Champion | Ralts |
| `Korrina` | Korrina | Gym Leader | Chespin |
| `Serena` | Serena | Protagonist | Fennekin |
| `Shauna` | Shauna | Rival | Chespin |
| `Sycamore` | Sycamore | Professor | Caterpie |
| `Valerie` | Valerie | Gym Leader | Eevee |
| `Wikstrom` | Wikstrom | Elite Four | Honedge |

### Generation 7

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Acerola` | Acerola | Elite Four | Dhelmise |
| `Elio` | Elio | Protagonist | Popplio |
| `Gladion` | Gladion | Rival | Eevee |
| `Guzma` | Guzma | Villain | Wimpod |
| `Hala` | Hala | Gym Leader | Crabrawler |
| `Hau` | Hau | Champion | Pichu |
| `Kahili` | Kahili | Elite Four | Pikipek |
| `Kukui` | Kukui | Champion | Litten |
| `Lanaanime` | Lana (anime) | Anime | Popplio |
| `Lusamine` | Lusamine | Villain | Stufful |
| `Olivia` | Olivia | Gym Leader | Rockruff |
| `SamsonOak` | Samson Oak | Professor | Cubone |
| `Selene` | Selene | Protagonist | Rowlet |

### Generation 8

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Adaman` | Adaman | Rival | Eevee |
| `Allister` | Allister | Gym Leader | Gastly |
| `Bede` | Bede | Rival | Eevee |
| `Chloe` | Chloe | Anime | Eevee |
| `Goh` | Goh | Anime | Aerodactyl |
| `Irida` | Irida | Rival | Eevee |
| `Kabu` | Kabu | Gym Leader | Sizzlipede |

### Generation 9

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Larry` | Larry | Gym Leader | Flamigo |
| `Nemona` | Nemona | Champion | Pawmi |
| `Penny` | Penny | Rival | Eevee |
| `Poppy` | Poppy | Elite Four | Tinkatink |
| `Tulip` | Tulip | Gym Leader | Florges |

## Credits

- **Pokemon Lazarus** by Nemo622 — this project modifies nothing about
  the hack's own content and requires the official patch.
- Character rosters from **Bulbapedia**.
- Character Mode concept and reference implementation: the Pokemon ROWE
  project; binary-port methodology proven on Pokemon Radical Red.
