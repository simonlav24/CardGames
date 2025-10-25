


from core.card import Card
from engine.events import post_event, MoveToTopEvent

class CardContainer:
    def __init__(self):
        self.cards: list[Card] = []

    def append(self, card: Card) -> None:
        self.cards.append(card)
        card.parent = self
        self._recalculate_depth()

    def remove(self, card: Card) -> None:
        card.break_lower_link()
        card.break_upper_link()
        card.parent = None
        self.cards.remove(card)

    def __contains__(self, card: Card) -> bool:
        return card in self.cards
    
    def _recalculate_depth(self) -> None:
        for card in self.cards:
            post_event(MoveToTopEvent(card=card))

    def __len__(self) -> int:
        return len(self.cards)
    
    def __iter__(self):
        return iter(self.cards)
    
    def clear(self) -> None:
        self.cards.clear()
