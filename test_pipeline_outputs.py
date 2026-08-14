from dataclasses import replace

from config import CFG
from export import export_all
from geometry import build_wall_solid
from holes import apply_holes, generate_hole_grid


def test_generate_solid_and_outputs(tmp_path) -> None:
    test_cfg = replace(
        CFG,
        panel_height=1200.0,
        panel_width=600.0,
        hole_spacing_x=300.0,
        hole_spacing_z=300.0,
        output_dir=tmp_path,
    )

    wall = build_wall_solid(test_cfg)
    holes = generate_hole_grid(test_cfg)
    wall = apply_holes(wall, holes, test_cfg)

    exported = export_all(wall, test_cfg)

    assert exported.step_path.exists()
    assert exported.step_path.stat().st_size > 0
    assert exported.stl_path.exists()
    assert exported.stl_path.stat().st_size > 0
