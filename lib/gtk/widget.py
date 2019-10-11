import gi  # type: ignore

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # type: ignore

from typing import *
import enum
from .params import RangeParam


class Margins(NamedTuple):
    start: int
    end: int
    top: int
    bottom: int


class Orientation(enum.Enum):
    HORIZONTAL = Gtk.Orientation.HORIZONTAL
    VERTICAL = Gtk.Orientation.VERTICAL


class Align(enum.Enum):
    FILL = Gtk.Align.FILL
    START = Gtk.Align.START
    END = Gtk.Align.END
    CENTER = Gtk.Align.CENTER
    BASELINE = Gtk.Align.BASELINE


class Position(enum.Enum):
    LEFT = Gtk.PositionType.LEFT
    RIGHT = Gtk.PositionType.RIGHT
    TOP = Gtk.PositionType.TOP
    BOTTOM = Gtk.PositionType.BOTTOM


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

    @property
    def vexpand(self) -> bool:
        return self.internal_widget.get_vexpand()

    @vexpand.setter
    def vexpand(self, should_expand: bool):
        self.internal_widget.set_vexpand(should_expand)

    @property
    def hexpand(self) -> bool:
        return self.internal_widget.get_hexpand()

    @hexpand.setter
    def hexpand(self, should_expand: bool):
        self.internal_widget.set_hexpand(should_expand)


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
        super().__init__(Gtk.Label(label=text))


# A wrapper for the grid that allows us to add our wrapped widgets
# directly
class Grid(Widget):
    def __init__(self):
        super().__init__(Gtk.Grid())

        # Modify the default alignment, as we likely want these fill
        self.align = (Align.FILL, Align.FILL)

    def attach(
        self,
        widget: Widget,
        column: int,
        row: int,
        column_span: int = 1,
        row_span: int = 1,
    ):
        self.internal_widget.attach(
            widget.internal_widget, column, row, column_span, row_span
        )

    # Removes all attached children
    def reset(self):
        for child in self.internal_widget.get_children():
            self.internal_widget.remove(child)


# A smart scale object that takes a range parameter for a well define
# range and whose value always reflects a valid value within that range
class Scale(Widget):
    def __init__(
        self,
        range: RangeParam,
        orientation: Orientation = Orientation.HORIZONTAL,
        val_pos: Position = Position.RIGHT,
    ):
        super().__init__(
            Gtk.Scale.new_with_range(
                Gtk.Orientation.HORIZONTAL, range.min, range.max, range.step
            )
        )

        # Set the orientation
        self.internal_widget.set_orientation(orientation.value)

        # Set the value position
        self.internal_widget.set_value_pos(val_pos.value)

        self.range = range
        self._val = range.default

        self.internal_widget.set_adjustment(
            Gtk.Adjustment(
                value=range.default,
                lower=range.min,
                upper=range.max,
                step_increment=range.step,
                page_increment=range.step,
                page_size=range.step,
            )
        )

        def set_val(range):
            value = self.range.round(range.get_value())
            self._val = value
            range.set_value(value)

        self.internal_widget.connect("value_changed", set_val)
        self.internal_widget.set_value(range.default)

    @property
    def value(self):
        if self.range.is_int:
            return round(self._val)
        return self._val


# A collection of widgets for scales, along with associated labels,
# all under a single grid
class ScaleGrid(Grid):
    def __init__(self, range_pairs: List[Tuple[str, RangeParam]]):
        super().__init__()

        self.scales: List[Scale] = []

        for row_idx, (text, range_p) in enumerate(range_pairs):
            label = Label(text)
            label.align = (Align.END, Align.FILL)

            scale = Scale(range_p)
            scale.align = (Align.FILL, Align.CENTER)
            scale.hexpand = True

            self.scales.append(scale)

            self.attach(label, 0, row_idx)
            self.attach(scale, 1, row_idx)


class FunctionComponent(Widget):
    def __init__(self, function_name, range_pairs: List[Tuple[str, RangeParam]]):
        super().__init__(Gtk.Box(spacing=10))

        # VBox, with the label for the function,
        self.internal_widget.set_orientation(Orientation.VERTICAL.value)

        function_label = Label(function_name)
        self.internal_widget.add(function_label.internal_widget)

        # HBox, with the scale_grid, and the switch
        parameter_grid = ScaleGrid(range_pairs)
        self.enabled_switch = Switch()
        self.enabled_switch.align = (Align.CENTER, Align.CENTER)

        hbox = Gtk.Box(spacing=10)
        hbox.set_halign(Gtk.Align.FILL)
        hbox.set_orientation(Orientation.HORIZONTAL.value)
        hbox.pack_start(parameter_grid.internal_widget, True, True, 0)
        hbox.pack_start(self.enabled_switch.internal_widget, False, False, 0)

        self.internal_widget.pack_start(function_label.internal_widget, False, False, 0)
        self.internal_widget.pack_start(hbox, True, True, 0)
        self.internal_widget.set_halign(Gtk.Align.FILL)

        # Create references so we can determine value as it updates
        self.scales = parameter_grid.scales
        self.function_name = function_name

    @property
    def value(self) -> Tuple[str, List[Any]]:
        return (self.function_name, [s.value for s in self.scales])

    @property
    def enabled(self) -> bool:
        return self.enabled_switch.on
