from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'hack')
match_file = None
pattern = re.compile(r'(?m)^\s*DisplayStarterMenu:(?!:)')
for p in root.rglob('*'):
    if not p.is_file() or '.git' in p.parts:
        continue
    try:
        s = p.read_text()
    except (UnicodeDecodeError, OSError):
        continue
    if pattern.search(s):
        match_file = p
        break

if match_file is None:
    candidates = []
    for p in root.rglob('*'):
        if not p.is_file() or '.git' in p.parts:
            continue
        try:
            s = p.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        if 'DisplayStarterMenu' in s:
            candidates.append(str(p.relative_to(root)))
    raise SystemExit('Could not locate selector definition. References: ' + ', '.join(candidates))

s = match_file.read_text()
s = pattern.sub('DisplayStarterMenuOriginal::', s, count=1)
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
