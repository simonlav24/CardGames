
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
    def __init__(self, pos: Vector2=(0,0), offset: Vector2=(0,20)):
        super().__init__()
        self.vacant = Vacant(Vector2(pos))
        self.card_offset = Vector2(offset)

    def set_pos(self, pos: Vector2):
        self.vacant.set_abs_pos(pos)
        self._update_positions()

    def _update_positions(self):
        pos = self.vacant.get_pos()
        for card in self.cards:
            card.set_pos(pos)
            pos += self.card_offset
        
    def insert(self, card: Card, position: int=-1) -> None:
        if card is None:
            return
        super().insert(card, position)
        self._recalculate_depth()
        self._update_positions()

    def draw_card(self) -> Card:
        card = self.get_top()
        if card is self.vacant:
            return None
        if card:
            self.remove(card)
        return card

    def __contains__(self, card) -> bool:
        if card is self.vacant:
            return True
        return super().__contains__(card)

    def get_top(self) -> Card:
        return self.cards[-1] if self.cards else self.vacant
    
    def get_vacant(self) -> Vacant:
        return self.vacant
    

class DraggedPile(CardContainer):
    def __init__(self, cards: list[Card], offset: Vector2=(0,20)):
        super().__init__()
        for card in cards:
            self.insert(card)
        self.card_offset = Vector2(offset)

    def set_pos(self, pos: Vector2):
        ...

    def refresh(self) -> None:
        self._update_positions()

    def _update_positions(self):
        pos = self.cards[0].get_pos()
        for card in self.cards:
            card.set_pos(pos)
            pos += self.card_offset
        
    def insert(self, card: Card, position: int=-1) -> None:
        if card is None:
            return
        super().insert(card, position)
        self._recalculate_depth()
        self._update_positions()

