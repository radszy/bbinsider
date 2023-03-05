from stats import Stats, Statistic


class Player:
    def __init__(self, name="") -> None:
        self.id = 0
        self.name = name
        self.stats = Stats()
        self.starter = False

    def get_shortened_name(self) -> str:
        full_name = self.name.split(" ")
        return full_name[0][0] + ". " + " ".join(full_name[1:])

    def __repr__(self) -> str:
        return f"{self.id}: {self.name}"

    def add_stats(self, stat: Statistic, val: int):
        self.stats.add(stat, val)

    def secs_total(self):
        return (
            self.stats.full.sheet[Statistic.SecsPG]
            + self.stats.full.sheet[Statistic.SecsSG]
            + self.stats.full.sheet[Statistic.SecsSF]
            + self.stats.full.sheet[Statistic.SecsPF]
            + self.stats.full.sheet[Statistic.SecsC]
        )
