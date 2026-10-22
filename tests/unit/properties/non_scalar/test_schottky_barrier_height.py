from tests.unit import UnitTestBase

from express.properties.non_scalar.non_scalar_property_context import NonScalarPropertyFromContext

SCHOTTKY_BARRIER_HEIGHT_VALUE = {"units": "eV", "pType": 1.046, "nType": 0.596}
SCHOTTKY_BARRIER_HEIGHT = {"name": "schottky_barrier_height", **SCHOTTKY_BARRIER_HEIGHT_VALUE}


class SchottkyBarrierHeightTest(UnitTestBase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_schottky_barrier_height(self):
        property_ = NonScalarPropertyFromContext("schottky_barrier_height", None, value=SCHOTTKY_BARRIER_HEIGHT_VALUE)
        self.assertDeepAlmostEqual(property_.serialize_and_validate(), SCHOTTKY_BARRIER_HEIGHT)
