from pathlib import Path
import subprocess,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else 'hack')
subprocess.run([sys.executable,str(Path(__file__).with_name('patch_battlehub_future_league_v5_sprites.py')),str(root)],check=True)

# Replace Bill's PC entry with an all-151 Pokemon catalog while keeping the
# player's item PC available as the second menu option.
p=root/'engine/menus/pc.asm';s=p.read_text()
old='\tfarcall BillsPC_\nReloadMainMenu:'
new='\tfarcall BattleHubPokemonCatalog\nReloadMainMenu:'
if old not in s: raise SystemExit('BillsPC farcall hook not found')
p.write_text(s.replace(old,new,1))

# Rename the first PC menu entry so it is obvious what it does.
p=root/'engine/pokemon/bills_pc.asm';s=p.read_text()
s=s.replace('SomeonesPCText:   db "SOMEONE\'s PC@"','SomeonesPCText:   db "POKEMON PC@"',1)
s=s.replace('BillsPCText:      db "BILL\'s PC@"','BillsPCText:      db "POKEMON PC@"',1)
p.write_text(s)

# Make the existing 151-species selector serve as the catalog UI.
p=root/'custom_starter/custom_starter_menu.asm';s=p.read_text()
s=s.replace('db "STARTER SPECIES@"','db "POKEMON SPECIES@"',1)
s=s.replace('db "(ENC. PRESS SEL.)@"','db "START=TAKE B=BACK@"',1)

catalog=r'''\n\nBattleHubPokemonCatalog::
\t; Reuse the stable alphabetical 151-species selector already present in
\t; this fork. START confirms; B/A/SELECT return without taking a Pokemon.
\tcall ClearScreen
\tcall LoadTextBoxTilePatterns
\tld a, $f
\tld hl, wCustomStarterAtkDV
\tld [hli], a
\tld [hli], a
\tld [hli], a
\tld [hl], a
\tcall DisplayStarterMenu
\tldh a, [hJoy5]
\tbit BIT_START, a
\tret z

\t; Force the catalog selection to level 5.
\tld a, [wCustomStarterInternalID]
\tld b, a
\tld c, 5
\tcall GivePokemon
\tjr nc, .done

\t; Give every catalog Pokemon perfect Gen I DVs (15/15/15/15).
\tld a, [wAddedToParty]
\tand a
\tjr z, .boxMon
.partyMon
\tld a, [wPartyCount]
\tdec a
\tld hl, wPartyMon1DVs
\tld bc, PARTYMON_STRUCT_LENGTH
\tcall AddNTimes
\tld a, $ff
\tld [hli], a
\tld [hl], a
\tjr .done
.boxMon
\tld a, [wBoxCount]
\tdec a
\tld hl, wBoxMon1DVs
\tld bc, BOXMON_STRUCT_LENGTH
\tcall AddNTimes
\tld a, $ff
\tld [hli], a
\tld [hl], a
.done
\tret
'''
s += catalog
p.write_text(s)
print('Added all-151 Pokemon PC catalog: START takes selected level-5 perfect-DV Pokemon')