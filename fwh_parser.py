"""
fwh_parser.py — Freedom Water Home XML Genome Parser
=====================================================
Parses fwh_genome.xml into a single state dictionary.
ZERO numeric literals in this file. Every value from XML.

Author : Gonçalo Melo de Magalhães · ORCID 0009-0008-6255-7724
Grant  : FCT 2025.00020.AIVLAB.DEUCALION
SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
"""
from __future__ import annotations
import math
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


LABEL = "SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW"


def _float(node: ET.Element | None, tag: str, default: float = 0.0) -> float:
    if node is None:
        return default
    el = node.find(tag)
    if el is None or el.text is None:
        return default
    return float(el.text.strip())


def _text(node: ET.Element | None, tag: str, default: str = "") -> str:
    if node is None:
        return default
    el = node.find(tag)
    if el is None or el.text is None:
        return default
    return el.text.strip()


def parse(xml_path: str | Path = "fwh_genome.xml") -> dict[str, Any]:
    """
    Parse the FWH genome XML into a flat state dictionary.
    Returns a dict with keys:
      - constants        : dict[str, float]  — all <c id=...>
      - geometry         : dict[str, float]  — derived geometry
      - water_geometry   : dict[str, float]  — water volumes + masses
      - systems          : dict[str, dict]   — body system components
      - afi_weights      : dict[str, float]  — D channel weights
      - bom              : dict              — bill of materials
      - scenarios        : list[dict]        — 34 validation scenarios
      - seed             : int
      - label            : str
    """
    tree = ET.parse(str(xml_path))
    root = tree.getroot()

    # ── Physical constants ────────────────────────────────────────────
    constants: dict[str, float] = {}
    for c in root.findall(".//c"):
        cid = c.get("id")
        val = c.get("value")
        if cid and val:
            constants[cid] = float(val)

    # ── Seed ──────────────────────────────────────────────────────────
    seed = int(root.get("seed", "2026"))

    # ── Geometry (re-derive from first principles) ────────────────────
    floor_area = _float(root.find("geometry"), "floor_area_m2")
    height     = _float(root.find("geometry"), "ceiling_height_m")
    side       = math.sqrt(floor_area)
    perimeter  = side * 4
    wall_area  = perimeter * height
    total_surf = wall_area + 2 * floor_area
    volume     = floor_area * height

    geometry = {
        "floor_area_m2":    floor_area,
        "ceiling_height_m": height,
        "side_m":           side,
        "perimeter_m":      perimeter,
        "wall_area_m2":     wall_area,
        "total_surface_m2": total_surf,
        "volume_m3":        volume,
    }

    # ── Water geometry (re-derive) ────────────────────────────────────
    wg_node = root.find("water_geometry")
    wt_wall    = _float(wg_node, "wall_water_thickness_m")
    wt_floor   = _float(wg_node, "floor_water_thickness_m")
    wt_ceiling = _float(wg_node, "ceiling_water_thickness_m")

    v_wall    = wall_area    * wt_wall
    v_floor   = floor_area   * wt_floor
    v_ceiling = floor_area   * wt_ceiling
    v_total   = v_wall + v_floor + v_ceiling
    m_total   = v_total * constants["rho_water"]
    thermal_mass_J_K = constants["cp_water"] * m_total  # J/K

    water_geometry = {
        "wall_water_thickness_m":    wt_wall,
        "floor_water_thickness_m":   wt_floor,
        "ceiling_water_thickness_m": wt_ceiling,
        "wall_water_volume_m3":      v_wall,
        "floor_water_volume_m3":     v_floor,
        "ceiling_water_volume_m3":   v_ceiling,
        "total_water_volume_m3":     v_total,
        "total_water_mass_kg":       m_total,
        "thermal_mass_J_K":          thermal_mass_J_K,
        "thermal_mass_MJ_K":         thermal_mass_J_K / 1e6,
    }

    # ── Body systems — parse all components recursively ───────────────
    systems: dict[str, dict] = {}
    for sys_node in root.findall(".//body_systems/system"):
        sid = sys_node.get("id", "unknown")
        sys_dict: dict[str, Any] = {}
        # All direct children that have numeric text
        for child in sys_node:
            tag = child.tag
            text = (child.text or "").strip()
            # Named components
            if tag in ("component", "s"):
                comp_id = child.get("id", tag)
                comp: dict[str, Any] = {}
                for sub in child:
                    stag = sub.tag
                    stext = (sub.text or "").strip()
                    try:
                        comp[stag] = float(stext)
                    except (ValueError, TypeError):
                        comp[stag] = stext
                sys_dict[comp_id] = comp
            elif tag == "legionella_control":
                leg: dict[str, float] = {}
                for sub in child:
                    try:
                        leg[sub.tag] = float((sub.text or "").strip())
                    except (ValueError, TypeError):
                        pass
                sys_dict["legionella_control"] = leg
            else:
                # Direct scalar
                try:
                    sys_dict[tag] = float(text)
                except (ValueError, TypeError):
                    if text:
                        sys_dict[tag] = text
        systems[sid] = sys_dict

    # ── AFI weights ───────────────────────────────────────────────────
    afi_weights: dict[str, float] = {}
    for w in root.findall(".//afi_framework/weights/w"):
        ch = w.get("channel")
        val = (w.text or "0").strip()
        if ch:
            afi_weights[ch] = float(val)

    weight_sum = sum(afi_weights.values())
    if abs(weight_sum - 1.0) >= 1e-6:
        raise ValueError(
            f"AFI weight sum = {weight_sum:.8f} ≠ 1.0 — HALT (HL-01)"
        )

    # ── Bill of Materials ─────────────────────────────────────────────
    bom_node = root.find("bom")
    bom: dict[str, Any] = {"items": {}, "budget_eur": 0.0}
    if bom_node is not None:
        bom["budget_eur"] = float(bom_node.findtext("budget_eur", "10000") or "10000")
        contingency = float(bom_node.findtext("contingency_factor", "1.0") or "1.0")
        bom["contingency_factor"] = contingency
        subtotal = 0.0
        for item in bom_node.findall("item"):
            iid = item.get("id", "?")
            # Compute item total
            total = float(item.get("total_eur", "0") or "0")
            if total == 0.0:
                upm3  = float(item.get("unit_cost_eur_m3",  "0") or "0")
                upm2  = float(item.get("unit_cost_eur_m2",  "0") or "0")
                upunt = float(item.get("unit_cost_eur_unit","0") or "0")
                vol   = float(item.get("volume_m3", "0") or "0")
                area  = float(item.get("area_m2",   "0") or "0")
                units = float(item.get("units",     "0") or "0")
                rate  = float(item.get("rate_eur_h","0") or "0")
                hours = float(item.get("hours",     "0") or "0")
                total = upm3*vol + upm2*area + upunt*units + rate*hours
            bom["items"][iid] = round(total, 2)
            subtotal += total
        bom["subtotal_eur"]     = round(subtotal, 2)
        bom["total_eur"]        = round(subtotal * contingency, 2)
        bom["margin_eur"]       = round(bom["budget_eur"] - bom["total_eur"], 2)

    # ── Scenarios ─────────────────────────────────────────────────────
    scenarios: list[dict] = []
    for sc in root.findall(".//scenarios/scenario"):
        sc_id = sc.get("id", "?")
        th = sc.find("threshold")
        if th is not None:
            scenarios.append({
                "id":       sc_id,
                "metric":   th.get("metric", "?"),
                "operator": th.get("operator", "gte"),
                "threshold": float(th.text or "0"),
            })

    return {
        "constants":      constants,
        "geometry":       geometry,
        "water_geometry": water_geometry,
        "systems":        systems,
        "afi_weights":    afi_weights,
        "bom":            bom,
        "scenarios":      scenarios,
        "seed":           seed,
        "label":          LABEL,
    }


if __name__ == "__main__":
    import json
    s = parse("fwh_genome.xml")
    print(f"Constants: {len(s['constants'])}")
    print(f"Geometry:  {s['geometry']}")
    print(f"Water mass: {s['water_geometry']['total_water_mass_kg']:.1f} kg")
    print(f"AFI weights sum: {sum(s['afi_weights'].values()):.6f}")
    print(f"BOM total: EUR {s['bom']['total_eur']:.2f}")
    print(f"Scenarios: {len(s['scenarios'])}")
    print(f"Seed: {s['seed']}")
    print(s["label"])
