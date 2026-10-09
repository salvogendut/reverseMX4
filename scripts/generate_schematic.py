#!/usr/bin/env python3
"""Generate the source schematic from the reviewed CPC contact table."""

import csv
import pathlib
import re
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
NAME = "reverseMX4"
SHEET_UUID = str(uuid.uuid5(uuid.NAMESPACE_URL, "reverseMX4/schematic/root"))


def uid(key):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"reverseMX4/{key}"))


def quoted(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def extract_symbol(source, name):
    text = source.read_text()
    match = re.search(r'\(symbol "' + re.escape(name) + r'"', text)
    if not match:
        raise ValueError(f"Cannot find {name} in {source}")
    start = match.start()
    depth = 0
    in_string = False
    escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '"':
                in_string = False
        elif ch == '"':
            in_string = True
        elif ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise ValueError(f"Unbalanced symbol {name}")


SYMBOLS = pathlib.Path('/var/lib/flatpak/runtime/org.kicad.kicad.Library/x86_64/stable/active/files/symbols')
connector = extract_symbol(SYMBOLS / 'Connector_Generic.kicad_sym', 'Conn_02x25_Odd_Even')
connector = connector.replace('(symbol "Conn_02x25_Odd_Even"', '(symbol "Connector_Generic:Conn_02x25_Odd_Even"', 1)
pinout = list(csv.DictReader((ROOT / 'docs/cpc-expansion-pinout.csv').open()))
assert len(pinout) == 50

body = []


def label(name, x, y, tag):
    body.append(f'(label {quoted(name)} (at {x:.3f} {y:.3f} 0) (effects (font (size 1 1)) (justify left bottom)) (uuid "{uid(tag)}"))')


def wire(x1, y1, x2, y2, tag):
    body.append(f'(wire (pts (xy {x1:.3f} {y1:.3f}) (xy {x2:.3f} {y2:.3f})) (stroke (width 0) (type default)) (uuid "{uid(tag)}"))')


def property_(key, val, x, y, hide=False):
    return f'(property {quoted(key)} {quoted(val)} (at {x:.3f} {y:.3f} 0) {"(hide yes)" if hide else ""} (effects (font (size 1 1)) (justify left)))'


for index, x in enumerate((38.1, 114.3, 190.5, 266.7, 342.9), start=1):
    y = 120.65
    ref = f'J{index}'
    value = 'CPC_CABLE_EDGE' if index == 1 else f'EDGE_SLOT_{index - 1}'
    fp = 'reverseMX4:CPC_Edge_2x25' if index == 1 else 'reverseMX4:EDAC_395-050-521-204'
    pins = ''.join(f'(pin "{n}" (uuid "{uid(ref + "/pin/" + str(n))}"))' for n in range(1, 51))
    body.append(f'''(symbol (lib_id "Connector_Generic:Conn_02x25_Odd_Even") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid(ref)}")
      {property_("Reference", ref, x, 85)}
      {property_("Value", value, x, 155)}
      {property_("Footprint", fp, x, y, True)}
      {property_("Datasheet", "", x, y, True)}
      {pins}
      (instances (project "{NAME}" (path "/{SHEET_UUID}" (reference "{ref}") (unit 1)))))''')
    for row in pinout:
        n = int(row['contact'])
        sig = row['signal']
        if sig == 'GND':
            sig = 'GND'
        elif sig == '+5V':
            sig = 'CPC_5V' if index == 1 else 'BUS_5V'
        elif sig.startswith('/'):
            sig = 'n' + sig[1:]
        # Schematic symbol pin 1 is at (-5.08,+30.48) in symbol coordinates.
        yy = y - 30.48 + ((n - 1) // 2) * 2.54
        if n % 2:
            xpin, xend = x - 5.08, x - 15.24
        else:
            xpin, xend = x + 7.62, x + 17.78
        wire(xpin, yy, xend, yy, f'{ref}/wire/{n}')
        label(sig, xend, yy, f'{ref}/label/{n}')


def simple_symbol(name, pins, width=10, height=10):
    shape = f'(rectangle (start {-width/2} {height/2}) (end {width/2} {-height/2}) (stroke (width 0.254) (type default)) (fill (type background)))'
    ptxt = ''
    for num, px, py, angle in pins:
        ptxt += f'(pin passive line (at {px} {py} {angle}) (length 5.08) (name "Pin_{num}" (effects (font (size 1 1)))) (number "{num}" (effects (font (size 1 1)))))'
    return f'''(symbol "reverseMX4:{name}" (pin_names (offset 0.5) (hide yes)) (in_bom yes) (on_board yes)
      (property "Reference" "X" (at 0 {height/2+2.54} 0) (effects (font (size 1 1))))
      (property "Value" "{name}" (at 0 {-height/2-2.54} 0) (effects (font (size 1 1))))
      (symbol "{name}_0_1" {shape})
      (symbol "{name}_1_1" {ptxt}))'''


parts = [
    ('J6', 'EXT_5V_IN', 'reverseMX4:PowerIn_2', 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2_1x02_P5.00mm_Horizontal', 50.8, 205.74, [(1, 'EXT_5V', 43.18, 203.2), (2, 'GND', 43.18, 208.28)]),
    ('F1', '3A_PTC', 'reverseMX4:Series_2', 'Fuse:Fuse_Bourns_MF-RG300', 114.3, 205.74, [(1, 'EXT_5V', 106.68, 205.74), (2, 'EXT_5V_FUSED', 121.92, 205.74)]),
    ('JP1', '5V_SOURCE_SELECT', 'reverseMX4:Select_3', 'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical', 190.5, 205.74, [(1, 'CPC_5V', 182.88, 203.2), (2, 'BUS_5V', 182.88, 205.74), (3, 'EXT_5V_FUSED', 182.88, 208.28)]),
    ('C1', '100uF_10V', 'reverseMX4:Shunt_2', 'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm', 266.7, 205.74, [(1, 'BUS_5V', 266.7, 198.12), (2, 'GND', 266.7, 213.36)]),
    ('C2', '100nF_50V', 'reverseMX4:Shunt_2', 'Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm', 342.9, 205.74, [(1, 'BUS_5V', 342.9, 198.12), (2, 'GND', 342.9, 213.36)]),
]
power_symbols = [
    simple_symbol('PowerIn_2', [(1, -7.62, 2.54, 0), (2, -7.62, -2.54, 0)]),
    simple_symbol('Series_2', [(1, -7.62, 0, 0), (2, 7.62, 0, 180)]),
    simple_symbol('Select_3', [(1, -7.62, 2.54, 0), (2, -7.62, 0, 0), (3, -7.62, -2.54, 0)]),
    simple_symbol('Shunt_2', [(1, 0, 7.62, 270), (2, 0, -7.62, 90)]),
]
(ROOT / 'reverseMX4.kicad_sym').write_text(
    '(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")\n'
    + '\n'.join(s.replace('(symbol "reverseMX4:', '(symbol "', 1) for s in power_symbols)
    + '\n)\n'
)
(ROOT / 'sym-lib-table').write_text('(sym_lib_table (lib (name "reverseMX4") (type "KiCad") (uri "${KIPRJMOD}/reverseMX4.kicad_sym") (options "") (descr "CPC backplane local symbols")))\n')
for ref, value, lib, fp, x, y, pins in parts:
    plist = ''.join(f'(pin "{p}" (uuid "{uid(ref + "/pin/" + str(p))}"))' for p, *_ in pins)
    body.append(f'''(symbol (lib_id "{lib}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid(ref)}")
    {property_("Reference", ref, x + 10, y - 5)}
    {property_("Value", value, x + 10, y)}
    {property_("Footprint", fp, x, y, True)}
    {property_("Datasheet", "", x, y, True)}
    {plist}
    (instances (project "{NAME}" (path "/{SHEET_UUID}" (reference "{ref}") (unit 1)))))''')
    for p, net, px, py in pins:
        label(net, px, py, f'{ref}/label/{p}')

output = f'''(kicad_sch (version 20250114) (generator "eeschema") (uuid "{SHEET_UUID}") (paper "A3")
(title_block (title "CPC four-slot edge backplane") (date "2026-10-09") (rev "A0") (comment 1 "CPC / CPC Plus via model-specific cable") (comment 2 "External 5V must be regulated; select one power source"))
(lib_symbols {connector} {' '.join(power_symbols)})
{' '.join(body)}
(embedded_fonts no))
'''
(ROOT / f'{NAME}.kicad_sch').write_text(output)
print(f'Wrote {NAME}.kicad_sch')
