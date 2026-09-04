from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "hack")
base = Path(__file__).with_name("patch_battlehub_chrono_nooak.py")
subprocess.run([sys.executable, str(base), str(root)], check=True)

# ---------------------------------------------------------------------------
# PC STOCK: ALL NORMALLY PURCHASABLE TMs x50
# ---------------------------------------------------------------------------
# In Pokemon Blue, Celadon Mart 2F sells these nine TMs. Keep all other
# non-gym TMs at quantity 1, but make every purchasable TM a stack of 50.
p = root / "engine/movie/oak_speech/oak_speech.asm"
s = p.read_text()
for tm in [
    "TM_DOUBLE_TEAM",
    "TM_REFLECT",
    "TM_RAZOR_WIND",
    "TM_HORN_DRILL",
    "TM_EGG_BOMB",
    "TM_MEGA_PUNCH",
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
# The prior hub used the generic EndTrainerBattle script while the map's base
# trainer-header pointer was always header 0. That makes the defeated-event
# bookkeeping fragile on a custom map containing unrelated event flags.
#
# This handler identifies the opponent class, restores the exact trainer header
# for that opponent, then calls EndTrainerBattle. That makes its normal defeated
# flag permanent, so every trainer can only be fought once.
#
# After a win, each Gym Leader immediately sets its badge and gives its original
# TM reward in the same post-battle handler. No polling of beat-event flags is
# needed anymore.
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
	; Re-select the exact trainer header from the opponent class. This ensures
	; EndTrainerBattle sets the correct one-time defeated event.
	ld a, [wEnemyMonOrTrainerClass]
	cp OPP_BROCK
	jr z, .brockHeader
	cp OPP_MISTY
	jr z, .mistyHeader
	cp OPP_LT_SURGE
	jr z, .surgeHeader
	cp OPP_ERIKA
	jr z, .erikaHeader
	cp OPP_KOGA
	jr z, .kogaHeader
	cp OPP_SABRINA
	jr z, .sabrinaHeader
	cp OPP_BLAINE
	jr z, .blaineHeader
	cp OPP_GIOVANNI
	jr z, .giovanniHeader
	cp OPP_LORELEI
	jr z, .loreleiHeader
	cp OPP_BRUNO
	jr z, .brunoHeader
	cp OPP_AGATHA
	jr z, .agathaHeader
	cp OPP_LANCE
	jr z, .lanceHeader
	ld hl, BattleHubTrainerHeader12
	jr .haveHeader
.brockHeader
	ld hl, BattleHubTrainerHeader0
	jr .haveHeader
.mistyHeader
	ld hl, BattleHubTrainerHeader1
	jr .haveHeader
.surgeHeader
	ld hl, BattleHubTrainerHeader2
	jr .haveHeader
.erikaHeader
	ld hl, BattleHubTrainerHeader3
	jr .haveHeader
.kogaHeader
	ld hl, BattleHubTrainerHeader4
	jr .haveHeader
.sabrinaHeader
	ld hl, BattleHubTrainerHeader5
	jr .haveHeader
.blaineHeader
	ld hl, BattleHubTrainerHeader6
	jr .haveHeader
.giovanniHeader
	ld hl, BattleHubTrainerHeader7
	jr .haveHeader
.loreleiHeader
	ld hl, BattleHubTrainerHeader8
	jr .haveHeader
.brunoHeader
	ld hl, BattleHubTrainerHeader9
	jr .haveHeader
.agathaHeader
	ld hl, BattleHubTrainerHeader10
	jr .haveHeader
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
	jr z, .awardBrock
	cp OPP_MISTY
	jr z, .awardMisty
	cp OPP_LT_SURGE
	jr z, .awardSurge
	cp OPP_ERIKA
	jr z, .awardErika
	cp OPP_KOGA
	jr z, .awardKoga
	cp OPP_SABRINA
	jr z, .awardSabrina
	cp OPP_BLAINE
	jr z, .awardBlaine
	cp OPP_GIOVANNI
	jr z, .awardGiovanni
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
print("Purchasable Celadon Mart TMs in PC: quantity 50 each")
