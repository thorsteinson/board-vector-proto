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
    win = Window()
    points = []
    img = None
    scaled = None
    factor = None
    image_added = False

    def add_point(x, y):
        nonlocal scaled, img

        # Add no more points after the 4th
        if len(points) < 4:
            points.append((x, y))
            if len(points) == 4:
                p1 = points[-1]
                p2 = points[0]
                p3 = points[-2]
                img.draw_line(p1, p2)
                img.draw_line(p1, p3)
            elif len(points) > 1:
                p1 = points[-2]
                p2 = points[-1]
                img.draw_line(p1, p2)
            win.show(img)
        else:
            # Reset image to the scaled down version with no lines, and
            # then copy again
            points.clear()
            img = scaled
            scaled = copy(img)
            win.show(img)
            # Call ourself again, so that the point will actually be added
            add_point(x, y)

    # Adds image to the database
    def add_image():
        nonlocal image_added

        if len(points) == 4:
            inverse = 1 / factor
            mgr.add(
                path, [(round(p[0] * inverse), round(p[1] * inverse)) for p in points]
            )
            points.clear()
            image_added = True

    win.handle_click(add_point)
    win.handle_key(KEY_ENTER, add_image)
    win.quit_on(lambda: image_added == True)
    for path in paths:
        image_added = False
        img = Image(path)
        factor = img.scale_bounded(X_MAX, Y_MAX)
        scaled = copy(img)
        win.show(img)
        win.run()


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
