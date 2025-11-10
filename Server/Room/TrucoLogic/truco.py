import re
from copy import copy
import random

class Truco:
    def __init__(self):
        self.cards = ['1_ouros', '2_ouros', '3_ouros', '4_ouros', '5_ouros', '6_ouros', '7_ouros', 'j_ouros', 'q_ouros', 'k_ouros',
                      '1_paus', '2_paus', '3_paus', '4_paus', '5_paus', '6_paus', '7_paus', 'j_paus', 'q_paus', 'k_paus',
                      '1_espadas', '2_espadas', '3_espadas', '4_espadas', '5_espadas', '6_espadas', '7_espadas', 'j_espadas', 'q_espadas', 'k_espadas',
                      '1_copas', '2_copas', '3_copas', '4_copas', '5_copas', '6_copas', '7_copas', 'j_copas', 'q_copas', 'k_copas']

        self.__cards_order_pat = re.compile(r'(?P<C0>1_espadas)|(?P<C1>1_paus)|(?P<C2>7_espadas)|(?P<C3>7_ouros)|(?P<C4>3_[a-z]+)|(?P<C5>2_[a-z]+)|(?P<C6>1_[a-z]+)|(?P<C7>k_[a-z]+)|(?P<C8>q_[a-z]+)|(?P<C9>j_[a-z]+)|(?P<C10>7_[a-z]+)|(?P<C11>6_[a-z]+)|(?P<C12>5_[a-z]+)|(?P<C13>4_[a-z]+)')

    def deal_cards(self, players : list) -> None:
        """Retorna cartas a partir de uma lista de jogadores [Player] -> {Player : list[cards]}"""
        for player in players:
            player.cards = {} # Zerar cartas
        cards = copy(self.cards)
        random.shuffle(cards)
        players = players * 3
        for i, player in enumerate(players):
            player.cards[cards[i]] = True

    def round_winner(self, players_cards : dict) -> dict:
        """Retorna vencedor da rodada a partir de um dicionário de jogadores com suas devidas cartas {Player : str(card)} -> {Player : True | False} --- Pode retornar mais de um Player com True, dependerá da partida decidir como empate ou vitória da mão"""
        players_cards = copy(players_cards)
        for player, card in players_cards.items():
            players_cards[player] = int(self.__cards_order_pat.match(card).lastgroup[1:])

        better = min(players_cards.values())
        for player, card in players_cards.items():
            if card == better:
                players_cards[player] = True
            else:
                players_cards[player] = False

        return players_cards

    @staticmethod
    def envido(players : list) -> None:
        """Calcula valores de envido individuais a partir de uma lista de jogadores list[Player] => Player.envido = int(points)}"""
        for player in players:
            values = list(map(lambda x: int(x[0]) if x[0] != 'j' and x[0] != 'q' and x[0] != 'k' else 0, player.cards))
            suits = list(map(lambda x: x[2:], player.cards))

            val = {}
            for v, s in zip(values, suits):
                val.setdefault(s, []).append(v)

            best = 0
            for n, vs in val.items():
                if len(vs) >= 2:
                    s = 20 + sum(sorted(vs, reverse=True)[:2])
                    if s > best:
                        best = s
                else:
                    if vs[0] > best:
                        best = vs[0]

            player.envido_points = best

    @staticmethod
    def flor(players : list) -> None:
        """Calcula valores de flor a partir de uma lista de jogadores list[Player] => Player.flor : int(points) | False --- Player : False pode ocorrer caso o Player não possua Flor"""
        for player in players:
            values = list(map(lambda x: int(x[0]) if x[0] != 'j' and x[0] != 'q' and x[0] != 'k' else 0, player.cards))
            suits = list(map(lambda x: x[2:], player.cards))

            val = {}
            for v, s in zip(values, suits):
                val.setdefault(s, []).append(v)

            if len(val) > 1:
                player.flor = False

            else:
                n, vs = val.popitem()
                player.flor = 20 + sum(vs)
