
from math import sin, pi
import time

from utils.utils import Vector2 

from core.card import Card, CARD_SIZE, rank_translate_ace_high
from core.card_container import CardContainer

class HandCards(CardContainer):
    ''' cards held in hand '''
    def __init__(self):
        super().__init__()
        # center pos
        self.pos = Vector2()
        self.margin = - CARD_SIZE[0] // 2
        self.rank_tranlsate = rank_translate_ace_high
        self.selected_cards: list[Card] = []
        self.is_turn: bool = False
        self.time = 0
    
    def set_pos(self, pos: Vector2) -> None:
        self.pos = pos.copy()

    def append(self, card):
        super().append(card)
        # sort by rank
        self.cards.sort(key=lambda c: self.rank_tranlsate(c.rank))
        self._recalculate_depth()
    
    def remove(self, card):
        super().remove(card)
        if card in self.selected_cards:
            self.selected_cards.remove(card)

    def step(self):
        num_of_cards = len(self.cards)
        width = num_of_cards * CARD_SIZE[0] + (num_of_cards - 1) * self.margin
        start_pos = self.pos + Vector2(- width // 2, 0)

        for i, card in enumerate(self.cards):
            pos = start_pos + Vector2(self.margin + CARD_SIZE[0], 0) * i
            if self.is_turn:
                pos += Vector2(0, 2 * sin(10 * time.time()))
            if card in self.selected_cards:
                pos += Vector2(0, -10)
            card.set_pos(pos)
        
    def toggle_select(self, card: Card) -> None:
        if card not in self.cards:
            return
        if card in self.selected_cards:
            self.selected_cards.remove(card)
        else:
            self.selected_cards.append(card)
    
    def get_selected(self) -> list[Card]:
        return self.selected_cards.copy()
    
    def toggle_turn(self) -> None:
        self.is_turn = not self.is_turn