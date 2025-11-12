from player import Player
from team import Team
from turn import Turn

def manage_truco(turn, caller):
    answer_player = players[(caller.id + 1) % len(players)]
    while True:
        ans = input(f'{answer_player.name} aceita truco? YES/NOO para aceitar ou recusar{", RET para aumentar" if turn.turn_value == 1 else ", VQT para aumentar" if turn.turn_value == 2 else ""}')
        match ans:
            case 'YES':
                turn.call_truco(caller.team)
                return 0
            
            case 'NOO':
                turn.recused_truco(caller.team)
                return 0
                
            case 'RET':
                if turn.turn_value == 1:
                    turn.call_truco(answer_player.team)
                    return manage_truco(turn, answer_player)
            
            case 'VQT':
                if turn.turn_value == 2:
                    turn.call_truco(answer_player.team)
                    return manage_truco(turn, answer_player)

def manage_envido(turn : Turn, caller : Player) -> None:
    answer_player = players[(caller.id + 1) % len(players)]
    while True:
        ans = input(f'{answer_player.name} aceita envido? YES/NOO para aceitar ou recusar, ou REN, FEN para aumentar: ')
        match ans:
            case 'YES':
                winners = turn.call_envido(caller.team, accepted=True)
                print(f'\nORDEM DO ENVIDO')
                for player in winners:
                    print(f'{player.name} : {player.envido_points}')
                return 0
            
            case 'NOO':
                turn.call_envido(caller.team, accepted=False)
                return 0
            
            case 'REN':
                if not any(env in turn.envidos for env in ['r', 'f']):
                    turn.envidos += 'r'
                    return manage_envido(turn, answer_player)
            
            case 'FEN':
                if 'f' not in turn.envidos:
                    turn.envidos += 'f'
                    return manage_envido(turn, answer_player)
            

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

    while True:
        t1.is_hand = not t1.is_hand
        t2.is_hand = not t2.is_hand
        p = (p + 1) % len(players)
        start_turn = players[p]
        turn = Turn(players, teams)

        while not turn.ended:
            for player in (players[start_turn.id:] + players[:start_turn.id]):
                print(f'ROUND INFOS:\nTEAM_1 POINTS: {teams[0].points}\nTEAM_2 POINTS: {teams[1].points}\nPLAYER HAND: {', '.join([card for card in player.cards if player.cards[card]])}\nPLAYER ENVIDO: {player.envido_points}\nTURN VALUE: {turn.turn_value}\nTURN ENVIDOS: {turn.envidos}\n')
                while player.playing_turn:
                    for team in teams:
                        if team.points >= 30:
                            print(f'Time {team.team} venceu o jogo!')
                            exit(0)
                    mov = input(f'{player.name} - insira seu movimento: ')
                    match mov[:3]:
                        case X if (X == 'ENV' or X == 'REN' or X == 'FEN'):
                            if not turn.envidos and turn.round == 0 and turn.turn_value == 1:
                                turn.envidos += mov[0].lower()
                                manage_envido(turn, player)
                        
                        case 'TRC':
                            if player.team is not turn.truco_caller and turn.turn_value < 4:
                                manage_truco(turn, player)
                        
                        case 'ABN':
                            turn.abandon_round(player)
                            break
                        
                        case 'PLY':
                            played = turn.play_card(player, mov[3:])
                            if played: break
            
            if not turn.ended: start_turn = turn.end_round()
