from player import Player
from team import Team
from turn import Turn

if __name__ == '__main__':
    t1 = Team('timeteu')
    t2 = Team('lh')

    th = Player(0, 'theo', t1)
    t1.players.append(th)
    lh = Player(1, 'luis', t2)
    t2.players.append(lh)

    players = [th, lh]
    teams = [t1, t2]
    t1.is_hand = False
    t2.is_hand = True

    p = -1
    sorted

    while True:
        t1.is_hand = not t1.is_hand
        t2.is_hand = not t2.is_hand
        p = (p + 1) % len(players)
        start_turn = players[p]
        for team in teams:
            print(f'Team {team.team}: {team.points}')
        turn = Turn(players, teams)
        print(th.cards, th.envido_points, th.flor)
        print(lh.cards, lh.envido_points, lh.flor)

        #test envido
        envido_chamado = False
        # pergunta p mao
        resposta = input(f"{start_turn.name}, deseja jogar envido? (n = não / e = envido / r = real envido / f = falta envido): ").strip().lower()
        if resposta in ('e', 'r', 'f'):
            tipo = (
                'envido' if resposta == 'e'
                else 'real_envido' if resposta == 'r'
                else 'falta_envido'
            )
            turn.envido(start_turn, tipo)
            envido_chamado = True
        else: #outro time pergunta
            next_player = [p for p in players if p != start_turn][0]
            resposta = input(f"{next_player.name}, deseja jogar envido? (n = não / e = envido / r = real envido / f = falta envido): ").strip().lower()
            if resposta in ('e', 'r', 'f'):
                tipo = (
                    'envido' if resposta == 'e'
                    else 'real_envido' if resposta == 'r'
                    else 'falta_envido'
                )
                turn.envido(next_player, tipo)
                envido_chamado = True
        #fim test envido

        while not turn.ended:
            for player in (players[start_turn.id:] + players[:start_turn.id]):
                play_card = input(f'{player.name} - insira a carta: ')
                turn.play_card(player, play_card)
            start_turn = turn.end_round()
            print(th.cards, th.envido_points, th.flor)
            print(lh.cards, lh.envido_points, lh.flor)
