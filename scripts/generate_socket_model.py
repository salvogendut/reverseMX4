#!/usr/bin/env python3
"""Create an indicative VRML body for the custom EDAC socket footprint.

The electrical footprint follows the EDAC drawing. This visual model is only
for design review; it is not a measured mechanical model of the connector.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'models/EDAC_395-050-521-204-preview.wrl'
MODEL.parent.mkdir(exist_ok=True)


def box(x0, x1, y0, y1, z0, z1):
    """Return a VRML box with mm inputs; KiCad VRML units are 2.54 mm."""
    center = ((x0 + x1) / 5.08, -(y0 + y1) / 5.08,
              (z0 + z1) / 5.08)
    size = ((x1 - x0) / 2.54, (y1 - y0) / 2.54,
            (z1 - z0) / 2.54)
    return '''Transform {
  translation %.6f %.6f %.6f
  children [ Shape {
    appearance Appearance { material Material { diffuseColor 0.10 0.105 0.11 } }
    geometry Box { size %.6f %.6f %.6f }
  } ]
}''' % (*center, *size)


# Two long walls leave a 1.8 mm card opening. The low end pieces suggest the
# mounting flanges while keeping the mounting-hole areas visually apparent.
parts = [
    box(-2.54, 63.50, -1.905, 1.64, 0.2, 11.5),
    box(-2.54, 63.50, 3.44, 6.985, 0.2, 11.5),
    box(-3.8, -2.54, -1.905, 6.985, 0.2, 11.5),
    box(63.50, 64.76, -1.905, 6.985, 0.2, 11.5),
    box(-11.875, -3.8, -1.905, 6.985, 0.2, 2.5),
    box(64.76, 72.835, -1.905, 6.985, 0.2, 2.5),
]
MODEL.write_text('#VRML V2.0 utf8\n' + '\n'.join(parts) + '\n')
print('Wrote', MODEL.relative_to(ROOT))
