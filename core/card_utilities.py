
from core.card import Card
from engine.events import post_event, MoveToTopEvent, DelayedSetPosEvent

def animate_and_relink(moved_card: Card, parent_card: Card, delay: int=0) -> None:
    # break link to parent
    moved_card_parent = moved_card.get_prev()
    if moved_card_parent is not None:
        moved_card_parent.break_lower_link()

    moved_card.break_upper_link()
    parent_card.link_card(moved_card)
 
    delay = delay
    pos = parent_card.get_pos() + parent_card.link_offset

    event = DelayedSetPosEvent(moved_card, pos, delay=delay)
    post_event(event)

    event = MoveToTopEvent(moved_card)
    post_event(event)


def move_cards_and_relink(cards: list[Card], target: Card):
    last_card = target.get_bottom_link()
    pos = last_card.get_pos() + last_card.link_offset
    for i, card in enumerate(cards):
        card.break_lower_link()
        card.break_upper_link()
        last_card.link_card(card)

        event = DelayedSetPosEvent(card, pos.copy(), delay=i)
        post_event(event)

        event = MoveToTopEvent(card)
        post_event(event)

        pos += last_card.link_offset
        last_card = card
