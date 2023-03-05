import math
import unittest

NUM_QUARTERS = 4
MINUTE = 60
MINUTES_IN_QUARTER_TIME = 12
MINUTES_IN_OVER_TIME = 5
QUARTER_TIME = MINUTES_IN_QUARTER_TIME * MINUTE
REGULAR_TIME = QUARTER_TIME * NUM_QUARTERS
OVER_TIME = MINUTES_IN_OVER_TIME * MINUTE


class Gameclock:
    def __init__(self, clock: int, quarter=1) -> None:
        self.clock = clock
        self.quarter = quarter

    def is_overtime(self) -> bool:
        return self.clock >= REGULAR_TIME

    def is_over(self) -> bool:
        return self.clock == REGULAR_TIME or (
            self.clock > REGULAR_TIME and (self.clock - REGULAR_TIME) % OVER_TIME == 0
        )

    def is_break(self) -> bool:
        return self.clock != 0 and (
            (self.clock <= REGULAR_TIME and self.clock % QUARTER_TIME == 0)
            or (self.is_overtime() and (self.clock - REGULAR_TIME) % OVER_TIME == 0)
        )

    def is_clutch(self) -> bool:
        return self.clock >= (REGULAR_TIME - OVER_TIME)

    def till_break(self) -> int:
        if self.clock < REGULAR_TIME:
            return QUARTER_TIME - (self.clock % QUARTER_TIME)
        else:
            return OVER_TIME - ((self.clock - REGULAR_TIME) % OVER_TIME)

    def minutes(self) -> int:
        if self.clock <= REGULAR_TIME and self.quarter <= NUM_QUARTERS:
            if (
                self.clock > 0
                and self.clock % QUARTER_TIME == 0
                and self.clock // QUARTER_TIME == self.quarter
            ):
                return 0

            return MINUTES_IN_QUARTER_TIME - math.ceil(
                (self.clock % QUARTER_TIME) / 60.0
            )
        else:
            if (self.clock - REGULAR_TIME) % OVER_TIME == 0 and (
                self.clock - REGULAR_TIME
            ) // OVER_TIME == self.quarter - NUM_QUARTERS:
                return 0

            return MINUTES_IN_OVER_TIME - math.ceil(
                (self.clock - REGULAR_TIME) % OVER_TIME / 60.0
            )

    def seconds(self) -> int:
        if self.clock % MINUTE == 0:
            return 0

        return MINUTE - (self.clock % MINUTE)

    def to_string(self):
        minutes = self.minutes()
        seconds = self.seconds()
        string = ""
        if minutes <= 9:
            string += "0"

        string += str(minutes)
        string += ":"
        if seconds <= 9:
            string += "0"

        string += str(seconds)
        return string


class TestGameclock(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(Gameclock(2).to_string(), "11:58")

    def test_end(self):
        self.assertEqual(Gameclock(clock=0, quarter=1).to_string(), "12:00")
        self.assertEqual(Gameclock(clock=720, quarter=1).to_string(), "00:00")
        self.assertEqual(Gameclock(clock=720, quarter=2).to_string(), "12:00")
        self.assertEqual(Gameclock(clock=720 * 4, quarter=4).to_string(), "00:00")
        self.assertEqual(Gameclock(clock=720 * 4, quarter=5).to_string(), "05:00")
        self.assertEqual(Gameclock(clock=720 * 4 + 1, quarter=5).to_string(), "04:59")
        self.assertEqual(Gameclock(clock=720 * 4 + 300, quarter=5).to_string(), "00:00")
        self.assertEqual(Gameclock(clock=720 * 4 + 300, quarter=6).to_string(), "05:00")


if __name__ == "__main__":
    unittest.main()
