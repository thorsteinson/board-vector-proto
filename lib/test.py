import cv2 as cv
import numpy as np
import itertools as it
import random
import pickle
import os

TEST_IMG = "./IMG_20190916_123045.jpg"

# These are the corners of the points in the image above. Note that
# the ORDER IS SIGNIFGANT. It will throw an error if we don't provide
# this specific order
#
# Additionally: The inputs must be transformed into 32bit floating
# point numbers. You can't say float, it must by float32.
CORNERS = [
    (1066, 803),  # Top Left
    (2160, 916),  # Top Right
    (2122, 2589),  # Bottom Right
    (1108, 2718),  # Bottom Left
]

# Returns an image that's projected from the 4 given points
def transform_img(img, top_left, top_right, bottom_right, bottom_left):
    source = np.array([top_left, top_right, bottom_right, bottom_left], dtype="float32")
    maxW = max(top_right[0] - top_left[0], bottom_right[0] - bottom_left[0])
    maxH = max(bottom_right[1] - top_right[1], bottom_left[1] - top_left[1])
    # This determines the output size we want to map onto. It's not
    # perfect, but it's good enough to get the general shape of what
    # was captured
    dest = np.array(
        [(0, 0), (maxW - 1, 0), (maxW - 1, maxH - 1), (0, maxH - 1)], dtype="float32"
    )
    transM = cv.getPerspectiveTransform(source, dest)

    return cv.warpPerspective(img, transM, (maxW, maxH))


# Takes a color image and returns a grayscale one
def grayscale(img):
    # Note that we use BGR, because apparently the deafult order is
    # reversed in OpenCV compared to what we'd normally suspect
    return cv.cvtColor(img, cv.COLOR_BGR2GRAY)


# Takes a binary image, and applies a threshold on sections of pixels
# that don't meet a given area. This can effectively filter bits of
# noise from actual blocks of text we wish to capture on the board
def area_threshold(img, area):
    # Keep track of each coordinate and the set that it belongs to
    regionMap = {}

    # Iterate through all coordinates of the image
    for (x, y), n in np.ndenumerate(img):
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

    return filtered


def pipeline(img, **kwargs):
    # Get our arguments
    crop_percent = kwargs["crop_percent"]
    adaptive_block_size = kwargs["adaptive_block_size"]
    adaptive_C = kwargs["adaptive_C"]
    min_area = kwargs["min_area"]
    blur_kernel_size = kwargs["blur_kernel_size"]
    percent_black = kwargs["percent_black"]

    cropped = crop_border(img, crop_percent)
    gray = grayscale(cropped)
    adaptive = cv.adaptiveThreshold(
        gray,
        # Max value that will be output, keep this to make image
        # purely black or white
        255,
        cv.ADAPTIVE_THRESH_GAUSSIAN_C,  # Use Guassion method
        cv.THRESH_BINARY,  # Threshold Type
        adaptive_block_size,  # Blocksize
        adaptive_C,
    )  # Constant that is subtracted during thresholding
    filtered = area_threshold(adaptive, min_area)
    blurred = cv.blur(filtered, (blur_kernel_size, blur_kernel_size))
    _, threshold = cv.threshold(
        blurred, 255 - int(percent_black * 255), 255, cv.THRESH_BINARY
    )

    # Take our parameters, and write those out onto the image so we
    # can compare different pipelines visually
    xP = 20
    yP = threshold.shape[0] - 20

    # Convert back into an RGB image so we can have a different color
    # for our watermark
    watermarked = cv.cvtColor(threshold, cv.COLOR_GRAY2BGR)
    for (param_name, param_val) in kwargs.items():
        # Write out a line for each parameter
        watermarked = cv.putText(
            watermarked,
            "{}: {}".format(param_name, param_val),
            (xP, yP),
            cv.FONT_HERSHEY_DUPLEX,
            1,
            (192, 36, 27),
        )
        yP -= 30

    return watermarked


def crop_border(img, percent):
    y = img.shape[0]
    y_offset = round(y * percent)
    y_size = y - y_offset * 2
    x = img.shape[1]
    x_offset = round(x * percent)
    x_size = x - x_offset * 2

    return np.array(img[y_offset : y_offset + y_size, x_offset : x_offset + x_size])


# Returns a series of dictionaries that can represent a range of
# permutations for params to be passed into a pipeline function. This
# way we can build a ton of different images with varying params and
# see what the effects are.
def gen_params():
    param_ranges = it.product(
        range(3, 30, 2),  # Adaptive block size
        # This value has enormous power. It
        # should be non zero, else the image is black
        range(1, 5),  # adaptive C
        range(10, 21),  # min area
        range(3, 30, 2),  # blur_kernel_size
        map(lambda n: 0.01 * n, range(1, 30)),
    )  # percent_black

    for params in param_ranges:
        yield {
            "crop_percent": 0.02,
            "adaptive_block_size": params[0],
            "adaptive_C": params[1],
            "min_area": params[2],
            "blur_kernel_size": params[3],
            "percent_black": params[4],
        }


PROJECT_DIR = "./experiment"
INDEX_FILE = PROJECT_DIR + "/index.dat"

if __name__ == "__main__":
    # create directory if not present
    try:
        os.mkdir(PROJECT_DIR)
    except FileExistsError:
        yes = input(
            "Project folder present. If we continue the data will be deleted. Enter 'y' to proceed: "
        )
        if yes != "y":
            os.abort()

    # Open this up early, so if we fail we don't waste 30 minutes
    with open(INDEX_FILE, "wb") as idx_file:

        img = cv.imread(TEST_IMG)
        transformed = transform_img(img, CORNERS[0], CORNERS[1], CORNERS[2], CORNERS[3])
        SAMPLE_SIZE = 500

        samples = {}  # Add our samples to this array as we create them, so
        # we can write this out and save the data for comparison purposes
        # later on. Note we use a map to handle the issue of errors.

        # We must take a small sub sample of our parameters, because
        # otherwise we would be dealing with an order of magnitude too
        # many. Hopefully we can learn something from the patterns we see
        # here and narrow down our ranges to get better results
        param_samples = random.sample(list(gen_params()), SAMPLE_SIZE)
        for i, p in enumerate(param_samples):
            try:
                print("Writing image {} of {}".format(i + 1, SAMPLE_SIZE))
                path = PROJECT_DIR + "/out_{}.png".format(i)
                out_img = pipeline(transformed, **p)
                cv.imwrite(path, out_img)
                samples[i] = {"params": p}
            except KeyboardInterrupt:
                os.abort()
            except:
                print("OpenCV ran into an error with pameters:", p)

        print("Saving index file")
        pickle.dump(samples, idx_file)
