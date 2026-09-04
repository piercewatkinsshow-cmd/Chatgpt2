from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "hack")
base = Path(__file__).with_name("patch_battlehub_clean_freeorder.py")

subprocess.run([sys.executable, str(base), str(root)], check=True)

# ---------------------------------------------------------------------------
# LARGE, WALLED, LOW-SPRITE-DENSITY HUB
# ---------------------------------------------------------------------------
# Enlarge Indigo Plateau Lobby from 8x6 blocks (16x12 movement cells) to
# 16x12 blocks (32x24 movement cells). This gives enough physical separation
# that only a few opponent sprites can occupy the viewport at once.
constants = root / "constants/map_constants.asm"
s = constants.read_text()
old_const = "\tmapconst INDIGO_PLATEAU_LOBBY,           6,  8 ; $AE"
new_const = "\tmapconst INDIGO_PLATEAU_LOBBY,          12, 16 ; $AE"
if old_const not in s:
    raise SystemExit("Indigo Plateau Lobby mapconst not found")
constants.write_text(s.replace(old_const, new_const, 1))

# Block 0 = plain walkable floor ($11).
# Block 1 = solid/non-walkable boundary ($00, not in MART walkable tiles).
blockset = root / "gfx/blocksets/pokecenter.bst"
b = bytearray(blockset.read_bytes())
if len(b) < 32:
    raise SystemExit("pokecenter blockset unexpectedly short")
b[0:16] = bytes([0x11] * 16)
b[16:32] = bytes([0x00] * 16)
blockset.write_bytes(b)

# 16x12 block room, with a one-block-thick solid wall ring.
mapfile = root / "maps/IndigoPlateauLobby.blk"
old = mapfile.read_bytes()
if len(old) != 48:
    raise SystemExit(f"Expected original 48-byte Indigo Plateau map, got {len(old)}")
rows = []
for y in range(12):
    for x in range(16):
        rows.append(0x01 if x in (0, 15) or y in (0, 11) else 0x00)
mapfile.write_bytes(bytes(rows))

# Spawn near the healer/PC service area, well inside the solid boundary.
special = root / "data/maps/special_warps.asm"
s = special.read_text()
old_spec = "FirstMapSpec:\n\tspecial_warp_spec INDIGO_PLATEAU_LOBBY, 7, 9, MART"
new_spec = "FirstMapSpec:\n\tspecial_warp_spec INDIGO_PLATEAU_LOBBY, 10, 20, MART"
if old_spec not in s:
    raise SystemExit("Battle Hub FirstMapSpec not found")
special.write_text(s.replace(old_spec, new_spec, 1))

# Trainers are separated by 8 movement cells horizontally and 6 vertically.
# With the Game Boy viewport, this keeps roughly four or fewer opponent sprites
# visible at once instead of presenting the whole roster in one screen.
#
# The PC is now a VISIBLE Poke Ball object directly beside the nurse. It uses
# text pointer 15, which already invokes script_pokecenter_pc.
objects = '''IndigoPlateauLobby_Object:
\tdb $1 ; solid border block

\tdef_warps

\tdef_signs

\tdef_objects
\t; Zone 1
\tobject SPRITE_SUPER_NERD,       4,  4, STAY, DOWN,  1, OPP_BROCK, 1
\tobject SPRITE_BRUNETTE_GIRL,   12,  4, STAY, DOWN,  2, OPP_MISTY, 1
\tobject SPRITE_COOLTRAINER_M,    20,  4, STAY, DOWN,  3, OPP_LT_SURGE, 1
\tobject SPRITE_BRUNETTE_GIRL,   28,  4, STAY, DOWN,  4, OPP_ERIKA, 1

\t; Zone 2
\tobject SPRITE_SUPER_NERD,       4, 10, STAY, DOWN,  5, OPP_KOGA, 1
\tobject SPRITE_BRUNETTE_GIRL,   12, 10, STAY, DOWN,  6, OPP_SABRINA, 1
\tobject SPRITE_SUPER_NERD,      20, 10, STAY, DOWN,  7, OPP_BLAINE, 1
\tobject SPRITE_COOLTRAINER_M,   28, 10, STAY, DOWN,  8, OPP_GIOVANNI, 3

\t; Zone 3
\tobject SPRITE_COOLTRAINER_F,    4, 16, STAY, DOWN,  9, OPP_LORELEI, 1
\tobject SPRITE_COOLTRAINER_M,   12, 16, STAY, DOWN, 10, OPP_BRUNO, 1
\tobject SPRITE_COOLTRAINER_F,   20, 16, STAY, DOWN, 11, OPP_AGATHA, 1
\tobject SPRITE_COOLTRAINER_M,   28, 16, STAY, DOWN, 12, OPP_LANCE, 1

\t; Champion and services near the bottom center.
\tobject SPRITE_BLUE,            20, 20, STAY, DOWN, 13, OPP_RIVAL3, 1
\tobject SPRITE_NURSE,            6, 20, STAY, RIGHT, 14
\tobject SPRITE_POKE_BALL,        8, 20, STAY, NONE, 15

\tdef_warps_to INDIGO_PLATEAU_LOBBY
'''
(root / "data/maps/objects/IndigoPlateauLobby.asm").write_text(objects)

print("Applied large low-sprite-density Battle Hub")
print("Map size: 32x24 movement cells with solid wall ring")
print("Trainer spacing: 8 cells horizontal / 6 vertical")
print("Visible PC object: Poke Ball at (8,20), nurse at (6,20)")
print("Player spawn: (10,20)")
print("All 13 opponents remain free-order")
