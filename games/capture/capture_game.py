
from enum import Enum
from dataclasses import dataclass

import game_globals
from utils.utils import Vector2
from engine.game_base import GameBase
from utils.custom_random import shuffle
from core import Card, Vacant, Rank, Suit, create_deck, CARD_SIZE, PileV2, HandCards, Row
from engine.rules import RuleSet
from engine.events import post_event, Event, EventType, DelayedSetPosEvent, MoveToTopEvent, SequenceCompleteEvent, DroppedCardEvent

@dataclass
class Event:
    delay: int
    action: callable

    def step(self) -> None:
        self.delay -= 1
    
    def is_ready(self) -> bool:
        return self.delay <= 0



class GamePhase(Enum):
    START_PHASE = 0
    ENEMY_PHASE = 1
    DISCARD_PHASE = 2
    DRAW_PHASE = 3
    CAPTURE_PHASE = 4

def reposition_row(row: Row) -> None:
    cards = [card for card in row]
    row.clear()
    for card in cards:
        row.append(card)


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

        self.phase = GamePhase.START_PHASE
        self.event: Event = Event(60, self.step_game)

    def handle_event(self, event: Event) -> None:
        super().handle_event(event)
        self.rules.handle_event(event)
        
        if event.type in [EventType.CLICK_CARD, EventType.DOUBLE_CLICK_CARD]:
            card: Card = event.card
            if card in self.hand:
                self.hand.toggle_select(card)
            
            if card in self.enemy_row:
                self.click_on_enemy(card)

            if card in self.player_waste:
                self.discard()
            
            if card in self.player_deck:
                if self.phase == GamePhase.DISCARD_PHASE:
                    self.phase = GamePhase.DRAW_PHASE
                    self.step_game()

        if event.type == EventType.DOUBLE_CLICK_CARD:
            pass

    def step_game(self) -> None:
        print(f'game step phase: {self.phase}')

        trigger_next_phase = True
        next_phase_delay = 60

        match self.phase:
            case GamePhase.START_PHASE:
                # discard face cards from enemy
                face_cards = []
                for card in self.enemy_row:
                    if card.rank in [Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE]:
                        face_cards.append(card)
                for card in face_cards:
                    self.enemy_row.remove(card)
                    card.flip()
                    self.enemy_deck.append_to_bottom(card)
                self.phase = GamePhase.ENEMY_PHASE

            case GamePhase.ENEMY_PHASE:
                # enemy moves
                reposition_row(self.enemy_row)
                # complete enemy
                for _ in range(4 - len(self.enemy_row)):
                    drawn_card = self.enemy_deck.draw_card()
                    if drawn_card:
                        drawn_card.flip()
                        self.enemy_row.append(drawn_card)
                self.phase = GamePhase.DISCARD_PHASE
                next_phase_delay = 0

            case GamePhase.DISCARD_PHASE:
                trigger_next_phase = False

            case GamePhase.DRAW_PHASE:
                # player draws
                cards_to_draw = 4 - len(self.hand)
                if cards_to_draw > len(self.player_deck):
                    # draw all remaining cards
                    for _ in range(len(self.player_deck)):
                        drawn_card = self.player_deck.draw_card()
                        drawn_card.flip()
                        self.hand.append(drawn_card)
                    
                    # reshuffle waste into deck
                    pile_cards = [card for card in self.player_waste]
                    for card in pile_cards:
                        card.flip()
                    self.player_waste.clear()
                    shuffle(pile_cards)
                    for card in pile_cards:
                        self.player_deck.append(card)

                # continue drawing
                for _ in range(4 - len(self.hand)):
                    drawn_card = self.player_deck.draw_card()
                    if drawn_card:
                        drawn_card.flip()
                        self.hand.append(drawn_card)
                self.phase = GamePhase.CAPTURE_PHASE

            case GamePhase.CAPTURE_PHASE:
                trigger_next_phase = False

            
        if trigger_next_phase:
            self.event = Event(next_phase_delay, self.step_game)
        


    def discard(self) -> None:
        if self.phase != GamePhase.DISCARD_PHASE:
            return
        selected_cards = self.hand.get_selected()
        for card in selected_cards:
            self.hand.remove(card)
            self.player_waste.append(card)
        
        self.phase = GamePhase.DRAW_PHASE
        self.step_game()
        
    def calculate_selected_value(self) -> int:
        ranks = [card.rank for card in self.hand.get_selected()]
        amount_of_jokers = ranks.count(Rank.JOKER)

        ranks = [rank for rank in ranks if rank != Rank.JOKER]
        value_calc = lambda x: x.value if x != Rank.ACE else 14
        max_rank_value = max([value_calc(rank) for rank in ranks], default=0)
        value = sum([value_calc(rank) for rank in ranks]) + amount_of_jokers * max_rank_value
        return value

    def sacrifice(self) -> None:
        selected_cards = self.hand.get_selected()
        for card in selected_cards:
            self.hand.remove(card)
            self.enemy_waste.append(card)
        first = next(iter(self.enemy_row))
        if first:
            self.enemy_row.remove(first)
            first.flip()
            self.enemy_deck.append_to_bottom(first)

    
    def click_on_enemy(self, card: Card) -> None:
        if self.phase != GamePhase.CAPTURE_PHASE:
            return
        
        selected_cards = self.hand.get_selected()
        if len(selected_cards) == 0:
            return
        
        check_for_sacrifice = False
        
        hand_except_jokers = [hand_card for hand_card in selected_cards if hand_card.rank != Rank.JOKER]
        legal_suit = all([hand_card.suit == card.suit for hand_card in hand_except_jokers])
        if not legal_suit:
            check_for_sacrifice = True
        
        else:
            capture_value = self.calculate_selected_value()
            if capture_value >= card.rank.value:
                # perform capture
                for hand_card in selected_cards:
                    self.hand.remove(hand_card)
                    self.player_waste.append(hand_card)
                self.enemy_row.remove(card)
                self.player_waste.append(card)
                self.phase = GamePhase.ENEMY_PHASE
                self.event = Event(60, self.step_game)

            else:
                check_for_sacrifice = True
            
        if check_for_sacrifice:
            # check for enemy capture
            if len(selected_cards) == 1 and self.enemy_row.index(card) == 0:
                # enemy capture
                captured_card = selected_cards[0]
                self.enemy_row.remove(card)
                self.enemy_waste.append(card)
                self.hand.remove(captured_card)
                self.enemy_waste.append(captured_card)
                self.phase = GamePhase.ENEMY_PHASE
                self.event = Event(60, self.step_game)
                return
            
            # check for sacrifice
            if len(selected_cards) == 2 and self.enemy_row.index(card) == 0:
                self.sacrifice()
                self.phase = GamePhase.ENEMY_PHASE
                self.event = Event(60, self.step_game)
                return


    def setup_game(self) -> list[Card]:
        cards: list[Card] = []
        cards = create_deck(joker_allowed=True)
        shuffle(cards)

        card_list = [self.player_deck.vacant, self.player_waste.vacant, self.enemy_deck.vacant, self.enemy_waste.vacant]

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
        self.enemy_waste.set_pos(Vector2(game_globals.win_width / 2 + 3 * CARD_SIZE[0], 100))
        self.enemy_waste.vacant.set_link_offset(Vector2(2,2))

        self.hand.set_pos(Vector2(game_globals.win_width / 2, 500))
        self.player_waste.set_pos(Vector2(game_globals.win_width / 2 + 3 * CARD_SIZE[0], 500))
        self.player_waste.vacant.set_link_offset(Vector2(2,2))

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

        if self.event:
            self.event.step()
            if self.event.is_ready():
                event = self.event
                self.event = None
                event.action()

