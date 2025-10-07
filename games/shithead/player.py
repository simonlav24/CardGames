
from enum import Enum

from core import HandCards, Card, Rank
from games.shithead.ai_player import AiPlayer

class GameStage(Enum):
    CARD_IN_HAND = 0
    FIRST_LEVEL_LUCKY = 1
    SECOND_LEVEL_LUCKY = 2


class Player:
    def __init__(self, ai: AiPlayer=None):
        self.hand_cards = HandCards()
        self.first_level_lucky: list[Card] = []
        self.second_level_lucky: list[Card] = []
        self.ai: AiPlayer = ai

    def is_ai(self) -> bool:
        return self.ai is not None
    
    def ai_play(self, pile_rank: Rank) -> None:
        self.ai.start_turn(pile_rank)

    def deal_first_lucky_card(self, card: Card) -> None:
        self.first_level_lucky.append(card)

    def deal_second_lucky_card(self, card: Card) -> None:
        self.second_level_lucky.append(card)

    def get_game_stage(self) -> GameStage:
        if len(self.hand_cards) > 0:
            return GameStage.CARD_IN_HAND
        if len(self.first_level_lucky) > 0:
            return GameStage.FIRST_LEVEL_LUCKY
        return GameStage.SECOND_LEVEL_LUCKY
    
    def toggle_turn(self) -> None:
        self.hand_cards.toggle_turn()

    def get_hand(self) -> HandCards:
        return self.hand_cards
    
    def step(self) -> None:
        self.hand_cards.step()