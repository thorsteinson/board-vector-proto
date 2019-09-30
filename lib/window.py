import cv2 as cv # type: ignore
import numpy as np # type: ignore
import sys
import asyncio
from .image import Image
from typing import *


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

NULL_CODE = 255

PointType = Tuple[int, int]


# Adds a control layer for the OpenCV window and event
# mangement. Intended to be used as a singleton
class Window:
    def __init__(self):
        cv.namedWindow(WINDOW_NAME)

    def _setup_callbacks(self):
        self.loop = asyncio.get_event_loop()
        self.pos_fut = self.loop.create_future()

        def cv_click_callback(event, x, y, flags, params):
            # Fire only when the button is lifted up
            if event == cv.EVENT_LBUTTONUP:
                self.pos_fut.set_result((x, y))

        cv.setMouseCallback(WINDOW_NAME, cv_click_callback, None)

        self.key_fut = self.loop.create_future()

    def run(self, coro: Awaitable) -> bool:
        self._setup_callbacks()

        task = self.loop.create_task(coro)

        # Drives the events through the usage of waitkey. Without it,
        # no events will ever be registered
        def driver():
            key_code = cv.waitKey(WAIT_PERIOD)
            if key_code == ord("q") or key_code == KEY_ESC:
                # Quit, the user wants out
                task.cancel()
                return
            if key_code != NULL_CODE:
                if self.key_fut.done():
                    # Reset our future, so old keys aren't sent
                    self.key_fut = self.loop.create_future()
                self.key_fut.set_result(key_code)

            # Reset future to ensure clicks aren't queued
            if self.pos_fut.done():
                self.pos_fut = self.loop.create_future()

            # Keep calling this, driving the main event loop
            self.loop.call_soon(driver)

        self.loop.call_soon(driver)
        try:
            self.loop.run_until_complete(task)
            return True
        except asyncio.CancelledError:
            return False

    def run_until_quit(self):
        while True:
            if cv.waitKey(-1) == ord("q") or key_code == KEY_ESC:
                return

    # Returns the X, Y coordinates of the position clicked
    async def click(self) -> PointType:
        p = await self.pos_fut
        # Reset the future for the next click
        self.pos_fut = self.loop.create_future()
        return p

    # Returns the keycode, or the character pressed if possible
    async def keypress(self) -> Union[int, str]:
        key_code = await self.key_fut
        self.key_fut = self.loop.create_future()
        if key_code in SPECIAL_KEYS:
            return key_code
        else:
            return chr(key_code)

    def show(self, img: Image):
        if isinstance(img, Image):
            cv.imshow(WINDOW_NAME, img.img)
        elif isinstance(np.ndarray):
            cv.imshow(WINDOW_NAME, img)
        else:
            raise TypeError
