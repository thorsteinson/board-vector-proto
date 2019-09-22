import cv2 as cv

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
def cv_click_callback(event, x, y, flags, handler):
    # Fire only when the button is lifted up
    if event == cv.EVENT_LBUTTONUP:
        handler(x, y)


# Adds a control layer for the OpenCV window and event
# mangement. Intended to be used as a singleton
class Window:
    def __init__(self):
        cv.namedWindow(WINDOW_NAME)
        self.click_handler = None
        self.exit = False
        # A dictionary that maps keycodes to handles
        # By default, map q and ESC to quit the program
        self.key_handlers = {ord("q"): self.close, KEY_ESC: self.close}

    def run(self):
        while not self.exit:
            k = cv.waitKey(WAIT_PERIOD)
            handler = self.key_handlers.get(k)
            if handler:
                handler()

    def handle_click(self, handler):
        if not callable(handler):
            raise ValueError

        self.click_handler = handler
        cv.setMouseCallback(WINDOW_NAME, cv_click_callback, handler)

    def handle_key(self, k, handler):
        if type(k) == int and k not in SPECIAL_KEYS:
            # Not one of the special keys we have codes for
            raise ValueError
        elif type(k) == str:
            k = ord(k)
        else:
            raise TypeError

        if not callable(handler):
            raise ValueError

        self.key_handlers[k] = handler

    def close(self):
        self.exit = True
        cv.destroyAllWindows()
