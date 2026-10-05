from pathlib import Path
import math
import gdsfactory as gf
from ubcpdk import PDK, cells
import dwdm

USERNAME = "IdoNirTheGreat"

OUTPUT_DIR = Path("submissions")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / f"EBeam_{USERNAME}.gds"

PDK.activate()

MZI_DELTA_LENGTH = 145.0
MZI_X = 0.0
REFERENCE_X = 200.0
DWDM_X = 400.0

LAMBDA_A_UM = 1.560
LAMBDA_C_UM = 1.540
FINESSE = 20.0


# MZI block
mzi = cells.mzi_1x1(
    delta_length=MZI_DELTA_LENGTH,
    splitter="ebeam_y_1550",
    cross_section="strip",
)

mzi_test = cells.add_fiber_array(
    component=mzi,
    component_name=f"{USERNAME}_MZI",
    with_loopback=False,
)

# Reference block
reference = cells.straight(length=100.0, cross_section="strip")

reference_test = cells.add_fiber_array(
    component=reference,
    component_name=f"{USERNAME}_REFERENCE",
    with_loopback=False,
)

# DWDM block
dwdm_test = dwdm.dwdm_splitter()

# Top cell
top = gf.Component(f"EBeam_{USERNAME}")

mzi_ref = top << mzi_test
ref_ref = top << reference_test
dwdm_ref = top << dwdm_test


mzi_ref.move((MZI_X, 0))
ref_ref.move((REFERENCE_X, 0))
dwdm_ref.move((DWDM_X, 0))

# Align top heights
ref_ref.movey(mzi_ref.ymax - ref_ref.ymax)

print(f"Layout size: {top.xsize:.1f} x {top.ysize:.1f} um")
if top.xsize > 605:
    print("WARNING: width exceeds 605 um")
if top.ysize > 410:
    print("WARNING: height exceeds 410 um")

top.write_gds(OUTPUT_FILE)
print(f"Saved to: {OUTPUT_FILE.resolve()}")

top.show()