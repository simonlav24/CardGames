
from card import Card, Rank, Suit

class RuleSet:
    def __init__(self):
        ...

    def can_link_cards(self, upper: Card, lower: Card) -> bool:
        ...

    def on_place_card(self, card: Card, previous_parent: Card | None):
        ...

    def can_drag_card(self, card: Card) -> bool:
        ...




