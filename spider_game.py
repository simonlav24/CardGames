

from pygame.math import Vector2

from game_base import GameBase
from custom_random import shuffle
from card import Card, Vacant, Rank, Suit, create_single_suit_deck, CARD_SIZE, LINK_OFFSET
from rules import RuleSet
from events import post_event, Event, EventType, AnimationEvent, MoveToTopEvent, SequenceCompleteEvent


class SpiderRuleSet(RuleSet):
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
        king = None
        for parent in card.iterate_up():
            if parent.rank == Rank.KING and parent.is_face_up():
                king = parent
                break
        if king is None:
            return

        # iterate the king down to the bottom, checking for a complete sequence
        expected_rank = Rank.KING.value
        for linked_card in king.iterate_down():
            if linked_card.rank.value != expected_rank:
                return
            expected_rank -= 1

        if expected_rank == 0:
            event = SequenceCompleteEvent(main_card=king)
            post_event(event)

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


class SpiderGame(GameBase):
    def __init__(self):
        super().__init__()
        self.rules = SpiderRuleSet()
        self.card_manipulator.set_rules(self.rules)
        self.deck: list[Card] = []

        self.playing_rows: list[Vacant] = []
        self.ending_rows: dict[Vacant, bool] = {}

    def handle_event(self, event: Event) -> None:
        super().handle_event(event)
        if event.type == EventType.SEQUENCE_COMPLETE:
            king = event.main_card
            self.complete_sequence(king)


    def complete_sequence(self, king: Card) -> None:
        # find vacant ending row
        for vacant, is_vacant in self.ending_rows.items():
            if is_vacant:
                break
        
        king_parent = king.get_prev()
        king_parent.break_lower_link()
        if not king_parent.is_face_up():
            king_parent.flip()
        king.break_upper_link()
        vacant.link_card(king)
        self.ending_rows[vacant] = False

        current_card = king
        delay = 30
        pos = vacant.pos + LINK_OFFSET
        while current_card is not None:

            event = AnimationEvent(current_card, current_card.pos, pos, delay=delay)
            post_event(event)

            event = MoveToTopEvent(current_card)
            post_event(event)

            current_card = current_card.get_next()
            delay += 3
            pos = pos + LINK_OFFSET


    def deal_from_deck(self):
        for i in range(10):
            if not self.deck:
                return
            
            card = self.deck.pop(0)
            bottom_vacant = self.playing_rows[i].get_bottom_link()
            bottom_vacant.link_card(card)
            card.face_up = True

            event = AnimationEvent(card, card.pos, bottom_vacant.pos + LINK_OFFSET, delay=i * 3)
            post_event(event)

            event = MoveToTopEvent(card)
            post_event(event)


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
        start_x = 50

        for i in range(10):
            col = start_x + (CARD_SIZE[0] + margin) * i
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
                col = start_x + (CARD_SIZE[0] + margin) * (i + 10) + 4 * margin
                row = 100 + j * 340
                ending_vacant = Vacant(Vector2(col, row))
                vacants.insert(0, ending_vacant)
                self.ending_rows[ending_vacant] = True

        self.cards = vacants + cards
        self.card_manipulator.set_cards(self.cards)
        return self.cards