
from typing import Protocol

from utils import Vector2

from card import Card


class DelayedPosCard:
    def __init__(self, card: Card, pos: Vector2, delay: int = 0):
        self.card = card
        self.pos = pos.copy()
        self.delay = delay

        self.finished = False

    def step(self):
        if self.finished:
            return
        
        if self.delay > 0:
            self.delay -= 1
            return
        
        self.card.set_pos(self.pos)
        self.finished = True
        
    def is_done(self) -> bool:
        return self.finished
        