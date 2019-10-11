#!/usr/bin/python3


from .params import *
from .widget import FunctionComponent

import gi  # type: ignore

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # type: ignore

class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")

        self.box = Gtk.Box(spacing=6)
        self.box.set_margin_top(10)
        self.box.set_margin_bottom(10)
        self.box.set_margin_start(10)
        self.box.set_margin_end(10)
        self.add(self.box)

        f_comp1 = FunctionComponent(
            "adaptive_threshhold",
            [
                ("c", RangeParam(range(21), default=5)),
                ("block", RangeParam(range(0, 10, 2), default=0)),
                ("beta block", RangeParam(0, 1, default=0.5)),
            ],
        )

        # def trigger_click1(button):
        #     # Cycles the function list
        #     self.f_list.funcs.insert(0, self.f_list.funcs.pop())
        #     self.f_list.update_grid()

        # self.button1 = Gtk.Button(label="Press Me")
        # self.button1.connect("clicked", trigger_click1)
        self.box.add(f_comp1.internal_widget)
        # self.add(self.button1, False, False, 0)



def main(args):
    # Onetime setup
    win = MyWindow()
    win.show_all()
    win.connect("destroy", quit)
    Gtk.main()
