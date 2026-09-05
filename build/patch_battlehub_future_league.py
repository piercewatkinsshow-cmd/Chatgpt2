from pathlib import Path
import subprocess, sys, re

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'hack')
base = Path(__file__).with_name('patch_battlehub_chrono_badges_pc50.py')
subprocess.run([sys.executable, str(base), str(root)], check=True)

# Custom league parties. Keep the existing 13 unique trainer classes so the
# proven one-time battle / badge handler remains intact.
parties = {
 'BrockData': (1, '$FF, 12, VENONAT, 14, DODUO, 0'),
 'MistyData': (1, '$FF, 16, BUTTERFREE, 17, BEEDRILL, 19, PINSIR, 0'),
 'LtSurgeData': (1, '$FF, 23, VOLTORB, 24, PIKACHU, 26, MAGNETON, 28, RAICHU, 0'),
 'ErikaData': (1, '$FF, 29, TANGELA, 30, VICTREEBEL, 31, EXEGGUTOR, 33, VILEPLUME, 0'),
 'KogaData': (1, '$FF, 35, GRAVELER, 36, RHYDON, 37, KABUTOPS, 39, GOLEM, 0'),
 'SabrinaData': (1, '$FF, 40, MR_MIME, 41, HYPNO, 42, JYNX, 44, ALAKAZAM, 0'),
 'BlaineData': (1, '$FF, 44, NINETALES, 45, RAPIDASH, 47, MAGMAR, 49, ARCANINE, 0'),
 'GiovanniData': (3, '$FF, 49, PIDGEOT, 50, RHYDON, 51, EXEGGUTOR, 52, GYARADOS, 54, ALAKAZAM, 0'),
 'LoreleiData': (1, '$FF, 53, VENOMOTH, 54, MUK, 54, WEEZING, 55, GOLBAT, 57, TENTACRUEL, 0'),
 'BrunoData': (1, '$FF, 55, DEWGONG, 56, CLOYSTER, 56, SLOWBRO, 57, JYNX, 59, LAPRAS, 0'),
 'AgathaData': (1, '$FF, 57, PERSIAN, 58, DUGTRIO, 59, NIDOQUEEN, 60, NIDOKING, 61, RHYDON, 0'),
 'LanceData': (1, '$FF, 60, GOLDUCK, 61, TENTACRUEL, 62, VAPOREON, 63, LAPRAS, 64, STARMIE, 65, GYARADOS, 0'),
 'Rival3Data': (1, '$FF, 65, MUK, 66, GENGAR, 66, KINGLER, 67, SNORLAX, 68, CHARIZARD, 72, PIKACHU, 0'),
}
p = root/'data/trainers/parties.asm'; s=p.read_text()
for label,(nth,newdata) in parties.items():
    start=s.index(label+':'); end=s.find('\n\n',start)
    block=s[start:end]
    lines=block.splitlines(); seen=0
    for i,line in enumerate(lines):
        if line.lstrip().startswith('db '):
            seen += 1
            if seen == nth:
                lines[i]='\tdb '+newdata; break
    else: raise SystemExit(f'party entry missing: {label} #{nth}')
    s=s[:start]+'\n'.join(lines)+s[end:]
p.write_text(s)

# Rename the 13 class labels as they appear in battle. These classes are used
# only as identities for the hub opponents here; their party data above is the
# custom roster.
p=root/'data/trainers/names.asm'; s=p.read_text()
renames={
 '"BROCK"':'"TRACEY"','"MISTY"':'"SAMURAI"','"KOGA"':'"BROCK"',
 '"GIOVANNI"':'"GARY"','"LORELEI"':'"KOGA"','"BRUNO"':'"LORELEI"',
 '"AGATHA"':'"GIOVANNI"','"LANCE"':'"MISTY"','"RIVAL3"':'"ASH"'}
for a,b in renames.items():
    old='\tli '+a
    if old not in s: raise SystemExit('trainer name missing '+a)
    s=s.replace(old,'\tli '+b,1)
p.write_text(s)

# Exact requested moves. ReadTrainer normally derives trainer moves from each
# species' level-up list. Hook its finish path and overwrite the move bytes for
# these 13 hub classes after the party has been constructed.
moves={
 'OPP_BROCK': [['TACKLE','DISABLE','SUPERSONIC','CONFUSION'],['PECK','GROWL','FURY_ATTACK','QUICK_ATTACK']],
 'OPP_MISTY': [['CONFUSION','SLEEP_POWDER','STUN_SPORE','SUPERSONIC'],['TWINEEDLE','FURY_ATTACK','FOCUS_ENERGY','RAGE'],['VICEGRIP','SEISMIC_TOSS','BIND','FOCUS_ENERGY']],
 'OPP_LT_SURGE': [['SONICBOOM','SCREECH','LIGHT_SCREEN','SELFDESTRUCT'],['THUNDERSHOCK','THUNDER_WAVE','QUICK_ATTACK','DOUBLE_TEAM'],['THUNDERBOLT','THUNDER_WAVE','SUPERSONIC','SWIFT'],['THUNDERBOLT','THUNDER_WAVE','BODY_SLAM','MEGA_PUNCH']],
 'OPP_ERIKA': [['MEGA_DRAIN','SLEEP_POWDER','BIND','GROWTH'],['RAZOR_LEAF','SLEEP_POWDER','WRAP','ACID'],['PSYCHIC_M','HYPNOSIS','MEGA_DRAIN','STOMP'],['PETAL_DANCE','SLEEP_POWDER','MEGA_DRAIN','ACID']],
 'OPP_KOGA': [['ROCK_SLIDE','DIG','BODY_SLAM','SELFDESTRUCT'],['EARTHQUAKE','ROCK_SLIDE','STOMP','HORN_DRILL'],['SLASH','SURF','ICE_BEAM','SWORDS_DANCE'],['EARTHQUAKE','ROCK_SLIDE','BODY_SLAM','EXPLOSION']],
 'OPP_SABRINA': [['PSYCHIC_M','BARRIER','THUNDER_WAVE','SEISMIC_TOSS'],['PSYCHIC_M','HYPNOSIS','HEADBUTT','THUNDER_WAVE'],['LOVELY_KISS','BLIZZARD','PSYCHIC_M','BODY_SLAM'],['PSYCHIC_M','RECOVER','REFLECT','THUNDER_WAVE']],
 'OPP_BLAINE': [['FLAMETHROWER','CONFUSE_RAY','FIRE_SPIN','BODY_SLAM'],['FIRE_BLAST','STOMP','AGILITY','FIRE_SPIN'],['FIRE_PUNCH','PSYCHIC_M','CONFUSE_RAY','BODY_SLAM'],['FIRE_BLAST','BODY_SLAM','HYPER_BEAM','REFLECT']],
 'OPP_GIOVANNI': [['FLY','DOUBLE_EDGE','SAND_ATTACK','MIRROR_MOVE'],['EARTHQUAKE','ROCK_SLIDE','BODY_SLAM','SURF'],['PSYCHIC_M','SLEEP_POWDER','MEGA_DRAIN','EXPLOSION'],['SURF','BLIZZARD','THUNDERBOLT','HYPER_BEAM'],['PSYCHIC_M','RECOVER','THUNDER_WAVE','SEISMIC_TOSS']],
 'OPP_LORELEI': [['PSYCHIC_M','SLEEP_POWDER','MEGA_DRAIN','DOUBLE_TEAM'],['SLUDGE','BODY_SLAM','MINIMIZE','TOXIC'],['SLUDGE','THUNDERBOLT','SMOKESCREEN','EXPLOSION'],['WING_ATTACK','CONFUSE_RAY','TOXIC','MEGA_DRAIN'],['SURF','BLIZZARD','WRAP','TOXIC']],
 'OPP_BRUNO': [['SURF','BLIZZARD','REST','HEADBUTT'],['BLIZZARD','CLAMP','SUPERSONIC','EXPLOSION'],['SURF','PSYCHIC_M','AMNESIA','REST'],['LOVELY_KISS','BLIZZARD','PSYCHIC_M','BODY_SLAM'],['BLIZZARD','SURF','THUNDERBOLT','BODY_SLAM']],
 'OPP_AGATHA': [['SLASH','BUBBLEBEAM','THUNDERBOLT','BODY_SLAM'],['EARTHQUAKE','SLASH','ROCK_SLIDE','SAND_ATTACK'],['EARTHQUAKE','BLIZZARD','THUNDERBOLT','BODY_SLAM'],['EARTHQUAKE','THUNDERBOLT','BLIZZARD','HYPER_BEAM'],['EARTHQUAKE','ROCK_SLIDE','SURF','BODY_SLAM']],
 'OPP_LANCE': [['SURF','BLIZZARD','PSYCHIC_M','BODY_SLAM'],['SURF','BLIZZARD','WRAP','TOXIC'],['SURF','ICE_BEAM','ACID_ARMOR','REST'],['SURF','BLIZZARD','THUNDERBOLT','SING'],['SURF','PSYCHIC_M','THUNDERBOLT','RECOVER'],['HYDRO_PUMP','BLIZZARD','THUNDERBOLT','HYPER_BEAM']],
 'OPP_RIVAL3': [['SLUDGE','BODY_SLAM','MINIMIZE','EXPLOSION'],['PSYCHIC_M','THUNDERBOLT','HYPNOSIS','NIGHT_SHADE'],['CRABHAMMER','BLIZZARD','BODY_SLAM','SWORDS_DANCE'],['BODY_SLAM','EARTHQUAKE','REST','HYPER_BEAM'],['FIRE_BLAST','SLASH','EARTHQUAKE','SEISMIC_TOSS'],['THUNDERBOLT','THUNDER','QUICK_ATTACK','THUNDER_WAVE']],
}

p=root/'engine/battle/read_trainer_party.asm'; s=p.read_text()
needle='.FinishUp\n; clear wAmountMoneyWon addresses'
if needle not in s: raise SystemExit('ReadTrainer finish hook missing')
asm='''BattleHubApplyCustomMoves:\n\tld a, [wCurOpponent]\n'''
classes=list(moves)
for idx,cls in enumerate(classes):
    asm += f'\tcp {cls}\n\tjr z, .c{idx}\n'
asm += '\tret\n'
for idx,cls in enumerate(classes):
    flat=[m for mon in moves[cls] for m in mon]
    asm += f'.c{idx}\n'
    if cls=='OPP_GIOVANNI':
        asm += '\tld a, [wTrainerNo]\n\tcp 3\n\tret nz\n'
    elif cls=='OPP_RIVAL3':
        asm += '\tld a, [wTrainerNo]\n\tcp 1\n\tret nz\n'
    asm += f'\tld hl, .m{idx}\n\tld de, wEnemyMon1Moves\n\tld b, {len(moves[cls])}\n\tjr .copy\n'
    asm += f'.m{idx}\n\tdb '+', '.join(flat)+'\n'
asm += '''.copy\n\tpush bc\n\tld bc, 4\n\tcall CopyData\n\tpop bc\n\tld a, PARTYMON_STRUCT_LENGTH - 4\n\tadd e\n\tld e, a\n\tjr nc, .noCarry\n\tinc d\n.noCarry\n\tdec b\n\tjr nz, .copy\n\tret\n\n'''
s=s.replace(needle,'.FinishUp\n\tcall BattleHubApplyCustomMoves\n; clear wAmountMoneyWon addresses',1)
# Put routine after ReadTrainer so local labels do not collide with ReadTrainer locals.
s += '\n'+asm
p.write_text(s)

print('Applied Future Kanto League roster: Tracey through Ash')
print('Exact levels/species/moves installed; original proven hub systems preserved')
