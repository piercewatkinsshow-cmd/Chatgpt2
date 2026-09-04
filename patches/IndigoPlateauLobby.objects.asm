object_const_def
const_export BATTLEHUB_BROCK
const_export BATTLEHUB_MISTY
const_export BATTLEHUB_LT_SURGE
const_export BATTLEHUB_ERIKA
const_export BATTLEHUB_KOGA
const_export BATTLEHUB_SABRINA
const_export BATTLEHUB_BLAINE
const_export BATTLEHUB_GIOVANNI
const_export BATTLEHUB_LORELEI
const_export BATTLEHUB_BRUNO
const_export BATTLEHUB_AGATHA
const_export BATTLEHUB_LANCE
const_export BATTLEHUB_CHAMPION
const_export BATTLEHUB_NURSE
const_export BATTLEHUB_PC

IndigoPlateauLobby_Object:
	db $0 ; border block

	def_warp_events

	def_bg_events

	def_object_events
	object_event  2,  2, SPRITE_GYM_GUIDE,     STAY, DOWN,  1, OPP_BROCK,     1
	object_event  5,  2, SPRITE_GIRL,          STAY, DOWN,  2, OPP_MISTY,     1
	object_event  8,  2, SPRITE_GYM_GUIDE,     STAY, DOWN,  3, OPP_LT_SURGE,  1
	object_event 11,  2, SPRITE_GIRL,          STAY, DOWN,  4, OPP_ERIKA,     1
	object_event  2,  5, SPRITE_GYM_GUIDE,     STAY, DOWN,  5, OPP_KOGA,      1
	object_event  5,  5, SPRITE_GIRL,          STAY, DOWN,  6, OPP_SABRINA,   1
	object_event  8,  5, SPRITE_GYM_GUIDE,     STAY, DOWN,  7, OPP_BLAINE,    1
	object_event 11,  5, SPRITE_GYM_GUIDE,     STAY, DOWN,  8, OPP_GIOVANNI,  1
	object_event  2,  8, SPRITE_COOLTRAINER_F, STAY, DOWN,  9, OPP_LORELEI,   1
	object_event  5,  8, SPRITE_GYM_GUIDE,     STAY, DOWN, 10, OPP_BRUNO,     1
	object_event  8,  8, SPRITE_CHANNELER,     STAY, DOWN, 11, OPP_AGATHA,    1
	object_event 11,  8, SPRITE_GYM_GUIDE,     STAY, DOWN, 12, OPP_LANCE,     1
	object_event  7,  1, SPRITE_GYM_GUIDE,     STAY, DOWN, 13, OPP_RIVAL3,    1
	object_event  4, 10, SPRITE_NURSE,         STAY, DOWN, 14
	object_event 10, 10, SPRITE_CLERK,         STAY, DOWN, 15

	def_warps_to INDIGO_PLATEAU_LOBBY
