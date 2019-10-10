from image import Image
from copy import copy
from pathlib import Path

from typing import *
import random as rand
import os
import csv

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
    area: int,
) -> Image:
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
            "area": rand.randrange(1, 20),
        }


class Result(NamedTuple):
    legible: bool
    blur_kernel: int
    adaptive_thresh_block: int
    adaptive_c: float
    thresh_percent: float
    area: int


EXPERIMENT_FOLDER = "experiments"


class Experiment:
    def __init__(self, asset_no):
        self.path = Path(EXPERIMENT_FOLDER, f"exp_{asset_no}.csv")

    def __enter__(self):
        dirpath = Path(EXPERIMENT_FOLDER)
        if not dirpath.exists():
            os.mkdir(dirpath)
        if self.path.exists():
            self.file = open(self.path, "a")
        else:
            self.file = open(self.path, "w")
            self._write_header()

        return self

    def __exit__(self, *args):
        self.file.close()

    # Writes the header line for the CSV file. This should only be
    # called when the file is being created for the first time
    def _write_header(self):
        HEADER = (
            "legible,blur_kernel,adaptive_thresh_block,adaptive_c,thresh_percent,area\n"
        )
        self.file.write(HEADER)

    # Captures a result, with parameters, and whether the image was good
    # or not, as a single line that can be appended to a data capture file
    def write_result(
        self,
        legible: bool,
        *,
        blur_kernel: int,
        adaptive_thresh_block: int,
        adaptive_c: float,
        thresh_percent: float,
        area: int,
    ):
        result_str = f"{legible},{blur_kernel},{adaptive_thresh_block},{adaptive_c},{thresh_percent},{area}\n"
        self.file.write(result_str)

    def read_results(self) -> List[Result]:
        # Even though we have the file open, that's our handler for
        # appending to the file, we use this just to read the contents
        if self.path.exists():
            with open(self.path, "r") as file:
                reader = csv.DictReader(file)
                rows = []
                for row in reader:
                    rows.append(
                        Result(
                            legible=True if row["legible"] == "True" else False,
                            blur_kernel=int(row["blur_kernel"]),
                            adaptive_thresh_block=int(row["adaptive_thresh_block"]),
                            adaptive_c=float(row["adaptive_c"]),
                            thresh_percent=float(row["thresh_percent"]),
                            area=int(row["area"]),
                        )
                    )
            return rows

        # No data has been written for the experiment yet
        else:
            return []
