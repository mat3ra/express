import os
from pathlib import Path
from typing import Dict, Optional

import numpy as np

from express.parsers import BaseParser
from express.parsers.apps.espresso import settings
from express.parsers.apps.espresso.formats.txt import EspressoTXTParser
from express.parsers.apps.espresso.formats.xml.xml_factory import get_xml_parser
from express.parsers.apps.espresso.settings import NEB_PATH_FILE_SUFFIX
from express.parsers.mixins.electronic import ElectronicDataMixin
from express.parsers.mixins.ionic import IonicDataMixin
from express.parsers.mixins.reciprocal import ReciprocalDataMixin
from express.parsers.settings import Constant
from express.parsers.utils import find_file, find_files_by_regex, lattice_basis_to_poscar


class EspressoParser(BaseParser, IonicDataMixin, ElectronicDataMixin, ReciprocalDataMixin):
    """
    Espresso parser class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.work_dir = self.kwargs["work_dir"]
        self.stdout_file = self.kwargs["stdout_file"]
        self.txt_parser = EspressoTXTParser(self.work_dir)

        self.xml_parser = get_xml_parser(
            self.version,
            work_dir=self.work_dir,
            is_sternheimer_gw=self._is_sternheimer_gw_calculation(),
        )

    def total_energy(self):
        """
        Returns total energy.

        Reference:
            func: express.parsers.mixins.electronic.ElectronicDataMixin.total_energy
        """
        return self.txt_parser.total_energy(self._get_file_content(self.stdout_file))

    def fermi_energy(self):
        """
        Returns fermi energy.

        Reference:
            func: express.parsers.mixins.electronic.ElectronicDataMixin.fermi_energy
        """
        return self.xml_parser.fermi_energy()

    def nspins(self):
        """
        Returns the number of spins.

        Reference:
            func: express.parsers.mixins.electronic.ElectronicDataMixin.nspins
        """
        return self.xml_parser.nspins()

    def _is_sternheimer_gw_calculation(self) -> bool:
        """
        Checks whether this is a Sternheimer GW calculation.

        The calculation is considered Sternheimer GW if "SternheimerGW" is written on top of the stdout file.

        NOTE: DO NOT READ THE WHOLE FILE INTO MEMORY AS IT IS BIG.

        Returns:
             bool
        """
        if os.path.exists(self.stdout_file):
            with open(self.stdout_file, "r") as f:
                for index, line in enumerate(f):
                    if index > 50:
                        return False
                    if settings.STERNHEIMER_GW_TITLE in line:
                        return True
        return False

    def eigenvalues_at_kpoints(self):
        """
        Returns eigenvalues for all kpoints.

        NOTE: eigenvalues are extracted from Sternheimer GW stdout file if this is a Sternheimer GW calculation.

        Reference:
            func: express.parsers.mixins.electronic.ElectronicDataMixin.eigenvalues_at_kpoints
        """
        if self._is_sternheimer_gw_calculation():
            text = self._get_file_content(self.stdout_file)
            inverse_reciprocal_lattice_vectors = self.xml_parser.get_inverse_reciprocal_lattice_vectors()
            return self.txt_parser.eigenvalues_at_kpoints_from_sternheimer_gw_stdout(
                text, inverse_reciprocal_lattice_vectors
            )
        else:
            return self.xml_parser.eigenvalues_at_kpoints()

    def ibz_k_points(self):
        """
        Returns ibz_k_points.

        Note:
            The function assumes that kpoints extracted from parsed source are inside the irreducible wedge of the
            Brillouin zone. Without checking whether it is the case or not.

        Reference:
            func: express.parsers.mixins.reciprocal.ReciprocalDataMixin.ibz_k_points
        """
        return np.array([eigenvalueData["kpoint"] for eigenvalueData in self.eigenvalues_at_kpoints()])

    def dos(self):
        """
        Returns density of states.

        Reference:
            func: express.parsers.mixins.electronic.ElectronicDataMixin.dos
        """
        return self.txt_parser.dos()

    def initial_basis(self):
        """
        Returns initial basis.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.initial_basis
        """
        return self.txt_parser.initial_basis(self._get_file_content(self.stdout_file))

    def initial_lattice_vectors(self):
        """
        Returns initial lattice vectors.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.initial_lattice_vectors
        """
        return self.txt_parser.initial_lattice_vectors(self._get_file_content(self.stdout_file))

    def final_basis(self):
        """
        Returns final basis.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.basis
        """
        return self.xml_parser.final_basis()

    def final_lattice_vectors(self):
        """
        Returns final lattice.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.lattice_vectors
        """
        return self.xml_parser.final_lattice_vectors(reciprocal=False)

    def convergence_electronic(self):
        """
        Extracts convergence electronic.

        Reference:
            func: express.parsers.mixins.electronic.ElectronicDataMixin.convergence_electronic
        """
        return self.txt_parser.convergence_electronic(self._get_file_content(self.stdout_file))

    def convergence_ionic(self):
        """
        Returns convergence ionic.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.convergence_ionic
        """
        return self.txt_parser.convergence_ionic(self._get_file_content(self.stdout_file))

    def stress_tensor(self):
        """
        Returns stress tensor.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.stress_tensor
        """
        return self.txt_parser.stress_tensor(self._get_file_content(self.stdout_file))

    def pressure(self):
        """
        Returns pressure.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.pressure
        """
        return self.txt_parser.pressure(self._get_file_content(self.stdout_file))

    def total_force(self):
        """
        Returns total force.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.total_force
        """
        return self.txt_parser.total_force(self._get_file_content(self.stdout_file))

    def atomic_forces(self):
        """
        Returns forces that is exerted on each atom by its surroundings.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.atomic_forces
        """
        return self.txt_parser.atomic_forces(self._get_file_content(self.stdout_file))

    def total_energy_contributions(self):
        """
        Extracts total energy contributions.

        Reference:
            func: express.parsers.mixins.electronic.ElectronicDataMixin.total_energy_contributions
        """
        return self.txt_parser.total_energy_contributions(self._get_file_content(self.stdout_file))

    def zero_point_energy(self):
        """
        Returns zero point energy.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.zero_point_energy
        """
        return self.txt_parser.zero_point_energy(self._get_file_content(self.stdout_file))

    def phonon_dos(self):
        """
        Returns phonon dos.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.phonon_dos
        """
        return self.txt_parser.phonon_dos()

    def phonon_dispersions(self):
        """
        Returns phonon dispersions.

        NOTE: q-points are returned in crystal coordinates, converted from matdyn's cartesian 2pi/alat units with the
        reciprocal lattice from the pw.x XML (__prefix__.xml), so that file has to be in the work directory.

        Reference:
            func: express.parsers.mixins.ionic.IonicDataMixin.phonon_dispersions
        """
        data = self.txt_parser.phonon_dispersions()
        data["qpoints"] = np.dot(data["qpoints"], self.xml_parser.get_inverse_reciprocal_lattice_vectors()).tolist()
        return data

    def _find_neb_dat_file(self):
        neb_path_file = find_file(NEB_PATH_FILE_SUFFIX, self.work_dir)
        if neb_path_file:
            return "{}.dat".format(neb_path_file[: neb_path_file.rfind(".")])

    def reaction_coordinates(self):
        """
        Returns reaction coordinates.

        Returns:
             list
        """
        neb_dat_file = self._find_neb_dat_file()
        return self.txt_parser.reaction_coordinates(self._get_file_content(neb_dat_file))

    def reaction_energies(self):
        """
        Returns reaction energies.

        Returns:
             list
        """
        neb_dat_file = self._find_neb_dat_file()
        return self.txt_parser.reaction_energies(self._get_file_content(neb_dat_file))

    def _get_esm_file(self):
        return find_file(".esm1", self.work_dir)

    def _get_wavefunction_file(self):
        return find_file(settings.WAVEFUNCTION_FILE, self.work_dir)

    def potential_profile(self):
        return self.txt_parser.potential_profile(self._get_file_content(self._get_esm_file()))

    def wavefunction_amplitude(self):
        # The data is [[coordinate], [value]]: for coordinates comes in alat units, we convert x data to angstroms
        data = self.txt_parser.wavefunction_amplitude(self._get_file_content(self._get_wavefunction_file()))
        lattice = self.final_lattice_vectors()
        alat = lattice["vectors"]["alat"]
        data[0] = [x * alat for x in data[0]]
        return data

    def charge_density_profile(self):
        return self.txt_parser.charge_density_profile(self._get_file_content(self._get_esm_file()))

    def _is_pw_scf_output_file(self, path):
        """
        Checks whether the given file is PWSCF output file.

        The file is considered PWSCF output file if "Program PWSCF" is written on top of the file.

        NOTE: DO NOT READ THE WHOLE FILE INTO MEMORY AS IT COULD BE BIG.

        Returns:
             bool
        """
        if os.path.exists(path):
            with open(path, "r") as f:
                for index, line in enumerate(f):
                    if index > 50:
                        return False
                    if settings.PWSCF_OUTPUT_FILE_REGEX in line:
                        return True

    def _find_pw_scf_output_files(self):
        pw_scf_output_files = []
        for root, dirs, files in os.walk(self.work_dir, followlinks=True):
            for file in files:
                path = os.path.join(root, file)
                if self._is_pw_scf_output_file(path):
                    pw_scf_output_files.append(path)
        return pw_scf_output_files

    def initial_structure_strings(self):
        structures = []
        for pw_scf_output_file in self._find_pw_scf_output_files():
            try:
                basis = self.txt_parser.initial_basis(self._get_file_content(pw_scf_output_file))
                lattice = self.txt_parser.initial_lattice_vectors(self._get_file_content(pw_scf_output_file))
                structures.append(lattice_basis_to_poscar(lattice, basis))
            except:
                raise
        return structures

    def final_structure_strings(self):
        structures = []
        for pw_scf_output_file in self._find_pw_scf_output_files():
            try:
                basis = self.txt_parser.final_basis(self._get_file_content(pw_scf_output_file))
                lattice = self.txt_parser.final_lattice_vectors(self._get_file_content(pw_scf_output_file))
                structures.append(lattice_basis_to_poscar(lattice, basis))
            except Exception:
                pass
        return structures

    def average_potential(self):
        data = self.txt_parser.average_quantity(self.stdout_file)
        data["x"] *= Constant.BOHR  # convert to angstrom
        data["planar_average"] *= Constant.RYDBERG  # convert to eV
        data["macroscopic_average"] *= Constant.RYDBERG  # convert to eV
        return data

    def dielectric_tensor(self) -> Dict[str, Optional[np.ndarray]]:
        """Parse all dielectric tensors (as a function of frequency) in current working directory.

        This function attempts to parse the real (`epsr.dat`) and imaginary (`epsi.dat`) parts of the diagonal
        components of the dielectric tensor. In the case of collinear spin mode, two versions per file are parsed, i.e.,
        `uepsr.dat`, depsr.dat`, `uepsi.dat`, `depsi.dat`.

        Returns:
            Dictionary mapping
        """
        epsilon_dat_files = find_files_by_regex(settings.REGEX["epsilon_filenames"]["regex"], Path(self.work_dir))
        tensor_by_filename = {}
        for dat_file in epsilon_dat_files:
            tensor_by_filename[dat_file.name] = self.txt_parser.dielectric_tensor_generic(dat_file)
        return tensor_by_filename

    def hubbard_u(self) -> Dict[str, list]:
        """
        Parses hp.x output file __prefix__.Hubbard_parameters.dat and returns
        Hubbard parameters. Example output:
        {
            "values": [
                {
                    "id": 1,
                    "atomicSpecies": "Co1",
                    "orbitalName": "3d",
                    "value": 6.7553
                },
                {
                    "id": 2,
                    "atomicSpecies": "Co2",
                    "orbitalName": "3d",
                    "value": 6.7553
                }
            ]
        }
        """
        return self.txt_parser.parse_hubbard_u()

    def hubbard_v(self) -> Dict[str, list]:
        """
        See parse_hubbard_v in formats/txt.py
        """
        return self.txt_parser.parse_hubbard_v()

    def hubbard_v_nn(self) -> Dict[str, list]:
        """
        See parse_hubbard_v_nn in formats/txt.py
        """
        return self.txt_parser.parse_hubbard_v_nn()
