
import pygame
from utils.utils import Vector2
from pygame import Rect

from core.card import Card, CARD_SIZE, Rank
from engine.rules import RuleSet
from engine.events import (
    post_event, 
    DelayedSetPosEvent, 
    DoubleClickedCard, 
    ClickedCard,
    DroppedCardEvent,
    DragStartEvent
)

DEBUG = False

def debug_print(*args):
    if DEBUG:
        print(*args)

class CardManipulator:
    def __init__(self):
        self.cards: list[Card] = []
        self.rules: RuleSet = None
        
        self.selected_card: Card | None = None
        self.dragged_card: Card | None = None
        self.drag_offset: Vector2 = Vector2(0, 0)
        self.last_pos: Vector2 = Vector2(0, 0)
    
    def set_rules(self, rules: RuleSet) -> None:
        self.rules = rules

    def set_cards(self, cards: list[Card]) -> None:
        self.cards = cards

    def on_mouse_move(self, pos: Vector2) -> None:
        if self.dragged_card:
            self.drag_card(self.dragged_card, Vector2(pos) - self.drag_offset)
        
        self.selected_card = None
        closest_card = self.find_card_at_pos(Vector2(pos))
        
        if closest_card is not None:
            self.selected_card = closest_card

    def on_mouse_press(self, pos: Vector2) -> None:
        if self.selected_card is None:
            return
        
        post_event(ClickedCard(card=self.selected_card))

        if not self.rules.can_drag_card(self.selected_card):
            return
        self.last_pos = self.selected_card.get_pos().copy()
        self.dragged_card = self.selected_card
        self.drag_offset = Vector2(pos) - self.dragged_card.pos
        post_event(DragStartEvent(self.dragged_card))

        if self.rules.move_to_front_on_drag:
            self.move_card_to_top(self.dragged_card)
        

    def on_double_click(self, pos: Vector2):
        if self.selected_card is None:
            return
        post_event(DoubleClickedCard(card=self.selected_card))


    def on_mouse_release(self, pos: Vector2) -> None:
        if not self.dragged_card:
            return
        
        dragged_card = self.dragged_card
        self.dragged_card = None
        self.drag_offset = Vector2(0, 0)


        potential_parent = self.find_card_near_pos(Vector2(pos), exclude=dragged_card)

        legal_drop = self.rules.can_drop_card(potential_parent, dragged_card)
        if not legal_drop:
            parent = dragged_card.parent
            if parent is not None:
                parent.refresh()
            

        if potential_parent is not None:
            if legal_drop:
                post_event(DroppedCardEvent(dragged_card, potential_parent, legal_drop))

            

    # def animate_sequence_to_pos(self, card: Card, end_pos: Vector2):
    #     for i, linked_card in enumerate(card.iterate_down()):
    #         event = DelayedSetPosEvent(card=linked_card, pos=end_pos, delay=i * 2)
    #         post_event(event)
    #         end_pos = end_pos + card.link_offset

        
    def find_card_near_pos(self, pos: Vector2, exclude: Card=None) -> Card | None:
        closest_card: Card = None
        closest_dist: float = float('inf')
        for card in reversed(self.cards):
            if card is exclude:
                continue
            card_rect = Rect(*(card.pos - CARD_SIZE * 0.5), *(CARD_SIZE * 2))
            if card_rect.collidepoint(pos):
                dist = pos.distance_squared_to(card.pos + CARD_SIZE * 0.5)
                if dist < closest_dist:
                    closest_card = card
                    closest_dist = dist
        return closest_card

    def find_card_at_pos(self, pos: Vector2, exclude: Card=None) -> Card | None:
        # TODO: find nearest card instead of first
        for card in reversed(self.cards):
            if card is exclude:
                continue
            card_rect = Rect(*card.pos, *CARD_SIZE)
            if card_rect.collidepoint(pos):
                return card
        return None


    def drag_card(self, card: Card, pos: Vector2):
        if card.rank == Rank.NONE:
            return
        card.set_abs_pos(pos)
        if card.parent is not None:
            card.parent.refresh()

        # next_card = card.get_next()
        # if next_card is not None:
        #     self.drag_card(next_card, pos + next_card.get_prev().link_offset)


    def move_card_to_top(self, card: Card):
        debug_print(f"Moving card to top: {card}")
        if card.rank == Rank.NONE:
            return
        self.cards.remove(card)
        self.cards.append(card)
        # next_card = card.get_next()
        # if next_card is not None:
        #     self.move_card_to_top(next_card)

    def step(self) -> None:
        for card in self.cards:
            card.step()
        