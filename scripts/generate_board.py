#!/usr/bin/env python3
"""Generate a four-layer CPC edge backplane from the KiCad XML netlist."""

import csv
import math
from pathlib import Path
import uuid
import xml.etree.ElementTree as ET

import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
LIBROOT = Path('/app/share/kicad/footprints')
NETLIST = ROOT / 'reverseMX4.net'
PCB = ROOT / 'reverseMX4.kicad_pcb'
PROJECT = ROOT / 'reverseMX4.kicad_pro'
project_bytes = PROJECT.read_bytes()


def uid(key):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f'reverseMX4/{key}'))


def pt(x, y):
    return p.VECTOR2I(p.FromMM(round(x, 4)), p.FromMM(round(y, 4)))


board = p.BOARD()
board.SetCopperLayerCount(4)
board.GetDesignSettings().SetBoardThickness(p.FromMM(1.6))
title = board.GetTitleBlock()
title.SetTitle('CPC four-slot edge backplane')
title.SetRevision('A0 prototype')
title.SetDate('2026-10-09')

net_xml = ET.parse(NETLIST).getroot()
nets = {}
pad_nets = {}
for node in net_xml.findall('./nets/net'):
    name = node.attrib['name']
    info = p.NETINFO_ITEM(board, name)
    board.Add(info)
    nets[name] = info
    for pin in node.findall('node'):
        pad_nets[(pin.attrib['ref'], pin.attrib['pin'])] = name

FP = {
    'J1': ('reverseMX4', 'CPC_Edge_2x25', (19.52, 192.5, 0)),
    'J2': ('reverseMX4', 'EDAC_395-050-521-204', (19.52, 42.46, 0)),
    'J3': ('reverseMX4', 'EDAC_395-050-521-204', (19.52, 77.46, 0)),
    'J4': ('reverseMX4', 'EDAC_395-050-521-204', (19.52, 112.46, 0)),
    'J5': ('reverseMX4', 'EDAC_395-050-521-204', (19.52, 147.46, 0)),
    'J6': ('TerminalBlock_Phoenix', 'TerminalBlock_Phoenix_MKDS-1,5-2_1x02_P5.00mm_Horizontal', (12, 15, 0)),
    'F1': ('Fuse', 'Fuse_Bourns_MF-RG300', (34, 15, 0)),
    'JP1': ('Connector_PinHeader_2.54mm', 'PinHeader_1x03_P2.54mm_Vertical', (54, 14, 0)),
    'C1': ('Capacitor_THT', 'CP_Radial_D6.3mm_P2.50mm', (70, 15, 0)),
    'C2': ('Capacitor_THT', 'C_Disc_D3.0mm_W1.6mm_P2.50mm', (81, 15, 0)),
}
VALUES = {'J1': 'CPC_CABLE_EDGE', 'J2': 'EDGE_SLOT_1', 'J3': 'EDGE_SLOT_2', 'J4': 'EDGE_SLOT_3', 'J5': 'EDGE_SLOT_4',
          'J6': 'EXT_5V_IN', 'F1': '3A_PTC', 'JP1': '5V_SOURCE_SELECT', 'C1': '100uF_10V', 'C2': '100nF_50V'}
fps = {}
for ref, (lib, name, (x, y, angle)) in FP.items():
    root = ROOT / 'reverseMX4.pretty' if lib == 'reverseMX4' else LIBROOT / (lib + '.pretty')
    fp = p.FootprintLoad(str(root), name)
    if fp is None:
        raise RuntimeError(f'Footprint not found: {lib}:{name} at {root}')
    fp.SetFPID(p.LIB_ID(lib, name))
    fp.SetReference(ref)
    fp.SetValue(VALUES[ref])
    fp.SetPath(p.KIID_PATH('/' + uid('schematic/root') + '/' + uid(ref)))
    board.Add(fp)
    fp.SetPosition(pt(x, y))
    fp.SetOrientationDegrees(angle)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    for pad in fp.Pads():
        name_ = pad_nets.get((ref, pad.GetNumber()))
        if name_ is not None:
            pad.SetNet(nets[name_])
    fps[ref] = fp


def pad(ref, number):
    found = [x for x in fps[ref].Pads() if x.GetNumber() == str(number)]
    assert len(found) == 1, (ref, number, len(found))
    x = found[0].GetPosition()
    return p.ToMM(x.x), p.ToMM(x.y)


def track(net, layer, a, b, width=0.25):
    if a == b:
        return
    t = p.PCB_TRACK(board)
    t.SetStart(pt(*a)); t.SetEnd(pt(*b))
    t.SetLayer(layer); t.SetWidth(p.FromMM(width)); t.SetNet(nets[net])
    board.Add(t)


def path(net, layer, points, width=0.25):
    for a, b in zip(points, points[1:]):
        track(net, layer, a, b, width)


def via(net, x, y, size=0.8, drill=0.4):
    v = p.PCB_VIA(board)
    v.SetPosition(pt(x, y)); v.SetWidth(p.FromMM(size)); v.SetDrill(p.FromMM(drill))
    v.SetViaType(p.VIATYPE_THROUGH); v.SetLayerPair(p.F_Cu, p.B_Cu)
    v.SetNet(nets[net]); board.Add(v)


# Board outline: 100 mm wide base with a 67 mm tongue at the cable end.
# EDAC specifies the recommended daughter-board width as D minus 0.30 mm:
# 66.04 - 0.30 = 65.74 mm for the 50-contact variant.
outline = [(0, 0), (100, 0), (100, 185), (82.87, 185), (82.87, 200),
           (17.13, 200), (17.13, 185), (0, 185)]
for a, b in zip(outline, outline[1:] + outline[:1]):
    edge = p.PCB_SHAPE()
    edge.SetShape(p.SHAPE_T_SEGMENT)
    edge.SetStart(pt(*a)); edge.SetEnd(pt(*b))
    edge.SetLayer(p.Edge_Cuts); edge.SetWidth(p.FromMM(0.05))
    board.Add(edge)


def silk(s, x, y, size=1.0, layer=p.F_SilkS, angle=0):
    t = p.PCB_TEXT(board)
    t.SetText(s); t.SetPosition(pt(x, y))
    t.SetTextSize(pt(size, size)); t.SetTextThickness(p.FromMM(0.15))
    t.SetTextAngle(p.EDA_ANGLE(angle, p.DEGREES_T)); t.SetLayer(layer)
    if layer == p.B_SilkS:
        t.SetMirrored(True)
    board.Add(t)


for slot, y in enumerate((45, 80, 115, 150), start=1):
    silk(f'SLOT {slot}', 50, y - 9, 1.3)
    silk('1', 16.2, y - 2.54, 1.0)
    silk('49', 83, y - 2.54, 1.0)
silk('reverseMX4  A0', 50, 30, 1.8)
silk('CPC / CPC PLUS - 50 WAY EDGE', 50, 34, 1.0)
silk('EXT 5V', 12, 27, 1.0)
silk('+5', 12, 23, 0.9)
silk('GND', 18, 23, 0.9)
silk('JP1: 1-2 CPC  /  2-3 EXT', 52, 25, 1.0)
silk('PIN 1 TOP / ODD FACE', 50, 180, 1.0)
silk('CABLE EDGE', 50, 184, 1.1)
silk('BOARD END: 1 ODD / 2 EVEN', 50, 188, 0.8, p.B_SilkS)

pinout = list(csv.DictReader((ROOT / 'docs/cpc-expansion-pinout.csv').open()))
for row in pinout:
    n = int(row['contact'])
    if n in (2, 27, 49):
        continue  # handled by dedicated power and ground copper
    name = row['signal']
    if name.startswith('/'):
        name = 'n' + name[1:]
    net = '/' + name
    col = (n - 1) // 2
    x = round(19.52 + col * 2.54, 2)
    trunk_x = round(x + 1.27, 2)
    layer = p.In1_Cu if n % 2 else p.In2_Cu
    # One bus spine per contact, one inner layer per face.
    for ref in ('J2', 'J3', 'J4', 'J5'):
        px, py = pad(ref, n)
        track(net, layer, (px, py), (trunk_x, py), 0.25)
    first_y = pad('J2', n)[1]
    last_y = pad('J5', n)[1]
    tongue_x, tongue_y = pad('J1', n)
    if n % 2:
        vx, vy = round(x - 0.65, 2), 190.0
        end_y = 187.5
        path(net, layer, [(trunk_x, first_y), (trunk_x, end_y), (vx, end_y), (vx, vy)], 0.25)
        path(net, p.F_Cu, [(tongue_x, tongue_y), (vx, vy)], 0.25)
    else:
        vx, vy = round(x + 0.65, 2), 190.0
        end_y = 188.5
        path(net, layer, [(trunk_x, first_y), (trunk_x, end_y), (vx, vy)], 0.25)
        path(net, p.B_Cu, [(tongue_x, tongue_y), (vx, vy)], 0.25)
    via(net, vx, vy)

# CPC-side 5 V is routed only to selector pin 1. It does not join BUS_5V
# unless the removable shunt is deliberately placed on pins 1-2.
cpc_x, cpc_y = pad('J1', 27)
sel1 = pad('JP1', 1)
path('/CPC_5V', p.F_Cu, [(cpc_x, cpc_y), (cpc_x - 0.8, 190),
                         (cpc_x - 0.8, 182), (5, 182), (5, 3),
                         (sel1[0] - 3, 3), (sel1[0] - 3, sel1[1]), sel1], 0.5)

# External supply input and protected feed to the selector.
path('/EXT_5V', p.F_Cu, [pad('J6', 1), (12, 8), (34, 8), pad('F1', 1)], 0.8)
path('/EXT_5V_FUSED', p.F_Cu, [pad('F1', 2), (46, 15), pad('JP1', 3)], 1.0)

# Broad outer copper fills carry the selected supply and return. Keep copper
# off the finger contact region, leaving deliberate isolated contact pads.
for layer, net in ((p.F_Cu, '/BUS_5V'), (p.B_Cu, '/GND')):
    zone = p.ZONE(board)
    zone.SetLayer(layer); zone.SetNet(nets[net])
    zone.SetLocalClearance(p.FromMM(0.25))
    zone.SetThermalReliefGap(p.FromMM(0.3))
    zone.SetThermalReliefSpokeWidth(p.FromMM(0.3))
    zone.SetPadConnection(p.ZONE_CONNECTION_THERMAL)
    zone.SetMinThickness(p.FromMM(0.25))
    poly = zone.Outline(); poly.NewOutline()
    for x, y in ((0.5, 0.5), (99.5, 0.5), (99.5, 184.5),
                 (82.37, 184.5), (82.37, 191), (17.63, 191),
                 (17.63, 184.5), (0.5, 184.5)):
        poly.Append(int(p.FromMM(x)), int(p.FromMM(y)))
    board.Add(zone)

# Keep screw heads and metal washers away from copper around the eight socket
# mounting holes. The EDAC x04 option has 3.96 mm through holes.
for slot_y in (45, 80, 115, 150):
    for hole_x in (10.945, 89.055):
        area = p.ZONE(board)
        area.SetIsRuleArea(True)
        area.SetLayerSet(p.LSET.AllCuMask(4))
        area.SetDoNotAllowTracks(True)
        area.SetDoNotAllowVias(True)
        area.SetDoNotAllowZoneFills(True)
        area.SetDoNotAllowPads(False)
        area.SetZoneName('Socket mounting hardware clearance')
        poly = area.Outline(); poly.NewOutline()
        for i in range(16):
            angle = 2 * math.pi * i / 16
            poly.Append(int(p.FromMM(hole_x + 4.5 * math.cos(angle))),
                        int(p.FromMM(slot_y + 4.5 * math.sin(angle))))
        board.Add(area)

# A small via joins the top-side odd ground finger to the return plane.
gx, gy = pad('J1', 2)
path('/GND', p.B_Cu, [(gx, gy), (gx + 0.65, 190.0)], 0.4)
gx, gy = pad('J1', 49)
via('/GND', gx - 0.65, 190.0)
path('/GND', p.F_Cu, [(gx, gy), (gx - 0.65, 190.0)], 0.4)

p.SaveBoard(str(PCB), board)
PROJECT.write_bytes(project_bytes)
print('Wrote', PCB.name, 'with', len(FP), 'footprints and 4 copper layers')
