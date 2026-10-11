import json
from typing import Any, Dict, Optional

from express.parsers import BaseParser
from express.parsers.apps.q3.settings import RESULTS_FILE_SUFFIX
from express.parsers.mixins.electronic import ElectronicDataMixin
from express.parsers.settings import Constant
from express.parsers.utils import find_file


class Q3Parser(BaseParser, ElectronicDataMixin):
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

        Reference: lib/q3/docs/io_reference.md, section 4.1.
        """
        if self._results is None:
            results_file = find_file(RESULTS_FILE_SUFFIX, self.work_dir)
            if not results_file:
                raise FileNotFoundError(
                    f"Could not find a q3 results file (*{RESULTS_FILE_SUFFIX}) under {self.work_dir}"
                )
            with open(results_file) as f:
                self._results = json.load(f)
        return self._results

    def total_energy(self):
        """
        Returns total energy.

        Reference:
            func: express.parsers.mixins.electronic.ElectronicDataMixin.total_energy
        """
        return self._get_results()["total_energy_ry"] * Constant.Ry

    def fermi_energy(self):
        """
        Returns fermi energy.

        Reference:
            func: express.parsers.mixins.electronic.ElectronicDataMixin.fermi_energy
        """
        return self._get_results()["fermi_energy_ry"] * Constant.Ry
