
from dataclasses import dataclass
from enum import Enum

import pygame
from utils import Vector2

from animation import DelayedPosCard
from card import Card


class EventType(Enum):
    DELAYED_SET_POS = 1
    MOVE_TO_TOP = 2
    SEQUENCE_COMPLETE = 3
    DOUBLE_CLICK_CARD = 4
    CLICK_CARD = 5


@dataclass
class Event:
    pass

@dataclass
class DelayedSetPosEvent(Event):
    card: Card
    pos: Vector2
    delay: int = 0
    type: EventType = EventType.DELAYED_SET_POS

    def create_element(self) -> DelayedPosCard:
        return DelayedPosCard(self.card, self.pos, self.delay)


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