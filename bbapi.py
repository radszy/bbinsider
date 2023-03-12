from typing import Set
import requests
import xml.etree.ElementTree as xml
from pprint import pprint
from team import Team
from player import Player
from stats import *
from os.path import exists


class Network:
    def __init__(self):
        self.cookies = None

    def first_get(self, url, parameters=None):
        r = requests.get(url, cookies=self.cookies, params=parameters)
        self.cookies = r.cookies
        return r.text

    def get(self, url, parameters=None):
        r = requests.get(url, cookies=self.cookies, params=parameters)
        return r.text


class BBApi:
    def __init__(self, login=None, password=None):
        if login is None or password is None:
            return

        self.login = login
        self.password = password
        self.logged_in = False
        self.network = Network()

        p = {"login": self.login, "code": self.password}
        data = self.network.first_get("http://bbapi.buzzerbeater.com/login.aspx", p)

        root = xml.fromstring(data)
        if root.tag == "bbapi":
            if root.attrib["version"] != "1":
                print("Error: Invalid BBApi Version!")

        for child in root:
            if child.tag == "loggedIn":
                self.logged_in = True
            elif child.tag == "error":
                print("Error:", child.attrib["message"])

    def arena(self, teamid=0):
        p = {"teamid": teamid}
        data = self.network.get("http://bbapi.buzzerbeater.com/arena.aspx", p)

        root = xml.fromstring(data)
        arena = root.find("arena")
        name = arena.find("name")

        arena_name = name.text
        arena_seats, arena_expansion = {}, {}

        seats = arena.find("seats")
        for seat in seats:
            arena_seats[seat.tag] = (
                int(seat.text),
                {
                    "price": int(seat.attrib["price"]),
                    "nextPrice": int(seat.attrib["nextPrice"]),
                },
            )

        seats = arena.find("expansion")
        if seats is not None:
            arena_expansion["daysLeft"] = int(seats.attrib["daysLeft"])
            for seat in seats:
                arena_expansion[seat.tag] = int(seat.text)

        return arena_name, arena_seats, arena_expansion

    def get_xml_boxscore(self, matchid) -> str:

        path = f"matches/boxscore_{matchid}.xml"

        if exists(path):
            with open(path, mode="r", encoding='utf-8') as f:
                return f.read()
        else:
            p = {"matchid": matchid}
            text = self.network.get("http://bbapi.buzzerbeater.com/boxscore.aspx", p)

            with open(path, mode="w", encoding='utf-8') as f:
                f.write(text)

            return text

    def get_xml_standings(self, leagueid: int, season: int) -> str:

        path = f"matches/standings_{leagueid}_{season}.xml"

        if exists(path):
            with open(path, mode="r", encoding='utf-8') as f:
                return f.read()
        else:
            p = {"leagueid": str(leagueid), "season": str(season)}
            text = self.network.get("http://bbapi.buzzerbeater.com/standings.aspx", p)

            with open(path, mode="w", encoding='utf-8') as f:
                f.write(text)

            return text

    def get_xml_schedule(self, teamid, season) -> str:

        path = f"matches/schedule_{teamid}_{season}.xml"

        if exists(path):
            with open(path, mode="r", encoding='utf-8') as f:
                return f.read()
        else:
            p = {"teamid": teamid, "season": season}
            text = self.network.get("http://bbapi.buzzerbeater.com/schedule.aspx", p)

            with open(path, mode="w", encoding='utf-8') as f:
                f.write(text)

            return text

    def player(self, playerid) -> str:
        p = {"playerid": playerid}
        data = self.network.get("http://bbapi.buzzerbeater.com/player.aspx", p)

        root = xml.fromstring(data)
        position = root.find("./player/bestPosition")

        return position.text

    def strategy(self, matchid=0):
        data = self.get_xml_boxscore(matchid)

        root = xml.fromstring(data)
        away_off = root.find("./match/awayTeam/offStrategy").text
        away_def = root.find("./match/awayTeam/defStrategy").text
        home_off = root.find("./match/homeTeam/offStrategy").text
        home_def = root.find("./match/homeTeam/defStrategy").text

        return away_off, away_def, home_off, home_def

    def boxscore(self, matchid=0) -> list[Team]:
        data = self.get_xml_boxscore(matchid)

        root = xml.fromstring(data)
        away = root.find("./match/awayTeam")
        home = root.find("./match/homeTeam")
        xml_teams = [away, home]
        bb_teams = [Team(), Team()]

        for index, xml_team in enumerate(xml_teams):
            bb_team = bb_teams[index]

            assert isinstance(xml_team, xml.Element), ""
            bb_team.id = int(xml_team.attrib["id"])
            bb_team.name = xml_team.find("./teamName").text

            bb_team.off_strategy = xml_team.find("./offStrategy").text
            bb_team.def_strategy = xml_team.find("./defStrategy").text

            quarters = xml_team.find("./score").attrib["partials"].split(",")
            for i in range(len(quarters)):
                bb_team.push_stat_sheet()
            for num, pts in enumerate(quarters):
                bb_team.stats.qtr[num].sheet[Statistic.Points] = pts

            totals = xml_team.find("./boxscore/teamTotals")

            def add_team_stat(stat: Statistic, val: int):
                bb_team.stats.full.sheet[stat] = val

            def team_stat(s: str) -> int:
                return int(totals.find(s).text)

            add_team_stat(Statistic.Points, team_stat("./pts"))
            add_team_stat(Statistic.FieldGoalsAtt, team_stat("./fga"))
            add_team_stat(Statistic.FieldGoalsMade, team_stat("./fgm"))
            add_team_stat(Statistic.ThreePointsAtt, team_stat("./tpa"))
            add_team_stat(Statistic.ThreePointsMade, team_stat("./tpm"))
            add_team_stat(Statistic.FreeThrowsAtt, team_stat("./fta"))
            add_team_stat(Statistic.FreeThrowsMade, team_stat("./ftm"))
            add_team_stat(Statistic.OffRebounds, team_stat("./oreb"))
            add_team_stat(
                Statistic.DefRebounds, team_stat("./reb") - team_stat("./oreb")
            )
            add_team_stat(Statistic.Assists, team_stat("./ast"))
            add_team_stat(Statistic.Turnovers, team_stat("./to"))
            add_team_stat(Statistic.Steals, team_stat("./stl"))
            add_team_stat(Statistic.Blocks, team_stat("./blk"))
            add_team_stat(Statistic.Fouls, team_stat("./pf"))

            players = xml_team.findall("./boxscore/player")
            for xml_player in players:
                bb_player = Player()

                assert isinstance(xml_player, xml.Element), ""
                bb_player.id = int(xml_player.attrib["id"])
                bb_player.name = f"{xml_player.find('./firstName').text} {xml_player.find('./lastName').text}"

                perf = xml_player.find("./performance")
                mins = xml_player.find("./minutes")

                def add_stat(s: Statistic, val: int):
                    bb_player.stats.full.sheet[s] = val

                def stat(s: str) -> int:
                    return int(perf.find(s).text)

                def minutes(s: str) -> int:
                    return int(mins.find(s).text)

                add_stat(Statistic.SecsPG, minutes("./PG") * 60)
                add_stat(Statistic.SecsSG, minutes("./SG") * 60)
                add_stat(Statistic.SecsSF, minutes("./SF") * 60)
                add_stat(Statistic.SecsPF, minutes("./PF") * 60)
                add_stat(Statistic.SecsC, minutes("./C") * 60)

                add_stat(Statistic.Points, stat("./pts"))
                add_stat(Statistic.FieldGoalsAtt, stat("./fga"))
                add_stat(Statistic.FieldGoalsMade, stat("./fgm"))
                add_stat(Statistic.ThreePointsAtt, stat("./tpa"))
                add_stat(Statistic.ThreePointsMade, stat("./tpm"))
                add_stat(Statistic.FreeThrowsAtt, stat("./fta"))
                add_stat(Statistic.FreeThrowsMade, stat("./ftm"))
                add_stat(Statistic.OffRebounds, stat("./oreb"))
                add_stat(
                    Statistic.DefRebounds,
                    (stat("./reb") - stat("./oreb")),
                )
                add_stat(Statistic.Assists, stat("./ast"))
                add_stat(Statistic.Turnovers, stat("./to"))
                add_stat(Statistic.Steals, stat("./stl"))
                add_stat(Statistic.Blocks, stat("./blk"))
                add_stat(Statistic.Fouls, stat("./pf"))
                bb_team.players.append(bb_player)

        return bb_teams

    def standings(self, league_id: int, season: int):
        data = self.get_xml_standings(league_id, season)

        root = xml.fromstring(data)
        teams = root.findall("./standings/regularSeason/conference/team")
        team_ids = [team.attrib["id"] for team in teams]

        return team_ids

    def schedule(self, team_id, season):
        data = self.get_xml_schedule(team_id, season)

        root = xml.fromstring(data)
        matches = root.findall("./schedule/match")

        match_ids = [
            match.attrib["id"]
            for match in matches
            if match.attrib["type"].startswith("league")
        ]

        return match_ids


def prefetch_data(
    username: str, password: str, leagueid_: int, season_from: int, season_to: int
):
    api = BBApi(username, password)

    unique_ids = set[str]()

    leagueids = [
        1,  # USA
        86,  # Argentina,
        107,  # Brasil
        128,  # Canada
        149,  # China
        170,  # Turkiye
        191,  # Espana
        212,  # Deutschland
        254,  # Italia
        275,  # France
        296,  # Hellas
        893,  # Belgium
        978,  # England
        999,  # Isreal
        1020,  # Nederland
        1062,  # Portugal
        1083,  # Rossiya
        1104,  # Lietuva
        1277,  # Srbija
        2083,  # Polska
    ]

    # [ 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 29, 58]
    season = 59

    for leagueid in leagueids:
        team_ids = api.standings(leagueid, season)
        print(f"Season {season}: teams: {len(team_ids)}")
        for team_id in team_ids:
            match_ids = api.schedule(team_id, season)
            unique_ids.update(match_ids)
            print(f"LeagueID: {leagueid}, Season {season}: matches: {len(match_ids)}")

    with open("uids-various.txt", "w", encoding='utf-8') as f:
        for index, uid in enumerate(unique_ids):
            print(f"Fetch {uid} ({index+1}/{len(unique_ids)})")
            api.boxscore(uid)

            f.write(str(uid) + "\n")

    print(unique_ids)
    print(len(unique_ids))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--leagueid", type=int, required=True)
    parser.add_argument("--season-from", type=int, required=True)
    parser.add_argument("--season-to", type=int, required=True)
    args = parser.parse_args()

    prefetch_data(
        args.username, args.password, args.leagueid, args.season_from, args.season_to
    )
