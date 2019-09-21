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
    x_res = img.xres
    y_res = img.xres
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


if __name__ == "__main__":
    unittest.main()
