


from utils.utils import Vector2

from core.card import Card
from engine.card_manipulator import CardManipulator
from engine.events import EventType, Event
from core.animation import DelayedPosCard

class GameBase:
    def __init__(self):
        self.cards: list[Card] = []
        self.elements: list[DelayedPosCard] = []
        self.card_manipulator: CardManipulator = CardManipulator()

    def handle_event(self, event: Event) -> None:
        match event.type:
            case EventType.DELAYED_SET_POS:
                self.elements.append(event.create_element())
            
            case EventType.MOVE_TO_TOP:
                card = event.card
                self.cards.remove(card)
                self.cards.append(card)

            case EventType.MOVE_TO_BOTTOM:
                card = event.card
                self.cards.remove(card)
                self.cards.insert(0, card)

    def step(self):
        self.card_manipulator.step()
        for element in self.elements:
            element.step()
        self.elements = [e for e in self.elements if not e.is_done()]
        for card in self.cards:
            card.step()

    def get_selected_card(self) -> Card | None:
        return self.card_manipulator.selected_card

    def on_mouse_move(self, pos: Vector2) -> None:
        self.card_manipulator.on_mouse_move(pos)

    def on_mouse_press(self, pos: Vector2) -> None:
        self.card_manipulator.on_mouse_press(pos)

    def on_mouse_release(self, pos: Vector2) -> None:
        self.card_manipulator.on_mouse_release(pos)

    def on_mouse_double_click(self, pos: Vector2) -> None:
        self.card_manipulator.on_double_click(pos)

    def on_key_press(self, key: int) -> None:
        ...