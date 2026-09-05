from pathlib import Path
import subprocess,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else 'hack')
subprocess.run([sys.executable,str(Path(__file__).with_name('patch_battlehub_future_league_v2.py')),str(root)],check=True)
p=root/'engine/battle/read_trainer_party.asm'
s=p.read_text()
old='\tld a, PARTYMON_STRUCT_LENGTH - 4'
if old not in s: raise SystemExit('custom move stride marker missing')
p.write_text(s.replace(old,'\tld a, 40',1))
print('Fixed Gen I party-mon move stride (44-byte struct, +40 after 4-byte move copy)')