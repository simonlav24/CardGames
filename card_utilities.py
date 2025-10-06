
from card import Card, LINK_OFFSET
from events import post_event, MoveToTopEvent, AnimationEvent

def animate_and_relink(moved_card: Card, parent_card: Card, delay: int=0) -> None:
    # break link to parent
    moved_card_parent = moved_card.get_prev()
    if moved_card_parent is not None:
        moved_card_parent.break_lower_link()

    moved_card.break_upper_link()
    parent_card.link_card(moved_card)

    delay = delay
    pos = parent_card.pos + LINK_OFFSET

    event = AnimationEvent(moved_card, moved_card.pos, pos, delay=delay)
    post_event(event)

    event = MoveToTopEvent(moved_card)
    post_event(event)
