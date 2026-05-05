from __future__ import annotations

import math
import re
from collections import defaultdict


ATOMIC_WEIGHTS = {
    "H": 1.008,
    "Li": 6.94,
    "B": 10.81,
    "C": 12.011,
    "N": 14.007,
    "O": 15.999,
    "F": 18.998,
    "Na": 22.990,
    "Mg": 24.305,
    "Al": 26.982,
    "Si": 28.085,
    "P": 30.974,
    "S": 32.06,
    "Cl": 35.45,
    "K": 39.098,
    "Ca": 40.078,
    "Sc": 44.956,
    "Ti": 47.867,
    "V": 50.942,
    "Cr": 51.996,
    "Mn": 54.938,
    "Fe": 55.845,
    "Co": 58.933,
    "Ni": 58.693,
    "Cu": 63.546,
    "Zn": 65.38,
    "Ga": 69.723,
    "Ge": 72.630,
    "As": 74.922,
    "Se": 78.971,
    "Sr": 87.62,
    "Zr": 91.224,
    "Nb": 92.906,
    "Mo": 95.95,
    "Ag": 107.868,
    "Cd": 112.414,
    "In": 114.818,
    "Sn": 118.710,
    "Sb": 121.760,
    "Te": 127.60,
    "Ba": 137.327,
    "Hf": 178.49,
    "Ta": 180.948,
    "W": 183.84,
    "Pt": 195.084,
    "Au": 196.967,
    "Hg": 200.592,
    "Pb": 207.2,
    "Bi": 208.980,
}

ELECTRONEGATIVITY = {
    "H": 2.20,
    "Li": 0.98,
    "B": 2.04,
    "C": 2.55,
    "N": 3.04,
    "O": 3.44,
    "F": 3.98,
    "Na": 0.93,
    "Mg": 1.31,
    "Al": 1.61,
    "Si": 1.90,
    "P": 2.19,
    "S": 2.58,
    "Cl": 3.16,
    "K": 0.82,
    "Ca": 1.00,
    "Sc": 1.36,
    "Ti": 1.54,
    "V": 1.63,
    "Cr": 1.66,
    "Mn": 1.55,
    "Fe": 1.83,
    "Co": 1.88,
    "Ni": 1.91,
    "Cu": 1.90,
    "Zn": 1.65,
    "Ga": 1.81,
    "Ge": 2.01,
    "As": 2.18,
    "Se": 2.55,
    "Sr": 0.95,
    "Zr": 1.33,
    "Nb": 1.60,
    "Mo": 2.16,
    "Ag": 1.93,
    "Cd": 1.69,
    "In": 1.78,
    "Sn": 1.96,
    "Sb": 2.05,
    "Te": 2.10,
    "Ba": 0.89,
    "Hf": 1.30,
    "Ta": 1.50,
    "W": 2.36,
    "Pt": 2.28,
    "Au": 2.54,
    "Hg": 2.00,
    "Pb": 2.33,
    "Bi": 2.02,
}

COVALENT_RADII_PM = {
    "H": 31,
    "Li": 128,
    "B": 84,
    "C": 76,
    "N": 71,
    "O": 66,
    "F": 57,
    "Na": 166,
    "Mg": 141,
    "Al": 121,
    "Si": 111,
    "P": 107,
    "S": 105,
    "Cl": 102,
    "K": 203,
    "Ca": 176,
    "Sc": 170,
    "Ti": 160,
    "V": 153,
    "Cr": 139,
    "Mn": 139,
    "Fe": 132,
    "Co": 126,
    "Ni": 124,
    "Cu": 132,
    "Zn": 122,
    "Ga": 122,
    "Ge": 120,
    "As": 119,
    "Se": 120,
    "Sr": 195,
    "Zr": 175,
    "Nb": 164,
    "Mo": 154,
    "Ag": 145,
    "Cd": 144,
    "In": 142,
    "Sn": 139,
    "Sb": 139,
    "Te": 138,
    "Ba": 215,
    "Hf": 175,
    "Ta": 170,
    "W": 162,
    "Pt": 136,
    "Au": 136,
    "Hg": 132,
    "Pb": 146,
    "Bi": 148,
}

TOXIC_ELEMENTS = {"Pb", "Cd", "Hg", "As", "Be"}
SUPPLY_RISK_ELEMENTS = {"In", "Ga", "Ge", "Ta", "Hf", "Pt", "Ir", "Ru", "Rh", "Pd", "Co"}
TRANSITION_METALS = {
    "Sc",
    "Ti",
    "V",
    "Cr",
    "Mn",
    "Fe",
    "Co",
    "Ni",
    "Cu",
    "Zn",
    "Zr",
    "Nb",
    "Mo",
    "Ag",
    "Hf",
    "Ta",
    "W",
    "Pt",
    "Au",
}
POLYMER_ELEMENTS = {"C", "H", "O", "N", "F", "Si", "S", "Cl"}

PEROVSKITE_A_RADII_PM = {
    "Ba": 161.0,
    "Sr": 144.0,
    "Pb": 149.0,
    "K": 164.0,
    "Na": 139.0,
    "Bi": 136.0,
    "Ca": 134.0,
}

PEROVSKITE_B_RADII_PM = {
    "Ti": 60.5,
    "Zr": 72.0,
    "Nb": 64.0,
    "Ta": 64.0,
    "Sc": 74.5,
    "Al": 53.5,
}

OXIDE_ION_RADIUS_PM = 140.0

TOKEN_RE = re.compile(r"([A-Z][a-z]?|\(|\)|\d+(?:\.\d+)?)")


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def parse_formula(formula: str) -> dict[str, float]:
    """Parse a chemical formula into element counts.

    Supports nested parentheses and fractional stoichiometries, for example
    ``Pb(Zr0.52Ti0.48)O3``.
    """

    compact = formula.replace(" ", "")
    if not compact:
        raise ValueError("formula cannot be empty")

    tokens = TOKEN_RE.findall(compact)
    if "".join(tokens) != compact:
        raise ValueError(f"unsupported formula syntax: {formula}")

    def is_number(token: str) -> bool:
        return token[0].isdigit()

    def parse_group(index: int, closing: bool = False) -> tuple[dict[str, float], int]:
        counts: dict[str, float] = defaultdict(float)
        while index < len(tokens):
            token = tokens[index]
            if token == ")":
                if not closing:
                    raise ValueError(f"unmatched closing parenthesis in {formula}")
                return dict(counts), index + 1
            if token == "(":
                subgroup, index = parse_group(index + 1, closing=True)
                multiplier = 1.0
                if index < len(tokens) and is_number(tokens[index]):
                    multiplier = float(tokens[index])
                    index += 1
                for element, amount in subgroup.items():
                    counts[element] += amount * multiplier
                continue
            if is_number(token):
                raise ValueError(f"unexpected multiplier in {formula}")
            if token not in ATOMIC_WEIGHTS:
                raise ValueError(f"unknown element {token} in {formula}")
            index += 1
            amount = 1.0
            if index < len(tokens) and is_number(tokens[index]):
                amount = float(tokens[index])
                index += 1
            counts[token] += amount

        if closing:
            raise ValueError(f"unmatched opening parenthesis in {formula}")
        return dict(counts), index

    counts, final_index = parse_group(0)
    if final_index != len(tokens):
        raise ValueError(f"could not parse complete formula: {formula}")
    return counts


def molecular_weight(formula_or_counts: str | dict[str, float]) -> float:
    counts = parse_formula(formula_or_counts) if isinstance(formula_or_counts, str) else formula_or_counts
    return sum(ATOMIC_WEIGHTS[element] * amount for element, amount in counts.items())


def _weighted_mean(values: dict[str, float], counts: dict[str, float]) -> float:
    total = sum(counts.values())
    return sum(values[element] * amount for element, amount in counts.items()) / total


def _weighted_std(values: dict[str, float], counts: dict[str, float], mean: float) -> float:
    total = sum(counts.values())
    variance = sum(amount * (values[element] - mean) ** 2 for element, amount in counts.items()) / total
    return math.sqrt(variance)


def featurize_formula(formula: str) -> dict[str, float]:
    counts = parse_formula(formula)
    atoms = sum(counts.values())
    elements = set(counts)
    weight = molecular_weight(counts)
    mean_en = _weighted_mean(ELECTRONEGATIVITY, counts)
    std_en = _weighted_std(ELECTRONEGATIVITY, counts, mean_en)
    en_values = [ELECTRONEGATIVITY[element] for element in counts]
    radius_mean = _weighted_mean(COVALENT_RADII_PM, counts)
    transition_fraction = sum(counts.get(element, 0.0) for element in TRANSITION_METALS) / atoms
    polymer_fraction = sum(counts.get(element, 0.0) for element in POLYMER_ELEMENTS) / atoms
    toxic_fraction = sum(counts.get(element, 0.0) for element in TOXIC_ELEMENTS) / atoms
    supply_risk_fraction = sum(counts.get(element, 0.0) for element in SUPPLY_RISK_ELEMENTS) / atoms
    oxygen_fraction = counts.get("O", 0.0) / atoms
    halogen_fraction = sum(counts.get(element, 0.0) for element in ("F", "Cl")) / atoms

    density_proxy = clamp((weight / atoms) / max(radius_mean, 1.0) * 2.0, 0.05, 1.0)
    ionic_contrast = max(en_values) - min(en_values)
    perovskite = estimate_perovskite_descriptors(counts)

    return {
        "num_elements": float(len(elements)),
        "atoms_per_formula": atoms,
        "molecular_weight": weight,
        "mean_electronegativity": mean_en,
        "std_electronegativity": std_en,
        "ionic_contrast": ionic_contrast,
        "mean_covalent_radius_pm": radius_mean,
        "transition_metal_fraction": transition_fraction,
        "polymer_element_fraction": polymer_fraction,
        "oxygen_fraction": oxygen_fraction,
        "halogen_fraction": halogen_fraction,
        "toxic_fraction": toxic_fraction,
        "supply_risk_fraction": supply_risk_fraction,
        "density_proxy": density_proxy,
        "lightness_score": 1.0 - density_proxy,
        **perovskite,
    }


def estimate_perovskite_descriptors(counts: dict[str, float]) -> dict[str, float]:
    oxygen = counts.get("O", 0.0)
    if not math.isclose(oxygen, 3.0, rel_tol=0.0, abs_tol=0.08):
        return {
            "perovskite_tolerance_factor": 0.0,
            "octahedral_factor": 0.0,
            "perovskite_stability_score": 0.0,
            "a_site_count": 0.0,
            "b_site_count": 0.0,
        }

    a_count = sum(amount for element, amount in counts.items() if element in PEROVSKITE_A_RADII_PM)
    b_count = sum(amount for element, amount in counts.items() if element in PEROVSKITE_B_RADII_PM)
    if not math.isclose(a_count, 1.0, rel_tol=0.0, abs_tol=0.15) or not math.isclose(
        b_count, 1.0, rel_tol=0.0, abs_tol=0.15
    ):
        return {
            "perovskite_tolerance_factor": 0.0,
            "octahedral_factor": 0.0,
            "perovskite_stability_score": 0.0,
            "a_site_count": round(a_count, 3),
            "b_site_count": round(b_count, 3),
        }

    r_a = sum(
        PEROVSKITE_A_RADII_PM[element] * amount
        for element, amount in counts.items()
        if element in PEROVSKITE_A_RADII_PM
    ) / a_count
    r_b = sum(
        PEROVSKITE_B_RADII_PM[element] * amount
        for element, amount in counts.items()
        if element in PEROVSKITE_B_RADII_PM
    ) / b_count
    tolerance = (r_a + OXIDE_ION_RADIUS_PM) / (math.sqrt(2.0) * (r_b + OXIDE_ION_RADIUS_PM))
    octahedral = r_b / OXIDE_ION_RADIUS_PM
    tolerance_fit = 1.0 - abs(tolerance - 1.0) / 0.18
    octahedral_fit = 1.0 - abs(octahedral - 0.46) / 0.12
    stability = clamp(0.65 * tolerance_fit + 0.35 * octahedral_fit)
    return {
        "perovskite_tolerance_factor": round(tolerance, 3),
        "octahedral_factor": round(octahedral, 3),
        "perovskite_stability_score": round(stability, 3),
        "a_site_count": round(a_count, 3),
        "b_site_count": round(b_count, 3),
    }


def estimate_material_properties(formula: str, domain: str) -> dict[str, float]:
    features = featurize_formula(formula)
    counts = parse_formula(formula)
    elements = set(counts)

    oxide_bonus = 0.22 if features["oxygen_fraction"] > 0.25 else 0.0
    halide_bonus = 0.12 if features["halogen_fraction"] > 0.10 else 0.0
    transition_penalty = 0.18 * features["transition_metal_fraction"]
    bandgap_proxy_ev = clamp(
        0.55 + 1.55 * features["ionic_contrast"] + oxide_bonus + halide_bonus - transition_penalty,
        0.0,
        8.5,
    )
    optical_score = clamp((bandgap_proxy_ev - 2.2) / 3.2 + 0.10 * features["oxygen_fraction"])
    stability_score = clamp(
        0.50
        + 0.30 * features["oxygen_fraction"]
        + 0.10 * features["halogen_fraction"]
        - 0.30 * features["toxic_fraction"]
    )
    resource_score = clamp(1.0 - 1.8 * features["supply_risk_fraction"] - 1.5 * features["toxic_fraction"])
    toxicity_score = clamp(2.2 * features["toxic_fraction"])
    hpc_cost_hours = round(0.15 + 0.08 * features["atoms_per_formula"] + 0.18 * features["num_elements"], 3)

    perovskite_like = features["perovskite_tolerance_factor"] > 0.0 or (
        {"Ba", "Sr", "Pb"} & elements and "Ti" in elements and "O" in elements
    )
    fluoropolymer_like = {"C", "F"} <= elements
    silicone_like = {"Si", "O", "C", "H"} <= elements
    shape_memory_like = {"Ni", "Ti"} <= elements

    piezoelectric_score = clamp(
        (0.82 if perovskite_like else 0.12)
        + (0.18 if "Zr" in elements else 0.0)
        + 0.18 * features["perovskite_stability_score"]
        + (0.16 if fluoropolymer_like else 0.0)
        - 0.22 * toxicity_score
    )
    strain_score = clamp(
        (0.42 if perovskite_like else 0.0)
        + (0.64 if fluoropolymer_like or silicone_like else 0.0)
        + (0.72 if shape_memory_like else 0.0)
        + 0.10 * features["polymer_element_fraction"]
    )
    processability_score = clamp(
        0.45
        + 0.35 * features["polymer_element_fraction"]
        + 0.15 * features["lightness_score"]
        - 0.10 * features["num_elements"] / 5.0
    )
    modulus_proxy = clamp(
        0.30 + 0.45 * features["oxygen_fraction"] + 0.22 * features["transition_metal_fraction"]
    )

    if domain == "ar_glasses":
        domain_score = (
            0.35 * optical_score
            + 0.20 * features["lightness_score"]
            + 0.18 * stability_score
            + 0.15 * resource_score
            + 0.12 * modulus_proxy
        )
    elif domain == "robotics_actuator":
        domain_score = (
            0.35 * piezoelectric_score
            + 0.25 * strain_score
            + 0.16 * processability_score
            + 0.14 * stability_score
            + 0.10 * (1.0 - toxicity_score)
        )
    else:
        domain_score = (
            0.25 * optical_score
            + 0.25 * piezoelectric_score
            + 0.20 * stability_score
            + 0.15 * processability_score
            + 0.15 * resource_score
        )

    return {
        **features,
        "bandgap_proxy_ev": round(bandgap_proxy_ev, 3),
        "optical_score": round(optical_score, 3),
        "stability_score": round(stability_score, 3),
        "resource_score": round(resource_score, 3),
        "toxicity_score": round(toxicity_score, 3),
        "hpc_cost_hours": hpc_cost_hours,
        "piezoelectric_score": round(piezoelectric_score, 3),
        "strain_score": round(strain_score, 3),
        "processability_score": round(processability_score, 3),
        "modulus_proxy": round(modulus_proxy, 3),
        "domain_score": round(clamp(domain_score), 3),
    }
