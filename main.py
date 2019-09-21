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
from image import Image


def get_point(event, x, y, flags, points):
    # The button click is finished, get the position
    if event == cv.EVENT_LBUTTONUP:
        points.append((x, y))


SCALE_FACTOR = 4

X_MAX = 1850
Y_MAX = 1000


def view(args):
    mgr = assets.AssetManager()

    (path, points) = mgr.get(args.n)

    img = Image(path)
    img.perspective_transform(points)
    img.scale_bounded(X_MAX, Y_MAX)
    cv.namedWindow("image")
    cv.imshow(
        "image",
        img.img,
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
