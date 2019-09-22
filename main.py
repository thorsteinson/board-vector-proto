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
from window import Window


X_MAX = 1850
Y_MAX = 1000


def view(args):
    mgr = assets.AssetManager()

    (path, points) = mgr.get(args.n)

    img = Image(path)
    img.perspective_transform(points)
    img.scale_bounded(X_MAX, Y_MAX)
    win = Window()
    win.show(img)
    win.run()


def interactive_add(args):
    mgr = assets.AssetManager()
    paths = [Path(p) for p in args.photopaths]
    win = Window()
    points = []
    win.handle_click(lambda x, y: points.append((x, y)))
    win.quit_on(lambda points: len(points) >= 4, data=points)
    for path in paths:
        img = Image(path)
        factor = img.scale_bounded(X_MAX, Y_MAX)
        win.show(img)
        win.run()
        # At this point, we must have all 4 points, or they pressed q

        # Now we can add an entry to our db
        inverse = 1 / factor
        mgr.add(path, [(round(p[0] * inverse), round(p[1] * inverse)) for p in points])
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
