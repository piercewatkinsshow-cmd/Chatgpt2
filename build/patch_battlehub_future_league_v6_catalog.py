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

catalog='\n\n'+r'''BattleHubPokemonCatalog::
	; Reuse the stable alphabetical 151-species selector already present in
	; this fork. START confirms; B/A/SELECT return without taking a Pokemon.
	call ClearScreen
	call LoadTextBoxTilePatterns
	ld a, $f
	ld hl, wCustomStarterAtkDV
	ld [hli], a
	ld [hli], a
	ld [hli], a
	ld [hl], a
	call DisplayStarterMenu
	ldh a, [hJoy5]
	bit BIT_START, a
	ret z

	; Force the catalog selection to level 5.
	ld a, [wCustomStarterInternalID]
	ld b, a
	ld c, 5
	call GivePokemon
	jr nc, .done

	; Give every catalog Pokemon perfect Gen I DVs (15/15/15/15).
	ld a, [wAddedToParty]
	and a
	jr z, .boxMon
.partyMon
	ld a, [wPartyCount]
	dec a
	ld hl, wPartyMon1DVs
	ld bc, 44 ; party_struct = 33-byte box_struct + 11 party-only bytes
	call AddNTimes
	ld a, $ff
	ld [hli], a
	ld [hl], a
	jr .done
.boxMon
	ld a, [wNumInBox]
	dec a
	ld hl, wBoxMon1DVs
	ld bc, 33 ; BOX_STRUCT_LENGTH = 25 + NUM_MOVES*2 = 33
	call AddNTimes
	ld a, $ff
	ld [hli], a
	ld [hl], a
.done
	ret
'''
s += catalog
p.write_text(s)
print('Added all-151 Pokemon PC catalog: START takes selected level-5 perfect-DV Pokemon')