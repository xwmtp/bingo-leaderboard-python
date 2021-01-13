from Util import make_request
from ParseResult import is_valid_bingo_race_info, parse_result, Result
import sys




class BingoLeaderboard:

    def __init__(self):
        self.PLAYERS = Players()

    def run(self):
        for player in self.PLAYERS.PLAYERS.values():
            player.printt()






class Players:

    def __init__(self):
        self.PLAYERS = {}
        self.update()

    def update(self):
        data = make_request("https://racetime.gg/oot/leaderboards/data")
        if not data:
            return
        bingo_rankings = next(board['rankings'] for board in data['leaderboards'] if board['goal'] == 'Bingo')
        for ranking in bingo_rankings[:20]:
            user = ranking['user']
            if not user['id'] in self.PLAYERS:
                self.PLAYERS[user['id']] = Player(user['name'], user['id'])
            self.PLAYERS[user['id']].load_results()


class Player:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.results = []
        self.MAX_RESULTS = 15

    def load_results(self):
        num_pages = sys.maxsize
        page = 1
        new_results = []
        while(page <= num_pages and len(new_results) < self.MAX_RESULTS):
            data = make_request(f"https://racetime.gg/user/{self.id}/races/data?show_entrants=true&page={page}")
            if not data:
                return
            num_pages = data['num_pages']
            page += 1
            for race in data['races']:
                if not is_valid_bingo_race_info(race):
                    continue
                entrant = next(entrant for entrant in race['entrants'] if entrant['user']['id'] == self.id)
                result = Result(parse_result(race, entrant))
                if result.is_valid_bingo_result():
                    new_results.append(result)
                if len(new_results) >= self.MAX_RESULTS:
                    break
        print(f"{self.name} {len(new_results)}")
        self.results = new_results

    def printt(self):
        print()
        print(self.name)
        for result in self.results:
            print(result.time)

lb = BingoLeaderboard()
lb.run()