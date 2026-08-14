"""Validazioni geometriche e di output del generatore."""

from __future__ import annotations

import math
from pathlib import Path

import cadquery as cq

from config import WallConfig
from geometry import build_layout, front_surface_normal, front_surface_point, panel_angle_deg_at_x
from holes import HolePoint


def validate_geometry(wall: cq.Workplane) -> None:
    solid = wall.val()
    if solid is None:
        raise RuntimeError("Validazione fallita: solido finale assente")
    if solid.Volume() <= 0:
        raise RuntimeError("Validazione fallita: volume nullo")
    if not solid.isValid():
        raise RuntimeError("Validazione fallita: solido OCC non valido")


def validate_dimensions(cfg: WallConfig) -> None:
    if len(cfg.panel_angles_deg) != 3:
        raise RuntimeError("Validazione fallita: devono essere presenti 3 pannelli")

    for expected, actual in zip((80.0, 90.0, 110.0), cfg.panel_angles_deg):
        if abs(expected - actual) > 1e-6:
            raise RuntimeError(
                f"Validazione fallita: angolo pannello atteso {expected} deg, trovato {actual} deg"
            )

    if abs(cfg.panel_width - 4000.0) > cfg.dimension_tolerance:
        raise RuntimeError("Validazione fallita: larghezza pannello fuori tolleranza")
    if abs(cfg.panel_height - 20000.0) > cfg.dimension_tolerance:
        raise RuntimeError("Validazione fallita: altezza pannello fuori tolleranza")
    if abs(cfg.panel_thickness - 40.0) > 2.0:
        raise RuntimeError("Validazione fallita: spessore pannello fuori tolleranza")


def validate_hole_grid(cfg: WallConfig, holes: list[HolePoint], wall: cq.Workplane | None = None) -> None:
    if cfg.hole_diameter <= 0:
        raise RuntimeError("Validazione fallita: diametro fori non valido")
    if cfg.hole_spacing_x <= 0 or cfg.hole_spacing_z <= 0:
        raise RuntimeError("Validazione fallita: passo fori non valido")
    if not holes:
        raise RuntimeError("Validazione fallita: nessun foro generato")

    layout = build_layout(cfg)
    regions = {"panel_1", "panel_2", "panel_3", "joint_1", "joint_2"}
    found = {p.region for p in holes}
    if not regions.issubset(found):
        missing = ", ".join(sorted(regions - found))
        raise RuntimeError(f"Validazione fallita: regioni senza fori: {missing}")

    first_row = sorted([p for p in holes if abs(p.z - holes[0].z) < 1e-6], key=lambda p: p.x)
    if len(first_row) > 1:
        for a, b in zip(first_row[:-1], first_row[1:]):
            spacing = b.x - a.x
            if abs(spacing - cfg.hole_spacing_x) > 1e-6:
                raise RuntimeError("Validazione fallita: passo orizzontale fori incoerente")

    col_x = holes[0].x
    first_col = sorted([p for p in holes if abs(p.x - col_x) < 1e-6], key=lambda p: p.z)
    if len(first_col) > 1:
        for a, b in zip(first_col[:-1], first_col[1:]):
            spacing = b.z - a.z
            if abs(spacing - cfg.hole_spacing_z) > 1e-6:
                raise RuntimeError("Validazione fallita: passo verticale fori incoerente")

    # Verifica indicativa degli angoli nei tre tratti principali.
    probes = [
        (layout.x_min + layout.panel_1_flat_end) * 0.5,
        (layout.panel_2_flat_start + layout.panel_2_flat_end) * 0.5,
        (layout.panel_3_flat_start + layout.x_max) * 0.5,
    ]
    for i, (x, expected) in enumerate(zip(probes, cfg.panel_angles_deg), start=1):
        measured = panel_angle_deg_at_x(x, cfg, layout)
        if not math.isclose(measured, expected, abs_tol=1e-6):
            raise RuntimeError(
                f"Validazione fallita: angolo pannello {i} non coerente ({measured} != {expected})"
            )

    if wall is not None and hasattr(wall.val(), "isInside"):
        solid = wall.val()
        sample_step = max(1, len(holes) // 24)
        sampled = holes[::sample_step]
        for hp in sampled:
            px, py, pz = front_surface_point(hp.x, hp.z, cfg)
            nx, ny, nz = front_surface_normal(hp.x, hp.z, cfg)
            test_point = cq.Vector(
                px - nx * (cfg.panel_thickness * 0.5),
                py - ny * (cfg.panel_thickness * 0.5),
                pz - nz * (cfg.panel_thickness * 0.5),
            )

            try:
                is_inside = solid.isInside(test_point, 1e-4, False)
            except TypeError:
                is_inside = solid.isInside(test_point, 1e-4)

            if is_inside:
                raise RuntimeError("Validazione fallita: almeno un foro non risulta passante")


def validate_outputs(step_path: Path, stl_path: Path, obj_path: Path | None, glb_path: Path | None) -> None:
    if not step_path.exists() or step_path.stat().st_size == 0:
        raise RuntimeError("Validazione fallita: output STEP mancante o vuoto")
    if not stl_path.exists() or stl_path.stat().st_size == 0:
        raise RuntimeError("Validazione fallita: output STL mancante o vuoto")

    if obj_path is not None and (not obj_path.exists() or obj_path.stat().st_size == 0):
        raise RuntimeError("Validazione fallita: output OBJ richiesto ma non valido")

    if glb_path is not None and (not glb_path.exists() or glb_path.stat().st_size == 0):
        raise RuntimeError("Validazione fallita: output GLB richiesto ma non valido")
