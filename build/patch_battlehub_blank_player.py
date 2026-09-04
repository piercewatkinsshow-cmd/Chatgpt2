from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "hack")
base = Path(__file__).with_name("patch_battlehub_clean_freeorder.py")

# Start from the proven original-151, free-order Battle Hub.
subprocess.run([sys.executable, str(base), str(root)], check=True)

# ---------------------------------------------------------------------------
# BLANK, FULLY WALKABLE ROOM
# ---------------------------------------------------------------------------
# The Indigo Plateau Lobby is 8x6 map blocks. MART and POKECENTER share the
# same blockset. Replace block 0 with sixteen copies of tile $11, which is a
# permitted MART collision tile and is the plain floor tile used throughout
# the original center/lobby graphics. Then make every map block block 0.
# Result: a 16x12 movement-cell room made entirely of plain walkable floor.
blockset = root / "gfx/blocksets/pokecenter.bst"
b = bytearray(blockset.read_bytes())
if len(b) < 16:
    raise SystemExit("pokecenter blockset unexpectedly short")
b[0:16] = bytes([0x11] * 16)
blockset.write_bytes(b)

mapfile = root / "maps/IndigoPlateauLobby.blk"
old = mapfile.read_bytes()
if len(old) != 48:
    raise SystemExit(f"Expected 48-byte Indigo Plateau map, got {len(old)}")
mapfile.write_bytes(bytes([0x00] * 48))

# Move the NEW GAME spawn onto a dedicated clear floor cell near the bottom
# center. This replaces the original Battle Hub spawn (7,9).
special = root / "data/maps/special_warps.asm"
s = special.read_text()
old_spec = "FirstMapSpec:\n\tspecial_warp_spec INDIGO_PLATEAU_LOBBY, 7, 9, MART"
new_spec = "FirstMapSpec:\n\tspecial_warp_spec INDIGO_PLATEAU_LOBBY, 7, 10, MART"
if old_spec not in s:
    raise SystemExit("Battle Hub FirstMapSpec not found")
special.write_text(s.replace(old_spec, new_spec, 1))

# Rebuild the object layout for the blank room. Every coordinate is now known
# to be on the same fully walkable floor. The player's spawn at (7,10) is kept
# clear, with no NPC adjacent below it and no object occupying that coordinate.
(root / "data/maps/objects/IndigoPlateauLobby.asm").write_text(r'''IndigoPlateauLobby_Object:
\tdb $0 ; border block

\tdef_warps

\tdef_signs
\tsign 15, 10, 15 ; PC access point (background text event)

\tdef_objects
\t; Gym Leaders -- top two rows.
\tobject SPRITE_SUPER_NERD,       2, 2, STAY, DOWN,  1, OPP_BROCK, 1
\tobject SPRITE_BRUNETTE_GIRL,    5, 2, STAY, DOWN,  2, OPP_MISTY, 1
\tobject SPRITE_COOLTRAINER_M,     8, 2, STAY, DOWN,  3, OPP_LT_SURGE, 1
\tobject SPRITE_BRUNETTE_GIRL,   11, 2, STAY, DOWN,  4, OPP_ERIKA, 1
\tobject SPRITE_SUPER_NERD,      14, 2, STAY, DOWN,  5, OPP_KOGA, 1
\n\tobject SPRITE_BRUNETTE_GIRL,    2, 5, STAY, DOWN,  6, OPP_SABRINA, 1
\tobject SPRITE_SUPER_NERD,       5, 5, STAY, DOWN,  7, OPP_BLAINE, 1
\tobject SPRITE_COOLTRAINER_M,     8, 5, STAY, DOWN,  8, OPP_GIOVANNI, 3

\t; Elite Four + Champion -- lower opponent row.
\tobject SPRITE_COOLTRAINER_F,     2, 8, STAY, DOWN,  9, OPP_LORELEI, 1
\tobject SPRITE_COOLTRAINER_M,     5, 8, STAY, DOWN, 10, OPP_BRUNO, 1
\tobject SPRITE_COOLTRAINER_F,     8, 8, STAY, DOWN, 11, OPP_AGATHA, 1
\tobject SPRITE_COOLTRAINER_M,    11, 8, STAY, DOWN, 12, OPP_LANCE, 1
\tobject SPRITE_BLUE,             14, 8, STAY, DOWN, 13, OPP_RIVAL3, 1

\t; Healer. Player begins at (7,10), safely away from all object positions.
\tobject SPRITE_NURSE,            12,10, STAY, LEFT, 14

\tdef_warps_to INDIGO_PLATEAU_LOBBY
''')

print("Applied blank-floor Battle Hub")
print("Player start: (7,10), dedicated clear tile")
print("All 13 opponents remain free-order")
