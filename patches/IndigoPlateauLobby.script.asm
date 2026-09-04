IndigoPlateauLobby_Script:
	call Serial_TryEstablishingExternallyClockedConnection
	call EnableAutoTextBoxDrawing

	ld a, [wPartyCount]
	and a
	call z, BattleHubChooseStarter

	ld a, [wCurMapScript]
	and a
	ret z
	xor a
	ld [wCurMapScript], a
	jp BattleHubPostBattle

IndigoPlateauLobby_TextPointers:
	def_text_pointers
	dw BattleHubBrockText
	dw BattleHubMistyText
	dw BattleHubLtSurgeText
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

BattleHubBrockText:
	text_asm
	ld a, [wObtainedBadges]
	bit BIT_BOULDERBADGE, a
	jp nz, BattleHubPrintAlready
	ld a, 1
	call BattleHubStartBoss
	jp TextScriptEnd

BattleHubMistyText:
	text_asm
	ld a, [wObtainedBadges]
	bit BIT_CASCADEBADGE, a
	jp nz, BattleHubPrintAlready
	bit BIT_BOULDERBADGE, a
	jp z, BattleHubPrintLocked
	ld a, 2
	call BattleHubStartBoss
	jp TextScriptEnd

BattleHubLtSurgeText:
	text_asm
	ld a, [wObtainedBadges]
	bit BIT_THUNDERBADGE, a
	jp nz, BattleHubPrintAlready
	bit BIT_CASCADEBADGE, a
	jp z, BattleHubPrintLocked
	ld a, 3
	call BattleHubStartBoss
	jp TextScriptEnd

BattleHubErikaText:
	text_asm
	ld a, [wObtainedBadges]
	bit BIT_RAINBOWBADGE, a
	jp nz, BattleHubPrintAlready
	bit BIT_THUNDERBADGE, a
	jp z, BattleHubPrintLocked
	ld a, 4
	call BattleHubStartBoss
	jp TextScriptEnd

BattleHubKogaText:
	text_asm
	ld a, [wObtainedBadges]
	bit BIT_SOULBADGE, a
	jp nz, BattleHubPrintAlready
	bit BIT_RAINBOWBADGE, a
	jp z, BattleHubPrintLocked
	ld a, 5
	call BattleHubStartBoss
	jp TextScriptEnd

BattleHubSabrinaText:
	text_asm
	ld a, [wObtainedBadges]
	bit BIT_MARSHBADGE, a
	jp nz, BattleHubPrintAlready
	bit BIT_SOULBADGE, a
	jp z, BattleHubPrintLocked
	ld a, 6
	call BattleHubStartBoss
	jp TextScriptEnd

BattleHubBlaineText:
	text_asm
	ld a, [wObtainedBadges]
	bit BIT_VOLCANOBADGE, a
	jp nz, BattleHubPrintAlready
	bit BIT_MARSHBADGE, a
	jp z, BattleHubPrintLocked
	ld a, 7
	call BattleHubStartBoss
	jp TextScriptEnd

BattleHubGiovanniText:
	text_asm
	ld a, [wObtainedBadges]
	bit BIT_EARTHBADGE, a
	jp nz, BattleHubPrintAlready
	bit BIT_VOLCANOBADGE, a
	jp z, BattleHubPrintLocked
	ld a, 8
	call BattleHubStartBoss
	jp TextScriptEnd

BattleHubLoreleiText:
	text_asm
	CheckEvent EVENT_BEAT_SAFFRON_GYM_TRAINER_0
	jp nz, BattleHubPrintAlready
	ld a, [wObtainedBadges]
	cp $ff
	jp nz, BattleHubPrintLocked
	ld a, 9
	call BattleHubStartBoss
	jp TextScriptEnd

BattleHubBrunoText:
	text_asm
	CheckEvent EVENT_BEAT_SAFFRON_GYM_TRAINER_1
	jp nz, BattleHubPrintAlready
	CheckEvent EVENT_BEAT_SAFFRON_GYM_TRAINER_0
	jp z, BattleHubPrintLocked
	ld a, 10
	call BattleHubStartBoss
	jp TextScriptEnd

BattleHubAgathaText:
	text_asm
	CheckEvent EVENT_BEAT_SAFFRON_GYM_TRAINER_2
	jp nz, BattleHubPrintAlready
	CheckEvent EVENT_BEAT_SAFFRON_GYM_TRAINER_1
	jp z, BattleHubPrintLocked
	ld a, 11
	call BattleHubStartBoss
	jp TextScriptEnd

BattleHubLanceText:
	text_asm
	CheckEvent EVENT_BEAT_SAFFRON_GYM_TRAINER_3
	jp nz, BattleHubPrintAlready
	CheckEvent EVENT_BEAT_SAFFRON_GYM_TRAINER_2
	jp z, BattleHubPrintLocked
	ld a, 12
	call BattleHubStartBoss
	jp TextScriptEnd

BattleHubChampionText:
	text_asm
	CheckEvent EVENT_BEAT_SAFFRON_GYM_TRAINER_4
	jp nz, BattleHubPrintChampionDone
	CheckEvent EVENT_BEAT_SAFFRON_GYM_TRAINER_3
	jp z, BattleHubPrintLocked
	ld a, 13
	call BattleHubStartBoss
	jp TextScriptEnd

BattleHubNurseText:
	script_pokecenter_nurse

BattleHubPCText:
	script_pokecenter_pc

BattleHubPrintAlready:
	ld hl, BattleHubAlreadyText
	call PrintText
	jp TextScriptEnd

BattleHubPrintLocked:
	ld hl, BattleHubLockedText
	call PrintText
	jp TextScriptEnd

BattleHubPrintChampionDone:
	ld hl, BattleHubChampionDoneText
	call PrintText
	jp TextScriptEnd

BattleHubStartBoss:
	ld [wUnusedPlayerDataByte], a
	ld hl, BattleHubChallengeText
	call PrintText
	ld hl, wStatusFlags3
	set BIT_TALKED_TO_TRAINER, [hl]
	set BIT_PRINT_END_BATTLE_TEXT, [hl]
	ld hl, BattleHubBossEndText
	ld de, BattleHubBossEndText
	call SaveEndBattleTextPointers
	ldh a, [hSpriteIndex]
	ld [wSpriteIndex], a
	call EngageMapTrainer
	call InitBattleEnemyParameters
	ld a, [wUnusedPlayerDataByte]
	cp 9
	jr nc, .notGym
	ld [wGymLeaderNo], a
	jr .setScript
.notGym
	xor a
	ld [wGymLeaderNo], a
.setScript
	ld a, 1
	ld [wCurMapScript], a
	ret

BattleHubPostBattle:
	ld a, [wIsInBattle]
	cp LOST_BATTLE
	jr z, .lost
	ld a, [wUnusedPlayerDataByte]
	cp 1
	jr z, .brock
	cp 2
	jr z, .misty
	cp 3
	jr z, .surge
	cp 4
	jr z, .erika
	cp 5
	jr z, .koga
	cp 6
	jr z, .sabrina
	cp 7
	jr z, .blaine
	cp 8
	jr z, .giovanni
	cp 9
	jr z, .lorelei
	cp 10
	jr z, .bruno
	cp 11
	jr z, .agatha
	cp 12
	jr z, .lance
	cp 13
	jr z, .champion
	ret

.brock
	ld hl, wObtainedBadges
	set BIT_BOULDERBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_BOULDERBADGE, [hl]
	ld a, TM_BIDE
	call BattleHubSendTMToPC
	jr .gymReward
.misty
	ld hl, wObtainedBadges
	set BIT_CASCADEBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_CASCADEBADGE, [hl]
	ld a, TM_BUBBLEBEAM
	call BattleHubSendTMToPC
	jr .gymReward
.surge
	ld hl, wObtainedBadges
	set BIT_THUNDERBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_THUNDERBADGE, [hl]
	ld a, TM_THUNDERBOLT
	call BattleHubSendTMToPC
	jr .gymReward
.erika
	ld hl, wObtainedBadges
	set BIT_RAINBOWBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_RAINBOWBADGE, [hl]
	ld a, TM_MEGA_DRAIN
	call BattleHubSendTMToPC
	jr .gymReward
.koga
	ld hl, wObtainedBadges
	set BIT_SOULBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_SOULBADGE, [hl]
	ld a, TM_TOXIC
	call BattleHubSendTMToPC
	jr .gymReward
.sabrina
	ld hl, wObtainedBadges
	set BIT_MARSHBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_MARSHBADGE, [hl]
	ld a, TM_PSYWAVE
	call BattleHubSendTMToPC
	jr .gymReward
.blaine
	ld hl, wObtainedBadges
	set BIT_VOLCANOBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_VOLCANOBADGE, [hl]
	ld a, TM_FIRE_BLAST
	call BattleHubSendTMToPC
	jr .gymReward
.giovanni
	ld hl, wObtainedBadges
	set BIT_EARTHBADGE, [hl]
	ld hl, wBeatGymFlags
	set BIT_EARTHBADGE, [hl]
	ld a, TM_FISSURE
	call BattleHubSendTMToPC
.gymReward
	ld hl, BattleHubGymRewardText
	call PrintText
	ret

.lorelei
	SetEvent EVENT_BEAT_SAFFRON_GYM_TRAINER_0
	jr .eliteReward
.bruno
	SetEvent EVENT_BEAT_SAFFRON_GYM_TRAINER_1
	jr .eliteReward
.agatha
	SetEvent EVENT_BEAT_SAFFRON_GYM_TRAINER_2
	jr .eliteReward
.lance
	SetEvent EVENT_BEAT_SAFFRON_GYM_TRAINER_3
.eliteReward
	ld hl, BattleHubEliteWinText
	call PrintText
	ret

.champion
	SetEvent EVENT_BEAT_SAFFRON_GYM_TRAINER_4
	ld hl, BattleHubChampionWinText
	call PrintText
	ret

.lost
	ld hl, BattleHubLostText
	call PrintText
	ret

BattleHubSendTMToPC:
	ld [wCurItem], a
	ld a, 1
	ld [wItemQuantity], a
	ld hl, wNumBoxItems
	call AddItemToInventory
	ret

BattleHubChooseStarter:
	call GBPalWhiteOut
	call ClearScreen
	call LoadTextBoxTilePatterns
	ld a, 1
	ld [wMaxItemQuantity], a
.loop
	call ClearScreen
	hlcoord 2, 2
	ld de, BattleHubStarterTitle
	call PlaceString
	hlcoord 2, 4
	ld de, BattleHubStarterHelp1
	call PlaceString
	hlcoord 2, 5
	ld de, BattleHubStarterHelp2
	call PlaceString
	hlcoord 2, 8
	ld de, wMaxItemQuantity
	lb bc, LEADING_ZEROES | 1, 3
	call PrintNumber

	ld a, [wMaxItemQuantity]
	ld [wPokedexNum], a
	callfar PokedexToIndex
	ld a, [wPokedexNum]
	ld [wNamedObjectIndex], a
	call GetMonName
	hlcoord 7, 8
	call PlaceString

	call Delay3
	call JoypadLowSensitivity
	ldh a, [hJoyPressed]
	bit B_PAD_A, a
	jr nz, .chosen
	bit B_PAD_UP, a
	jr nz, .up
	bit B_PAD_DOWN, a
	jr nz, .down
	bit B_PAD_RIGHT, a
	jr nz, .right
	bit B_PAD_LEFT, a
	jr nz, .left
	jr .loop
.up
	ld a, [wMaxItemQuantity]
	cp 151
	jr z, .loop
	inc a
	ld [wMaxItemQuantity], a
	jr .loop
.down
	ld a, [wMaxItemQuantity]
	cp 1
	jr z, .loop
	dec a
	ld [wMaxItemQuantity], a
	jr .loop
.right
	ld a, [wMaxItemQuantity]
	add 10
	cp 152
	jr c, .store
	ld a, 151
.store
	ld [wMaxItemQuantity], a
	jr .loop
.left
	ld a, [wMaxItemQuantity]
	sub 10
	jr nc, .leftNonZero
	ld a, 1
	jr .storeLeft
.leftNonZero
	and a
	jr nz, .storeLeft
	ld a, 1
.storeLeft
	ld [wMaxItemQuantity], a
	jr .loop
.chosen
	ld a, [wMaxItemQuantity]
	ld [wPokedexNum], a
	callfar PokedexToIndex
	ld a, [wPokedexNum]
	ld [wCurPartySpecies], a
	ld [wCurSpecies], a
	ld a, 5
	ld [wCurEnemyLevel], a
	ld a, $80
	ld [wMonDataLocation], a
	call AddPartyMon
	ld hl, wStatusFlags4
	set BIT_GOT_STARTER, [hl]
	call GBPalWhiteOutWithDelay3
	call ReloadMapData
	ret

BattleHubChallengeText:
	text "Your next boss"
	line "is ready!"
	text_end

BattleHubBossEndText:
	text "Excellent battle!"
	text_end

BattleHubAlreadyText:
	text "You already won"
	line "this battle."
	text_end

BattleHubLockedText:
	text "Defeat the previous"
	line "boss first."
	text_end

BattleHubGymRewardText:
	text "Badge earned!"
	line "The TM was sent"
	cont "to your PC."
	text_end

BattleHubEliteWinText:
	text "Elite Four victory!"
	line "The next battle"
	cont "is unlocked."
	text_end

BattleHubChampionWinText:
	text "YOU DID IT!"
	line "You defeated BLUE"
	cont "and became CHAMPION!"
	text_end

BattleHubChampionDoneText:
	text "You are already the"
	line "POKEMON CHAMPION!"
	text_end

BattleHubLostText:
	text "Heal up and try"
	line "again!"
	text_end

BattleHubStarterTitle:
	db "CHOOSE ANY #MON@"
BattleHubStarterHelp1:
	db "UP/DOWN = 1@"
BattleHubStarterHelp2:
	db "LEFT/RIGHT = 10   A=OK@"
