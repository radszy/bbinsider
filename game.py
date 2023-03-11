from typing import Dict

from bbapi import BBApi
from team import Team
from comments import Comments
from event import *
from event_types import *
from stats import *
import json


class Extension:
    def __init__(self):
        pass

    def on_shot_event(self, game, event):
        pass

    def on_interrupt_event(self, game, event):
        pass

    def on_foul_event(self, game, event):
        pass

    def on_rebound_event(self, game, event):
        pass

    def on_free_throw_event(self, game, event):
        pass

    def on_injury_event(self, game, event):
        pass

    def on_sub_event(self, game, event):
        pass

    def on_break_event(self, game, event):
        pass


class Game:
    def __init__(
        self,
        matchid: str,
        events: list[BBEvent],
        ht: Team,
        at: Team,
        args,
        extensions: list[Extension],
    ) -> None:
        self.matchid = matchid
        self.events = events
        self.teams = [ht, at]
        self.comments = Comments()
        self.gameclock = 0
        self.shotclock = 24
        self.poss = 0
        self.quarter = 1
        self.quater_poss = [0, 0, 0, 0]
        self.args = args
        self.event_index = 0
        self.baseevents: list[BaseEvent] = []
        self.extensions = extensions

    def update_clocks(self, shot: int, game: int):
        self.shotclock = min(shot, Gameclock(game).till_break())
        self.gameclock = game

        if self.args.print_events:
            print(f"Set shotclock: {self.shotclock}")

    def patch_clock(self, bev, prev_bev):
        clock_delta = bev.gameclock - prev_bev.gameclock
        bev.shotclock = max(0, self.shotclock - clock_delta)

        if self.args.print_events:
            print(f"Remaining shotclock: {bev.shotclock}")

    def update_possession(self, team: int):
        self.poss = team
        if self.args.print_events:
            print(f"Next possession: {self.teams[self.poss].name}")

    def gameclock_normalized(self, gameclock: int):
        # TODO: translate gameclock at first parse
        clock = gameclock
        if self.quarter > 4:
            clock -= (self.quarter - 4) * 420
        return clock

    def play(self) -> None:
        idx = 0
        for event in self.events:
            comment = self.comments.get_comment(event, self.teams)
            event.comment = comment
            idx += 1

        for team in self.teams:
            team.push_stat_sheet()

        self.baseevents = convert(self.events)
        prev_bev = BaseEvent([], Clocks(-1, -1, -1))

        for idx, bev in enumerate(self.baseevents):
            if self.args.print_events:
                print()
                print("###", bev.gameclock, bev.comments)

            self.event_index = idx
            gameclock = self.gameclock_normalized(bev.gameclock)

            if isinstance(bev, ShotEvent):
                att_team = self.teams[bev.att_team]
                def_team = self.teams[bev.def_team]

                if bev.is_3pt():
                    pts = 3

                    if not (bev.is_fouled() and bev.has_missed()):
                        att_team.add_stats(Statistic.ThreePointsAtt, 1, bev.attacker)

                    if bev.has_scored():
                        att_team.add_stats(Statistic.ThreePointsMade, 1, bev.attacker)
                else:
                    pts = 2

                if not (bev.is_fouled() and bev.has_missed()):
                    att_team.add_stats(Statistic.FieldGoalsAtt, 1, bev.attacker)

                self.patch_clock(bev, prev_bev)

                if bev.has_scored():
                    att_team.add_stats(Statistic.FieldGoalsMade, 1, bev.attacker)
                    att_team.add_stats(Statistic.Points, pts, bev.attacker)
                    for player in att_team.active:
                        player.add_stats(Statistic.PlusMinus, pts)
                    for player in def_team.active:
                        player.add_stats(Statistic.PlusMinus, -pts)
                    att_team.shot_chart.add_made(bev.shot_pos.x, bev.shot_pos.y)
                    if not bev.is_fouled():
                        self.update_clocks(24, gameclock)
                        self.update_possession(bev.def_team)
                else:
                    att_team.shot_chart.add_miss(bev.shot_pos.x, bev.shot_pos.y)

                if bev.is_blocked():
                    def_team.add_stats(Statistic.Blocks, 1, bev.defender)

                if bev.is_assisted():
                    att_team.add_stats(Statistic.Assists, 1, bev.assistant)

                for ext in self.extensions:
                    ext.on_shot_event(self, bev)

            elif isinstance(bev, FreeThrowEvent):
                att_team = self.teams[bev.att_team]
                def_team = self.teams[opponent(bev.att_team)]

                att_team.add_stats(Statistic.FreeThrowsAtt, 1, bev.attacker)
                if bev.has_scored():
                    att_team.add_stats(Statistic.FreeThrowsMade, 1, bev.attacker)
                    att_team.add_stats(Statistic.Points, 1, bev.attacker)

                    for player in att_team.active:
                        player.add_stats(Statistic.PlusMinus, 1)
                    for player in def_team.active:
                        player.add_stats(Statistic.PlusMinus, -1)

                for ext in self.extensions:
                    ext.on_free_throw_event(self, bev)

            elif isinstance(bev, ReboundEvent):
                att_team = self.teams[bev.att_team]
                def_team = self.teams[bev.def_team]

                if not bev.is_jumpball():
                    self.patch_clock(bev, prev_bev)
                    self.update_clocks(24, gameclock)

                if bev.is_rebound():
                    if bev.is_off_rebound():
                        att_team.add_stats(Statistic.OffRebounds, 1, bev.attacker)
                    else:
                        def_team.add_stats(Statistic.DefRebounds, 1, bev.attacker)
                        self.update_possession(bev.def_team)
                elif bev.is_jumpball():
                    bev.shotclock = 0
                    self.update_clocks(24, gameclock)
                    self.update_possession(bev.att_team)

                    # Who will start each quarter
                    if idx == 0:
                        self.quater_poss = [
                            bev.att_team,
                            bev.def_team,
                            bev.def_team,
                            bev.att_team,
                        ]

                for ext in self.extensions:
                    ext.on_rebound_event(self, bev)

            elif isinstance(bev, InterruptEvent):
                att_team = self.teams[bev.att_team]
                def_team = self.teams[bev.def_team]

                self.patch_clock(bev, prev_bev)

                if bev.interrupt_type in (
                    InterruptType.BALL_THROWN_OUT,
                    InterruptType.LOST_HANDLE,
                    InterruptType.THREE_SEC_VIOLATION,
                    InterruptType.TRAVELLING,
                ):
                    att_team.add_stats(Statistic.Turnovers, 1, bev.attacker)
                    self.update_clocks(24, gameclock)
                    self.update_possession(bev.def_team)
                elif bev.interrupt_type in (
                    InterruptType.PASS_INTERCEPTED,
                    InterruptType.BALL_STOLEN,
                ):
                    att_team.add_stats(Statistic.Turnovers, 1, bev.attacker)
                    def_team.add_stats(Statistic.Steals, 1, bev.defender)
                    self.update_clocks(24, gameclock)
                    self.update_possession(bev.def_team)
                elif bev.interrupt_type in (InterruptType.SHOTCLOCK_VIOLATION,):
                    att_team.add_stats(Statistic.Turnovers, 1)
                    self.update_clocks(24, gameclock)
                    self.update_possession(bev.def_team)

                for ext in self.extensions:
                    ext.on_interrupt_event(self, bev)

            elif isinstance(bev, FoulEvent):
                att_team = self.teams[bev.att_team]
                def_team = self.teams[bev.def_team]

                self.patch_clock(bev, prev_bev)

                if bev.foul_type == FoulType.OFFENSIVE_FOUL:
                    att_team.add_stats(Statistic.Turnovers, 1, bev.attacker)
                    att_team.add_stats(Statistic.Fouls, 1, bev.attacker)
                    self.update_clocks(24, gameclock)
                    self.update_possession(bev.def_team)
                elif bev.foul_type == FoulType.PERSONAL_FOUL:
                    if def_team.stats.qtr[self.quarter - 1].sheet[Statistic.Fouls] < 4:
                        if bev.shotclock < 14:
                            self.update_clocks(14, gameclock)
                        else:
                            self.update_clocks(bev.shotclock, gameclock)
                    else:
                        self.update_clocks(24, gameclock)
                elif bev.foul_type == FoulType.SHOOTING_FOUL:
                    self.update_clocks(24, gameclock)

                if bev.foul_type in (
                    FoulType.PERSONAL_FOUL,
                    FoulType.SHOOTING_FOUL,
                ):
                    def_team.add_stats(Statistic.Fouls, 1, bev.defender)

                for ext in self.extensions:
                    ext.on_foul_event(self, bev)

            elif isinstance(bev, InjuryEvent):
                self.patch_clock(bev, prev_bev)

                for ext in self.extensions:
                    ext.on_injury_event(self, bev)

            elif isinstance(bev, SubEvent):
                team = self.teams[bev.team]
                team.update_minutes(gameclock)

                self.patch_clock(bev, prev_bev)

                if bev.sub_type != SubType.POS_SWAP:
                    team.make_sub(bev.sub_type, bev.player_out, bev.player_in)
                else:
                    team.make_swap(bev.player_in, bev.player_out)

                for ext in self.extensions:
                    ext.on_sub_event(self, bev)

            elif isinstance(bev, BreakEvent):
                if bev.break_type == BreakType.END_OF_QUARTER:
                    self.update_clocks(24, bev.gameclock)

                    if (
                        self.quarter < 4
                        or self.teams[0].points() == self.teams[1].points()
                    ):
                        self.teams[0].push_stat_sheet()
                        self.teams[1].push_stat_sheet()
                        self.quarter += 1

                    if self.quarter <= 4:
                        self.update_possession(self.quater_poss[self.quarter - 1])
                elif bev.break_type == BreakType.END_OF_HALF:
                    pass
                elif bev.break_type == BreakType.END_OF_GAME:
                    for team in self.teams:
                        team.update_minutes(gameclock)
                elif bev.break_type == BreakType.TIMEOUT_30:
                    self.teams[bev.team].add_stats(Statistic.Timeouts30, 1)
                elif bev.break_type == BreakType.TIMEOUT_60:
                    self.teams[bev.team].add_stats(Statistic.Timeouts60, 1)

                for ext in self.extensions:
                    ext.on_break_event(self, bev)

            if (
                idx + 1 < len(self.baseevents)
                and (
                    bev.gameclock != self.baseevents[idx + 1].gameclock
                    or isinstance(bev, ReboundEvent)
                )
            ) or bev.gameclock == -1:
                prev_bev = bev

        for team in reversed(self.teams):
            if self.args.print_stats:
                team.print_stats()
            if self.args.save_charts:
                team.shot_chart.save(f"matches/{self.matchid}-{team.short}.png")

        # Verify data against BBApi boxscore
        if self.args.username and self.args.password and self.args.verify:
            bbapi = BBApi(self.args.username, self.args.password)
            bbteams = bbapi.boxscore(matchid=self.matchid)
            assert bbteams[0] == self.teams[1]
            assert bbteams[1] == self.teams[0]

    def save(self, filename):
        teams = []
        for tid, team in enumerate(self.teams):
            players = []

            for pid, player in enumerate(team.players):
                stats = {}
                for qtr, stat in enumerate(player.stats.qtr, start=1):
                    stats[f"q{qtr}"] = stat.player_stats()
                stats["total"] = player.stats.full.player_stats()

                p = {
                    "id": player.id,
                    "name": player.name,
                    "starter": player.starter,
                    "stats": stats,
                }
                players.append(p)

            stats = {}
            for qtr, stat in enumerate(team.stats.qtr, start=1):
                stats[f"q{qtr}"] = stat.team_stats()
            stats["total"] = team.stats.full.team_stats()

            t = {"id": team.id, "name": team.name, "players": players, "stats": stats}
            teams.append(t)

        events = []
        for event in self.baseevents:
            events.append(event.to_json())

        game = {
            "teamHome": teams[0],
            "teamAway": teams[1],
            "events": events,
        }

        with open(filename, "w") as f:
            json.dump(game, f, indent=4, ensure_ascii=False)


class Possessions(Extension):
    def __init__(self) -> None:
        super().__init__()
        self.possessions: list[list[int]] = [[], []]

    def add_possession(self, game: Game, team, shotclock):
        assert team == 0 or team == 1
        assert shotclock >= 0 and shotclock <= 24, f"Got shotclock {shotclock}!"
        self.possessions[team].append(shotclock)

        if game.args.print_events:
            print(
                f"nPossessions: {len(self.possessions[1])}:{len(self.possessions[0])} (+1 {game.teams[team].name})"
            )

    def on_shot_event(self, game, event: ShotEvent):
        # For other shot results the def teams needs to rebound ball first
        if event.shot_result in (ShotResult.SCORED, ShotResult.GOALTEND):
            self.add_possession(game, event.att_team, event.shotclock)

    def on_interrupt_event(self, game, event: InterruptEvent):
        self.add_possession(game, event.att_team, event.shotclock)

    def on_foul_event(self, game, event: FoulEvent):
        if event.foul_type == FoulType.OFFENSIVE_FOUL:
            self.add_possession(game, event.att_team, event.shotclock)
        # elif (
        #     event.foul_type == FoulType.PERSONAL_FOUL
        #     and game.teams[event.def_team]
        #     .stats.qtr[game.quarter - 1]
        #     .sheet[Statistic.Fouls]
        #     > 4
        # ):
        #     self.add_possession(game, event.att_team, event.shotclock)

    def on_rebound_event(self, game: Game, event: ReboundEvent):
        # Defensive team gained possession by rebounding ball
        # game.poss is already reflecting possession change
        if game.poss == event.def_team:
            self.add_possession(game, event.att_team, event.shotclock)

    def on_free_throw_event(self, game: Game, event: FreeThrowEvent):
        pass

    def on_injury_event(self, game: Game, event: InjuryEvent):
        pass

    def on_sub_event(self, game: Game, event: SubEvent):
        pass

    def on_break_event(self, game: Game, event: BreakEvent):
        if event.break_type == BreakType.END_OF_QUARTER:
            prev_bev = game.baseevents[game.event_index - 1]
            if isinstance(prev_bev, ShotEvent) and prev_bev.shot_result not in (
                ShotResult.SCORED,
                ShotResult.GOALTEND,
            ):
                self.add_possession(game, prev_bev.att_team, event.shotclock)
            elif isinstance(prev_bev, FreeThrowEvent):
                self.add_possession(game, prev_bev.att_team, event.shotclock)


class ShotTypes(Extension):
    def __init__(self) -> None:
        super().__init__()
        self.shot_types: list[Dict[ShotType, list[int]]] = [{}, {}]

    def table(self, game: Game) -> str:
        from tabulate import tabulate

        headers = [
            "Type",
            "Missed",
            "Scored",
            "Goaltended",
            "Blocked",
            "Missed Fouled",
            "Scored Fouled",
        ]
        tables: list[list[list[str]]] = [[], []]
        for index, team in enumerate(self.shot_types):
            for shot_type, results in team.items():
                tables[index].append(
                    [
                        str(shot_type),
                        str(results[0]),
                        str(results[1]),
                        str(results[2]),
                        str(results[3]),
                        str(results[4]),
                        str(results[5]),
                    ]
                )
        return f"{game.teams[0].name}:\n{tabulate(tables[0], headers=headers)}\n\n{game.teams[1].name}:\n{tabulate(tables[1], headers=headers)}"

    def on_shot_event(self, game: Game, event: ShotEvent):
        result = int(event.shot_result)

        shot_type = self.shot_types[event.att_team].get(
            str(event.shot_type), [0, 0, 0, 0, 0, 0]
        )
        shot_type[result] += 1
        self.shot_types[event.att_team][str(event.shot_type)] = shot_type

    def on_interrupt_event(self, game: Game, event: InterruptEvent):
        pass

    def on_foul_event(self, game: Game, event: FoulEvent):
        pass

    def on_rebound_event(self, game: Game, event: ReboundEvent):
        pass

    def on_free_throw_event(self, game: Game, event: FreeThrowEvent):
        pass

    def on_injury_event(self, game: Game, event: InjuryEvent):
        pass

    def on_sub_event(self, game: Game, event: SubEvent):
        pass

    def on_break_event(self, game: Game, event: BreakEvent):
        pass
