


from utils import Vector2

from card import Card
from card_manipulator import CardManipulator
from events import EventType, Event
from animation import AnimateCard

class GameBase:
    def __init__(self):
        self.cards: list[Card] = []
        self.animations: list[AnimateCard] = []
        self.card_manipulator: CardManipulator = CardManipulator()


    def handle_event(self, event: Event) -> None:
        match event.type:
            case EventType.ADD_ANIMATION:
                new_animation = event.create_animation()
                self.animations.append(new_animation)
            
            case EventType.MOVE_TO_TOP:
                card = event.card
                self.cards.remove(card)
                self.cards.append(card)

    def step(self):
        for element in self.animations:
            element.step()
        self.animations = [e for e in self.animations if not e.is_done()]

    def on_mouse_move(self, pos: Vector2) -> None:
        self.card_manipulator.on_mouse_move(pos)

    def on_mouse_press(self, pos: Vector2) -> None:
        self.card_manipulator.on_mouse_press(pos)

    def on_mouse_release(self, pos: Vector2) -> None:
        self.card_manipulator.on_mouse_release(pos)

    def on_mouse_double_click(self, pos: Vector2) -> None:
        self.card_manipulator.on_double_click(pos)