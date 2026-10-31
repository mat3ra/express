import json
from typing import Any, Dict, List, Optional

import numpy as np

from express.parsers import BaseParser
from express.parsers.apps.q3.settings import RESULTS_FILE_SUFFIX
from express.parsers.mixins.electronic import ElectronicDataMixin
from express.parsers.mixins.ionic import IonicDataMixin
from express.parsers.mixins.reciprocal import ReciprocalDataMixin
from express.parsers.settings import Constant
from express.parsers.utils import find_file

# Express returns energies in eV and forces in eV/angstrom. Q3 writes each
# quantity as an ESSE record whose units field names the source unit
# (schemas/q3/results.json). A k-point channel with no spin is spin-up:
# express looks channels up as 0.5 and then -0.5.
ENERGY_UNIT_IN_ELECTRONVOLTS = {
    "Ry": Constant.Ry,
    "hartree": Constant.Ha,
    "eV": Constant.eV,
}
FORCE_UNIT_IN_ELECTRONVOLT_PER_ANGSTROM = {
    "Ry/a.u.": Constant.ry_bohr_to_eV_A,
    "eV/angstrom": 1.0,
}
CHANNEL_SPIN = (0.5, -0.5)


def property_record(results: Dict[str, Any], record_name: str) -> Dict[str, Any]:
    """
    The ESSE record named record_name under properties.records.
    """
    for record in results["properties"]["records"]:
        if record.get("name") == record_name:
            return record
    raise KeyError(f"q3 results have no '{record_name}' record under properties.records")


def conversion_factor(units: str, factors: Dict[str, float], quantity_name: str) -> float:
    """
    The multiplier that takes a value in units into the unit express returns.
    """
    factor = factors.get(units)
    if factor is None:
        raise ValueError(f"q3 {quantity_name} record uses unsupported units '{units}'")
    return factor


def energy_in_electronvolts(record: Dict[str, Any]) -> float:
    """
    An ESSE energy record converted to eV.
    """
    factor = conversion_factor(record["units"], ENERGY_UNIT_IN_ELECTRONVOLTS, record.get("name", "energy"))
    return record["value"] * factor


def energy_contributions_in_electronvolts(record: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    ESSE total_energy_contributions terms, each value converted to eV.
    """
    contributions = {}
    for key, term in record.items():
        if not isinstance(term, dict) or "value" not in term:
            continue
        units = term.get("units", record["units"])
        factor = conversion_factor(units, ENERGY_UNIT_IN_ELECTRONVOLTS, key)
        contributions[key] = {"name": term.get("name", key), "value": term["value"] * factor}
    return contributions


def convergence_energies_in_electronvolts(record: Dict[str, Any]) -> List[List[float]]:
    """
    Total energy after each SCF iteration, in eV, one row per ionic step.
    """
    factor = conversion_factor(record["units"], ENERGY_UNIT_IN_ELECTRONVOLTS, record["name"])
    rows = record["data"]
    if rows and not isinstance(rows[0], list):
        rows = [rows]
    return [[energy * factor for energy in row] for row in rows]


def value_in_kilobar(record: Dict[str, Any]):
    """
    A pressure or stress record. Express keeps these in kbar.
    """
    if record["units"] != "kbar":
        raise ValueError(f"q3 {record.get('name')} record uses unsupported units '{record['units']}'")
    return record["value"]


def atomic_forces_in_electronvolt_per_angstrom(record: Dict[str, Any]) -> List[List[float]]:
    """
    Forces ordered by atom id, in eV/angstrom.
    """
    factor = conversion_factor(record["units"], FORCE_UNIT_IN_ELECTRONVOLT_PER_ANGSTROM, record["name"])
    ordered_atoms = sorted(record["values"], key=lambda atom: atom["id"])
    return [[component * factor for component in atom["value"]] for atom in ordered_atoms]


def channel_spin(channel: Dict[str, Any], channel_index: int) -> float:
    """
    The channel's spin, or the express spin for that position when Q3 omitted it.
    """
    if "spin" in channel:
        return channel["spin"]
    if channel_index >= len(CHANNEL_SPIN):
        raise ValueError(f"q3 eigenvalue channel {channel_index} has no spin")
    return CHANNEL_SPIN[channel_index]


def eigenvalues_at_kpoint(kpoint: Dict[str, Any], energy_factor: float) -> Dict[str, Any]:
    """
    One k-point's eigenvalues, energies in eV.
    """
    channels = []
    for channel_index, channel in enumerate(kpoint["eigenvalues"]):
        channels.append(
            {
                "energies": [energy * energy_factor for energy in channel["energies"]],
                "occupations": list(channel.get("occupations") or []),
                "spin": channel_spin(channel, channel_index),
            }
        )
    return {"kpoint": list(kpoint["kpoint"]), "weight": kpoint["weight"], "eigenvalues": channels}


def eigenvalues_in_electronvolts(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    eigenvalues_at_kpoints with energies in eV.
    """
    factor = conversion_factor(record["units"], ENERGY_UNIT_IN_ELECTRONVOLTS, record["name"])
    return [eigenvalues_at_kpoint(kpoint, factor) for kpoint in record["values"]]


def lattice_vectors_from_material(material: Dict[str, Any]) -> Dict[str, Any]:
    """
    Lattice vectors in angstrom, the shape lattice_basis_to_poscar reads.
    """
    vectors = material["lattice"]["vectors"]
    return {
        "vectors": {
            "a": list(vectors["a"]),
            "b": list(vectors["b"]),
            "c": list(vectors["c"]),
            "alat": material["lattice"]["a"],
        },
        "units": "angstrom",
    }


def basis_from_material(material: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crystal basis with ids starting at 0, ordered as in the material.
    """
    basis = material["basis"]
    elements = sorted(basis["elements"], key=lambda element: element["id"])
    coordinates = sorted(basis["coordinates"], key=lambda coordinate: coordinate["id"])
    return {
        "units": basis.get("units", "crystal"),
        "elements": [{"id": index, "value": element["value"]} for index, element in enumerate(elements)],
        "coordinates": [
            {"id": index, "value": list(coordinate["value"])} for index, coordinate in enumerate(coordinates)
        ],
    }


class Q3Parser(BaseParser, IonicDataMixin, ElectronicDataMixin, ReciprocalDataMixin):
    """
    Q3 parser class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.work_dir = self.kwargs["work_dir"]
        self._results: Optional[Dict[str, Any]] = None

    def _get_results(self) -> Dict[str, Any]:
        """
        Loads and caches the contents of q3's "<outdir>/<prefix>_results.json" file.

        Reference: lib/q3/docs/io_reference.md, section 4.1, and schemas/q3/results.json.
        """
        if self._results is None:
            results_file = find_file(RESULTS_FILE_SUFFIX, self.work_dir)
            if not results_file:
                raise FileNotFoundError(
                    f"Could not find a q3 results file (*{RESULTS_FILE_SUFFIX}) under {self.work_dir}"
                )
            with open(results_file) as results_handle:
                self._results = json.load(results_handle)
        return self._results

    def _material(self) -> Dict[str, Any]:
        """
        The structure the run computed.
        """
        return self._get_results()["structure"]["material"]

    def total_energy(self):
        """
        Returns total energy.

        Reference:
            func: express.parsers.mixins.electronic.ElectronicDataMixin.total_energy
        """
        return energy_in_electronvolts(property_record(self._get_results(), "total_energy"))

    def fermi_energy(self):
        """
        Returns fermi energy.

        Reference:
            func: express.parsers.mixins.electronic.ElectronicDataMixin.fermi_energy
        """
        return energy_in_electronvolts(property_record(self._get_results(), "fermi_energy"))

    def nspins(self):
        """
        Returns the number of spin channels written for each k-point.

        Reference:
            func: express.parsers.mixins.electronic.ElectronicDataMixin.nspins
        """
        record = property_record(self._get_results(), "eigenvalues_at_kpoints")
        return max(len(kpoint["eigenvalues"]) for kpoint in record["values"])

    def eigenvalues_at_kpoints(self):
        """
        Returns eigenvalues for all kpoints.

        Reference:
            func: express.parsers.mixins.electronic.ElectronicDataMixin.eigenvalues_at_kpoints
        """
        return eigenvalues_in_electronvolts(property_record(self._get_results(), "eigenvalues_at_kpoints"))

    def convergence_electronic(self):
        """
        Extracts convergence electronic.

        Reference:
            func: express.parsers.mixins.electronic.ElectronicDataMixin.convergence_electronic
        """
        record = property_record(self._get_results(), "convergence_electronic")
        return convergence_energies_in_electronvolts(record)

    def total_energy_contributions(self):
        """
        Extracts total energy contributions.

        Reference:
            func: express.parsers.mixins.electronic.ElectronicDataMixin.total_energy_contributions
        """
        record = property_record(self._get_results(), "total_energy_contributions")
        return energy_contributions_in_electronvolts(record)

    def ibz_k_points(self):
        """
        Returns ibz_k_points.

        Reference:
            func: express.parsers.mixins.reciprocal.ReciprocalDataMixin.ibz_k_points
        """
        return np.array([kpoint["kpoint"] for kpoint in self.eigenvalues_at_kpoints()])

    def pressure(self):
        """
        Returns pressure.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.pressure
        """
        return value_in_kilobar(property_record(self._get_results(), "pressure"))

    def stress_tensor(self):
        """
        Returns stress tensor.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.stress_tensor
        """
        return value_in_kilobar(property_record(self._get_results(), "stress_tensor"))

    def atomic_forces(self):
        """
        Returns forces that is exerted on each atom by its surroundings.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.atomic_forces
        """
        record = property_record(self._get_results(), "atomic_forces")
        return atomic_forces_in_electronvolt_per_angstrom(record)

    def initial_lattice_vectors(self):
        """
        Returns initial lattice vectors.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.initial_lattice_vectors
        """
        return lattice_vectors_from_material(self._material())

    def final_lattice_vectors(self):
        """
        Returns final lattice vectors.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.final_lattice_vectors
        """
        return self.initial_lattice_vectors()

    def initial_basis(self):
        """
        Returns initial basis.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.initial_basis
        """
        return basis_from_material(self._material())

    def final_basis(self):
        """
        Returns final basis.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.final_basis
        """
        return self.initial_basis()
