from .truco import Truco

class Turn:
    def __init__(self, players : list, teams : list) -> None:
        self.players = players
        self.teams = teams
        self.truco = Truco()
        for player in self.players:
            player.playing_turn = True
        self.truco.deal_cards(self.players)
        self.truco.envido(players)
        self.truco.flor(players)
        self.rounds_winners = []
        self.played_cards = {}
        self.round = 0
        self.turn_value = 1
        self.envidos : str = ''
        self.flor : str = ''
        self.envido_completed = False
        self.ended = False
        self.truco_caller : object | None = None

    def play_card(self, player, card : str) -> bool:
        if player.cards.get(card, False):
            self.played_cards[player] = card
            player.cards[card] = False
            return True
        return False

    def call_truco(self, caller : object) -> None:
        if self.turn_value == 4:
            raise Exception('TrucoLimit')
        self.turn_value += 1
        self.truco_caller = caller
        
    def call_flor(self, caller_team : object, accepted : bool) -> list | None:
        """Gerencia a chamada e resolução da Flor, Contra-Flor e Contra-Flor & o Resto entre dois times."""
        winner = sorted(self.players, key=lambda x: (x.flor if x.flor is not None else False, x.team.is_hand), reverse=True)
        winner_team = winner[0].team
        for team in self.teams:
            if team is not winner_team:
                other_team = team
                break
        
        match self.flor:
            case 'f':
                points = (3, 3)
                
            case 'fc':
                points = (3, 6)
                
            case 'fcr':
                points = (6, 30 - other_team.points)
                
        if not accepted:
            caller_team.points += points[0]
        
        else:
            winner_team.points += points[1]
            return winner

    def call_envido(self, caller_team : object, accepted : bool) -> list | None:
        """Gerencia a chamada e resolução do Envido, Real Envido, Falta Envido entre dois times."""
        winner = sorted(self.players, key=lambda x: (x.envido_points, x.team.is_hand), reverse=True)
        winner_team = winner[0].team
        for team in self.teams:
            if team is not winner_team:
                other_team = team
                break
        
        match self.envidos:
            case 'e':
                points = (1, 2)
            
            case 'r':
                points = (1, 3)
            
            case 'er':
                points = (2, 5)
            
            case 'f':
                points = (1, 30 - other_team.points)
            
            case 'ef':
                points = (2, 30 - other_team.points)
            
            case 'rf':
                points = (3, 30 - other_team.points)
            
            case 'erf':
                points = (5, 30 - other_team.points)
                
        if not accepted:
            caller_team.points += points[0]
            self.completed_envido = True
            
        else:
            winner_team.points += points[1]
            self.completed_envido = True
            return winner
            
    def abandon_round(self, abandon_player : object) -> None:
        abandon_player.playing_turn = False
        for player in abandon_player.team.players:
            if player.playing_turn:
                return None
        for team in self.teams:
            if abandon_player.team is not team:
                team.points += self.turn_value
                if self.envidos == '' and self.flor == '' and self.round == 0:
                    team.points += 1
                self.ended = True
                break
            
    def recused_truco(self, winner_team : object) -> None:
        winner_team.points += self.turn_value
        self.ended = True

    def end_round(self) -> object:
        """Retorna player que deve começar a próxima rodada"""
        winner = self.truco.round_winner(self.played_cards)
        self.played_cards = {}
        winner = {s_w: winner[s_w] for s_w in sorted(winner, key=lambda x: x.team.is_hand, reverse=True)}
        winners = []
        team_winners = set()
        for player, won in winner.items():
            if won and player.team not in team_winners:
                winners.append(player)
                team_winners.add(player.team)

        if len(winners) == 1:
            if winners[0].team in self.rounds_winners or 'draw' in self.rounds_winners:
                winner_team = winners[0].team
                winner_team.points += self.turn_value
                self.ended = True
            self.rounds_winners.append(winners[0].team)
        else:
            winner_team = None
            for team in self.rounds_winners:
                if team != 'draw':
                    winner_team = team
                    break
            if not winner_team:
                self.rounds_winners.append('draw')
                if self.round == 2:
                    self.ended = True
            else:
                winner_team.points += self.turn_value
                self.ended = True

        self.round += 1
        return winners[0]
