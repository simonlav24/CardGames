
from typing import Protocol

from pygame.math import Vector2


class Positionable(Protocol):
    def set_pos(self, pos: Vector2) -> None:
        ...


class Animation:
    def __init__(self, target: Positionable, start: Vector2, end: Vector2, delay: int = 0):
        self.target = target
        self.start = start
        self.end = end
        self.delay = delay

        self.current_pos: Vector2 = start
        self.finished = False

    def step(self):
        if self.finished:
            return
        
        if self.delay > 0:
            self.delay -= 1
            return
        
        self.current_pos += (self.end - self.current_pos) * 0.2

        if (self.current_pos - self.end).length() < 1:
            self.current_pos = self.end
            self.finished = True

        self.target.set_pos(self.current_pos)
        
    def is_done(self) -> bool:
        return self.finished
        