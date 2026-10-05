from pathlib import Path
import gdsfactory as gf
from ubcpdk import PDK, cells
import dwdm

USERNAME = "IdoNirTheGreat"

OUTPUT_DIR = Path("submissions")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / f"EBeam_{USERNAME}.gds"

PDK.activate()

# ============================================================
# PLACEMENT
# ============================================================

MZI_X = 0.0
REFERENCE_X = 150.0
REFERENCE_Y = 22.5
RING_REFERENCE_X = 350.0
RING_REFERENCE_Y = 290.584
DWDM_X = -125.55
DWDM_Y = 100.0

# ============================================================
# PARAMETERS
# ============================================================

MZI_DELTA_LENGTH = 145.0

# Same gap as DWDM
RING_REFERENCE_GAP = 0.2
RING_REFERENCE_RADIUS = 10.0


# ============================================================
# MZI
# ============================================================

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


# ============================================================
# STRAIGHT REFERENCE
# ============================================================

reference = cells.straight(
    length=100.0,
    cross_section="strip",
)

reference_test = cells.add_fiber_array(
    component=reference,
    component_name=f"{USERNAME}_REFERENCE",
    with_loopback=False,
)


# ============================================================
# RING REFERENCE
#
# Simple PDK add-drop ring.
# 4 optical ports -> 4 grating couplers.
# ============================================================

ring_reference = cells.ring_double(
    radius=RING_REFERENCE_RADIUS,
    gap=RING_REFERENCE_GAP,
    length_x=0.01,
    length_y=0.01,
    length_extension=10.0,
    cross_section="strip",
)

ring_reference_test = cells.add_fiber_array(
    component=ring_reference,
    component_name=f"{USERNAME}_RING_REFERENCE",
    with_loopback=False,
)


# ============================================================
# DWDM
# ============================================================

dwdm_test = dwdm.dwdm_splitter()


# ============================================================
# TOP CELL
# ============================================================

top = gf.Component(f"EBeam_{USERNAME}")

mzi_ref = top << mzi_test
ref_ref = top << reference_test
ring_ref = top << ring_reference_test
dwdm_ref = top << dwdm_test


# ============================================================
# POSITIONING
# ============================================================

mzi_ref.move((MZI_X, 0))

ref_ref.move((REFERENCE_X, REFERENCE_Y))

ring_ref.move((RING_REFERENCE_X, RING_REFERENCE_Y))

dwdm_ref.move((DWDM_X, DWDM_Y))


# ============================================================
# CHECK SIZE
# ============================================================

print(
    f"Layout size: "
    f"{top.xsize:.1f} x {top.ysize:.1f} um"
)

if top.xsize > 605:
    print("WARNING: width exceeds 605 um")

if top.ysize > 410:
    print("WARNING: height exceeds 410 um")


# ============================================================
# EXPORT
# ============================================================

top.write_gds(OUTPUT_FILE)

print(f"Saved to: {OUTPUT_FILE.resolve()}")

top.show()
