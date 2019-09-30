#!/usr/bin/python3

from lib.asset_manager import add_cmd, delete_cmd
from lib.cmdlet import Commander, Cmdlet
from lib.image import Image
from lib.window import KEY_ENTER
from lib import get_window, get_asset_mgr
from pathlib import Path
from copy import copy
from argparse import Namespace
from typing import *

X_MAX = 1850
Y_MAX = 1000

PointType = Tuple[int, int]

def view(args: Namespace):
    mgr = get_asset_mgr()

    (path, points) = mgr.get(args.n)

    img = Image(path)
    img.perspective_transform(points)
    img.scale_bounded(X_MAX, Y_MAX)
    win = get_window()
    win.show(img)
    win.run_until_quit()


def interactive_add(args: Namespace):
    mgr = get_asset_mgr()
    paths = [Path(p) for p in args.photopaths]
    points: List[PointType] = []

    async def add():
        # Adds image to the database
        def add_image():
            inverse = 1 / factor
            mgr.add(
                path, [(round(p[0] * inverse), round(p[1] * inverse)) for p in points]
            )
            points.clear()

        for path in paths:
            img = Image(path)
            factor = img.scale_bounded(X_MAX, Y_MAX)
            scaled = copy(img)
            win.show(img)

            while True:
                while len(points) < 4:
                    x, y = await win.click()
                    points.append((x, y))
                    if len(points) == 4:
                        p1 = points[-1]
                        p2 = points[0]
                        img.draw_line(p1, p2)
                    if len(points) > 1:
                        p1 = points[-2]
                        p2 = points[-1]
                        img.draw_line(p1, p2)

                    img.draw_point(x, y)
                    win.show(img)

                k = await win.keypress()

                if k == KEY_ENTER:
                    add_image()
                    break

                # Reset
                points.clear()
                img = copy(scaled)
                win.show(img)

    win = get_window()
    win.run(add())


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

    commander = Commander([add_cmd, delete_cmd, iadd_cmd, view_cmd])
    commander.run()
