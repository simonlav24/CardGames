
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
        self.vacant.parent = self

    def set_pos(self, pos: Vector2):
        self.vacant.set_abs_pos(pos)
        self._update_positions()

    def _update_positions(self):
        pos = self.vacant.pos.copy()
        for card in self.cards:
            card.set_pos(pos)
            pos += self.vacant.link_offset
        
    def append(self, card: Card) -> None:
        if card is None:
            return
        top = self.get_top()
        super().append(card)
        card.break_lower_link()
        top.link_card(card)
        self._recalculate_depth()
        self._update_positions()

    def append_to_bottom(self, card: Card) -> None:
        if card is None:
            return
        if len(self.cards) == 0:
            super().append(card)
        else:
            previous_bottom_card = self.vacant.linked_down
            previous_bottom_card.break_upper_link()
            self.vacant.link_card(card)
            card.link_card(previous_bottom_card)
            self.cards.insert(0, card)
        self._update_positions()
        self._recalculate_depth()

    def draw_card(self) -> Card:
        card = self.get_top()
        if card is self.vacant:
            return None
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
    
    def get_cards_for_registry(self) -> list[Card]:
        return [self.vacant] + self.cards
    