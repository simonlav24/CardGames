
from pygame.math import Vector2

from animation import Positionable


class Event:
    pass


class AnimationEvent(Event):
    def __init__(self, element: Positionable, start_pos: Vector2, end_pos: Vector2):
        self.element = element
        self.start_pos = start_pos
        self.end_pos = end_pos


class EventSystem:
    def __init__(self):
        self.events = []

    def post_event(self, event):
        self.events.append(event)