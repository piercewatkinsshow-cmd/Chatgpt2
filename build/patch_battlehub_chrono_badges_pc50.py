from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "hack")
base = Path(__file__).with_name("patch_battlehub_chrono_nooak.py")
subprocess.run([sys.executable, str(base), str(root)], check=True)

# ---------------------------------------------------------------------------
# PC STOCK: ALL NORMALLY PURCHASABLE TMs x50
# ---------------------------------------------------------------------------
# Pokemon Blue's Celadon Dept. Store 2F sells nine TMs:
# TM01, TM02, TM05, TM07, TM09, TM17, TM32, TM33 and TM37.
# TM01 was previously in the starting Bag; move it into the PC so all nine
# purchasable TMs are together there at quantity 50.
p = root / "engine/movie/oak_speech/oak_speech.asm"
s = p.read_text()

old = "BattleHubBagItems:\n\tdb 12\n"
new = "BattleHubBagItems:\n\tdb 11\n"
if old not in s:
    raise SystemExit("BattleHub bag count not found")
s = s.replace(old, new, 1)

old = "\tdb TM_FLASH, 1\n\tdb TM_MEGA_PUNCH, 1\n\tdb $ff\nBattleHubBagItemsEnd:"
# The HM constant is HM_FLASH, not TM_FLASH; handle the actual source below.
if old in s:
    s = s.replace(old, "\tdb TM_FLASH, 1\n\tdb $ff\nBattleHubBagItemsEnd:", 1)
else:
    old = "\tdb HM_FLASH, 1\n\tdb TM_MEGA_PUNCH, 1\n\tdb $ff\nBattleHubBagItemsEnd:"
    if old not in s:
        raise SystemExit("TM01 bag entry not found")
    s = s.replace(old, "\tdb HM_FLASH, 1\n\tdb $ff\nBattleHubBagItemsEnd:", 1)

old = "BattleHubPCItems:\n\tdb 41\n"
new = "BattleHubPCItems:\n\tdb 42\n\tdb TM_MEGA_PUNCH, 50\n"
if old not in s:
    raise SystemExit("BattleHub PC count not found")
s = s.replace(old, new, 1)

for tm in [
    "TM_DOUBLE_TEAM",
    "TM_REFLECT",
    "TM_RAZOR_WIND",
    "TM_HORN_DRILL",
    "TM_EGG_BOMB",
    "TM_MEGA_KICK",
    "TM_TAKE_DOWN",
    "TM_SUBMISSION",
]:
    old = f"\tdb {tm}, 1"
    new = f"\tdb {tm}, 50"
    if old not in s:
        raise SystemExit(f"PC TM entry not found: {tm}")
    s = s.replace(old, new, 1)
p.write_text(s)

# ---------------------------------------------------------------------------
# RELIABLE ONE-TIME TRAINERS + DIRECT GYM REWARDS
# ---------------------------------------------------------------------------
# Re-select the exact trainer header after each battle so EndTrainerBattle sets
# the correct defeated-event flag. That flag makes all 13 opponents permanently
# non-battleable after a victory.
#
# Gym badges and their original TM rewards are awarded immediately from this
# same post-battle handler, based on the actual opponent class. This avoids the
# old polling routine that could miss/mis-associate rewards on the custom map.
p = root / "scripts/IndigoPlateauLobby.asm"
s = p.read_text()

old = "\tcall BattleHubAwardGymRewards\n"
if old not in s:
    raise SystemExit("old polling reward call not found")
s = s.replace(old, "", 1)

old = "\tdw EndTrainerBattle\n"
if old not in s:
    raise SystemExit("EndTrainerBattle script pointer not found")
s = s.replace(old, "\tdw BattleHubEndTrainerBattle\n", 1)

insert_at = s.find("IndigoPlateauLobby_TextPointers:\n")
if insert_at < 0:
    raise SystemExit("text pointer insertion point not found")

handler = r'''BattleHubEndTrainerBattle:
	; Select the exact trainer header from the opponent class.
	ld a, [wEnemyMonOrTrainerClass]
	cp OPP_BROCK
	jp z, .brockHeader
	cp OPP_MISTY
	jp z, .mistyHeader
	cp OPP_LT_SURGE
	jp z, .surgeHeader
	cp OPP_ERIKA
	jp z, .erikaHeader
	cp OPP_KOGA
	jp z, .kogaHeader
	cp OPP_SABRINA
	jp z, .sabrinaHeader
	cp OPP_BLAINE
	jp z, .blaineHeader
	cp OPP_GIOVANNI
	jp z, .giovanniHeader
	cp OPP_LORELEI
	jp z, .loreleiHeader
	cp OPP_BRUNO
	jp z, .brunoHeader
	cp OPP_AGATHA
	jp z, .agathaHeader
	cp OPP_LANCE
	jp z, .lanceHeader
	ld hl, BattleHubTrainerHeader12
	jp .haveHeader
.brockHeader
	ld hl, BattleHubTrainerHeader0
	jp .haveHeader
.mistyHeader
	ld hl, BattleHubTrainerHeader1
	jp .haveHeader
.surgeHeader
	ld hl, BattleHubTrainerHeader2
	jp .haveHeader
.erikaHeader
	ld hl, BattleHubTrainerHeader3
	jp .haveHeader
.kogaHeader
	ld hl, BattleHubTrainerHeader4
	jp .haveHeader
.sabrinaHeader
	ld hl, BattleHubTrainerHeader5
	jp .haveHeader
.blaineHeader
	ld hl, BattleHubTrainerHeader6
	jp .haveHeader
.giovanniHeader
	ld hl, BattleHubTrainerHeader7
	jp .haveHeader
.loreleiHeader
	ld hl, BattleHubTrainerHeader8
	jp .haveHeader
.brunoHeader
	ld hl, BattleHubTrainerHeader9
	jp .haveHeader
.agathaHeader
	ld hl, BattleHubTrainerHeader10
	jp .haveHeader
.lanceHeader
	ld hl, BattleHubTrainerHeader11
.haveHeader
	call StoreTrainerHeaderPointer
	ld a, [wBattleResult]
	push af
	call EndTrainerBattle
	pop af
	and a
	ret nz ; no badge/TM on a loss

	; Award gym rewards immediately from the actual opponent class.
	ld a, [wEnemyMonOrTrainerClass]
	cp OPP_BROCK
	jp z, .awardBrock
	cp OPP_MISTY
	jp z, .awardMisty
	cp OPP_LT_SURGE
	jp z, .awardSurge
	cp OPP_ERIKA
	jp z, .awardErika
	cp OPP_KOGA
	jp z, .awardKoga
	cp OPP_SABRINA
	jp z, .awardSabrina
	cp OPP_BLAINE
	jp z, .awardBlaine
	cp OPP_GIOVANNI
	jp z, .awardGiovanni
	ret ; Elite Four / Champion: defeated flag only

.awardBrock
	ld hl, wObtainedBadges
	set BIT_BOULDERBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_BOULDERBADGE, [hl]
	CheckEvent EVENT_GOT_TM34
	ret nz
	lb bc, TM_BIDE, 1
	call GiveItem
	ret nc
	SetEvent EVENT_GOT_TM34
	ret
.awardMisty
	ld hl, wObtainedBadges
	set BIT_CASCADEBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_CASCADEBADGE, [hl]
	CheckEvent EVENT_GOT_TM11
	ret nz
	lb bc, TM_BUBBLEBEAM, 1
	call GiveItem
	ret nc
	SetEvent EVENT_GOT_TM11
	ret
.awardSurge
	ld hl, wObtainedBadges
	set BIT_THUNDERBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_THUNDERBADGE, [hl]
	CheckEvent EVENT_GOT_TM24
	ret nz
	lb bc, TM_THUNDERBOLT, 1
	call GiveItem
	ret nc
	SetEvent EVENT_GOT_TM24
	ret
.awardErika
	ld hl, wObtainedBadges
	set BIT_RAINBOWBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_RAINBOWBADGE, [hl]
	CheckEvent EVENT_GOT_TM21
	ret nz
	lb bc, TM_MEGA_DRAIN, 1
	call GiveItem
	ret nc
	SetEvent EVENT_GOT_TM21
	ret
.awardKoga
	ld hl, wObtainedBadges
	set BIT_SOULBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_SOULBADGE, [hl]
	CheckEvent EVENT_GOT_TM06
	ret nz
	lb bc, TM_TOXIC, 1
	call GiveItem
	ret nc
	SetEvent EVENT_GOT_TM06
	ret
.awardSabrina
	ld hl, wObtainedBadges
	set BIT_MARSHBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_MARSHBADGE, [hl]
	CheckEvent EVENT_GOT_TM46
	ret nz
	lb bc, TM_PSYWAVE, 1
	call GiveItem
	ret nc
	SetEvent EVENT_GOT_TM46
	ret
.awardBlaine
	ld hl, wObtainedBadges
	set BIT_VOLCANOBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_VOLCANOBADGE, [hl]
	CheckEvent EVENT_GOT_TM38
	ret nz
	lb bc, TM_FIRE_BLAST, 1
	call GiveItem
	ret nc
	SetEvent EVENT_GOT_TM38
	ret
.awardGiovanni
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

'''

s = s[:insert_at] + handler + s[insert_at:]
p.write_text(s)

print("Applied direct one-time Battle Hub rewards")
print("All 13 trainers: one battle after a win")
print("Gym badges/TMs: awarded immediately in post-battle handler")
print("All nine Celadon purchasable TMs are in the PC at quantity 50")
