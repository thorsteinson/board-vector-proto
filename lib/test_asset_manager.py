import unittest
from .asset_manager import validate_points


class TestPointValidation(unittest.TestCase):
    def test_length(self):
        with self.assertRaises(ValueError):
            validate_points([])
        with self.assertRaises(ValueError):
            validate_points([1, 2])
        with self.assertRaises(ValueError):
            validate_points([1, 2, 3, 4, 5])

    def test_negative(self):
        with self.assertRaises(ValueError):
            validate_points([(-1, 0), (0, 0), (0, 0), (0, 0)])

    def test_non_int(self):
        with self.assertRaises(ValueError):
            validate_points([(0, 0), (0, "a"), (0, 0), (0, 0)])

    def test_valid(self):
        points = [(0, 1), (1, 0), (1, 1), (1, 0)]
        self.assertTrue(validate_points(points))


if __name__ == "__main__":
    unittest.main()
