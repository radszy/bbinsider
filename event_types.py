from enum import IntEnum, auto


class ShotType(IntEnum):
    # Just a normal 3PT?
    DEFAULT_THREE_POINTER = 100
    TOPKEY_THREE_POINTER = 101
    WING_THREE_POINTER = 102
    CORNER_THREE_POINTER = 103
    LONG_THREE_POINTER = 104
    HALF_COURT_THREE_POINTER = 105
    # Just a normal 2PT?
    DEFAULT_TWO_POINTER = 200
    ELBOW_TWO_POINTER = 201
    WING_TWO_POINTER = 202
    BASELINE_TWO_POINTER = 203
    TOPKEY_TWO_POINTER = 204
    DUNK1 = 401
    LAYUP = 402
    POST_UP_MOVE = 403
    FADE_AWAY = 404
    HOOK = 405
    OFF_DRIBBLE_JUMP_SHOT = 406
    PUTBACK_DUNK = 407
    TIPIN = 408
    REBOUND_SHOT = 409
    DUNK2 = 410
    DRIVING_LAYUP = 411


class ShotResult(IntEnum):
    MISSED = 0
    SCORED = 1
    GOALTEND = 2
    BLOCKED = 3
    MISSED_WITH_FOUL = 4
    SCORED_WITH_FOUL = 5


class FreeThrowType(IntEnum):
    REGULAR = auto()
    TECHNICAL = auto()


class InterruptType(IntEnum):
    THREE_SEC_VIOLATION = 801
    BALL_THROWN_OUT = 802
    SHOTCLOCK_VIOLATION = 804
    PASS_INTERCEPTED = 808
    BALL_STOLEN = 807
    TRAVELLING = 810
    LOST_HANDLE = 812


class ReboundType(IntEnum):
    OFF_REBOUND = 9317
    DEF_REBOUND = 9318
    # How is this one different?
    DEFAULT_REBOUND = 9319
    REBOUND_OUT_OF_BOUNDS = 934
    JUMP_BALL = 933


class FoulType(IntEnum):
    OFFENSIVE_FOUL = 803
    SHOOTING_FOUL = 504
    PERSONAL_FOUL = 507


class InjuryType(IntEnum):
    INJURY_OUT = 901
    INJURY_BACK = 902
    EXHAUSTED = 903
    FAINTED = 904


class SubType(IntEnum):
    SUB_PG = 9510
    SUB_SG = 9511
    SUB_SF = 9512
    SUB_PF = 9513
    SUB_C = 9514
    POS_SWAP = 9520


class BreakType(IntEnum):
    TIMEOUT_30 = 7060
    TIMEOUT_60 = 7061
    END_OF_QUARTER = 961
    END_OF_HALF = 963
    END_OF_GAME = 962
