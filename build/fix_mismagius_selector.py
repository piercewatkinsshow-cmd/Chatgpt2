from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'hack')
match_file = None
for p in root.rglob('*.asm'):
    try:
        s = p.read_text()
    except UnicodeDecodeError:
        continue
    if re.search(r'(?m)^DisplayStarterMenu:(?!:)', s):
        match_file = p
        break

if match_file is None:
    raise SystemExit('Could not locate single-colon DisplayStarterMenu label')

s = match_file.read_text()
s = re.sub(r'(?m)^DisplayStarterMenu:(?!:)', 'DisplayStarterMenuOriginal::', s, count=1)
s += r'''

; Battle Hub expansion wrapper: original 151 choices + dedicated Mismagius.
DisplayStarterMenu::
	call DisplayStarterMenuOriginal
	call ClearScreen
	hlcoord 1, 7
	ld de, BattleHubMismagiusChoiceText
	call PlaceString
	call UpdateSprites
	call YesNoChoice
	ld a, [wCurrentMenuItem]
	and a
	ret nz
	ld a, MISMAGIUS
	ld [wCustomStarterInternalID], a
	ld a, DEX_GENGAR
	ld [wCustomStarterDexID], a
	ret

BattleHubMismagiusChoiceText:
	db "MISMAGIUS INSTEAD?@"
'''
match_file.write_text(s)
print('Wrapped selector:', match_file.relative_to(root))
