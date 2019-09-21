import unittest
from image import Image
import numpy as np
from pathlib import Path
from copy import copy

test_array = np.zeros((10, 10, 3), dtype="uint8")


class TestInit(unittest.TestCase):
    def test_from_array(self):
        img = Image(test_array)

    def test_fails_imaginary_path(self):
        with self.assertRaises(FileNotFoundError):
            img = Image(Path("/this/is/made/up.png"))

    def test_bad_values(self):
        bad_types = ["a", 1, (1.0), {"x": 5}]
        for t in bad_types:
            with self.assertRaises(TypeError):
                img = Image(t)


def same_res(img, func):
    x_res = img.x_res
    y_res = img.y_res
    func()

    return img.x_res == x_res and img.y_res == y_res


class TestCopy(unittest.TestCase):
    def test_type(self):
        img = Image(test_array)
        self.assertIsInstance(img, Image)

    def test_independent(self):
        img = Image(test_array)
        img_cp = copy(img)
        img_cp.img[0, 0, 0] = 1

        self.assertNotEqual(img.img[0, 0, 0], 1)


class TestGrayscale(unittest.TestCase):
    def test_dimensions_reduced(self):
        img = Image(test_array)
        img.grayscale()
        self.assertTrue(img.is_gray())

    def test_x_y_same(self):
        img = Image(test_array)
        self.assertTrue(same_res(img, img.grayscale))

    def idempotent(self):
        img = Image(test_array)
        img.grayscale()
        img.grayscale()


class TestColorConversion(unittest.TestCase):
    def test_dimensions_increased(self):
        img = Image(test_array)
        img.bgr_color()
        self.assertFalse(img.is_gray())

    def test_x_y_same(self):
        img = Image(test_array)
        self.assertTrue(same_res(img, img.bgr_color))

    def idempotent(self):
        img = Image(test_array)
        img.bgr_color()
        img.bgr_color()


if __name__ == "__main__":
    unittest.main()
