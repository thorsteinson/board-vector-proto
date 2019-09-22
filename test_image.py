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


class TestAreaThreshold(unittest.TestCase):
    def test_only_grayscale(self):
        img = Image(test_array)
        with self.assertRaises(ValueError):
            img.area_threshold(10)

    def test_only_positive_areas(self):
        img = Image(test_array)
        img.grayscale()
        with self.assertRaises(ValueError):
            img.area_threshold(-1)
        with self.assertRaises(ValueError):
            img.area_threshold(0)

    def res_preserved(self):
        img = Image(test_array)
        img.grayscale()
        self.assertTrue(same_res(img, lambda: img.area_threshold(0.2)))


class TestCropBorder(unittest.TestCase):
    def test_valid_vals(self):
        img = Image(test_array)
        with self.assertRaises(ValueError):
            img.crop_border(-100)
        with self.assertRaises(ValueError):
            img.crop_border(0.6)


class TestPerspectiveTransform(unittest.TestCase):
    def test_valid_points(self):
        img = Image(test_array)
        bad_points = [[1], [(1, 0), ("1", 0), (1, 1), (1, 1)]]
        for points in bad_points:
            with self.assertRaises(ValueError):
                img.perspective_transform(points)


class TestAdaptiveThreshold(unittest.TestCase):
    def test_valid_block_sizes(self):
        img = Image(test_array)
        bad_blocks = [-1, 2, 4, 6, 1]
        for block in bad_blocks:
            with self.assertRaises(ValueError):
                img.adaptive_threshold(block, 0)

    def test_valid_c(self):
        img = Image(test_array)
        bad_cs = [None, complex(1, 2), "hello"]
        for c in bad_cs:
            with self.assertRaises(ValueError):
                img.adaptive_threshold(3, c)


class TestBlur(unittest.TestCase):
    def test_valid_kernel_size(self):
        img = Image(test_array)
        bad_kernels = [-1, -2, 1, 2, 4, 100]
        for kernel in bad_kernels:
            with self.assertRaises(ValueError):
                img.blur(kernel)


class TestThreshold(unittest.TestCase):
    def test_valid_percent(self):
        img = Image(test_array)
        bad_percent = [-1, -2, 1.23, 100]
        for p in bad_percent:
            with self.assertRaises(ValueError):
                img.threshold(p)


class TestWatermark(unittest.TestCase):
    def test_valid_values(self):
        img = Image(test_array)
        bad_dicts = [1.0, 1, None, False]
        for d in bad_dicts:
            with self.assertRaises(TypeError):
                img.watermark(d)

    def test_res_preserved(self):
        img = Image(test_array)
        self.assertTrue(same_res(img, lambda: img.watermark({"test": 1})))


class TestScale(unittest.TestCase):
    def test_valid_scales(self):
        img = Image(test_array)
        with self.assertRaises(ValueError):
            img.scale(-2)

    def test_double_res(self):
        img = Image(test_array)
        img.scale(2)
        self.assertEquals(test_array.shape[0] * 2, img.y_res)
        self.assertEquals(test_array.shape[1] * 2, img.x_res)


class TestScaleBounded(unittest.TestCase):
    def test_valid_resize(self):
        img = Image(test_array)
        with self.assertRaises(ValueError):
            img.scale_bounded(-1, 100)
        with self.assertRaises(ValueError):
            img.scale_bounded(100, -1)

    def test_fits_bounds(self):
        img = Image(np.zeros((102, 10), dtype="uint8"))
        factor = img.scale_bounded(1000, 1000)
        max_res = max(img.x_res, img.y_res)
        self.assertEquals(1000, max_res)
        self.assertIsInstance(factor, float)

    # If we invert the scale factor, we should return to our original resolution.
    def test_factor_invertible(self):
        img = Image(test_array)
        init_x = img.x_res
        init_y = img.y_res

        factor = img.scale_bounded(1000, 1000)
        img.scale(1 / factor)

        self.assertEquals(init_x, img.x_res)
        self.assertEquals(init_y, img.y_res)


class TestDrawLine(unittest.TestCase):
    def test_types(self):
        img = Image(test_array)
        bad_types = [(("a", "b"), ("a", "b")), ((None, None), ([1, 2.3], {}))]
        for p0, p1 in bad_types:
            with self.assertRaises(TypeError):
                img.draw_line(p0, p1)

    def test_values(self):
        img = Image(test_array)
        bad_vals = [((-1, 0), (0, 0)), ((100, 0), (0, 0))]
        for p0, p1 in bad_vals:
            with self.assertRaises(ValueError):
                img.draw_line(p0, p1)

    def test_grayscale(self):
        img = Image(test_array)
        img.grayscale()
        img.draw_line((0, 0), (5, 5))


class TestDrawMarker(unittest.TestCase):
    def test_types(self):
        img = Image(test_array)
        bad_types = [(None, 1), (0, {}), (0, "Hello")]
        for x, y in bad_types:
            with self.assertRaises(TypeError):
                img.draw_point(self, x, y)

    def test_res_preserver(self):
        img = Image(test_array)
        self.assertTrue(same_res(img, lambda: img.draw_point(5, 5)))


if __name__ == "__main__":
    unittest.main()
