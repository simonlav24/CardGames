
from enum import Enum

from utils.utils import Vector2, Rect

import game_globals

DEBUG = False

CARD_SIZE = Vector2(71, 96)
DEFAULT_LINK_OFFSET = Vector2(0, 17)

class Rank(Enum):
    NONE = 0
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13


class Suit(Enum):
    NONE = 0
    SPADES = 1
    HEARTS = 2
    CLUBS = 3
    DIAMONDS = 4

suit_text = {
    Suit.HEARTS: "Hearts",
    Suit.DIAMONDS: "Diamonds",
    Suit.CLUBS: "Clubs",
    Suit.SPADES: "Spades"
}

suit_color = {
    Suit.HEARTS: (255, 0, 0),
    Suit.DIAMONDS: (255, 0, 0),
    Suit.CLUBS: (0, 0, 0),
    Suit.SPADES: (0, 0, 0)
}

rank_text = {
    Rank.ACE: "Ace",
    Rank.TWO: "2",
    Rank.THREE: "3",
    Rank.FOUR: "4",
    Rank.FIVE: "5",
    Rank.SIX: "6",
    Rank.SEVEN: "7",
    Rank.EIGHT: "8",
    Rank.NINE: "9",
    Rank.TEN: "10",
    Rank.JACK: "Jack",
    Rank.QUEEN: "Queen",
    Rank.KING: "King"
}


def rank_translate_ace_low(rank: Rank) -> int:
    return rank.value

def rank_translate_ace_high(rank: Rank) -> int:
    if rank == Rank.ACE:
        return 14
    return rank.value


class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
        self.face_up = True
        self.linked_up: Card | None = None
        self.linked_down: Card | None = None
        
        self.pos = Vector2()
        self.target_pos = Vector2()

        self.link_offset = DEFAULT_LINK_OFFSET
        self.is_hidden = False

    def set_link_offset(self, offset: Vector2) -> None:
        self.link_offset = offset.copy()

    def set_pos(self, pos: Vector2) -> None:
        self.target_pos = pos.copy()

    def set_abs_pos(self, pos: Vector2) -> None:
        self.target_pos = pos.copy()
        self.pos = pos.copy()

    def get_pos(self) -> Vector2:
        return self.target_pos.copy()

    def get_bottom_link(self) -> 'Card':
        # return bottom most linked card
        card = self
        while card.linked_down is not None:
            card = card.linked_down
        return card
    
    def get_top_link(self) -> 'Card':
        *_, last = self.iterate_up()
        return last

    def is_linked(self) -> bool:
        ''' check if linked from above '''
        return self.linked_up is not None
    
    def get_next(self) -> 'Card | None':
        return self.linked_down
    
    def get_prev(self) -> 'Card | None':
        return self.linked_up
    
    def break_upper_link(self) -> None:
        ''' break link to upper card '''
        if self.linked_up is not None:
            self.linked_up.linked_down = None
            self.linked_up = None

    def break_lower_link(self) -> None:
        ''' break link to lower card '''
        if self.linked_down is not None:
            self.linked_down.linked_up = None
            self.linked_down = None

    def link_card(self, card: 'Card') -> bool:
        ''' link a card below this card '''

        for uplink in self.iterate_up():
            if uplink is self:
                continue
            if uplink is card:
                return False  # already linked
        for downlink in self.iterate_down():
            if downlink is self:
                continue
            if downlink is card:
                return False  # already linked

        if card.linked_up is not None:
            card.break_upper_link()    
        
        self.linked_down = card
        card.linked_up = self
        
        card.set_link_offset(self.link_offset)
        return True

    def __repr__(self):
        return f"{rank_text[self.rank]} of {suit_text[self.suit]}"
    
    def iterate_up(self):
        card = self
        while card is not None:
            yield card
            card = card.linked_up

    def iterate_down(self):
        card = self
        while card is not None:
            yield card
            card = card.linked_down

    def is_face_up(self) -> bool:
        return self.face_up

    def flip(self) -> None:
        self.face_up = not self.face_up

    def step(self) -> None:
        self.pos = self.pos + (self.target_pos - self.pos) * 0.2
        if self.pos.distance_squared_to(self.target_pos) < 1:
            self.pos = self.target_pos
    

class Vacant(Card):
    def __init__(self, pos: Vector2 = Vector2(0,0)):
        super().__init__(Rank.NONE, Suit.NONE)
        self.target_pos = pos

    def __repr__(self):
        return "Vacant"
    
    def is_free(self) -> bool:
        return self.get_next() is None



def create_deck() -> list[Card]:
    deck = []
    for suit in Suit:
        if suit == Suit.NONE:
            continue
        for rank in Rank:
            if rank == Rank.NONE:
                continue
            card = Card(rank, suit)
            card.face_up = False
            deck.append(card)

    return deck

def create_single_suit_deck(suit: Suit) -> list[Card]:
    deck = []
    for rank in Rank:
        if rank == Rank.NONE:
            continue
        card = Card(rank, suit)
        card.face_up = False
        deck.append(card)

    return deck
