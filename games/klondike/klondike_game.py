

from utils.utils import Vector2

import game_globals
from engine.game_base import GameBase
from utils.custom_random import shuffle
from core.card import Card, Vacant, Rank, Suit, create_deck, CARD_SIZE
from core import PileV2
from engine.rules import RuleSet
from engine.events import post_event, Event, EventType, DelayedSetPosEvent, MoveToTopEvent, DroppedCardEvent, DragStartEvent
from core.card_utilities import animate_and_relink

class KlondikeRuleSet(RuleSet):
    def __init__(self):
        super().__init__()
        self.ending_rows: list[PileV2] = None
        self.drawn_deck: PileV2 = None

    def initialize(self, ending_rows: list[PileV2], drawn_deck: PileV2) -> None:
        self.ending_rows = ending_rows
        self.drawn_deck = drawn_deck

    def _is_alternating(self, suit_upper: Suit, suit_lower: Suit) -> bool:
        if suit_upper in [Suit.CLUBS, Suit.SPADES] and suit_lower in [Suit.DIAMONDS, Suit.HEARTS]:
            return True
        if suit_upper in [Suit.DIAMONDS, Suit.HEARTS] and suit_lower in [Suit.CLUBS, Suit.SPADES]:
            return True
        return False

    def can_drop_card(self, upper: Card, lower: Card) -> bool:
        if upper is None or upper in self.drawn_deck:
            return False

        # can only link by alternating suit color
        if upper.rank.value == lower.rank.value + 1 and self._is_alternating(upper.suit, lower.suit):
            return True
        
        # cards in ending rows
        if upper.parent in self.ending_rows:
            if upper.rank == Rank.NONE and lower.rank == Rank.ACE:
                return True
            elif upper.rank.value + 1 == lower.rank.value and upper.suit == lower.suit:
                return True
        
        if upper.rank == Rank.NONE and upper.parent not in self.ending_rows:
            # vacant can link anything
            return True
        
        return False

    def can_drag_card(self, card: Card) -> bool:
        # can only drag face up cards
        if not card.is_face_up():
            return False

        return True
    


class KlondikeGame(GameBase):
    def __init__(self):
        super().__init__()
        self.rules = KlondikeRuleSet()
        self.card_manipulator.set_rules(self.rules)

        self.deck: PileV2 = None
        self.drawn_deck: PileV2 = None

        self.playing_piles: list[PileV2] = []
        self.ending_piles: list[PileV2] = []

    def on_key_press(self, key):
        if key == game_globals.KEY_D:
            self.deal_from_deck()

    def deal_from_deck(self):
        # if len(self.deck) == 0:
        #     if len(self.drawn_deck) == 0:
        #         return
        #     for card in self.drawn_deck:
        #         card.flip()
        #         card.set_pos(self.deck_pos.copy())
        #         self.deck.append(card)
        #     self.drawn_deck.clear()
        #     return
        
        card = self.deck.get_top()
        self.deck.remove(card)

        card.flip()
        self.drawn_deck.insert(card)

        event = MoveToTopEvent(card)
        post_event(event)

    def handle_event(self, event: Event) -> None:
        super().handle_event(event)

        if event.type == EventType.DOUBLE_CLICK_CARD:
            self.double_click_on_card(event.card)

        if event.type == EventType.CLICK_CARD:
            card: Card = event.card
            if card in self.deck and not card.is_face_up():
                self.deal_from_deck()

        if event.type == EventType.DROPPED_CARD:
            event: DroppedCardEvent = event
            print('dropped')
            
            # if event.placed_card in self.drawn_deck:
            #     self.drawn_deck.remove(event.placed_card)

        if event.type == EventType.DRAG_START:
            event: DragStartEvent = event
            print('drag start')


        
    def setup_game(self) -> list[Card]:
        cards = create_deck()
        shuffle(cards)
        visual_cards = cards.copy()

        self.deck = PileV2(Vector2(600, 400), Vector2(1,1))
        self.drawn_deck = PileV2(Vector2(600 - CARD_SIZE[0] - 20, 400), Vector2(1,1))
        
        start_x = 200
        margin = 10
        for i in range(7):

            col = start_x + (CARD_SIZE[0] + margin) * i
            # pile
            pile = PileV2(Vector2(col, margin))
            self.playing_piles.append(pile)

            # place i face down cards
            for j in range(i):
                card = cards.pop()
                pile.insert(card)
                post_event(MoveToTopEvent(card))
    
            # place 1 face up card
            card = cards.pop()
            card.flip()
            pile.insert(card)
            post_event(MoveToTopEvent(card))

        # create ending rows
        for i in range(4):
            col = start_x + (CARD_SIZE[0] + margin) * (i + 7) + 4 * margin
            self.ending_piles.append(PileV2(Vector2(col, margin)))

        # remaining cards go to deck
        for card in cards:
            self.deck.insert(card)

        self.rules.initialize(self.ending_piles, self.drawn_deck)

        all_cards = visual_cards + [i.get_vacant() for i in [self.deck, self.drawn_deck] + self.playing_piles + self.ending_piles] 
        self.card_manipulator.set_cards(all_cards)
        self.cards = all_cards
        return all_cards
    

    def double_click_on_card(self, card: Card) -> None:
        return
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
