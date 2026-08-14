"""Costruzione geometrica della parete tramite CadQuery."""

from __future__ import annotations

import math
from dataclasses import dataclass

import cadquery as cq

from config import WallConfig


@dataclass(frozen=True)
class SegmentLayout:
    x_min: float
    x_max: float
    panel_1_flat_end: float
    joint_1_start: float
    joint_1_end: float
    panel_2_flat_start: float
    panel_2_flat_end: float
    joint_2_start: float
    joint_2_end: float
    panel_3_flat_start: float


def build_layout(cfg: WallConfig) -> SegmentLayout:
    half_total = 1.5 * cfg.panel_width
    x_min = -half_total
    x_max = half_total

    split_1 = -0.5 * cfg.panel_width
    split_2 = 0.5 * cfg.panel_width
    jh = 0.5 * cfg.joint_width

    return SegmentLayout(
        x_min=x_min,
        x_max=x_max,
        panel_1_flat_end=split_1 - jh,
        joint_1_start=split_1 - jh,
        joint_1_end=split_1 + jh,
        panel_2_flat_start=split_1 + jh,
        panel_2_flat_end=split_2 - jh,
        joint_2_start=split_2 - jh,
        joint_2_end=split_2 + jh,
        panel_3_flat_start=split_2 + jh,
    )


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def panel_angle_deg_at_x(x: float, cfg: WallConfig, layout: SegmentLayout | None = None) -> float:
    if layout is None:
        layout = build_layout(cfg)

    a1, a2, a3 = cfg.panel_angles_deg
    if x <= layout.panel_1_flat_end:
        return a1
    if layout.joint_1_start <= x <= layout.joint_1_end:
        t = (x - layout.joint_1_start) / (layout.joint_1_end - layout.joint_1_start)
        return _lerp(a1, a2, t)
    if layout.panel_2_flat_start <= x <= layout.panel_2_flat_end:
        return a2
    if layout.joint_2_start <= x <= layout.joint_2_end:
        t = (x - layout.joint_2_start) / (layout.joint_2_end - layout.joint_2_start)
        return _lerp(a2, a3, t)
    return a3


def angle_derivative_rad_per_mm_at_x(
    x: float,
    cfg: WallConfig,
    layout: SegmentLayout | None = None,
) -> float:
    if layout is None:
        layout = build_layout(cfg)

    a1, a2, a3 = cfg.panel_angles_deg
    if layout.joint_1_start <= x <= layout.joint_1_end:
        return math.radians(a2 - a1) / (layout.joint_1_end - layout.joint_1_start)
    if layout.joint_2_start <= x <= layout.joint_2_end:
        return math.radians(a3 - a2) / (layout.joint_2_end - layout.joint_2_start)
    return 0.0


def front_surface_point(x: float, z: float, cfg: WallConfig) -> tuple[float, float, float]:
    angle_deg = panel_angle_deg_at_x(x, cfg)
    angle_rad = math.radians(angle_deg)
    y = -z / math.tan(angle_rad)
    return (x, y, z)


def front_surface_normal(x: float, z: float, cfg: WallConfig) -> tuple[float, float, float]:
    angle_deg = panel_angle_deg_at_x(x, cfg)
    angle_rad = math.radians(angle_deg)
    da_dx = angle_derivative_rad_per_mm_at_x(x, cfg)

    s = math.sin(angle_rad)
    c = math.cos(angle_rad)
    s_safe = s if abs(s) > 1e-8 else (1e-8 if s >= 0 else -1e-8)
    csc2 = 1.0 / (s_safe * s_safe)

    # Normale alla superficie y(x, z) = -z / tan(a(x)).
    nx = -(z * csc2 * da_dx)
    ny = 1.0
    nz = c / s_safe

    norm = math.sqrt(nx * nx + ny * ny + nz * nz)
    return (nx / norm, ny / norm, nz / norm)


def _section_profile_yz(angle_deg: float, cfg: WallConfig) -> list[tuple[float, float]]:
    angle_rad = math.radians(angle_deg)
    h = cfg.panel_height
    t = cfg.panel_thickness

    y_fb = 0.0
    z_fb = 0.0
    y_ft = -h / math.tan(angle_rad)
    z_ft = h

    ny = math.sin(angle_rad)
    nz = math.cos(angle_rad)

    y_bb = y_fb - t * ny
    z_bb = z_fb - t * nz
    y_bt = y_ft - t * ny
    z_bt = z_ft - t * nz

    return [(y_fb, z_fb), (y_ft, z_ft), (y_bt, z_bt), (y_bb, z_bb)]


def build_wall_solid(cfg: WallConfig) -> cq.Workplane:
    layout = build_layout(cfg)

    stations = [
        layout.x_min,
        0.5 * (layout.x_min + layout.panel_1_flat_end),
        layout.panel_1_flat_end,
    ]

    for i in range(1, cfg.joint_slices + 1):
        t = i / (cfg.joint_slices + 1)
        stations.append(_lerp(layout.joint_1_start, layout.joint_1_end, t))

    stations += [
        layout.joint_1_end,
        0.5 * (layout.panel_2_flat_start + layout.panel_2_flat_end),
        layout.panel_2_flat_end,
    ]

    for i in range(1, cfg.joint_slices + 1):
        t = i / (cfg.joint_slices + 1)
        stations.append(_lerp(layout.joint_2_start, layout.joint_2_end, t))

    stations += [
        layout.joint_2_end,
        0.5 * (layout.panel_3_flat_start + layout.x_max),
        layout.x_max,
    ]

    stations = sorted(set(stations))

    x0 = stations[0]
    a0 = panel_angle_deg_at_x(x0, cfg, layout)
    profile0 = _section_profile_yz(a0, cfg)

    wall = cq.Workplane("YZ").workplane(offset=x0).polyline(profile0).close()
    prev_x = x0

    for x in stations[1:]:
        angle = panel_angle_deg_at_x(x, cfg, layout)
        profile = _section_profile_yz(angle, cfg)
        wall = wall.workplane(offset=(x - prev_x)).polyline(profile).close()
        prev_x = x

    wall = wall.loft(combine=True, ruled=True)
    return wall


def build_floor_solid(cfg: WallConfig, wall: cq.Workplane) -> cq.Workplane:
    area_mm2 = cfg.floor_area_m2 * 1_000_000.0
    total_wall_width = 3.0 * cfg.panel_width
    min_floor_width = total_wall_width + (2.0 * cfg.floor_side_margin)
    side_from_area = math.sqrt(area_mm2)
    floor_width = max(min_floor_width, side_from_area, total_wall_width + cfg.floor_min_extra_width)
    floor_depth = area_mm2 / floor_width

    bb = wall.val().BoundingBox()
    cx = 0.5 * (bb.xmin + bb.xmax)
    cy = 0.5 * (bb.ymin + bb.ymax)

    floor = (
        cq.Workplane("XY")
        .box(floor_width, floor_depth, cfg.floor_thickness, centered=(True, True, True))
        .translate((cx, cy, -cfg.floor_gap - (0.5 * cfg.floor_thickness)))
    )
    return floor


def orient_y_up(model: cq.Workplane) -> cq.Workplane:
    # Rotazione globale: Z (altezza CAD interna) -> Y (altezza modello esportato).
    return model.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), -90.0)
