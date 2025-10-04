
from dataclasses import dataclass
from enum import Enum

import pygame
from pygame.math import Vector2

from animation import Positionable, Animation
from card import Card


class EventType(Enum):
    ADD_ELEMENT = 1
    MOVE_TO_TOP = 2


@dataclass
class Event:
    pass

@dataclass
class AnimationEvent(Event):
    card: Positionable
    start_pos: Vector2
    end_pos: Vector2
    type: EventType = EventType.ADD_ELEMENT
    delay: int = 0

    def create_element(self) -> Animation:
        return Animation(self.card, self.start_pos, self.end_pos, self.delay)


@dataclass
class MoveToTopEvent(Event):
    card: Card
    type: EventType = EventType.MOVE_TO_TOP


def post_event(event: Event):
    custom_event = pygame.event.Event(pygame.USEREVENT, {"event": event})
    pygame.event.post(custom_event)