

from typing import Callable

from core import Card, CARD_SIZE, Rank, Suit
from utils import Vector2
from engine import post_event, MoveToBottomEvent

margin = 10

class DurakPot:
    def __init__(self, pos: Vector2):
        self.places: list[list[Card, Card]] = []
        self.pos = pos.copy()
        self.alternate_pos = False
        self.current_place_pos = pos.copy()

    def place_attack(self, card: Card):
        self.places.append([card, None])
        card.set_pos(self.current_place_pos)
        if self.alternate_pos:
            self.current_place_pos = self.current_place_pos + Vector2(CARD_SIZE[0] + margin, 0) * len(self.places)
        else:
            self.current_place_pos = self.current_place_pos - Vector2(CARD_SIZE[0] + margin, 0) * len(self.places)
        self.alternate_pos = not self.alternate_pos
        post_event(MoveToBottomEvent(card))

    def place_defend(self, attack_card: Card, defend_card: Card):
        for place in self.places:
            if place[0] == attack_card:
                place[1] = defend_card
                defend_card.set_pos(attack_card.get_pos() + attack_card.link_offset)
                return
        post_event(MoveToBottomEvent(defend_card))
        post_event(MoveToBottomEvent(attack_card))
    
    def get_all_cards(self) -> list[Card]:
        '''get all cards in the pot'''
        cards: list[Card] = []
        for place in self.places:
            for i in range(2):
                if place[i] is not None:
                    cards.append(place[i])
        return cards

    def is_clear_for_defence(self, attack_card: Card) -> bool:
        for place in self.places:
            if place[0] == attack_card and place[1] is None:
                return True
        return False

    def clear_links(self) -> None:
        '''clear any natural links in the pot'''
        for place in self.places:
            if place[0] is not None and place[1] is not None:
                place[0].break_lower_link()
                place[1].break_upper_link()

    def clear_cards(self) -> None:
        '''clear all cards'''
        self.places.clear()
        self.current_place_pos = self.pos.copy()

    def __contains__(self, card: Card) -> bool:
        for place in self.places:
            if card is place[0]:
                return True
        return False
    
    def get_ranks(self) -> set[Rank]:
        rank_set = set()
        for card in self.get_all_cards():
            rank_set.add(card.rank)
        return rank_set
    
    def can_burn(self) -> bool:
        if len(self.places) == 0:
            return False
        for place in self.places:
            if place[0] is not None and place[1] is None:
                return False
        return True
    
    def get_card_of_suit(self, suit: Suit) -> Card:
        return self._look_for_card_satisfying(lambda x: x.suit == suit)

    def get_if_one(self) -> Card:
        '''return attack card if its the only one left'''
        return self._look_for_card_satisfying(lambda _: True)
    
    def _look_for_card_satisfying(self, condition: Callable[[Card], bool]) -> Card:
        '''look for single card that satisfies condition'''
        count = 0
        candidate = None
        for place in self.places:
            attack_card = place[0]
            if (attack_card is not None and place[1] is None and
                condition(attack_card)):
                count += 1
                if count > 1:
                    return None
                candidate = attack_card
        return candidate





    