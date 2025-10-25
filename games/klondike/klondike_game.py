

from utils.utils import Vector2

import game_globals
from engine.game_base import GameBase
from utils.custom_random import shuffle
from core.card import Card, Vacant, Rank, Suit, create_deck, CARD_SIZE
from core import PileV2
from engine.rules import RuleSet
from engine.events import post_event, Event, EventType, DelayedSetPosEvent, MoveToTopEvent, DroppedCardEvent
from core.card_utilities import animate_and_relink

class KlondikeRuleSet(RuleSet):
    def __init__(self):
        super().__init__()
        self.ending_rows: dict[Vacant, bool] = None
        self.deck: PileV2 = None
        self.drawn_deck: PileV2 = None

    def set_lists(self, ending_rows: dict[Vacant, bool], deck: PileV2, drawn_deck: PileV2) -> None:
        self.ending_rows = ending_rows
        self.deck = deck
        self.drawn_deck = drawn_deck

    def _is_alternating(self, suit_upper: Suit, suit_lower: Suit) -> bool:
        if suit_upper in [Suit.CLUBS, Suit.SPADES] and suit_lower in [Suit.DIAMONDS, Suit.HEARTS]:
            return True
        if suit_upper in [Suit.DIAMONDS, Suit.HEARTS] and suit_lower in [Suit.CLUBS, Suit.SPADES]:
            return True
        return False

    def can_drop_card(self, upper: Card, lower: Card) -> bool:
        if upper in self.deck or upper in self.drawn_deck:
            return False

        if upper in self.drawn_deck:
            return False

        # can only link by alternating suit color
        if upper.rank.value == lower.rank.value + 1 and self._is_alternating(upper.suit, lower.suit):
            return True
        
        # cards in ending rows
        if any(upper in pile for pile in self.ending_rows):
            if upper.rank == Rank.NONE and lower.rank == Rank.ACE:
                return True
            elif upper.rank.value + 1 == lower.rank.value and upper.suit == lower.suit:
                return True
        
        if upper.rank == Rank.NONE and not any(upper in pile for pile in self.ending_rows):
            # vacant can link anything
            return True
        
        return False

    def can_drag_card(self, card: Card) -> bool:
        if card in self.deck:
            return False
        if card in self.drawn_deck and card is not self.drawn_deck.get_top():
            return False

        # can only drag face up cards
        if not card.is_face_up():
            return False

        return True
    
    def handle_event(self, event: Event) -> None:
        super().handle_event(event)
        if event.type == EventType.DROPPED_CARD:
            event: DroppedCardEvent = event
            if not event.legal_drop:
                return
            if event.placed_card in self.drawn_deck:
                self.drawn_deck.remove(event.placed_card) 
            if event.last_parent is None:
                return
            if not event.last_parent.is_face_up():
                event.last_parent.flip()


class KlondikeGame(GameBase):
    def __init__(self):
        super().__init__()
        self.rules = KlondikeRuleSet()
        self.card_manipulator.set_rules(self.rules)
        self.deck: PileV2 = PileV2()
        self.drawn_deck: PileV2 = PileV2()

        self.playing_rows: list[PileV2] = []
        self.ending_rows: list[PileV2] = []

    def on_key_press(self, key):
        if key == game_globals.KEY_D:
            self.deal_from_deck()

    def deal_from_deck(self):
        if len(self.deck) == 0:
            if len(self.drawn_deck) == 0:
                return

            drawn_pile = [card for card in self.drawn_deck]
            drawn_pile.reverse()
            for card in drawn_pile:
                self.drawn_deck.remove(card)
                card.flip()
                self.deck.append(card)
            return
        
        card = self.deck.draw_card()
        card.flip()
        self.drawn_deck.append(card)

    def handle_event(self, event: Event) -> None:
        super().handle_event(event)

        self.rules.handle_event(event)
        if event.type == EventType.DOUBLE_CLICK_CARD:
            self.double_click_on_card(event.card)

        if event.type == EventType.CLICK_CARD:
            card: Card = event.card
            if card in self.deck:
                if not card.is_face_up():
                    self.deal_from_deck()
                if card.rank == Rank.NONE and len(self.deck) == 0:
                    self.deal_from_deck()

        if event.type == EventType.DROPPED_CARD:
            dropped_event: DroppedCardEvent = event
            placed_card = dropped_event.placed_card
            placed_upon = dropped_event.placed_upon
            if dropped_event.legal_drop:

                placed_card.parent.remove(placed_card)
                placed_upon.parent.append(placed_card)



        
    def setup_game(self) -> list[Card]:
        cards = create_deck()
        shuffle(cards)

        deck_pos = Vector2(600, 400)
        deck_offset = Vector2(0.5, 0.5)

        self.deck.set_pos(deck_pos)
        self.deck.vacant.set_link_offset(deck_offset)
        for card in cards:
            self.deck.append(card)

        self.drawn_deck.set_pos(deck_pos - Vector2(CARD_SIZE[0] + 10, 0))
        self.drawn_deck.vacant.set_link_offset(deck_offset)

        start_x = 200
        margin = 10
        for i in range(7):

            col = start_x + (CARD_SIZE[0] + margin) * i
            # create pile
            pile = PileV2()
            pile.set_pos(Vector2(col, margin))
            self.playing_rows.append(pile)

            # place i face down cards
            for _ in range(i):
                card = self.deck.draw_card()
                pile.append(card)
    
            # place 1 face up card
            card = self.deck.draw_card()
            card.flip()
            pile.append(card)

        # create ending rows
        for i in range(4):
            col = start_x + (CARD_SIZE[0] + margin) * (i + 7) + 4 * margin
            pile = PileV2()
            pile.set_pos(Vector2(col, margin))
            self.ending_rows.append(pile)

        self.rules.set_lists(self.ending_rows, self.deck, self.drawn_deck)
        self.cards: list[Card] = []
        for pile in self.playing_rows + self.ending_rows + [self.deck, self.drawn_deck]:
            self.cards += pile.get_cards_for_registry()
        self.card_manipulator.set_cards(self.cards)
        return self.cards
    

    def double_click_on_card(self, card: Card) -> None:
        for row_vacant, is_vacant in self.ending_rows.items():

            if card.rank == Rank.ACE and is_vacant:
                card_parent = card.get_prev()
                if card_parent is not None and not card_parent.is_face_up():
                    card_parent.flip()
                animate_and_relink(card, row_vacant)
                if card in self.drawn_deck:
                    self.drawn_deck.remove(card)
                self.ending_rows[row_vacant] = False
                break

            bottom_card = row_vacant.get_bottom_link()
            if bottom_card.suit == card.suit and bottom_card.rank.value + 1 == card.rank.value:
                card_parent = card.get_prev()
                if card_parent is not None and not card_parent.is_face_up():
                    card_parent.flip()
                animate_and_relink(card, bottom_card)
                if card in self.drawn_deck:
                    self.drawn_deck.remove(card)
                break
