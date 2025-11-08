from truco import Truco

class Turn:
    def __init__(self, players : list, teams : list) -> None:
        self.players = players
        self.teams = teams
        self.truco = Truco()
        self.truco.deal_cards(self.players)
        self.truco.envido(players)
        self.truco.flor(players)
        self.rounds_winners = []
        self.played_cards = {}
        self.turn = 0
        self.turn_value = 1
        self.ended = False

    def play_card(self, player, card : str) -> None:
        self.played_cards[player] = card
        player.cards[card] = False

    def call_truco(self):
        if self.turn_value == 4:
            raise Exception('TrucoLimit')
        self.turn_value += 1

    def envido(self, caller: object, initial_type: str = 'envido') -> None:
        """Gerencia a chamada e resolução do Envido, Real Envido, Falta Envido entre dois times."""
        opponent = [p for p in self.players if p.team != caller.team][0]
        #CASO 1
        if initial_type == 'real_envido': # chama real envido direto
            print(f"Time {caller.team.team} chamou REAL ENVIDO")
            resp = input(f"{opponent.name} aceita o REAL ENVIDO? (s = quero / n = não quero / f = falta envido): ").strip().lower()
            if resp == 'n': #nao quis
                print(f"{opponent.name} recusou, time {caller.team.team} ganha 2 pontos")
                caller.team.points += 2
                return
            if resp == 'f': #chama falta em cima do real
                print(f"{opponent.name} respondeu com FALTA ENVIDO")
                resp2 = input(f"{caller.name}, aceita FALTA ENVIDO? (s = quero / n = não quero): ").strip().lower()
                if resp2 == 'n': #rewcusou falta
                    print(f"{caller.name} nao quis FALTA ENVIDO, time {opponent.team.team} ganha 3 pontos")
                    opponent.team.points += 5
                    return
                else: #aceitou falta
                    tipo = 'falta_envido'
            else: #aceitou real
                tipo = 'real_envido'

        else:  #CASO 2
            if initial_type == 'envido':   #envido
                print(f"Time {caller.team.team} chamou ENVIDO")
                resp = input(f"{opponent.name}, aceita o envido? (s = quero / n = não quero / r = real envido / f = falta envido): ").strip().lower()

                if resp == 'n': #recusa envido
                    print(f"{opponent.name} nao quis o ENVIDO, time {caller.team.team} ganha 1 ponto")
                    caller.team.points += 1
                    return
                
                if resp == 'r': #subiu pra real
                    print(f"{opponent.name} respondeu com REAL ENVIDO")
                    resp2 = input(f"{caller.name} aceita o REAL ENVIDO? (s = quero / n = não quero): ").strip().lower()
                    if resp2 == 'n': #nao quis real
                        print(f"{caller.name} nao quis o REAL ENVIDO, time {opponent.team.team} ganha 3 pontos")
                        opponent.team.points += 3
                        return
                    else: #aceitou real em cima do envido
                        tipo = 'real_envido_after_envido'
                elif resp == 'f': # subiu para falta envido
                    print(f"{opponent.name} respondeu com FALTA ENVIDO")
                    resp2 = input(f"{caller.name} aceita FALTA ENVIDO? (s = quero / n = não quero): ").strip().lower()
                    if resp2 == 'n': #recusa falta em cima do envido
                        print(f"{caller.name} nao quis FALTA ENVIDO, time {opponent.team.team} ganha 2 pontos")
                        opponent.team.points += 2
                        return
                    else: #aceita falta
                        tipo = 'falta_envido'
                else:
                    # aceitou envido simples
                    tipo = 'envido'
            #CASO 3
            else:   #chama falta direto
                print(f"Time {caller.team.team} chamou FALTA ENVIDO")
                resp = input(f"{opponent.name} aceita FALTA ENVIDO? (s = quero / n = não quero): ").strip().lower()
                if resp == 'n': #recusa
                    print(f"{opponent.name} nao quis FALTA ENVIDO, time {caller.team.team} ganha 1 pontos")
                    caller.team.points += 1
                    return
                else: #aceita
                    tipo = 'falta_envido'

        if tipo == 'envido':
            value = 2
        elif tipo == 'real_envido':
            value = 3
        elif tipo == 'real_envido_after_envido':
            value = 5
        elif tipo == 'falta_envido':
            value = 30 - min(team.points for team in self.teams)  #calculo do falta

        #det vencedor
        best_points = max(p.envido_points for p in self.players)
        candidates = [p for p in self.players if p.envido_points == best_points]

        if len(candidates) == 1:
            winner = candidates[0]
        else: #empate ganha a mao
            winner = next((p for p in candidates if p.team.is_hand), candidates[0])
        winner.team.points += value
        print(f"{winner.name} venceu o com {winner.envido_points} pontos, ganhando {value} pontos")

    def end_round(self) -> object:
        """Retorna player que deve começar a próxima rodada"""
        winner = self.truco.round_winner(self.played_cards)
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
                if self.turn == 2:
                    self.ended = True
            else:
                winner_team.points += self.turn_value
                self.ended = True

        self.turn += 1
        return winners[0]
