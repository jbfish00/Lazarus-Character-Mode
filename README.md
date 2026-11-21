# Character Mode for Pokemon Lazarus v2.0

An opt-in game mode where you play as an iconic Pokemon character — a
protagonist, rival, gym leader, Elite Four member, champion, villain, or
anime cast member — and are restricted to catching and keeping only that
character's canon roster (as documented on Bulbapedia, expanded to full
evolution families). 116 characters, Generations 1 through 9.

Ported from the original Character Mode built for Pokemon ROWE, following
the Radical Red port.

## ▶️ How to turn Character Mode on

> **Character Mode is opt-in. Nothing in the game changes until you do this.**

1. Go to the **desk in Acrisia University** — the professor's building where
   you start.
2. Interact with it. It asks for a cheat code.
3. **Type your character's code** and confirm.

**Your code** is the character's name with spaces and punctuation removed —
`Cynthia`, `LtSurge`, `Red`. Case does not matter.
📋 **Full list: [Character codes](#character-codes)** (116 selectable).

**You will know it worked:** a confirmation message naming your character —
with their portrait beside it — and their signature starter at Lv. 5.

**To turn it back off:** enter the code **`CMDbgOff`** at the same desk.

---

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

## What happens after you activate

From then on, catching or receiving any Pokemon **not on your character's
roster is refused or sent to the PC**: a wild off-roster Pokémon can't be caught at all, and off-roster gifts, eggs and trades go to the PC. Everything
on-roster (including every evolution of a roster Pokemon) joins your party
normally.

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

## Quality-of-life rules (added 2026-10)

While Character Mode is on:
- **Every on-roster Pokémon is caught at 100%**, with any ball. **Off-roster wild Pokémon cannot be caught at all**
  (the ball is dodged or bounces off with no shakes). Gifts, eggs and trades keep their PC routing.
- **TMs are reusable.** Native to Lazarus.
- **Exp. Share, party-wide.** Native to Lazarus: every player gets it (Character Mode on or off) in the Rotom Phone
  scene after the delivery errand, before gym 1 (live-tested 2026-10-21).
- **Move relearner, any level** (Character Mode on or off, 2026-10-24): the relearner offers every level-up move of the
  Pokémon, not only the ones up to its level, then its egg moves (24 at most).
- **HMs** are already badge-only in Lazarus, so any party Pokémon can use them.
- **Battle animations off on new games** (Character Mode on or off, 2026-10-28): Options turns them back on; an
  existing save keeps its own setting.
- **Instant HP bar** (every save, 2026-10-28; fixed 2026-11-14): the HP bar jumps straight to its new value in battle; a Pokémon with under 48 max HP no longer starts a battle with a nearly empty red bar.
- **Heal + PC anywhere** (every save, Character Mode on or off, 2026-11-11): START > **Extras** (the last row) has
  *Heal party* (a free full heal, any time outside battle) and *PC* (the Pokémon storage system) once you have a
  Pokémon, next to *Exp. Rate*.
- **EXP rate** (every save, Character Mode on or off, 2026-10-30): START > **Extras** > *Exp. Rate* sets battle
  EXP to x0.5, x1, x1.5, x2 or x3; the current rate is preselected and B keeps it. It multiplies what the game already
  pays (after the Lucky Egg and Exp. Share), and an existing save starts at x1.
- **Your overworld sprite becomes the character** (walking and running) for all 116 selectable characters: 110 use
  a character sheet, and Ethan, Lyra, Calem, Serena, Elio and Selene wear Lazarus's own Johto/Kalos/Alolan Fashion
  outfits. Tested live 2026-10-22.

## Seeing your roster in-game

With Character Mode on, use the **Cheat Code System desk** again (the same
desk in Acrisia University, or any other terminal that runs it). Instead of
"Would you like to enter a code?" you get a short menu:

- **View roster**: a list of your character's Pokémon, one row per
  evolution family (the first stage is shown, and the whole family counts).
  The highlighted Pokémon's icon appears in a box beside the list. Scroll with
  Up/Down; A or B closes it.
- **Enter a code**: straight to the code screen (for your character, `CMDbgOff`,
  or the game's own cheat codes).

With Character Mode off, the desk works exactly as it always did.

## Known limitations

- Sycamore keeps Caterpie as his starter: Gible's family is not in Lazarus.
- A character
  portrait is shown when you select one, for the 179 characters art is
  staged for (98 of the 116 selectable).
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
| `Erika` | Erika | Gym Leader | Bellsprout |
| `Gary` | Gary | Anime | Doduo |
| `Giovanni` | Giovanni | Villain | Cubone |
| `James` | James | Anime | Aron |
| `Jessie` | Jessie | Anime | Ekans |
| `Koga` | Koga | Elite Four | Ekans |
| `Lance` | Lance | Champion | Dratini |
| `Leaf` | Leaf | Protagonist | Eevee |
| `LtSurge` | Lt. Surge | Gym Leader | Pikachu |
| `Misty` | Misty | Gym Leader | Buizel |
| `Oak` | Oak | Professor | Bellsprout |
| `Red` | Red | Protagonist | Pikachu |
| `Ritchie` | Ritchie | Anime | Pikachu |
| `Sabrina` | Sabrina | Gym Leader | Chingling |

### Generation 2

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Bugsy` | Bugsy | Gym Leader | Scyther |
| `Chuck` | Chuck | Gym Leader | Poliwag |
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

## Starter kit (2026-11-07)
Every new game (Character Mode on or off) starts with the Running Shoes, the Mach Bike (Rydel then offers the swap), the Shiny Charm and the Oval Charm. Build 2026-11-07: `build/lazarus_cm.gba` sha1 `ce03be5810735b5862ff4ff7504fa8c04429857e`, `build/lazarus_cm.bps` sha1 `831848d17ad866de76ffe60b8262f165779636d0` (round trip checked). The kit comes with a new game only; an existing save keeps what it has. On My Boy!, keep the old ROM and save, and load the new ROM under the same file name so the `.sav` carries over.

## Wild-intro roster hint (2026-11-08)
With Character Mode on, a wild Pokémon off your character's roster says so in its intro ("Wild X appeared! / It is not on your roster."), so you know before you throw a ball that it can't be caught. On-roster Pokémon still say "destined for <NAME>!". Build 2026-11-08: `build/lazarus_cm.gba` sha1 `343f3f3a66d084155adb92525c708e73fd63e28e`, `build/lazarus_cm.bps` sha1 `072692a6aefc761ff7af9437ccbed5a151052522` (round trip checked). Save-compatible: on My Boy!, keep the old ROM and save, and load the new ROM under the same file name so the `.sav` carries over.

### Fix: instant HP bar drew low-max-HP bars red (2026-11-14)
The 2026-10-28 instant HP bar drew any Pokémon with under 48 max HP (most early-game Pokémon) as a nearly empty red bar at the start of a battle, and after every hit. The bar is now drawn at its real value and is still instant. Build 2026-11-14: `build/lazarus_cm.gba` sha1 `9bde6d8e8766607a40de214fd85c2215c7b6dbee`, `build/lazarus_cm.bps` sha1 `2ddc39c04ca2d438f3696355abe9c224ef2d9ab2` (round trip checked; differs from the old patch in 5 bytes). Save-compatible: on My Boy!, keep the old ROM and save, and load the new ROM under the same file name so the `.sav` carries over.

### Fix: a gift into an emptied party is never boxed (2026-11-20)
The roster check on gifts trusted the party count. A cutscene that empties the party for a loaner battle without updating that count (the shape that froze Gaia's Regigigas battle) would have sent an off-roster loaner to the PC and started the battle with no Pokémon. The check now looks at the party slots themselves. Build 2026-11-20: `build/lazarus_cm.gba` sha1 `66475e59f347bd037912b7c047ecd2174f7ac38c`, `build/lazarus_cm.bps` sha1 `65d920a1da36e18a0a0bf74a112253f766029f1a` (round trip checked). `shim_unit_test.py` 39/39 (new case: count 1, every slot blank -> give; the `CM_OLD_GIFTGATE=1` build fails exactly that case), live suite ALL PASS, every checker and negative test pass. Save-compatible: on My Boy!, keep the old ROM and save, and load the new ROM under the same file name so the `.sav` carries over.

### Roster change: the Pokémon Stadium games no longer count (2026-11-21)
A Pokémon that a character used only in *Pokémon Stadium* or *Pokémon Stadium 2* is no longer on that character's
roster. Anything they also have in a main-series game, the anime or the manga stays, and a whole evolution family stays
if any member does. 28 characters lose 171 families in all (Kanto and Johto gym leaders, the Elite Four, the rivals and
Team Rocket's executives). In this game that leaves Archer, Ariana, Bruno, Clair, Lorelei, Whitney, Will with fewer than six fully-evolved Pokémon, so they are now hidden from the picker (the slot stays, so a save that already uses one keeps working). The roster docs now show Eevee's evolutions as one "Eevee (any evolution)" entry; all of
them are still allowed in the game. Build 2026-11-21: `build/lazarus_cm.gba` sha1 `b80504101f0772964d54250fd84a0c904b64b0a1`, `build/lazarus_cm.bps` sha1 `9876c03a932dd697d434d5e39a105dc2bfbe85e2` (round trip checked; live suite, every checker, negative test and guard pass).
