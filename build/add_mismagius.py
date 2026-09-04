from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "hack")


def replace(path, old, new, count=1):
    p = root / path
    s = p.read_text()
    if old not in s:
        raise SystemExit(f"Missing expected text in {path}: {old[:80]!r}")
    p.write_text(s.replace(old, new, count))

# ---------------------------------------------------------------------------
# Species ID: repurpose unused internal slot $1f. This does NOT consume a
# Pokédex number; Mismagius is handled as a special species like the fossil
# sprites / Mew paths in the Gen I engine.
# ---------------------------------------------------------------------------
replace("constants/pokemon_constants.asm",
        "\tconst_skip               ; $1F",
        "\tconst MISMAGIUS          ; $1F ; Battle Hub expansion")

# ---------------------------------------------------------------------------
# Four post-Gen-I moves. Insert before STRUGGLE so the move data/name/animation
# tables remain contiguous. All symbolic animation constants shift together.
# ---------------------------------------------------------------------------
replace("constants/move_constants.asm",
        "\tconst SUBSTITUTE   ; a4\n\nNUM_ATTACKS EQU const_value - 1\n\n\tconst STRUGGLE     ; a5",
        "\tconst SUBSTITUTE   ; a4\n\tconst SHADOW_BALL  ; a5 ; Gen II\n\tconst ASTONISH     ; a6 ; Gen III\n\tconst MAGICAL_LEAF ; a7 ; Gen III\n\tconst POWER_GEM    ; a8 ; Gen IV\n\nNUM_ATTACKS EQU const_value - 1\n\n\tconst STRUGGLE     ; a9")

replace("data/moves/moves.asm",
        "\tmove SUBSTITUTE,   SUBSTITUTE_EFFECT,            0, NORMAL,       100, 10\n\tmove STRUGGLE,     RECOIL_EFFECT,               50, NORMAL,       100, 10",
        "\tmove SUBSTITUTE,   SUBSTITUTE_EFFECT,            0, NORMAL,       100, 10\n\tmove SHADOW_BALL,  NO_ADDITIONAL_EFFECT,        80, GHOST,        100, 15\n\tmove ASTONISH,     FLINCH_SIDE_EFFECT1,         30, GHOST,        100, 15\n\tmove MAGICAL_LEAF, SWIFT_EFFECT,                60, GRASS,        100, 20\n\tmove POWER_GEM,    NO_ADDITIONAL_EFFECT,        80, ROCK,         100, 20\n\tmove STRUGGLE,     RECOIL_EFFECT,               50, NORMAL,       100, 10")

replace("data/moves/names.asm",
        "\tdb \"SUBSTITUTE@\"\n\tdb \"STRUGGLE@\"",
        "\tdb \"SUBSTITUTE@\"\n\tdb \"SHADOW BALL@\"\n\tdb \"ASTONISH@\"\n\tdb \"MAGICAL LEAF@\"\n\tdb \"POWER GEM@\"\n\tdb \"STRUGGLE@\"")

# Reuse compatible Gen-I visual effects rather than adding an entirely new
# animation engine: Night Shade, Lick, Swift and Rock Slide respectively.
replace("data/moves/animations.asm",
        "\tdw SubstituteAnim\n\tdw StruggleAnim",
        "\tdw SubstituteAnim\n\tdw NightShadeAnim ; SHADOW_BALL\n\tdw LickAnim       ; ASTONISH\n\tdw SwiftAnim      ; MAGICAL_LEAF\n\tdw RockSlideAnim  ; POWER_GEM\n\tdw StruggleAnim")

# Matching sound table entries; these intentionally reuse existing SFX.
replace("data/moves/sfx.asm",
        "\tdb SFX_BATTLE_2C,          $d8, $04 ; SUBSTITUTE\n\tdb SFX_BATTLE_0B,          $00, $80 ; STRUGGLE",
        "\tdb SFX_BATTLE_2C,          $d8, $04 ; SUBSTITUTE\n\tdb SFX_BATTLE_0C,          $f0, $f0 ; SHADOW_BALL\n\tdb SFX_BATTLE_1E,          $12, $ff ; ASTONISH\n\tdb SFX_NOT_VERY_EFFECTIVE, $01, $ff ; MAGICAL_LEAF\n\tdb SFX_BATTLE_36,          $f0, $20 ; POWER_GEM\n\tdb SFX_BATTLE_0B,          $00, $80 ; STRUGGLE")

# ---------------------------------------------------------------------------
# Mismagius base data. Gen I has a single Special stat, so modern SpA/SpD 105
# map cleanly to Special 105. Pure Ghost. Gengar graphics are used as a safe
# Gen-I placeholder in this build; gameplay identity/stats/moves are distinct.
# ---------------------------------------------------------------------------
p = root / "data/pokemon/mew.asm"
s = p.read_text()
s += r'''

MismagiusBaseStats:
	db 0 ; no Gen-I Pokédex number
	db 60, 60, 60, 105, 105
	;  hp atk def spd  spc
	db GHOST, GHOST
	db 45 ; catch rate
	db 173 ; base exp
	INCBIN "gfx/pokemon/front/gengar.pic", 0, 1
	dw GengarPicFront, GengarPicBack
	db ASTONISH, MAGICAL_LEAF, SHADOW_BALL, POWER_GEM
	db GROWTH_MEDIUM_FAST
	tmhm TOXIC,        BODY_SLAM,    TAKE_DOWN,    DOUBLE_EDGE,  HYPER_BEAM,   \
	     MEGA_DRAIN,   THUNDERBOLT,  THUNDER,      PSYCHIC_M,    MIMIC,        \
	     DOUBLE_TEAM,  BIDE,         METRONOME,    DREAM_EATER,  REST,         \
	     THUNDER_WAVE, PSYWAVE,      SUBSTITUTE,   FLASH
	db 0
'''
p.write_text(s)

# Load the dedicated base-stat record for internal species $1f.
replace("home/pokemon.asm",
        "\tcp MEW\n\tjr z, .mew\n\tpredef IndexToPokedex",
        "\tcp MISMAGIUS\n\tjr z, .mismagius\n\tcp MEW\n\tjr z, .mew\n\tpredef IndexToPokedex")
replace("home/pokemon.asm",
        ".mew\n\tld hl, MewBaseStats\n\tld de, wMonHeader\n\tld bc, MonBaseStatsEnd - MonBaseStats\n\tld a, BANK(MewBaseStats)\n\tcall FarCopyData\n.done",
        ".mismagius\n\tld hl, MismagiusBaseStats\n\tld de, wMonHeader\n\tld bc, MonBaseStatsEnd - MonBaseStats\n\tld a, BANK(MismagiusBaseStats)\n\tcall FarCopyData\n\tjr .done\n.mew\n\tld hl, MewBaseStats\n\tld de, wMonHeader\n\tld bc, MonBaseStatsEnd - MonBaseStats\n\tld a, BANK(MewBaseStats)\n\tcall FarCopyData\n.done")

# Front-sprite validation normally rejects internal IDs without a dex number.
replace("home/pokemon.asm",
        "\tld a, [wcf91]\n\tld [wd11e], a\n\tpredef IndexToPokedex\n\tld hl, wd11e",
        "\tld a, [wcf91]\n\tld [wd11e], a\n\tcp MISMAGIUS\n\tjr z, .validDexNumber\n\tpredef IndexToPokedex\n\tld hl, wd11e")

# Mismagius currently reuses Gengar's Gen-I sprite graphics; make sure the
# decompressor selects Gengar's ROM bank despite the new internal ID.
replace("home/pics.asm",
        "\tld a, [wcf91] ; XXX name for this ram location\n\tld b, a\n\tcp MEW",
        "\tld a, [wcf91] ; XXX name for this ram location\n\tld b, a\n\tcp MISMAGIUS\n\tld a, BANK(GengarPicFront)\n\tjr z, .GotBank\n\tld a, b\n\tcp MEW")

# Reuse Gengar's cry rather than indexing the MissingNo cry-table entry.
replace("home/pokemon.asm",
        "GetCryData::\n; Load cry data for monster a.\n\tdec a",
        "GetCryData::\n; Load cry data for monster a.\n\tcp MISMAGIUS\n\tjr nz, .notMismagius\n\tld a, GENGAR\n.notMismagius\n\tdec a")

# Custom fixed-width species name, bypassing the 151-entry MonsterNames table.
replace("home/names.asm",
        "GetMonName::\n\tpush hl",
        "GetMonName::\n\tld a, [wd11e]\n\tcp MISMAGIUS\n\tjr nz, .normalSpecies\n\tpush hl\n\tld hl, MismagiusName\n\tld de, wcd6d\n\tld bc, 10\n\tcall CopyData\n\tpop hl\n\tld de, wcd6d\n\tret\n.normalSpecies\n\tpush hl")
p = root / "home/names.asm"
s = p.read_text() + '\nMismagiusName:\n\tdb "MISMAGIUS@"\n'
p.write_text(s)

# Give/party routines normally set a 151-bit Pokédex flag. Skip that operation
# for Mismagius while still displaying its name and adding it to the party.
replace("engine/events/give_pokemon.asm",
        "SetPokedexOwnedFlag:\n\tld a, [wcf91]\n\tpush af",
        "SetPokedexOwnedFlag:\n\tld a, [wcf91]\n\tcp MISMAGIUS\n\tjr z, .skipDexFlag\n\tpush af")
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
	cp MISMAGIUS
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

# Give Mismagius a proper level-up pointer in the internal-ID table. Its four
# expansion moves are already its starting moves, then it gains familiar
# ghost/psychic options as it levels.
replace("data/pokemon/evos_moves.asm",
        "\tdw MissingNo1FEvosMoves",
        "\tdw MismagiusEvosMoves")
p = root / "data/pokemon/evos_moves.asm"
s = p.read_text() + r'''

MismagiusEvosMoves:
	db 0 ; no evolutions in this standalone Battle Hub implementation
	db 10, PSYWAVE
	db 14, CONFUSE_RAY
	db 19, NIGHT_SHADE
	db 24, PSYCHIC_M
	db 30, THUNDERBOLT
	db 36, DREAM_EATER
	db 42, SHADOW_BALL
	db 0
'''
p.write_text(s)

# ---------------------------------------------------------------------------
# Starter UI: preserve the fork's complete 151-species selector. Wrap it with
# one extra yes/no choice. No = keep selected Gen-I mon. Yes = Mismagius.
# ---------------------------------------------------------------------------
selector_file = None
for p in root.rglob("*.asm"):
    try:
        text = p.read_text()
    except UnicodeDecodeError:
        continue
    if "DisplayStarterMenu::" in text:
        selector_file = p
        break
if selector_file is None:
    raise SystemExit("Could not locate DisplayStarterMenu::")
text = selector_file.read_text()
text = text.replace("DisplayStarterMenu::", "DisplayStarterMenuOriginal::", 1)
text += r'''

; Battle Hub expansion wrapper: original 151 choices + dedicated Mismagius.
DisplayStarterMenu::
	call DisplayStarterMenuOriginal
	call ClearScreen
	hlcoord 1, 7
	ld de, BattleHubMismagiusChoiceText
	call PlaceString
	call UpdateSprites
	call YesNoChoice
	ld a, [wCurrentMenuItem]
	and a
	ret nz
	ld a, MISMAGIUS
	ld [wCustomStarterInternalID], a
	; Keep the fork's dex helper on a valid Gen-I number. Gameplay uses the
	; internal ID above; Mismagius deliberately has no Gen-I dex bit.
	ld a, DEX_GENGAR
	ld [wCustomStarterDexID], a
	ret

BattleHubMismagiusChoiceText:
	db "MISMAGIUS INSTEAD?@"
'''
selector_file.write_text(text)
print(f"Wrapped starter selector in {selector_file.relative_to(root)}")
