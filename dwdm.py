from pathlib import Path
import math
import gdsfactory as gf
from ubcpdk import PDK, cells

@gf.cell
def dwdm_splitter():
    """
    Direct GDSFactory recreation of the Nazca DWDM layout.

    Top -> bottom:
        A: y = 381 um
        B: y = 254 um
        C: y = 127 um
        D: y =   0 um

    B and D form the main vertical bus on the right.

    Ring C:
        - radius = 10 um
        - LEFT of B-D bus
        - collector LEFT of ring

    Ring A:
        - radius = 50 um
        - RIGHT of B-D bus
        - collector RIGHT of ring
    """

    c = gf.Component()

    # ========================================================
    # PARAMETERS FROM YOUR NAZCA DESIGN
    # ========================================================

    pitch = 127.0

    y_A = 3 * pitch       # 381
    y_B = 2 * pitch       # 254
    y_C = pitch           # 127
    y_D = 0.0

    short_length = 20.0
    long_length = 200.0

    bd_bend_radius = 30.0

    ring_C_radius = 10.0
    ring_C_gap = 0.2

    ring_A_radius = 50.0
    ring_A_gap = 0.2

    # Get actual UBC strip width/layer
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
    # B -> D MAIN BUS
    #
    # B and D both end at x = 200.
    # Route goes right by 30 um and then vertically.
    #
    # Vertical bus centerline: x = 230 um
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

    # Tangency points of the vertical B-D section
    bus_top_y = y_B - bd_bend_radius     # 224
    bus_bottom_y = y_D + bd_bend_radius  # 30

    # ========================================================
    # RING C
    # ========================================================

    # Nazca:
    # ring_C_X = bus_x - R - gap - width
    #
    # Nazca ring starts at its bottom point.
    # Therefore actual ring CENTER is R above ring_C_Y.

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

    # Move collector o1 exactly to desired lower point
    collector_C.move(
        (
            collector_C_x
            - collector_C.ports["o1"].center[0],
            collector_C_y
            - collector_C.ports["o1"].center[1],
        )
    )

    # Collector -> C
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

    # Collector -> A
    gf.routing.route_single(
        c,
        port1=collector_A.ports["o2"],
        port2=A.ports["o2"],
        radius=10.0,
        bend=gf.components.bend_circular,
        cross_section="strip",
    )

    # ========================================================
    # EXTERNAL PORTS
    #
    # Important for cells.add_fiber_array()
    # ========================================================

    c.add_port(name="o1", port=A.ports["o1"])  # A
    c.add_port(name="o2", port=B.ports["o1"])  # B
    c.add_port(name="o3", port=C.ports["o1"])  # C
    c.add_port(name="o4", port=D.ports["o1"])  # D

    return c
