import cv2 as cv
import numpy as np
from pathlib import Path
from copy import copy

DEFAULT_COLOR = (192, 36, 27)


class Image:
    # Allow an image to be constructed from either a path that
    # references an image or an array literal
    def __init__(self, image):
        if isinstance(image, Path):
            # Since imread doesn't raise an exception, attempt to grab
            # the file handle to trigger an appropriate error if there
            # are any file errors
            f = open(image, "rb")
            f.close()
            self.img = cv.imread(str(image.resolve()))
        elif isinstance(image, np.ndarray):
            self.img = copy(image)
        else:
            raise TypeError(
                "Image must be constructed with a numpy array or path to an image"
            )

    def __copy__(self):
        return Image(copy(self.img))

    # Looks at number of dimensions to determine whether the image is
    # color or grayscale in colorspace
    def is_gray(self):
        if len(self.img.shape) == 2:
            return True
        elif len(self.img.shape) == 3:
            return False
        raise ValueError

    # Converts the image to grayscale
    def grayscale(self):
        if not self.is_gray():
            self.img = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)

    # Converts image to BGR colorspace
    def bgr_color(self):
        if self.is_gray():
            self.img = cv.cvtColor(self.img, cv.COLOR_GRAY2BGR)

    # Takes a binary image, and applies a threshold on sections of pixels
    # that don't meet a given area. This can effectively filter bits of
    # noise from actual blocks of text we wish to capture on the board
    def area_threshold(self, area):
        if not self.is_gray():
            raise ValueError("Image must be grayscale")

        if area < 1:
            raise ValueError("Area cannot be less than 1")

        # Keep track of each coordinate and the set that it belongs to
        regionMap = {}

        # Iterate through all coordinates of the image
        for (x, y), n in np.ndenumerate(self.img):
            # Only black pixels
            if n == 0:
                leftNeighbor = (x - 1, y)
                upNeighbor = (x, y - 1)

                region = set()

                if leftNeighbor[0] >= 0 and leftNeighbor in regionMap:
                    region = regionMap[leftNeighbor]

                elif upNeighbor[1] >= 0 and upNeighbor in regionMap:
                    region = regionMap[upNeighbor]

                regionMap[(x, y)] = region
                region.add((x, y))

        # Create a new a array of the same shape
        filtered = np.zeros_like(img)

        WHITE = 255
        for (x, y), n in np.ndenumerate(img):
            if n == 0 and len(regionMap[(x, y)]) < area:
                n = WHITE

            filtered[x, y] = n

        self.img = filtered

    def crop_border(self, percent):
        if percent > 0.5 or percent < 0:
            raise ValueError("Border percent must be between 0-0.5")

        y = self.img.shape[0]
        y_offset = round(y * percent)
        y_size = y - y_offset * 2
        x = self.img.shape[1]
        x_offset = round(x * percent)
        x_size = x - x_offset * 2

        self.img = np.array(
            self.img[y_offset : y_offset + y_size, x_offset : x_offset + x_size]
        )

    # Returns an image that's projected from the 4 given points
    def perspective_transform(self, points):
        if len(points) != 4:
            raise ValueError("Exactly 4 points must be provided")
        for x, y in points:
            if type(x) != int or type(y) != int:
                raise ValueError("Non integer value passed as point")

        top_left = points[0]
        top_right = points[1]
        bottom_right = points[2]
        bottom_left = points[3]

        source = np.array(
            [top_left, top_right, bottom_right, bottom_left], dtype="float32"
        )
        maxW = max(top_right[0] - top_left[0], bottom_right[0] - bottom_left[0])
        maxH = max(bottom_right[1] - top_right[1], bottom_left[1] - top_left[1])
        # This determines the output size we want to map onto. It's not
        # perfect, but it's good enough to get the general shape of what
        # was captured
        dest = np.array(
            [(0, 0), (maxW - 1, 0), (maxW - 1, maxH - 1), (0, maxH - 1)],
            dtype="float32",
        )
        transM = cv.getPerspectiveTransform(source, dest)

        self.img = cv.warpPerspective(self.img, transM, (maxW, maxH))

    def adaptive_threshold(self, block_size, c):
        if block_size % 2 != 1 or block_size <= 1:
            raise ValueError("Block size must be odd integer greater than 1")
        try:
            c = float(c)
        except TypeError:
            raise ValueError("Constant c is not a numeric value")

        self.img = cv.adaptiveThreshold(
            self.img,
            # Max value that will be output, keep this to make image
            # purely black or white
            255,
            cv.ADAPTIVE_THRESH_GAUSSIAN_C,  # Use Guassion method
            cv.THRESH_BINARY,  # Threshold Type
            block_size,
            c,
        )  # Constant that is subtracted during thresholding

    def blur(self, kernel_size):
        if kernel_size % 2 != 1 or kernel_size <= 1:
            raise ValueError("Kernel size must be odd integer greater than 1")

        self.img = cv.blur(self.img, (kernel_size, kernel_size))

    def threshold(self, percent_black):
        if percent_black < 0 or percent_black > 1.0:
            raise ValueError("Percent black must be between 0 and 1.0")

        _, self.img = cv.threshold(
            self.img, 255 - int(percent_black * 255), 255, cv.THRESH_BINARY
        )

    # It's nice to have these properties, because it can be easy to
    # forget that y is the first value in the shape and x is the 2nd
    @property
    def x_res(self):
        return self.img.shape[1]

    @property
    def y_res(self):
        return self.img.shape[0]

    # Writes a watermark to the bottom left corner of an image. The
    # water mark consists of the keys and values in the dictionary passed
    def watermark(self, dictionary):
        if type(dictionary) != dict:
            raise TypeError("Non dictionary passed in")

        if self.is_gray():
            self.bgr_color()

        (_, line_height), _ = cv.getTextSize("TEXT", cv.FONT_HERSHEY_DUPLEX, 1.0, 0)

        x = round(self.x_res * 0.05)
        y = round(self.y_res - self.y_res * 0.05)

        for k, v in dictionary.items():
            self.img = cv.putText(
                self.img,
                "{}: {}".format(k, v),
                (x, y),
                cv.FONT_HERSHEY_DUPLEX,
                1,
                DEFAULT_COLOR,
            )
            y -= round(line_height * 1.1)

    # Writes the image to the specified path, possibly encoding the
    # image in the process
    def save(self, path):
        f = open(path, "wb")
        f.close()
        imwrite(self, self.img, str(path.resolve()))

    def scale(self, factor):
        if factor <= 0:
            raise ValueError("Factor must be non negative / zero value")

        projected_x_res = round(self.x_res * factor)
        projected_y_res = round(self.y_res * factor)
        self.img = cv.resize(self.img, (projected_x_res, projected_y_res))

    # Scales an image so that it's bounded by either the x or y max
    # provided. The aspect ratio is preserved. Returns the scaling
    # factor that was used
    def scale_bounded(self, x_max, y_max):
        if type(x_max) != int or type(y_max) != int:
            raise TypeError("x_max and y_max must be integers")

        if x_max < 1 or y_max < 1:
            raise ValueError("x_man and y_max cannot be less than 1")

        x_scale = x_max / self.x_res
        y_scale = y_max / self.y_res

        factor = min(x_scale, y_scale)
        self.scale(min(x_scale, y_scale))

        return factor

    def draw_line(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2

        for n in [x1, y1, x2, y2]:
            if type(n) != int:
                raise TypeError("Point contains non integer value")
            if n < 0:
                raise ValueError("Point contains negative value")

        if x1 > self.x_res - 1 or x2 > self.x_res - 1:
            raise ValueError("Point goes beyond x resolution of image")
        if y1 > self.y_res - 1 or y2 > self.y_res - 1:
            raise ValueError("Point goes beyond y resolution of image")

        self.img = cv.line(self.img, p1, p2, DEFAULT_COLOR, 2)

    def draw_point(self, x, y):
        if type(x) != int or type(y) != int:
            raise TypeError("Point must be integer value")

        self.img = cv.drawMarker(
            self.img, (x, y), DEFAULT_COLOR, cv.MARKER_CROSS, 20, 2
        )
