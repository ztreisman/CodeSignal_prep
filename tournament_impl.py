import threading


class Tournament:
    """Base class — do not modify."""

    def add_player(self, name: str) -> int:
        raise NotImplementedError

    def get_player(self, player_id: int):
        return None

    def record_result(self, winner_id: int, loser_id: int, points: int) -> bool:
        return False

    def get_ranking(self, n: int = None) -> list:
        return []

    def get_undefeated(self) -> list:
        return []

    def get_by_score_range(self, min_score: int, max_score: int) -> list:
        return []

    def get_stats(self) -> dict:
        return {"total_players": 0, "total_matches": 0,
                "total_points": 0, "average_score": 0.0}

    def get_top_scorer(self):
        return None

    def record_results_parallel(self, results: list) -> list:
        return []


class TournamentImpl(Tournament):

    def __init__(self):
        self.players = {}
        self.next_id = 1
        self.total_matches = 0
        self.total_players = 0
        self.total_points = 0
        self.lock = threading.Lock()

# level 1

    def add_player(self, name):
        player_id=self.next_id
        self.next_id += 1
        self.players[player_id] = {"id": player_id, "name": name, "score":0, "wins":0, "losses":0}
        self.total_players += 1
        return player_id
    
    def get_player(self, player_id):
        return self.players.get(player_id)
    
# level 2

    def record_result(self, winner_id: int, loser_id: int, points: int) -> bool:
        if winner_id in self.players:
            if loser_id in self.players:
                self.get_player(winner_id)["score"] += points
                self.get_player(winner_id)["wins"] += 1
                self.get_player(loser_id)["losses"] += 1
                self.total_matches += 1
                self.total_points += points
                return True
        return False
    
    def get_ranking(self, n: int = None) -> list:
       sorted_players = sorted(self.players.values(), key=lambda x : (-x["score"], x["name"])) 
       if n == None:
           return sorted_players
       return sorted_players[:n]
    
# level 3

    def get_undefeated(self) -> list:
        return sorted([x for x in self.players.values() if x["losses"] == 0 if x["wins"]>0], key = lambda p : p["score"], reverse=True)
    
    def get_by_score_range(self, min_score: int, max_score: int) -> list:
        return sorted([x for x in self.players.values() if x["score"] >= min_score if x["score"]<= max_score], key = lambda p : (-p["score"], p["name"]))
    
# level 4

    def get_stats(self) -> dict:
        if self.total_players == 0:
            avg_score = 0.0
        else:
            avg_score = round(sum([x["score"] for x in self.players.values()])/self.total_players, 2)
        return {"total_players": self.total_players, "total_matches":self.total_matches, "total_points":self.total_points, "average_score":avg_score}
    
    def get_top_scorer(self):
        if self.players:
            top_score = max([x["score"] for x in self.players.values()])
            top_scorers = sorted([x for x in self.players.values() if x["score"] == top_score], key=lambda x : x["name"])
            return top_scorers[0]
        return None

# level 5

    def record_results_parallel(self, results):

        bool_results = [None]*len(results)
        current_i = 0

        def worker():
            nonlocal current_i
            while True:
                with self.lock:
                    if current_i >= len(results):
                        break
                    i =current_i
                    current_i += 1
                    bool_results[i] = self.record_result(
                        results[i][0], results[i][1], results[i][2])
        
        threads = []
        for _ in range(len(results)):
            t= threading.Thread(target=worker)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        return bool_results
