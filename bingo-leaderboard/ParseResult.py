import datetime as dt
import isodate
import re
import Definitions

def is_valid_bingo_race_info(race_info):
    if race_info['category']['slug'] != 'oot' or race_info['goal']['name'] != 'Bingo' or race_info['goal']['custom']:
        return False
    return is_regular_bingo_goal(race_info['info'])

def is_regular_bingo_goal(goal):
    for mode in ['short', 'long', 'blackout', 'black out', '3x3', '4x4', 'anti', 'double', 'bufferless', 'child', 'jp', 'japanese', 'bingo-j']:
        if mode in goal.lower():
            return False
    version_re = r"((?:v|beta)\d+(?:\.\d+)*(?:-[A-Za-z]*)?)"
    match = re.search(rf'ootbingo\.github\.io/bingo/{version_re}/bingo\.html\?seed=\d+&mode=normal', goal.lower())
    return match is not None


def parse_result(race, entrant):
    dct = {}
    dct['id'] = race['name'].replace('oot/', '')
    dct['date'] = race['ended_at']
    if dct['date']:
        dct['date'] = str(isodate.parse_date(dct['date']))
    else:
        dct['date'] = str(dt.date(1970, 1, 1))
    dct['num_entrants'] = race['entrants_count']
    dct['goal'] = race['info']
    dct['time'] = entrant['finish_time']
    if dct['time']:
        dct['time'] = isodate.parse_duration(dct['time'])
    else:
        dct['time'] = dt.timedelta(seconds=0)
    dct['forfeit'] = entrant['status']['value'] == 'dnf'
    dct['dq'] = entrant['status']['value'] == 'dq'
    dct['finished'] = not dct['forfeit'] and not dct['dq']
    dct['rank'] = entrant['place']
    dct['points'] = entrant['score'] if entrant['score'] else 0
    dct['comment'] = entrant['comment'] if entrant['comment'] else ''
    return dct


class Result:

    def __init__(self, race_info):
        self.id = race_info['id']
        self.goal = race_info['goal']
        self.total_players = race_info['num_entrants']
        self.date = dt.datetime.strptime(race_info['date'], '%Y-%m-%d').date()
        self.time = race_info['time']

        self.forfeit = race_info['forfeit']
        self.dq = race_info['dq']
        self.finished = not self.forfeit and not self.dq
        if not self.finished:
            self.time = dt.timedelta(seconds=86313600) # 999 days
        self.rank = race_info['rank']
        self.points = int(race_info['points'])
        self.comment = race_info['comment']
        self.blocklisted = self.id in Definitions.EXCLUDE

    def is_valid_bingo_result(self):
        return not self.blocklisted and not self.dq and is_regular_bingo_goal(self.goal)

    def time_penalized_by_age(self):
        now = dt.datetime.now().date()
        age = max((now - self.date).days, 0)
        factor = age_penalty_factor(age)
        return self.time * factor



def age_penalty_factor(days):
    penalty_factor = 1 - 1.5/335 + (days * 0.05 / 335)
    if penalty_factor >= 1.1:
        return 1.1
    if penalty_factor <= 1:
        return 1
    return penalty_factor
