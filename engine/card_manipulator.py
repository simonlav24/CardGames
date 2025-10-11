
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
    DroppedCardEvent
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

        self.is_linking: bool = True
    
    def set_rules(self, rules: RuleSet) -> None:
        self.rules = rules

    def set_cards(self, cards: list[Card]) -> None:
        self.cards = cards

    def on_mouse_move(self, pos: Vector2) -> None:
        if self.dragged_card:
            self.drag_card(self.dragged_card, Vector2(pos) - self.drag_offset)
        
        self.selected_card = None
        closest_card = self.find_card_at_pos(pos)
        
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

        if self.rules.move_to_front_on_drag:
            self.move_card_to_top(self.dragged_card)
        

    def on_double_click(self, pos: Vector2):
        if (self.selected_card is None or
            not self.selected_card.is_face_up()):
            return
        post_event(DoubleClickedCard(card=self.selected_card))

    def _calc_previous_pos(self, card: Card) -> Vector2:
        parent = card.get_prev()
        if parent is None:
            return self.last_pos
        return parent.pos + parent.link_offset

    def on_mouse_release(self, pos: Vector2) -> None:
        if not self.dragged_card:
            return
        
        card_to_link = self.dragged_card
        self.dragged_card = None
        self.drag_offset = Vector2(0, 0)

        legal_drop = False

        potential_parent = self.find_card_at_pos(pos, exclude=card_to_link)
        previous_link = card_to_link.get_prev()

        if potential_parent is not None:
            if self.rules.can_drop_card(potential_parent, card_to_link):
                # card is placed, link cards
                legal_drop = True
                is_linked = self.link_cards(potential_parent, card_to_link)
                if not is_linked:
                    legal_drop = False

        if legal_drop:
            self.animate_sequence_to_pos(card_to_link, potential_parent.pos + potential_parent.link_offset)

        if not legal_drop and self.rules.on_drop_return_to_previous_pos:
            self.animate_sequence_to_pos(card_to_link, self.last_pos)
        
        post_event(DroppedCardEvent(card_to_link, potential_parent, self.last_pos, previous_link, legal_drop))
            

    def animate_sequence_to_pos(self, card: Card, end_pos: Vector2):
        for i, linked_card in enumerate(card.iterate_down()):
            event = DelayedSetPosEvent(card=linked_card, pos=end_pos, delay=i * 2)
            post_event(event)
            end_pos = end_pos + card.link_offset

        
    def find_card_at_pos(self, pos: Vector2, exclude: Card=None) -> Card | None:
        for card in reversed(self.cards):
            if card is exclude:
                continue
            card_rect = Rect(*card.pos, *CARD_SIZE)
            if card_rect.collidepoint(pos):
                return card
        return None


    def link_cards(self, upper: Card, lower: Card) -> bool:

        bottom_card = upper.get_bottom_link()
        
        if bottom_card is lower:
            return False
        
        if not self.rules.can_drop_card(bottom_card, lower):
            return False
        
        is_linked = bottom_card.link_card(lower)

        return is_linked

    def drag_card(self, card: Card, pos: Vector2):
        if card.rank == Rank.NONE:
            return

        card.set_abs_pos(pos)
        next_card = card.get_next()
        if next_card is not None:
            self.drag_card(next_card, pos + next_card.get_prev().link_offset)


    def move_card_to_top(self, card: Card):
        debug_print(f"Moving card to top: {card}")
        if card.rank == Rank.NONE:
            return
        self.cards.remove(card)
        self.cards.append(card)
        next_card = card.get_next()
        if next_card is not None:
            self.move_card_to_top(next_card)
        