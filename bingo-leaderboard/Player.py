from Util import make_request
from ParseResult import is_valid_bingo_race_info, parse_result, Result
import datetime as dt
import sys

MAX_RESULTS = 15
DROP_RESULTS = 3

class Player:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.results = []

    def update(self):
        self.results = load_results(self.id)
        print(f"{self.name} {len(self.results)}")

    def leaderboard_time(self):
        num_races = max(len(self.results) - DROP_RESULTS, DROP_RESULTS)
        relevant_races = sorted([r for r in self.results], key=lambda r: r.time)[:num_races]
        print([str(t.time) for t in relevant_races])
        times = [r.time_penalized_by_age() for r in relevant_races]
        print([str(t) for t in times])
        print(average([r.time for r in relevant_races]))
        print(average(times))


def average(times):
    if len(times) > 0:
        return sum(times, dt.timedelta(0)) / len(times)
    else:
        return dt.timedelta(0)

def load_results(id):
    num_pages = sys.maxsize
    page = 1
    new_results = []
    while(page <= num_pages and len(new_results) < MAX_RESULTS):
        data = make_request(f"https://racetime.gg/user/{id}/races/data?show_entrants=true&page={page}")
        if not data:
            return
        num_pages = data['num_pages']
        page += 1
        for race in data['races']:
            if not is_valid_bingo_race_info(race):
                continue
            entrant = next(entrant for entrant in race['entrants'] if entrant['user']['id'] == id)
            result = Result(parse_result(race, entrant))
            if result.is_valid_bingo_result():
                new_results.append(result)
            if len(new_results) >= MAX_RESULTS:
                break
    return new_results
