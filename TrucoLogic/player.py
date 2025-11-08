class Player:
    def __init__(self, id : int, name : str, team : object):
        self.id : int = id
        self.name : str = name
        self.team = team
        self.cards : dict
        self.flor : int | bool
        self.envido_points : int
