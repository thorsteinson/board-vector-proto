#!/usr/bin/python3

# The main interface for the program. Divides everything into sub
# commands for an easy to use iterface with a single entry point.

import asset_manager as assets
from pathlib import Path
from cmdlet import Commander, Cmdlet
from image import Image
from window import Window, KEY_ENTER, KEY_SPACE
from copy import copy


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
    points = []

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

    win = Window()
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

    commander = Commander([assets.add_cmd, assets.delete_cmd, iadd_cmd, view_cmd])
    commander.run()
