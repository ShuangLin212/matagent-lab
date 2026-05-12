from __future__ import annotations

import json
import math
from dataclasses import dataclass
from fractions import Fraction
from functools import reduce
from pathlib import Path

from .chemistry import (
    ATOMIC_WEIGHTS,
    PEROVSKITE_A_RADII_PM,
    PEROVSKITE_B_RADII_PM,
    molecular_weight,
    parse_formula,
)


@dataclass(frozen=True)
class AtomSite:
    element: str
    fractional: tuple[float, float, float]


@dataclass(frozen=True)
class PreparedStructure:
    formula: str
    prototype: str
    lattice: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]
    sites: tuple[AtomSite, ...]
    integer_counts: dict[str, int]
    source_counts: dict[str, float]
    warnings: tuple[str, ...] = ()

    @property
    def elements(self) -> list[str]:
        return list(self.integer_counts)

    @property
    def natoms(self) -> int:
        return len(self.sites)


@dataclass(frozen=True)
class PreparedInputSet:
    engine: str
    directory: Path
    files: tuple[Path, ...]
    metadata: dict


def build_structure(
    formula: str,
    prototype: str = "auto",
    lattice_a: float | None = None,
    max_atoms: int = 96,
) -> PreparedStructure:
    """Create a simple crystal structure suitable for input-deck scaffolding.

    The builder favors readable, deterministic prototypes over physical claims.
    Simple ABO3 compositions become a five-atom cubic perovskite cell. Other
    formulas are placed on a regular cubic grid after fractional stoichiometry is
    converted to a bounded integer cell.
    """

    source_counts = parse_formula(formula)
    integer_counts, warnings = integerize_counts(source_counts, max_atoms=max_atoms)
    requested = prototype.lower()
    if requested not in {"auto", "perovskite", "cubic"}:
        raise ValueError("prototype must be one of: auto, perovskite, cubic")

    if requested in {"auto", "perovskite"} and _is_simple_abo3(source_counts, integer_counts):
        return _build_perovskite_structure(formula, source_counts, integer_counts, lattice_a, warnings)

    if requested == "perovskite":
        warnings = (
            *warnings,
            "Fell back to a cubic packing because the formula is not a simple five-atom ABO3 cell.",
        )
    return _build_cubic_grid_structure(formula, source_counts, integer_counts, lattice_a, warnings)


def integerize_counts(
    counts: dict[str, float],
    max_denominator: int = 24,
    max_atoms: int = 96,
) -> tuple[dict[str, int], tuple[str, ...]]:
    warnings: list[str] = []
    fractions = {
        element: Fraction(str(round(amount, 8))).limit_denominator(max_denominator)
        for element, amount in counts.items()
    }
    scale = reduce(_lcm, (fraction.denominator for fraction in fractions.values()), 1)
    integer_counts = {
        element: max(1, int(fraction.numerator * scale / fraction.denominator))
        for element, fraction in fractions.items()
    }

    total_atoms = sum(integer_counts.values())
    if total_atoms > max_atoms:
        compression = max_atoms / total_atoms
        integer_counts = {
            element: max(1, int(round(amount * compression)))
            for element, amount in integer_counts.items()
        }
        warnings.append(
            f"Fractional stoichiometry was compressed from {total_atoms} to "
            f"{sum(integer_counts.values())} atoms for a practical prototype cell."
        )

    return integer_counts, tuple(warnings)


def write_vasp_inputs(
    formula: str,
    directory: str | Path,
    *,
    prototype: str = "auto",
    lattice_a: float | None = None,
    kpoints: tuple[int, int, int] = (4, 4, 4),
    encut: int = 520,
    relax: bool = True,
    bands: bool = False,
) -> PreparedInputSet:
    structure = build_structure(formula, prototype=prototype, lattice_a=lattice_a)
    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "POSCAR": _format_poscar(structure),
        "INCAR": _format_incar(structure, encut=encut, relax=relax, bands=bands),
        "KPOINTS": _format_vasp_kpoints(kpoints),
        "POTCAR.spec": _format_potcar_spec(structure),
        "README.md": _format_input_readme("vasp", structure),
    }
    written = _write_named_files(output_dir, files)
    metadata = _input_metadata("vasp", structure, written, {"kpoints": kpoints, "encut": encut})
    metadata_path = output_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return PreparedInputSet("vasp", output_dir, (*written, metadata_path), metadata)


def write_quantum_espresso_inputs(
    formula: str,
    directory: str | Path,
    *,
    prototype: str = "auto",
    lattice_a: float | None = None,
    kpoints: tuple[int, int, int] = (4, 4, 4),
    ecutwfc: float = 60.0,
    ecutrho: float = 480.0,
    relax: bool = True,
    pseudo_dir: str = "./pseudo",
) -> PreparedInputSet:
    structure = build_structure(formula, prototype=prototype, lattice_a=lattice_a)
    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "pw.in": _format_qe_input(
            structure,
            kpoints=kpoints,
            ecutwfc=ecutwfc,
            ecutrho=ecutrho,
            relax=relax,
            pseudo_dir=pseudo_dir,
        ),
        "pseudo.spec": _format_qe_pseudo_spec(structure, pseudo_dir),
        "README.md": _format_input_readme("quantum_espresso", structure),
    }
    written = _write_named_files(output_dir, files)
    metadata = _input_metadata(
        "quantum_espresso",
        structure,
        written,
        {"kpoints": kpoints, "ecutwfc": ecutwfc, "ecutrho": ecutrho, "pseudo_dir": pseudo_dir},
    )
    metadata_path = output_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return PreparedInputSet("quantum_espresso", output_dir, (*written, metadata_path), metadata)


def write_lammps_inputs(
    formula: str,
    directory: str | Path,
    *,
    prototype: str = "auto",
    lattice_a: float | None = None,
    potential: str = "reaxff",
    potential_file: str = "ffield.reax",
    temperature: float = 300.0,
    steps: int = 50000,
    timestep_fs: float = 0.25,
    chemical_potentials: dict[str, float] | None = None,
) -> PreparedInputSet:
    structure = build_structure(formula, prototype=prototype, lattice_a=lattice_a)
    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    chemical_potentials = chemical_potentials or {}
    replicate = _lammps_replicate_factors(structure, potential)

    files = {
        "structure.data": _format_lammps_data(structure),
        "in.lammps": _format_lammps_input(
            structure,
            potential=potential,
            potential_file=potential_file,
            temperature=temperature,
            steps=steps,
            timestep_fs=timestep_fs,
            chemical_potentials=chemical_potentials,
            replicate=replicate,
        ),
        "chemical_potentials.json": json.dumps(chemical_potentials, indent=2) + "\n",
        "README.md": _format_input_readme("lammps", structure),
    }
    written = _write_named_files(output_dir, files)
    metadata = _input_metadata(
        "lammps",
        structure,
        written,
        {
            "potential": potential,
            "potential_file": potential_file,
            "temperature": temperature,
            "steps": steps,
            "timestep_fs": timestep_fs,
            "chemical_potentials": chemical_potentials,
            "replicate": replicate,
        },
    )
    metadata_path = output_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return PreparedInputSet("lammps", output_dir, (*written, metadata_path), metadata)


def parse_chemical_potentials(values: list[str] | None) -> dict[str, float]:
    potentials: dict[str, float] = {}
    for value in values or []:
        if "=" not in value:
            raise ValueError(f"chemical potential must look like Element=value, got {value!r}")
        element, raw = value.split("=", 1)
        element = element.strip()
        if not element:
            raise ValueError(f"chemical potential has an empty element label: {value!r}")
        potentials[element] = float(raw)
    return potentials


def _build_perovskite_structure(
    formula: str,
    source_counts: dict[str, float],
    integer_counts: dict[str, int],
    lattice_a: float | None,
    warnings: tuple[str, ...],
) -> PreparedStructure:
    a_site = next(element for element in source_counts if element in PEROVSKITE_A_RADII_PM)
    b_site = next(element for element in source_counts if element in PEROVSKITE_B_RADII_PM)
    a = lattice_a or _estimate_perovskite_lattice_a(a_site, b_site)
    lattice = ((a, 0.0, 0.0), (0.0, a, 0.0), (0.0, 0.0, a))
    sites = (
        AtomSite(a_site, (0.0, 0.0, 0.0)),
        AtomSite(b_site, (0.5, 0.5, 0.5)),
        AtomSite("O", (0.5, 0.5, 0.0)),
        AtomSite("O", (0.5, 0.0, 0.5)),
        AtomSite("O", (0.0, 0.5, 0.5)),
    )
    counts = {a_site: 1, b_site: 1, "O": 3}
    return PreparedStructure(formula, "cubic_perovskite", lattice, sites, counts, source_counts, warnings)


def _build_cubic_grid_structure(
    formula: str,
    source_counts: dict[str, float],
    integer_counts: dict[str, int],
    lattice_a: float | None,
    warnings: tuple[str, ...],
) -> PreparedStructure:
    species = [
        element
        for element, count in integer_counts.items()
        for _ in range(count)
    ]
    grid = math.ceil(len(species) ** (1.0 / 3.0))
    a = lattice_a or max(6.0, 2.35 * grid)
    lattice = ((a, 0.0, 0.0), (0.0, a, 0.0), (0.0, 0.0, a))
    sites: list[AtomSite] = []
    for index, element in enumerate(species):
        ix = index % grid
        iy = (index // grid) % grid
        iz = index // (grid * grid)
        sites.append(
            AtomSite(
                element,
                (
                    (ix + 0.5) / grid,
                    (iy + 0.5) / grid,
                    (iz + 0.5) / grid,
                ),
            )
        )
    return PreparedStructure(formula, "cubic_grid", lattice, tuple(sites), integer_counts, source_counts, warnings)


def _is_simple_abo3(source_counts: dict[str, float], integer_counts: dict[str, int]) -> bool:
    if integer_counts.get("O") != 3 or sum(integer_counts.values()) != 5:
        return False
    a_sites = [element for element, amount in source_counts.items() if element in PEROVSKITE_A_RADII_PM and amount > 0]
    b_sites = [element for element, amount in source_counts.items() if element in PEROVSKITE_B_RADII_PM and amount > 0]
    return len(a_sites) == 1 and len(b_sites) == 1


def _estimate_perovskite_lattice_a(a_site: str, b_site: str) -> float:
    r_a = PEROVSKITE_A_RADII_PM.get(a_site, 145.0)
    r_b = PEROVSKITE_B_RADII_PM.get(b_site, 64.0)
    return round(max(3.65, (r_a + r_b + 280.0) / 125.0), 3)


def _format_poscar(structure: PreparedStructure) -> str:
    lines = [f"MatAgent Lab {structure.formula} {structure.prototype}", "1.0"]
    lines.extend(_format_vector(vector) for vector in structure.lattice)
    lines.append(" ".join(structure.elements))
    lines.append(" ".join(str(structure.integer_counts[element]) for element in structure.elements))
    lines.append("Direct")
    for element in structure.elements:
        for site in structure.sites:
            if site.element == element:
                lines.append(_format_vector(site.fractional))
    return "\n".join(lines) + "\n"


def _format_incar(
    structure: PreparedStructure,
    *,
    encut: int,
    relax: bool,
    bands: bool,
) -> str:
    lines = [
        f"SYSTEM = {structure.formula}",
        "PREC = Accurate",
        f"ENCUT = {encut}",
        "EDIFF = 1E-6",
        "ISMEAR = 0",
        "SIGMA = 0.05",
        "LREAL = Auto",
        "LWAVE = .FALSE.",
        "LCHARG = .FALSE.",
    ]
    if relax:
        lines.extend(["IBRION = 2", "NSW = 80", "ISIF = 3"])
    else:
        lines.extend(["IBRION = -1", "NSW = 0"])
    if bands:
        lines.append("# After relaxation, run a static SCF and line-mode KPOINTS for bands.")
    return "\n".join(lines) + "\n"


def _format_vasp_kpoints(kpoints: tuple[int, int, int]) -> str:
    return "\n".join(
        [
            "MatAgent Lab automatic mesh",
            "0",
            "Gamma",
            f"{kpoints[0]} {kpoints[1]} {kpoints[2]}",
            "0 0 0",
            "",
        ]
    )


def _format_potcar_spec(structure: PreparedStructure) -> str:
    lines = [
        "# VASP POTCAR files are licensed separately; concatenate matching PAW datasets in this order.",
    ]
    lines.extend(f"{element}  {element}" for element in structure.elements)
    return "\n".join(lines) + "\n"


def _format_qe_input(
    structure: PreparedStructure,
    *,
    kpoints: tuple[int, int, int],
    ecutwfc: float,
    ecutrho: float,
    relax: bool,
    pseudo_dir: str,
) -> str:
    calculation = "vc-relax" if relax else "scf"
    prefix = _safe_name(structure.formula)
    lines = [
        "&CONTROL",
        f"  calculation = '{calculation}',",
        f"  prefix = '{prefix}',",
        f"  pseudo_dir = '{pseudo_dir}',",
        "  outdir = './tmp',",
        "/",
        "&SYSTEM",
        "  ibrav = 0,",
        f"  nat = {structure.natoms},",
        f"  ntyp = {len(structure.elements)},",
        f"  ecutwfc = {ecutwfc:.1f},",
        f"  ecutrho = {ecutrho:.1f},",
        "  occupations = 'fixed',",
        "/",
        "&ELECTRONS",
        "  conv_thr = 1.0d-8,",
        "/",
    ]
    if relax:
        lines.extend(["&IONS", "/", "&CELL", "/"])
    lines.append("ATOMIC_SPECIES")
    for element in structure.elements:
        lines.append(f"  {element} {ATOMIC_WEIGHTS[element]:.6f} {element}.pbe.UPF")
    lines.append("CELL_PARAMETERS angstrom")
    lines.extend(f"  {_format_vector(vector)}" for vector in structure.lattice)
    lines.append("ATOMIC_POSITIONS crystal")
    for site in structure.sites:
        lines.append(f"  {site.element} {_format_vector(site.fractional)}")
    lines.extend(["K_POINTS automatic", f"  {kpoints[0]} {kpoints[1]} {kpoints[2]} 0 0 0", ""])
    return "\n".join(lines)


def _format_qe_pseudo_spec(structure: PreparedStructure, pseudo_dir: str) -> str:
    lines = [f"# Put these UPF files under {pseudo_dir} or edit pw.in to match your local library."]
    lines.extend(f"{element}.pbe.UPF" for element in structure.elements)
    return "\n".join(lines) + "\n"


def _format_lammps_data(structure: PreparedStructure) -> str:
    a, b, c = structure.lattice[0][0], structure.lattice[1][1], structure.lattice[2][2]
    element_to_type = {element: index + 1 for index, element in enumerate(structure.elements)}
    lines = [
        f"MatAgent Lab structure for {structure.formula}",
        "",
        f"{structure.natoms} atoms",
        f"{len(structure.elements)} atom types",
        "",
        f"0.0 {a:.8f} xlo xhi",
        f"0.0 {b:.8f} ylo yhi",
        f"0.0 {c:.8f} zlo zhi",
        "",
        "Masses",
        "",
    ]
    for element in structure.elements:
        lines.append(f"{element_to_type[element]} {ATOMIC_WEIGHTS[element]:.6f} # {element}")
    lines.extend(["", "Atoms # charge", ""])
    for index, site in enumerate(structure.sites, start=1):
        x = site.fractional[0] * a
        y = site.fractional[1] * b
        z = site.fractional[2] * c
        lines.append(f"{index} {element_to_type[site.element]} 0.0 {x:.8f} {y:.8f} {z:.8f} # {site.element}")
    return "\n".join(lines) + "\n"


def _format_lammps_input(
    structure: PreparedStructure,
    *,
    potential: str,
    potential_file: str,
    temperature: float,
    steps: int,
    timestep_fs: float,
    chemical_potentials: dict[str, float],
    replicate: tuple[int, int, int],
) -> str:
    potential_key = potential.lower()
    lines = [
        f"# MatAgent Lab MD deck for {structure.formula}",
        "units real",
        "atom_style charge",
        "boundary p p p",
        "read_data structure.data",
    ]
    if replicate != (1, 1, 1):
        lines.append(f"replicate {replicate[0]} {replicate[1]} {replicate[2]}")
    lines.extend(
        [
            "",
            f"variable T equal {temperature:.6g}",
            f"variable nsteps equal {steps}",
            f"timestep {timestep_fs:.6g}",
        ]
    )
    for element, value in chemical_potentials.items():
        lines.append(f"variable mu_{element} equal {value:.8g}")
    lines.extend(["", "neighbor 2.0 bin", "neigh_modify every 10 delay 0 check yes", ""])

    if potential_key in {"reaxff", "reax/c", "reax"}:
        lines.extend(
            [
                "pair_style reaxff NULL",
                f"pair_coeff * * {potential_file} {' '.join(structure.elements)}",
                "fix charges all qeq/reaxff 1 0.0 10.0 1.0e-6 reaxff",
            ]
        )
    elif potential_key == "lj":
        lines.extend(["pair_style lj/cut 10.0", "pair_coeff * * 0.10 3.00"])
    elif potential_key == "eam":
        lines.extend(["pair_style eam/alloy", f"pair_coeff * * {potential_file} {' '.join(structure.elements)}"])
    elif potential_key == "tersoff":
        lines.extend(["pair_style tersoff", f"pair_coeff * * {potential_file} {' '.join(structure.elements)}"])
    else:
        raise ValueError("potential must be one of: reaxff, lj, eam, tersoff")

    lines.extend(
        [
            "",
            "thermo 100",
            "thermo_style custom step temp pe ke etotal press vol",
            "velocity all create ${T} 20260512 mom yes rot yes dist gaussian",
            "fix ensemble all nvt temp ${T} ${T} 100.0",
            "dump traj all custom 500 trajectory.lammpstrj id type q x y z",
            "run ${nsteps}",
            "write_data final.data",
            "",
        ]
    )
    if chemical_potentials:
        lines.append(
            "# mu_* variables are exposed for reactive/GCMC extensions, sensitivity sweeps, or custom fixes."
        )
    return "\n".join(lines) + "\n"


def _lammps_replicate_factors(structure: PreparedStructure, potential: str) -> tuple[int, int, int]:
    if potential.lower() not in {"reaxff", "reax/c", "reax"}:
        return 1, 1, 1
    minimum_length = 10.5
    lengths = (structure.lattice[0][0], structure.lattice[1][1], structure.lattice[2][2])
    return tuple(max(1, math.ceil(minimum_length / length)) for length in lengths)


def _format_input_readme(engine: str, structure: PreparedStructure) -> str:
    return "\n".join(
        [
            f"# {engine} input deck for {structure.formula}",
            "",
            f"Prototype: {structure.prototype}",
            f"Atoms in generated cell: {structure.natoms}",
            f"Formula mass: {molecular_weight(structure.source_counts):.3f} g/mol",
            "",
            "These files are generated by MatAgent Lab as launch-ready scaffolds.",
            "Check pseudopotentials, force-field files, convergence settings, and prototype choice before production use.",
            "",
        ]
    )


def _input_metadata(
    engine: str,
    structure: PreparedStructure,
    files: tuple[Path, ...],
    settings: dict,
) -> dict:
    return {
        "engine": engine,
        "formula": structure.formula,
        "prototype": structure.prototype,
        "natoms": structure.natoms,
        "elements": structure.elements,
        "integer_counts": structure.integer_counts,
        "source_counts": structure.source_counts,
        "warnings": list(structure.warnings),
        "settings": settings,
        "files": [path.name for path in files],
    }


def _write_named_files(directory: Path, files: dict[str, str]) -> tuple[Path, ...]:
    written: list[Path] = []
    for name, content in files.items():
        path = directory / name
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return tuple(written)


def _format_vector(vector: tuple[float, float, float]) -> str:
    return f"{vector[0]:.10f} {vector[1]:.10f} {vector[2]:.10f}"


def _safe_name(formula: str) -> str:
    return "".join(character for character in formula if character.isalnum()) or "material"


def _lcm(left: int, right: int) -> int:
    return abs(left * right) // math.gcd(left, right)
