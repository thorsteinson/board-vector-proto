#!/usr/bin/python3

# The main interface for the program. Divides everything into sub
# commands for an easy to use iterface with a single entry point.

import argparse
import sys
import asset_manager as assets
from pathlib import Path
import cv2 as cv
import time
import numpy as np
from cmdlet import Commander, Cmdlet


def get_point(event, x, y, flags, points):
    # The button click is finished, get the position
    if event == cv.EVENT_LBUTTONUP:
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
    cv.setMouseCallback("image", get_point, points)
    for path in paths:
        img = cv.imread(str(path))
        xres = img.shape[1]
        yres = img.shape[0]

        cv.imshow(
            "image",
            cv.resize(img, (round(xres / SCALE_FACTOR), round(yres / SCALE_FACTOR))),
        )

        while len(points) < 4:
            # Wait key must be called! Otherwise the event loop
            # doesn't run. We'll basically move the clock forward
            # every 10 ms
            cv.waitKey(10)

        # Now we can add an entry to our db
        mgr.add(path, [(p[0] * SCALE_FACTOR, p[1] * SCALE_FACTOR) for p in points])
        points.clear()


if __name__ == "__main__":
    iadd_cmd = Cmdlet("iadd", "Interactively add coordinates", interactive_add)
    iadd_cmd.add_arg(
        "photopaths", nargs="+", help="Paths of the photos you want to add"
    )

    view_cmd = Cmdlet(
        "view",
        "View an image in the db with the perspective transformation applied",
        view,
    )
    view_cmd.add_arg("n", type=int, help="Image number in the db to lookup")

    commander = Commander([assets.add_cmd, assets.delete_cmd, iadd_cmd, view_cmd])
    commander.run()
