
import pygame
from pygame.math import Vector2

from card import Card, CARD_SIZE, Rank, LINK_OFFSET
from rules import RuleSet
from events import EventSystem

DEBUG = False

def debug_print(*args):
    if DEBUG:
        print(*args)

class CardEventHandler:
    def __init__(self, rules: RuleSet, event_system: EventSystem):
        self.cards: list[Card] = []
        self.rules = rules
        self.event_system = event_system
        
        self.selected_card: Card | None = None
        self.dragged_card: Card | None = None
        self.drag_offset: Vector2 = Vector2(0, 0)

        self.previous_pos: Vector2 = Vector2(0, 0)

        self.is_linking: bool = True

    def set_cards(self, cards: list[Card]):
        self.cards = cards

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.dragged_card:
                self.drag_card(self.dragged_card, Vector2(event.pos) - self.drag_offset)
            
            self.selected_card = None
            for card in reversed(self.cards):
                card_rect = pygame.Rect(*card.pos, *CARD_SIZE)
                if card_rect.collidepoint(event.pos):
                    self.selected_card = card
                    break
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.selected_card:
                if not self.rules.can_drag_card(self.selected_card):
                    return
                debug_print(f"Selected card: {self.selected_card.rank} of {self.selected_card.suit}")
                self.previous_pos = self.selected_card.pos
                self.dragged_card = self.selected_card
                self.drag_offset = Vector2(event.pos) - self.dragged_card.pos

                self.move_card_to_top(self.dragged_card)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if not self.dragged_card:
                    return
                
                card_to_link = self.dragged_card
                self.dragged_card = None
                self.drag_offset = Vector2(0, 0)
                if self.is_linking:
                    potential_parent = self.find_card_at_pos(event.pos, exclude=card_to_link)

                    if potential_parent is None:
                        custom_event = pygame.event.Event(pygame.USEREVENT, {"key": "animation", "card": card_to_link, "start_pos": card_to_link.pos, "end_pos": self.previous_pos})
                        pygame.event.post(custom_event)
                        return
                    
                    else:
                        # link cards
                        previous_link = card_to_link.get_prev()
                        is_linked = self.link_cards(potential_parent, card_to_link)
                        if not is_linked:
                            # self.drag_card(card_to_link, self.previous_pos)
                            custom_event = pygame.event.Event(pygame.USEREVENT, {"key": "animation", "card": card_to_link, "start_pos": card_to_link.pos, "end_pos": self.previous_pos})
                            pygame.event.post(custom_event)
                        else:
                            self.rules.on_place_card(card_to_link, previous_link)
        
    def find_card_at_pos(self, pos: Vector2, exclude: Card) -> Card | None:
        for card in reversed(self.cards):
            if card is exclude:
                continue
            card_rect = pygame.Rect(*card.pos, *CARD_SIZE)
            if card_rect.collidepoint(pos):
                return card
        return None


    def link_cards(self, upper: Card, lower: Card) -> bool:

        bottom_card = upper.get_bottom_link()
        
        if bottom_card is lower:
            return False
        
        if not self.rules.can_link_cards(bottom_card, lower):
            return False
        
        is_linked = bottom_card.link_card(lower)
        if is_linked:
            lower.set_pos(bottom_card.pos + LINK_OFFSET)

        return is_linked

    def drag_card(self, card: Card, pos: Vector2):
        if card.rank == Rank.NONE:
            return

        card.set_pos(pos)
        next_card = card.get_next()
        if next_card is not None:
            self.drag_card(next_card, pos + LINK_OFFSET)

    def move_card_to_top(self, card: Card):
        debug_print(f"Moving card to top: {card}")
        if card.rank == Rank.NONE:
            return
        self.cards.remove(card)
        self.cards.append(card)
        next_card = card.get_next()
        if next_card is not None:
            self.move_card_to_top(next_card)
        