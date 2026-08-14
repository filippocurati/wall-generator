"""Entry point per generare la parete di arrampicata parametrica."""

from __future__ import annotations

import sys
import time

import cadquery as cq

from config import CFG
from export import export_all
from geometry import build_floor_solid, build_wall_solid, orient_y_up
from holes import apply_holes, compute_hole_stats, generate_hole_grid
from validation import (
    validate_dimensions,
    validate_geometry,
    validate_hole_grid,
    validate_outputs,
)


def _fmt_optional(name: str, path: object | None) -> str:
    if path is None:
        return f"  {name}: not generated (optional output unavailable)"
    return f"  {name}: generated"


def main() -> int:
    start = time.perf_counter()

    try:
        print("[1/7] Validating configuration...")
        validate_dimensions(CFG)

        print("[2/7] Creating wall geometry (panels + joints)...")
        wall = build_wall_solid(CFG)

        print("[3/7] Generating hole grid...")
        hole_points = generate_hole_grid(CFG)
        hole_stats = compute_hole_stats(hole_points)

        print("[4/7] Applying boolean cuts...")
        wall = apply_holes(wall, hole_points, CFG)

        print("[4.5/7] Creating floor and assembling scene...")
        floor = build_floor_solid(CFG, wall)
        wall_oriented = orient_y_up(wall)
        floor_oriented = orient_y_up(floor)
        model_compound = cq.Compound.makeCompound([wall_oriented.val(), floor_oriented.val()])
        model = cq.Workplane(obj=model_compound)

        print("[5/7] Validating geometry and holes...")
        validate_geometry(wall)
        validate_hole_grid(CFG, hole_points, wall)

        print("[6/7] Exporting files...")
        exported = export_all(model, CFG)

        print("[7/7] Validating outputs...")
        validate_outputs(exported.step_path, exported.stl_path, exported.obj_path, exported.glb_path)

        elapsed = time.perf_counter() - start

        print()
        print("Wall generation completed.")
        print()
        print("Panels:")
        print(f"  Panel 1: {CFG.panel_angles_deg[0]:.1f} deg")
        print(f"  Panel 2: {CFG.panel_angles_deg[1]:.1f} deg")
        print(f"  Panel 3: {CFG.panel_angles_deg[2]:.1f} deg")
        print()
        print("Dimensions:")
        print(f"  Panel width: {CFG.panel_width:.1f} mm")
        print(f"  Panel height: {CFG.panel_height:.1f} mm")
        print(f"  Thickness: {CFG.panel_thickness:.1f} mm")
        print(f"  Floor area: {CFG.floor_area_m2:.1f} m2")
        print()
        print("Holes:")
        print(f"  Diameter: {CFG.hole_diameter:.1f} mm")
        print(f"  Spacing: {CFG.hole_spacing_x:.1f} x {CFG.hole_spacing_z:.1f} mm")
        print(f"  Total: {hole_stats.total}")
        print(f"  Panel 1: {hole_stats.panel_1}")
        print(f"  Panel 2: {hole_stats.panel_2}")
        print(f"  Panel 3: {hole_stats.panel_3}")
        print(f"  Joint 1: {hole_stats.joint_1}")
        print(f"  Joint 2: {hole_stats.joint_2}")
        print()
        print("Output:")
        print(f"  STEP: {exported.step_path}")
        print(f"  STL: {exported.stl_path}")
        print(_fmt_optional("OBJ", exported.obj_path))
        print(_fmt_optional("GLB", exported.glb_path))
        print()
        print(f"Generation time: {elapsed:.2f} s")

        return 0
    except Exception as exc:
        print()
        print(f"Generation failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
