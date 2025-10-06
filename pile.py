
from utils import Vector2

from card import Card, Vacant
from card_container import CardContainer

class Pile(CardContainer):
    def __init__(self):
        super().__init__()
        self.vacant = Vacant()

    def set_pos(self, pos: Vector2):
        self.vacant.set_pos(pos)
        
    def append(self, card):
        super().append(card)
        self.get_top().link_card(card)

    def __contains__(self, card):
        if card is self.vacant:
            return True
        return super().__contains__(card)

    def get_top(self) -> Card:
        return self.vacant.get_bottom_link()
    
    