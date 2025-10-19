
from dataclasses import dataclass
from collections import Counter

from utils import randint
from core import Card, Rank, sort_aces_high, HandCards, Suit
from engine import post_event, ClickedCard, DoubleClickedCard

from games.durak.player import PlayerBase, PlayerMode
from games.durak.durak_table import DurakTable, GameStage
from games.durak.constants import *


DEBUG = True

def debug_print(text: str) -> None:
    if DEBUG:
        print(f'> Ai Player: {text}')



class AiPlayer(PlayerBase):
    def start_turn(self):
        debug_print('AI starting turn')
        self._asses_options()

    
    def _asses_options(self) -> None:
        debug_print(f'Assessing options, mode: {self.mode}, game stage: {self.table.stage}')
        match self.mode:
            case PlayerMode.DEFEND:
                self._defend()
    

    def _defend(self) -> None:
        undefended = self._get_undefended_cards()



    def _get_undefended_cards(self) -> list[Card]:
        undefended: list[Card] = []
        for place in self.table.pot.places:
            if place[1] is None:
                undefended.append(place[0])
        return undefended



@dataclass
class KnowledgeBase:
    table: DurakTable
    hand: HandCards
    other_players_cards: dict[int, list[Card]]

    def get_kozer(self) -> Suit:
        return self.table.kozer


class OptionBase:
    def __init__(self, knowledge: KnowledgeBase):
        self.knowledge = knowledge

    def score(self) -> int:
        return -1
    



class AttackCardOption(OptionBase):
    def __init__(self, knowledge: KnowledgeBase, card: Card):
        super().__init__(knowledge)
        self.card_choice = card
    
    def score(self) -> int:
        remaining_cards = self.knowledge.hand.cards.copy()
        remaining_cards.remove(self.card_choice)
        score = hand_score(remaining_cards, self.knowledge.get_kozer())

        return score


def hand_score(hand: list[Card], kozer: Suit) -> int:
    score = 0
    # better score for higher ranked cards
    for card in hand:
        score += card.rank.value
        if card.suit == kozer:
            score += KOZER_BONUS

    # better score for card with pairs
    rank_counts = Counter(card.rank for card in hand)
    pairs = [rank for rank, count in rank_counts.items() if count >= 2]
    
    return score







