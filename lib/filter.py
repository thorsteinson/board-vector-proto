import cv2 as cv
import numpy as np
import pickle

PROJECT_DIR = "./experiment"
INDEX_FILE = PROJECT_DIR + "/index.dat"
SPACE_KEY = 32


def collect_data(data_map):
    for i, data in data_map.items():
        img = cv.imread("{}/out_{}.png".format(PROJECT_DIR, i))
        cv.imshow("File", cv.resize(img, (500, 1000)))
        key = cv.waitKey()
        data["good_image"] = key == SPACE_KEY  # Pressing space marks it as
        # a legible good image


def summarize_stats(data_map):
    quality_params = [
        data["params"] for data in data_map.values() if data["good_image"]
    ]

    keys = [
        "adaptive_block_size",
        "adaptive_C",
        "min_area",
        "blur_kernel_size",
        "percent_black",
    ]

    means = {}

    for k in keys:
        total = 0
        n = 0
        # find the mean statistic
        for params in quality_params:
            n += 1
            total += params[k]
        means[k] = total / n

    return means


if __name__ == "__main__":
    with open(INDEX_FILE, "r+b") as idx_file:
        data_map = pickle.load(idx_file)
        collect_data(data_map)
        # Write the data back out, the data map passed in is mutated
        pickle.dump(data_map, idx_file)

    print(summarize_stats(data_map))
