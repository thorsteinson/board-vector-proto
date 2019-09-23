# Asset manager provides tools for managing a local database of
# photos, that are tagged with point information. These photos can
# then be used in other commands, without us having to specify via the
# command line.

import pickle
import collections
import os
from pathlib import Path
from cmdlet import Cmdlet

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
        if n < len(self._entries) and n >= 0:
            path = Path(ASSET_FOLDER, self._entries[n].name)
            os.remove(path)
            del (self._entries[n])
            self.save()

    # Writes data to main file
    def save(self):
        with open(ASSET_DATA_FILE, "wb") as data_f:
            pickle.dump(self._entries, data_f)

    # Returns the PATH (not name), and the transform points
    def get(self, i):
        entry = self._entries[i]
        return (Path(ASSET_FOLDER, entry.name), entry.points)


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


def add(args):
    mgr = AssetManager()
    print(args)
    mgr.add(Path(args.photopath), assets.get_points(args))


add_cmd = Cmdlet("add", "Add an asset with set coordinates", add)
add_cmd.add_arg("photopath", help="Path of the photo you want to add").add_arg(
    "x1", help="Pixel coordinates for perspective transform", type=int
).add_arg("y1", type=int).add_arg("x2", type=int).add_arg("y2", type=int).add_arg(
    "x3", type=int
).add_arg(
    "y3", type=int
).add_arg(
    "x4", type=int
).add_arg(
    "y4", type=int
)


def delete_asset(args):
    mgr = AssetManager()
    mgr.delete(args.n)


delete_cmd = Cmdlet("delete", "Remove an asset from the db", delete_asset)
delete_cmd.add_arg("n", type=int, help="The asset number you want to remove")
