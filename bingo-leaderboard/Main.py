from Util import make_request
from Player import Player
import pickle


class BingoLeaderboard:

    def __init__(self):
        self.PLAYERS = {}
        self.load_pickle()

    def update(self):
        data = make_request("https://racetime.gg/oot/leaderboards/data")
        if not data:
            return
        bingo_rankings = next(board['rankings'] for board in data['leaderboards'] if board['goal'] == 'Bingo')
        for ranking in bingo_rankings:
            user = ranking['user']
            if not user['id'] in self.PLAYERS:
                self.PLAYERS[user['id']] = Player(user['name'], user['id'], ranking['times_raced'])
            self.PLAYERS[user['id']].update(user['name'], ranking['times_raced'], ranking['score'])
        pickle.dump(self.PLAYERS, open("players.pickle", "wb"))

    def load_pickle(self):
        self.PLAYERS = pickle.load(open("players.pickle", "rb"))


    def display(self):
        players = sorted(self.PLAYERS.values(), key = lambda p: p.leaderboard_time())
        rank = 1
        for i, player in enumerate(players):
            if player.num_finished() == 0:
                continue
            info = [
                player.name,
                str(player.leaderboard_time()).split('.')[0],
                str(player.effective_median()).split('.')[0],
                str(player.average()).split('.')[0],
                player.points,
                f"{player.num_finished()}/{player.num_included_races()}",
                player.last_race_date()
            ]
            print(f"{rank} {' | '.join([str(i) for i in info])}")
            rank += 1

lb = BingoLeaderboard()
lb.display()