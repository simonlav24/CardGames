

from utils import Vector2, shuffle

from core.card import Card, Vacant, CARD_SIZE
from core.card_container import CardContainer

margin = 10

class Row(CardContainer):
    def __init__(self):
        super().__init__()
        self.pos = Vector2()
        self.direction = -1


    def set_pos(self, pos: Vector2) -> None:
        self.pos = pos.copy()
        pos = pos.copy()
        for card in self.cards:
            card.set_pos(pos)
            pos += Vector2((CARD_SIZE[0] + margin) * self.direction, 0)


    def append(self, card):
        super().append(card)
        card.set_pos(self.pos + Vector2(((CARD_SIZE[0] + margin) * self.direction) * (len(self.cards) -1), 0))