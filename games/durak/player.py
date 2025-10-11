
from enum import Enum

from core import Card, Vacant, Suit, sort_aces_high, HandCards
from games.durak.durak_pot import DurakPot

class PlayerMode(Enum):
    NONE = 0
    ATTACK = 1
    DEFEND = 2


class DurakSort:
    def __init__(self, kozer: Suit):
        self.kozer = kozer

    def tranlsate(self, card: Card) -> int:
        base_value = sort_aces_high(card.rank)
        if card.suit == self.kozer:
            base_value += 15
        return base_value


class PlayerBase:
    def __init__(self):
        self.hand_cards = HandCards()
        self.sorter: DurakSort = None
        self.hand_cards.sort_func = None
        self.hand_cards.multi_select = False
        self.pot: DurakPot = None
        self.mode = PlayerMode.NONE
        self.kozer: Suit = None

    def initialize(self, pot: list[Vacant], kozer: Suit) -> None:
        self.pot = pot
        self.kozer = kozer
        self.sorter = DurakSort(kozer)
        self.hand_cards.sort_func = self.sorter.tranlsate
        
    def get_hand(self) -> HandCards:
        return self.hand_cards
    
    def step(self) -> None:
        self.hand_cards.step()

    def attack(self) -> None:
        self.mode = PlayerMode.ATTACK

    def defend(self) -> None:
        self.mode = PlayerMode.DEFEND
    
    def deal(self, card: Card) -> None:
        self.hand_cards.append(card)
    
    def toggle_turn(self) -> None:
        self.hand_cards.toggle_turn()

class Player(PlayerBase):
    ...
