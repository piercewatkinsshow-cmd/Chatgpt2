from pathlib import Path
import shutil
import sys

root = Path(sys.argv[1]).resolve()
here = Path(__file__).resolve().parent


def replace_once(relpath: str, old: str, new: str) -> None:
    path = root / relpath
    text = path.read_text()
    if old not in text:
        raise RuntimeError(f"Could not find patch target in {relpath}: {old!r}")
    path.write_text(text.replace(old, new, 1))


# Replace the Indigo Plateau lobby with the single-room Battle Hub.
shutil.copyfile(here / "patches" / "IndigoPlateauLobby.script.asm", root / "scripts" / "IndigoPlateauLobby.asm")
shutil.copyfile(here / "patches" / "IndigoPlateauLobby.objects.asm", root / "data" / "maps" / "objects" / "IndigoPlateauLobby.asm")

# Start a New Game directly in the hub.
replace_once(
    "data/maps/special_warps.asm",
    "special_warp_spec REDS_HOUSE_2F, 3, 6, REDS_HOUSE_2",
    "special_warp_spec INDIGO_PLATEAU_LOBBY, 7, 10, MART",
)
replace_once(
    "engine/overworld/special_warps.asm",
    "\tld a, PALLET_TOWN\n.next",
    "\tld a, INDIGO_PLATEAU\n.next",
)

# Make any player-added Pokemon have perfect Gen I DVs: FF/FF.
replace_once(
    "engine/pokemon/add_mon.asm",
    "; Not wild.\n\tcall Random ; generate random IVs\n\tld b, a\n\tcall Random",
    "; Battle Hub: gifted/player-added Pokemon have perfect DVs.\n\tld a, $ff\n\tld b, a",
)

# Keep blackouts in the Battle Hub and heal the party instead of warping away.
replace_once(
    "engine/events/black_out.asm",
    ".lostmoney\n\tld hl, wStatusFlags6",
    ".lostmoney\n\tld a, [wCurMap]\n\tcp INDIGO_PLATEAU_LOBBY\n\tjr nz, .normalWarp\n\tld a, PAD_BUTTONS | PAD_CTRL_PAD\n\tld [wJoyIgnore], a\n\tpredef_jump HealParty\n.normalWarp\n\tld hl, wStatusFlags6",
)

# Fill the starting Bag and item-storage PC immediately after player data is initialized.
replace_once(
    "engine/movie/oak_speech/init_player_data.asm",
    "\tld hl, wNumBoxItems\n\tcall InitializeEmptyList\n\nDEF START_MONEY EQU $3000",
    "\tld hl, wNumBoxItems\n\tcall InitializeEmptyList\n\n\tld hl, BattleHubBagItems\n\tld de, wNumBagItems\n\tld bc, BattleHubBagItemsEnd - BattleHubBagItems\n\tcall CopyData\n\tld hl, BattleHubPCItems\n\tld de, wNumBoxItems\n\tld bc, BattleHubPCItemsEnd - BattleHubPCItems\n\tcall CopyData\n\nDEF START_MONEY EQU $3000",
)

inventory_data = r'''

; Battle Hub starting Bag. Gen I permits at most 20 unique Bag slots.
BattleHubBagItems:
	db 11
	db HP_UP, 10
	db PROTEIN, 10
	db IRON, 10
	db CARBOS, 10
	db CALCIUM, 10
	db RARE_CANDY, 13
	db HM_CUT, 1
	db HM_FLY, 1
	db HM_SURF, 1
	db HM_STRENGTH, 1
	db HM_FLASH, 1
	db $ff
BattleHubBagItemsEnd:

; All non-Gym-Leader TMs. The 8 reward TMs fill the remaining PC slots.
BattleHubPCItems:
	db 42
	db TM_MEGA_PUNCH, 1
	db TM_RAZOR_WIND, 1
	db TM_SWORDS_DANCE, 1
	db TM_WHIRLWIND, 1
	db TM_MEGA_KICK, 1
	db TM_HORN_DRILL, 1
	db TM_BODY_SLAM, 1
	db TM_TAKE_DOWN, 1
	db TM_DOUBLE_EDGE, 1
	db TM_WATER_GUN, 1
	db TM_ICE_BEAM, 1
	db TM_BLIZZARD, 1
	db TM_HYPER_BEAM, 1
	db TM_PAY_DAY, 1
	db TM_SUBMISSION, 1
	db TM_COUNTER, 1
	db TM_SEISMIC_TOSS, 1
	db TM_RAGE, 1
	db TM_SOLARBEAM, 1
	db TM_DRAGON_RAGE, 1
	db TM_THUNDER, 1
	db TM_EARTHQUAKE, 1
	db TM_DIG, 1
	db TM_PSYCHIC_M, 1
	db TM_TELEPORT, 1
	db TM_MIMIC, 1
	db TM_DOUBLE_TEAM, 1
	db TM_REFLECT, 1
	db TM_METRONOME, 1
	db TM_SELFDESTRUCT, 1
	db TM_EGG_BOMB, 1
	db TM_SWIFT, 1
	db TM_SKULL_BASH, 1
	db TM_SOFTBOILED, 1
	db TM_DREAM_EATER, 1
	db TM_SKY_ATTACK, 1
	db TM_REST, 1
	db TM_THUNDER_WAVE, 1
	db TM_EXPLOSION, 1
	db TM_ROCK_SLIDE, 1
	db TM_TRI_ATTACK, 1
	db TM_SUBSTITUTE, 1
	db $ff
BattleHubPCItemsEnd:
'''

init_path = root / "engine" / "movie" / "oak_speech" / "init_player_data.asm"
text = init_path.read_text()
marker = "InitializeEmptyList:\n\txor a ; count\n\tld [hli], a\n\tdec a ; terminator\n\tld [hl], a\n\tret\n"
if marker not in text:
    raise RuntimeError("Could not find inventory-data insertion point")
init_path.write_text(text.replace(marker, marker + inventory_data, 1))

print("Battle Hub source patches applied successfully.")
