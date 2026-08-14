"""Metadati materiale per output mesh o integrazioni future."""

from __future__ import annotations

from dataclasses import dataclass

from config import WallConfig


@dataclass(frozen=True)
class MaterialDefinition:
    name: str
    rgb: tuple[float, float, float]


def wall_material(cfg: WallConfig) -> MaterialDefinition:
    return MaterialDefinition(name=cfg.material_name, rgb=cfg.material_rgb)
