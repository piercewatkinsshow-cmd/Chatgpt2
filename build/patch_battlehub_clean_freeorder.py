from pathlib import Path
import subprocess
import sys
import re

root = Path(sys.argv[1] if len(sys.argv) > 1 else "hack")
base_patcher = Path(__file__).with_name("patch_battlehub.py")

# Apply the proven original-151 Battle Hub patch first (starter selector,
# inventory, trainer parties, badge/TM rewards, healer/PC, etc.).
subprocess.run([sys.executable, str(base_patcher), str(root)], check=True)

# ---------------------------------------------------------------------------
# CLEAN LAYOUT
# ---------------------------------------------------------------------------
# Indigo Plateau Lobby is an 8x6 block MART-tileset map, producing a 16x12
# movement-cell grid. These positions were chosen only from cells whose
# collision tile is $11 (plain walkable floor) and from the connected component
# containing the player's start position.
#
# Trainers are arranged in two spaced rows with a clear aisle between them.
# Every trainer can be approached from an adjacent plain-floor tile.
(root / "data/maps/objects/IndigoPlateauLobby.asm").write_text(r'''IndigoPlateauLobby_Object:
	db $0 ; border block

	def_warps

	def_signs
	sign 13, 5, 15 ; Pokemon Center PC

	def_objects
	; Upper trainer row -- all confirmed plain floor ($11 collision tile).
	object SPRITE_SUPER_NERD,       4, 7, STAY, DOWN,  1, OPP_BROCK, 1
	object SPRITE_BRUNETTE_GIRL,    6, 7, STAY, DOWN,  2, OPP_MISTY, 1
	object SPRITE_COOLTRAINER_M,     8, 7, STAY, DOWN,  3, OPP_LT_SURGE, 1
	object SPRITE_BRUNETTE_GIRL,   10, 7, STAY, DOWN,  4, OPP_ERIKA, 1
	object SPRITE_SUPER_NERD,       12, 7, STAY, DOWN,  5, OPP_KOGA, 1
	object SPRITE_BRUNETTE_GIRL,   14, 7, STAY, DOWN,  6, OPP_SABRINA, 1

	; Lower trainer row -- separated by a fully open aisle at y=8.
	object SPRITE_SUPER_NERD,        4, 9, STAY, DOWN,  7, OPP_BLAINE, 1
	object SPRITE_COOLTRAINER_M,     6, 9, STAY, DOWN,  8, OPP_GIOVANNI, 3
	object SPRITE_COOLTRAINER_F,     8, 9, STAY, DOWN,  9, OPP_LORELEI, 1
	object SPRITE_COOLTRAINER_M,    10, 9, STAY, DOWN, 10, OPP_BRUNO, 1
	object SPRITE_COOLTRAINER_F,    12, 9, STAY, DOWN, 11, OPP_AGATHA, 1
	object SPRITE_COOLTRAINER_M,    14, 9, STAY, DOWN, 12, OPP_LANCE, 1

	; Champion has open floor above and on both sides.
	object SPRITE_BLUE,              9,11, STAY, DOWN, 13, OPP_RIVAL3, 1

	; Healer is on the confirmed open right-side floor near the existing PC.
	object SPRITE_NURSE,            15, 5, STAY, LEFT, 14

	def_warps_to INDIGO_PLATEAU_LOBBY
''')

# ---------------------------------------------------------------------------
# FREE-ORDER BATTLES
# ---------------------------------------------------------------------------
# The original patch used a prior-trainer event check for every trainer after
# Brock. Remove those checks while preserving each trainer's own persistent
# defeated event flag in the trainer header. This means any Gym Leader, Elite
# Four member, or Champion can be challenged first.
p = root / "scripts/IndigoPlateauLobby.asm"
s = p.read_text()
pattern = re.compile(
    r"\tCheckEvent [^\n]+\n"
    r"\tjr z, \.locked\n"
    r"(\tld hl, BattleHubTrainerHeader\d+\n"
    r"\tcall TalkToTrainer\n"
    r"\tjp TextScriptEnd)\n"
    r"\.locked\n"
    r"\tld hl, BattleHubLockedText\n"
    r"\tcall PrintText\n"
    r"\tjp TextScriptEnd"
)
s, count = pattern.subn(r"\1", s)
if count != 12:
    raise SystemExit(f"Expected to remove 12 progression gates; removed {count}")

# Remove obsolete locked-dialogue text so the source accurately reflects the
# new rules. It is no longer referenced anywhere.
s = re.sub(
    r"\nBattleHubLockedText:\n"
    r"\ttext \"Beat the previous\"\n"
    r"\tline \"trainer first!\"\n"
    r"\tdone\n",
    "\n",
    s,
    count=1,
)
p.write_text(s)

print("Applied clean original-151 Battle Hub layout")
print("Removed progression gates:", count)
print("All 13 opponents are independently challengeable")
