

from utils import Vector2

from game_base import GameBase
from custom_random import shuffle
from card import Card, Vacant, Rank, Suit, create_deck, CARD_SIZE
from rules import RuleSet
from events import post_event, Event, EventType, AnimationEvent, MoveToTopEvent
from card_utilities import animate_and_relink

class KlondikeRuleSet(RuleSet):
    def __init__(self):
        super().__init__()
        self.ending_rows: dict[Vacant, bool] = None
        self.drawn_deck: list[Card] = None

    def set_lists(self, ending_rows: dict[Vacant, bool], drawn_deck: list[Card]) -> None:
        self.ending_rows = ending_rows
        self.drawn_deck = drawn_deck

    def _is_alternating(self, suit_upper: Suit, suit_lower: Suit) -> bool:
        if suit_upper in [Suit.CLUBS, Suit.SPADES] and suit_lower in [Suit.DIAMONDS, Suit.HEARTS]:
            return True
        if suit_upper in [Suit.DIAMONDS, Suit.HEARTS] and suit_lower in [Suit.CLUBS, Suit.SPADES]:
            return True
        return False

    def can_link_cards(self, upper: Card, lower: Card) -> bool:
        if upper in self.drawn_deck:
            return False

        # can only link by alternating suit color
        if upper.rank.value == lower.rank.value + 1 and self._is_alternating(upper.suit, lower.suit):
            return True
        
        # cards in ending rows
        if upper.get_top_link() in self.ending_rows.keys():
            if upper.rank == Rank.NONE and lower.rank == Rank.ACE:
                return True
            elif upper.rank.value + 1 == lower.rank.value and upper.suit == lower.suit:
                return True
        
        if upper.rank == Rank.NONE and upper not in self.ending_rows.keys():
            # vacant can link anything
            return True
        
        return False

    def on_place_card(self, card: Card, previous_parent: Card | None):
        if card in self.drawn_deck:
            self.drawn_deck.remove(card) 
        if previous_parent is None:
            return
        if not previous_parent.is_face_up():
            previous_parent.flip()

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
        self.deck: list[Card] = []
        self.drawn_deck: list[Card] = []

        self.playing_rows: list[Vacant] = []
        self.ending_rows: dict[Vacant, bool] = {}
        self.deck_pos: Vector2 = Vector2(0, 0)

    def deal_from_deck(self):
        if len(self.deck) == 0:
            if len(self.drawn_deck) == 0:
                return
            for card in self.drawn_deck:
                card.flip()
                event = AnimationEvent(card, card.pos, self.deck_pos.copy())
                post_event(event)
                self.deck.append(card)
            self.drawn_deck.clear()
            return
        
        card = self.deck.pop(0)
        card.flip()
        self.drawn_deck.append(card)

        event = AnimationEvent(card, card.pos, card.pos + Vector2(- 10 - CARD_SIZE[0], 0))
        post_event(event)

        event = MoveToTopEvent(card)
        post_event(event)

    def handle_event(self, event: Event) -> None:
        super().handle_event(event)

        if event.type == EventType.DOUBLE_CLICK_CARD:
            self.double_click_on_card(event.card)

        
    def setup_game(self) -> list[Card]:
        cards = create_deck()
        shuffle(cards)
        self.deck = cards.copy()

        self.deck_pos = Vector2(600, 400)
        for card in cards:
            card.set_pos(self.deck_pos.copy())
        vacants: list[Vacant] = []
        
        start_x = 200
        margin = 10
        for i in range(7):

            col = start_x + (CARD_SIZE[0] + margin) * i
            # create vacant
            last_card = Vacant(Vector2(col, margin))
            self.playing_rows.append(last_card)
            vacants.insert(0, last_card)

            # place i face down cards
            for j in range(i):
                card = self.deck.pop(0)
                last_card.link_card(card)
                last_card = card
                card.face_up = False
                card.set_pos(Vector2(col, margin + (card.link_offset.y * (j + 1))))
    
            # place 1 face up card
            card = self.deck.pop(0)
            last_card.link_card(card)
            card.face_up = True
            card.set_pos(Vector2(col, margin + (card.link_offset.y * (i + 1))))

        # create ending rows
        for i in range(4):
            col = start_x + (CARD_SIZE[0] + margin) * (i + 7) + 4 * margin
            last_card = Vacant(Vector2(col, margin))
            self.ending_rows[last_card] = True
            vacants.append(last_card)

        self.rules.set_lists(self.ending_rows, self.drawn_deck)
        self.cards = vacants + cards
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
