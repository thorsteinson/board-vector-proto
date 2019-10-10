#!/usr/bin/python3


from params import *

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class RangeComponent:
    def __init__(self, range: RangeParam, *, label):
        self.range = range
        self._val = range.default
        self.label = Gtk.Label(label=label)
        self.label.set_halign(Gtk.Align.END)

        self.widget = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, range.min, range.max, range.step
        )
        self.widget.set_adjustment(Gtk.Adjustment(value=range.default, lower=range.min, upper=range.max, step_increment=range.step, page_increment=range.step, page_size=range.step))
        self.widget.set_size_request(200, -1)

        def set_val(range):
            value = self.range.round(range.get_value())
            self._val = value
            range.set_value(value)

        self.widget.connect("value_changed", set_val)
        self.widget.set_value(range.default)

    @property
    def value(self):
        if self.range.is_int:
            return round(self._val)
        return self._val


class FunctionComponent:
    def __init__(self, function: str, grouping: List[RangeComponent]):
        self.components = grouping
        self.function = function
        self.label = Gtk.Label(label=function)
        # Add some extra space, so we can distinguish between our functions
        self.label.set_margin_top(30)
        self.label.set_margin_bottom(10)

        self.switch = Gtk.Switch()
        self.switch.set_state(True) # Set to true by default
        self.switch.set_valign(Gtk.Align.CENTER)
        self.switch.set_halign(Gtk.Align.CENTER)

    # Returns a tuple with the name of the associated function (should
    # match the method of 'img' we wish to use) as well as any
    # parameters associated with that function. These should be Ints
    # or Floats
    @property
    def value(self) -> Tuple[str, List[Any]]:
        param_vals = [c.value for c in self.components]
        return (self.function, param_vals)

    @property
    def is_enabled(self):
        return self.switch.get_state()

# Use a grid for nice alignment of all the functions and their
# parameters together
class FunctionListComponent:
    def __init__(self, funcs: List[FunctionComponent]):
        self.funcs = funcs
        self.grid = Gtk.Grid()
        self.update_grid()

    def update_grid(self):
        for child in self.grid.get_children():
            # Completely empty the grid before proceeding
            self.grid.remove(child)

        row_idx = 0
        for func in self.funcs:
            row_height = len(func.components) + 1

            # Add the label for the  whole thing
            self.grid.attach(func.label, 1, row_idx, 1, 1)

            # Add the switch
            self.grid.attach(func.switch, 2, row_idx, 1, row_height)

            # Add the Sliders underneath with labels for the params
            for i, comp in enumerate(func.components):
                self.grid.attach(comp.label, 0, row_idx+1+i, 1, 1)
                self.grid.attach(comp.widget, 1, row_idx+1+i, 1, 1)

            row_idx += row_height

    @property
    def value(self):
        return [f.value for f in self.funcs if f.is_enabled]

class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")

        self.box = Gtk.Box(spacing=6)
        self.box.set_margin_top(10)
        self.box.set_margin_bottom(10)
        self.box.set_margin_start(10)
        self.box.set_margin_end(10)
        self.add(self.box)

        self.scale_v_1 = 0
        self.scale_v_2 = 0

        def set_scale_val_1(scale):
            self.scale_v_1 = scale.get_value()

        r1 = RangeComponent(RangeParam(0, 5, default=0.25), label="c")
        r2 = RangeComponent(RangeParam(range(31), default=5), label="block size")
        r3 = RangeComponent(RangeParam(range(5, 21, 2), default=5), label="label 3")
        r4 = RangeComponent(RangeParam(1, 20, default=10), label="label 4")

        f_comp1 = FunctionComponent("adaptive_threshold", [r1, r2])
        f_comp2 = FunctionComponent("different_func", [r3, r4])
        f_comp3 = FunctionComponent("no parameters", [])

        self.f_list = FunctionListComponent([f_comp1, f_comp2, f_comp3])

        def trigger_click1(button):
            # Cycles the function list
            self.f_list.funcs.insert(0, self.f_list.funcs.pop())
            self.f_list.update_grid()


        self.button1 = Gtk.Button(label="Press Me")
        self.button1.connect("clicked", trigger_click1)
        self.box.pack_start(self.f_list.grid, False, False, 0)
        self.box.pack_start(self.button1, False, False, 0)


# Onetime setup
win = MyWindow()
win.show_all()
win.connect("destroy", quit)
Gtk.main()
