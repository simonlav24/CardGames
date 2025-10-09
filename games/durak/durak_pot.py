

from core import Card, CARD_SIZE
from utils import Vector2

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
            self.current_place_pos = self.current_place_pos + Vector2(CARD_SIZE[0] + margin) * len(self.places)
        else:
            self.current_place_pos = self.current_place_pos - Vector2(CARD_SIZE[0] + margin) * len(self.places)
        self.alternate_pos = not self.alternate_pos

    def place_defend(self, attack_card: Card, defend_card: Card):
        for place in self.places:
            if place[0] == attack_card:
                place[1] = defend_card
                defend_card.set_pos(attack_card.get_pos() + attack_card.link_offset)
                return
    
    def get_all_cards(self) -> list[Card]:
        cards: list[Card] = []
        for place in self.places:
            for i in range(2):
                if place[i] is not None:
                    cards.append(place[0])
        return cards

    def is_clear_for_defence(self, attack_card: Card) -> bool:
        for place in self.places:
            if place[0] == attack_card and place[1] is None:
                return True
        return False

    def clear(self) -> None:
        self.places.clear()
        self.current_place_pos = self.pos.copy()

    def __contains__(self, card: Card) -> bool:
        for place in self.places:
            if card is place[0]:
                return True
        return False




    