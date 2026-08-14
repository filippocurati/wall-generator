import math

from config import CFG
from geometry import build_layout, panel_angle_deg_at_x
from holes import generate_hole_grid


def test_panel_count_and_angles() -> None:
    assert len(CFG.panel_angles_deg) == 3
    assert CFG.panel_angles_deg == (80.0, 90.0, 110.0)


def test_angle_function_flat_regions() -> None:
    layout = build_layout(CFG)

    x1 = (layout.x_min + layout.panel_1_flat_end) * 0.5
    x2 = (layout.panel_2_flat_start + layout.panel_2_flat_end) * 0.5
    x3 = (layout.panel_3_flat_start + layout.x_max) * 0.5

    assert math.isclose(panel_angle_deg_at_x(x1, CFG, layout), 80.0, abs_tol=1e-6)
    assert math.isclose(panel_angle_deg_at_x(x2, CFG, layout), 90.0, abs_tol=1e-6)
    assert math.isclose(panel_angle_deg_at_x(x3, CFG, layout), 110.0, abs_tol=1e-6)


def test_hole_grid_spacing() -> None:
    points = generate_hole_grid(CFG)
    assert points

    row0_z = points[0].z
    row = sorted([p for p in points if abs(p.z - row0_z) < 1e-6], key=lambda p: p.x)
    for a, b in zip(row[:-1], row[1:]):
        assert math.isclose(b.x - a.x, CFG.hole_spacing_x, abs_tol=1e-6)

    col0_x = points[0].x
    col = sorted([p for p in points if abs(p.x - col0_x) < 1e-6], key=lambda p: p.z)
    for a, b in zip(col[:-1], col[1:]):
        assert math.isclose(b.z - a.z, CFG.hole_spacing_z, abs_tol=1e-6)
