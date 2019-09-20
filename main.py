# The main interface for the program. Divides everything into sub
# commands for an easy to use iterface with a single entry point.

import argparse
import sys
import asset_manager as assets
from pathlib import Path
import cv2 as cv
import time


def add(args):
    mgr = assets.AssetManager()
    mgr.add(Path(args.photopath), assets.get_points(args))


def delete(args):
    mgr = assets.AssetManager()
    mgr.delete(args.n)


def get_point(event, x, y, flags, params):
    scaleFactor = params[0]
    points = params[1]

    # The button click is finished, get the position
    if event == cv.EVENT_LBUTTONUP:
        selected_x = x
        selected_y = y
        points.append((x, y))


SCALE_FACTOR = 4


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
        mgr.add(path, points.copy())
        points.clear()


command_map = {"add": add, "delete": delete, "iadd": interactive_add}

if __name__ == "__main__":
    main_parser = argparse.ArgumentParser("Board Vector")

    subparsers = main_parser.add_subparsers(help="sub command help")

    assets.add_add_parser(subparsers)
    assets.add_delete_parser(subparsers)
    assets.add_add_interactive_parser(subparsers)

    args = main_parser.parse_args()

    command = sys.argv[1]

    if command not in command_map:
        raise ValueError

    command_map[command](args)
