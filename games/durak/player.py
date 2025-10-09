
from enum import Enum

from core import HandCards, Card, Vacant, Suit
from games.durak.durak_pot import DurakPot

class PlayerMode(Enum):
    NONE = 0
    ATTACK = 1
    DEFEND = 2


class PlayerBase:
    def __init__(self):
        self.hand_cards = HandCards()
        self.hand_cards.multi_select = False
        self.pot: DurakPot = None
        self.mode = PlayerMode.NONE
        self.kozer: Suit = None

    def initialize(self, pot: list[Vacant], kozer: Suit) -> None:
        self.pot = pot
        self.kozer = kozer
        
    def get_hand(self) -> HandCards:
        return self.hand_cards
    
    def step(self) -> None:
        self.hand_cards.step()

    def attack(self) -> None:
        self.mode = PlayerMode.ATTACK

    def defend(self) -> None:
        self.mode = PlayerMode.DEFEND
    
    def deal(self, card: Card) -> None:
        ...

class Player(PlayerBase):
    ...
