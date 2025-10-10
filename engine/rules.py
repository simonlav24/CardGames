from utils import Vector2
from core import Card, Rank, Suit
# from engine import Event

class RuleSet:
    def __init__(self):
        self.on_drop_return_to_previous_pos = True
        self.move_to_front_on_drag = True

    def can_drop_card(self, upper: Card, lower: Card) -> bool:
        ...

    def can_drag_card(self, card: Card) -> bool:
        ...

    def handle_event(self, event) -> None:
        ...




