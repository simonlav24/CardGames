
from typing import Protocol

from utils import Vector2

from card import Card


class AnimateCard:
    def __init__(self, target: Card, start: Vector2, end: Vector2, delay: int = 0):
        self.target = target
        self.start = start.copy()
        self.end = end.copy()
        self.delay = delay

        self.current_pos: Vector2 = start
        self.finished = False

    def step(self):
        if self.finished:
            return
        
        if self.delay > 0:
            self.delay -= 1
            return
        
        self.target.is_locked = True
        self.current_pos += (self.end - self.current_pos) * 0.2

        if (self.current_pos - self.end).length() < 1:
            self.current_pos = self.end
            self.finished = True

        self.target.set_pos(self.current_pos)
        
    def is_done(self) -> bool:
        self.target.is_locked = False
        return self.finished
        