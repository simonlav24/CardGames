
from enum import Enum

from core import Card, Suit, sort_aces_high, HandCards
from games.durak.durak_table import DurakTable
from games.durak.constants import *

class PlayerMode(Enum):
    NONE = 0
    FIRST_ATTACKER = 1
    ATTACK = 2
    DEFEND = 3


class DurakSort:
    def __init__(self, kozer: Suit):
        self.kozer = kozer

    def tranlsate(self, card: Card) -> int:
        base_value = sort_aces_high(card.rank)
        if card.suit == self.kozer:
            base_value += KOZER_BONUS
        return base_value


class PlayerBase:
    def __init__(self):
        self.hand_cards = HandCards()
        self.sorter: DurakSort = None
        self.hand_cards.sort_func = None
        self.hand_cards.multi_select = False
        self.table: DurakTable = None
        self.mode = PlayerMode.NONE
        self.player_index = -1

    def initialize(self, table: DurakTable) -> None:
        self.table = table
        self.sorter = DurakSort(table.kozer)
        self.hand_cards.sort_func = self.sorter.tranlsate
        
    def get_hand(self) -> HandCards:
        return self.hand_cards
    
    def step(self) -> None:
        self.hand_cards.step()
    
    def deal(self, card: Card) -> None:
        self.hand_cards.append(card)
    
    def toggle_turn(self) -> None:
        self.hand_cards.toggle_turn()

    def start_turn(self) -> None:
        ...

class Player(PlayerBase):
    def start_turn(self) -> None:
        print('Human starting turn')
