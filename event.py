from enum import IntEnum, auto
from venv import create

from clocks import Gameclock
from team import Team, opponent
from player import Player
import math
from event_types import *


class Clocks:
    def __init__(self, game: int, real: int, shot: int) -> None:
        self.game = game
        self.real = real
        self.shot = shot


class ShotPos:
    def __init__(self, posx: int, posy: int) -> None:
        self.x = posx
        self.y = posy


class BaseEvent:
    def __init__(self, comments: list[str], clocks: Clocks) -> None:
        self.comments = comments
        self.gameclock = clocks.game
        self.realclock = clocks.real
        self.shotclock = clocks.shot

    def patch_shotclock(self, clock):
        self.shotclock = clock


class ShotEvent(BaseEvent):
    def __init__(
        self,
        comments: list[str],
        clocks: Clocks,
        shot_type: ShotType,
        shot_result: ShotResult,
        attacker: int,
        defender: int,
        assistant: int,
        att_team: int,
        def_team: int,
        shot_pos: ShotPos,
    ) -> None:
        super().__init__(comments, clocks)
        self.shot_type = shot_type
        self.shot_result = shot_result
        self.attacker = attacker
        self.defender = defender
        self.assistant = assistant
        self.att_team = att_team
        self.def_team = def_team
        self.shot_pos = shot_pos

    def is_3pt(self):
        return self.shot_type in (
            ShotType.THREE_POINTER_DEFAULT,
            ShotType.THREE_POINTER_LONG,
            ShotType.THREE_POINTER_WING,
            ShotType.THREE_POINTER_CORNER,
            ShotType.THREE_POINTER_TOPKEY,
            ShotType.THREE_POINTER_HALFCOURT,
        )

    def is_blocked(self):
        return self.shot_result == ShotResult.BLOCKED

    def is_assisted(self):
        return self.assistant != 0

    def is_fouled(self):
        return self.shot_result in (
            ShotResult.SCORED_WITH_FOUL,
            ShotResult.MISSED_WITH_FOUL,
        )

    def is_rebound(self):
        return self.shot_type in (
            ShotType.TIPIN,
            ShotType.PUTBACK_DUNK,
            ShotType.REBOUND_SHOT,
        )

    def has_scored(self):
        return self.shot_result in (
            ShotResult.SCORED,
            ShotResult.SCORED_WITH_FOUL,
            ShotResult.GOALTEND,
        )

    def has_missed(self):
        return not self.has_scored()


class InterruptEvent(BaseEvent):
    def __init__(
        self,
        comments: list[str],
        clocks: Clocks,
        interrupt_type: InterruptType,
        attacker: int,
        defender: int,
        att_team: int,
        def_team: int,
    ) -> None:
        super().__init__(comments, clocks)
        self.interrupt_type = interrupt_type
        self.attacker = attacker
        self.defender = defender
        self.att_team = att_team
        self.def_team = def_team


class FoulEvent(BaseEvent):
    def __init__(
        self,
        comments: list[str],
        clocks: Clocks,
        foul_type: FoulType,
        attacker: int,
        defender: int,
        att_team: int,
        def_team: int,
        flagrant: int,
    ) -> None:
        super().__init__(comments, clocks)
        self.foul_type = foul_type
        self.attacker = attacker
        self.defender = defender
        self.att_team = att_team
        self.def_team = def_team
        self.flagrant = flagrant


class ReboundEvent(BaseEvent):
    def __init__(
        self,
        comments: list[str],
        clocks: Clocks,
        rebound_type: ReboundType,
        attacker: int,
        defender: int,
        att_team: int,
        def_team: int,
    ) -> None:
        super().__init__(comments, clocks)
        self.rebound_type = rebound_type
        self.attacker = attacker
        self.defender = defender
        self.att_team = att_team
        self.def_team = def_team

    def is_rebound(self):
        return self.rebound_type not in (
            ReboundType.JUMP_BALL,
            ReboundType.REBOUND_OUT_OF_BOUNDS,
        )

    def is_off_rebound(self):
        return self.rebound_type == ReboundType.OFF_REBOUND

    def is_jumpball(self):
        return self.rebound_type == ReboundType.JUMP_BALL


class FreeThrowEvent(BaseEvent):
    def __init__(
        self,
        comments: list[str],
        clocks: Clocks,
        free_throw_type: FreeThrowType,
        shot_result: ShotResult,
        attacker: int,
        att_team: int,
    ) -> None:
        super().__init__(comments, clocks)
        self.free_throw_type = free_throw_type
        self.shot_result = shot_result
        self.attacker = attacker
        self.att_team = att_team

    def has_scored(self):
        return self.shot_result == ShotResult.SCORED


class InjuryEvent(BaseEvent):
    def __init__(
        self,
        comments: list[str],
        clocks: Clocks,
        injury_type: InjuryType,
        injured_player: int,
        causedby_player: int,
        injured_team: int,
        causedby_team: int,
    ) -> None:
        super().__init__(comments, clocks)
        self.injury_type = injury_type
        self.injured_player = injured_player
        self.causedby_player = causedby_player
        self.injured_team = injured_team
        self.causedby_team = causedby_team


class SubEvent(BaseEvent):
    def __init__(
        self,
        comments: list[str],
        clocks: Clocks,
        sub_type: SubType,
        player_in: int,
        player_out: int,
        team: int,
    ) -> None:
        super().__init__(comments, clocks)
        self.sub_type = sub_type
        self.player_in = player_in
        self.player_out = player_out
        self.team = team


class BreakEvent(BaseEvent):
    def __init__(
        self, comments: list[str], clocks: Clocks, break_type: BreakType, team: int
    ) -> None:
        super().__init__(comments, clocks)
        self.break_type = break_type
        self.team = team


class BBEvent:
    def __init__(
        self,
        team: int,
        type: int,
        result: int,
        variation: int,
        player1: int,
        player2: int,
        gameclock: int,
        realclock: int,
        data: str,
    ) -> None:
        self.team = team
        self.type = type
        self.result = result
        self.variation = variation
        self.player1 = player1
        self.player2 = player2
        self.gameclock = Gameclock(gameclock)
        self.realclock = realclock
        self.data = data
        self.comment = ""
        self.player1obj: Player
        self.player2obj: Player

    def __repr__(self) -> str:
        return """BBEvent
            team: {}
            type: {}
            result: {}
            variation: {}
            player1: {}
            player2: {}
            gameclock: {}
            realclock: {}
            data: {}
            comment: {}
        """.format(
            self.team,
            self.type,
            self.result,
            self.variation,
            self.player1,
            self.player2,
            self.gameclock.clock,
            self.realclock,
            self.data,
            self.comment,
        )

    def to_string(self, p1, p2):
        return """BBEvent
            team: {}
            type: {}
            result: {}
            variation: {}
            player1: {} ({})
            player2: {} ({})
            gameclock: {}
            realclock: {}
            data: {}
            comment: {}""".format(
            self.team,
            self.type,
            self.result,
            self.variation,
            p1,
            self.player1,
            p2,
            self.player2,
            self.gameclock.clock,
            self.realclock,
            self.data,
            self.comment,
        )


def convert(events: list[BBEvent]) -> list[BaseEvent]:
    bb_idx = 0
    base_events: list[BaseEvent] = []
    shotclock = 0

    while bb_idx < len(events):
        event = events[bb_idx]
        bb_idx += 1

        comments = [event.comment]
        clocks = Clocks(event.gameclock.clock, event.realclock, 0)

        etype = event.type
        eprefix = etype // 100
        eresult = event.result
        evar1 = int(event.data[4], 16)
        evar2 = int(event.data[5], 16)
        unknown5 = 0

        if evar1 > 0:
            eprefix = 99

        if eresult > 9:
            if eresult < 13 or eresult > 14:
                unknown5 = 1
            eresult -= 9
        else:
            unknown5 = 0

        if etype >= 100 and etype < 500 and etype not in (210, 211, 212, 213, 214, 215):
            shot_type = ShotType(etype)
            shot_pos = create_shot(
                event.team,
                event.type,
                event.player1obj.id,
                event.player1obj.name,
                event.gameclock.clock,
            )

            result_event = events[bb_idx]
            bb_idx += 1
            comments.append(result_event.comment)

            assert result_event.type == 0, f"This should be a result event"
            unknown2 = 1 if result_event.result == 1 or result_event.result == 4 else 0
            if result_event.result == 0:
                unknown2 = 2
            elif result_event.result == 3 or result_event.result == 6:
                unknown2 = 3
            shot_result = ShotResult(unknown2)

            next_event = events[bb_idx]
            if next_event.type in (504, 507, 508, 509):
                if shot_result == ShotResult.SCORED:
                    shot_result = ShotResult.SCORED_WITH_FOUL
                elif shot_result == ShotResult.MISSED:
                    shot_result = ShotResult.MISSED_WITH_FOUL
                elif shot_result == ShotResult.GOALTEND:
                    pass
                else:
                    assert False, (
                        f"This shouldn't happen result: {str(shot_result)},\n"
                        f"next event: {next_event.type}\n",
                        f"data: {event.data}\n",
                        f"comments: {comments}",
                    )

            defender = 0
            assistant = 0
            if shot_result in (
                ShotResult.SCORED,
                ShotResult.SCORED_WITH_FOUL,
                ShotResult.GOALTEND,
                ShotResult.BLOCKED,
            ):
                if unknown5 == 1:
                    # CHECKME: alters shot, block attempt?
                    defender = event.player2
                elif eresult <= 3 or eresult == 7 or eresult == 6:
                    defender = event.player2
                else:
                    assistant = event.player2

            base_events.append(
                ShotEvent(
                    comments,
                    clocks=clocks,
                    shot_type=shot_type,
                    shot_result=shot_result,
                    attacker=event.player1,
                    defender=defender,
                    assistant=assistant,
                    att_team=event.team,
                    def_team=opponent(event.team),
                    shot_pos=shot_pos,
                )
            )

        elif etype in (210, 211, 212, 213, 214):
            # We can find these ourselves
            pass
        elif etype == 215:
            # Garbage time
            pass

        elif etype == 502 or etype == 503:
            if etype == 502:
                shot_result = ShotResult.SCORED
            elif etype == 503:
                shot_result = ShotResult.MISSED

            base_events.append(
                FreeThrowEvent(
                    comments,
                    clocks,
                    FreeThrowType.REGULAR,
                    shot_result,
                    event.player1,
                    event.team,
                )
            )
        elif etype == 504:
            base_events.append(
                FoulEvent(
                    comments,
                    clocks,
                    FoulType.SHOOTING_FOUL,
                    event.player1,
                    event.player2,
                    event.team,
                    opponent(event.team),
                    flagrant=0,
                )
            )
        elif etype == 505:
            base_events.append(
                FoulEvent(
                    comments,
                    clocks,
                    FoulType.PERSONAL_FOUL,
                    event.player1,
                    event.player2,
                    event.team,
                    opponent(event.team),
                    flagrant=0,
                )
            )
        elif etype == 507:
            assert False, "FIXME: event 507"
        elif etype == 508:
            base_events.append(
                FoulEvent(
                    comments,
                    clocks,
                    FoulType.PERSONAL_FOUL,
                    event.player1,
                    event.player2,
                    event.team,
                    opponent(event.team),
                    flagrant=0,
                )
            )
        elif etype == 509:
            # Upgrade previous foul to flagrant one
            prev_event = base_events[-1]
            assert isinstance(prev_event, FoulEvent)
            prev_event.flagrant = 1
            prev_event.comments.append(*comments)
        elif etype == 510:
            # Upgrade previous foul to flagrant two
            prev_event = base_events[-1]
            assert isinstance(prev_event, FoulEvent)
            prev_event.flagrant = 2
            prev_event.comments.append(*comments)
        elif etype == 706:
            break_type = (
                BreakType.TIMEOUT_30 if event.result == 0 else BreakType.TIMEOUT_60
            )
            base_events.append(BreakEvent(comments, clocks, break_type, event.team))
        elif etype == 801:
            base_events.append(
                InterruptEvent(
                    comments,
                    clocks,
                    InterruptType.THREE_SEC_VIOLATION,
                    event.player1,
                    event.player2,
                    event.team,
                    opponent(event.team),
                )
            )
        elif etype == 802:
            base_events.append(
                InterruptEvent(
                    comments,
                    clocks,
                    InterruptType.BALL_THROWN_OUT,
                    event.player1,
                    event.player2,
                    event.team,
                    opponent(event.team),
                )
            )
        elif etype == 803:
            base_events.append(
                FoulEvent(
                    comments,
                    clocks,
                    FoulType.OFFENSIVE_FOUL,
                    event.player1,
                    event.player2,
                    event.team,
                    opponent(event.team),
                    flagrant=0,
                )
            )
        elif etype == 804:
            base_events.append(
                InterruptEvent(
                    comments,
                    clocks,
                    InterruptType.SHOTCLOCK_VIOLATION,
                    event.player1,
                    event.player2,
                    event.team,
                    opponent(event.team),
                )
            )
        elif etype == 807:
            base_events.append(
                InterruptEvent(
                    comments,
                    clocks,
                    InterruptType.BALL_STOLEN,
                    event.player2,
                    event.player1,
                    event.team,
                    opponent(event.team),
                )
            )
        elif etype == 808:
            base_events.append(
                InterruptEvent(
                    comments,
                    clocks,
                    InterruptType.PASS_INTERCEPTED,
                    event.player2,
                    event.player1,
                    event.team,
                    opponent(event.team),
                )
            )
        elif etype == 809:
            # This assist is added as part of the shot event
            base_events[-1].comments.extend(comments)
        elif etype == 810:
            base_events.append(
                InterruptEvent(
                    comments,
                    clocks,
                    InterruptType.TRAVELLING,
                    event.player1,
                    event.player2,
                    event.team,
                    opponent(event.team),
                )
            )
        elif etype == 812:
            base_events.append(
                InterruptEvent(
                    comments,
                    clocks,
                    InterruptType.LOST_HANDLE,
                    event.player1,
                    event.player2,
                    event.team,
                    opponent(event.team),
                )
            )
        elif etype == 901:
            # Seems to be connected to the previous event
            base_events.append(
                InjuryEvent(
                    comments,
                    clocks,
                    InjuryType.INJURY_OUT,
                    event.player1,
                    event.player2,
                    event.team,
                    opponent(event.team),
                )
            )
        elif etype == 902:
            # Just an information that player will return
            base_events.append(
                InjuryEvent(
                    comments,
                    clocks,
                    InjuryType.INJURY_BACK,
                    event.player1,
                    event.player2,
                    event.team,
                    opponent(event.team),
                )
            )
        elif etype == 903:
            # Looks like a random message, seems to be irrelevant for other events
            base_events.append(
                InjuryEvent(
                    comments,
                    clocks,
                    InjuryType.EXHAUSTED,
                    event.player1,
                    event.player2,
                    event.team,
                    opponent(event.team),
                )
            )
        elif etype == 904:
            assert False, "CHECKME 904"
            base_events.append(
                InjuryEvent(
                    comments,
                    clocks,
                    InjuryType.FAINTED,
                    event.player1,
                    event.player2,
                    event.team,
                    opponent(event.team),
                )
            )
        elif etype == 931:
            if event.result == 7:
                rebound_type = ReboundType.OFF_REBOUND
            elif event.result == 8:
                rebound_type = ReboundType.DEF_REBOUND
            elif event.result == 9:
                rebound_type = ReboundType.DEFAULT_REBOUND
            base_events.append(
                ReboundEvent(
                    comments,
                    clocks,
                    rebound_type,
                    event.player1,
                    event.player2,
                    event.team,
                    opponent(event.team),
                )
            )
        elif etype == 933:
            base_events.append(
                ReboundEvent(
                    comments,
                    clocks,
                    ReboundType.JUMP_BALL,
                    event.player1,
                    event.player2,
                    event.team,
                    opponent(event.team),
                )
            )
        elif etype == 934:
            if event.result == 7:
                pass  # FIXME offensive?
            elif event.result == 8:
                pass  # FIXME defensive?
            base_events.append(
                ReboundEvent(
                    comments,
                    clocks,
                    ReboundType.REBOUND_OUT_OF_BOUNDS,
                    event.player1,
                    event.player2,
                    event.team,
                    opponent(event.team),
                )
            )
        elif etype == 951:
            team = 1 if event.result > 4 else 0
            if event.result == 0 or event.result == 5:
                sub_type = SubType.SUB_PG
            elif event.result == 1 or event.result == 6:
                sub_type = SubType.SUB_SG
            elif event.result == 2 or event.result == 7:
                sub_type = SubType.SUB_SF
            elif event.result == 3 or event.result == 8:
                sub_type = SubType.SUB_PF
            elif event.result == 4 or event.result == 9:
                sub_type = SubType.SUB_C

            base_events.append(
                SubEvent(
                    comments,
                    clocks,
                    sub_type,
                    event.player1 - 1,
                    event.player2 - 1,
                    team,
                )
            )
        elif etype == 952:
            assert event.result == 0 or event.result == 1
            team = event.result
            base_events.append(
                SubEvent(
                    comments,
                    clocks,
                    SubType.POS_SWAP,
                    event.player1 - 1,
                    event.player2 - 1,
                    team,
                )
            )
        elif etype == 961:
            base_events.append(
                BreakEvent(comments, clocks, BreakType.END_OF_QUARTER, -1)
            )
        elif etype == 962:
            base_events.append(BreakEvent(comments, clocks, BreakType.END_OF_GAME, -1))
        elif etype == 963:
            base_events.append(BreakEvent(comments, clocks, BreakType.END_OF_HALF, -1))
        else:
            if etype != -100:
                print(f"Unknown event {etype}")

    return base_events


def create_shot(
    team: int,
    evtype: int,
    pid: int,
    pname: str,
    gameclock: int,
):
    if evtype == 100:
        loc8 = 0
        loc9 = 90
        loc10 = 94
        loc11 = 16
    elif evtype == 101:
        loc8 = 60
        loc9 = 20
        loc10 = 94
        loc11 = 16
    elif evtype == 102:
        loc8 = 0
        loc9 = 60
        loc10 = 94
        loc11 = 16
    elif evtype == 103:
        loc8 = -12
        loc9 = 22
        loc10 = 94
        loc11 = 16
    elif evtype == 104:
        loc8 = 40
        loc9 = 60
        loc10 = 94
        loc11 = 40
    elif evtype == 105:
        loc8 = 40
        loc9 = 60
        loc10 = 130
        loc11 = 60
    elif evtype == 200:
        loc8 = 0
        loc9 = 90
        loc10 = 40
        loc11 = 450
    elif evtype == 201:
        loc8 = 50
        loc9 = 20
        loc10 = 45
        loc11 = 30
    elif evtype == 202:
        loc8 = -10
        loc9 = 60
        loc10 = 45
        loc11 = 40
    elif evtype == 203:
        loc8 = -15
        loc9 = 4
        loc10 = 35
        loc11 = 50
    elif evtype == 204:
        loc8 = 70
        loc9 = 20
        loc10 = 55
        loc11 = 35
    elif evtype == 400:
        loc8 = 0
        loc9 = 90
        loc10 = 8
        loc11 = 40
    elif evtype == 401:
        loc8 = 0
        loc9 = 90
        loc10 = 8
        loc11 = 24
    elif evtype == 402:
        loc8 = 0
        loc9 = 90
        loc10 = 9
        loc11 = 42
    else:
        loc8 = 0
        loc9 = 90
        loc10 = 9
        loc11 = 40

    loc16 = pid >> gameclock % 3
    if loc16 < 0:
        loc16 *= -1

    loc12 = (loc16 - gameclock) % loc11 + loc10
    loc13 = float((loc16 + gameclock) % loc9 + loc8)
    if gameclock % 2 == 1:
        loc13 = 180 - loc13

    loc13 = math.radians(loc13)
    if team == 0:
        loc13 = -loc13
        x_coord = int(math.sin(loc13) * loc12 + 347)
        y_coord = int(math.cos(loc13) * loc12 + 96)
    else:
        x_coord = int(math.sin(loc13) * loc12 + 21)
        y_coord = int(math.cos(loc13) * loc12 + 96)

    y_coord = max(min(y_coord, 188), 4)
    x_coord = max(min(x_coord, 364), 4)
    if evtype // 100 == 2:
        y_coord = max(min(y_coord, 176), 14)

    return ShotPos(x_coord, y_coord)


if __name__ == "__main__":
    from shot_chart import ShotChart
    import sys

    sc = ShotChart()

    for i in range(2880):
        shot = create_shot(0, int(sys.argv[1]), 51805514, "", i + 1)
        sc.add_made(shot.x, shot.y)

    sc.save(f"shot_{sys.argv[1]}.png")
