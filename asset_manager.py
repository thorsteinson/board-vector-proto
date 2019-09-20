# Asset manager provides tools for managing a local database of
# photos, that are tagged with point information. These photos can
# then be used in other commands, without us having to specify via the
# command line.

import pickle
import collections
import os
from pathlib import Path
import argparse


# A tuple to represent an entry in our database
# - Name is the name of the file in our asset directory,
# - Points is a vector of 4 points, describing the perspective transform
# on an image
Entry = collections.namedtuple("Entry", "name points")

ASSET_FOLDER = "./assets"
ASSET_DATA_FILE = ASSET_FOLDER + "/data.dat"

# Singleton class
class AssetManager:
    def __init__(self):
        if not os.path.exists(ASSET_FOLDER):
            os.mkdir(ASSET_FOLDER)

        if not os.path.exists(ASSET_DATA_FILE):
            self._entries = []
        else:
            with open(ASSET_DATA_FILE, "rb") as data_f:
                self._entries = pickle.load(data_f)

    # Adds the entry
    def add(self, photo_path, points):
        if not os.path.exists(photo_path):
            raise ValueError

        # Check the points, ensure they all are in a good format
        validate_points(points)

        # Hard link photo into asset folder.
        name = photo_path.name
        dst = Path(ASSET_FOLDER, name)
        os.link(photo_path, dst)

        # Modify state
        entry = Entry(name, points)
        self._entries.append(entry)

        # Persist state
        self.save()

    def delete(self, n):
        if n < len(self._entries):
            del (self._entries[n])

    # Writes data to main file
    def save(self):
        with open(ASSET_DATA_FILE, "wb") as data_f:
            pickle.dump(self._entries, data_f)

    def get(self, i):
        return self._entries[i]


def validate_points(points):
    if len(points) != 4:
        raise ValueError

    for p in points:
        x = p[0]
        y = p[1]
        if type(x) != int or type(y) != int or x < 0 or y < 0:
            raise ValueError

    return True


def get_points(args):
    return [
        (args.x1, args.y1),
        (args.x2, args.y2),
        (args.x3, args.y3),
        (args.x4, args.y4),
    ]


add_parser = argparse.ArgumentParser(description="Add an asset with set coordinates")
add_parser.add_argument("photopath", help="Path of the photo you want to add")
add_parser.add_argument(
    "x1", help="Pixel coordinates for perspective transform", type=int
)
add_parser.add_argument("y1", type=int)
add_parser.add_argument("x2", type=int)
add_parser.add_argument("y2", type=int)
add_parser.add_argument("x3", type=int)
add_parser.add_argument("y3", type=int)
add_parser.add_argument("x4", type=int)
add_parser.add_argument("y4", type=int)

interactive_add_parser = argparse.ArgumentParser(
    description="Add assets interactively by clicking points"
)
interactive_add_parser.add_argument(
    "photopaths", nargs="?", help="Path of the photos you want to add"
)

delete_parser = argparse.ArgumentParser(description="Remove an assset")
delete_parser.add_argument("n", type=int, help="The asset number you want to remove")

if __name__ == "__main__":
    args = add_parser.parse_args()

    mgr = AssetManager()
    mgr.add(Path(args.photopath), get_points(args))
