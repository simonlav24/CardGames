
from utils import Vector2, shuffle

from core.card import Card, Vacant
from core.card_container import CardContainer

class Pile(CardContainer):
    def __init__(self):
        super().__init__()
        self.vacant = Vacant()

    def set_pos(self, pos: Vector2):
        self.vacant.set_abs_pos(pos)

    def update_positions(self):
        pos = self.vacant.pos.copy()
        for card in self.cards:
            card.set_pos(pos)
            pos += self.vacant.link_offset
        
    def append(self, card) -> None:
        super().append(card)
        self.get_top().link_card(card)

    def __contains__(self, card) -> bool:
        if card is self.vacant:
            return True
        return super().__contains__(card)

    def get_top(self) -> Card:
        return self.vacant.get_bottom_link()
    
    def shuffle(self) -> None:
        shuffle(self.cards)
    

class PileV2(CardContainer):
    def __init__(self):
        super().__init__()
        self.vacant = Vacant()

    def set_pos(self, pos: Vector2):
        self.vacant.set_abs_pos(pos)
        self._update_positions()

    def _update_positions(self):
        pos = self.vacant.pos.copy()
        for card in self.cards:
            card.set_pos(pos)
            pos += self.vacant.link_offset
        
    def append(self, card: Card) -> None:
        super().append(card)
        self.get_top().link_card(card)

    def draw_card(self) -> Card:
        card = self.get_top()
        if card:
            self.remove(card)
            card.break_links()
        return card

    def __contains__(self, card) -> bool:
        if card is self.vacant:
            return True
        return super().__contains__(card)

    def get_top(self) -> Card:
        return self.vacant.get_bottom_link()
    