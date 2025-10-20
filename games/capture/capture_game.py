
from utils.utils import Vector2

import game_globals
from engine.game_base import GameBase
from utils.custom_random import shuffle
from core import Card, Vacant, Rank, Suit, create_deck, CARD_SIZE, PileV2, HandCards, Row
from engine.rules import RuleSet
from engine.events import post_event, Event, EventType, DelayedSetPosEvent, MoveToTopEvent, SequenceCompleteEvent, DroppedCardEvent



class CardCaptureRules(RuleSet):
    def can_drop_card(self, upper: Card, lower: Card) -> bool:
        return False

    def on_place_card(self, placed_Card: Card, placed_upon_card: Card, previous_parent: Card | None, legal_drop: bool) -> None:
        return

    def can_drag_card(self, card: Card) -> bool:
        return False


class CardCaptureGame(GameBase):
    def __init__(self):
        super().__init__()
        self.rules = CardCaptureRules()
        self.card_manipulator.set_rules(self.rules)

        self.enemy_deck = PileV2()
        self.enemy_waste = PileV2()
        self.enemy_row: Row = Row()
        self.player_deck = PileV2()
        self.player_waste = PileV2()
        self.hand = HandCards()

    def handle_event(self, event: Event) -> None:
        super().handle_event(event)
        self.rules.handle_event(event)
        
        if event.type in [EventType.CLICK_CARD, EventType.DOUBLE_CLICK_CARD]:
            card: Card = event.card
            if card in self.hand:
                self.hand.toggle_select(card)

        if event.type == EventType.DOUBLE_CLICK_CARD:
            pass

    # def deal_from_deck(self):
    #     for i in range(10):
    #         if not self.deck:
    #             return
            
    #         card = self.deck.pop(0)
    #         bottom_vacant = self.playing_rows[i].get_bottom_link()
    #         bottom_vacant.link_card(card)
    #         card.face_up = True

    #         event = DelayedSetPosEvent(card, bottom_vacant.pos + bottom_vacant.link_offset, delay=i * 3)
    #         post_event(event)

    #         event = MoveToTopEvent(card)
    #         post_event(event)


    def setup_game(self) -> list[Card]:
        cards: list[Card] = []
        cards = create_deck(joker_allowed=True)
        shuffle(cards)

        card_list = [self.player_deck.vacant, self.enemy_deck.vacant]

        for card in cards:
            if card.rank in [Rank.TWO, Rank.THREE, Rank.FOUR, Rank.JOKER]:
                self.player_deck.append(card)
            else:
                self.enemy_deck.append(card)
            card_list.append(card)
        
        self.enemy_deck.vacant.set_link_offset(Vector2(1,1))
        self.enemy_deck.set_pos(Vector2(100, 100))
        self.player_deck.vacant.set_link_offset(Vector2(2,2))
        self.player_deck.set_pos(Vector2(100, 500))

        self.enemy_row.set_pos(Vector2(game_globals.win_width / 2 + CARD_SIZE[0], 100))

        self.hand.set_pos(Vector2(game_globals.win_width / 2, 500))
        for _ in range(4):
            card = self.player_deck.draw_card()
            card.flip()
            self.hand.append(card)

        for _ in range(4):
            card = self.enemy_deck.draw_card()
            card.flip()
            self.enemy_row.append(card)

        self.cards = card_list
        self.card_manipulator.set_cards(self.cards)
        return self.cards
    
    def step(self):
        super().step()
        self.hand.step()