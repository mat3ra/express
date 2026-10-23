from tests.unit import UnitTestBase
from express.properties.scalar.scalar_property_context import ScalarPropertyFromContext

SCHOTTKY_BARRIER_HEIGHT_P = {"units": "eV", "name": "schottky_barrier_height_p", "value": 1.046}
SCHOTTKY_BARRIER_HEIGHT_N = {"units": "eV", "name": "schottky_barrier_height_n", "value": 0.596}


class SchottkyBarrierHeightTest(UnitTestBase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_schottky_barrier_height_p(self):
        property_ = ScalarPropertyFromContext("schottky_barrier_height_p", None, value=1.046)
        self.assertDeepAlmostEqual(property_.serialize_and_validate(), SCHOTTKY_BARRIER_HEIGHT_P)

    def test_schottky_barrier_height_n(self):
        property_ = ScalarPropertyFromContext("schottky_barrier_height_n", None, value=0.596)
        self.assertDeepAlmostEqual(property_.serialize_and_validate(), SCHOTTKY_BARRIER_HEIGHT_N)
