from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "hack")
base = Path(__file__).with_name("patch_battlehub_chrono_badges_pc50.py")
subprocess.run([sys.executable, str(base), str(root)], check=True)


def replace(path, old, new, count=1):
    p = root / path
    s = p.read_text()
    if old not in s:
        raise SystemExit(f"Missing expected text in {path}: {old[:100]!r}")
    p.write_text(s.replace(old, new, count))

# Reuse the unused internal species slot $1F for Smeargle.
replace("constants/pokemon_constants.asm",
        "\tconst_skip               ; $1F",
        "\tconst SMEARGLE           ; $1F ; Gen II backport")

# Add Sketch as a real move id immediately before Struggle.
replace("constants/move_constants.asm",
        "\tconst SUBSTITUTE   ; a4\n\nNUM_ATTACKS EQU const_value - 1\n\n\tconst STRUGGLE     ; a5",
        "\tconst SUBSTITUTE   ; a4\n\tconst SKETCH       ; a5 ; Gen II\n\nNUM_ATTACKS EQU const_value - 1\n\n\tconst STRUGGLE     ; a6")

replace("data/moves/moves.asm",
        "\tmove SUBSTITUTE,   SUBSTITUTE_EFFECT,            0, NORMAL,       100, 10\n\tmove STRUGGLE,     RECOIL_EFFECT,               50, NORMAL,       100, 10",
        "\tmove SUBSTITUTE,   SUBSTITUTE_EFFECT,            0, NORMAL,       100, 10\n\tmove SKETCH,       MIMIC_EFFECT,                 0, NORMAL,       100,  1\n\tmove STRUGGLE,     RECOIL_EFFECT,               50, NORMAL,       100, 10")
replace("data/moves/names.asm",
        "\tdb \"SUBSTITUTE@\"\n\tdb \"STRUGGLE@\"",
        "\tdb \"SUBSTITUTE@\"\n\tdb \"SKETCH@\"\n\tdb \"STRUGGLE@\"")
replace("data/moves/animations.asm",
        "\tdw SubstituteAnim\n\tdw StruggleAnim",
        "\tdw SubstituteAnim\n\tdw MimicAnim ; SKETCH\n\tdw StruggleAnim")
replace("data/moves/sfx.asm",
        "\tdb SFX_BATTLE_2C,          $d8, $04 ; SUBSTITUTE\n\tdb SFX_BATTLE_0B,          $00, $80 ; STRUGGLE",
        "\tdb SFX_BATTLE_2C,          $d8, $04 ; SUBSTITUTE\n\tdb SFX_BATTLE_0B,          $00, $80 ; SKETCH\n\tdb SFX_BATTLE_0B,          $00, $80 ; STRUGGLE")

# Add Smeargle graphics as a separate relocatable ROM section.
p = root / "gfx/pics.asm"
s = p.read_text()
s += r'''

SECTION "Smeargle Pics", ROMX
SmearglePicFront:: INCBIN "gfx/pokemon/front/smeargle.pic"
SmearglePicBack::  INCBIN "gfx/pokemon/back/smeargleb.pic"
'''
p.write_text(s)

# Base stats. Gen I has only one Special stat; use Smeargle's Gen II Sp. Atk (20)
# for the closest offensive behavior to its original design.
p = root / "data/pokemon/mew.asm"
s = p.read_text()
s += r'''

SmeargleBaseStats::
	db 0 ; no Gen-I Pokedex number
	db 55, 20, 35, 75, 20
	;  hp atk def spd spc
	db NORMAL, NORMAL
	db 45 ; catch rate
	db 106 ; base exp
	INCBIN "gfx/pokemon/front/smeargle.pic", 0, 1
	dw SmearglePicFront, SmearglePicBack
	db SKETCH, NO_MOVE, NO_MOVE, NO_MOVE
	db GROWTH_MEDIUM_FAST
	; Smeargle learns through Sketch, not TMs/HMs.
	db 0, 0, 0, 0, 0, 0, 0
	db 0
'''
p.write_text(s)

# Special-case base stat lookup for the reused MissingNo slot.
replace("home/pokemon.asm",
        "\tcp MEW\n\tjr z, .mew\n\tpredef IndexToPokedex",
        "\tcp SMEARGLE\n\tjr z, .smeargle\n\tcp MEW\n\tjr z, .mew\n\tpredef IndexToPokedex")
replace("home/pokemon.asm",
        ".mew\n\tld hl, MewBaseStats\n\tld de, wMonHeader\n\tld bc, MonBaseStatsEnd - MonBaseStats\n\tld a, BANK(MewBaseStats)\n\tcall FarCopyData\n.done",
        ".smeargle\n\tld hl, SmeargleBaseStats\n\tld de, wMonHeader\n\tld bc, MonBaseStatsEnd - MonBaseStats\n\tld a, BANK(SmeargleBaseStats)\n\tcall FarCopyData\n\tjr .done\n.mew\n\tld hl, MewBaseStats\n\tld de, wMonHeader\n\tld bc, MonBaseStatsEnd - MonBaseStats\n\tld a, BANK(MewBaseStats)\n\tcall FarCopyData\n.done")
replace("home/pokemon.asm",
        "\tld a, [wcf91]\n\tld [wd11e], a\n\tpredef IndexToPokedex\n\tld hl, wd11e",
        "\tld a, [wcf91]\n\tld [wd11e], a\n\tcp SMEARGLE\n\tjr z, .validDexNumber\n\tpredef IndexToPokedex\n\tld hl, wd11e")

# Smeargle sprite bank and cry.
replace("home/pics.asm",
        "\tld a, [wcf91] ; XXX name for this ram location\n\tld b, a\n\tcp MEW",
        "\tld a, [wcf91] ; XXX name for this ram location\n\tld b, a\n\tcp SMEARGLE\n\tld a, BANK(SmearglePicFront)\n\tjr z, .GotBank\n\tld a, b\n\tcp MEW")
replace("home/pokemon.asm",
        "GetCryData::\n; Load cry data for monster a.\n\tdec a",
        "GetCryData::\n; Load cry data for monster a.\n\tcp SMEARGLE\n\tjr nz, .notSmeargle\n\tld a, DITTO ; compatible Gen-I cry fallback\n.notSmeargle\n\tdec a")

# Name lookup for a species with no Gen-I dex number.
replace("home/names.asm",
        "GetMonName::\n\tpush hl",
        "GetMonName::\n\tld a, [wd11e]\n\tcp SMEARGLE\n\tjr nz, .normalSpecies\n\tpush hl\n\tld hl, SmeargleName\n\tld de, wcd6d\n\tld bc, 10\n\tcall CopyData\n\tpop hl\n\tld de, wcd6d\n\tret\n.normalSpecies\n\tpush hl")
p = root / "home/names.asm"
s = p.read_text() + '\nSmeargleName:\n\tdb "SMEARGLE@"\n'
p.write_text(s)

# Avoid writing an out-of-range dex flag for Smeargle.
replace("engine/events/give_pokemon.asm",
        "SetPokedexOwnedFlag:\n\tld a, [wcf91]\n\tpush af",
        "SetPokedexOwnedFlag:\n\tld a, [wcf91]\n\tcp SMEARGLE\n\tjr z, .skipDexFlag\n\tpush af")
replace("engine/events/give_pokemon.asm",
        "\tpop af\n\tld [wd11e], a\n\tcall GetMonName",
        "\tpop af\n.skipDexFlag\n\tld [wd11e], a\n\tcall GetMonName")

old = r'''	ld a, [wcf91]
	ld [wd11e], a
	push de
	predef IndexToPokedex
	pop de
	ld a, [wd11e]
	dec a
	ld c, a
	ld b, FLAG_TEST
	ld hl, wPokedexOwned
	call FlagAction
	ld a, c ; whether the mon was already flagged as owned
	ld [wUnusedD153], a ; not read
	ld a, [wd11e]
	dec a
	ld c, a
	ld b, FLAG_SET
	push bc
	call FlagAction
	pop bc
	ld hl, wPokedexSeen
	call FlagAction
'''
new = r'''	ld a, [wcf91]
	cp SMEARGLE
	jr z, .skipPlayerDexFlags
	ld [wd11e], a
	push de
	predef IndexToPokedex
	pop de
	ld a, [wd11e]
	dec a
	ld c, a
	ld b, FLAG_TEST
	ld hl, wPokedexOwned
	call FlagAction
	ld a, c ; whether the mon was already flagged as owned
	ld [wUnusedD153], a ; not read
	ld a, [wd11e]
	dec a
	ld c, a
	ld b, FLAG_SET
	push bc
	call FlagAction
	pop bc
	ld hl, wPokedexSeen
	call FlagAction
.skipPlayerDexFlags
'''
replace("engine/pokemon/add_mon.asm", old, new)

# Smeargle learns Sketch every 10 levels, matching Gen II's basic pattern.
replace("data/pokemon/evos_moves.asm",
        "\tdw MissingNo1FEvosMoves",
        "\tdw SmeargleEvosMoves")
p = root / "data/pokemon/evos_moves.asm"
s = p.read_text() + r'''

SmeargleEvosMoves:
	db 0
	db 11, SKETCH
	db 21, SKETCH
	db 31, SKETCH
	db 41, SKETCH
	db 51, SKETCH
	db 61, SKETCH
	db 71, SKETCH
	db 81, SKETCH
	db 91, SKETCH
	db 0
'''
p.write_text(s)

# Add Smeargle to the alphabetical starter selector, before Snorlax.
p = root / "custom_starter/custom_starter_init.asm"
s = p.read_text()
old = "\tdb SLOWPOKE,    DEX_SLOWPOKE\n\tdb SNORLAX,     DEX_SNORLAX"
new = "\tdb SLOWPOKE,    DEX_SLOWPOKE\n\tdb SMEARGLE,    0 ; Gen II backport\n\tdb SNORLAX,     DEX_SNORLAX"
if old not in s:
    raise SystemExit("starter alphabetical insertion point missing")
s = s.replace(old, new, 1)
p.write_text(s)

p = root / "custom_starter/custom_starter_menu.asm"
s = p.read_text()
s = s.replace("\tcp 151\n\tjr c, .updateStarterName\n\tld a, 150", "\tcp 152\n\tjr c, .updateStarterName\n\tld a, 151", 1)
s = s.replace("\tcp 151\n\tjp c, .updateStarterName", "\tcp 152\n\tjp c, .updateStarterName", 1)
p.write_text(s)

# Implement Sketch as a permanent Gen-I-compatible copy of the target's selected
# move. It replaces the Sketch slot in both battle RAM and party RAM. Because
# Gen I stores PP separately and has no native Sketch routine, initialize the
# newly copied move to 5 PP; the move itself otherwise behaves normally.
p = root / "engine/battle/effects.asm"
s = p.read_text()
old = "MimicEffect:\n\tld c, 50"
new = r'''MimicEffect:
	ldh a, [hWhoseTurn]
	and a
	jr nz, .normalMimic
	ld a, [wPlayerMoveNum]
	cp SKETCH
	jr nz, .normalMimic
	jp SketchEffect
.normalMimic
	ld c, 50'''
if old not in s:
    raise SystemExit("MimicEffect insertion point missing")
s = s.replace(old, new, 1)

insert = s.find("MimicLearnedMoveText:\n")
if insert < 0:
    raise SystemExit("Mimic text insertion point missing")
sketch = r'''SketchEffect:
	ld c, 30
	call DelayFrames
	ld a, [wEnemyMoveNum]
	and a
	jr z, .failed
	cp SKETCH
	jr z, .failed
	cp STRUGGLE
	jr z, .failed
	ld d, a

	; Replace the current battle move slot.
	ld hl, wBattleMonMoves
	ld a, [wPlayerMoveListIndex]
	ld c, a
	ld b, 0
	add hl, bc
	ld a, d
	ld [hl], a

	; Persist the copied move to the active party Pokemon.
	ld hl, wPartyMon1Moves
	ld a, [wPlayerMonNumber]
	ld bc, wPartyMon2 - wPartyMon1
	call AddNTimes
	ld a, [wPlayerMoveListIndex]
	ld c, a
	ld b, 0
	add hl, bc
	ld a, d
	ld [hl], a

	; Give the copied move usable PP in both battle and party storage.
	ld hl, wBattleMonPP
	ld a, [wPlayerMoveListIndex]
	ld c, a
	ld b, 0
	add hl, bc
	ld [hl], 5
	ld hl, wPartyMon1PP
	ld a, [wPlayerMonNumber]
	ld bc, wPartyMon2 - wPartyMon1
	call AddNTimes
	ld a, [wPlayerMoveListIndex]
	ld c, a
	ld b, 0
	add hl, bc
	ld [hl], 5

	ld a, d
	ld [wd11e], a
	call GetMoveName
	call PlayCurrentMoveAnimation
	ld hl, MimicLearnedMoveText
	jp PrintText
.failed
	jp PrintButItFailedText_

'''
s = s[:insert] + sketch + s[insert:]
p.write_text(s)

print("Applied Smeargle backport")
print("Smeargle selectable as starter")
print("Sketch added and persists copied move to party")
print("Gen II Smeargle front/back sprites expected from pret/pokecrystal")
