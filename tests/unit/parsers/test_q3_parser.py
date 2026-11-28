import json
import os
import tempfile
import unittest

from express import ExPrESS
from express.parsers.apps.q3.parser import Q3Parser
from express.parsers.settings import Constant

DENSITY_OF_STATES_RECORD = {
    "name": "density_of_states",
    "xAxis": {"label": "energy", "units": "Ry"},
    "yAxis": {"label": "density of states", "units": "states/unitcell"},
    "xDataArray": [-0.5, 0.0, 0.5],
    "yDataSeries": [[0.0, 13.6, 27.2]],
    "legend": [],
}


def write_results(work_dir: str, records: list) -> None:
    """
    Writes records as the properties.records of "<work_dir>/outdir/q3_results.json".
    """
    outdir = os.path.join(work_dir, "outdir")
    os.makedirs(outdir)
    with open(os.path.join(outdir, "q3_results.json"), "w") as results_file:
        json.dump({"properties": {"records": records}}, results_file)


class Q3ParserDensityOfStatesTest(unittest.TestCase):
    """
    Covers the density of states the q3_dos shell unit adds to the q3 results file as ESSE's
    density_of_states record.
    """

    def setUp(self):
        self.work_dir = tempfile.TemporaryDirectory()
        fermi_energy = {"name": "fermi_energy", "units": "Ry", "value": 0.25}
        write_results(self.work_dir.name, [fermi_energy, DENSITY_OF_STATES_RECORD])

    def tearDown(self):
        self.work_dir.cleanup()

    def test_converts_energies_and_values_to_eV(self):
        density_of_states = Q3Parser(work_dir=self.work_dir.name).dos()
        expected_energies = [energy * Constant.Ry for energy in DENSITY_OF_STATES_RECORD["xDataArray"]]
        expected_values = [value / Constant.Ry for value in DENSITY_OF_STATES_RECORD["yDataSeries"][0]]
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
        self.assertEqual(len(density_of_states["xDataArray"][0]), len(DENSITY_OF_STATES_RECORD["xDataArray"]))
        self.assertEqual(len(density_of_states["yDataSeries"]), 1)
        self.assertEqual(density_of_states["legend"], [{}])

    def test_a_record_in_eV_is_kept_as_it_is(self):
        record = dict(DENSITY_OF_STATES_RECORD, xAxis={"label": "energy", "units": "eV"})
        with tempfile.TemporaryDirectory() as work_dir:
            write_results(work_dir, [record])
            density_of_states = Q3Parser(work_dir=work_dir).dos()
        self.assertEqual(density_of_states["energy"], record["xDataArray"])
        self.assertEqual(density_of_states["total"], record["yDataSeries"][0])

    def test_unsupported_energy_units_raise(self):
        record = dict(DENSITY_OF_STATES_RECORD, xAxis={"label": "energy", "units": "cm-1"})
        with tempfile.TemporaryDirectory() as work_dir:
            write_results(work_dir, [record])
            with self.assertRaises(ValueError):
                Q3Parser(work_dir=work_dir).dos()

    def test_results_without_density_of_states_raise(self):
        with tempfile.TemporaryDirectory() as work_dir:
            write_results(work_dir, [{"name": "fermi_energy", "units": "Ry", "value": 0.25}])
            with self.assertRaises(KeyError):
                Q3Parser(work_dir=work_dir).dos()

    def test_missing_results_file_raises(self):
        with tempfile.TemporaryDirectory() as empty_work_dir:
            with self.assertRaises(FileNotFoundError):
                Q3Parser(work_dir=empty_work_dir).dos()

    def test_backup_copy_of_results_file_is_ignored(self):
        with tempfile.TemporaryDirectory() as work_dir:
            write_results(work_dir, [DENSITY_OF_STATES_RECORD])
            backup_path = os.path.join(work_dir, "outdir", "q3_results.json-1")
            with open(backup_path, "w") as backup_file:
                json.dump({"properties": {"records": []}}, backup_file)
            density_of_states = Q3Parser(work_dir=work_dir).dos()
        self.assertEqual(len(density_of_states["energy"]), len(DENSITY_OF_STATES_RECORD["xDataArray"]))

    def test_more_than_one_results_file_raises(self):
        with tempfile.TemporaryDirectory() as work_dir:
            write_results(work_dir, [DENSITY_OF_STATES_RECORD])
            other_results_path = os.path.join(work_dir, "outdir", "other_results.json")
            with open(other_results_path, "w") as other_results_file:
                json.dump({"properties": {"records": []}}, other_results_file)
            with self.assertRaises(ValueError):
                Q3Parser(work_dir=work_dir).dos()


if __name__ == "__main__":
    unittest.main()
