class Team:
    def __init__(self, team : str):
        self.team = team
        self.players : list = []
        self.is_hand : bool
        self.points = 0
