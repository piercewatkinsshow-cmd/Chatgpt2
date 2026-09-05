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

# Reuse unused internal species slot $1F. This starts from the successful
# Battle Hub base, not the Smeargle branch.
replace("constants/pokemon_constants.asm",
        "\tconst_skip               ; $1F",
        "\tconst PORYGON_Z          ; $1F ; Gen IV backport")

# Graphics live in a relocatable section so the original Gen I picture banks
# are left intact.
p = root / "gfx/pics.asm"
s = p.read_text()
s += r'''

SECTION "Porygon-Z Pics", ROMX
PorygonZPicFront:: INCBIN "gfx/pokemon/front/porygonz.pic"
PorygonZPicBack::  INCBIN "gfx/pokemon/back/porygonzb.pic"
'''
p.write_text(s)

# Gen IV base stats are 85/80/70/90/135 SpA/75 SpD. Gen I has a single Special
# stat, so use 135 to preserve Porygon-Z's defining special-offense identity.
# TM/HM compatibility is based on Gen I Porygon, which is the closest native
# analogue and keeps the hack mechanically coherent.
p = root / "data/pokemon/mew.asm"
s = p.read_text()
s += r'''

PorygonZBaseStats::
	db 0 ; no Gen-I Pokedex number
	db 85, 80, 70, 90, 135
	;  hp atk def spd spc
	db NORMAL, NORMAL
	db 30 ; catch rate
	db 241 ; base exp
	INCBIN "gfx/pokemon/front/porygonz.pic", 0, 1
	dw PorygonZPicFront, PorygonZPicBack
	db TACKLE, SHARPEN, CONVERSION, NO_MOVE
	db GROWTH_MEDIUM_FAST
	tmhm TOXIC,        TAKE_DOWN,    DOUBLE_EDGE,  ICE_BEAM,     BLIZZARD,     \
	     HYPER_BEAM,   RAGE,         THUNDERBOLT,  THUNDER,      PSYCHIC_M,    \
	     TELEPORT,     MIMIC,        DOUBLE_TEAM,  REFLECT,      BIDE,         \
	     SWIFT,        SKULL_BASH,   REST,         THUNDER_WAVE, PSYWAVE,      \
	     TRI_ATTACK,   SUBSTITUTE,   FLASH
	db 0
'''
p.write_text(s)

# Special-case base-stat lookup for the reused MissingNo slot.
replace("home/pokemon.asm",
        "\tcp MEW\n\tjr z, .mew\n\tpredef IndexToPokedex",
        "\tcp PORYGON_Z\n\tjr z, .porygonZ\n\tcp MEW\n\tjr z, .mew\n\tpredef IndexToPokedex")
replace("home/pokemon.asm",
        ".mew\n\tld hl, MewBaseStats\n\tld de, wMonHeader\n\tld bc, MonBaseStatsEnd - MonBaseStats\n\tld a, BANK(MewBaseStats)\n\tcall FarCopyData\n.done",
        ".porygonZ\n\tld hl, PorygonZBaseStats\n\tld de, wMonHeader\n\tld bc, MonBaseStatsEnd - MonBaseStats\n\tld a, BANK(PorygonZBaseStats)\n\tcall FarCopyData\n\tjr .done\n.mew\n\tld hl, MewBaseStats\n\tld de, wMonHeader\n\tld bc, MonBaseStatsEnd - MonBaseStats\n\tld a, BANK(MewBaseStats)\n\tcall FarCopyData\n.done")
replace("home/pokemon.asm",
        "\tld a, [wcf91]\n\tld [wd11e], a\n\tpredef IndexToPokedex\n\tld hl, wd11e",
        "\tld a, [wcf91]\n\tld [wd11e], a\n\tcp PORYGON_Z\n\tjr z, .validDexNumber\n\tpredef IndexToPokedex\n\tld hl, wd11e")

# Picture bank and a compatible electronic Gen-I cry fallback.
replace("home/pics.asm",
        "\tld a, [wcf91] ; XXX name for this ram location\n\tld b, a\n\tcp MEW",
        "\tld a, [wcf91] ; XXX name for this ram location\n\tld b, a\n\tcp PORYGON_Z\n\tld a, BANK(PorygonZPicFront)\n\tjr z, .GotBank\n\tld a, b\n\tcp MEW")
replace("home/pokemon.asm",
        "GetCryData::\n; Load cry data for monster a.\n\tdec a",
        "GetCryData::\n; Load cry data for monster a.\n\tcp PORYGON_Z\n\tjr nz, .notPorygonZ\n\tld a, PORYGON\n.notPorygonZ\n\tdec a")

# Custom species name because this slot has no Gen-I dex entry.
replace("home/names.asm",
        "GetMonName::\n\tpush hl",
        "GetMonName::\n\tld a, [wd11e]\n\tcp PORYGON_Z\n\tjr nz, .normalSpecies\n\tpush hl\n\tld hl, PorygonZName\n\tld de, wcd6d\n\tld bc, 10\n\tcall CopyData\n\tpop hl\n\tld de, wcd6d\n\tret\n.normalSpecies\n\tpush hl")
p = root / "home/names.asm"
s = p.read_text() + '\nPorygonZName:\n\tdb "PORYGON-Z@"\n'
p.write_text(s)

# Do not touch the 151-entry Pokedex bitfields for the custom species.
replace("engine/events/give_pokemon.asm",
        "SetPokedexOwnedFlag:\n\tld a, [wcf91]\n\tpush af",
        "SetPokedexOwnedFlag:\n\tld a, [wcf91]\n\tcp PORYGON_Z\n\tjr z, .skipDexFlag\n\tpush af")
replace("engine/events/give_pokemon.asm",
        "\tpop af\n\tld [wd11e], a\n\tcall GetMonName",
        "\tpop af\n.skipDexFlag\n\tld [wd11e], a\n\tcall GetMonName")

old = r'''\tld a, [wcf91]
\tld [wd11e], a
\tpush de
\tpredef IndexToPokedex
\tpop de
\tld a, [wd11e]
\tdec a
\tld c, a
\tld b, FLAG_TEST
\tld hl, wPokedexOwned
\tcall FlagAction
\tld a, c ; whether the mon was already flagged as owned
\tld [wUnusedD153], a ; not read
\tld a, [wd11e]
\tdec a
\tld c, a
\tld b, FLAG_SET
\tpush bc
\tcall FlagAction
\tpop bc
\tld hl, wPokedexSeen
\tcall FlagAction
'''
new = r'''\tld a, [wcf91]
\tcp PORYGON_Z
\tjr z, .skipPlayerDexFlags
\tld [wd11e], a
\tpush de
\tpredef IndexToPokedex
\tpop de
\tld a, [wd11e]
\tdec a
\tld c, a
\tld b, FLAG_TEST
\tld hl, wPokedexOwned
\tcall FlagAction
\tld a, c ; whether the mon was already flagged as owned
\tld [wUnusedD153], a ; not read
\tld a, [wd11e]
\tdec a
\tld c, a
\tld b, FLAG_SET
\tpush bc
\tcall FlagAction
\tpop bc
\tld hl, wPokedexSeen
\tcall FlagAction
.skipPlayerDexFlags
'''
replace("engine/pokemon/add_mon.asm", old, new)

# A Gen-I-native approximation of Porygon-Z's level-up progression.
replace("data/pokemon/evos_moves.asm",
        "\tdw MissingNo1FEvosMoves",
        "\tdw PorygonZEvosMoves")
p = root / "data/pokemon/evos_moves.asm"
s = p.read_text() + r'''

PorygonZEvosMoves:
	db 0
	db 23, PSYBEAM
	db 28, RECOVER
	db 35, AGILITY
	db 42, TRI_ATTACK
	db 49, PSYCHIC_M
	db 56, HYPER_BEAM
	db 0
'''
p.write_text(s)

# Add Porygon-Z immediately after Porygon in the alphabetical starter selector.
p = root / "custom_starter/custom_starter_init.asm"
s = p.read_text()
old = "\tdb PORYGON,     DEX_PORYGON\n\tdb PRIMEAPE,    DEX_PRIMEAPE"
new = "\tdb PORYGON,     DEX_PORYGON\n\tdb PORYGON_Z,   0 ; Gen IV backport\n\tdb PRIMEAPE,    DEX_PRIMEAPE"
if old not in s:
    raise SystemExit("starter insertion point missing")
p.write_text(s.replace(old, new, 1))

p = root / "custom_starter/custom_starter_menu.asm"
s = p.read_text()
s = s.replace("\tcp 151\n\tjr c, .updateStarterName\n\tld a, 150", "\tcp 152\n\tjr c, .updateStarterName\n\tld a, 151", 1)
s = s.replace("\tcp 151\n\tjp c, .updateStarterName", "\tcp 152\n\tjp c, .updateStarterName", 1)
p.write_text(s)

print("Applied Porygon-Z backport")
print("Porygon-Z selectable as starter from the successful base Battle Hub")
print("Stats: 85 HP / 80 Atk / 70 Def / 90 Spd / 135 Special")
