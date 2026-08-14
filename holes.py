"""Generazione e applicazione dei fori passanti sulla parete."""

from __future__ import annotations

from dataclasses import dataclass

import cadquery as cq

from config import WallConfig
from geometry import (
    SegmentLayout,
    build_layout,
    front_surface_normal,
    front_surface_point,
)


@dataclass(frozen=True)
class HolePoint:
    x: float
    z: float
    region: str


@dataclass(frozen=True)
class HoleStats:
    total: int
    panel_1: int
    panel_2: int
    panel_3: int
    joint_1: int
    joint_2: int


def _classify_region(x: float, layout: SegmentLayout) -> str:
    if x <= layout.panel_1_flat_end:
        return "panel_1"
    if layout.joint_1_start <= x <= layout.joint_1_end:
        return "joint_1"
    if layout.panel_2_flat_start <= x <= layout.panel_2_flat_end:
        return "panel_2"
    if layout.joint_2_start <= x <= layout.joint_2_end:
        return "joint_2"
    return "panel_3"


def generate_hole_grid(cfg: WallConfig) -> list[HolePoint]:
    layout = build_layout(cfg)
    x_min = layout.x_min + cfg.hole_margin
    x_max = layout.x_max - cfg.hole_margin
    z_min = cfg.hole_margin
    z_max = cfg.panel_height - cfg.hole_margin

    points: list[HolePoint] = []

    z = z_min
    while z <= z_max + 1e-9:
        x = x_min
        while x <= x_max + 1e-9:
            points.append(HolePoint(x=x, z=z, region=_classify_region(x, layout)))
            x += cfg.hole_spacing_x
        z += cfg.hole_spacing_z

    return points


def _hole_cylinder(point: HolePoint, cfg: WallConfig) -> cq.Solid:
    px, py, pz = front_surface_point(point.x, point.z, cfg)
    nx, ny, nz = front_surface_normal(point.x, point.z, cfg)

    # Il cilindro deve attraversare completamente lo spessore con piccolo margine,
    # evitando tagli eccessivi sulle superfici laterali dei raccordi.
    depth = cfg.panel_thickness + cfg.hole_depth_margin
    radius = cfg.hole_diameter * 0.5

    start = cq.Vector(px - nx * depth * 0.5, py - ny * depth * 0.5, pz - nz * depth * 0.5)
    direction = cq.Vector(nx, ny, nz)
    return cq.Solid.makeCylinder(radius, depth, start, direction)


def apply_holes(
    wall: cq.Workplane,
    hole_points: list[HolePoint],
    cfg: WallConfig,
) -> cq.Workplane:
    cutters = [_hole_cylinder(p, cfg) for p in hole_points]

    def _cut_batch(target: cq.Workplane, batch: list[cq.Solid]) -> cq.Workplane:
        compound = cq.Compound.makeCompound(batch)
        return target.cut(cq.Workplane(obj=compound))

    # Booleane robuste per modelli con migliaia di fori: taglio per blocchi.
    result = wall
    batch_size = 300
    for i in range(0, len(cutters), batch_size):
        batch = cutters[i : i + batch_size]
        try:
            result = _cut_batch(result, batch)
        except Exception:
            # Fallback: se il blocco fallisce, prova con sottoblocchi piu' piccoli.
            sub_batch_size = 60
            for j in range(0, len(batch), sub_batch_size):
                sub_batch = batch[j : j + sub_batch_size]
                result = _cut_batch(result, sub_batch)

    return result


def compute_hole_stats(hole_points: list[HolePoint]) -> HoleStats:
    counters = {
        "panel_1": 0,
        "panel_2": 0,
        "panel_3": 0,
        "joint_1": 0,
        "joint_2": 0,
    }
    for p in hole_points:
        counters[p.region] += 1

    return HoleStats(
        total=len(hole_points),
        panel_1=counters["panel_1"],
        panel_2=counters["panel_2"],
        panel_3=counters["panel_3"],
        joint_1=counters["joint_1"],
        joint_2=counters["joint_2"],
    )
