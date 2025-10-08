
from enum import Enum

from core import HandCards, Card, Vacant

class GameStage(Enum):
    CARD_IN_HAND = 0
    FIRST_LEVEL_LUCKY = 1
    SECOND_LEVEL_LUCKY = 2
    END = 3


class PlayerBase:
    def __init__(self):
        self.hand_cards = HandCards()
        self.first_level_lucky: list[Card] = []
        self.second_level_lucky: list[Card] = []
        self.pile_vacant: Vacant

    def initialize(self, pile_vacant: Vacant) -> None:
        self.pile_vacant = pile_vacant
    
    def deal_first_lucky_card(self, card: Card) -> None:
        self.first_level_lucky.append(card)

    def deal_second_lucky_card(self, card: Card) -> None:
        self.second_level_lucky.append(card)

    def get_game_stage(self) -> GameStage:
        if len(self.hand_cards) > 0:
            return GameStage.CARD_IN_HAND
        if len(self.first_level_lucky) > 0:
            return GameStage.FIRST_LEVEL_LUCKY
        if len(self.second_level_lucky) > 0:
            return GameStage.SECOND_LEVEL_LUCKY
        return GameStage.END
    
    def toggle_turn(self) -> None:
        self.hand_cards.toggle_turn()

    def get_hand(self) -> HandCards:
        return self.hand_cards
    
    def step(self) -> None:
        self.hand_cards.step()

    def start_turn(self) -> bool:
        ...
    
    def deal(self, card: Card) -> None:
        ...


class Player(PlayerBase):
    def start_turn(self) -> bool:
        return True
    
    def deal(self, card: Card) -> None:
        self.hand_cards.append(card)