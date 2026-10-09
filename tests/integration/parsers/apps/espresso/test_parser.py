# ruff: noqa: F403,F405
from express.parsers.apps.espresso.parser import EspressoParser
from tests.fixtures.espresso.v6_5.references import *
from tests.integration import IntegrationTestBase


class TestEspressoParser(IntegrationTestBase):
    """Test espresso parser for post-6.4 versions, specifically XML parser."""

    def setUp(self):
        super(TestEspressoParser, self).setUp()
        self.parser = EspressoParser(work_dir=self.workDir, stdout_file=self.stdoutFile, version="6.5.0")

    def tearDown(self):
        super(TestEspressoParser, self).tearDown()

    def test_espresso_total_energy(self):
        self.assertAlmostEqual(self.parser.total_energy(), TOTAL_ENERGY, places=2)

    def test_espresso_fermi_energy(self):
        self.assertAlmostEqual(self.parser.fermi_energy(), FERMI_ENERGY, places=2)

    def test_espresso_nspins(self):
        self.assertEqual(self.parser.nspins(), NSPIN)

    def test_espresso_final_lattice_vectors(self):
        self.assertDeepAlmostEqual(self.parser.final_lattice_vectors(), LATTICE, places=2)

    def test_espresso_eigenvalues_at_kpoints(self):
        self.assertDeepAlmostEqual(self.parser.eigenvalues_at_kpoints()[0], EIGENVALUES_AT_KPOINTS_ZERO, places=2)

    def test_espresso_eigenvalues_at_kpoints_lsda(self):
        self.assertDeepAlmostEqual(self.parser.eigenvalues_at_kpoints()[0], EIGENVALUES_AT_KPOINTS_ZERO_LSDA, places=2)

    def test_espresso_ibz_k_point(self):
        print(self.parser.ibz_k_points())
        self.assertDeepAlmostEqual(self.parser.ibz_k_points(), IBZ_KPOINTS, places=2)

    def test_espresso_dos(self):
        self.assertDeepAlmostEqual(self.parser.dos(), DOS, places=2)

    def test_espresso_convergence_electronic(self):
        self.assertDeepAlmostEqual(self.parser.convergence_electronic(), CONVERGENCE_ELECTRONIC, places=2)

    def test_espresso_convergence_ionic(self):
        self.assertDeepAlmostEqual(self.parser.convergence_ionic(), CONVERGENCE_IONIC, places=2)

    def test_espresso_stress_tensor(self):
        self.assertDeepAlmostEqual(self.parser.stress_tensor(), STRESS_TENSOR, places=2)

    def test_espresso_pressure(self):
        self.assertAlmostEqual(self.parser.pressure(), PRESSURE, places=2)

    def test_espresso_total_force(self):
        self.assertAlmostEqual(self.parser.total_force(), TOTAL_FORCE, places=2)

    def test_espresso_atomic_forces(self):
        self.assertDeepAlmostEqual(self.parser.atomic_forces(), ATOMIC_FORCES, places=2)

    def test_espresso_total_energy_contributions(self):
        self.assertDeepAlmostEqual(self.parser.total_energy_contributions(), TOTAL_ENERGY_CONTRIBUTION, places=2)

    def test_espresso_phonon_dos(self):
        pass
        # self.assertDeepAlmostEqual(self.parser.phonon_dos(), PHONON_DOS, places=2)

    def test_espresso_phonon_dispersions(self):
        qpoints = self.parser.phonon_dispersions()["qpoints"]
        self.assertDeepAlmostEqual(qpoints[-1], PHONON_DISPERSIONS_QPOINT_X, places=4)

    def test_espresso_final_basis(self):
        self.assertDeepAlmostEqual(self.parser.final_basis(), FINAL_BASIS, places=2)
