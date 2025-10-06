
from dataclasses import dataclass
from enum import Enum

import pygame
from utils import Vector2

from animation import AnimateCard
from card import Card


class EventType(Enum):
    ADD_ANIMATION = 1
    MOVE_TO_TOP = 2
    SEQUENCE_COMPLETE = 3
    DOUBLE_CLICK_CARD = 4
    CLICK_CARD = 5


@dataclass
class Event:
    pass

@dataclass
class AnimationEvent(Event):
    card: Card
    start_pos: Vector2
    end_pos: Vector2
    type: EventType = EventType.ADD_ANIMATION
    delay: int = 0

    def create_animation(self) -> AnimateCard:
        return AnimateCard(self.card, self.start_pos, self.end_pos, self.delay)


@dataclass
class MoveToTopEvent(Event):
    card: Card
    type: EventType = EventType.MOVE_TO_TOP


@dataclass
class SequenceCompleteEvent(Event):
    main_card: Card
    type: EventType = EventType.SEQUENCE_COMPLETE


@dataclass
class ClickedCard(Event):
    card: Card
    type: EventType = EventType.CLICK_CARD


@dataclass
class DoubleClickedCard(Event):
    card: Card
    type: EventType = EventType.DOUBLE_CLICK_CARD


def post_event(event: Event):
    custom_event = pygame.event.Event(pygame.USEREVENT, {"event": event})
    pygame.event.post(custom_event)