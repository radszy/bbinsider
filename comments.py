import xml.etree.ElementTree as XML
from event import *

DEBUG = 0


class Comments:
    def __init__(self) -> None:
        self.comments: dict[str, dict[int, str]] = {}

        input = "commentary-pl.xml"
        tree = XML.parse(input)
        root = tree.getroot()

        for child in root:
            tag = child.tag
            if tag == "Events":
                for event in child:
                    key = event.tag[0:-2]
                    ty = int(event.tag[-1])
                    val = event.text.strip() if event.text else ""

                    if key in self.comments:
                        self.comments[key][ty] = val
                    else:
                        self.comments[key] = {ty: val}

    def get_text2(self, data: str) -> str:
        loc2: int = 0
        loc3: str = ""
        loc4: str = ""
        loc5: str = "e" + data[0:3]
        loc6: int = int(data[0])  # event prefix
        loc7: int = int(data[3], 16)  # result
        loc8: int = int(data[4], 16)  # variation
        loc9: int = int(data[5], 16)  # variation

        if loc6 == 1 or loc6 == 2 or loc6 == 4:
            if loc7 <= 3 or loc7 == 7 or loc7 == 6:
                loc3 = self.get_variant2("e0001", loc8, loc9)
            elif loc7 == 8 or loc7 == 9:
                loc3 = self.get_variant2("e0003", loc8, loc9)
            else:
                loc3 = self.get_variant2("e0002", loc8, loc9)

            partial = self.get_variant2(loc5 + "x", loc8, loc9)
            loc3 = loc3.replace("$event1$", partial)
        elif loc6 == 0:
            loc2 = 1 if loc7 == 1 or loc7 == 4 else 0
            if loc7 == 0:
                loc2 = 2

            loc3 = self.comments["e0000"][loc2]
        else:
            loc4 = loc5 + str(loc7)
            loc3 = self.get_variant2(loc4, loc8, loc9)

        return loc3

    def get_variant2(self, key: str, ty1: int, ty2: int) -> str:
        if key not in self.comments:
            return " "
        if (ty1 * 10 + ty2) in self.comments[key]:
            return self.comments[key][ty1 * 10 + ty2]
        elif ty1 * 10 in self.comments[key]:
            return self.comments[key][ty1 * 10]
        return self.comments[key][0]

    def get_text(self, data: str) -> str:
        loc2 = 0
        loc3 = ""
        loc4 = ""
        loc5 = 0
        loc6 = ""
        event_prefix = int(data[0])  # event_prefix
        event_result = int(data[3], 16)  # result
        evar1 = int(data[4], 16)  # ???
        event_variation = int(data[5], 16)

        if DEBUG:
            print(
                "\nRaw:\n\tprefix: {}\n\tresult: {}\n\tloc9: {}\n\tvar: {}".format(
                    event_prefix, event_result, evar1, event_variation
                )
            )

        # Dunk
        if data[0:3] == "401" and event_variation == 3 and event_result != 4:
            event_variation = 4

        if evar1 > 0:
            loc6 = "e{}{}".format(data[4], data[0:3])
            event_prefix = 99
        else:
            loc6 = "e{}".format(data[0:3])

        if event_result > 9:
            if event_result < 13 or event_result > 14:
                loc5 = 1
            event_result -= 9
        else:
            loc5 = 0

        if event_prefix == 1 or event_prefix == 2 or event_prefix == 4:
            if loc5 == 1:
                loc3 = self.get_variant("e0003", event_variation)
            elif event_result <= 3 or event_result == 7 or event_result == 6:
                loc3 = self.get_variant("e0001", event_variation)
            else:
                loc3 = self.get_variant("e0002", event_variation)

            loc3 = loc3.replace(
                "$event1$", self.get_variant(loc6 + "x", event_variation)
            )
        elif event_prefix == 0:
            loc2 = 1 if event_result == 1 or event_result == 4 else 0
            if event_result == 0:
                loc2 = 2  # Goaltend
            elif event_result == 3 or event_result == 6:
                loc2 = 3  # Blocked
                loc3 = self.comments["e0000"][loc2]
            loc3 = self.comments["e0000"][loc2]
        else:
            loc4 = loc6 + str(event_result)
            loc3 = self.get_variant(loc4, event_variation)

        return loc3

    def get_actors(self, event: BBEvent, teams: list[Team]):
        loc3 = event.result % 16
        loc10 = 0

        if loc3 > 9:
            if loc3 < 13 or loc3 > 14:
                loc10 = 1
            loc3 -= 9
        else:
            loc10 = 0

        team_att = event.team
        team_def = (team_att + 1) % 2
        event_prefix = event.type // 100
        event_type = event.type

        if DEBUG:
            print(
                f"RAW2:\n\tloc3: {loc3}\n\tloc10: {loc10}\n\ttype: {event_type}\n\tprefix: {event_prefix}"
            )

        player_primary = teams[team_att].players[event.player1 - 1]
        player_secondary = teams[team_def].players[event.player2 - 1]

        if loc3 == 4 or loc3 == 5:
            if loc10 == 1 and loc3 == 5:
                player_secondary = teams[team_def].players[event.player2 - 1]
            else:
                player_secondary = teams[team_att].players[event.player2 - 1]

        if loc3 == 8 and event_prefix == 9 and event_type < 950:
            player_primary = teams[team_def].players[event.player1 - 1]

        elif loc3 == 8 and event_prefix != 9:
            player_secondary = teams[team_att].players[event.player2 - 1]

        # Steal / turnover
        if event_type == 807 or event_type == 808:
            player_primary = teams[team_def].players[event.player1 - 1]
            player_secondary = teams[team_att].players[event.player2 - 1]

        # Flagrant foul
        if event_type == 509 or event_type == 510:
            player_primary = teams[team_def].players[event.player1 - 1]

        # Substition
        if event_type == 951:
            team_att = 1 if event.result > 4 else 0
            player_primary = teams[team_att].players[event.player1 - 1]
            player_secondary = teams[team_att].players[event.player2 - 1]
            if player_primary.name == "":
                assert False, "Lucky fan!"

        # Players swapping positions
        if event_type == 952:
            team_att = event.result
            player_primary = teams[team_att].players[event.player1 - 1]
            player_secondary = teams[team_att].players[event.player2 - 1]

        # Ball going out of bounds
        if event_type == 934 and loc3 == 7 and event.variation != 2:
            team_def = event.team
            team_att = (team_def + 1) % 2

        if event_type != 1:
            if event_type != 981 and event_type != 1:
                p1 = player_primary
                t1 = team_att
                p2 = player_secondary
                t2 = team_def
                return p1, t1, p2, t2

        return None, "Invalid", None, "Invalid"

    def get_comment(self, event: BBEvent, teams: list[Team]) -> str:
        text = self.get_text(event.data)
        p1, t1, p2, t2 = self.get_actors(event, teams)
        event.player1obj = p1
        event.player2obj = p2

        if DEBUG:
            print(event.to_string(p1, p2))

        if "$player1$" in text:
            loc = None
            for p in teams[0].players:
                if p.id == p1.id:
                    loc = "(D)"
                    break
            if loc is None:
                for p in teams[1].players:
                    if p.id == p1.id:
                        loc = "(W)"
                        break
            text = text.replace("$player1$", f"{p1.get_shortened_name()} {loc}")

        if "$player2$" in text:
            loc = None
            for p in teams[0].players:
                if p.id == p2.id:
                    loc = "(D)"
                    break
            if loc is None:
                for p in teams[1].players:
                    if p.id == p2.id:
                        loc = "(W)"
                        break
            text = text.replace("$player2$", f"{p2.get_shortened_name()} {loc}")

        if "$team1$" in text:
            text = text.replace("$team1$", teams[t1].name)

        event.comment = text
        print(event.to_string(p1, p2))

        return text

    def get_variant(self, key: str, ty: int) -> str:
        if ty in self.comments[key]:
            return self.comments[key][ty]
        else:
            return self.comments[key][0]
