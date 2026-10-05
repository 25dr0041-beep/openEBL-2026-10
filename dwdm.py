from pathlib import Path
import math
import gdsfactory as gf
from ubcpdk import PDK, cells

PDK.activate()

@gf.cell
def dwdm_splitter():
    """
    DWDM test structure with four integrated grating couplers.

    Top -> bottom:
        A: y = 381 um
        B: y = 254 um  <- input
        C: y = 127 um
        D: y =   0 um

    All grating couplers are 127 um apart vertically.
    """

    c = gf.Component()

    # ========================================================
    # PARAMETERS
    # ========================================================

    pitch = 127.0

    y_A = 3 * pitch
    y_B = 2 * pitch
    y_C = pitch
    y_D = 0.0

    short_length = 20.0
    long_length = 200.0

    bd_bend_radius = 30.0

    ring_C_radius = 10.0
    ring_C_gap = 0.2

    ring_A_radius = 50.0
    ring_A_gap = 0.2

    xs = gf.get_cross_section("strip")
    wg_width = xs.width
    wg_layer = xs.layer

    # ========================================================
    # FOUR HORIZONTAL WAVEGUIDES
    # ========================================================

    A = c << cells.straight(
        length=short_length,
        cross_section="strip",
    )
    A.move((0, y_A))

    B = c << cells.straight(
        length=long_length,
        cross_section="strip",
    )
    B.move((0, y_B))

    C = c << cells.straight(
        length=short_length,
        cross_section="strip",
    )
    C.move((0, y_C))

    D = c << cells.straight(
        length=long_length,
        cross_section="strip",
    )
    D.move((0, y_D))

    # ========================================================
    # GRATING COUPLERS
    #
    # Connecting them directly to the LEFT ports of A/B/C/D
    # makes the waveguides extend to the RIGHT, as required
    # by the Phot1x automated tester.
    # ========================================================

    gc_component = cells.ebeam_gc_te1550()

    gc_A = c << gc_component
    gc_A.connect("o1", A.ports["o1"])

    gc_B = c << gc_component
    gc_B.connect("o1", B.ports["o1"])

    gc_C = c << gc_component
    gc_C.connect("o1", C.ports["o1"])

    gc_D = c << gc_component
    gc_D.connect("o1", D.ports["o1"])

    # Automated measurement label:
    # B is the SECOND coupler from the top = input fiber.
    c.add_label(
        text="opt_in_TE_1550_device_IdoNirTheGreat_DWDM",
        position=gc_B.ports["o1"].center,
        layer=(10, 0),
    )

    # ========================================================
    # B -> D MAIN BUS
    # ========================================================

    bus_x = long_length + bd_bend_radius

    gf.routing.route_single(
        c,
        port1=B.ports["o2"],
        port2=D.ports["o2"],
        waypoints=[
            (bus_x, y_B),
            (bus_x, y_D),
        ],
        radius=bd_bend_radius,
        bend=gf.components.bend_circular,
        cross_section="strip",
    )

    bus_top_y = y_B - bd_bend_radius
    bus_bottom_y = y_D + bd_bend_radius

    # ========================================================
    # RING C
    # ========================================================

    ring_C_center_x = (
        bus_x
        - ring_C_radius
        - ring_C_gap
        - wg_width
    )

    ring_C_bottom_y = (
        bus_bottom_y
        + ring_C_radius
        + 5.0
    )

    ring_C_center_y = (
        ring_C_bottom_y
        + ring_C_radius
    )

    ring_C_component = gf.components.ring(
        radius=ring_C_radius,
        width=wg_width,
        layer=wg_layer,
    )

    ring_C = c << ring_C_component
    ring_C.move(
        (
            ring_C_center_x,
            ring_C_center_y,
        )
    )

    # ========================================================
    # RING C COLLECTOR
    # ========================================================

    collector_C_x = (
        ring_C_center_x
        - ring_C_radius
        - wg_width
        - ring_C_gap
    )

    collector_C_y = (
        ring_C_bottom_y
        - 10.0
    )

    collector_C = c << cells.straight(
        length=2 * ring_C_radius,
        cross_section="strip",
    )

    collector_C.rotate(90)

    collector_C.move(
        (
            collector_C_x
            - collector_C.ports["o1"].center[0],
            collector_C_y
            - collector_C.ports["o1"].center[1],
        )
    )

    gf.routing.route_single(
        c,
        port1=collector_C.ports["o2"],
        port2=C.ports["o2"],
        radius=10.0,
        bend=gf.components.bend_circular,
        cross_section="strip",
    )

    # ========================================================
    # RING A
    # ========================================================

    ring_A_center_x = (
        bus_x
        + ring_A_radius
        + ring_A_gap
        + wg_width
    )

    ring_A_bottom_y = (
        bus_top_y
        - 2 * ring_A_radius
        - 5.0
    )

    ring_A_center_y = (
        ring_A_bottom_y
        + ring_A_radius
    )

    ring_A_component = gf.components.ring(
        radius=ring_A_radius,
        width=wg_width,
        layer=wg_layer,
    )

    ring_A = c << ring_A_component
    ring_A.move(
        (
            ring_A_center_x,
            ring_A_center_y,
        )
    )

    # ========================================================
    # RING A COLLECTOR
    # ========================================================

    collector_A_x = (
        ring_A_center_x
        + ring_A_radius
        + wg_width
        + ring_A_gap
    )

    collector_A_y = (
        ring_A_bottom_y
        - 10.0
    )

    collector_A = c << cells.straight(
        length=2 * ring_A_radius,
        cross_section="strip",
    )

    collector_A.rotate(90)

    collector_A.move(
        (
            collector_A_x
            - collector_A.ports["o1"].center[0],
            collector_A_y
            - collector_A.ports["o1"].center[1],
        )
    )

    gf.routing.route_single(
        c,
        port1=collector_A.ports["o2"],
        port2=A.ports["o2"],
        radius=10.0,
        bend=gf.components.bend_circular,
        cross_section="strip",
    )

    return c
