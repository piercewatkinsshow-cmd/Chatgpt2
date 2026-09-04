from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "hack")


def replace_exact(path, old, new):
    p = root / path
    s = p.read_text()
    if old not in s:
        raise SystemExit(f"expected block not found in {path}")
    p.write_text(s.replace(old, new, 1))

# Start the new game directly inside the Indigo Plateau lobby.
replace_exact(
    "data/maps/special_warps.asm",
    "FirstMapSpec:\n\tspecial_warp_spec REDS_HOUSE_2F, 3, 6, REDS_HOUSE_2",
    "FirstMapSpec:\n\tspecial_warp_spec INDIGO_PLATEAU_LOBBY, 7, 9, MART",
)

# Automatically open the custom starter selector when NEW GAME is chosen.
# The custom-starter project already contains all 151 species and DV controls.
# Force all four DVs back to 15 when the selector closes.
replace_exact(
    "engine/menus/main_menu.asm",
    "StartNewGame:\n\tld a, 1 ; CHANGE\n\tld [wDisabledCustomStarterMenu], a ; disables starter menu even without save",
    "StartNewGame:\n\tfarcall DisplayStarterMenu\n\tld a, $f\n\tld hl, wCustomStarterAtkDV\n\tld [hli], a\n\tld [hli], a\n\tld [hli], a\n\tld [hl], a\n\tld a, 1 ; CHANGE\n\tld [wDisabledCustomStarterMenu], a ; disables starter menu even without save",
)

# Replace the stock Potion/Repel startup items with the requested Battle Hub kit.
replace_exact(
    "engine/movie/oak_speech/oak_speech.asm",
    "\tld hl, wNumBoxItems\n\tld a, POTION\n\tld [wcf91], a\n\tld a, 1\n\tld [wItemQuantity], a\n\tcall AddItemToInventory  ; give one potion\n\tld a, REPEL ; CHANGE\n\tld [wcf91], a \n\tld a, 6 \n\tld [wItemQuantity], a\n\tcall AddItemToInventory  ; give six Repels",
    "\tld hl, BattleHubBagItems\n\tld de, wNumBagItems\n\tld bc, BattleHubBagItemsEnd - BattleHubBagItems\n\tcall CopyData\n\tld hl, BattleHubPCItems\n\tld de, wNumBoxItems\n\tld bc, BattleHubPCItemsEnd - BattleHubPCItems\n\tcall CopyData",
)

# Give the selected species at level 5 after the player/rival names are chosen.
replace_exact(
    "engine/movie/oak_speech/oak_speech.asm",
    ".skipChoosingNames\n\tcall GBFadeOutToWhite",
    ".skipChoosingNames\n\tld a, [wCustomStarterInternalID]\n\tld b, a\n\tld c, 5\n\tcall GivePokemon\n\tSetEvent EVENT_GOT_STARTER\n\tcall GBFadeOutToWhite",
)

# Append startup inventory lists. Bag intentionally leaves eight free unique-item
# slots so every Gym Leader TM can be awarded without immediately overflowing.
p = root / "engine/movie/oak_speech/oak_speech.asm"
s = p.read_text()
s += r'''

; Battle Hub starting inventory.
; Inventory format: count, (item, quantity)*, $ff.
BattleHubBagItems:
	db 12
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
	db TM_MEGA_PUNCH, 1
	db $ff
BattleHubBagItemsEnd:

; All remaining non-Gym-reward TMs are immediately available in the player's PC.
BattleHubPCItems:
	db 41
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
p.write_text(s)

# One-room object layout. Fourteen NPCs + player stays within the engine's
# sixteen-sprite state-data limit. The PC is a background/sign event.
(root / "data/maps/objects/IndigoPlateauLobby.asm").write_text(r'''IndigoPlateauLobby_Object:
	db $0 ; border block

	def_warps

	def_signs
	sign 13, 5, 15 ; Pokemon Center PC

	def_objects
	object SPRITE_SUPER_NERD,      1, 2, STAY, DOWN,  1, OPP_BROCK, 1
	object SPRITE_BRUNETTE_GIRL,   4, 2, STAY, DOWN,  2, OPP_MISTY, 1
	object SPRITE_COOLTRAINER_M,    7, 2, STAY, DOWN,  3, OPP_LT_SURGE, 1
	object SPRITE_BRUNETTE_GIRL,  10, 2, STAY, DOWN,  4, OPP_ERIKA, 1
	object SPRITE_SUPER_NERD,       1, 4, STAY, DOWN,  5, OPP_KOGA, 1
	object SPRITE_BRUNETTE_GIRL,    4, 4, STAY, DOWN,  6, OPP_SABRINA, 1
	object SPRITE_SUPER_NERD,      10, 4, STAY, DOWN,  7, OPP_BLAINE, 1
	object SPRITE_COOLTRAINER_M,   12, 4, STAY, DOWN,  8, OPP_GIOVANNI, 3
	object SPRITE_COOLTRAINER_F,    1, 7, STAY, DOWN,  9, OPP_LORELEI, 1
	object SPRITE_COOLTRAINER_M,    4, 7, STAY, DOWN, 10, OPP_BRUNO, 1
	object SPRITE_COOLTRAINER_F,   10, 7, STAY, DOWN, 11, OPP_AGATHA, 1
	object SPRITE_COOLTRAINER_M,   12, 7, STAY, DOWN, 12, OPP_LANCE, 1
	object SPRITE_BLUE,             7, 7, STAY, DOWN, 13, OPP_RIVAL3, 1
	object SPRITE_NURSE,            7, 5, STAY, DOWN, 14

	def_warps_to INDIGO_PLATEAU_LOBBY
''')

# The Battle Hub script uses the original trainer classes/party numbers.
# Event flags provide progression gating and persistent defeated state.
(root / "scripts/IndigoPlateauLobby.asm").write_text(r'''IndigoPlateauLobby_Script:
	call EnableAutoTextBoxDrawing
	call BattleHubAwardGymRewards
	ld hl, BattleHubTrainerHeader0
	ld de, IndigoPlateauLobby_ScriptPointers
	ld a, [wIndigoPlateauLobbyCurScript]
	call ExecuteCurMapScriptInTable
	ld [wIndigoPlateauLobbyCurScript], a
	ret

IndigoPlateauLobby_ScriptPointers:
	dw CheckFightingMapTrainers
	dw DisplayEnemyTrainerTextAndStartBattle
	dw EndTrainerBattle

IndigoPlateauLobby_TextPointers:
	dw BattleHubBrockText
	dw BattleHubMistyText
	dw BattleHubSurgeText
	dw BattleHubErikaText
	dw BattleHubKogaText
	dw BattleHubSabrinaText
	dw BattleHubBlaineText
	dw BattleHubGiovanniText
	dw BattleHubLoreleiText
	dw BattleHubBrunoText
	dw BattleHubAgathaText
	dw BattleHubLanceText
	dw BattleHubChampionText
	dw BattleHubNurseText
	dw BattleHubPCText

BattleHubTrainerHeader0:
	trainer EVENT_BEAT_BROCK, 0, BattleHubBeforeBattleText, BattleHubEndBattleText, BattleHubAfterBattleText
BattleHubTrainerHeader1:
	trainer EVENT_BEAT_MISTY, 0, BattleHubBeforeBattleText, BattleHubEndBattleText, BattleHubAfterBattleText
BattleHubTrainerHeader2:
	trainer EVENT_BEAT_LT_SURGE, 0, BattleHubBeforeBattleText, BattleHubEndBattleText, BattleHubAfterBattleText
BattleHubTrainerHeader3:
	trainer EVENT_BEAT_ERIKA, 0, BattleHubBeforeBattleText, BattleHubEndBattleText, BattleHubAfterBattleText
BattleHubTrainerHeader4:
	trainer EVENT_BEAT_KOGA, 0, BattleHubBeforeBattleText, BattleHubEndBattleText, BattleHubAfterBattleText
BattleHubTrainerHeader5:
	trainer EVENT_BEAT_SABRINA, 0, BattleHubBeforeBattleText, BattleHubEndBattleText, BattleHubAfterBattleText
BattleHubTrainerHeader6:
	trainer EVENT_BEAT_BLAINE, 0, BattleHubBeforeBattleText, BattleHubEndBattleText, BattleHubAfterBattleText
BattleHubTrainerHeader7:
	trainer EVENT_BEAT_VIRIDIAN_GYM_GIOVANNI, 0, BattleHubBeforeBattleText, BattleHubEndBattleText, BattleHubAfterBattleText
BattleHubTrainerHeader8:
	trainer EVENT_BEAT_LORELEIS_ROOM_TRAINER_0, 0, BattleHubBeforeBattleText, BattleHubEndBattleText, BattleHubAfterBattleText
BattleHubTrainerHeader9:
	trainer EVENT_BEAT_BRUNOS_ROOM_TRAINER_0, 0, BattleHubBeforeBattleText, BattleHubEndBattleText, BattleHubAfterBattleText
BattleHubTrainerHeader10:
	trainer EVENT_BEAT_AGATHAS_ROOM_TRAINER_0, 0, BattleHubBeforeBattleText, BattleHubEndBattleText, BattleHubAfterBattleText
BattleHubTrainerHeader11:
	trainer EVENT_BEAT_LANCES_ROOM_TRAINER_0, 0, BattleHubBeforeBattleText, BattleHubEndBattleText, BattleHubAfterBattleText
BattleHubTrainerHeader12:
	trainer EVENT_BEAT_CHAMPION_RIVAL, 0, BattleHubChampionBeforeText, BattleHubChampionEndText, BattleHubChampionAfterText
	db -1 ; end

BattleHubBrockText:
	text_asm
	ld hl, BattleHubTrainerHeader0
	call TalkToTrainer
	jp TextScriptEnd

BattleHubMistyText:
	text_asm
	CheckEvent EVENT_BEAT_BROCK
	jr z, .locked
	ld hl, BattleHubTrainerHeader1
	call TalkToTrainer
	jp TextScriptEnd
.locked
	ld hl, BattleHubLockedText
	call PrintText
	jp TextScriptEnd

BattleHubSurgeText:
	text_asm
	CheckEvent EVENT_BEAT_MISTY
	jr z, .locked
	ld hl, BattleHubTrainerHeader2
	call TalkToTrainer
	jp TextScriptEnd
.locked
	ld hl, BattleHubLockedText
	call PrintText
	jp TextScriptEnd

BattleHubErikaText:
	text_asm
	CheckEvent EVENT_BEAT_LT_SURGE
	jr z, .locked
	ld hl, BattleHubTrainerHeader3
	call TalkToTrainer
	jp TextScriptEnd
.locked
	ld hl, BattleHubLockedText
	call PrintText
	jp TextScriptEnd

BattleHubKogaText:
	text_asm
	CheckEvent EVENT_BEAT_ERIKA
	jr z, .locked
	ld hl, BattleHubTrainerHeader4
	call TalkToTrainer
	jp TextScriptEnd
.locked
	ld hl, BattleHubLockedText
	call PrintText
	jp TextScriptEnd

BattleHubSabrinaText:
	text_asm
	CheckEvent EVENT_BEAT_KOGA
	jr z, .locked
	ld hl, BattleHubTrainerHeader5
	call TalkToTrainer
	jp TextScriptEnd
.locked
	ld hl, BattleHubLockedText
	call PrintText
	jp TextScriptEnd

BattleHubBlaineText:
	text_asm
	CheckEvent EVENT_BEAT_SABRINA
	jr z, .locked
	ld hl, BattleHubTrainerHeader6
	call TalkToTrainer
	jp TextScriptEnd
.locked
	ld hl, BattleHubLockedText
	call PrintText
	jp TextScriptEnd

BattleHubGiovanniText:
	text_asm
	CheckEvent EVENT_BEAT_BLAINE
	jr z, .locked
	ld hl, BattleHubTrainerHeader7
	call TalkToTrainer
	jp TextScriptEnd
.locked
	ld hl, BattleHubLockedText
	call PrintText
	jp TextScriptEnd

BattleHubLoreleiText:
	text_asm
	CheckEvent EVENT_BEAT_VIRIDIAN_GYM_GIOVANNI
	jr z, .locked
	ld hl, BattleHubTrainerHeader8
	call TalkToTrainer
	jp TextScriptEnd
.locked
	ld hl, BattleHubLockedText
	call PrintText
	jp TextScriptEnd

BattleHubBrunoText:
	text_asm
	CheckEvent EVENT_BEAT_LORELEIS_ROOM_TRAINER_0
	jr z, .locked
	ld hl, BattleHubTrainerHeader9
	call TalkToTrainer
	jp TextScriptEnd
.locked
	ld hl, BattleHubLockedText
	call PrintText
	jp TextScriptEnd

BattleHubAgathaText:
	text_asm
	CheckEvent EVENT_BEAT_BRUNOS_ROOM_TRAINER_0
	jr z, .locked
	ld hl, BattleHubTrainerHeader10
	call TalkToTrainer
	jp TextScriptEnd
.locked
	ld hl, BattleHubLockedText
	call PrintText
	jp TextScriptEnd

BattleHubLanceText:
	text_asm
	CheckEvent EVENT_BEAT_AGATHAS_ROOM_TRAINER_0
	jr z, .locked
	ld hl, BattleHubTrainerHeader11
	call TalkToTrainer
	jp TextScriptEnd
.locked
	ld hl, BattleHubLockedText
	call PrintText
	jp TextScriptEnd

BattleHubChampionText:
	text_asm
	CheckEvent EVENT_BEAT_LANCES_ROOM_TRAINER_0
	jr z, .locked
	ld hl, BattleHubTrainerHeader12
	call TalkToTrainer
	jp TextScriptEnd
.locked
	ld hl, BattleHubLockedText
	call PrintText
	jp TextScriptEnd

BattleHubNurseText:
	script_pokecenter_nurse

BattleHubPCText:
	script_pokecenter_pc

BattleHubBeforeBattleText:
	text "Your challenge"
	line "starts now!"
	done

BattleHubEndBattleText:
	text "A worthy win!"
	prompt

BattleHubAfterBattleText:
	text "You already beat"
	line "me. Move on!"
	done

BattleHubChampionBeforeText:
	text "One last battle!"
	line "For the title!"
	done

BattleHubChampionEndText:
	text "You earned it!"
	prompt

BattleHubChampionAfterText:
	text "You are the"
	line "CHAMPION!"
	done

BattleHubLockedText:
	text "Beat the previous"
	line "trainer first!"
	done

; Give the eight badges and their normal Gym Leader TM rewards.
; Got-TM event flags make the routine idempotent.
BattleHubAwardGymRewards:
	CheckEvent EVENT_BEAT_BROCK
	jr z, .misty
	ld hl, wObtainedBadges
	set BIT_BOULDERBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_BOULDERBADGE, [hl]
	CheckEvent EVENT_GOT_TM34
	jr nz, .misty
	lb bc, TM_BIDE, 1
	call GiveItem
	jr nc, .misty
	SetEvent EVENT_GOT_TM34
.misty
	CheckEvent EVENT_BEAT_MISTY
	jr z, .surge
	ld hl, wObtainedBadges
	set BIT_CASCADEBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_CASCADEBADGE, [hl]
	CheckEvent EVENT_GOT_TM11
	jr nz, .surge
	lb bc, TM_BUBBLEBEAM, 1
	call GiveItem
	jr nc, .surge
	SetEvent EVENT_GOT_TM11
.surge
	CheckEvent EVENT_BEAT_LT_SURGE
	jr z, .erika
	ld hl, wObtainedBadges
	set BIT_THUNDERBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_THUNDERBADGE, [hl]
	CheckEvent EVENT_GOT_TM24
	jr nz, .erika
	lb bc, TM_THUNDERBOLT, 1
	call GiveItem
	jr nc, .erika
	SetEvent EVENT_GOT_TM24
.erika
	CheckEvent EVENT_BEAT_ERIKA
	jr z, .koga
	ld hl, wObtainedBadges
	set BIT_RAINBOWBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_RAINBOWBADGE, [hl]
	CheckEvent EVENT_GOT_TM21
	jr nz, .koga
	lb bc, TM_MEGA_DRAIN, 1
	call GiveItem
	jr nc, .koga
	SetEvent EVENT_GOT_TM21
.koga
	CheckEvent EVENT_BEAT_KOGA
	jr z, .sabrina
	ld hl, wObtainedBadges
	set BIT_SOULBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_SOULBADGE, [hl]
	CheckEvent EVENT_GOT_TM06
	jr nz, .sabrina
	lb bc, TM_TOXIC, 1
	call GiveItem
	jr nc, .sabrina
	SetEvent EVENT_GOT_TM06
.sabrina
	CheckEvent EVENT_BEAT_SABRINA
	jr z, .blaine
	ld hl, wObtainedBadges
	set BIT_MARSHBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_MARSHBADGE, [hl]
	CheckEvent EVENT_GOT_TM46
	jr nz, .blaine
	lb bc, TM_PSYWAVE, 1
	call GiveItem
	jr nc, .blaine
	SetEvent EVENT_GOT_TM46
.blaine
	CheckEvent EVENT_BEAT_BLAINE
	jr z, .giovanni
	ld hl, wObtainedBadges
	set BIT_VOLCANOBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_VOLCANOBADGE, [hl]
	CheckEvent EVENT_GOT_TM38
	jr nz, .giovanni
	lb bc, TM_FIRE_BLAST, 1
	call GiveItem
	jr nc, .giovanni
	SetEvent EVENT_GOT_TM38
.giovanni
	CheckEvent EVENT_BEAT_VIRIDIAN_GYM_GIOVANNI
	ret z
	ld hl, wObtainedBadges
	set BIT_EARTHBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_EARTHBADGE, [hl]
	CheckEvent EVENT_GOT_TM27
	ret nz
	lb bc, TM_FISSURE, 1
	call GiveItem
	ret nc
	SetEvent EVENT_GOT_TM27
	ret
''')

print("Battle Hub source patch applied")
