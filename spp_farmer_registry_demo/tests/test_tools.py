from odoo.tests.common import TransactionCase

from .. import tools


class TestTools(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_generate_polygon(self):
        points = tools.generate_polygon(lat=1.0, lon=1.0, acres=51.0)
        self.assertTrue(bool(points))
        self.assertIsInstance(points, list)
        self.assertIsInstance(points[0], tuple)
        self.assertEqual(len(points[0]), 2)

    def test_random_location_in_kenya(self):
        min_lat, max_lat = -1.900, 2.6766
        min_lon, max_lon = 36.2509, 40.651
        latitude, longitude = tools.random_location_in_kenya()
        self.assertTrue(bool(latitude))
        self.assertTrue(bool(longitude))
        self.assertIsInstance(latitude, float)
        self.assertIsInstance(longitude, float)
        self.assertGreaterEqual(latitude, min_lat)
        self.assertLessEqual(latitude, max_lat)
        self.assertGreaterEqual(longitude, min_lon)
        self.assertLessEqual(longitude, max_lon)

    def test_random_location_in_laos(self):
        min_lat, max_lat = 13.9095, 22.5085
        min_lon, max_lon = 100.0843, 107.6346
        latitude, longitude = tools.random_location_in_laos()
        self.assertTrue(bool(latitude))
        self.assertTrue(bool(longitude))
        self.assertIsInstance(latitude, float)
        self.assertIsInstance(longitude, float)
        self.assertGreaterEqual(latitude, min_lat)
        self.assertLessEqual(latitude, max_lat)
        self.assertGreaterEqual(longitude, min_lon)
        self.assertLessEqual(longitude, max_lon)

    def test_random_location_in_sri_lanka(self):
        min_lat, max_lat = 5.9194, 9.8351
        min_lon, max_lon = 79.6521, 81.8790
        latitude, longitude = tools.random_location_in_sri_lanka()
        self.assertTrue(bool(latitude))
        self.assertTrue(bool(longitude))
        self.assertIsInstance(latitude, float)
        self.assertIsInstance(longitude, float)
        self.assertGreaterEqual(latitude, min_lat)
        self.assertLessEqual(latitude, max_lat)
        self.assertGreaterEqual(longitude, min_lon)
        self.assertLessEqual(longitude, max_lon)
