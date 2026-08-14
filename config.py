"""Configurazione parametrica per il generatore della parete di arrampicata."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WallConfig:
    panel_width: float = 4000.0
    panel_height: float = 20000.0
    panel_thickness: float = 40.0
    panel_angles_deg: tuple[float, float, float] = (80.0, 90.0, 110.0)

    hole_diameter: float = 11.0
    hole_spacing_x: float = 200.0
    hole_spacing_z: float = 200.0
    hole_margin: float = 6.0
    hole_depth_margin: float = 2.0

    # Larghezza del raccordo lungo X; piccola per preservare larghezza nominale pannelli.
    joint_width: float = 40.0
    joint_slices: int = 8

    stl_tolerance: float = 0.8
    stl_angular_tolerance: float = 0.2

    output_dir: Path = Path("output")
    step_name: str = "wall.step"
    stl_name: str = "wall.stl"
    obj_name: str = "wall.obj"
    glb_name: str = "wall.glb"

    material_name: str = "Wall"
    material_rgb: tuple[float, float, float] = (1.0, 1.0, 1.0)

    floor_area_m2: float = 50.0
    floor_thickness: float = 100.0
    floor_side_margin: float = 250.0
    floor_min_extra_width: float = 500.0
    floor_gap: float = 1.0

    dimension_tolerance: float = 60.0


CFG = WallConfig()
