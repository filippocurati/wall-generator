from config import CFG


def test_nominal_config_values() -> None:
    assert CFG.panel_width == 4000.0
    assert CFG.panel_height == 20000.0
    assert CFG.panel_thickness == 40.0
    assert CFG.panel_angles_deg == (80.0, 90.0, 110.0)

    assert CFG.hole_diameter == 11.0
    assert CFG.hole_spacing_x == 200.0
    assert CFG.hole_spacing_z == 200.0
