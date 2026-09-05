from pathlib import Path
import subprocess,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else 'hack')
subprocess.run([sys.executable,str(Path(__file__).with_name('patch_battlehub_future_league_v3.py')),str(root)],check=True)

# Overworld sprites: use exact Gen I character sprites where they exist, and
# the closest sensible stock Gen I sprite for characters without one.
p=root/'data/maps/objects/IndigoPlateauLobby.asm';s=p.read_text()
repls={
'object SPRITE_SUPER_NERD,        5,  9':'object SPRITE_COOLTRAINER_M,     5,  9', # Tracey
'object SPRITE_BRUNETTE_GIRL,    10, 14':'object SPRITE_GUARD,            10, 14', # Samurai
'object SPRITE_SUPER_NERD,        5, 29':'object SPRITE_SUPER_NERD,        5, 29', # Brock (stock gym-like)
'object SPRITE_COOLTRAINER_M,    10, 44':'object SPRITE_BLUE,             10, 44', # Gary
'object SPRITE_COOLTRAINER_F,     5, 49':'object SPRITE_KOGA,              5, 49', # Koga
'object SPRITE_COOLTRAINER_M,    10, 54':'object SPRITE_LORELEI,          10, 54', # Lorelei
'object SPRITE_COOLTRAINER_F,     5, 59':'object SPRITE_GIOVANNI,          5, 59', # Giovanni
'object SPRITE_COOLTRAINER_M,    10, 64':'object SPRITE_BRUNETTE_GIRL,    10, 64', # Misty
'object SPRITE_BLUE,              7, 68':'object SPRITE_RED,               7, 68', # Ash
}
for a,b in repls.items():
 if a not in s: raise SystemExit('missing overworld '+a)
 s=s.replace(a,b,1)
p.write_text(s)

# In-battle portraits. Repoint the repurposed trainer classes to portraits
# matching the Future League identity. Existing unchanged leaders keep theirs.
p=root/'data/trainers/pic_pointers_money.asm';s=p.read_text()
repls={
'pic_money BrockPic,        9900':'pic_money JrTrainerMPic,   9900', # Tracey
'pic_money MistyPic,        9900':'pic_money BugCatcherPic,   9900', # Samurai
'pic_money KogaPic,         9900':'pic_money BrockPic,        9900', # Brock
'pic_money GiovanniPic,     9900':'pic_money Rival3Pic,       9900', # Gary
'pic_money LoreleiPic,      9900':'pic_money KogaPic,         9900', # Koga
'pic_money BrunoPic,        9900':'pic_money LoreleiPic,      9900', # Lorelei
'pic_money AgathaPic,       9900':'pic_money GiovanniPic,     9900', # Giovanni
'pic_money LancePic,        9900':'pic_money MistyPic,        9900', # Misty
'pic_money Rival3Pic,       9900':'pic_money JrTrainerMPic,   9900', # Ash: closest stock young-male portrait
}
for a,b in repls.items():
 if a not in s: raise SystemExit('missing battle pic '+a)
 s=s.replace(a,b,1)
p.write_text(s)
print('Future League overworld and battle sprites corrected')