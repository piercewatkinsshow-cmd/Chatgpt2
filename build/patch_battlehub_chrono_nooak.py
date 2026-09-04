from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "hack")
base = Path(__file__).with_name("patch_battlehub_clean_freeorder.py")
subprocess.run([sys.executable, str(base), str(root)], check=True)

# ---------------------------------------------------------------------------
# LONG CHRONOLOGICAL HUB
# ---------------------------------------------------------------------------
# Make the Indigo Plateau Lobby a narrow, long room: 8 blocks wide by
# 36 blocks tall = 16 x 72 movement cells.  Trainers are placed from top to
# bottom in the exact badge/E4 order, five cells apart, which keeps only a
# small handful of sprites within a Game Boy viewport at any time.
constants = root / "constants/map_constants.asm"
s = constants.read_text()
old_const = "\tmapconst INDIGO_PLATEAU_LOBBY,           6,  8 ; $AE"
new_const = "\tmapconst INDIGO_PLATEAU_LOBBY,          36,  8 ; $AE"
if old_const not in s:
    raise SystemExit("Indigo Plateau Lobby mapconst not found")
constants.write_text(s.replace(old_const, new_const, 1))

# Block 0 = walkable floor ($11), block 1 = solid wall ($00).
blockset = root / "gfx/blocksets/pokecenter.bst"
b = bytearray(blockset.read_bytes())
if len(b) < 32:
    raise SystemExit("pokecenter blockset unexpectedly short")
b[0:16] = bytes([0x11] * 16)
b[16:32] = bytes([0x00] * 16)
blockset.write_bytes(b)

# 8 x 36 block map with a one-block solid wall ring.
mapfile = root / "maps/IndigoPlateauLobby.blk"
old = mapfile.read_bytes()
if len(old) != 48:
    raise SystemExit(f"Expected original 48-byte Indigo Plateau map, got {len(old)}")
rows = []
for y in range(36):
    for x in range(8):
        rows.append(0x01 if x in (0, 7) or y in (0, 35) else 0x00)
mapfile.write_bytes(bytes(rows))

# Start beside the service area at the top of the route.
special = root / "data/maps/special_warps.asm"
s = special.read_text()
old_spec = "FirstMapSpec:\n\tspecial_warp_spec INDIGO_PLATEAU_LOBBY, 7, 9, MART"
new_spec = "FirstMapSpec:\n\tspecial_warp_spec INDIGO_PLATEAU_LOBBY, 8, 4, MART"
if old_spec not in s:
    raise SystemExit("Battle Hub FirstMapSpec not found")
special.write_text(s.replace(old_spec, new_spec, 1))

# Visible service area, followed by the complete chronological route.
# Text IDs still map to the existing Battle Hub scripts; all battles remain
# free-order mechanically even though their physical layout is chronological.
objects = '''IndigoPlateauLobby_Object:
\tdb $1 ; solid border block

\tdef_warps

\tdef_signs

\tdef_objects
\t; Services at the entrance. The Poke Ball is the visible PC.
\tobject SPRITE_NURSE,             5,  4, STAY, RIGHT, 14
\tobject SPRITE_POKE_BALL,         7,  4, STAY, NONE,  15

\t; Gym Leaders in badge order.
\tobject SPRITE_SUPER_NERD,        5,  9, STAY, DOWN,   1, OPP_BROCK, 1
\tobject SPRITE_BRUNETTE_GIRL,    10, 14, STAY, DOWN,   2, OPP_MISTY, 1
\tobject SPRITE_COOLTRAINER_M,     5, 19, STAY, DOWN,   3, OPP_LT_SURGE, 1
\tobject SPRITE_BRUNETTE_GIRL,    10, 24, STAY, DOWN,   4, OPP_ERIKA, 1
\tobject SPRITE_SUPER_NERD,        5, 29, STAY, DOWN,   5, OPP_KOGA, 1
\tobject SPRITE_BRUNETTE_GIRL,    10, 34, STAY, DOWN,   6, OPP_SABRINA, 1
\tobject SPRITE_SUPER_NERD,        5, 39, STAY, DOWN,   7, OPP_BLAINE, 1
\tobject SPRITE_COOLTRAINER_M,    10, 44, STAY, DOWN,   8, OPP_GIOVANNI, 3

\t; Elite Four, then Champion.
\tobject SPRITE_COOLTRAINER_F,     5, 49, STAY, DOWN,   9, OPP_LORELEI, 1
\tobject SPRITE_COOLTRAINER_M,    10, 54, STAY, DOWN,  10, OPP_BRUNO, 1
\tobject SPRITE_COOLTRAINER_F,     5, 59, STAY, DOWN,  11, OPP_AGATHA, 1
\tobject SPRITE_COOLTRAINER_M,    10, 64, STAY, DOWN,  12, OPP_LANCE, 1
\tobject SPRITE_BLUE,              7, 68, STAY, DOWN,  13, OPP_RIVAL3, 1

\tdef_warps_to INDIGO_PLATEAU_LOBBY
'''
(root / "data/maps/objects/IndigoPlateauLobby.asm").write_text(objects)

# ---------------------------------------------------------------------------
# SKIP OAK INTRO; KEEP PLAYER NAME + STARTER NICKNAME
# ---------------------------------------------------------------------------
# StartNewGame was already patched by patch_battlehub.py to open the 151-species
# starter selector and force perfect DVs. Replace OakSpeech itself with a lean
# new-game initializer. It calls ChoosePlayerName directly, never shows Oak or
# asks for a rival name. GivePokemon retains the game's normal nickname prompt.
p = root / "engine/movie/oak_speech/oak_speech.asm"
s = p.read_text()
start = s.find("OakSpeech:\n")
end = s.find("OakSpeechText1:\n")
if start < 0 or end < 0 or end <= start:
    raise SystemExit("Could not locate OakSpeech routine boundaries")
minimal = r'''OakSpeech:
	ld a, SFX_STOP_ALL_MUSIC
	call PlaySound
	call ClearScreen
	call LoadTextBoxTilePatterns
	call SetDefaultNames
	predef InitPlayerData2

	; Requested Battle Hub starting inventory.
	ld hl, BattleHubBagItems
	ld de, wNumBagItems
	ld bc, BattleHubBagItemsEnd - BattleHubBagItems
	call CopyData
	ld hl, BattleHubPCItems
	ld de, wNumBoxItems
	ld bc, BattleHubPCItemsEnd - BattleHubPCItems
	call CopyData

	; Prepare the special first-map warp before the naming screen, as vanilla
	; does during its intro sequence.
	ld a, [wDefaultMap]
	ld [wDestinationMap], a
	call SpecialWarpIn
	xor a
	ldh [hTilesetType], a

	; The only intro interaction: choose the player's name.
	call ChoosePlayerName
	call GBFadeOutToWhite
	call ClearScreen

	; Give the selected level-5 starter. GivePokemon performs the standard
	; "Do you want to give a nickname?" flow.
	ld a, [wCustomStarterInternalID]
	ld b, a
	ld c, 5
	call GivePokemon
	SetEvent EVENT_GOT_STARTER

	call ResetPlayerSpriteData
	ld a, 1
	ld [wUpdateSpritesEnabled], a
	call ClearScreen
	ret

'''
s = s[:start] + minimal + s[end:]
p.write_text(s)

print("Applied chronological low-density Battle Hub")
print("Order: Brock, Misty, Surge, Erika, Koga, Sabrina, Blaine, Giovanni, Lorelei, Bruno, Agatha, Lance, Champion")
print("Oak intro removed; player-name entry retained")
print("Starter nickname prompt retained through GivePokemon")
print("Visible PC is beside the nurse at the entrance")
