
from utils import Vector2 

from card import Card, CARD_SIZE
from events import MoveToTopEvent, post_event
from card_container import CardContainer

class HandCards(CardContainer):
    ''' cards held in hand '''
    def __init__(self):
        super().__init__()
        # center pos
        self.pos = Vector2()
        self.target_positions: list[Vector2] = []
        self.margin = - CARD_SIZE[0] // 2
        # self.margin = 10
    
    def set_pos(self, pos: Vector2) -> None:
        self.pos = pos.copy()

    def step(self):
        num_of_cards = len(self.cards)
        width = num_of_cards * CARD_SIZE[0] + (num_of_cards - 1) * self.margin
        start_pos = self.pos + Vector2(- width // 2)
        self.target_positions.clear()
        for i in range(num_of_cards):
            pos = start_pos + Vector2(self.margin + CARD_SIZE[0], 0) * i
            self.target_positions.append(pos)
        
        for card, target_pos in zip(self.cards, self.target_positions):
            card_pos = card.get_pos()
            pos = card_pos + (target_pos - card_pos) * 0.2
            card.set_pos(pos)
        