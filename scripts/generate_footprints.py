#!/usr/bin/env python3
"""Generate CPC card-edge and EDAC socket footprints from dimensional inputs."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / 'reverseMX4.pretty'
LIB.mkdir(exist_ok=True)
(ROOT / 'fp-lib-table').write_text('(fp_lib_table (lib (name "reverseMX4") (type "KiCad") (uri "${KIPRJMOD}/reverseMX4.pretty") (options "") (descr "CPC edge backplane footprints")))\n')

sock = ['''(footprint "EDAC_395-050-521-204" (version 20241229) (generator "pcbnew") (layer "F.Cu")
  (descr "EDAC 395-050-521-204 50-contact vertical edge socket; 2.54mm pitch; 5.08mm row separation; Mfr mechanical dimensions require prototype fit check")
  (tags "CPC card edge EDAC 395") (attr through_hole)
  (property "Reference" "REF**" (at 30.48 -6 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
  (property "Value" "EDAC_395-050-521-204" (at 30.48 10 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
  (fp_rect (start -11.875 -1.905) (end 72.835 6.985) (stroke (width 0.12) (type solid)) (fill none) (layer "F.Fab"))
  (fp_rect (start -12.125 -2.155) (end 73.085 7.235) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))
  (fp_line (start -11.875 -1.905) (end 72.835 -1.905) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
''']
for i in range(25):
    x = round(i * 2.54, 2)
    sock.append(f'  (pad "{2*i+1}" thru_hole circle (at {x:.2f} 0) (size 1.70 1.70) (drill 1.10) (layers "*.Cu" "*.Mask"))')
    sock.append(f'  (pad "{2*i+2}" thru_hole circle (at {x:.2f} 5.08) (size 1.70 1.70) (drill 1.10) (layers "*.Cu" "*.Mask"))')
for x in (-8.575, 69.535):
    sock.append(f'  (pad "" np_thru_hole circle (at {x:.3f} 2.54) (size 3.96 3.96) (drill 3.96) (layers "*.Cu" "*.Mask"))')
sock.append('''  (model "${KIPRJMOD}/models/EDAC_395-050-521-204-preview.wrl"
    (offset (xyz 0 0 0))
    (scale (xyz 1 1 1))
    (rotate (xyz 0 0 0)))''')
sock.append(')')
(LIB / 'EDAC_395-050-521-204.kicad_mod').write_text('\n'.join(sock) + '\n')

# Tongue contact centres align with the EDAC socket's 25 positions. The bottom
# 6.9 mm of each face is a masked contact. It ends 0.6 mm before the board tip,
# while EDAC's nominal contact point lies about 4.06 mm behind that tip.
edge = ['''(footprint "CPC_Edge_2x25" (version 20241229) (generator "pcbnew") (layer "F.Cu")
  (descr "CPC 50-contact 2.54mm pitch card-edge tongue; 1.6mm board; odd contacts front, even contacts back")
  (tags "CPC card edge gold fingers") (attr smd)
  (property "Reference" "REF**" (at 30.48 -10 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
  (property "Value" "CPC_Edge_2x25" (at 30.48 -12 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
  (fp_line (start -2.54 -3.5) (end 63.50 -3.5) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
  (fp_text user "TOP: ODD 1..49" (at 30.48 -6 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
''']
for i in range(25):
    x = round(i * 2.54, 2)
    edge.append(f'  (pad "{2*i+1}" smd rect (at {x:.2f} 3.45) (size 1.80 6.90) (layers "F.Cu" "F.Mask"))')
    edge.append(f'  (pad "{2*i+2}" smd rect (at {x:.2f} 3.45) (size 1.80 6.90) (layers "B.Cu" "B.Mask"))')
edge.append(')')
(LIB / 'CPC_Edge_2x25.kicad_mod').write_text('\n'.join(edge) + '\n')
print('Wrote local CPC/EDAC footprints')
