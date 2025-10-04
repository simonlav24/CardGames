
import pygame
from pygame.math import Vector2

from custom_random import shuffle
from card import Card, Vacant, Rank, Suit, create_single_suit_deck, CARD_SIZE, LINK_OFFSET
from rules import RuleSet


class SpiderRuleSet(RuleSet):
    def __init__(self):
        ...

    def can_link_cards(self, upper: Card, lower: Card) -> bool:
        # only rank matters in spider
        if upper.rank == Rank.NONE:
            # vacant can link anything
            return True
        
        if upper.rank.value == lower.rank.value + 1:
            return True
        
        return False

    def on_place_card(self, card: Card, previous_parent: Card | None):
        if not previous_parent.is_face_up():
            previous_parent.flip()

        # check for completed sequence
        ...

    def can_drag_card(self, card: Card) -> bool:
        # can only drag face up cards
        if not card.is_face_up():
            return False
        
        # can only drag if all linked cards below are in sequence
        expected_rank = card.rank.value
        for linked_card in card.iterate_down():
            if linked_card.rank.value != expected_rank:
                return False
            expected_rank -= 1
        
        return True

    
class SpiderGame:
    def __init__(self):
        self.rules = SpiderRuleSet()
        self.deck: list[Card] = []

        self.playing_rows: list[Vacant] = []
        self.ending_rows: list[Vacant] = []

    def deal_from_deck(self):
        for i in range(10):
            if not self.deck:
                return
            
            card = self.deck.pop(0)
            bottom_vacant = self.playing_rows[i].get_bottom_link()
            bottom_vacant.link_card(card)
            card.face_up = True

            custom_event = pygame.event.Event(pygame.USEREVENT, {"key": "animation", "card": card, "start_pos": card.pos, "end_pos": bottom_vacant.pos + LINK_OFFSET})
            pygame.event.post(custom_event)
            custom_event = pygame.event.Event(pygame.USEREVENT, {"key": "move_to_top", "card": card})
            pygame.event.post(custom_event)

    def setup_game(self) -> list[Card]:
        cards: list[Card] = []
        for i in range(8):
            cards += create_single_suit_deck(Suit.CLUBS)

        shuffle(cards)
        self.deck = cards.copy()
        
        vacants: list[Vacant] = []

        # 10 places
        margin = 10
        last_card: Card = None

        for i in range(10):
            col = 100 + (CARD_SIZE[0] + margin) * i
            last_card = Vacant(Vector2(col, 100))
            self.playing_rows.append(last_card)
            vacants.insert(0, last_card)

            upside_down_cards = 5
            if i >= 4:
                upside_down_cards = 4

            # place 6 face down cards
            for j in range(upside_down_cards):
                card = self.deck.pop(0)
                last_card.link_card(card)
                last_card = card
                card.face_up = False
                card.set_pos(Vector2(col, 100 + (LINK_OFFSET.y * (j + 1))))

            # place 1 face up card
            card = self.deck.pop(0)
            last_card.link_card(card)
            last_card = card
            card.face_up = True
            card.set_pos(Vector2(col, 100 + (LINK_OFFSET.y * (upside_down_cards + 1))))

        # 8 empty cards in the end
        for i in range(4):
            for j in range(2):
                col = 100 + (CARD_SIZE[0] + margin) * (i + 10)
                row = 100 + j * 340
                ending_vacant = Vacant(Vector2(col, row))
                vacants.insert(0, ending_vacant)
                self.ending_rows.append(ending_vacant)

        return vacants + cards