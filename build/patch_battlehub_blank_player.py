from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "hack")
base = Path(__file__).with_name("patch_battlehub_clean_freeorder.py")

subprocess.run([sys.executable, str(base), str(root)], check=True)

# ---------------------------------------------------------------------------
# SIMPLE SAFE ROOM
# ---------------------------------------------------------------------------
# Block 0 = plain walkable floor ($11).
# Block 1 = solid/non-walkable boundary ($00, not in the MART walkable list).
# The 8x6 block map gets a one-block-thick wall around the outside, leaving a
# 6x4-block (12x8 movement-cell) playable floor in the center.
blockset = root / "gfx/blocksets/pokecenter.bst"
b = bytearray(blockset.read_bytes())
if len(b) < 32:
    raise SystemExit("pokecenter blockset unexpectedly short")
b[0:16] = bytes([0x11] * 16)   # floor
b[16:32] = bytes([0x00] * 16)  # solid boundary
blockset.write_bytes(b)

mapfile = root / "maps/IndigoPlateauLobby.blk"
old = mapfile.read_bytes()
if len(old) != 48:
    raise SystemExit(f"Expected 48-byte Indigo Plateau map, got {len(old)}")

rows = []
for y in range(6):
    row = []
    for x in range(8):
        row.append(0x01 if x in (0, 7) or y in (0, 5) else 0x00)
    rows.extend(row)
mapfile.write_bytes(bytes(rows))

# Spawn safely inside the walled floor, away from all objects.
special = root / "data/maps/special_warps.asm"
s = special.read_text()
old_spec = "FirstMapSpec:\n\tspecial_warp_spec INDIGO_PLATEAU_LOBBY, 7, 9, MART"
new_spec = "FirstMapSpec:\n\tspecial_warp_spec INDIGO_PLATEAU_LOBBY, 7, 9, MART"
if old_spec not in s:
    raise SystemExit("Battle Hub FirstMapSpec not found")
# Keep the same known-good spawn coordinate; the important fix is the solid
# room boundary and an object-free spawn tile.
special.write_text(s.replace(old_spec, new_spec, 1))

objects = '''IndigoPlateauLobby_Object:
\tdb $1 ; solid border block

\tdef_warps

\tdef_signs
\t; PC is immediately beside the healer, at the lower-right of the safe room.
\tsign 12, 9, 15 ; PC access point

\tdef_objects
\t; All opponents are on the central walkable floor and can be challenged in
\t; any order. Outer movement cells are blocked by the wall ring.
\tobject SPRITE_SUPER_NERD,       2, 2, STAY, DOWN,  1, OPP_BROCK, 1
\tobject SPRITE_BRUNETTE_GIRL,    4, 2, STAY, DOWN,  2, OPP_MISTY, 1
\tobject SPRITE_COOLTRAINER_M,     6, 2, STAY, DOWN,  3, OPP_LT_SURGE, 1
\tobject SPRITE_BRUNETTE_GIRL,    8, 2, STAY, DOWN,  4, OPP_ERIKA, 1
\tobject SPRITE_SUPER_NERD,      10, 2, STAY, DOWN,  5, OPP_KOGA, 1
\tobject SPRITE_BRUNETTE_GIRL,   12, 2, STAY, DOWN,  6, OPP_SABRINA, 1

\tobject SPRITE_SUPER_NERD,       2, 5, STAY, DOWN,  7, OPP_BLAINE, 1
\tobject SPRITE_COOLTRAINER_M,     4, 5, STAY, DOWN,  8, OPP_GIOVANNI, 3
\tobject SPRITE_COOLTRAINER_F,     6, 5, STAY, DOWN,  9, OPP_LORELEI, 1
\tobject SPRITE_COOLTRAINER_M,     8, 5, STAY, DOWN, 10, OPP_BRUNO, 1
\tobject SPRITE_COOLTRAINER_F,    10, 5, STAY, DOWN, 11, OPP_AGATHA, 1
\tobject SPRITE_COOLTRAINER_M,    12, 5, STAY, DOWN, 12, OPP_LANCE, 1

\tobject SPRITE_BLUE,              4, 8, STAY, DOWN, 13, OPP_RIVAL3, 1
\tobject SPRITE_NURSE,            11, 9, STAY, RIGHT, 14

\tdef_warps_to INDIGO_PLATEAU_LOBBY
'''
(root / "data/maps/objects/IndigoPlateauLobby.asm").write_text(objects)

print("Applied safe walled Battle Hub")
print("Solid boundary prevents walking outside the room")
print("PC moved beside healer at (12,9); nurse at (11,9)")
print("All 13 opponents remain free-order")
