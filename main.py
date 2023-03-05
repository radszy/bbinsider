#!/usr/bin/env python3

import argparse
import requests
import xml.etree.ElementTree as XML
from pprint import pprint as pp
from typing import TextIO

from game import *
from event import *
from player import Player
from team import Team
from bbapi import *


def parse_report(report: str, ht: Team, at: Team) -> list[BBEvent]:
    events = []

    # Read players
    i = 0
    index = 0
    while i < 96:
        id = int(report[i : i + 8])
        i += 8

        if index < len(ht.players):
            ht.players[index].id = id
        index += 1

    index = 0
    while i < 192:
        id = int(report[i : i + 8])
        i += 8

        if index < len(at.players):
            at.players[index].id = id
        index += 1

    # Read starters
    pos = 0
    while i < 197:
        id = int(report[i], 16) - 1
        print("starter: ", id, f"{ht.players[id]}")
        ht.set_starter(id, pos)
        i += 1
        pos += 1
    pos = 0
    while i < 202:
        id = int(report[i], 16) - 1
        print("starter: ", id, f"{at.players[id]}")
        at.set_starter(id, pos)
        i += 1
        pos += 1

    # Read events
    while i < len(report):
        s = report[i : i + 17]

        e = BBEvent(
            team=int(s[0]),
            type=int(s[1:4]),
            result=int(s[4], 16),
            variation=int(s[6], 16),
            player1=int(s[7], 16),
            player2=int(s[8], 16),
            gameclock=int(s[9:13]),
            realclock=int(s[13:17]),
            data=s[1:9],
        )

        sub_type = e.type // 100
        if int(s[5]) > 0:
            e.type = -100
            e.result = 0
            sub_type = 99

        events.append(e)

        if sub_type in (1, 2, 4):
            n = BBEvent(
                team=e.team,
                type=0,
                variation=0,
                result=e.result,
                player1=e.player1,
                player2=e.player2,
                gameclock=e.gameclock.clock,
                realclock=e.realclock + 2,
                data="",
            )

            if n.result > 9:
                n.result -= 9
            if e.result > 9:
                n.data = "000{}0000".format(e.result - 9)
            else:
                n.data = "000{}0000".format(e.result)

            events.append(n)

        i += 17

    return events


def parse_xml(text: str) -> tuple[list[BBEvent], Team, Team]:
    tree = XML.ElementTree(XML.fromstring(text))
    root = tree.getroot()

    ht = Team()
    at = Team()
    report = ""

    for child in root:
        tag = child.tag
        if tag == "HomeTeam":
            for team in child:
                if team.tag == "ID":
                    assert team.text, "Missing team ID"
                    ht.id = int(team.text)
                elif team.tag == "Name":
                    assert team.text, "Missing team name"
                    ht.name = team.text
                elif team.tag == "ShortName":
                    assert team.text, "Missing team short name"
                    ht.short = team.text
        elif tag == "AwayTeam":
            for team in child:
                if team.tag == "ID":
                    assert team.text
                    at.id = int(team.text)
                elif team.tag == "Name":
                    assert team.text
                    at.name = team.text
                elif team.tag == "ShortName":
                    assert team.text
                    at.short = team.text
        elif tag.startswith("HPlayer") and not tag.startswith("HPlayerNick"):
            assert child.text, "Missing HPlayer string"
            p = Player()
            p.name = child.text
            ht.players.append(p)
        elif tag.startswith("APlayer") and not tag.startswith("APlayerNick"):
            assert child.text, "Missing APlayer string"
            p = Player()
            p.name = child.text
            at.players.append(p)
        elif tag == "ReportString":
            assert child.text, "Missing report string"
            report = child.text.strip()

    # Fill upto 12 players with empty objects, as the events events apparently reference these.
    while len(ht.players) < 12:
        ht.players.append(Player("Lucky Fan"))
    while len(at.players) < 12:
        at.players.append(Player("Lucky Fan"))

    events = parse_report(report, ht, at)

    return (events, ht, at)


def get_xml_text(matchid) -> str:
    from os.path import exists

    path = f"matches/report_{matchid}.xml"

    if exists(path):
        with open(path, mode="r") as f:
            return f.read()
    else:
        data = requests.get(
            f"https://buzzerbeater.com/match/viewmatch.aspx?matchid={matchid}"
        )

        with open(path, mode="w") as f:
            f.write(data.text)

        return data.text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ids", help="A comma delimited list of match IDs", required=True
    )
    parser.add_argument("--user", help="BBAPI username")
    parser.add_argument("--password", help="BBAPI password")
    args = parser.parse_args()

    matchids = args.ids.split(",")

    for matchid in matchids:
        assert matchid.isnumeric()

        text = get_xml_text(matchid)
        events, ht, at = parse_xml(text)

        # game = Game(matchid, events, ht, at, args)
        # game.play()

        possessions = Possessions()
        shot_types = ShotTypes()
        game = Game(matchid, events, ht, at, args, [possessions, shot_types])
        game.play()

        print(len(possessions.possessions[1]))
        print(possessions.possessions[1])
        print(len(possessions.possessions[0]))
        print(possessions.possessions[0])
        print(shot_types.table(game))


if __name__ == "__main__":
    main()
