# The main interface for the program. Divides everything into sub
# commands for an easy to use iterface with a single entry point.

import argparse
import sys
import asset_manager as assets
from pathlib import Path
import cv2 as cv
import time
import numpy as np


def add(args):
    mgr = assets.AssetManager()
    mgr.add(Path(args.photopath), assets.get_points(args))


def delete(args):
    mgr = assets.AssetManager()
    mgr.delete(args.n)


def add_view_parser(subparsers):
    view_parser = subparsers.add_parser(
        "view",
        help="View an image in the db with the perspective transformation applied",
    )
    view_parser.add_argument("n", type=int, help="Image number in the db to lookup")


def get_point(event, x, y, flags, params):
    scaleFactor = params[0]
    points = params[1]

    # The button click is finished, get the position
    if event == cv.EVENT_LBUTTONUP:
        selected_x = x
        selected_y = y
        points.append((x, y))


SCALE_FACTOR = 4


def transform_img(img, points):
    top_left = points[0]
    top_right = points[1]
    bottom_right = points[2]
    bottom_left = points[3]

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


def view(args):
    mgr = assets.AssetManager()

    (path, points) = mgr.get(args.n)

    img = cv.imread(str(path))
    transformed = transform_img(img, points)
    xres = transformed.shape[1]
    yres = transformed.shape[0]
    cv.namedWindow("image")
    cv.imshow(
        "image",
        cv.resize(
            transformed, (round(xres / SCALE_FACTOR), round(yres / SCALE_FACTOR))
        ),
    )
    cv.waitKey()


def interactive_add(args):
    mgr = assets.AssetManager()
    paths = [Path(p) for p in args.photopaths]
    cv.namedWindow("image")
    points = []
    cv.setMouseCallback("image", get_point, param=(SCALE_FACTOR, points))
    for path in paths:
        img = cv.imread(str(path))
        xres = img.shape[1]
        yres = img.shape[0]

        cv.imshow(
            "image",
            cv.resize(img, (round(xres / SCALE_FACTOR), round(yres / SCALE_FACTOR))),
        )

        global points_clicked
        while len(points) < 4:
            # Wait key must be called! Otherwise the event loop
            # doesn't run. We'll basically move the clock forward
            # every 10 ms
            cv.waitKey(10)

        # Now we can add an entry to our db
        mgr.add(path, [(p[0] * SCALE_FACTOR, p[1] * SCALE_FACTOR) for p in points])
        points.clear()


command_map = {"add": add, "delete": delete, "iadd": interactive_add, "view": view}

if __name__ == "__main__":
    main_parser = argparse.ArgumentParser("Board Vector")

    subparsers = main_parser.add_subparsers(help="sub command help")

    assets.add_add_parser(subparsers)
    assets.add_delete_parser(subparsers)
    assets.add_add_interactive_parser(subparsers)
    add_view_parser(subparsers)

    args = main_parser.parse_args()

    command = sys.argv[1]

    if command not in command_map:
        raise ValueError

    command_map[command](args)
