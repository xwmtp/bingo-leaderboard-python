from Util import make_request
from Player import Player


class BingoLeaderboard:

    def __init__(self):
        self.PLAYERS = Players()

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
            self.PLAYERS[user['id']].update()

lb = BingoLeaderboard()
for player in lb.PLAYERS.PLAYERS.values():
    print(player.name)
    player.leaderboard_time()