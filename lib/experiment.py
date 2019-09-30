from image import Image
from copy import copy

from typing import *
import random as rand

PointType = Tuple[int, int]

# Transforms a raw image into a black and white version that
# distinguishes only letter forms. Returns a new image, doesn't mutate
# the input
def filter_letterforms(
        img: Image,
        *,
        trans_matrix: List[PointType],
        blur_kernel: int,
        adaptive_thresh_block: int,
        adaptive_c: float,
        thresh_percent: float,
        area: int) -> Image:
    img = copy(img)

    # Apply the transformation to the board portion of the image
    img.perspective_transform(trans_matrix)

    # Crop a small portion of the border, ensuring that the image only
    # contains the board, and none of the border
    img.crop_border(0.02)

    # Resize the image to a predetermined resolution. This will ensure
    # that selected parameters have the same impact, regardless of the
    # image resolution we use for input
    img.scale_min(2000, 2000)

    # Apply an adaptive threshold on the image. If the lighting
    # differs through the image this does an excellent job
    img.adaptive_threshold(adaptive_thresh_block, adaptive_c)

    # Blur the image, so that portions of the image that weren't
    # connected, end up connected together, and are counted as part of
    # a greater area
    img.blur(blur_kernel)

    # Apply a threshold, connecting whatever was just blurred
    img.threshold(thresh_percent)

    # Noise in the image should be leftover from the adaptive
    # threshold, leaving a bunch of spots. This clears the spots, but
    # retains the larger letter forms by filtering by the area of a
    # region.
    img.area_threshold(area)

    return img

# Returns a generator that yields random parameters for testing
def gen_parameters() -> Iterator:
    while True:
        yield {
            "blur_kernel": rand.randrange(3, 30, step=2),
            "adaptive_thresh_block": rand.randrange(3, 30, step=2),
            "adaptive_c": rand.uniform(0, 5),
            "thresh_percent": rand.uniform(0, 0.2),
            "area": rand.randrange(1, 20)
        }
