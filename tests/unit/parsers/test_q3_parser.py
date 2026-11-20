import json
import os
import tempfile
import unittest

from express import ExPrESS
from express.parsers.apps.q3.parser import Q3Parser
from express.parsers.settings import Constant

DENSITY_OF_STATES = {
    "energies_ry": [-0.5, 0.0, 0.5],
    "dos": [0.0, 13.6, 27.2],
    "fermi_energy_ry": 0.25,
}


class Q3ParserDensityOfStatesTest(unittest.TestCase):
    """
    Covers the density of states written by the q3_dos shell unit to q3_dos.json.
    """

    def setUp(self):
        self.work_dir = tempfile.TemporaryDirectory()
        with open(os.path.join(self.work_dir.name, "q3_dos.json"), "w") as density_of_states_file:
            json.dump(DENSITY_OF_STATES, density_of_states_file)

    def tearDown(self):
        self.work_dir.cleanup()

    def test_converts_energies_and_values_to_electronvolts(self):
        density_of_states = Q3Parser(work_dir=self.work_dir.name).dos()
        expected_energies = [energy * Constant.Ry for energy in DENSITY_OF_STATES["energies_ry"]]
        expected_values = [value / Constant.Ry for value in DENSITY_OF_STATES["dos"]]
        for actual, expected in zip(density_of_states["energy"], expected_energies):
            self.assertAlmostEqual(actual, expected)
        for actual, expected in zip(density_of_states["total"], expected_values):
            self.assertAlmostEqual(actual, expected)
        self.assertEqual(density_of_states["partial"], [])
        self.assertEqual(density_of_states["partial_info"], [])

    def test_density_of_states_property_has_single_total_series(self):
        express = ExPrESS("q3", work_dir=self.work_dir.name)
        density_of_states = express.property("density_of_states")
        self.assertEqual(density_of_states["name"], "density_of_states")
        self.assertEqual(len(density_of_states["xDataArray"][0]), len(DENSITY_OF_STATES["energies_ry"]))
        self.assertEqual(len(density_of_states["yDataSeries"]), 1)
        self.assertEqual(density_of_states["legend"], [{}])

    def test_missing_file_raises(self):
        with tempfile.TemporaryDirectory() as empty_work_dir:
            with self.assertRaises(FileNotFoundError):
                Q3Parser(work_dir=empty_work_dir).dos()


if __name__ == "__main__":
    unittest.main()
