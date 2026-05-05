from __future__ import annotations

from .chemistry import PEROVSKITE_A_RADII_PM, PEROVSKITE_B_RADII_PM, parse_formula
from .models import ChemistryInsight, MaterialCandidate


def infer_chemistry_insight(
    candidate: MaterialCandidate, properties: dict[str, float], domain: str
) -> ChemistryInsight:
    counts = parse_formula(candidate.formula)
    elements = set(counts)
    family = _material_family(counts)
    motif = _structure_motif(counts, properties)
    bonding = _bonding_character(elements, properties)
    mechanisms = _mechanisms(elements, family, motif, domain, properties)
    tradeoffs = _tradeoffs(elements, properties)
    validation = _validation_priorities(elements, family, motif, domain, candidate.metadata.get("workflow", "dft"))
    descriptors = {
        "ionic_contrast": round(properties["ionic_contrast"], 3),
        "oxygen_fraction": round(properties["oxygen_fraction"], 3),
        "transition_metal_fraction": round(properties["transition_metal_fraction"], 3),
        "perovskite_tolerance_factor": properties["perovskite_tolerance_factor"],
        "octahedral_factor": properties["octahedral_factor"],
        "perovskite_stability_score": properties["perovskite_stability_score"],
        "toxicity_score": properties["toxicity_score"],
        "supply_risk_fraction": round(properties["supply_risk_fraction"], 3),
    }
    return ChemistryInsight(
        material_family=family,
        structure_motif=motif,
        bonding_character=bonding,
        mechanism_hypotheses=mechanisms,
        tradeoff_notes=tradeoffs,
        validation_priorities=validation,
        descriptors=descriptors,
    )


def _material_family(counts: dict[str, float]) -> str:
    elements = set(counts)
    if {"C", "F"} <= elements:
        return "fluorinated electroactive polymer"
    if {"Si", "O", "C", "H"} <= elements:
        return "silicone elastomer"
    if {"Ni", "Ti"} <= elements:
        return "shape-memory alloy"
    if "O" in elements and _looks_like_perovskite(counts):
        return "oxide perovskite"
    if "O" in elements and _looks_like_spinel(counts):
        return "oxide spinel"
    if "O" in elements:
        return "functional oxide"
    if "N" in elements and ("Al" in elements or "Sc" in elements):
        return "III-nitride"
    return "composition candidate"


def _structure_motif(counts: dict[str, float], properties: dict[str, float]) -> str:
    elements = set(counts)
    if _looks_like_perovskite(counts):
        tolerance = properties["perovskite_tolerance_factor"]
        if 0.95 <= tolerance <= 1.03:
            return "near-cubic ABO3 perovskite"
        return "distorted ABO3 perovskite"
    if _looks_like_spinel(counts):
        return "AB2O4 spinel network"
    if {"Zr", "O"} <= elements or {"Hf", "O"} <= elements:
        return "fluorite-derived high-k oxide"
    if ({"Al", "O"} <= elements or {"Ga", "O"} <= elements) and abs(counts.get("O", 0.0) - 3.0) <= 0.08:
        return "corundum or polymorphic sesquioxide network"
    if {"In", "O"} <= elements and abs(counts.get("O", 0.0) - 3.0) <= 0.08:
        return "bixbyite-like transparent conducting oxide"
    if {"Sn", "O"} <= elements or {"Ti", "O"} <= elements:
        return "rutile-like oxide network"
    if {"Zn", "O"} <= elements:
        return "wurtzite-like transparent oxide"
    if {"Si", "O"} <= elements and "C" not in elements:
        return "silicate network former"
    if {"C", "F"} <= elements:
        return "polar polymer repeat unit"
    if {"Ni", "Ti"} <= elements:
        return "B2/B19 martensitic alloy motif"
    if "N" in elements and ("Al" in elements or "Sc" in elements):
        return "wurtzite nitride lattice"
    return "composition-level motif"


def _bonding_character(elements: set[str], properties: dict[str, float]) -> str:
    if {"Ni", "Ti"} <= elements:
        return "metallic with martensitic phase instability"
    if "C" in elements and ("F" in elements or "H" in elements):
        return "covalent polymer backbone with polar side groups"
    if properties["ionic_contrast"] > 2.3:
        return "strongly ionic or iono-covalent"
    if properties["ionic_contrast"] > 1.4:
        return "mixed ionic-covalent"
    return "mostly covalent or metallic"


def _mechanisms(
    elements: set[str],
    family: str,
    motif: str,
    domain: str,
    properties: dict[str, float],
) -> list[str]:
    mechanisms: list[str] = []
    if "perovskite" in family:
        mechanisms.append("off-center B-site displacement and domain switching can drive dielectric or piezoelectric response")
        if properties["perovskite_tolerance_factor"]:
            mechanisms.append(
                f"Goldschmidt tolerance factor {properties['perovskite_tolerance_factor']:.3f} suggests the degree of perovskite distortion"
            )
    if family == "oxide spinel":
        mechanisms.append("dense oxygen framework can combine optical transmission with hardness and thermal stability")
    if "functional oxide" in family:
        mechanisms.append("oxygen sublattice and cation chemistry tune band gap, defects, and dielectric response")
    if {"Zn", "O"} <= elements or {"Sn", "O"} <= elements or {"In", "O"} <= elements:
        mechanisms.append("aliovalent doping or oxygen-vacancy control can tune transparent conductivity")
    if family == "fluorinated electroactive polymer":
        mechanisms.append("polar C-F dipoles can reorient under electric field for lightweight actuation")
    if family == "silicone elastomer":
        mechanisms.append("low glass-transition silicone backbone supports compliant strain and soft sensing skins")
    if family == "shape-memory alloy":
        mechanisms.append("reversible martensitic transformation can deliver high strain density")
    if family == "III-nitride":
        mechanisms.append("wurtzite polarity and alloying can enhance piezoelectric response")
    if domain == "ar_glasses" and properties["bandgap_proxy_ev"] > 3.0:
        mechanisms.append("wide-gap chemistry supports visible transparency for optical stacks")
    if domain == "robotics_actuator" and properties["strain_score"] > 0.5:
        mechanisms.append("screening indicates actuator-relevant strain or compliance")
    return mechanisms[:4]


def _tradeoffs(elements: set[str], properties: dict[str, float]) -> list[str]:
    notes: list[str] = []
    if properties["toxicity_score"] > 0.1:
        notes.append("toxicity or regulatory burden should be checked before device integration")
    if properties["supply_risk_fraction"] > 0.0:
        notes.append("scarce or supply-sensitive elements may limit scale-up")
    if properties["density_proxy"] > 0.75:
        notes.append("density proxy is high for lightweight wearable hardware")
    if properties["hpc_cost_hours"] > 1.5:
        notes.append("larger or more complex formula may need higher simulation budget")
    if {"Pb"} & elements:
        notes.append("lead-containing reference should be treated as a performance baseline rather than a consumer product candidate")
    if not notes:
        notes.append("no high-severity chemistry tradeoff triggered by current heuristics")
    return notes


def _validation_priorities(
    elements: set[str], family: str, motif: str, domain: str, workflow: str
) -> list[str]:
    priorities: list[str] = []
    if workflow == "dft":
        priorities.append("DFT relaxation, band structure, and defect energetics")
    elif workflow == "md":
        priorities.append("MD thermal stability, chain mobility, and mechanical response")
    elif workflow == "monte_carlo":
        priorities.append("Monte Carlo sampling of phase or configurational stability")
    if "perovskite" in family:
        priorities.append("phonon stability, polarization estimate, and tetragonal/rhombohedral distortion")
    if family == "oxide spinel" or domain == "ar_glasses":
        priorities.append("thin-film optical constants, haze, stress, and humidity aging")
    if domain == "robotics_actuator":
        priorities.append("cyclic fatigue, actuation strain, dielectric loss, and displacement per gram")
    if "transparent" in motif or {"Zn", "Sn", "In"} & elements:
        priorities.append("carrier concentration, mobility, and visible transmittance after processing")
    return priorities[:4]


def _looks_like_perovskite(counts: dict[str, float]) -> bool:
    oxygen = counts.get("O", 0.0)
    a_count = sum(amount for element, amount in counts.items() if element in PEROVSKITE_A_RADII_PM)
    b_count = sum(amount for element, amount in counts.items() if element in PEROVSKITE_B_RADII_PM)
    return (
        abs(oxygen - 3.0) <= 0.08
        and abs(a_count - 1.0) <= 0.15
        and abs(b_count - 1.0) <= 0.15
    )


def _looks_like_spinel(counts: dict[str, float]) -> bool:
    oxygen = counts.get("O", 0.0)
    non_oxygen = sum(amount for element, amount in counts.items() if element != "O")
    return abs(oxygen - 4.0) <= 0.08 and abs(non_oxygen - 3.0) <= 0.18
