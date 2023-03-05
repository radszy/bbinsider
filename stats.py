from enum import IntEnum


class Statistic(IntEnum):
    Points = 0
    FieldGoalsAtt = 1
    FieldGoalsMade = 2
    ThreePointsAtt = 3
    ThreePointsMade = 4
    FreeThrowsAtt = 5
    FreeThrowsMade = 6
    OffRebounds = 7
    DefRebounds = 8
    Assists = 9
    Turnovers = 10
    Steals = 11
    Blocks = 12
    Fouls = 13
    Seconds = 14
    PlusMinus = 15
    Dunks = 16
    PointsInThePaint = 17
    SecsPG = 18
    SecsSG = 19
    SecsSF = 20
    SecsPF = 21
    SecsC = 22
    PlayerStats = 23
    FastBreakPoints = 23
    SecondChancePoints = 24
    BenchPoints = 25
    PointsOffTurnovers = 26
    BiggestLead = 27
    TimeOfPossession = 28
    Possessions = 29
    Timeouts30 = 30
    Timeouts60 = 31
    TeamStats = 32


class StatSheet:
    def __init__(self) -> None:
        self.sheet = [0] * Statistic.TeamStats

    def __repr__(self) -> str:
        return f"""Stats
    MIN: {self.minutes()}
    PTS: {self.sheet[Statistic.Points]}
    FG:  {self.sheet[Statistic.FieldGoalsMade]} / {self.sheet[Statistic.FieldGoalsAtt]}
    TP:  {self.sheet[Statistic.ThreePointsMade]} / {self.sheet[Statistic.ThreePointsAtt]}
    FT:  {self.sheet[Statistic.FreeThrowsMade]} / {self.sheet[Statistic.FreeThrowsAtt]}
    +/-: {self.sheet[Statistic.PlusMinus]}
    OR:  {self.sheet[Statistic.OffRebounds]}
    DR:  {self.sheet[Statistic.DefRebounds]}
    TR:  {self.sheet[Statistic.OffRebounds] + self.sheet[Statistic.DefRebounds]}
    AST: {self.sheet[Statistic.Assists]}
    TO:  {self.sheet[Statistic.Turnovers]}
    STL: {self.sheet[Statistic.Steals]}
    BLK: {self.sheet[Statistic.Blocks]}
    PF:  {self.sheet[Statistic.Fouls]}
        """

    def row(self):
        return [
            f"{self.minutes()}",
            f"{self.sheet[Statistic.Points]}",
            f"{self.sheet[Statistic.FieldGoalsMade]}/{self.sheet[Statistic.FieldGoalsAtt]}",
            f"{self.sheet[Statistic.ThreePointsMade]}/{self.sheet[Statistic.ThreePointsAtt]}",
            f"{self.sheet[Statistic.FreeThrowsMade]}/{self.sheet[Statistic.FreeThrowsAtt]}",
            f"{self.sheet[Statistic.PlusMinus]}",
            f"{self.sheet[Statistic.OffRebounds]}",
            f"{self.sheet[Statistic.DefRebounds]}",
            f"{self.sheet[Statistic.OffRebounds] + self.sheet[Statistic.DefRebounds]}",
            f"{self.sheet[Statistic.Assists]}",
            f"{self.sheet[Statistic.Turnovers]}",
            f"{self.sheet[Statistic.Steals]}",
            f"{self.sheet[Statistic.Blocks]}",
            f"{self.sheet[Statistic.Fouls]}",
        ]

    def minutes(self):
        return (
            round(self.sheet[Statistic.SecsPG] / 60)
            + round(self.sheet[Statistic.SecsSG] / 60)
            + round(self.sheet[Statistic.SecsSF] / 60)
            + round(self.sheet[Statistic.SecsPF] / 60)
            + round(self.sheet[Statistic.SecsC] / 60)
        )


class Stats:
    def __init__(self) -> None:
        self.full = StatSheet()
        self.qtr: list[StatSheet] = []

    def add(self, stat: Statistic, val: int):
        self.full.sheet[stat] += val
        self.qtr[-1].sheet[stat] += val

    def new_qtr_sheet(self):
        self.qtr.append(StatSheet())
