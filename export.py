"""Esportazione geometria in STEP/STL e formati opzionali."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cadquery as cq
from cadquery import exporters
import trimesh

from config import WallConfig


@dataclass(frozen=True)
class ExportResult:
    step_path: Path
    stl_path: Path
    obj_path: Path | None
    glb_path: Path | None


def export_all(wall: cq.Workplane, cfg: WallConfig) -> ExportResult:
    out_dir = cfg.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    step_path = out_dir / cfg.step_name
    stl_path = out_dir / cfg.stl_name
    obj_path = out_dir / cfg.obj_name
    glb_path = out_dir / cfg.glb_name

    exporters.export(wall, str(step_path))
    exporters.export(
        wall,
        str(stl_path),
        tolerance=cfg.stl_tolerance,
        angularTolerance=cfg.stl_angular_tolerance,
    )

    obj_out: Path | None = None
    glb_out: Path | None = None

    # CadQuery non esporta OBJ in molte installazioni; fallback affidabile via trimesh da STL.
    try:
        mesh = trimesh.load_mesh(str(stl_path), file_type="stl")
        if isinstance(mesh, trimesh.Scene):
            mesh = mesh.dump(concatenate=True)
        mesh.export(str(obj_path), file_type="obj")
        if obj_path.exists() and obj_path.stat().st_size > 0:
            obj_out = obj_path
    except Exception:
        obj_out = None

    # GLB non e' disponibile nativamente in CadQuery in modo affidabile su tutte le installazioni.
    glb_out = None

    return ExportResult(step_path=step_path, stl_path=stl_path, obj_path=obj_out, glb_path=glb_out)
