import math
from typing import *


class RangeParam:
    def __init__(self, p1, *args, default):
        if type(p1) == range:
            if default >= p1.stop or default < p1.start:
                raise ValueError("Default value is outside of range boundary")
            # If there's a non 1 step value, ensure that it's also in the range
            if (default - p1.start) % p1.step != 0:
                raise ValueError("Default value is in-bounds, but not along step path")
            self.min = p1.start
            self.max = p1.stop
            self.step = p1.step

            self.is_int = True

        else:
            self.max = args[0]
            self.min = p1
            self.is_int = False
            self.step = 0.01

            if default >= self.max or default < self.min:
                raise ValueError("Default value is outside of range boundary")

        self.default = default

    def __iter__(self):
        if self.is_int:
            return iter(range(self.min, self.max, self.step))
        else:
            # Determine how many steps there will be
            steps = math.ceil((self.max - self.min) / self.step)

            # Create a range with that many steps, and map the values
            # so we get proper increments
            distribution = map(lambda n: self.min + (n * self.step), range(steps))
            return iter(distribution)

    # Rounds to the nearest valid value in the range
    def round(self, n):
        # Clamp value, if it was outside the range
        n = min(self.max, n)
        n = max(self.min, n)

        # Set range to 0, so we can scale
        n -= self.min

        n = round(n / self.step)
        n = n * self.step

        # Add minimum value back
        n += self.min

        return n
