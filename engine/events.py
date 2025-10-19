
from dataclasses import dataclass
from enum import Enum

import pygame
from utils.utils import Vector2

from core.animation import DelayedPosCard
from core.card import Card

TEST_MODE = False

class EventType(Enum):
    NONE = 0
    DELAYED_SET_POS = 1
    MOVE_TO_TOP = 2
    MOVE_TO_BOTTOM = 3
    SEQUENCE_COMPLETE = 4
    DOUBLE_CLICK_CARD = 5
    CLICK_CARD = 6
    DROPPED_CARD = 7


@dataclass
class Event:
    ...

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
class MoveToBottomEvent(Event):
    card: Card
    type: EventType = EventType.MOVE_TO_BOTTOM


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

@dataclass
class DroppedCardEvent(Event):
    placed_card: Card
    placed_upon: Card
    last_pos: Vector2
    last_parent: Card
    legal_drop: bool
    type: EventType = EventType.DROPPED_CARD

def post_event(event: Event):
    if(TEST_MODE):
        return
    custom_event = pygame.event.Event(pygame.USEREVENT, {"event": event})
    pygame.event.post(custom_event)