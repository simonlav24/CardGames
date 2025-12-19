


from core.card import Card
from engine.events import post_event, MoveToTopEvent

class CardContainer:
    def __init__(self):
        self.cards: list[Card] = []

    def insert(self, card: Card, position: int=-1) -> None:
        if position == -1:
            self.cards.append(card)
        else:
            self.cards.insert(position, card)
        card.parent = self
        self._recalculate_depth()

    def remove(self, card: Card) -> None:
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

    def refresh(self) -> None:
        ...
