from Util import make_request
from ParseResult import is_valid_bingo_race_info, parse_result, Result
import datetime as dt
import sys

MAX_RESULTS = 15
DROP_RESULTS = 3

class Player:
    def __init__(self, name, id, times_raced):
        self.name = name
        self.id = id
        self.results = []
        self.times_raced = times_raced
        self.points = 0

    def update(self, name, times_raced, points):
        self.name = name
        self.times_raced = times_raced
        self.points = points
        self.results = load_results(self.id, times_raced)
        print(f"{self.name} {len(self.results)}\n")

    def leaderboard_time(self):
        forfeit_penalty_time = self.forfeit_time()
        times = [r.time_penalized_by_age() if not r.forfeit else forfeit_penalty_time for r in self.relevant_races()]
        leaderboard_time = average(times)
        return leaderboard_time

    def average(self):
        finished_times = [r.time for r in self.results if not r.forfeit]
        return average(finished_times)

    def effective_median(self):
        worst_time = max([r.time for r in self.results if not r.forfeit])
        times_with_penalized_forfeits = [r.time if not r.forfeit else worst_time for r in self.results]
        return median(times_with_penalized_forfeits)

    def forfeit_time(self):
        relevant_races = self.relevant_races()
        finished_times = [r.time for r in relevant_races if not r.forfeit]
        non_forfeit_avg = average(finished_times)
        if len(finished_times) == 0:
            return non_forfeit_avg
        worst_time = max(finished_times)
        return max(non_forfeit_avg * 1.2, worst_time * 1.1)

    def relevant_races(self):
        top_n_to_include = max(len(self.results) - DROP_RESULTS, DROP_RESULTS)
        return sorted([r for r in self.results], key=lambda r: r.time)[:top_n_to_include]

    def last_race_date(self):
        if len(self.results) == 0:
            return dt.date(1970, 1, 1)
        return max([r.date for r in self.results])

    def num_included_races(self):
        return len(self.results)

    def num_finished(self):
        return len([r for r in self.results if not r.forfeit])

    def print_debug_info(self):
        forfeit_penalty_time = self.forfeit_time()
        times = [r.time_penalized_by_age() if not r.forfeit else forfeit_penalty_time for r in self.relevant_races()]
        leaderboard_time = average(times)
        print('sorted results', [str(r.time).split('.')[0] for r in sorted(self.results, key=lambda r: r.time)])
        print('relevant times', [str(r.time).split('.')[0] for r in self.relevant_races()])
        print('avg relevant times', average([r.time for r in self.relevant_races()]))
        print('avg non forfeit times', average([r.time for r in self.relevant_races() if not r.forfeit]))
        print('leaderboard time     ', leaderboard_time)
        print('forfeit time', forfeit_penalty_time)
        print('age penalized and forfeit times', [str(t).split('.')[0] for t in times])
        if (len([r for r in self.results if r.forfeit]) > DROP_RESULTS):
            print('more forfeits than results dropped')

def average(times):
    if len(times) > 0:
        return sum(times, dt.timedelta(0)) / len(times)
    else:
        return dt.timedelta(0)

def median(times):
    if len(times) > 0:
        times = sorted(times)
        mid = int(len(times) / 2)
        if len(times) % 2 == 0:
            return (times[mid - 1] + times[mid]) / 2
        else:
            return times[mid]
    else:
        return dt.timedelta(0)

def load_results(id, times_raced):
    num_pages = sys.maxsize
    page = 0
    new_results = []
    while(page < num_pages and len(new_results) < MAX_RESULTS and len(new_results) < times_raced):
        page += 1
        data = make_request(f"https://racetime.gg/user/{id}/races/data?show_entrants=true&page={page}")
        if not data:
            return
        num_pages = data['num_pages']
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
