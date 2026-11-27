# Lazarus: move, ability and stat changes

> **Generated 2026-11-26** from the repo manifests by `make_change_docs.py`. Sections 1-3 are in the shipped release; section 4 (Planned) is **not in any release**.
>
> Status: round 2 pushed (4dd4fad, build 78a65c75).

The change sets here apply with Character Mode on or off (they change the game's move data). Source manifest: `Lazarus-Character-Mode/tools/character_mode/move_changes.json`.

## 1. Move values

Every move the hack changed is raised to the best value any generation gave it (accuracy, PP, power, effect chance, priority, type). **452 moves changed**: 88 power, 391 pp, 17 accuracy, 33 effect %, 8 priority, 8 type edits. Cells read old → new.

| Move | Power | PP | Accuracy | Effect % | Priority | Type |
|---|---|---|---|---|---|---|
| Comet Punch | 18 → 30 |  |  |  |  |  |
| Fire Punch |  | 15 → 16 |  | 10 → 30 |  |  |
| Ice Punch |  | 15 → 16 |  | 10 → 30 |  |  |
| Thunder Punch |  | 15 → 16 |  | 10 → 30 |  |  |
| Guillotine |  | 5 → 8 |  |  |  |  |
| Swords Dance |  | 20 → 30 |  |  |  |  |
| Whirlwind |  |  |  |  | -6 → 0 |  |
| Fly |  | 15 → 16 |  |  |  |  |
| Slam | 70 → 80 | 10 → 20 |  |  | -6 → 0 |  |
| Mega Kick | 110 → 120 | 5 → 8 |  |  |  |  |
| Jump Kick | 95 → 100 | 10 → 25 |  |  |  |  |
| Horn Drill |  | 5 → 8 |  |  |  |  |
| Tackle | 40 → 50 |  |  |  |  |  |
| Body Slam |  | 15 → 16 |  |  |  |  |
| Thrash |  | 10 → 20 |  |  |  |  |
| Double-Edge |  | 15 → 16 |  |  |  |  |
| Poison Sting | 15 → 30 |  |  | 30 → 50 |  |  |
| Roar |  |  |  |  | -6 → 0 |  |
| Sing |  | 15 → 16 |  |  |  |  |
| Acid |  |  |  | 10 → 33 |  |  |
| Ember |  |  |  | 10 → 30 |  |  |
| Flamethrower | 90 → 95 | 15 → 16 |  | 10 → 20 |  |  |
| Hydro Pump | 110 → 120 | 5 → 8 | 80 → 85 |  |  |  |
| Surf | 90 → 95 | 15 → 16 |  |  |  |  |
| Ice Beam | 90 → 95 | 10 → 12 |  | 10 → 20 |  |  |
| Blizzard | 110 → 120 | 5 → 8 | 70 → 90 | 10 → 30 |  |  |
| Bubble Beam |  |  |  | 10 → 33 |  |  |
| Aurora Beam |  |  |  | 10 → 33 |  |  |
| Hyper Beam |  | 5 → 8 |  |  |  |  |
| Submission |  | 20 → 25 |  |  |  |  |
| Counter |  |  |  |  | -5 → -1 |  |
| Strength |  |  |  |  |  | Rock → Normal |
| Absorb | 30 → 40 |  |  |  |  |  |
| Mega Drain | 50 → 75 |  |  |  |  |  |
| Leech Seed |  | 10 → 12 |  |  |  |  |
| Growth |  | 20 → 40 |  |  |  | Normal → Grass |
| Solar Beam | 120 → 200 | 10 → 12 |  |  |  |  |
| Poison Powder |  |  | 75 → 80 |  |  |  |
| Stun Spore |  |  | 75 → 80 |  |  |  |
| Sleep Powder |  | 15 → 20 | 75 → 80 |  |  |  |
| Petal Dance |  | 10 → 20 |  |  |  |  |
| Fire Spin |  | 15 → 16 |  |  |  |  |
| Thunder Shock |  |  |  | 10 → 30 |  |  |
| Thunderbolt | 90 → 95 | 15 → 16 |  | 10 → 20 |  |  |
| Thunder Wave |  |  | 90 → 100 |  |  |  |
| Thunder | 110 → 120 | 10 → 12 | 70 → 75 |  |  |  |
| Earthquake |  | 10 → 12 |  |  |  |  |
| Fissure |  | 5 → 8 |  |  |  |  |
| Dig | 80 → 100 | 10 → 12 |  |  |  |  |
| Toxic |  | 10 → 12 |  |  |  |  |
| Psychic |  | 10 → 12 |  | 10 → 33 |  |  |
| Hypnosis |  |  | 60 → 70 |  |  |  |
| Teleport |  |  |  |  | -6 → 0 |  |
| Night Shade |  | 15 → 16 |  |  |  |  |
| Double Team |  | 15 → 16 |  |  |  |  |
| Recover |  | 5 → 20 |  |  |  |  |
| Minimize |  | 10 → 20 |  |  |  |  |
| Confuse Ray |  | 10 → 12 |  |  |  |  |
| Barrier |  | 20 → 30 |  |  |  |  |
| Self-Destruct |  | 5 → 8 |  |  |  |  |
| Sludge |  |  |  | 30 → 40 |  |  |
| Fire Blast | 110 → 120 | 5 → 8 |  | 10 → 30 |  |  |
| Waterfall |  | 15 → 16 |  |  |  |  |
| Skull Bash | 130 → 150 | 10 → 15 |  |  |  |  |
| Spike Cannon |  |  |  |  |  | Steel → Normal |
| Constrict |  |  |  | 10 → 33 |  |  |
| Soft-Boiled |  | 5 → 10 |  |  |  |  |
| High Jump Kick |  | 10 → 20 |  |  |  |  |
| Barrage |  |  |  |  |  | Grass → Normal |
| Leech Life |  | 10 → 15 |  |  |  |  |
| Sky Attack | 140 → 200 | 5 → 8 |  |  |  |  |
| Transform |  | 10 → 12 |  |  |  |  |
| Bubble | 30 → 40 |  |  |  |  |  |
| Dizzy Punch | 60 → 70 |  |  |  |  |  |
| Acid Armor |  | 20 → 40 |  |  |  |  |
| Crabhammer | 90 → 100 | 10 → 12 |  |  |  |  |
| Explosion |  | 5 → 8 |  |  |  |  |
| Bonemerang | 50 → 55 |  |  |  |  |  |
| Rest |  | 5 → 10 |  |  |  |  |
| Rock Slide |  | 10 → 12 |  |  |  |  |
| Tri Attack |  | 10 → 12 |  | 20 → 30 |  |  |
| Super Fang |  | 10 → 12 |  |  |  |  |
| Slash | 70 → 80 |  |  |  |  |  |
| Substitute |  | 10 → 12 |  |  |  |  |
| Struggle |  | 1 → 10 |  |  |  |  |
| Nightmare |  |  | 100 → 101 |  |  |  |
| Flame Wheel |  |  |  | 10 → 30 |  |  |
| Snore |  | 15 → 16 |  |  |  |  |
| Curse |  | 10 → 12 |  |  |  |  |
| Flail |  | 15 → 16 |  |  |  |  |
| Reversal |  | 15 → 16 |  |  |  |  |
| Spite |  | 10 → 12 |  |  |  |  |
| Powder Snow |  |  |  | 10 → 30 |  |  |
| Scary Face |  | 10 → 12 |  |  |  |  |
| Sweet Kiss |  | 10 → 12 |  |  |  |  |
| Belly Drum |  | 10 → 12 |  |  |  |  |
| Sludge Bomb |  | 10 → 12 |  |  |  |  |
| Mud-Slap | 20 → 30 | 10 → 20 |  |  |  |  |
| Octazooka | 60 → 65 | 10 → 15 |  |  |  |  |
| Zap Cannon |  | 5 → 8 |  |  |  |  |
| Destiny Bond |  | 5 → 8 |  |  |  |  |
| Perish Song |  | 5 → 8 |  |  |  |  |
| Icy Wind | 55 → 60 | 15 → 20 |  |  |  |  |
| Detect |  | 5 → 8 |  |  |  |  |
| Bone Rush | 25 → 30 | 10 → 12 |  |  |  |  |
| Lock-On |  | 5 → 8 |  |  |  |  |
| Outrage |  | 10 → 15 |  |  |  |  |
| Giga Drain |  | 10 → 12 |  |  |  |  |
| Endure |  | 10 → 12 |  |  |  |  |
| Rollout | 30 → 60 |  |  |  |  |  |
| Swagger |  | 15 → 16 | 85 → 90 |  |  |  |
| Milk Drink |  | 5 → 10 |  |  |  |  |
| Mean Look |  | 5 → 8 |  |  |  |  |
| Attract |  | 15 → 16 |  |  |  |  |
| Sleep Talk |  | 10 → 12 |  |  |  |  |
| Heal Bell |  | 5 → 8 |  |  |  |  |
| Dynamic Punch |  | 5 → 8 |  |  |  |  |
| Megahorn |  | 10 → 12 |  |  |  |  |
| Encore |  | 5 → 8 |  |  |  |  |
| Iron Tail |  | 15 → 16 |  |  |  |  |
| Morning Sun |  | 5 → 8 |  |  |  |  |
| Synthesis |  | 5 → 8 |  |  |  |  |
| Moonlight |  | 5 → 8 |  |  |  |  |
| Cross Chop |  | 5 → 8 |  |  |  |  |
| Twister |  | 20 → 25 |  |  |  |  |
| Rain Dance |  | 5 → 8 |  |  |  |  |
| Sunny Day |  | 5 → 8 |  |  |  |  |
| Crunch |  | 15 → 16 |  |  |  |  |
| Mirror Coat |  |  |  |  | -5 → -1 |  |
| Psych Up |  | 10 → 12 |  |  |  |  |
| Extreme Speed |  | 5 → 8 |  |  |  |  |
| Ancient Power |  | 10 → 15 |  |  |  |  |
| Shadow Ball |  | 15 → 16 |  |  |  |  |
| Future Sight |  | 10 → 15 |  |  |  |  |
| Rock Smash |  | 15 → 20 |  |  |  |  |
| Whirlpool |  | 15 → 16 |  |  |  |  |
| Beat Up |  | 10 → 12 |  |  |  |  |
| Fake Out |  | 10 → 12 |  |  |  |  |
| Uproar |  | 10 → 12 |  |  |  |  |
| Spit Up |  | 10 → 12 |  |  |  |  |
| Swallow |  | 10 → 12 |  |  |  |  |
| Heat Wave | 95 → 100 | 10 → 12 |  |  |  |  |
| Torment |  | 15 → 16 |  |  |  |  |
| Flatter |  | 15 → 16 |  |  |  |  |
| Will-O-Wisp |  | 10 → 16 |  |  |  |  |
| Memento |  | 10 → 12 | 100 → 101 |  |  |  |
| Facade | 70 → 75 |  |  |  |  |  |
| Follow Me |  |  |  |  | 2 → 3 |  |
| Trick |  | 10 → 12 |  |  |  |  |
| Role Play |  | 10 → 12 |  |  |  |  |
| Superpower |  | 5 → 8 |  |  |  |  |
| Recycle |  | 10 → 12 |  |  |  |  |
| Brick Break |  | 15 → 16 |  |  |  |  |
| Yawn |  | 10 → 12 |  |  |  |  |
| Endeavor |  | 5 → 8 |  |  |  |  |
| Eruption |  | 5 → 8 |  |  |  |  |
| Skill Swap |  | 10 → 12 |  |  |  |  |
| Imprison |  | 10 → 12 |  |  |  |  |
| Dive |  | 10 → 12 |  |  |  |  |
| Feather Dance |  | 15 → 16 |  |  |  |  |
| Blaze Kick |  | 10 → 12 |  |  |  |  |
| Ice Ball | 30 → 40 |  |  |  |  |  |
| Slack Off |  | 5 → 10 |  |  |  |  |
| Hyper Voice |  | 10 → 12 |  |  |  |  |
| Poison Fang |  | 15 → 16 |  |  |  |  |
| Crush Claw |  | 10 → 12 |  |  |  |  |
| Blast Burn |  | 5 → 8 |  |  |  |  |
| Hydro Cannon |  | 5 → 8 |  |  |  |  |
| Meteor Mash | 90 → 100 | 10 → 12 |  |  |  |  |
| Astonish |  | 15 → 25 |  |  |  |  |
| Weather Ball |  | 10 → 12 |  |  |  |  |
| Overheat | 130 → 140 | 5 → 8 |  |  |  |  |
| Rock Tomb |  | 15 → 16 |  |  |  |  |
| Silver Wind |  | 10 → 15 |  |  |  |  |
| Grass Whistle |  | 10 → 15 |  |  |  |  |
| Water Spout |  | 5 → 8 |  |  |  |  |
| Extrasensory |  | 20 → 30 |  |  |  |  |
| Sand Tomb |  | 15 → 16 |  |  |  |  |
| Sheer Cold |  | 5 → 8 |  |  |  |  |
| Muddy Water | 85 → 95 | 10 → 12 |  |  |  |  |
| Iron Defense |  | 15 → 20 |  |  |  |  |
| Block |  | 5 → 8 |  |  |  |  |
| Dragon Claw |  | 15 → 16 |  |  |  |  |
| Frenzy Plant |  | 5 → 8 |  |  |  |  |
| Bounce |  | 5 → 8 |  |  |  |  |
| Mud Shot |  | 15 → 16 |  |  |  |  |
| Covet |  | 25 → 40 |  |  |  | Fairy → Normal |
| Volt Tackle |  | 15 → 16 |  | 10 → 30 |  |  |
| Leaf Blade |  | 15 → 16 |  |  |  |  |
| Rock Blast |  | 10 → 12 |  |  |  |  |
| Water Pulse |  |  | 100 → 101 |  |  |  |
| Roost |  | 5 → 10 |  |  |  |  |
| Gravity |  | 5 → 8 |  |  |  |  |
| Hammer Arm |  | 10 → 12 |  |  |  |  |
| Gyro Ball |  | 5 → 8 |  |  |  |  |
| Healing Wish |  | 10 → 12 |  |  |  |  |
| Feint | 30 → 50 | 10 → 12 |  |  |  |  |
| Tailwind |  | 15 → 30 |  |  |  |  |
| Metal Burst |  | 10 → 12 |  |  |  |  |
| Close Combat |  | 5 → 8 |  |  |  |  |
| Payback |  | 10 → 12 |  |  |  |  |
| Assurance |  | 10 → 12 |  |  |  |  |
| Fling |  | 10 → 12 |  |  |  |  |
| Power Trick |  | 10 → 12 |  |  |  |  |
| Gastro Acid |  | 10 → 12 |  |  |  |  |
| Power Swap |  | 10 → 12 |  |  |  |  |
| Guard Swap |  | 10 → 12 |  |  |  |  |
| Last Resort |  | 5 → 8 |  |  |  |  |
| Worry Seed |  | 10 → 12 |  |  |  |  |
| Sucker Punch | 70 → 80 | 5 → 8 |  |  |  |  |
| Magnet Rise |  | 10 → 12 |  |  |  |  |
| Flare Blitz |  | 15 → 16 |  | 10 → 20 |  |  |
| Aura Sphere | 80 → 90 |  |  |  |  |  |
| Dark Pulse |  | 15 → 16 | 100 → 101 |  |  |  |
| Night Slash |  | 15 → 20 |  |  |  |  |
| Aqua Tail | 85 → 90 | 10 → 12 |  |  |  |  |
| Seed Bomb |  | 15 → 16 |  |  |  |  |
| Air Slash |  | 15 → 20 |  |  |  |  |
| X-Scissor |  | 15 → 16 |  |  |  |  |
| Bug Buzz |  | 10 → 12 |  | 10 → 20 |  |  |
| Dragon Pulse | 85 → 90 | 10 → 12 | 100 → 101 |  |  |  |
| Dragon Rush | 90 → 100 | 10 → 12 |  |  |  |  |
| Drain Punch |  | 10 → 12 |  |  |  |  |
| Focus Blast |  | 5 → 8 |  |  |  |  |
| Energy Ball |  | 10 → 12 |  | 10 → 20 |  |  |
| Brave Bird |  | 15 → 16 |  |  |  |  |
| Earth Power |  | 10 → 12 |  | 10 → 20 |  |  |
| Switcheroo |  | 10 → 12 |  |  |  |  |
| Giga Impact |  | 5 → 8 |  |  |  |  |
| Avalanche |  | 10 → 12 |  |  |  |  |
| Shadow Claw |  | 15 → 16 |  |  |  |  |
| Thunder Fang |  | 15 → 16 |  | 10 → 20 |  |  |
| Ice Fang |  | 15 → 16 |  | 10 → 20 |  |  |
| Fire Fang |  | 15 → 16 |  | 10 → 20 |  |  |
| Mud Bomb |  | 10 → 15 |  |  |  |  |
| Zen Headbutt |  | 15 → 16 |  |  |  |  |
| Flash Cannon |  | 10 → 12 |  | 10 → 20 |  |  |
| Defog |  | 15 → 16 |  |  |  |  |
| Trick Room |  | 5 → 8 |  |  |  |  |
| Draco Meteor | 130 → 140 | 5 → 8 |  |  |  |  |
| Discharge |  | 15 → 16 |  |  |  |  |
| Lava Plume |  | 15 → 16 |  |  |  |  |
| Leaf Storm | 130 → 140 | 5 → 8 |  |  |  |  |
| Power Whip |  | 10 → 12 |  |  |  |  |
| Rock Wrecker |  | 5 → 8 |  |  |  |  |
| Cross Poison |  |  |  | 10 → 20 |  |  |
| Gunk Shot |  | 5 → 8 |  |  |  |  |
| Iron Head |  | 15 → 16 |  |  |  |  |
| Magnet Bomb | 60 → 95 |  |  |  |  |  |
| Stone Edge |  | 5 → 8 |  |  |  |  |
| Charge Beam |  | 10 → 15 |  |  |  |  |
| Wood Hammer |  | 15 → 16 |  |  |  |  |
| Double Hit | 40 → 50 | 10 → 12 |  |  |  |  |
| Magma Storm | 100 → 120 |  |  |  |  |  |
| Dark Void |  |  | 50 → 90 |  |  |  |
| Ominous Wind |  | 5 → 15 |  |  |  |  |
| Wide Guard |  | 10 → 12 |  |  |  |  |
| Guard Split |  | 10 → 12 |  |  |  |  |
| Power Split |  | 10 → 12 |  |  |  |  |
| Wonder Room |  | 10 → 12 |  |  |  |  |
| Psyshock |  | 10 → 12 |  |  |  |  |
| Venoshock |  | 10 → 15 |  |  |  |  |
| Rage Powder |  |  |  |  | 2 → 3 |  |
| Magic Room |  | 10 → 12 |  |  |  |  |
| Smack Down |  | 15 → 16 |  |  |  |  |
| Storm Throw | 60 → 65 | 10 → 12 |  |  |  |  |
| Sludge Wave |  | 10 → 12 |  |  |  |  |
| Heavy Slam |  | 10 → 12 |  |  |  |  |
| Synchronoise |  | 10 → 15 |  |  |  |  |
| Electro Ball |  | 10 → 12 |  |  |  |  |
| Foul Play |  | 15 → 16 |  |  |  |  |
| Simple Beam |  | 15 → 16 |  |  |  |  |
| Entrainment |  | 15 → 16 |  |  |  |  |
| After You |  | 15 → 16 |  |  |  |  |
| Round |  | 15 → 16 |  |  |  |  |
| Clear Smog |  | 15 → 16 |  |  |  |  |
| Stored Power |  | 10 → 12 |  |  |  |  |
| Quick Guard |  | 15 → 16 |  |  |  |  |
| Ally Switch |  | 15 → 16 |  |  |  |  |
| Scald |  | 15 → 16 |  |  |  |  |
| Shell Smash |  | 15 → 16 |  |  |  |  |
| Heal Pulse |  | 10 → 12 |  |  |  |  |
| Hex |  | 10 → 15 |  |  |  |  |
| Shift Gear |  | 10 → 12 |  |  |  |  |
| Circle Throw |  | 10 → 12 |  |  |  |  |
| Quash |  | 15 → 16 |  |  |  |  |
| Acrobatics |  | 15 → 16 |  |  |  |  |
| Reflect Type |  | 15 → 16 |  |  |  |  |
| Final Gambit |  | 5 → 8 |  |  |  |  |
| Inferno |  | 5 → 8 |  |  |  |  |
| Frost Breath | 50 → 65 | 10 → 12 |  |  |  |  |
| Dragon Tail | 55 → 60 | 10 → 12 |  |  |  |  |
| Electroweb |  | 15 → 16 |  |  |  |  |
| Wild Charge |  | 15 → 16 |  |  |  |  |
| Drill Run |  | 10 → 12 |  |  |  |  |
| Dual Chop | 40 → 45 |  |  |  |  |  |
| Horn Leech |  | 10 → 12 |  |  |  |  |
| Sacred Sword |  | 15 → 20 |  |  |  |  |
| Razor Shell |  | 10 → 12 |  |  |  |  |
| Heat Crash |  | 10 → 12 |  |  |  |  |
| Cotton Guard |  | 10 → 12 |  |  |  |  |
| Night Daze | 85 → 90 | 10 → 12 |  |  |  |  |
| Tail Slap |  | 10 → 12 |  |  |  |  |
| Hurricane | 110 → 120 | 10 → 12 | 70 → 75 |  |  |  |
| Gear Grind | 50 → 60 |  | 85 → 90 |  |  |  |
| Fiery Dance |  | 10 → 12 |  |  |  |  |
| Snarl | 55 → 60 | 15 → 16 |  |  |  |  |
| Icicle Crash |  | 10 → 12 |  |  |  |  |
| Flying Press | 80 → 100 | 10 → 12 |  |  |  |  |
| Belch |  | 10 → 12 |  |  |  |  |
| Phantom Force |  | 10 → 12 |  |  |  |  |
| Petal Blizzard |  | 15 → 16 |  |  |  |  |
| Draining Kiss |  | 10 → 15 |  |  |  |  |
| Grassy Terrain |  | 10 → 12 |  |  |  |  |
| Misty Terrain |  | 10 → 12 |  |  |  |  |
| Play Rough |  | 10 → 12 |  | 10 → 20 |  |  |
| Moonblast |  | 15 → 16 |  |  |  |  |
| Boomburst |  | 10 → 12 |  |  |  |  |
| Fairy Lock |  | 10 → 12 |  |  |  |  |
| Mystical Fire |  | 10 → 12 |  |  |  |  |
| Eerie Impulse |  | 15 → 16 |  |  |  |  |
| Electric Terrain |  | 10 → 12 |  |  |  |  |
| Dazzling Gleam |  | 10 → 12 |  |  |  |  |
| Light of Ruin |  | 5 → 8 |  |  |  |  |
| Shore Up |  | 5 → 10 |  |  |  |  |
| First Impression | 90 → 100 | 10 → 12 |  |  |  |  |
| Spirit Shackle |  | 10 → 12 |  |  |  |  |
| Darkest Lariat |  | 10 → 12 |  |  |  |  |
| Sparkling Aria |  | 10 → 12 |  |  |  |  |
| Ice Hammer |  | 10 → 12 |  |  |  |  |
| High Horsepower | 90 → 95 | 10 → 12 |  |  |  |  |
| Solar Blade |  | 10 → 12 |  |  |  |  |
| Throat Chop |  | 15 → 16 |  |  |  |  |
| Pollen Puff |  | 15 → 16 |  |  |  |  |
| Anchor Shot | 80 → 90 |  |  |  |  |  |
| Psychic Terrain |  | 10 → 12 |  |  |  |  |
| Lunge |  | 15 → 16 |  |  |  |  |
| Fire Lash | 80 → 90 | 15 → 16 |  |  |  |  |
| Power Trip |  | 10 → 12 |  |  |  |  |
| Burn Up |  | 5 → 8 |  |  |  |  |
| Speed Swap |  | 10 → 12 |  |  |  |  |
| Smart Strike |  | 10 → 12 |  |  |  |  |
| Revelation Dance | 90 → 100 |  |  |  |  |  |
| Trop Kick | 70 → 85 | 15 → 16 |  |  |  |  |
| Instruct |  | 15 → 16 |  |  |  |  |
| Beak Blast | 100 → 120 |  |  |  |  | Fire → Flying |
| Clanging Scales |  | 5 → 8 |  |  |  |  |
| Dragon Hammer | 90 → 100 |  |  |  |  |  |
| Stomping Tantrum |  | 10 → 12 |  |  |  |  |
| Liquidation |  | 10 → 12 |  |  |  |  |
| Moongeist Beam | 95 → 100 |  |  |  |  |  |
| Zing Zap |  | 10 → 12 |  |  |  |  |
| Snipe Shot | 80 → 85 | 15 → 16 |  |  |  |  |
| Jaw Lock |  | 10 → 12 |  |  |  |  |
| Stuff Cheeks |  | 10 → 12 |  |  |  |  |
| No Retreat |  | 5 → 8 |  |  |  |  |
| Dragon Darts |  | 10 → 12 |  |  |  |  |
| Teatime |  | 10 → 12 |  |  |  |  |
| Octolock |  | 15 → 16 |  |  |  |  |
| Bolt Beak | 75 → 85 |  |  |  |  |  |
| Fishious Rend | 75 → 85 |  |  |  |  |  |
| Court Change |  | 10 → 12 |  |  |  |  |
| Clangorous Soul |  | 5 → 8 |  |  |  |  |
| Body Press |  | 10 → 12 |  |  |  |  |
| Decorate |  | 15 → 16 |  |  |  |  |
| Drum Beating |  | 10 → 12 |  |  |  |  |
| Snap Trap |  | 15 → 16 |  |  |  | Grass → Steel |
| Pyro Ball |  | 5 → 8 |  |  |  |  |
| Aura Wheel |  | 10 → 12 |  |  |  |  |
| Breaking Swipe |  | 15 → 16 |  |  |  |  |
| Overdrive |  | 10 → 12 |  |  |  |  |
| Apple Acid | 80 → 90 | 10 → 12 |  |  |  |  |
| Grav Apple | 80 → 90 | 10 → 12 |  |  |  |  |
| Spirit Break |  | 15 → 16 |  |  |  |  |
| Life Dew |  | 10 → 12 |  |  |  |  |
| Meteor Assault | 150 → 170 | 5 → 8 |  |  |  |  |
| Steel Beam |  | 5 → 8 |  |  |  |  |
| Expanding Force |  | 10 → 12 |  |  |  |  |
| Steel Roller |  | 5 → 8 |  |  |  |  |
| Meteor Beam |  | 10 → 12 |  |  |  |  |
| Shell Side Arm |  | 10 → 12 |  |  |  |  |
| Misty Explosion |  | 5 → 8 |  |  |  |  |
| Grassy Glide | 65 → 70 |  |  |  |  |  |
| Terrain Pulse |  | 10 → 12 |  |  |  |  |
| Skitter Smack | 65 → 70 | 10 → 12 |  |  |  |  |
| Burning Jealousy |  | 5 → 8 |  |  |  |  |
| Lash Out |  | 5 → 8 |  |  |  |  |
| Poltergeist |  | 5 → 8 |  |  |  |  |
| Coaching |  | 10 → 12 |  |  |  |  |
| Triple Axel | 20 → 40 | 10 → 12 |  |  |  |  |
| Dual Wingbeat | 40 → 45 | 10 → 12 |  |  |  |  |
| Scorching Sands |  | 10 → 12 |  |  |  |  |
| Wicked Blow | 75 → 80 |  |  |  |  |  |
| Freezing Glare | 80 → 90 |  |  |  |  |  |
| Thunderous Kick | 80 → 90 |  |  |  |  | Electric → Fighting |
| Glacial Lance | 110 → 130 |  |  |  |  |  |
| Eerie Spell |  | 5 → 8 |  |  |  |  |
| Dire Claw | 70 → 80 | 15 → 16 |  |  |  |  |
| Psyshield Bash | 70 → 90 | 10 → 12 |  |  |  |  |
| Stone Axe |  | 15 → 16 |  |  |  |  |
| Raging Fury | 100 → 120 | 10 → 12 |  |  |  |  |
| Wave Crash |  | 10 → 12 |  |  |  |  |
| Mountain Gale | 90 → 120 | 5 → 12 |  |  |  |  |
| Headlong Rush |  | 5 → 8 |  |  |  |  |
| Barb Barrage |  | 10 → 15 |  |  |  |  |
| Esper Wing | 65 → 80 |  |  |  |  |  |
| Shelter |  | 10 → 12 |  |  |  |  |
| Triple Arrows | 70 → 90 | 10 → 15 |  |  |  |  |
| Infernal Parade |  | 15 → 16 |  |  |  |  |
| Ceaseless Edge |  | 15 → 16 |  |  |  |  |
| Wildbolt Storm |  |  |  | 20 → 30 |  |  |
| Sandsear Storm |  |  |  | 20 → 30 |  |  |
| Take Heart |  | 10 → 15 |  |  |  |  |
| Axe Kick |  | 10 → 12 |  |  |  |  |
| Last Respects |  | 10 → 12 |  |  |  |  |
| Lumina Crash |  | 10 → 12 |  |  |  |  |
| Jet Punch |  | 15 → 16 |  |  |  |  |
| Spicy Extract |  | 15 → 16 |  |  |  |  |
| Population Bomb |  | 10 → 12 |  |  |  |  |
| Ice Spinner |  | 15 → 16 |  |  |  |  |
| Glaive Rush |  | 5 → 8 |  |  |  |  |
| Salt Cure |  | 15 → 16 |  |  |  |  |
| Triple Dive | 30 → 35 |  |  |  |  |  |
| Mortal Spin |  | 15 → 16 |  |  |  |  |
| Kowtow Cleave |  | 10 → 12 |  |  |  |  |
| Flower Trick |  | 10 → 12 |  |  |  |  |
| Torch Song |  | 10 → 12 |  |  |  |  |
| Aqua Step |  | 10 → 12 |  |  |  |  |
| Raging Bull |  | 10 → 12 |  |  |  |  |
| Make It Rain |  | 5 → 8 |  |  |  |  |
| Shed Tail |  | 10 → 12 |  |  |  |  |
| Chilly Reception |  | 10 → 12 |  |  |  |  |
| Tidy Up |  | 10 → 12 |  |  |  |  |
| Hyper Drill | 100 → 120 |  |  |  |  |  |
| Twin Beam |  | 10 → 12 |  |  |  |  |
| Rage Fist |  | 10 → 12 |  |  |  |  |
| Armor Cannon |  | 5 → 8 |  |  |  |  |
| Bitter Blade |  | 10 → 12 |  |  |  |  |
| Double Shock |  | 5 → 8 |  |  |  |  |
| Gigaton Hammer |  | 5 → 8 |  |  |  |  |
| Comeuppance |  | 10 → 12 |  |  |  |  |
| Matcha Gotcha | 75 → 80 | 15 → 16 |  |  |  |  |
| Syrup Bomb |  | 10 → 12 |  |  |  |  |
| Electro Shot |  | 10 → 12 |  |  |  |  |
| Fickle Beam |  | 5 → 8 |  |  |  |  |
| Hard Press |  | 10 → 12 |  |  |  |  |
| Dragon Cheer |  | 15 → 16 |  |  |  |  |
| Alluring Voice |  | 10 → 12 |  |  |  |  |
| Temper Flare |  | 10 → 12 |  |  |  |  |
| Supercell Slam |  | 15 → 16 |  |  |  |  |
| Psychic Noise |  | 10 → 12 |  |  |  |  |
| Upper Hand |  | 15 → 16 |  |  |  |  |

## 2. Critical hits and move properties

**High critical-hit ratio (+2 stages):** 25 moves: Karate Chop, Razor Wind, Razor Leaf, Sky Attack, Crabhammer, Slash, Aeroblast, Cross Chop, Blaze Kick, Air Cutter, Poison Tail, Leaf Blade, Night Slash, Shadow Claw, Psycho Cut, Cross Poison, Stone Edge, Attack Order, Spacial Rend, Drill Run, Snipe Shot, Esper Wing, Triple Arrows, Aqua Cutter, Ivy Cudgel.

**Properties:**

- **Magic Coat / Magic Bounce no longer reflect it** (16): Defog, Disable, Embargo, Encore, Foresight, Heal Block, Miracle Eye, Odor Sleuth, Roar, Spikes, Spite, Stealth Rock, Taunt, Torment, Toxic Spikes, Whirlwind
- **Mirror Move / Copycat can no longer copy it** (13): Counter, Dragon Cheer, Feint, Geomancy, Hold Hands, Mimic, Mirror Move, Nature Power, Protect, Snatch, Swords Dance, Taunt, Teeter Dance
- **Protect / Detect no longer block it** (7): Dragon Cheer, Geomancy, Mirror Move, Nature Power, Protect, Snatch, Swords Dance
- **Snatch no longer steals it** (9): Aqua Ring, Healing Wish, Imprison, Lucky Chant, Lunar Dance, Magnet Rise, Power Trick, Recycle, Wish
- **now hits all adjacent foes (doubles)** (1): Surf

## 3. Behaviour changes (moves and abilities)

**committed behaviour_cards.json at HEAD**

| Card | Kind | What it does |
|---|---|---|
| Double-Edge (Gen I) | move | Recoil. Gen I-II: 1/4 of damage dealt (Gen I: none when it breaks a Substitute). Gen III onward: 1/3. Lowest recoil is Gen I-II. (Power 100 in Gen I-III, 120 after, is a separate row.) |
| Astonish (Gen III) | move | Gen III only: double damage against a target that used Minimize. Removed from Gen IV. |
| Extrasensory (Gen III) | move | Gen III only: double damage against a target that used Minimize. Removed from Gen IV. |
| Needle Arm (Gen III) | move | Gen III only: double damage against a target that used Minimize. Removed from Gen IV. |
| Phantom Force (Gen VI) | move | Gen VI only: double damage and never misses against a target that used Minimize. Removed from Gen VII. |
| Substitute (Gen II-V) | move | Gen I: a Substitute blocks sleep, paralysis and Leech Seed less reliably, and a 255+ damage hit always breaks it. Gen II-V: blocks all status and stat drops from others. Gen VI onward: sound moves and Infiltrator go through it, a drawback for the user. |
| Cute Charm (Gen III) | ability | Contact infatuation chance: 1/3 in Gen III, 30% from Gen IV. Gen III-IV only if the holder lost HP. Gen III's 33% is the highest. |
| Flame Body (Gen III) | ability | Contact burn chance: 1/3 in Gen III, 30% from Gen IV. Gen III-IV only if the holder lost HP. Gen III's 33% is the highest. |
| Poison Point (Gen III) | ability | Contact poison chance: 1/3 in Gen III, 30% from Gen IV. Gen III-IV only if the holder lost HP. Gen III's 33% is the highest. |
| Static (Gen III) | ability | Contact paralysis chance: 1/3 in Gen III, 30% from Gen IV. Gen III-IV: only triggers if the holder lost HP. Gen III's 33% is the highest. |
| Aerilate / Pixilate / Refrigerate (Gen VI) | ability | Normal moves become Flying with 1.3x power in Gen VI, 1.2x from Gen VII. Normal moves become Fairy with 1.3x power in Gen VI, 1.2x from Gen VII. Normal moves become Ice with 1.3x power in Gen VI, 1.2x from Gen VII. |
| Protect / Detect / Endure (Gen IV) | move | Chance when used repeatedly. Gen II: halves each time. Gen III: halves for three uses, then erratic. Gen IV-V: halves each time, floor 1/8. Gen VI onward: drops to 1/3 each time. Gen II and IV-V keep the best odds. Chance when used repeatedly. Gen II: halves each time. Gen III: halves for three uses, then erratic. Gen IV-V: halves each time, floor 1/8. Gen VI onward: drops to 1/3 each time. Gen IV-V keeps the best odds. |
| Parental Bond (Gen VI) | ability | Second hit does 50% damage in Gen VI, 25% from Gen VII. |
| High Jump Kick / Jump Kick (Gen I) | move | Crash damage on a miss. Gen I: 1 HP. Gen II: 1/8 of the damage it would have done. Gen III-IV: half the damage it would have done. Gen V onward: half the user's max HP. Smallest crash is Gen I. |
| Transistor (Gen VIII) | ability | Electric moves 1.5x in Gen VIII, 1.3x in Gen IX. |
| Brick Break (Gen III) | move | Gen III-IV: breaks screens even if the target is immune (e.g. a Ghost). Gen V onward: only if it actually hits. Gen III is slightly better for the user. |
| Payback (Gen IV) | move | Gen IV: power also doubles if the target switches out that turn (or the opponent uses an item). Gen V onward: switching out no longer counts. Gen IV is better. |
| Gale Wings (Gen VI) | ability | Gen VI: Flying moves always get +1 priority. Gen VII onward: only at full HP. Gen VI is far stronger. |
| Intimidate (Gen VII) | ability | Gen III-VII: lowers foes' Attack by 1. Gen VIII onward: Inner Focus, Oblivious, Own Tempo and Scrappy block it (worse for the holder). Strongest for the holder: Gen VII. |
| Leaf Guard (Gen IV) | ability | Gen IV: in sun blocks status, but the holder can still use Rest. Gen V onward: Rest fails in sun. Gen IV is better for the holder. |
| Parting Shot (Gen VI) | move | Gen VII onward: the user doesn't switch out if neither stat could be lowered. Gen VI always switches. |
| Heal Bell / Soundproof (Gen V) | mixed | Soundproof Pokemon are not cured in Gen III-IV and VI-VII; cured in Gen V. Gen VIII onward: Soundproof party members are skipped but the user is always cured. Gen II and V cure everyone. Whether the holder is cured by an ally's Heal Bell: no in Gen III-IV and VI-VII, yes in Gen V, and Gen VIII onward cured only if it used the move itself. Gen V helps the holder most. |
| Protean / Libero (Gen VI-VIII) | ability | Gen VI-VIII: changes type before every move. Gen IX: only once per switch-in. Gen VI-VIII is far stronger. Gen VIII: changes type before every move. Gen IX: only once per switch-in. |
| Disguise (Gen VII) | ability | Gen VIII onward: breaking the disguise also costs Mimikyu 1/8 HP. Gen VII doesn't. |

**Not done yet in this engine:** round 3: Disable 4-7, Taunt 3-5, Encore 4-8, Flail / Reversal Gen IV bands, Explosion / Self-Destruct Defense halving, Moonlight / Morning Sun / Synthesis Gen II, Thrash, Swallow, Arena Trap / Magnet Pull / Shadow Tag (Gen III), Anger Point, Magic Guard, Moody, Battle Bond, Snow -> Hail outside Snow Warning, Dauntless / Intrepid (Seaglass, Lazarus), Protect 5th+ use (Spirits, Dreamstone). (EXPANSION_BINARIES.md bottom)

## 4. Planned (NOT in any release)

Everything below is the Pokémon Legacy balance pass (`game_plans/legacy_balance_2026-11-26/`): decisions are closed and the manifests are built, but it is not applied in this repo; nothing here ships until the apply step runs.

### Planned: Pokémon Legacy move values (149 moves)

`from` is the value in the release plus the best-version tier above; Legacy values below the hack's are not applied.

| Move | Power | PP | Accuracy | Priority | Type |
|---|---|---|---|---|---|
| Double Slap | 15 → 20 | 10 → 35 | 85 → 100 |  | Normal → Fairy |
| Comet Punch |  | 15 → 25 | 90 → 100 |  |  |
| Mega Punch | 80 → 90 |  | 85 → 95 |  |  |
| Pay Day | 40 → 60 |  |  |  |  |
| Razor Wind |  | 10 → 15 |  |  | Normal → Flying |
| Cut | 50 → 60 |  | 95 → 100 |  | Normal → Bug |
| Fly |  |  | 95 → 100 |  |  |
| Bind | 15 → 35 |  | 85 → 100 |  |  |
| Slam |  | 20 → 25 | 95 → 100 |  |  |
| Mega Kick |  | 8 → 10 |  |  |  |
| Rolling Kick | 60 → 70 | 15 → 25 | 85 → 100 |  |  |
| Fury Attack |  | 20 → 35 |  |  |  |
| Wrap | 15 → 30 |  | 90 → 100 |  |  |
| Take Down | 90 → 95 |  | 85 → 100 |  |  |
| Poison Sting | 30 → 35 |  |  |  |  |
| Twineedle | 25 → 40 |  |  |  |  |
| Pin Missile |  | 20 → 30 |  |  |  |
| Supersonic |  |  | 55 → 70 |  |  |
| Sonic Boom |  |  | 90 → 100 |  |  |
| Acid | 40 → 65 |  |  |  |  |
| Hydro Pump |  | 8 → 10 |  |  |  |
| Ice Beam |  | 12 → 15 |  |  |  |
| Submission | 80 → 90 |  |  |  |  |
| Mega Drain |  | 15 → 25 |  |  |  |
| Poison Powder |  |  | 80 → 90 |  |  |
| Dragon Rage |  | 10 → 20 |  |  |  |
| Thunder |  |  | 75 → 85 |  |  |
| Rock Throw |  | 15 → 25 | 90 → 95 |  |  |
| Dig |  | 12 → 20 |  |  |  |
| Psychic |  | 12 → 15 |  |  |  |
| Rage | 20 → 60 |  |  |  |  |
| Egg Bomb | 100 → 110 | 10 → 15 | 75 → 100 |  | Normal → Grass |
| Lick | 30 → 40 |  |  |  |  |
| Smog | 30 → 40 |  | 70 → 100 |  |  |
| Sludge | 65 → 90 |  |  |  |  |
| Bone Club |  | 20 → 25 |  |  |  |
| Clamp | 35 → 50 | 15 → 20 |  |  |  |
| Spike Cannon | 25 → 30 |  |  |  | Normal → Steel |
| Constrict | 10 → 40 |  |  |  |  |
| Kinesis |  |  | 80 → 100 |  |  |
| Leech Life |  | 15 → 25 |  |  |  |
| Sky Attack |  | 8 → 10 |  |  |  |
| Transform |  |  |  | 0 → 1 |  |
| Dizzy Punch |  | 10 → 20 |  |  |  |
| Crabhammer | 100 → 110 |  | 95 → 100 |  |  |
| Fury Swipes | 18 → 20 | 15 → 20 | 80 → 100 |  |  |
| Bonemerang |  | 10 → 20 |  |  |  |
| Rock Slide | 75 → 80 | 12 → 15 | 90 → 95 |  |  |
| Tri Attack | 80 → 85 | 12 → 15 |  |  |  |
| Triple Kick | 15 → 30 | 10 → 15 | 95 → 100 |  |  |
| Flame Wheel | 60 → 65 |  |  |  |  |
| Snore | 50 → 60 | 16 → 20 |  |  |  |
| Aeroblast |  | 5 → 10 |  |  |  |
| Mach Punch | 40 → 50 |  |  |  |  |
| Feint Attack | 60 → 70 |  |  |  |  |
| Sludge Bomb | 90 → 95 | 12 → 15 |  |  |  |
| Octazooka | 65 → 70 |  |  |  |  |
| Zap Cannon |  | 8 → 10 | 50 → 70 |  |  |
| Icy Wind | 60 → 65 |  |  |  |  |
| Bone Rush |  | 12 → 20 |  |  |  |
| Giga Drain |  | 12 → 15 |  |  |  |
| Steel Wing | 70 → 75 |  |  |  |  |
| Present |  | 15 → 25 | 90 → 100 |  |  |
| Sacred Fire |  | 5 → 10 |  |  |  |
| Dynamic Punch |  | 8 → 10 | 50 → 70 |  |  |
| Dragon Breath | 60 → 70 |  |  |  |  |
| Iron Tail |  |  | 75 → 90 |  |  |
| Metal Claw | 50 → 70 |  | 95 → 100 |  |  |
| Vital Throw |  | 10 → 20 |  |  |  |
| Cross Chop |  | 8 → 10 | 80 → 90 |  |  |
| Twister | 40 → 70 |  |  |  |  |
| Rain Dance |  | 8 → 10 |  |  |  |
| Sunny Day |  | 8 → 10 |  |  |  |
| Extreme Speed |  | 8 → 15 |  |  |  |
| Rock Smash | 40 → 60 |  |  |  |  |
| Uproar |  | 12 → 25 |  |  |  |
| Heat Wave |  |  | 90 → 100 |  |  |
| Smelling Salts | 70 → 75 | 10 → 15 |  |  |  |
| Dive | 80 → 90 | 12 → 15 |  |  |  |
| Arm Thrust | 15 → 18 |  |  |  |  |
| Luster Purge |  | 5 → 15 |  |  |  |
| Mist Ball |  | 5 → 15 |  |  |  |
| Blaze Kick |  | 12 → 15 | 95 → 100 |  |  |
| Needle Arm | 60 → 80 | 15 → 20 |  |  |  |
| Hyper Voice | 90 → 100 |  |  |  |  |
| Poison Fang | 50 → 60 |  |  |  |  |
| Crush Claw | 75 → 80 | 12 → 15 |  |  |  |
| Astonish | 30 → 50 |  |  |  |  |
| Weather Ball |  | 12 → 30 |  |  |  |
| Air Cutter | 60 → 65 |  |  |  |  |
| Rock Tomb |  | 16 → 25 |  |  |  |
| Signal Beam | 75 → 85 |  |  |  |  |
| Shadow Punch | 60 → 80 |  |  |  |  |
| Sky Uppercut | 85 → 90 |  |  |  |  |
| Muddy Water |  | 12 → 15 |  |  |  |
| Dragon Claw | 80 → 90 |  |  |  |  |
| Bounce |  | 8 → 15 | 85 → 90 |  |  |
| Mud Shot |  | 16 → 20 |  |  |  |
| Poison Tail | 50 → 80 |  |  |  |  |
| Covet |  |  |  |  | Normal → Fairy |
| Rock Blast |  | 12 → 15 |  |  |  |
| Doom Desire | 140 → 150 |  |  |  |  |
| Hammer Arm |  |  | 90 → 100 |  |  |
| Gyro Ball |  | 8 → 10 |  |  |  |
| Payback | 50 → 60 |  |  |  |  |
| Night Slash | 70 → 75 |  |  |  |  |
| Aqua Tail |  | 12 → 15 |  |  |  |
| X-Scissor | 80 → 85 |  |  |  |  |
| Dragon Pulse |  | 12 → 15 |  |  |  |
| Focus Blast |  | 8 → 10 |  |  |  |
| Energy Ball |  | 12 → 15 |  |  |  |
| Mud Bomb | 65 → 70 |  | 85 → 90 |  |  |
| Psycho Cut | 70 → 75 |  |  |  |  |
| Zen Headbutt | 80 → 85 |  |  |  |  |
| Mirror Shot | 65 → 70 | 10 → 15 |  |  |  |
| Flash Cannon | 80 → 90 | 12 → 15 |  |  |  |
| Rock Climb | 90 → 100 |  |  |  |  |
| Cross Poison | 70 → 80 |  |  |  |  |
| Gunk Shot |  | 8 → 10 | 80 → 85 |  |  |
| Stone Edge |  | 8 → 10 | 80 → 85 |  |  |
| Attack Order | 90 → 100 |  |  |  |  |
| Double Hit |  | 12 → 20 |  |  |  |
| Psyshock |  | 12 → 15 |  |  |  |
| Smack Down |  | 16 → 20 |  |  |  |
| Storm Throw |  | 12 → 15 |  |  |  |
| Round | 60 → 65 | 16 → 20 |  |  |  |
| Sky Drop | 60 → 70 |  |  |  |  |
| Retaliate |  | 5 → 10 |  |  |  |
| Inferno |  |  | 50 → 60 |  |  |
| Frost Breath |  | 12 → 15 |  |  |  |
| Drill Run |  | 12 → 15 | 95 → 100 |  |  |
| Horn Leech |  | 12 → 15 |  |  |  |
| Razor Shell | 75 → 80 | 12 → 15 | 95 → 100 |  |  |
| Steamroller | 65 → 80 |  |  |  |  |
| Night Daze |  | 12 → 15 |  |  |  |
| Tail Slap |  | 12 → 15 | 85 → 100 |  |  |
| Head Charge | 120 → 130 |  |  |  |  |
| Gear Grind |  |  | 90 → 95 |  |  |
| Relic Song | 75 → 85 |  |  |  |  |
| Icicle Crash |  |  | 90 → 95 |  |  |
| Fusion Flare |  | 5 → 10 |  |  |  |
| Fusion Bolt |  | 5 → 10 |  |  |  |
| Flying Press |  | 12 → 15 |  |  |  |
| Phantom Force |  | 12 → 15 |  |  |  |
| Disarming Voice | 40 → 60 | 15 → 20 |  |  |  |
| Play Rough |  | 12 → 15 |  |  |  |
| Mystical Fire | 75 → 80 | 12 → 15 |  |  |  |
| Dazzling Gleam |  | 12 → 15 |  |  |  |
| Infestation | 20 → 30 |  |  |  |  |

**Planned move effects (18; candidates, the apply step checks each hack's current effect first):**

- Vise Grip: stat:Attack-1 20% (emerald L.)
- Razor Wind: one turn + 100% trapping (bind-style), keep power/crit/targeting (user note)
- Razor Wind: status:Capture 100% (xy L.)
- Razor Wind: one-turn (emerald L.)
- Razor Wind: status:Trapped 100% (emerald L.)
- Razor Wind: one-turn (yellow L.)
- Slam: flinch 10% (yellow L.)
- Egg Bomb: category Special (Grass, X&Y L.) where the engine has the split
- Skull Bash: one-turn (yellow L.)
- Sky Attack: one turn (no charge), no retype, keep 200/90 and current flinch/crit (user note)
- Sky Attack: one-turn (emerald L.)
- Sky Attack: one-turn (crystal L.)
- Sky Attack: one-turn (yellow L.)
- Dizzy Punch: status:Confusion 10% (yellow L.)
- Rock Slide: flinch 10% (yellow L.)
- Crunch: defence drop matches Dark's category in this game (user note)
- Hyper Voice: status:Confusion 30% (emerald L.)
- Power Gem: stat:Special Defense-1 20% (xy L.)

**Skipped (2):** Night Shade (power 1 is a placeholder (fixed/variable damage); Legacy yellow power 60 not applied); Beat Up (power 1 is a placeholder (fixed/variable damage); Legacy crystal power 20 not applied)

### Planned: base stat changes (109 species)

Species Legacy changed get Legacy's per-stat delta on the hack's own line; a hack-customised line keeps the higher of each stat (user ruling 2026-11-26).

<details><summary>Show the stat table</summary>

| Species | Changes |
|---|---|
| Butterfree | HP 60 → 70, Def 50 → 60, SpD 80 → 90 |
| Beedrill | Atk 95 → 100, Spe 80 → 85 |
| Ekans | HP 35 → 40, Atk 60 → 65, Spe 55 → 60 |
| Arbok | Spe 80 → 90 |
| Sandslash | Spe 65 → 75 |
| Vulpix | HP 38 → 48, Def 40 → 45, Spe 65 → 75, SpD 60 → 70 |
| Ninetales | HP 73 → 78, Def 75 → 80, SpD 96 → 100 |
| Jigglypuff | Def 25 → 30, SpA 45 → 55, SpD 25 → 30 |
| Wigglytuff | Atk 60 → 70, Def 50 → 60, SpA 85 → 90, SpD 55 → 60 |
| Paras | HP 35 → 55, Def 55 → 60, SpD 55 → 60 |
| Parasect | HP 80 → 85, Atk 95 → 100, Def 85 → 90, SpD 85 → 90 |
| Meowth | Atk 50 → 55 |
| Persian | Atk 80 → 85, Spe 115 → 120 |
| Mankey | HP 40 → 45, Spe 70 → 75 |
| Primeape | HP 65 → 70, Spe 95 → 100 |
| Victreebel | Atk 105 → 120, Spe 70 → 75, SpA 100 → 115, SpD 70 → 60 |
| Ponyta | Spe 90 → 100 |
| Rapidash | Spe 115 → 125 |
| Seel | Atk 45 → 55, SpD 65 → 70 |
| Dewgong | Atk 75 → 80, Spe 65 → 70, SpD 90 → 95 |
| Grimer | HP 80 → 90, SpD 50 → 75 |
| Muk | HP 110 → 115 |
| Onix | HP 35 → 45 |
| Drowzee | HP 60 → 70, Spe 42 → 34 |
| Hypno | HP 90 → 100 |
| Electrode | Spe 150 → 160 |
| Flareon | HP 75 → 95 |
| Omanyte | SpA 80 → 90, SpD 55 → 65 |
| Omastar | SpA 95 → 115, SpD 70 → 80 |
| Noctowl | HP 100 → 110, Spe 65 → 70 |
| Ariados | SpA 60 → 70 |
| Chinchou | Spe 57 → 67, SpA 61 → 66 |
| Lanturn | Spe 62 → 67, SpA 81 → 86 |
| Igglybuff | Def 20 → 25 |
| Togetic | HP 65 → 75 |
| Natu | Spe 70 → 75 |
| Xatu | Spe 95 → 105 |
| Politoed | SpA 95 → 100 |
| Aipom | Atk 70 → 75 |
| Wooper | SpA 25 → 35, SpD 25 → 35 |
| Quagsire | SpA 65 → 75, SpD 65 → 75 |
| Murkrow | Atk 85 → 90, Spe 91 → 96 |
| Girafarig | SpA 90 → 100 |
| Corsola | HP 65 → 95, Atk 55 → 65, Def 95 → 105, SpA 65 → 75, SpD 95 → 105 |
| Remoraid | HP 35 → 45, Atk 55 → 60 |
| Octillery | SpA 100 → 115 |
| Stantler | Atk 85 → 105 |
| Blaziken | Spe 80 → 85 |
| Linoone | Atk 75 → 80 |
| Beautifly | Atk 50 → 80 |
| Dustox | SpD 90 → 100 |
| Kirlia | HP 38 → 43, Atk 35 → 40, Def 35 → 40, SpA 65 → 75, SpD 55 → 65 |
| Shedinja | SpA 30 → 75 |
| Nosepass | HP 30 → 45, Atk 45 → 40, Def 135 → 125, SpA 45 → 70, SpD 90 → 105 |
| Mawile | Atk 85 → 95, SpA 50 → 55 |
| Wailmer | Spe 60 → 55, SpA 70 → 85 |
| Wailord | Atk 85 → 90, Def 45 → 50, SpA 95 → 115, SpD 45 → 50 |
| Numel | HP 60 → 70 |
| Camerupt | Atk 95 → 105, SpA 100 → 110 |
| Torkoal | SpA 85 → 95 |
| Vibrava | HP 50 → 60, Atk 75 → 80, Def 55 → 60, SpA 50 → 70, SpD 55 → 60 |
| Flygon | SpA 85 → 90 |
| Swablu | HP 50 → 60 |
| Altaria | Def 85 → 90 |
| Barboach | SpA 46 → 56 |
| Whiscash | SpA 76 → 91 |
| Corphish | HP 43 → 53, SpA 50 → 60 |
| Crawdaunt | HP 63 → 73, SpA 70 → 100 |
| Armaldo | SpD 80 → 90 |
| Kecleon | Spe 30 → 40, SpA 60 → 70 |
| Banette | SpA 53 → 93 |
| Tropius | HP 109 → 120, Spe 42 → 51 |
| Snorunt | HP 50 → 60, Atk 50 → 60, Def 50 → 60, Spe 50 → 60, SpA 50 → 60, SpD 50 → 60 |
| Glalie | Spe 80 → 85, SpA 70 → 85 |
| Relicanth | Atk 90 → 110, Spe 35 → 55 |
| Rampardos | HP 97 → 107, Spe 58 → 63, SpA 65 → 60 |
| Bastiodon | HP 75 → 80, SpA 37 → 47, SpD 128 → 138 |
| Pachirisu | HP 60 → 70, Spe 95 → 110 |
| Cherubi | Atk 35 → 55 |
| Ambipom | Atk 100 → 105 |
| Honchkrow | Spe 71 → 91 |
| Chingling | SpA 65 → 70 |
| Chatot | Def 45 → 60 |
| Spiritomb | Atk 92 → 108, SpA 92 → 108 |
| Lumineon | Spe 91 → 106 |
| Snover | HP 60 → 70, Spe 40 → 30, SpA 62 → 72 |
| Abomasnow | HP 100 → 110, SpA 102 → 112 |
| Probopass | HP 60 → 70, SpA 80 → 105 |
| Dusknoir | HP 60 → 65, Atk 100 → 110 |
| Froslass | Atk 75 → 85, Def 70 → 75, SpD 71 → 75 |
| Blitzle | Spe 76 → 81 |
| Zebstrika | Spe 116 → 121 |
| Swoobat | Def 55 → 65, Spe 114 → 119, SpD 60 → 65 |
| Crustle | Spe 45 → 55, SpD 75 → 85 |
| Carracosta | Spe 32 → 52, SpA 83 → 73 |
| Swanna | Spe 98 → 108 |
| Cubchoo | HP 60 → 65, Spe 35 → 50 |
| Beartic | Spe 50 → 70 |
| Skiddo | Atk 65 → 70, Def 53 → 58 |
| Gogoat | Atk 104 → 105, Def 67 → 87, Spe 64 → 68, SpD 81 → 86 |
| Pangoro | HP 95 → 110, Spe 58 → 53, SpA 69 → 59 |
| Skrelp | HP 50 → 55, SpA 60 → 70, SpD 60 → 75 |
| Dragalge | HP 65 → 76, Spe 39 → 44 |
| Clauncher | Def 62 → 67, SpA 58 → 73, SpD 63 → 68 |
| Amaura | HP 77 → 87, Atk 59 → 46, Def 50 → 58, Spe 46 → 26, SpA 67 → 77, SpD 63 → 68 |
| Aurorus | Def 82 → 92, SpA 99 → 114, SpD 92 → 102 |
| Dedenne | HP 72 → 82 |
| Sliggoo | Spe 60 → 55, SpA 83 → 88 |
| Goodra | Spe 80 → 70, SpA 110 → 120 |

</details>

Not built yet: 92 Mega / form stat rows.

### Planned: species ability changes (108 slots)

<details><summary>Show the ability table</summary>

| Species | Slot | Old → new |
|---|---|---|
| Caterpie | 2 | (none) → Run Away |
| Caterpie | 3 | Run Away → Rattled |
| Butterfree | 2 | (none) → Tinted Lens |
| Butterfree | 3 | Tinted Lens → Overcoat |
| Weedle | 2 | (none) → Run Away |
| Weedle | 3 | Run Away → Rattled |
| Beedrill | 2 | (none) → Sniper |
| Beedrill | 3 | Sniper → Technician |
| Sandshrew | 1 | Sand Veil → Sand Rush |
| Sandslash | 1 | Sand Veil → Sand Rush |
| Vulpix | 2 | (none) → Drought |
| Vulpix | 3 | Drought → Solar Power |
| Ninetales | 2 | (none) → Drought |
| Ninetales | 3 | Drought → Solar Power |
| Jigglypuff | 2 | Competitive → Friend Guard |
| Wigglytuff | 2 | Competitive → Magic Bounce |
| Meowth | 3 | Unnerve → Super Luck |
| Persian | 3 | Unnerve → Super Luck |
| Golduck | 1 | Damp → Magic Guard |
| Poliwrath | 2 | Damp → Iron Fist |
| Ponyta | 3 | Flame Body → Reckless |
| Rapidash | 1 | Run Away → Quick Feet |
| Rapidash | 3 | Flame Body → Reckless |
| Dodrio | 1 | Run Away → Quick Feet |
| Seel | 3 | Ice Body → Simple |
| Dewgong | 3 | Ice Body → Simple |
| Kabuto | 3 | Weak Armor → Sand Rush |
| Kabutops | 3 | Weak Armor → Sand Rush |
| Ariados | 1 | Swarm → Poison Touch |
| Igglybuff | 2 | Competitive → Friend Guard |
| Politoed | 2 | Damp → Drizzle |
| Politoed | 3 | Drizzle → Swift Swim |
| Girafarig | 2 | Early Bird → Scrappy |
| Corsola | 2 | Natural Cure → Regenerator |
| Corsola | 3 | Regenerator → Natural Cure |
| Remoraid | 2 | Sniper → Analytic |
| Remoraid | 3 | Moody → Sniper |
| Octillery | 2 | Sniper → Analytic |
| Octillery | 3 | Moody → Sniper |
| Raikou | 1 | Pressure → Volt Absorb |
| Raikou | 2 | (none) → Volt Absorb |
| Entei | 1 | Pressure → Flash Fire |
| Entei | 2 | (none) → Flash Fire |
| Suicune | 1 | Pressure → Water Absorb |
| Suicune | 2 | (none) → Water Absorb |
| Lugia | 3 | Multiscale → Pressure |
| Ho-Oh | 3 | Regenerator → Pressure |
| Beautifly | 3 | Rivalry → Defiant |
| Wingull | 3 | Rain Dish → Hydration |
| Pelipper | 3 | Rain Dish → Drizzle |
| Wailmer | 2 | Oblivious → Rain Dish |
| Wailord | 2 | Oblivious → Rain Dish |
| Camerupt | 1 | Magma Armor → Flame Body |
| Camerupt | 3 | Anger Point → Sheer Force |
| Torkoal | 3 | Shell Armor → Drought |
| Whiscash | 1 | Oblivious → Gluttony |
| Lileep | 2 | (none) → Rain Dish |
| Cradily | 2 | (none) → Rain Dish |
| Anorith | 2 | (none) → Hyper Cutter |
| Armaldo | 2 | (none) → Hyper Cutter |
| Shuppet | 2 | Frisk → Prankster |
| Banette | 2 | Frisk → Prankster |
| Huntail | 3 | Water Veil → Guts |
| Gorebyss | 3 | Hydration → Marvel Scale |
| Stunky | 3 | Keen Eye → Defiant |
| Skuntank | 3 | Keen Eye → Defiant |
| Chatot | 2 | Big Pecks → Soundproof |
| Leafeon | 3 | Chlorophyll → Sniper |
| Glaceon | 3 | Ice Body → Heatproof |
| Gliscor | 2 | Sand Veil → Sand Rush |
| Gallade | 1 | Steadfast → Justified |
| Gallade | 3 | Justified → Steadfast |
| Probopass | 3 | Sand Force → Levitate |
| Dusknoir | 1 | Pressure → Cursed Body |
| Dusknoir | 2 | (none) → Cursed Body |
| Froslass | 1 | Snow Cloak → Frisk |
| Pansage | 3 | Overgrow → Sap Sipper |
| Simisage | 3 | Overgrow → Sap Sipper |
| Pansear | 3 | Blaze → Flash Fire |
| Simisear | 3 | Blaze → Flash Fire |
| Panpour | 3 | Torrent → Water Absorb |
| Simipour | 3 | Torrent → Water Absorb |
| Musharna | 2 | Synchronize → Unaware |
| Woobat | 1 | Unaware → Simple |
| Woobat | 3 | Simple → Unaware |
| Swoobat | 1 | Unaware → Simple |
| Swoobat | 3 | Simple → Unaware |
| Ducklett | 1 | Keen Eye → Hydration |
| Skrelp | 2 | Poison Touch → Adaptability |
| Skrelp | 3 | Adaptability → Liquid Ooze |
| Dragalge | 2 | Poison Touch → Adaptability |
| Dragalge | 3 | Adaptability → Liquid Ooze |
| Helioptile | 2 | Sand Veil → Solar Power |
| Helioptile | 3 | Solar Power → Sand Veil |
| Heliolisk | 2 | Sand Veil → Solar Power |
| Heliolisk | 3 | Solar Power → Sand Veil |
| Tyrunt | 2 | (none) → Sturdy |
| Tyrunt | 3 | Sturdy → Intimidate |
| Tyrantrum | 2 | (none) → Rock Head |
| Tyrantrum | 3 | Rock Head → Intimidate |
| Amaura | 2 | (none) → Wonder Skin |
| Aurorus | 2 | (none) → Wonder Skin |
| Goomy | 2 | Hydration → Gooey |
| Goomy | 3 | Gooey → Hydration |
| Sliggoo | 2 | Hydration → Gooey |
| Sliggoo | 3 | Gooey → Hydration |
| Goodra | 2 | Hydration → Gooey |
| Goodra | 3 | Gooey → Hydration |

</details>

82 slots where the hack already holds something other than Legacy's old ability keep the hack's (user ruling).

### Planned: learnset changes (1701 moves added, 1888 moves learned earlier)

<details><summary>Show the learnset changes</summary>

| Species | Added | Earlier |
|---|---|---|
| Metapod | Tackle L1, String Shot L1 |  |
| Butterfree | Tackle L1, Harden L1, String Shot L1, Leech Life L10, Giga Drain L27, Captivate L30, Signal Beam L37, Synchronoise L42 | Supersonic L23→L17, Whirlwind L29→L21, Psychic L37→L32, Air Slash L43→L32 |
| Kakuna | Poison Sting L1, String Shot L1 |  |
| Beedrill | String Shot L1, Harden L1, Poison Sting L1, Leech Life L10, Acid L21, Sludge L25, Spike Cannon L25, Swords Dance L30, Drill Run L37 | Pin Missile L32→L10, Rage L14→L10, Focus Energy L20→L12, Toxic Spikes L29→L21, Fell Stinger L44→L23, U-turn L38→L30, Poison Jab L35→L32 |
| Ekans | Substitute L22, Sludge L27, Crunch L28, Poison Jab L33, Sludge Bomb L36, Foul Play L48 | Bite L9→L6, Glare L12→L10, Acid L20→L13, Screech L17→L15, Poison Fang L26→L18, Gastro Acid L36→L20, Haze L41→L22, Acid Spray L28→L24, Mud Bomb L33→L30, Coil L44→L42, Gunk Shot L49→L45 |
| Arbok | Substitute L22, Sludge L27, Poison Jab L33, Sludge Bomb L36, Foul Play L48 | Glare L12→L10, Acid L20→L13, Screech L17→L15, Poison Fang L26→L18, Gastro Acid L36→L20, Haze L41→L22, Acid Spray L28→L24, Mud Bomb L33→L30, Coil L44→L42, Gunk Shot L49→L45 |
| Pikachu | Headbutt L18, Thunderpunch L20, Iron Tail L44, Volt Tackle L50 | Growl L5→L4, Quick Attack L10→L6, Thunder Wave L18→L10, Spark L26→L13, Double Team L23→L16, Discharge L34→L27, Agility L45→L30, Light Screen L53→L40, Thunder L58→L48 |
| Raichu | Nasty Plot L1, Headbutt L18, Iron Tail L44, Volt Tackle L53 | Growl L5→L1, Thunder Wave L18→L1, Quick Attack L10→L6, Spark L26→L13, Double Team L23→L15, Slam L37→L20, Nuzzle L29→L23, Discharge L34→L27, Thunderbolt L42→L30, Agility L45→L30, Light Screen L53→L40, Thunder L58→L41 |
| Sandshrew | Mud-Slap L9, Metal Claw L16, Cut L28, Drill Run L30, Sandstorm L32, X-Scissor L38, Spike Cannon L46 | Fury Swipes L20→L1, Sand Attack L3→L1, Poison Sting L5→L3, Sand Tomb L23→L5, Magnitude L14→L12, Dig L30→L14, Earthquake L46→L33 |
| Sandslash | Mud-Slap L9, Metal Claw L16, Spike Cannon L24, Cut L28, Drill Run L30, Sandstorm L32, X-Scissor L38 | Fury Swipes L20→L1, Sand Tomb L24→L5, Magnitude L14→L12, Dig L33→L14, Earthquake L53→L30, Swords Dance L43→L42 |
| Vulpix | Flame Wheel L19, Reflect L25, Shadow Ball L36, Night Shade L37, Sunny Day L40, Nasty Plot L51 | Tail Whip L4→L1, Roar L7→L4, Baby-Doll Eyes L9→L6, Quick Attack L10→L7, Fire Spin L15→L11, Feint Attack L23→L17, Flame Burst L28→L19, Hex L26→L25, Safeguard L34→L27, Flamethrower L36→L30, Captivate L47→L37, Fire Blast L42→L40, Inferno L50→L47 |
| Ninetales | Mystical Fire L1, Flame Wheel L19, Reflect L25, Shadow Ball L36, Night Shade L37, Sunny Day L40 | Tail Whip L4→L1, Roar L7→L1, Baby-Doll Eyes L9→L1, Fire Spin L15→L11, Will-O-Wisp L20→L17, Feint Attack L23→L17, Flame Burst L28→L19, Hex L26→L25, Imprison L39→L26, Flamethrower L36→L29, Captivate L47→L37, Fire Blast L42→L40, Inferno L50→L47 |
| Jigglypuff | Charm L7, Fake Tears L17, Lovely Kiss L22, Encore L33, Play Rough L33, Dazzling Gleam L41, Perish Song L48, Moonblast L51 | Pound L5→L1, Play Nice L9→L5, Double Slap L17→L8, Disable L14→L10, Rollout L20→L12, Round L22→L15, Rest L30→L24, Body Slam L32→L25, Hyper Voice L41→L36, Double-Edge L45→L41 |
| Wigglytuff | Boomburst L1, Charm L7, Fake Tears L17, Lovely Kiss L22, Encore L33, Dazzling Gleam L41, Perish Song L48, Moonblast L51 | Pound L5→L1, Play Nice L9→L1, Rollout L20→L12, Round L22→L15, Rest L30→L24, Body Slam L32→L25, Hyper Voice L41→L36, Double-Edge L45→L39 |
| Paras | Mega Drain L13, Twineedle L29, Seed Bomb L34, Swords Dance L37, Moonlight L46 | Absorb L11→L3, Leech Life L30→L8, Growth L33→L15, Slash L25→L21, Giga Drain L38→L26, Aromatherapy L43→L31, Rage Powder L49→L40, X-Scissor L54→L43 |
| Parasect | Mega Drain L13, Infestation L24, Twineedle L29, Seed Bomb L34, Swords Dance L37, Moonlight L46 | Growth L34→L15, Slash L25→L21, Giga Drain L38→L26, Aromatherapy L43→L31, Rage Powder L49→L40, X-Scissor L54→L43 |
| Meowth | Swift L20, Take Down L28, Power Gem L32, Snatch L36, Double-Edge L38, Swagger L40, Knock Off L43, Hyper Beam L45, Trump Card L48 | Bite L6→L1, Fake Out L9→L7, Fury Swipes L14→L8, Pay Day L30→L12, Captivate L46→L15, Feint Attack L22→L17, Taunt L25→L22, Slash L33→L24, Assurance L41→L26, Feint L50→L29, Night Slash L49→L34 |
| Persian | Pay Day L12, Swift L20, Take Down L28, Snatch L36, Double-Edge L38, Swagger L40, Knock Off L43, Trump Card L48, Hyper Beam L50 | Fury Swipes L14→L8, Captivate L56→L15, Feint Attack L22→L17, Taunt L25→L22, Assurance L49→L26, Feint L65→L29, Night Slash L61→L34 |
| Psyduck | Bubblebeam L17, Signal Beam L29, Scald L34, Psychic L37, Power Gem L42 | Tail Whip L4→L1, Water Gun L7→L4, Confusion L10→L7, Disable L19→L10, Fury Swipes L13→L10, Water Pulse L16→L13, Screech L22→L18, Zen Headbutt L25→L21, Aqua Tail L28→L24, Psych Up L34→L26, Amnesia L37→L29 |
| Golduck | Bubblebeam L17, Signal Beam L29, Calm Mind L31, Scald L34, Power Gem L42 | Amnesia L37→L1, Confusion L10→L7, Fury Swipes L13→L10, Water Pulse L16→L13, Screech L22→L18, Zen Headbutt L25→L21, Aqua Tail L28→L24, Psych Up L34→L26, Psychic L49→L37, Hydro Pump L45→L43 |
| Mankey | Low Sweep L16, Submission L24, Work Up L26, Mega Punch L30 | Seismic Toss L15→L11, Assurance L26→L14, Screech L40→L19, Final Gambit L50→L48 |
| Primeape | Shadow Punch L1, Low Sweep L16, Covet L21, Submission L24, Work Up L26, Mega Punch L30 | Seismic Toss L15→L11, Assurance L26→L14, Screech L44→L19, Outrage L53→L52 |
| Growlithe | Growl L1, Snarl L24, Extreme Speed L49 | Ember L6→L1, Leer L8→L6, Odor Sleuth L10→L8, Helping Hand L12→L10, Flame Wheel L17→L13, Take Down L23→L16, Retaliate L32→L31 |
| Arcanine | Growl L1, Snarl L24 | Agility L30→L1, Ember L6→L1, Leer L8→L6, Helping Hand L12→L10, Flame Wheel L17→L13, Take Down L23→L16, Retaliate L32→L31 |
| Poliwag | Mind Reader L1, Mist L4, Helping Hand L27, Muddy Water L31, Amnesia L36, Double-Edge L49 | Doubleslap L15→L1, Water Gun L5→L1, Hypnosis L8→L1, Bubble L11→L10, Mud Shot L28→L15, Bubble Beam L25→L18, Wake-Up Slap L35→L34, Mud Bomb L41→L39 |
| Poliwhirl | Mist L1, Mind Reader L1, Karate Chop L25, Helping Hand L27, Ice Punch L30, Muddy Water L31, Amnesia L36, Double-Edge L49 | Doubleslap L15→L10, Bubble L11→L10, Mud Shot L32→L15, Bubble Beam L27→L18, Wake-Up Slap L43→L34, Mud Bomb L53→L39, Hydro Pump L48→L42 |
| Poliwrath | Mist L1, Karate Chop L1, Ice Punch L1, Mind Reader L1, Hammer Arm L1, Dive L1, Detect L1, Comet Punch L12, Mach Punch L15, Muddy Water L31, Bulk Up L36, Amnesia L48 | Bubble L11→L1, Bubblebeam L27→L20, Hydro Pump L48→L42 |
| Bellsprout | Headbutt L27, Leaf Tornado L27, Body Slam L30, Sludge Bomb L32, Cross Poison L38, Leaf Storm L53 | Sweet Scent L32→L1, Growth L7→L5, Wrap L11→L8, Acid L23→L12, Poisonpowder L15→L13, Stun Spore L17→L16, Razor Leaf L25→L20, Sludge L29→L25, Gastro Acid L35→L32, Wring Out L50→L45 |
| Weepinbell | Headbutt L27, Leaf Tornado L27, Body Slam L30, Sludge Bomb L32, Cross Poison L38, Slam L45, Leaf Storm L53 | Poisonpowder L15→L1, Sweet Scent L32→L1, Acid L23→L12, Stun Spore L17→L16, Razor Leaf L25→L20, Sludge L29→L25, Gastro Acid L35→L32, Wring Out L50→L45 |
| Victreebel | Headbutt L27, Body Slam L30, Sludge Bomb L32, Cross Poison L38, Slam L45 | Growth L7→L1, Wrap L11→L1, Acid L23→L1, Poisonpowder L15→L13, Stun Spore L17→L16, Sludge L29→L25, Gastro Acid L35→L32, Wring Out L50→L45 |
| Tentacool | Bubble L1, Whirlpool L9, Water Gun L13, Sludge L25, Sludge Bomb L34 | Supersonic L4→L1, Constrict L7→L3, Acid L10→L6, Water Pulse L16→L13, Wrap L19→L15, Acid Spray L22→L18, Bubble Beam L25→L19, Barrier L28→L26, Poison Jab L32→L29, Brine L34→L33, Screech L37→L36, Sludge Wave L43→L40 |
| Tentacruel | Bubble L1, Whirlpool L9, Water Gun L13, Sludge L20, Sludge Bomb L34 | Water Pulse L16→L13, Wrap L19→L15, Acid Spray L22→L18, Bubble Beam L25→L19, Barrier L28→L26, Poison Jab L33→L29, Brine L36→L33, Screech L40→L36, Sludge Wave L48→L40, Hex L44→L43, Hydro Pump L52→L47 |
| Ponyta | Double Kick L14, Sunny Day L25, Blaze Kick L29, Flamethrower L33, High Jump Kick L42, Double-Edge L49 | Fire Spin L25→L1, Ember L9→L6, Stomp L17→L9, Flame Charge L21→L12, Take Down L29→L22, Bounce L45→L32, Agility L37→L34 |
| Rapidash | Tackle L1, Double Kick L14, Sunny Day L25, Blaze Kick L29, Flamethrower L33, Hi Jump Kick L40, Double-Edge L49 | Fire Spin L25→L1, Stomp L17→L9, Flame Charge L21→L12, Take Down L29→L22, Bounce L45→L32, Agility L37→L34 |
| Magnemite | Swift L24, Reflect L27, Tri Attack L30, Thunderbolt L33, Electric Terrain L42, Thunder L50 | Sonic Boom L17→L8, Spark L19→L17, Screech L35→L19, Electro Ball L29→L22, Magnet Rise L43→L28, Discharge L37→L36, Gyro Ball L47→L45 |
| Magneton | Swift L24, Reflect L27, Thunderbolt L33, Thunder L50, Refresh L57 | Spark L19→L17, Screech L39→L19, Electro Ball L29→L22, Magnet Rise L53→L28, Discharge L43→L37, Gyro Ball L59→L45 |
| Doduo | Low Kick L23, Bounce L24, Acupressure L27, Double Hit L31, Agility L33, Tri Attack L39, Double-Edge L50, Mega Kick L52 | Uproar L29→L1, Double Kick L22→L11, Drill Peck L43→L34, Endeavor L47→L37 |
| Dodrio | Low Kick L23, Bounce L24, Acupressure L27, Agility L33, Double-Edge L50, Mega Kick L52 | Uproar L29→L1, Blaze Kick L33→L1, Thrash L50→L1, Double Kick L22→L11, Drill Peck L43→L34, Endeavor L47→L37 |
| Seel | Whirlpool L1, Powder Snow L1, Water Gun L5, Bubblebeam L25, Work Up L27, Avalanche L44, Blizzard L50 | Growl L3→L1, Water Sport L7→L3, Aqua Jet L31→L7, Icy Wind L11→L10, Encore L13→L12, Aqua Ring L23→L15, Aurora Beam L27→L16, Brine L33→L20, Take Down L37→L24, Dive L41→L30, Ice Beam L47→L32, Safeguard L51→L38, Aqua Tail L43→L41, Hail L53→L46 |
| Dewgong | Water Gun L1, Powder Snow L1, Drill Run L1, Whirlpool L1, Water Sport L1, Bubblebeam L25, Work Up L27, Avalanche L44, Blizzard L50 | Aqua Jet L31→L7, Encore L13→L12, Aqua Ring L23→L15, Brine L33→L20, Aurora Beam L27→L22, Take Down L39→L24, Dive L45→L30, Ice Beam L51→L32, Safeguard L61→L38, Aqua Tail L49→L41, Hail L65→L46 |
| Grimer | Acid L16, Fling L17, Sludge Wave L22, Toxic L24, Mud Shot L26, Payback L27, Poison Jab L30, Body Slam L37, Pain Split L38, Punishment L45 | Mud-Slap L7→L6, Disable L12→L8, Sludge L15→L11, Minimize L21→L12, Mud Bomb L18→L14, Screech L37→L19, Acid Armor L43→L24, Belch L46→L35 |
| Muk | Ice Punch L1, Thunder Punch L1, Acid L16, Fling L17, Sludge Wave L22, Toxic L24, Mud Shot L26, Payback L27, Poison Jab L30, Body Slam L37, Pain Split L38, Punishment L45, Hammer Arm L52 | Disable L12→L1, Fire Punch L32→L1, Sludge L15→L11, Minimize L21→L12, Mud Bomb L18→L14, Screech L37→L19, Acid Armor L46→L24, Belch L52→L35, Memento L57→L48 |
| Shellder | Bubble Beam L22, Blizzard L50, Explosion L55 | Withdraw L4→L1, Supersonic L8→L4, Whirlpool L39→L7, Aurora Beam L37→L12, Protect L16→L14, Leer L20→L17, Ice Shard L26→L17, Clamp L23→L22, Iron Defense L47→L33, Ice Beam L52→L35, Brine L44→L35, Hydro Pump L61→L44, Shell Smash L56→L47 |
| Cloyster | Bubble Beam L22, Blizzard L50 | Clamp L23→L1, Whirlpool L39→L1, Leer L20→L17, Ice Shard L26→L17, Iron Defense L47→L33, Brine L44→L35, Ice Beam L52→L37, Hydro Pump L61→L50 |
| Gastly | Smog L4, Psywave L15, Clear Smog L18, Poison Gas L23 | Payback L26→L23, Hex L45→L28 |
| Haunter | Smog L1, Psywave L15, Clear Smog L18 | Payback L26→L23, Hex L45→L28, Dream Eater L36→L35 |
| Gengar | Smog L1, Psywave L1, Clear Smog L18 | Payback L26→L23, Hex L45→L28, Dream Eater L36→L35 |
| Onix | Bulldoze L18, Earthquake L40 | Rock Throw L7→L4, Rage L13→L6, Slam L28→L13, Stealth Rock L16→L15, Dig L43→L18, Sandstorm L52→L29, Rock Slide L34→L30, Screech L31→L30, Stone Edge L46→L43, Double-Edge L49→L46 |
| Drowzee | Dream Eater L24, Payback L27, Swagger L30, Skill Swap L35, Zen Headbutt L38, Foul Play L42 | Disable L5→L4, Confusion L9→L6, Headbutt L13→L9, Poison Gas L17→L11, Meditate L21→L14, Psybeam L23→L17, Psych Up L33→L20, Psychic L49→L33, Future Sight L61→L46, Nasty Plot L53→L49 |
| Hypno | Dream Eater L24, Payback L27, Swagger L30, Skill Swap L35, Zen Headbutt L38, Foul Play L42 | Headbutt L13→L9, Poison Gas L17→L11, Meditate L21→L14, Psybeam L23→L17, Psych Up L33→L20, Psychic L49→L32 |
| Voltorb | Rapid Spin L1, Thunder Wave L14, Thundershock L19, Electric Terrain L21, Thunderbolt L35, Thunder L40, Signal Beam L40, Rain Dance L42, Nasty Plot L54 | Eerie Impulse L6→L4, Swift L20→L17, Discharge L37→L35 |
| Electrode | Volt Tackle L1, Weather Ball L1, Rapid Spin L1, Thunder Wave L14, Thundershock L19, Electric Terrain L21, Thunderbolt L35, Thunder L40, Signal Beam L40, Rain Dance L42, Nasty Plot L54, Refresh L59 | Spark L9→L1, Swift L20→L17, Discharge L41→L35, Explosion L47→L44, Mirror Coat L58→L49 |
| Cubone | Tackle L1, Earthquake L47, Belly Drum L51, Iron Head L53 | Leer L13→L5, Focus Energy L17→L13, False Swipe L27→L15, Rage L23→L17, Fling L33→L27, Bone Rush L43→L33, Endeavor L41→L37, Double-Edge L51→L41, Retaliate L47→L43 |
| Marowak | Tackle L1, Head Smash L1, Earthquake L46, Belly Drum L51, Iron Head L53 | Leer L13→L5, Focus Energy L17→L13, False Swipe L27→L15, Rage L23→L17, Fling L33→L27, Bone Rush L43→L33, Endeavor L41→L37, Double-Edge L51→L41, Retaliate L47→L43 |
| Scyther | Razor Wind L1, Cut L15, Twineedle L42, Acrobatics L52 | Fury Cutter L25→L1, Pursuit L9→L8, False Swipe L13→L11, Slash L29→L28, Double Team L37→L31, Air Slash L50→L35, X-Scissor L41→L40, Night Slash L45→L44, Double Hit L49→L48, Feint L61→L57 |
| Tauros | Refresh L1, Rock Climb L1, Iron Head L1, Outrage L1, Captivate L1, Leer L15, Stomp L19, Headbutt L22, Punishment L29, Take Down L32, Superpower L50 | Tail Whip L3→L1, Rage L5→L4, Horn Attack L8→L7, Rest L19→L18, Work Up L29→L25, Swagger L48→L40, Thrash L55→L45, Double-Edge L63→L50, Giga Impact L71→L60 |
| Gyarados | Tackle L1, Gust L20, Waterfall L25, Bounce L44, Slam L48 | Leer L21→L1, Hyper Beam L54→L50 |
| Lapras | Icy Wind L15, Aurora Beam L23, Waterfall L34, Surf L43, Heal Pulse L46, Blizzard L55 | Brine L37→L29, Safeguard L43→L33 |
| Eevee | Double Kick L14, Headbutt L22, Focus Energy L30, Wish L35, Jump Kick L36 | Sand Attack L5→L4, Quick Attack L13→L6, Bite L17→L9, Charm L29→L20, Baton Pass L33→L30 |
| Vaporeon | Bubble L1, Growl L1, Icy Wind L1, Jump Kick L1, Mist L12, Double Kick L14, Bite L17, Bubblebeam L26, Brine L29, Rest L47, Ice Beam L52 | Sand Attack L5→L4, Quick Attack L13→L6, Aqua Ring L25→L22 |
| Jolteon | Growl L1, Magnet Rise L1, Jump Kick L1, Charge L12, Bite L17, Eerie Impulse L22, Spark L26, Charge Beam L29, Thunderbolt L36, Electric Terrain L48, Zap Cannon L52 | Sand Attack L5→L4, Quick Attack L13→L6, Double Kick L17→L14, Thunder L50→L49 |
| Flareon | Leer L1, Growl L1, Inferno L1, Jump Kick L1, Double Kick L14, Facade L25, Flame Wheel L26, Growth L32, Will-O-Wisp L35, Flamethrower L36, Double-Edge L36, Play Rough L48, Fire Blast L52, Superpower L52 | Sand Attack L5→L4, Quick Attack L13→L6, Fire Spin L25→L12, Scary Face L29→L22, Lava Plume L37→L29 |
| Omanyte | Rock Throw L14, Clamp L14, Bubblebeam L18, Horn Attack L22, Spike Cannon L27, Iron Defense L29, Rock Slide L37, Power Gem L38, Earth Power L45, Spikes L51 | Leer L19→L1, Water Gun L10→L5, Rollout L16→L12, Mud Shot L25→L17, Protect L34→L23, Ancient Power L37→L26, Tickle L43→L35, Hydro Pump L55→L46, Shell Smash L50→L49 |
| Omastar | Stealth Rock L1, Rock Throw L14, Clamp L14, Bubblebeam L18, Iron Defense L29, Rock Slide L37, Power Gem L38, Earth Power L45, Spikes L51 | Leer L19→L1, Water Gun L10→L1, Rollout L16→L12, Mud Shot L25→L17, Protect L34→L23, Ancient Power L37→L26, Tickle L43→L35, Hydro Pump L55→L46, Shell Smash L50→L49 |
| Kabuto | Rock Throw L6, Water Gun L11, Smack Down L15, Mega Drain L20, Metal Sound L21, Slash L32, Rock Slide L36, Swords Dance L42, X-Scissor L43, Hydro Pump L48, Stone Edge L53 | Leer L11→L1, Absorb L6→L1, Sand Attack L21→L1, Ancient Power L46→L26, Aqua Jet L31→L28 |
| Kabutops | Rock Throw L1, Water Gun L11, Smack Down L15, Mega Drain L20, Metal Sound L21, Rock Slide L36, Swords Dance L42, X-Scissor L43, Hydro Pump L48, Stone Edge L53 | Sand Attack L21→L1, Ancient Power L46→L26, Aqua Jet L31→L28 |
| Aerodactyl | Gust L1, Rock Throw L27, Double-Edge L45, Dragon Claw L50, Stone Edge L60 | Agility L17→L15, Ancient Power L25→L20, Take Down L41→L25, Sky Drop L49→L30, Rock Slide L51→L40, Hyper Beam L65→L50, Giga Impact L81→L65 |
| Dratini | Tackle L1, Headbutt L18, Dragon Breath L31, Tri Attack L53 | Twister L11→L9, Dragon Rage L15→L14, Agility L25→L22, Dragon Tail L31→L27, Safeguard L45→L40, Outrage L55→L45, Dragon Dance L51→L48, Hyper Beam L61→L54 |
| Dragonair | Tackle L1, Headbutt L18, Dragon Tail L27, Tri Attack L53 | Dragon Rage L15→L14, Agility L25→L22, Dragon Breath L33→L31, Aqua Tail L39→L35, Safeguard L53→L40, Dragon Rush L47→L44, Dragon Dance L50→L48, Outrage L63→L50, Hyper Beam L65→L61 |
| Dragonite | Tackle L1, Heal Bell L1, Extreme Speed L1, Headbutt L18, Dragon Breath L31, Tri Attack L53 | Dragon Rage L15→L14, Agility L25→L22, Dragon Tail L33→L27, Aqua Tail L39→L35, Safeguard L53→L40, Dragon Rush L47→L44, Dragon Dance L61→L48, Outrage L67→L56, Hyper Beam L75→L61 |
| Chikorita | Leech Seed L9, Mega Drain L21, Giga Drain L26, Seed Bomb L39, Heal Pulse L42, Sunny Day L46 | Razor Leaf L6→L4, Poison Powder L9→L6, Reflect L17→L12, Magical Leaf L20→L15, Natural Gift L23→L20, Light Screen L31→L23, Body Slam L34→L30, Safeguard L39→L34 |
| Bayleef | Leech Seed L9, Mega Drain L21, Giga Drain L26, Seed Bomb L39, Heal Pulse L42, Sunny Day L46 | Reflect L18→L12, Magical Leaf L20→L15, Natural Gift L26→L20, Light Screen L36→L23, Body Slam L40→L30, Safeguard L46→L34, Solarbeam L54→L45 |
| Meganium | Power Whip L1, Weather Ball L1, Leech Seed L9, Mega Drain L21, Giga Drain L26, Heal Pulse L42, Sunny Day L46, Flower Shield L54 | Reflect L18→L12, Magical Leaf L20→L15, Natural Gift L26→L20, Light Screen L36→L23, Body Slam L40→L30, Safeguard L46→L34, Solarbeam L54→L45 |
| Cyndaquil | Work Up L25, Sunny Day L34, Endure L47, Fire Blast L50, Heat Wave L51 | Ember L10→L4, Quick Attack L13→L10, Defense Curl L22→L12, Flame Wheel L19→L16, Swift L31→L19, Flame Charge L28→L23, Lava Plume L37→L29, Flamethrower L40→L31, Rollout L49→L31, Inferno L46→L42, Double-Edge L55→L45 |
| Quilava | Work Up L25, Sunny Day L34, Heat Wave L45, Endure L47, Fire Blast L50 | Ember L10→L1, Quick Attack L13→L10, Defense Curl L24→L12, Flame Wheel L20→L16, Swift L31→L19, Flame Charge L35→L23, Lava Plume L42→L29, Flamethrower L46→L31, Rollout L57→L31, Inferno L53→L42, Double-Edge L64→L45 |
| Typhlosion | Thunder Punch L1, Work Up L25, Sunny Day L34, Heat Wave L45, Endure L47, Fire Blast L50 | Quick Attack L13→L10, Defense Curl L24→L12, Flame Wheel L20→L16, Swift L31→L19, Flame Charge L35→L23, Lava Plume L42→L29, Flamethrower L46→L31, Rollout L57→L31, Inferno L53→L42 |
| Totodile | Bubble Beam L17, Agility L25, Dive L28 | Water Gun L6→L4, Bite L13→L11, Scary Face L15→L13, Chip Away L29→L22, Aqua Tail L43→L40 |
| Croconaw | Bubble Beam L17, Agility L25, Dive L28 | Bite L13→L11, Scary Face L15→L13, Ice Fang L21→L20, Chip Away L33→L22, Slash L39→L35, Screech L42→L37, Aqua Tail L51→L40, Hydro Pump L60→L50, Superpower L57→L51 |
| Feraligatr | Dynamic Punch L1, Bubble Beam L17, Circle Throw L22, Dive L28, Outrage L47 | Bite L13→L11, Scary Face L15→L13, Ice Fang L21→L20, Slash L39→L35, Screech L42→L37, Aqua Tail L51→L40, Hydro Pump L60→L50, Superpower L57→L51 |
| Hoothoot | Take Down L18, Psybeam L20, Light Screen L22, Wing Attack L24, Mirror Coat L30, Psychic L40, Hyper Voice L41, Defog L43, Future Sight L50 | Peck L7→L6, Echoed Voice L13→L10, Psycho Shift L19→L16, Roost L37→L29, Dream Eater L46→L45 |
| Noctowl | Future Sight L1, Take Down L18, Light Screen L22, Wing Attack L24, Mirror Coat L30, Psychic L40, Hyper Voice L41, Defog L43 | Echoed Voice L13→L10, Psycho Shift L19→L16, Psybeam L23→L20, Roost L43→L29, Air Slash L35→L33 |
| Spinarak | Leech Life L5, Fury Swipes L10, Poison Fang L13, Twineedle L18, Fell Stinger L22, Giga Drain L25, Psychic L30, Megahorn L43, Knock Off L44 | Scary Face L12→L1, Night Shade L15→L8, Shadow Sneak L19→L15, Spider Web L29→L20, Poison Jab L43→L27, Pin Missile L36→L35, Sticky Web L50→L38 |
| Ariados | Leech Life L1, Fury Swipes L10, Poison Fang L13, Twineedle L18, Giga Drain L25, Psychic L30, Megahorn L43, Knock Off L44 | Electroweb L55→L1, Night Shade L15→L8, Shadow Sneak L19→L15, Spider Web L32→L20, Poison Jab L47→L27, Pin Missile L41→L35, Sticky Web L52→L38, Cross Poison L44→L41 |
| Chinchou | Take Down L15, Thunderbolt L33, Rain Dance L33, Dive L35, Thunder L42, Charge L44 | Flail L31→L1, Thunder Wave L6→L5, Spark L23→L19, Signal Beam L28→L26, Discharge L34→L30, Ion Deluge L47→L38 |
| Lanturn | Take Down L15, Thunderbolt L33, Rain Dance L33, Dive L35, Thunder L42 | Flail L31→L1, Spark L23→L19, Signal Beam L28→L26, Discharge L34→L30, Ion Deluge L47→L38, Hydro Pump L45→L41 |
| Togepi | Helping Hand L1, Fairy Wind L1, Return L10, Disarming Voice L20, Swift L25, Dazzling Gleam L35, Tri Attack L43, Soft-Boiled L50 | Sweet Kiss L9→L7, Encore L17→L15, Follow Me L21→L17, Bestow L25→L22, Ancient Power L33→L27, Safeguard L37→L32, Double-Edge L45→L38, After You L53→L47 |
| Togetic | Helping Hand L1, Return L10, Disarming Voice L20, Tailwind L22, Wing Attack L24, Air Cutter L25, Tri Attack L39, Defog L47, Soft-Boiled L50 | Fairy Wind L14→L1, Encore L17→L15, Follow Me L21→L17, Ancient Power L29→L27, Safeguard L37→L32 |
| Natu | Morning Sun L1, Air Cutter L16, Psybeam L21, Recover L30, Baton Pass L30, Air Slash L31, Wing Attack L40, Drill Peck L40 | Miracle Eye L36→L1, Confusion L15→L4, Teleport L9→L7, Confuse Ray L23→L19, Wish L28→L25, Power Swap L47→L40, Guard Swap L47→L40 |
| Xatu | Ally Switch L1, Air Cutter L16, Psybeam L21, Recover L30, Baton Pass L30, Wing Attack L40, Drill Peck L40, Morning Sun L49 | Confusion L15→L1, Miracle Eye L35→L1, Confuse Ray L23→L19, Wish L29→L25, Psycho Shift L43→L34, Power Swap L53→L40, Guard Swap L53→L40 |
| Mareep | Shock Wave L21, Thunderbolt L47, Natural Gift L47, Tail Glow L62 | Cotton Spore L11→L4, Thundershock L8→L7, Confuse Ray L25→L24 |
| Flaaffy | Shock Wave L21, Thunderbolt L47, Natural Gift L47, Tail Glow L62 | Cotton Spore L11→L1, Charge L16→L15, Take Down L20→L18, Confuse Ray L29→L24, Power Gem L34→L33, Discharge L38→L37, Signal Beam L47→L41, Thunder L56→L52 |
| Ampharos | Shock Wave L21, Thunderbolt L47, Tail Glow L62 | Cotton Spore L11→L1, Charge L16→L15, Take Down L20→L18, Confuse Ray L29→L24, Power Gem L35→L33, Discharge L38→L37, Light Screen L57→L39, Cotton Guard L46→L44, Thunder L62→L52 |
| Politoed | Mist L1, Weather Ball L1, Sweet Kiss L1, Light Screen L15, Muddy Water L31, Ice Beam L36, Amnesia L36 | Bubble L11→L1, Bubblebeam L27→L20, Hydro Pump L43→L42 |
| Hoppip | Gust L1, Protect L24, Seed Bomb L42, Cotton Guard L45 | Tackle L8→L1, Synthesis L4→L3, Tail Whip L6→L5, Fairy Wind L10→L9, Poisonpowder L12→L10, Bullet Seed L19→L12, Mega Drain L25→L19, Leech Seed L22→L21, Cotton Spore L34→L24, U-turn L37→L26, Giga Drain L43→L30, Worry Seed L40→L38 |
| Skiploom | Gust L1, Protect L24, Seed Bomb L42, Cotton Guard L45 | Fairy Wind L10→L9, Poisonpowder L12→L10, Bullet Seed L20→L12, Mega Drain L28→L19, Leech Seed L24→L21, Cotton Spore L40→L24, U-turn L44→L26, Giga Drain L35→L30, Rage Powder L37→L35, Worry Seed L48→L38, Bounce L56→L48, Memento L60→L52 |
| Jumpluff | Gust L1, Encore L1, Protect L24, Seed Bomb L42, Cotton Guard L45 | Fairy Wind L10→L9, Poisonpowder L12→L10, Bullet Seed L20→L12, Mega Drain L28→L19, Leech Seed L24→L21, Cotton Spore L40→L24, U-turn L44→L26, Giga Drain L35→L30, Rage Powder L37→L35, Worry Seed L48→L38, Bounce L56→L48, Memento L60→L52 |
| Aipom | Pursuit L17, Low Kick L19, Dizzy Punch L28, Fling L35, Fake Out L38, Focus Punch L43, Beat Up L50 | Sand Attack L4→L3, Astonish L8→L6, Fury Swipes L18→L8, Tickle L16→L14, Swift L22→L20 |
| Yanma | Leech Life L1, Twister L12, Wing Attack L15, Supersonic L20, Signal Beam L24, Twineedle L25, Air Cutter L26, Air Slash L38, Acrobatics L49 | Quick Attack L6→L4, Sonic Boom L15→L10, U-turn L40→L35, Bug Buzz L46→L43 |
| Wooper | Mud-Slap L5, Headbutt L10, Bubble Beam L14, Magnitude L20, Body Slam L25, Aqua Tail L31 | Mud Sport L5→L4, Mud Shot L9→L7, Mud Bomb L19→L17, Amnesia L23→L19, Yawn L29→L28, Rain Dance L37→L33, Mist L43→L40, Haze L43→L40, Muddy Water L47→L45 |
| Quagsire | Recover L1, Mud-Slap L5, Headbutt L10, Bubble Beam L14, Magnitude L20 | Mud Shot L9→L1, Mud Bomb L19→L17, Amnesia L22→L19, Body Slam L27→L25, Yawn L31→L28, Aqua Tail L39→L31, Earthquake L35→L33, Rain Dance L41→L33, Mist L48→L40, Haze L48→L40, Muddy Water L53→L45 |
| Espeon | Growl L1, Ally Switch L1, Jump Kick L1, Telekinesis L12, Double Kick L14, Bite L17, Miracle Eye L25, Stored Power L45, Calm Mind L48, Reflect L52, Tri Attack L52 | Sand Attack L5→L4, Quick Attack L13→L6, Power Swap L45→L22 |
| Umbreon | Growl L1, Curse L1, Sucker Punch L1, Jump Kick L1, Torment L12, Double Kick L14, Bite L17, Snarl L20, Dark Pulse L37 | Sand Attack L5→L4, Quick Attack L13→L6, Guard Swap L45→L22 |
| Murkrow | Beat Up L1, Drill Peck L33, Sky Attack L53 | Quash L65→L1, Haze L11→L9, Wing Attack L15→L13, Night Shade L21→L17, Assurance L25→L21, Taunt L31→L25, Feint Attack L35→L29, Mean Look L41→L37, Foul Play L44→L41, Tailwind L50→L45, Sucker Punch L55→L49, Torment L61→L57 |
| Unown | Ancientpower L1 |  |
| Girafarig | Odor Sleuth L4, Bite L8, Zen Headbutt L27, Work Up L29, Tri Attack L40, Body Slam L42, Skill Swap L48 | Psybeam L19→L15, Double Hit L28→L24, Crunch L37→L32, Baton Pass L41→L33, Psychic L50→L38, Nasty Plot L46→L44 |
| Gligar | Mud-Slap L16, Wing Attack L18, Air Cutter L24, Earthquake L36, Sky Uppercut L38 | Sand Attack L4→L1, Harden L7→L3, Quick Attack L13→L6, Sand Tomb L25→L10, Fury Cutter L16→L14, Screech L35→L24 |
| Steelix | Bulldoze L18, Earthquake L45 | Rock Slide L34→L1, Rock Throw L7→L4, Rage L13→L6, Slam L28→L13, Stealth Rock L16→L15, Dig L43→L18, Screech L31→L30, Stone Edge L46→L43, Double-Edge L49→L46 |
| Scizor | Razor Wind L1, Cut L15, Double Team L24, Steel Wing L35, Twineedle L42 | Fury Cutter L25→L1, Pursuit L9→L8, False Swipe L13→L11, Slash L29→L28, Iron Defense L37→L31, X-Scissor L41→L40, Night Slash L45→L44, Double Hit L49→L48 |
| Heracross | Spike Cannon L1, Struggle Bug L1, Pin Missile L5, Work Up L6, Twineedle L34, Cross Chop L38 | Fury Attack L23→L15, Reversal L46→L41 |
| Sneasel | Pursuit L4, Assurance L15, Ice Punch L33, Night Slash L39, Beat Up L47, Blizzard L50 | Quick Attack L8→L6, Icy Wind L14→L9, Knock Off L28→L12, Fury Swipes L16→L13, Agility L20→L18, Metal Claw L22→L20, Slash L34→L22, Screech L32→L30 |
| Swinub | Take Down L26, Ice Fang L30, Dig L35, Icicle Crash L44 | Mud Sport L5→L3, Powder Snow L8→L6, Mud-Slap L11→L8, Endure L14→L12, Icy Wind L21→L16, Ice Shard L24→L19, Mist L35→L34, Amnesia L48→L45 |
| Piloswine | Ice Shard L19, Mud Shot L22, Take Down L26, Dig L35, Blizzard L50 | Mud-Slap L11→L1, Endure L14→L12, Icy Wind L21→L16, Mist L35→L34, Earthquake L43→L39, Amnesia L58→L45 |
| Corsola | Growth L1, Rock Throw L9, Water Gun L13, Spikes L22, Hydro Pump L43 | Bubble L4→L1, Refresh L13→L7, Lucky Chant L23→L12, Brine L27→L26, Power Gem L41→L31, Aqua Ring L38→L35 |
| Remoraid | Swift L5, Simple Beam L28, Seed Bomb L30, Scald L36, Sludge Bomb L41 | Lock-On L6→L1, Psybeam L10→L8, Bubble Beam L18→L11, Bullet Seed L38→L14, Focus Energy L22→L20, Water Pulse L26→L22, Ice Beam L34→L33 |
| Octillery | Zap Cannon L1, Lock-On L1, Water Pulse L22, Seed Bomb L30, Scald L36, Sludge Bomb L41, Egg Bomb L53 | Bubble Beam L18→L11, Bullet Seed L46→L14, Focus Energy L22→L20, Ice Beam L40→L33, Signal Beam L34→L33, Hydro Pump L55→L44, Hyper Beam L58→L48, Soak L64→L50 |
| Skarmory | Whirlwind L1, Swift L12, Air Cutter L14, Feint L17, Slash L35, Night Slash L43, Iron Defense L52, Defog L55, Brave Bird L59 | Fury Attack L15→L12, Spikes L28→L17, Metal Sound L42→L19, Steel Wing L34→L26, Drill Peck L45→L38 |
| Houndour | Torment L20, Flame Wheel L22, Snarl L23, Flame Burst L26, Feint Attack L29, Destiny Bond L56 | Roar L13→L7, Smog L8→L7, Bite L16→L12, Odor Sleuth L20→L15, Fire Fang L24→L18, Embargo L36→L31, Flamethrower L39→L38, Dark Pulse L45→L41, Nasty Plot L46→L45, Inferno L56→L52 |
| Houndoom | Torment L20, Flame Wheel L22, Flame Burst L26, Feint Attack L29, Destiny Bond L56 | Roar L13→L1, Bite L16→L1, Beat Up L28→L1, Odor Sleuth L20→L15, Fire Fang L24→L18, Embargo L36→L31, Flamethrower L39→L38, Dark Pulse L45→L41 |
| Phanpy | Mud-Slap L5, Mud Sport L7, Bulldoze L27, Earthquake L40, Curse L52 | Natural Gift L13→L12, Magnitude L16→L14 |
| Donphan | Mud-Slap L1, Odor Sleuth L1, Endure L19, Flail L23, Take Down L25, Scary Face L33, Superpower L44, Double-Edge L48, Curse L52 | Assurance L15→L12, Magnitude L16→L14, Body Slam L33→L30, Earthquake L43→L40 |
| Stantler | Pursuit L17, Reflect L33, Light Screen L33, Rock Climb L35, Double-Edge L40, Dream Eater L45 | Role Play L33→L1, Astonish L7→L6, Hypnosis L10→L9, Stomp L13→L12, Sand Attack L16→L14, Confuse Ray L23→L18, Captivate L50→L20, Zen Headbutt L38→L31, Jump Kick L43→L41, Imprison L49→L46 |
| Raikou | Aura Sphere L1, Charge L12, Extreme Speed L30, Thunderbolt L31, Mind Reader L74, Zap Cannon L80 | Roar L15→L1, Thunder Shock L8→L1, Quick Attack L20→L6, Spark L25→L11, Thunder Fang L40→L18, Reflect L30→L24, Rain Dance L55→L54, Thunder L70→L60 |
| Entei | Flame Wheel L11, Curse L11, Light Screen L24, Extreme Speed L30, Crunch L41, Sunny Day L54, Flare Blitz L60 | Roar L15→L1, Ember L8→L1, Stomp L25→L6, Fire Fang L40→L18 |
| Suicune | Air Slash L1, Whirlpool L1, Aqua Ring L1, Extreme Speed L30, Ice Beam L31, Surf L36, Reflect L41, Light Screen L51 | Mist L30→L1, Gust L20→L6 |
| Larvitar | Rock Throw L8, Smack Down L13, Bulldoze L25, Dragon Claw L56 | Screech L10→L9, Payback L37→L21, Thrash L28→L26, Stone Edge L50→L43 |
| Pupitar | Rock Throw L1, Smack Down L13, Bulldoze L25, Dragon Claw L56 | Payback L41→L21, Thrash L28→L26, Stone Edge L60→L43, Earthquake L54→L47, Hyper Beam L67→L61 |
| Tyranitar | Rock Throw L1, Smack Down L13, Bulldoze L25, Dragon Claw L56 | Payback L41→L21, Thrash L28→L26, Stone Edge L63→L43, Earthquake L54→L47, Hyper Beam L73→L61, Giga Impact L82→L67 |
| Lugia | Feather Dance L1, Aqua Tail L1, Defog L1, Whirlpool L10, Psycho Boost L66, Tailwind L75 | Gust L9→L1, Safeguard L65→L5, Natural Gift L85→L15, Extrasensory L23→L20, Recover L71→L22, Hydro Pump L37→L35, Aeroblast L43→L40, Ancientpower L57→L44, Future Sight L79→L60, Calm Mind L93→L65, Sky Attack L99→L70 |
| Ho-Oh | Heat Wave L1, Defog L1, Feather Dance L1, Fire Spin L10, Tailwind L75 | Gust L9→L1, Safeguard L65→L5, Natural Gift L85→L15, Extrasensory L23→L20, Recover L71→L22, Fire Blast L37→L25, Sacred Fire L43→L40, Ancientpower L57→L44, Sky Attack L99→L60, Calm Mind L93→L65, Future Sight L79→L70 |
| Celebi | Helping Hand L1, Mega Drain L20, Zen Headbutt L25, Psybeam L30, Nasty Plot L60, Earth Power L65 | Heal Block L55→L1, Natural Gift L44→L1, Safeguard L10→L5, Magical Leaf L19→L10, Ancient Power L28→L15, Healing Wish L73→L30, Future Sight L64→L45, Perish Song L91→L50, Leaf Storm L82→L55 |
| Igglybuff | Fairy Wind L7, Double Slap L14, Round L14, Perish Song L25 | Pound L5→L1 |
| Torchic | Flame Charge L18, Feather Dance L34, Bounce L44, Overheat L48 | Ember L6→L5, Peck L14→L6, Quick Attack L23→L21, Mirror Move L41→L28, Flamethrower L46→L38 |
| Combusken | Fire Punch L23, Rolling Kick L25, Mach Punch L32, Bounce L44, Overheat L48, High Jump Kick L51, Brave Bird L55 | Peck L14→L7, Flame Charge L19→L18, Quick Attack L23→L21, Mirror Move L47→L28, Sky Uppercut L53→L38 |
| Blaziken | Mach Punch L1, Thunder Punch L1, Rolling Kick L25, Mirror Move L28, Bounce L44, Overheat L48 | Peck L14→L1, Flame Charge L19→L18, Quick Attack L23→L21, Sky Uppercut L57→L38, Slash L44→L41 |
| Zigzagoon | Fury Swipes L18, Slash L31, Double-Edge L38, Play Rough L42 | Tail Whip L5→L4, Mud Sport L17→L16, Covet L23→L22, Fling L41→L24, Flail L29→L26, Rest L35→L32, Belly Drum L37→L35 |
| Linoone | Pursuit L20, Pin Missile L29, Night Slash L46 | Mud Sport L17→L16, Fury Swipes L19→L18, Covet L24→L22, Fling L48→L24, Slash L32→L26, Rest L40→L32, Belly Drum L43→L35 |
| Silcoon | Tackle L1, String Shot L1, Poison Sting L5 |  |
| Beautifly | String Shot L1, Harden L1, Leech Life L10, Sleep Powder L12, Air Slash L30, Signal Beam L43, Hurricane L43, Beat Up L45, Defog L47 | Rage L37→L1, Stun Spore L15→L12, Morning Sun L17→L16, Air Cutter L20→L18, Whirlwind L30→L26 |
| Cascoon | Tackle L1, Poison Sting L1, String Shot L1 |  |
| Dustox | Poison Sting L1, String Shot L1, Harden L1, Leech Life L10, Silver Wind L17, Hypnosis L20, Reflect L27, Sludge Bomb L30, Signal Beam L43, Synchronoise L43, Imprison L45, Sticky Web L47, Psychic L48 | Poison Powder L15→L12, Moonlight L17→L16, Venoshock L20→L18 |
| Wingull | Hydro Pump L42, Tailwind L44, Defog L47 | Mist L12→L11, Quick Attack L19→L18, Air Slash L40→L36 |
| Pelipper | Air Cutter L22, Feather Dance L25, Rain Dance L32, Air Slash L36 | Supersonic L5→L1, Mist L12→L11, Payback L19→L18, Stockpile L33→L25, Swallow L33→L25, Spit Up L33→L25 |
| Kirlia | Fairy Wind L1, Psybeam L18, Wish L42, Moonblast L58 | Magical Leaf L17→L1, Charm L40→L16, Imprison L33→L32 |
| Gardevoir | Fairy Wind L1, Lucky Chant L15, Charm L16, Psybeam L18 | Magical Leaf L17→L1, Captivate L44→L23, Imprison L35→L32, Hypnosis L49→L47, Dream Eater L53→L49 |
| Shroomish | Synthesis L31 | Mega Drain L12→L11, Poison Powder L19→L18, Growth L29→L21, Toxic L33→L29, Seed Bomb L36→L34 |
| Breloom | Drain Punch L1, Bullet Seed L11, Brick Break L29, Worry Seed L42 | Feint L19→L18, Counter L22→L21, Force Palm L28→L26, Mind Reader L37→L33, Seed Bomb L44→L37, Dynamic Punch L50→L49 |
| Nincada | Silver Wind L28, X-Scissor L30 | Sand Attack L9→L1, Mud-Slap L17→L8, Fury Swipes L13→L11, Mind Reader L25→L15, Metal Claw L21→L18, Dig L37→L22, Bide L29→L27 |
| Ninjask | Gust L8, Aerial Ace L22, Silver Wind L28, U-turn L28, Air Cutter L34, Acrobatics L34, Metal Claw L38, Quick Guard L50 | Fury Swipes L13→L9, Mind Reader L29→L15 |
| Shedinja | Leech Life L1, Astonish L8, Gust L12, Silver Wind L23, Shadow Ball L29, X-Scissor L35, Faint Attack L38, Bug Buzz L44 | Fury Swipes L13→L9, Mind Reader L25→L15, Confuse Ray L29→L26, Heal Block L41→L32 |
| Nosepass | Headbutt L11, Shock Wave L17, Ancient Power L20, Smelling Salts L26, Iron Defense L34, Tri Attack L39, Thunderbolt L40, Sleep Talk L45 | Harden L4→L1, Block L7→L5, Rock Throw L10→L9, Sandstorm L34→L33 |
| Mawile | Sweet Scent L1, Double Slap L12, Meteor Mash L45, Metal Burst L47, Swords Dance L53 | Swallow L41→L1, Spit Up L41→L1, Fake Tears L5→L3, Bite L9→L6, Iron Defense L33→L27 |
| Aron | Rock Throw L9, Rock Blast L23, Submission L42, Earthquake L51, Head Smash L56 | Iron Defense L37→L15, Roar L19→L16, Take Down L28→L21, Metal Sound L31→L25 |
| Lairon | Rock Throw L9, Rock Blast L23, Metal Sound L25, Double-Edge L41, Submission L42, Earthquake L51, Head Smash L56 | Iron Defense L39→L15, Roar L19→L16, Take Down L28→L21, Autotomize L47→L44, Heavy Slam L51→L47 |
| Aggron | Submission L1, Rock Throw L9, Rock Blast L23, Metal Sound L25, Double-Edge L41, Autotomize L44, Earthquake L51, Head Smash L56 | Iron Defense L39→L15, Roar L19→L16, Take Down L28→L21, Heavy Slam L51→L47 |
| Meditite | Karate Chop L13, Jump Kick L22, Rolling Kick L23, Extrasensory L29, Drain Punch L32, Zen Headbutt L44 | Detect L9→L1, Endure L12→L10, Force Palm L17→L12, Psych Up L31→L20, Reversal L42→L38 |
| Medicham | Karate Chop L14, Jump Kick L22, Rolling Kick L23, Extrasensory L29, Drain Punch L32 | Endure L12→L10, Force Palm L17→L12, Psych Up L31→L20, Reversal L42→L38 |
| Roselia | Venoshock L25, Sludge L27, Solar Beam L50 | Sweet Scent L31→L1, Aromatherapy L43→L22, Ingrain L34→L33, Toxic L40→L37, Petal Dance L50→L40 |
| Wailmer | Tackle L1, Yawn L21, Body Slam L29, Heavy Slam L42, Curse L45, Wide Guard L51 | Growl L4→L3, Water Gun L7→L5, Rollout L10→L8, Whirlpool L13→L11, Astonish L16→L13, Mist L23→L16, Rest L29→L24, Water Spout L33→L32, Bounce L45→L35, Dive L41→L40 |
| Wailord | Double-Edge L1, Tackle L1, Noble Roar L1, Yawn L21, Body Slam L29, Heavy Slam L42, Curse L45, Wide Guard L51 | Whirlpool L13→L11, Astonish L16→L13, Mist L23→L16, Rest L29→L24, Water Spout L33→L32, Bounce L45→L35, Dive L41→L40, Hydro Pump L49→L48 |
| Numel | Mud-Slap L1, Flame Wheel L17, Take Down L20, Rock Slide L32, Eruption L45, Fissure L55 | Ember L5→L4, Focus Energy L8→L7, Flame Burst L15→L14, Amnesia L19→L17, Flamethrower L43→L36, Double-Edge L47→L46 |
| Camerupt | Mud-Slap L1, Heat Wave L1, Flame Wheel L17, Take Down L20, Flamethrower L36, Double-Edge L46 | Focus Energy L8→L7, Flame Burst L15→L14, Amnesia L19→L17, Earthquake L42→L40 |
| Torkoal | Clear Smog L14, Yawn L18, Sunny Day L24, Slack Off L33, Heat Crash L46, Overheat L50 | Withdraw L7→L1, Smokescreen L15→L1, Smog L4→L1, Rapid Spin L10→L1, Fire Spin L13→L6, Flame Wheel L18→L17, Body Slam L27→L25, Heat Wave L45→L30, Amnesia L40→L37 |
| Trapinch | Hyper Fang L33, Magnitude L38, Block L39, Screech L43, Bug Bite L43, Earthquake L47, Hyper Beam L55 | Mud-Slap L5→L4, Sandstorm L36→L15 |
| Vibrava | Bite L1, Uproar L20, Crunch L25, Dig L27, Signal Beam L33, Earthquake L47, Hyper Beam L55, Dragon Rush L55, Boomburst L59 | Supersonic L19→L1, Sandstorm L36→L15, Dragon Dance L41→L39 |
| Flygon | Superpower L1, Bite L1, Crunch L25, Dig L27, Signal Beam L33, Bug Buzz L44, Earthquake L47, Hyper Beam L55, Dragon Rush L55, Boomburst L59 | Sandstorm L36→L1, Supersonic L19→L1, Dragon Tail L28→L20 |
| Swablu | Air Cutter L13, Take Down L19, Pluck L23, Feather Dance L28, Heal Bell L29, Sky Attack L45 | Astonish L3→L1, Sing L5→L3, Fury Attack L7→L5, Safeguard L9→L7, Disarming Voice L11→L9, Refresh L26→L11, Round L17→L16, Hyper Voice L37→L33 |
| Altaria | Dragon Rush L1, Air Cutter L13, Take Down L19, Feather Dance L28, Heal Bell L29, Dragon Claw L42 | Fury Attack L7→L5, Safeguard L9→L7, Disarming Voice L11→L9, Refresh L26→L11, Round L17→L16, Hyper Voice L37→L33, Perish Song L52→L46 |
| Barboach | Yawn L14, Zen Headbutt L29, Earth Power L36 | Mud Sport L6→L5, Water Sport L6→L5, Water Gun L9→L8, Mud Bomb L13→L12, Magnitude L20→L13, Muddy Water L35→L29 |
| Whiscash | Yawn L14, Sleep Talk L26, Earth Power L36 | Mud Bomb L13→L12, Magnitude L20→L13, Muddy Water L39→L29, Future Sight L45→L39, Fissure L52→L50 |
| Corphish | Assurance L15, Aqua Jet L20, Metal Claw L24 | Leer L10→L9, Bubble Beam L14→L12, Taunt L34→L31 |
| Crawdaunt | Assurance L15, Aqua Jet L20, Metal Claw L24 | Bubble Beam L14→L12, Taunt L36→L31, Crabhammer L48→L36, Crunch L43→L39 |
| Baltoy | Smokescreen L3, Stealth Rock L8, Mud Shot L19, Psychic L36, Zen Headbutt L41, Earthquake L42, Hyper Beam L48, Recover L53 | Heal Block L10→L1, Mud-Slap L7→L5, Psybeam L16→L11, Self-Destruct L28→L17, Extrasensory L31→L27, Sandstorm L46→L30, Earth Power L40→L33, Imprison L52→L46 |
| Claydol | Gravity L1, Smokescreen L3, Stealth Rock L8, Mud Shot L19, Psychic L36, Zen Headbutt L41, Earthquake L42, Recover L53 | Heal Block L10→L1, Mud-Slap L7→L5, Psybeam L16→L11, Self-Destruct L28→L17, Extrasensory L31→L27, Sandstorm L46→L30, Earth Power L40→L33, Imprison L52→L46 |
| Lileep | Rock Throw L7, Mega Drain L12, Rock Blast L33, Stealth Rock L38, Recover L44 | Acid L5→L4, Brine L21→L20, Gastro Acid L31→L22, Stockpile L46→L30, Swallow L46→L30, Spit Up L46→L30, Wring Out L52→L50 |
| Cradily | Rock Throw L1, Leech Seed L1, Mega Drain L12, Rock Blast L33, Stealth Rock L38, Recover L44 | Brine L21→L20, Gastro Acid L31→L22 |
| Anorith | Rock Throw L15, Brine L20, Hone Claws L25, Twineedle L36, Stone Edge L45, Swords Dance L50 | Mud Sport L4→L1, Water Gun L15→L6, Smack Down L13→L8, Metal Claw L17→L14, Ancient Power L21→L17, Bug Bite L25→L23, Crush Claw L37→L28, Rock Blast L53→L32 |
| Armaldo | Iron Tail L1, Rock Throw L15, Brine L20, Hone Claws L25, Twineedle L36, Aqua Tail L41, Stone Edge L45, Swords Dance L50 | Smack Down L13→L8, Metal Claw L17→L14, Ancient Power L21→L17, Bug Bite L25→L23, Rock Blast L53→L32 |
| Kecleon | Fake Out L1, Conversion L1, Swift L20, Swagger L22, Psychic L37, Double-Edge L44 | Feint L10→L7, Psybeam L18→L16, Camouflage L30→L27, Substitute L42→L30, Shadow Claw L33→L32, Sucker Punch L46→L40 |
| Shuppet | Lick L1, Astonish L14, Revenge L25, Substitute L34, Destiny Bond L56 | Shadow Sneak L13→L12, Curse L26→L17, Snatch L42→L41, Grudge L46→L44, Phantom Force L54→L48 |
| Banette | Lick L1, Play Rough L1, Astonish L14, Revenge L25, Substitute L34, Shadow Claw L37, Destiny Bond L50 | Shadow Sneak L13→L12, Snatch L42→L41, Grudge L46→L44 |
| Duskull | Hypnosis L31, Shadow Punch L32, Pain Split L37, Snatch L37, Sucker Punch L44, Phantom Force L53 | Disable L6→L4, Astonish L9→L6, Foresight L14→L8, Pursuit L22→L11, Shadow Sneak L17→L14, Will-O-Wisp L25→L18, Hex L38→L21, Payback L49→L26, Curse L33→L28, Mean Look L46→L34, Shadow Ball L41→L40, Future Sight L54→L48 |
| Dusclops | Hypnosis L31, Pain Split L37, Snatch L37, Sucker Punch L44, Phantom Force L53 | Astonish L9→L1, Foresight L14→L8, Pursuit L22→L11, Shadow Sneak L17→L14, Will-O-Wisp L25→L18, Hex L38→L21, Payback L49→L26, Curse L33→L28, Mean Look L46→L34, Shadow Ball L41→L40 |
| Tropius | Outrage L1, Air Cutter L18, Sunny Day L23, Defog L43 | Sweet Scent L6→L5, Stomp L10→L9, Whirlwind L21→L11, Magical Leaf L16→L14, Solar Beam L54→L38, Synthesis L48→L45, Dragon Pulse L51→L46 |
| Chimecho | Follow Me L1, Helping Hand L1, Ally Switch L3, Echoed Voice L6, Disarming Voice L13, Psyshock L20, Psychic L38, Wish L38, Magic Room L44, Hyper Voice L47 | Psywave L16→L1, Recover L45→L1, Uproar L32→L10, Yawn L13→L11, Take Down L19→L16, Heal Bell L27→L22, Heal Pulse L47→L27, Safeguard L38→L32 |
| Snorunt | Fake Tears L23, Icicle Spear L24, Ice Beam L37, Body Slam L40, Endeavor L43 | Ice Shard L10→L7, Hail L50→L13, Headbutt L28→L18, Ice Fang L23→L21, Frost Breath L37→L26, Crunch L41→L30 |
| Glalie | Ice Ball L1, Super Fang L1, Scary Face L23, Icicle Spear L24, Icicle Crash L37, Body Slam L40, Explosion L47, Wide Guard L49 | Hail L54→L15, Headbutt L28→L18, Ice Fang L23→L21, Frost Breath L37→L26, Crunch L41→L30, Blizzard L48→L43 |
| Spheal | Water Pulse L25, Frost Breath L29, Dive L33, Avalanche L40, Hydro Pump L47, Slack Off L53 | Rollout L5→L4, Ice Ball L13→L11, Brine L17→L15, Body Slam L26→L16, Aurora Beam L21→L18, Rest L31→L25, Snore L31→L25 |
| Sealeo | Water Pulse L25, Frost Breath L29, Dive L33, Avalanche L40, Hydro Pump L47, Slack Off L53 | Rollout L5→L4, Ice Ball L13→L11, Brine L17→L15, Body Slam L26→L16, Aurora Beam L21→L18, Rest L31→L25, Snore L31→L25, Blizzard L50→L43, Sheer Cold L52→L50 |
| Walrein | Icicle Spear L1, Super Fang L1, Water Pulse L25, Frost Breath L29, Dive L33, Avalanche L40, Hydro Pump L47 | Rollout L5→L4, Ice Ball L13→L11, Brine L17→L15, Body Slam L26→L16, Aurora Beam L21→L18, Rest L31→L25, Snore L31→L25, Blizzard L50→L43, Sheer Cold L52→L50 |
| Huntail | Agility L1, Take Down L21, Double-Edge L43, Shell Smash L50 | Water Pulse L14→L9, Dive L26→L25, Coil L45→L30, Aqua Tail L39→L35, Hydro Pump L50→L47 |
| Gorebyss | Psybeam L27, Double-Edge L43, Shell Smash L50 | Agility L9→L1, Captivate L23→L5, Water Pulse L14→L9, Amnesia L16→L13, Dive L26→L25, Coil L45→L30, Dazzling Gleam L35→L32, Aqua Tail L39→L35, Hydro Pump L50→L47 |
| Relicanth | Water Pulse L18, Take Down L22, Sleep Talk L30, Rock Slide L37, Stealth Rock L46, Hydro Pump L51 | Rock Tomb L13→L10, Yawn L35→L13, Rest L42→L30, Double-Edge L50→L41 |
| Kyogre | Avalanche L1, Icy Wind L10, Rest L25, Surf L40 | Calm Mind L50→L45, Double-Edge L80→L50, Water Spout L90→L65 |
| Groudon | Iron Tail L1, Fire Punch L10, Stealth Rock L30, Flamethrower L45 | Rest L30→L25, Bulk Up L50→L45, Solar Beam L60→L50, Fire Blast L75→L60, Eruption L90→L65 |
| Rayquaza | Earth Power L1, Sky Drop L10, Dragon Claw L20, Tailwind L30, Sky Attack L75 | Ancient Power L15→L1, Rest L35→L15, Extreme Speed L45→L40, Dragon Dance L60→L45, Fly L65→L60 |
| Magikarp | Bounce L35 | Flail L30→L25 |
| Pichu | Spark L11, Bestow L18, Electro Ball L22 | Tail Whip L5→L4, Thunder Wave L18→L8 |
| Ralts | Fairy Wind L1, Psybeam L18, Wish L42, Moonblast L58 | Charm L34→L23 |
| Budew | Venoshock L20 |  |
| Roserade | Venoshock L25, Grass Whistle L43 | Growth L4→L1, Aromatherapy L43→L22 |
| Cranidos | Smack Down L12, Rock Slide L32, Stealth Rock L38, Iron Head L42, Agility L49 | Focus Energy L6→L5, Pursuit L10→L9, Scary Face L20→L18, Assurance L24→L21, Ancient Power L30→L23, Screech L42→L28, Zen Headbutt L37→L35 |
| Rampardos | Superpower L1, Smack Down L12, Rock Slide L32, Stealth Rock L38, Iron Head L42, Agility L49, Head Charge L54 | Focus Energy L6→L1, Pursuit L10→L1, Scary Face L20→L18, Assurance L24→L21, Ancient Power L30→L23, Screech L42→L28, Zen Headbutt L37→L35 |
| Shieldon | Smack Down L7, Counter L14, Mirror Shot L19, Stealth Rock L34, Stone Edge L38, Power Split L44 | Taunt L6→L4, Iron Defense L20→L16, Swagger L24→L21, Ancient Power L30→L23, Iron Head L42→L32 |
| Bastiodon | Super Fang L1, Quick Guard L1, Wide Guard L1, Smack Down L1, Counter L14, Mirror Shot L19, Stealth Rock L34, Stone Edge L38, Power Split L44, King’s Shield L52 | Iron Defense L20→L16, Swagger L24→L21, Ancient Power L30→L23, Iron Head L42→L32 |
| Pachirisu | Volt Switch L25, Lovely Kiss L41, Volt Tackle L49 | Quick Attack L5→L1, Nuzzle L19→L7, Endure L17→L15, Swift L21→L17, Electro Ball L25→L20, Sweet Kiss L29→L22, Super Fang L37→L27, Thunder Wave L33→L30, Discharge L41→L33, Hyper Fang L49→L37 |
| Buizel | Pound L1, Helping Hand L1, Bite L22, Quick Guard L25, Ice Fang L33, Aqua Tail L36, Crunch L40, Iron Tail L47 | Growl L4→L1, Water Sport L7→L3, Water Gun L15→L8, Pursuit L18→L14, Swift L21→L17, Aqua Jet L24→L20, Whirlpool L31→L27 |
| Floatzel | Pound L1, Helping Hand L1, Bite L22, Quick Guard L25, Aqua Tail L36, Iron Tail L47 | Water Gun L15→L8, Pursuit L18→L14, Swift L21→L17, Aqua Jet L24→L20, Whirlpool L31→L27 |
| Cherubi | Petal Dance L25, Natural Gift L30, After You L32, Body Slam L39, Heal Pulse L46 | Helping Hand L13→L1, Growth L7→L5, Leech Seed L10→L8, Magical Leaf L19→L12, Sunny Day L22→L16, Take Down L31→L20, Worry Seed L28→L22, Lucky Chant L40→L27, Petal Blizzard L47→L36 |
| Ambipom | Fire Punch L1, Thunder Punch L1, Ice Punch L1, Pursuit L17, Low Kick L23, Dizzy Punch L28, Fling L35, Fake Out L38, Focus Punch L43 | Fury Swipes L18→L8, Tickle L16→L14, Swift L22→L20 |
| Honchkrow | Brave Bird L1, Beat Up L1, Swagger L23, Drill Peck L33, Sky Attack L53, Dark Pulse L55 | Quash L65→L1, Night Shade L21→L17, Assurance L25→L21, Taunt L31→L25, Feint Attack L35→L29, Mean Look L41→L37, Foul Play L44→L41, Tailwind L50→L45, Torment L61→L57 |
| Chingling | Psyshock L19, Recover L24 | Growl L4→L1, Astonish L7→L3, Confusion L10→L5, Yawn L13→L8, Entrainment L19→L11, Uproar L32→L15 |
| Stunky | Pursuit L12, Poison Tail L24, Sludge Bomb L31, Gunk Shot L44 | Screech L7→L6, Acid Spray L19→L17, Toxic L27→L26, Night Slash L31→L29 |
| Skuntank | Fire Fang L1, Pursuit L12, Poison Tail L24, Sludge Bomb L31, Gunk Shot L44 | Acid Spray L19→L17, Toxic L27→L26, Night Slash L31→L29 |
| Bronzor | Gravity L1, Mirror Shot L16, Stealth Rock L24, Skill Swap L40, Zen Headbutt L52 | Imprison L9→L7, Confuse Ray L11→L10, Psywave L15→L12, Extrasensory L39→L27, Metal Sound L31→L30, Heavy Slam L49→L46 |
| Bronzong | Weather Ball L1, Trick L1, Gravity L1, Mirror Shot L16, Skill Swap L24, Zen Headbutt L52 | Confuse Ray L11→L10, Psywave L15→L12, Extrasensory L39→L27, Metal Sound L31→L30, Heavy Slam L49→L46 |
| Chatot | Flatter L1, Fury Attack L16, Disarming Voice L19, Air Slash L33, Nasty Plot L40, Parting Shot L46, Boomburst L49 | Echoed Voice L35→L1, Growl L5→L4, Mirror Move L9→L7, Round L29→L10, Uproar L41→L28, Mimic L33→L30, Feather Dance L50→L35 |
| Spiritomb | Ancient Power L1, Switcheroo L20, Revenge L25, Shadow Ball L40, Grudge L55, Phantom Force L60, Outrage L65, Parting Shot L70 | Feint Attack L7→L5, Hypnosis L13→L10, Dream Eater L19→L10, Ominous Wind L23→L15, Sucker Punch L31→L30, Nasty Plot L37→L35 |
| Skorupi | Poison Jab L31, X-Scissor L40 | Pursuit L16→L5, Bug Bite L20→L9, Acupressure L13→L12, Venoshock L27→L14, Poison Fang L23→L21, Hone Claws L30→L27, Night Slash L38→L37, Cross Poison L49→L46 |
| Drapion | Focus Energy L1, Poison Jab L31, X-Scissor L40 | Pursuit L16→L1, Bug Bite L20→L9, Acupressure L13→L12, Venoshock L27→L14, Poison Fang L23→L21, Hone Claws L30→L27, Night Slash L38→L37, Cross Poison L49→L46 |
| Finneon | Defog L1, Air Slash L28, Scald L31, Hydro Pump L44, Tailwind L46, Follow Me L51 | Attract L10→L1, Water Gun L6→L4, Gust L17→L7, Rain Dance L13→L11, Whirlpool L37→L13, Draining Kiss L20→L16, Water Pulse L22→L19, Captivate L26→L21, Silver Wind L49→L24, U-turn L43→L40 |
| Lumineon | Quiver Dance L1, Defog L1, Scald L31, Hydro Pump L44, Tailwind L46, Follow Me L51 | Rain Dance L13→L11, Whirlpool L37→L13, Draining Kiss L20→L16, Water Pulse L22→L19, Captivate L26→L21, Silver Wind L49→L24, Air Slash L40→L28, U-turn L43→L40 |
| Snover | Grass Knot L19, Ice Punch L32, Energy Ball L34, Worry Seed L39, Hammer Arm L50 | Mist L21→L11, Ice Shard L24→L23, Ingrain L31→L28 |
| Abomasnow | Leaf Storm L1, Grass Knot L19, Energy Ball L34, Worry Seed L39, Hammer Arm L50 | Mist L21→L11, Ice Shard L24→L23, Ingrain L31→L28 |
| Weavile | Pursuit L1, Slash L33, Ice Punch L35, Beat Up L44 | Icy Wind L14→L9, Fury Swipes L16→L13, Nasty Plot L20→L18, Metal Claw L22→L20, Screech L32→L30 |
| Togekiss | Return L10, Disarming Voice L20, Tailwind L22, Air Cutter L25, Tri Attack L45, Defog L47, Soft-Boiled L50 | Fairy Wind L14→L1, Encore L17→L15, Follow Me L21→L17, Ancient Power L29→L27, Safeguard L37→L32 |
| Yanmega | Defog L1, Leech Life L1, Feint L1, Twister L12, Wing Attack L15, Supersonic L20, Signal Beam L24, Air Cutter L26, Slash L28, Acrobatics L49 | Sonic Boom L15→L10, U-turn L40→L35 |
| Leafeon | Worry Seed L1, Jump Kick L1, Growl L1, Grassy Terrain L12, Double Kick L14, Bite L17, Bullet Seed L29, X-Scissor L48, Solar Beam L52 | Sand Attack L5→L4, Quick Attack L13→L6, Magical Leaf L20→L9, Leaf Blade L45→L37 |
| Glaceon | Sheer Cold L1, Jump Kick L1, Growl L1, Powder Snow L9, Disable L12, Double Kick L14, Haze L22, Frost Breath L29, Yawn L35, Ice Beam L37, Freeze-Dry L48 | Sand Attack L5→L4, Quick Attack L13→L6 |
| Gliscor | Wing Attack L18, Sky Uppercut L38, Earthquake L44, Sky Attack L59 | Quick Attack L13→L1, Sand Tomb L25→L10, Fury Cutter L16→L14, Screech L35→L24 |
| Mamoswine | Icy Wind L16, Ice Shard L19, Take Down L26, Dig L35, Amnesia L51 | Mud-Slap L11→L8, Endure L14→L12 |
| Gallade | Cross Chop L1, Double Kick L1, Brick Break L28, Sacred Sword L39, Zen Headbutt L46 | Wide Guard L23→L20 |
| Probopass | Heavy Slam L11, Shock Wave L17, Ancient Power L20, Flash Cannon L39 | Rock Throw L10→L1, Sandstorm L34→L33 |
| Dusknoir | Snatch L37, Sucker Punch L44, Phantom Force L53, Drain Punch L58 | Astonish L9→L1, Foresight L14→L8, Pursuit L22→L11, Shadow Sneak L17→L14, Will-O-Wisp L25→L18, Hex L38→L21, Payback L49→L26, Curse L33→L29, Mean Look L46→L34, Shadow Ball L41→L40 |
| Froslass | Trick L1, Icicle Spear L21, Frost Breath L26, Curse L49, Sheer Cold L58 | Hail L54→L15, Draining Kiss L23→L18, Captivate L41→L23, Ice Beam L44→L37, Blizzard L48→L47 |
| Lillipup | Headbutt L13, Covet L18, Punishment L37, Double-Edge L42 | Odor Sleuth L5→L3, Baby-Doll Eyes L10→L6, Helping Hand L12→L10, Work Up L19→L16 |
| Herdier | Baby-Doll Eyes L6, Headbutt L13, Covet L18, Punishment L37, Double-Edge L42 | Helping Hand L12→L10, Work Up L20→L16, Retaliate L33→L30, Reversal L37→L34, Play Rough L50→L49 |
| Stoutland | Baby-Doll Eyes L1, Headbutt L13, Covet L18, Punishment L37, Double-Edge L42, Giga Impact L55 | Helping Hand L12→L10, Work Up L20→L16, Retaliate L33→L30, Reversal L37→L34, Play Rough L50→L49 |
| Pansage | Role Play L8, Dizzy Punch L40, Wood Hammer L46, Snatch L49 | Lick L7→L6 |
| Simisage | Work Up L1, Role Play L8, Dizzy Punch L40, Wood Hammer L46, Snatch L49 | Acrobatics L32→L31 |
| Pansear | Role Play L8, Blaze Kick L34, Endeavor L40, Me First L49 | Lick L7→L6 |
| Simisear | Work Up L1, Role Play L8, Bite L19, Blaze Kick L34, Endeavor L40, Crunch L43, Me First L49 | Acrobatics L32→L31 |
| Panpour | Role Play L8, Hyper Voice L40, Hydro Pump L46, Encore L49 | Lick L7→L6 |
| Simipour | Work Up L1, Role Play L8, Brine L34, Hyper Voice L40, Hydro Pump L46, Encore L49 | Acrobatics L32→L31 |
| Munna | Zen Headbutt L17, Psyshock L25, Dazzling Gleam L30, Heal Bell L42, Moonblast L49 | Lucky Chant L5→L4, Yawn L7→L6, Psybeam L11→L10, Imprison L13→L12, Moonlight L17→L15, Nightmare L29→L22, Telekinesis L43→L27, Dream Eater L41→L39 |
| Musharna | Gravity L1, Zen Headbutt L17, Psyshock L25, Dazzling Gleam L30, Heal Bell L42, Moonblast L49 | Yawn L7→L1, Imprison L13→L12, Moonlight L17→L15, Nightmare L29→L22, Telekinesis L43→L27, Dream Eater L41→L39 |
| Blitzle | Double Kick L17, Ion Deluge L42, Jump Kick L46, Volt Tackle L50 | Tail Whip L4→L3, Charge L8→L5, Shock Wave L11→L9, Thunder Wave L15→L11, Flame Charge L18→L15, Spark L24→L20, Stomp L27→L25, Discharge L34→L28, Agility L36→L30, Wild Charge L39→L37, Thrash L52→L40 |
| Zebstrika | Outrage L1, Double Kick L17, Jump Kick L46, Volt Tackle L50 | Shock Wave L11→L1, Flame Charge L18→L15, Spark L24→L20, Stomp L27→L25, Discharge L34→L28, Agility L36→L30, Wild Charge L39→L37, Thrash L52→L40 |
| Woobat | Simple Beam L22, Extrasensory L26, Roost L35, Hurricane L43 | Odor Sleuth L4→L1, Gust L8→L4, Assurance L12→L8, Heart Stamp L15→L11, Attract L25→L13, Air Cutter L21→L16, Amnesia L29→L28, Air Slash L32→L31, Psychic L39→L38 |
| Swoobat | Trick L1, Simple Beam L22, Extrasensory L26, Roost L35, Hurricane L43 | Heart Stamp L15→L11, Attract L25→L13, Air Cutter L21→L16, Amnesia L29→L28, Air Slash L32→L31, Psychic L39→L38 |
| Timburr | Work Up L28 |  |
| Gurdurr | Work Up L28 |  |
| Conkeldurr | Fire Punch L1, Ice Punch L1, Thunder Punch L1, Work Up L28 |  |
| Sandile | Mud-Slap L1 | Torment L10→L7 |
| Krokorok | Mud-Slap L1 | Torment L10→L7 |
| Krookodile | Block L1, Mud-Slap L1 | Torment L10→L7 |
| Dwebble | Rock Throw L1, Sharpen L1, Stone Edge L40, Snatch L46 | X-Scissor L35→L34, Flail L41→L37 |
| Crustle | Rock Throw L1, Sharpen L1, Stone Edge L40, Heavy Slam L46 | X-Scissor L35→L34, Flail L41→L37, Rock Wrecker L53→L51 |
| Scraggy | Jump Kick L31, Fling L50 | Payback L19→L9, Facade L42→L40 |
| Scrafty | Zen Headbutt L1, Jump Kick L31, Fling L50 | Payback L19→L1, Facade L42→L40 |
| Tirtouga | Iron Defense L18, Aqua Tail L35, Hydro Pump L49, Stone Edge L53 | Rollout L5→L4, Bite L8→L7, Protect L11→L9, Aqua Jet L15→L12, Ancient Power L18→L16, Smack Down L31→L21, Brine L28→L24, Curse L35→L26, Rock Slide L45→L38, Rain Dance L48→L45 |
| Carracosta | Super Fang L1, Iron Defense L16, Aqua Tail L35, Stone Edge L53 | Bite L8→L7, Protect L11→L9, Aqua Jet L15→L12, Smack Down L31→L21, Brine L28→L24, Curse L35→L26, Rock Slide L45→L38, Rain Dance L48→L45 |
| Archen | Gust L1, Stone Edge L47, Sky Attack L57 | Ancient Power L18→L16, Dragon Breath L31→L25, Crunch L35→L28, Rock Slide L45→L32, Thrash L50→L37, Dragon Claw L48→L43 |
| Archeops | Defog L1, Gust L1, Stone Edge L47, Sky Attack L57 | Ancient Power L18→L16, Dragon Breath L31→L25, Rock Slide L45→L32, Thrash L50→L37, Dragon Claw L48→L43 |
| Zorua | Uproar L46 | Pursuit L5→L4, Fake Tears L9→L7, Fury Swipes L13→L11, Snarl L17→L15, Scary Face L21→L18, Punishment L45→L28, Agility L37→L35, Embargo L42→L40, Imprison L53→L52, Night Daze L57→L55 |
| Zoroark | Crush Claw L46 | Extrasensory L40→L1, Fury Swipes L13→L11, Snarl L17→L15, Scary Face L21→L18, Punishment L45→L28, Agility L37→L35, Embargo L42→L40 |
| Gothita | Torment L5, Trick Room L29, Foul Play L49 | Play Nice L8→L1, Double Slap L14→L10, Psybeam L16→L13, Embargo L19→L18, Feint Attack L24→L21, Psyshock L25→L24, Flatter L28→L26, Dark Pulse L39→L38, Charm L46→L40 |
| Gothorita | Torment L5, Trick Room L29, Foul Play L49 | Double Slap L14→L10, Psybeam L16→L13, Embargo L19→L18, Feint Attack L24→L21, Psyshock L25→L24, Flatter L28→L26, Dark Pulse L39→L38, Charm L46→L40 |
| Gothitelle | Fake Out L1, Torment L1, Trick Room L29, Foul Play L49 | Double Slap L14→L10, Psybeam L16→L13, Embargo L19→L18, Feint Attack L24→L21, Psyshock L25→L24, Flatter L28→L26, Dark Pulse L39→L38, Charm L46→L40 |
| Solosis | Psybeam L11, Counter L43 | Snatch L10→L9, Wonder Room L48→L31 |
| Duosion | Psybeam L11, Counter L43 | Wonder Room L48→L31 |
| Reuniclus | Psybeam L11, Counter L43, Hammer Arm L57 | Wonder Room L48→L31 |
| Ducklett | Razor Wind L23, Brine L30, Acrobatics L36, Scald L41 | Hurricane L46→L44 |
| Swanna | Razor Wind L23, Brine L30, Acrobatics L36, Scald L41 | Hurricane L46→L44 |
| Litwick | Lava Plume L33 | Imprison L24→L23, Hex L28→L26, Pain Split L55→L30, Curse L43→L36, Shadow Ball L49→L40, Overheat L61→L52 |
| Lampent | Lava Plume L33 | Imprison L24→L23, Hex L28→L26, Pain Split L55→L30, Curse L43→L36, Shadow Ball L49→L40, Overheat L61→L52 |
| Chandelure | Hypnosis L1, Lava Plume L33 | Minimize L3→L1, Imprison L24→L23, Curse L43→L36, Shadow Ball L49→L40, Overheat L61→L52 |
| Cubchoo | Endure L15, Ice Shard L18, Ice Punch L27, Frost Breath L33, Tickle L51 | Powder Snow L5→L1, Play Nice L15→L1, Bide L9→L4, Icy Wind L13→L8, Fury Swipes L17→L11, Charm L25→L23, Slash L33→L30, Hail L49→L35, Thrash L53→L49, Sheer Cold L57→L56 |
| Beartic | Scary Face L1, Endure L15, Ice Shard L18, Swagger L23, Ice Punch L27, Frost Breath L33, Submission L39, Bulk Up L51 | Fury Swipes L17→L11, Slash L33→L30, Hail L49→L35 |
| Mienfoo | Vacuum Wave L8, Me First L31, Bounce L47, Focus Blast L54 | Meditate L5→L1, Detect L9→L5, Fake Out L13→L12, Swift L21→L15, Force Palm L29→L20, Quick Guard L45→L23, Drain Punch L33→L29, Jump Kick L38→L35, Aura Sphere L57→L41 |
| Mienshao | Wide Guard L1, Vacuum Wave L1, Me First L31, Bounce L47, Focus Blast L54 | Swift L21→L15, Force Palm L29→L20, Quick Guard L45→L23, Drain Punch L33→L29, Jump Kick L38→L35 |
| Rufflet | Revenge L30, Rock Climb L47, Superpower L51 | Wing Attack L10→L9, Hone Claws L14→L12, Rock Smash L25→L15, Scary Face L19→L17, Aerial Ace L23→L20, Slash L28→L24, Defog L32→L26, Sky Drop L50→L33, Crush Claw L46→L37, Whirlwind L55→L41, Brave Bird L59→L55, Thrash L64→L58 |
| Braviary | Zen Headbutt L1, Revenge L30, Rock Climb L47, Final Gambit L62 | Hone Claws L14→L12, Rock Smash L25→L15, Scary Face L19→L17, Aerial Ace L23→L20, Slash L28→L24, Defog L32→L26, Sky Drop L50→L33, Crush Claw L46→L37 |
| Vullaby | Air Cutter L24, Bounce L33, Dark Pulse L37, Foul Play L47, Bone Rush L51 | Pluck L10→L9, Embargo L52→L12, Bone Club L25→L15, Flatter L19→L17, Feint Attack L23→L20, Defog L32→L26, Whirlwind L55→L41, Brave Bird L59→L55 |
| Mandibuzz | Block L1, Air Cutter L24, Bounce L33, Dark Pulse L37, Foul Play L47, Knock Off L62 | Embargo L52→L12, Bone Club L25→L15, Flatter L19→L17, Feint Attack L23→L20, Defog L32→L26 |
| Chespin | Needle Arm L18, Drain Punch L34 | Leech Seed L15→L14, Mud Shot L24→L23 |
| Quilladin | Take Down L27, Drain Punch L34 | Vine Whip L5→L1, Leech Seed L15→L14, Mud Shot L24→L23 |
| Chesnaught | Spike Cannon L1, Take Down L27, Drain Punch L34 | Vine Whip L5→L1, Rollout L8→L1, Leech Seed L15→L14, Mud Shot L24→L23 |
| Fennekin | Incinerate L26, Hex L45 | Howl L11→L7, Flame Charge L14→L12, Lucky Chant L25→L14, Magic Room L46→L23 |
| Braixen | Incinerate L26, Hex L45 | Ember L5→L1, Howl L11→L7, Flame Charge L14→L12, Lucky Chant L25→L14, Magic Room L46→L23 |
| Delphox | Incinerate L26, Hex L45 | Ember L5→L1, Howl L11→L1, Flame Charge L14→L12, Lucky Chant L25→L14, Magic Room L46→L23 |
| Froakie | Assurance L23, Dive L27, Feint Attack L33, Muddy Water L42 | Smokescreen L18→L17, Round L21→L20 |
| Frogadier | Assurance L23, Dive L27, Feint Attack L33, Muddy Water L42 | Smokescreen L18→L17, Round L21→L20 |
| Greninja | Assurance L23, Dive L27, Muddy Water L42 | Bubble L5→L1, Quick Attack L8→L1, Smokescreen L18→L17, Extrasensory L47→L45 |
| Litleo | Snarl L27, Sunny Day L33 | Noble Roar L15→L14, Fire Fang L23→L17, Echoed Voice L33→L20, Incinerate L46→L23 |
| Skiddo | Grassy Terrain L10, Take Down L19, Agility L34, Zen Headbutt L40, Earthquake L51 | Vine Whip L7→L4, Tail Whip L9→L7, Worry Seed L16→L12, Bulldoze L26→L22, Milk Drink L50→L25, Seed Bomb L30→L28, Horn Leech L42→L37 |
| Gogoat | Rock Climb L1, Grassy Terrain L10, Take Down L19, Agility L34, Zen Headbutt L40 | Leech Seed L12→L1, Vine Whip L7→L1, Tail Whip L9→L1, Worry Seed L16→L12, Bulldoze L26→L22, Milk Drink L50→L25, Seed Bomb L30→L28, Horn Leech L42→L37 |
| Pancham | Bite L17, Dizzy Punch L20, Drain Punch L27, Taunt L30 | Arm Thrust L7→L6, Work Up L10→L9, Comet Punch L15→L14, Circle Throw L25→L24, Sky Uppercut L48→L37 |
| Pangoro | Bite L17, Dizzy Punch L20, Drain Punch L27, Night Slash L32, Sucker Punch L54 | Arm Thrust L7→L1, Work Up L10→L1, Comet Punch L15→L14, Circle Throw L25→L24, Taunt L53→L30, Sky Uppercut L48→L37 |
| Honedge | Sharpen L1, Metal Claw L20, Shadow Claw L32 | Metal Sound L8→L7, Shadow Sneak L20→L11, Autotomize L18→L17, Slash L29→L26, Iron Defense L32→L29 |
| Doublade | Sharpen L1, Metal Claw L20, Shadow Claw L32 | Fury Cutter L5→L1, Metal Sound L8→L7, Shadow Sneak L20→L11, Autotomize L18→L17, Slash L29→L26, Iron Defense L32→L29 |
| Skrelp | Twister L15, Dragon Tail L29, Gunk Shot L50 | Bubble L12→L1, Tail Whip L9→L5, Acid L15→L8, Camouflage L19→L17, Water Pulse L25→L21, Double Team L28→L26, Aqua Tail L35→L34, Dragon Pulse L46→L41 |
| Dragalge | Foul Play L1, Gunk Shot L50, Outrage L54, Sludge Wave L63 | Bubble L12→L1, Tail Whip L9→L1, Acid L15→L8, Camouflage L19→L17, Water Pulse L25→L21, Double Team L28→L26, Aqua Tail L35→L34, Dragon Pulse L46→L41 |
| Clauncher | Hone Claws L10, Vacuum Wave L22, Aura Sphere L32, Dragon Pulse L39, Agility L42, Dark Pulse L45 | Water Sport L7→L4, Vice Grip L9→L7, Aqua Jet L43→L12, Flail L16→L15, Bubble Beam L20→L17, Smack Down L39→L20, Water Pulse L32→L28 |
| Clawitzer | Hone Claws L10, Vacuum Wave L22, Agility L42, Muddy Water L49, Hyper Beam L55 | Aqua Jet L43→L12, Flail L16→L15, Bubble Beam L20→L17, Smack Down L39→L20, Water Pulse L32→L28 |
| Helioptile | Electric Terrain L16, Swift L22, Mud Bomb L33, Eerie Impulse L40 | Charge L11→L4, Mud-Slap L13→L9, Quick Attack L17→L13, Parabolic Charge L25→L20, Thunder Wave L31→L25, Electrify L43→L28, Volt Switch L36→L31, Hyper Voice L50→L38, Thunderbolt L46→L43 |
| Heliolisk | Electric Terrain L16, Swift L22, Mud Bomb L33, Sunny Day L47, Rain Dance L47, Weather Ball L52 | Thunder Shock L6→L1, Mud-Slap L13→L9, Thunder Wave L31→L25, Volt Switch L36→L31, Hyper Voice L50→L38, Thunderbolt L46→L43 |
| Tyrunt | Slam L10, Rock Throw L13, Charm L15, Fire Fang L28, Thunder Fang L28, Rock Slide L31, Hyper Fang L41 | Roar L6→L5, Stomp L10→L8, Ancient Power L26→L21, Dragon Tail L30→L24, Ice Fang L35→L28 |
| Tyrantrum | Dragon Rush L1, Slam L10, Rock Throw L13, Charm L15, Fire Fang L28, Thunder Fang L28, Hyper Fang L41, Outrage L55, Giga Impact L63 | Roar L6→L1, Stomp L10→L1, Ancient Power L26→L21, Dragon Tail L30→L24, Ice Fang L35→L28 |
| Amaura | Power Gem L36, Moonlight L45, Hyper Beam L55 | Mist L18→L3, Rock Throw L10→L6, Icy Wind L13→L9, Round L27→L16, Aurora Beam L20→L19, Ancient Power L23→L22, Hail L34→L27, Encore L40→L32, Ice Beam L46→L39, Blizzard L53→L50 |
| Aurorus | Wide Guard L1, Power Gem L36, Tri Attack L41, Moonlight L45, Hyper Beam L55, Stone Edge L60 | Mist L18→L1, Rock Throw L10→L1, Icy Wind L13→L9, Round L27→L16, Aurora Beam L20→L19, Ancient Power L23→L22, Hail L34→L27, Encore L40→L32, Ice Beam L46→L39, Blizzard L53→L50 |
| Sylveon | Lucky Chant L1, Jump Kick L1, Confide L1, Double Kick L14, Bite L17, Wrap L25, Amnesia L32, Dazzling Gleam L37, Encore L48, Hyper Voice L52 | Sand Attack L5→L4, Quick Attack L13→L6, Swift L17→L12, Misty Terrain L29→L22 |
| Hawlucha | Submission L1, Endeavor L14, Rolling Kick L17, Endure L24 | Encore L20→L1, Wing Attack L8→L1, Aerial Ace L16→L11, Sky Drop L55→L20, Bounce L32→L31, Feather Dance L40→L34, High Jump Kick L44→L42, Swords Dance L60→L55 |
| Dedenne | Draining Kiss L14, Electric Terrain L25, Recycle L38 | Thunder Wave L23→L1, Thunder Shock L7→L5, Charge L11→L8, Charm L14→L11, Nuzzle L21→L16, Entrainment L39→L19, Snore L31→L30, Dazzling Gleam L36→L33, Discharge L50→L41 |
| Goomy | Slam L10, Acid Spray L16, Bubble Beam L18, Acid Armor L32, Recover L52, Outrage L60 | Absorb L5→L4, Bide L13→L6, Dragon Pulse L42→L36 |
| Sliggoo | Slam L10, Bubble Beam L18, Acid Armor L32, Recover L52 | Bide L13→L6, Dragon Pulse L42→L36 |
| Goodra | Slam L10, Bubble Beam L18, Acid Armor L32, Recover L52 | Bide L13→L1, Dragon Pulse L42→L36 |
| Zygarde | Fissure L1, Camouflage L5, Dragon Tail L25, Extreme Speed L50, Pain Split L70 | Safeguard L5→L1, Bind L18→L15, Haze L42→L30, Crunch L45→L35, Dragon Pulse L55→L45 |
| Clamperl |  | Shell Smash L50→L40 |
| Magnezone |  | Spark L19→L17, Screech L39→L19, Electro Ball L29→L22, Magnet Rise L53→L28, Discharge L43→L37, Gyro Ball L59→L45 |

</details>

Engine learnset caps may stop adds short of this list (never overflow); Legacy learnset adds never remove a move.

### Planned: evolution changes (12)

- Poliwag → Poliwhirl: level 25 → 18 (yellow)
- Spinarak → Ariados: level 22 → 21 (crystal)
- Ralts → Kirlia: level 20 → 16 (emerald)
- Vibrava → Flygon: level 45 → 42 (emerald)
- Swablu → Altaria: level 35 → 30 (xy)
- Stunky → Skuntank: level 34 → 28 (xy)
- Sandile → Krokorok: level 29 → 27 (xy)
- Ducklett → Swanna: level 31 → 30 (xy)
- Haunter → Gengar: **added** method level (42) (yellow)
- Eevee → Glaceon: **added** method item (Dawn Stone) (xy)
- Murkrow → Honchkrow: **added** method move (Beat Up) (xy)
- Gurdurr → Conkeldurr: **added** method level (40) (xy)

Skipped (engine lacks it): Poliwhirl -> Politoed: item King's Rock not found in this engine; Onix -> Steelix: item Metal Coat not found in this engine; Scyther -> Scizor: item Metal Coat not found in this engine; Clamperl -> Huntail: item Deepseatooth not found in this engine; Clamperl -> Gorebyss: item Deepseascale not found in this engine; Dusclops -> Dusknoir: engine has no "held_night" method (no probe species uses it); Lampent -> Chandelure: engine has no "level_night" method (no probe species uses it)
