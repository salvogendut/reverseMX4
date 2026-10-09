# Assembly and connection notes — A0 prototype

## Placement and orientation

The 100 × 200 mm board has four top-entry card-edge sockets, J2 to J5, on 35 mm centres. Fit four **EDAC 395-050-521-204** sockets with the even-numbered row on the side marked by the footprint and the odd-numbered row along the printed `1 … 49` edge. Check the manufacturer's numbering on the actual delivered parts before soldering. Each socket has two 3.96 mm mounting holes; use insulating hardware or washers within the copper keepouts.

The narrow tongue, J1, is the **cable input**. Looking at the front of the board with `reverseMX4 A0` readable, contacts 1, 3, … 49 are on the visible face, from left to right. Contacts 2, 4, … 50 are on the reverse face at the same positions. The tongue is 65.74 mm wide and accepts a 1.6 mm nominal, dual-sided 50-contact socket.

## Host cables

Make a short cable with a 50-contact female edge socket at the **board** end. At the computer end:

| Computer | Computer-side cable connector | Electrical mapping |
| --- | --- | --- |
| CPC 464/664/6128 | 50-contact female card-edge socket | CPC contact *n* to J1 contact *n* |
| CPC 464 Plus/6128 Plus | 50-contact male Delta/Amphenol style plug | Expansion signal named on Plus pin *n* to J1 contact *n*, following Amstrad's Arnold V pin table |

Do not infer contact order from a cable stripe or how two sockets face each other. Before connecting a computer, use a meter to verify **all 50** paths against [`cpc-expansion-pinout.csv`](cpc-expansion-pinout.csv), with no adjacent-contact shorts. As quick orientation checks, contact 1 is SOUND, 2 and 49 are GND, 27 is computer 5 V, and 50 is the 4 MHz clock. The board-end socket must mate with the front/reverse contact convention above.

The classic CPC edge socket and the Plus Delta plug are different mechanical parts. Use a separate cable for each host style. The Plus bus signal numbering is documented in the [Amstrad Arnold V specification](https://www.cpctech.cpcwiki.de/docs/arn5new.html).

## Power

Only fit **one** shunt on JP1:

| JP1 shunt | Slot 5 V source |
| --- | --- |
| Pins 1–2 | CPC expansion contact 27 |
| Pins 2–3 | External regulated 5 V via J6 and F1 |
| Removed | Slot 5 V disconnected |

J6 pin 1 is `+5 V`; pin 2 is `GND`. Ground is shared with the CPC in both modes. F1 protects only the external positive input. Fit C1 with its positive lead at pad 1. Check supply polarity and 5 V at each socket contact 27 before inserting expansion cards. The CPC expansion power pin is described as suitable for limited peripheral power, so use external power when card load exceeds the computer's available margin. The 3 A PTC is a hold-current part at 23 °C, not a precise 3 A trip threshold.

## PCB fabrication and inspection

- Four copper layers, 1.6 mm finished board thickness, plated through holes and separate NPTH tooling/mounting holes.
- The J1 tongue's copper contacts are exposed on both faces. Request a durable gold contact finish and a shallow bevel on the insertion edge; have the fabricator review the 0.6 mm copper setback against its finish and bevel process. Ordinary ENIG may serve for low-cycle prototype mating.
- Maintain the 65.74 mm tongue width and 2.54 mm contact pitch. Avoid edge rounding at the tongue's side shoulders where it sets insertion width.
- The EDAC drawing gives 1.37–1.78 mm accepted card thickness. Confirm actual card stock and socket fit with a bare board before assembling all four sockets.
- Support installed cards mechanically. The 35 mm spacing is a centre pitch; bulky components on expansion cards may require clearance checks.
- The four black sockets in the [3D rendering](preview/board-3d.png) use an illustrative model. Validate the connector's real height, housing clearance and orientation against samples or the manufacturer's current drawing.

## Electrical review record

KiCad 10.0.6 ERC: **0 violations**. KiCad PCB DRC after zone refill: **0 violations, 0 unconnected items, 0 schematic parity issues**. An independent exported-netlist check confirmed every J1 contact except the deliberately isolated CPC 5 V reaches the same-numbered contact on J2–J5. Contact 27 from J1 reaches only JP1 pin 1; the four socket contact-27 pads share `BUS_5V` with JP1 pin 2 and the capacitors. DRC checks copper geometry; it does not prove physical mating or CPC compatibility.
