import cv2 as cv
import numpy as np
import sys
from image import Image


WINDOW_NAME = "Board Vector"
WAIT_PERIOD = 10

KEY_UP = 82
KEY_DOWN = 84
KEY_LEFT = 81
KEY_RIGHT = 83
KEY_SPACE = 32
KEY_ENTER = 10
KEY_ESC = 27

SPECIAL_KEYS = {KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_SPACE, KEY_ENTER, KEY_ESC}

# Modifies a click handler that the handler will work with OpenCV
# style callbacks.
def cv_click_callback(event, x, y, flags, params):
    # Fire only when the button is lifted up
    if event == cv.EVENT_LBUTTONUP:
        handler, data = params
        if data:
            handler(x, y, data)
        else:
            handler(x, y)


# Adds a control layer for the OpenCV window and event
# mangement. Intended to be used as a singleton
class Window:
    def __init__(self):
        cv.namedWindow(WINDOW_NAME)
        self.click_handler = None
        self.exit = False
        # By default, our quit handler just spits out false, no matter what
        self.quit_handler = lambda: False
        self.quit_data = None
        # A dictionary that maps keycodes to handles
        # By default, map q and ESC to quit the program
        self.key_handlers = {ord("q"): (sys.exit, None), KEY_ESC: (sys.exit, None)}

    # Run will basically stay in this loop until some exit condition
    # has been reached through the quit_on callback, or through close
    # being called on the window.
    def run(self):
        while not self.exit:
            if self.quit_data:
                quit = self.quit_handler(self.quit_data)
            else:
                quit = self.quit_handler()
            if quit:
                break

            k = cv.waitKey(WAIT_PERIOD)
            pair = self.key_handlers.get(k)
            if pair:
                handler, data = pair
                if data:
                    handler(data)
                else:
                    handler()

    def handle_click(self, handler, data=None):
        if not callable(handler):
            raise ValueError

        self.click_handler = handler
        cv.setMouseCallback(WINDOW_NAME, cv_click_callback, (handler, data))

    def handle_key(self, k, handler, data=None):
        if type(k) == int and k not in SPECIAL_KEYS:
            # Not one of the special keys we have codes for
            raise ValueError
        # Need to organize and fix this disaster
        elif k in SPECIAL_KEYS:
            k = k
        elif type(k) == str:
            k = ord(k)
        else:
            raise TypeError

        if not callable(handler):
            raise ValueError

        self.key_handlers[k] = (handler, data)

    def quit_on(self, quit_handler, data=None):
        self.quit_handler = quit_handler
        self.quit_data = data

    def close(self):
        self.exit = True
        cv.destroyAllWindows()

    def show(self, img):
        if isinstance(img, Image):
            cv.imshow(WINDOW_NAME, img.img)
        elif isinstance(np.ndarray):
            cv.imshow(WINDOW_NAME, img)
        else:
            raise TypeError
