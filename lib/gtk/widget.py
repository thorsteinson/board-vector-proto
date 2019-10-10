import gi # type: ignore
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk # type: ignore

from typing import *
import enum

class Margins(NamedTuple):
    start: int
    end: int
    top: int
    bottom: int

class Align(enum.Enum):
    FILL = Gtk.Align.FILL
    START = Gtk.Align.START
    END = Gtk.Align.END
    CENTER = Gtk.Align.CENTER
    BASELINE = Gtk.Align.BASELINE


# Takes a GTK widget and wraps it up in a nicer interface for us to
# work with. Adds setters and properties for commonly accessed
# elements of widgets.
class Widget:
    def __init__(self, gtk_widget):
        self.internal_widget = gtk_widget

        # Modify the default alignment, since fill tends to be ridiculous
        self.align = (Align.CENTER, Align.CENTER)

    @property
    def margins(self) -> Margins:
        return Margins(
            start=self.internal_widget.get_margin_start(),
            end=self.internal_widget.get_margin_end(),
            bottom=self.internal_widget.get_margin_bottom(),
            top=self.internal_widget.get_margin_top(),
        )

    @margins.setter
    def margins(self, margins: Margins):
            self.internal_widget.set_margin_start(margins.start)
            self.internal_widget.set_margin_end(margins.end)
            self.internal_widget.set_margin_bottom(margins.bottom)
            self.internal_widget.set_margin_top(margins.top)


    @property
    def align(self) -> Tuple[Align, Align]:
        return self.internal_widget.get_halign()

    @align.setter
    def align(self, align: Tuple[Align, Align]):
        halign, valign = align
        self.internal_widget.set_halign(halign.value)
        self.internal_widget.set_valign(valign.value)

    @property
    def min_width(self):
        return self.internal_widget.get_preferred_width()

    @min_width.setter
    def min_width(self, width):
        self.internal_widget.set_size_request(width, -1)

# Make a switch that's on by default, and with a simple on property
# that reads the state of the underlying widget.
class Switch(Widget):
    def __init__(self, on=True):
        super().__init__(Gtk.Switch())
        print(self.internal_widget)
        self.internal_widget.set_state(on)

    @property
    def on(self):
        return self.interactive_add.get_state()

# A class that makes adding text really simple.
class Label(Widget):
    def __init__(self, text):
        super().__init__(gtk.Label(label=text))
