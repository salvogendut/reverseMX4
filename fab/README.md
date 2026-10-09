# A0 prototype fabrication package

[`reverseMX4-A0-gerbers.zip`](reverseMX4-A0-gerbers.zip) is the Gerber X2 and Excellon output from the editable KiCad board. It contains front and back copper, two inner copper layers, front and back mask and silkscreen, the board outline, and separate PTH and NPTH files. The loose files in [`gerbers/`](gerbers/) are the same export.

Specify a four-layer, 1.6 mm finished FR-4 board. The mating tongue is 65.74 mm wide. Both faces have exposed edge contacts. Request a durable gold contact finish and a shallow insertion-edge bevel, then have the fabricator check the 0.6 mm copper setback and bevel process before release. The eight 3.96 mm socket mounting holes are NPTH.

This is an unbuilt A0 prototype. Check the EDAC socket footprint, contact orientation, cable mapping, and mechanical fit with real parts before ordering a larger run. The [assembly notes](../docs/assembly.md) contain the power-selection and first-power checks.
